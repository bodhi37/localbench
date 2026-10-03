"""Endpoint lifecycle + the run loop.

One model resident at a time: stop every GPU-holding profile, drain VRAM,
start the endpoint, confirm its identity via ``/v1/models`` plus a 1-token warm
completion, run the selected units, stop the endpoint. Records are appended to
``results/results.jsonl``, one JSON object per unit.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import signal
import shutil
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from typing import Optional

from . import harness, netguard
from .config import RESULTS_DIR, RESULTS_JSONL, load_local
from .graders import grade
from .registry import Unit, load_units


def _sh(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True)


def make_run_id() -> str:
    return time.strftime("%Y%m%d-%H%M%S")


def _gpu_mem_mib() -> int:
    r = _sh(["nvidia-smi", "--query-gpu=memory.used",
             "--format=csv,noheader,nounits"])
    try:
        return int(r.stdout.strip().splitlines()[0])
    except (ValueError, IndexError):
        return -1


def _pkill(patterns: list[str]) -> None:
    for pat in patterns:
        # `--` is mandatory: stop_endpoint's own serve_cmd pattern is
        # `--port <n>\b`, and getopt_long would otherwise read it as an
        # unrecognised *option* and exit 2. The output is captured, so that
        # failure used to be invisible — and the endpoint simply never died,
        # holding the GPU for the next model that needed it.
        subprocess.run(["pkill", "-f", "--", pat], capture_output=True)
    time.sleep(2.0)
    for pat in patterns:
        subprocess.run(["pkill", "-9", "-f", "--", pat], capture_output=True)


def stop_everything(local: dict) -> None:
    """Stop every profile that might hold the GPU so the next endpoint starts clean."""
    for u in local.get("conflict_units", []):
        subprocess.run(["systemctl", "--user", "stop", u], capture_output=True)
    _pkill(local.get("conflict_procs", []))
    deadline = time.time() + 150
    while time.time() < deadline:
        m = _gpu_mem_mib()
        if 0 <= m < 1600:
            return
        time.sleep(3.0)


def _endpoint_warm(ep: dict) -> bool:
    url = f"http://127.0.0.1:{ep['port']}/v1/chat/completions"
    body = json.dumps(dict(model=ep["model"], max_tokens=1,
                           messages=[{"role": "user", "content": "hi"}])).encode()
    try:
        req = urllib.request.Request(url, data=body,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.status == 200
    except Exception:
        return False


def wait_ready(ep: dict, log: Path) -> tuple[bool, str, Optional[str]]:
    """Poll /v1/models until the endpoint answers, then confirm weights are hot.

    Returns (ok, message, reported_model_id). Servers that only ever host one
    model — llama.cpp reports the GGUF path rather than any logical name — are
    accepted on a single-model response plus a successful 1-token completion;
    the id actually reported is returned so it can be recorded in results.
    """
    url = f"http://127.0.0.1:{ep['port']}/v1/models"
    deadline = time.time() + ep.get("ready", 420)
    t0 = time.time()
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=3) as r:
                data = json.loads(r.read().decode())
            ids = [m.get("id") for m in data.get("data", [])]
            if ep["model"] in ids:
                reported = ep["model"]
            elif len(ids) == 1:
                reported = ids[0]
            else:
                return False, f"expected {ep['model']!r} on :{ep['port']}, server offers {ids}", None
            if _endpoint_warm(ep):
                how = ("exact id match" if reported == ep["model"]
                       else f"sole model served: {reported}")
                return True, (f"ready in {time.time() - t0:.0f}s "
                              f"({how} on :{ep['port']})"), reported
        except Exception:
            pass
        time.sleep(4.0)
    tail = ""
    if log.is_file():
        tail = " | ".join(log.read_text(errors="replace").splitlines()[-4:])
    return False, f"timeout waiting for {ep['model']} on :{ep['port']}. {tail}", None


def start_endpoint(local: dict, ep: dict, log: Path) -> tuple[bool, str, Optional[str]]:
    if ep.get("external"):
        # already running and not ours to manage: no VRAM drain, no start
        return wait_ready(ep, log)
    stop_everything(local)
    if ep.get("units"):
        for u in ep["units"]:
            _sh(["systemctl", "--user", "reset-failed", u])
            r = _sh(["systemctl", "--user", "start", "--no-block", u])
            if r.returncode != 0:
                return False, f"systemctl start {u} failed: {r.stderr.strip()}", None
    elif ep.get("serve_cmd"):
        # A path typo here would otherwise surface as a bare `timeout waiting
        # for <model>` minutes later, with the real cause buried in a log.
        script = Path(ep["serve_cmd"])
        if not script.is_file():
            return False, f"serve_cmd does not exist: {script}", None
        if not os.access(script, os.X_OK):
            return False, (f"serve_cmd is not executable: {script} "
                           f"— run `chmod +x {script}`"), None
        with open(log, "ab") as fh:
            # start_new_session=True is setsid(2): the server becomes a
            # session *and* process-group leader, so stop can take down the
            # whole serving tree with one killpg instead of guessing at a
            # command-line pattern (which matches anything containing that
            # string — including your shell if it happens to mention the port).
            proc = subprocess.Popen([str(script)], stdout=fh, stderr=fh,
                                    start_new_session=True)
        ep["_proc"], ep["_pid"] = proc, proc.pid
    else:
        return False, "no start method configured", None
    return wait_ready(ep, log)


def _kill_group(pid: int) -> None:
    """Take down the whole process group we started, by id rather than by
    pattern matching."""
    try:
        pgid = os.getpgid(pid)
    except ProcessLookupError:
        return
    for sig in (signal.SIGTERM, signal.SIGKILL):
        try:
            os.killpg(pgid, sig)
        except ProcessLookupError:
            return
        deadline = time.time() + 3.0
        while time.time() < deadline:
            try:
                os.killpg(pgid, 0)
            except ProcessLookupError:
                return
            time.sleep(0.2)


def _listening(port: int) -> bool:
    """Is anything still accepting connections on this port?"""
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=1.0):
            return True
    except OSError:
        return False


def stop_endpoint(local: dict, ep: dict) -> None:
    if ep.get("external"):
        return          # we did not start it, so we do not stop it
    for u in ep.get("units", []):
        _sh(["systemctl", "--user", "stop", u])
    if ep.get("proc_kill"):
        _pkill(ep["proc_kill"])
    proc, pid = ep.pop("_proc", None), ep.pop("_pid", None)
    if pid:
        _kill_group(pid)
    if proc is not None:
        try:
            proc.wait(timeout=5)        # reap, so a long run leaves no zombies
        except Exception:
            pass
    # Only reach for the fuzzy command-line pattern if something is still
    # listening — that pattern matches *any* process whose argv merely
    # contains the text, so it is a fallback for a server that daemonised
    # itself out of our group, not the first resort.
    if ep.get("serve_cmd") and _listening(ep["port"]):
        _pkill([rf"--port {ep['port']}\b"])
    time.sleep(5.0)


# --------------------------------------------------------------------------- #
# the run loop
# --------------------------------------------------------------------------- #

def _append(rec: dict) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with RESULTS_JSONL.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")


def run(models: list[str], benchmarks: Optional[list[str]],
        tasks: Optional[list[str]], limit: int, dry_run: bool,
        keep_work: bool, run_id: Optional[str] = None) -> int:
    local = load_local()
    endpoints = local["endpoints"]
    if models:
        wanted = set(models)
        endpoints = [e for e in endpoints if e["slug"] in wanted or e["name"] in wanted]
        if not endpoints:
            print(f"FATAL: no endpoint matched {sorted(wanted)}", file=sys.stderr)
            return 2

    units = load_units(benchmarks, tasks, limit)
    if not units:
        print("FATAL: no units selected (bad --bench / --tasks, or known "
              "benchmarks not fetched yet — try `localbench fetch`)",
              file=sys.stderr)
        return 2

    per_bench: dict[str, int] = {}
    for u in units:
        per_bench[u.benchmark] = per_bench.get(u.benchmark, 0) + 1
    selected_counts = dict(per_bench)   # stamped on every record as `expected`
    print(f"=== localbench: {len(endpoints)} endpoint(s) x {len(units)} unit(s) "
          f"across {len(per_bench)} benchmark(s) ===")
    for name in sorted(per_bench):
        print(f"    {name:28} {per_bench[name]}")
    if limit:
        print(f"  (known benchmarks capped at {limit} items each — --limit 0 for all)")
    if dry_run:
        print("\n--dry-run: not starting any endpoint")
        return 0

    # kernel-enforced egress guard: install now (once per boot) so every
    # sandbox below is inside the cgroup from its first instruction
    ok, msg = netguard.ensure()
    lines = (msg or "").splitlines() or [""]
    print(f"  netguard: {lines[0]}")
    for line in lines[1:]:
        print(f"             {line}")
    if not ok:
        print(f"FATAL: kernel egress guard unavailable:\n{msg}", file=sys.stderr)
        return 2

    run_id = run_id or make_run_id()
    transcripts = RESULTS_DIR / "transcripts"
    out_root = RESULTS_DIR / "out"
    work_root = RESULTS_DIR / "work"
    print(f"\nrun_id = {run_id}")

    for ep in endpoints:
        print(f"\n### {ep['name']} ({ep['provider']}:{ep['model']} :{ep['port']})"
              + ("  [external — not managed]" if ep.get("external") else ""))
        log = transcripts / f"server-{ep['slug']}.log"
        transcripts.mkdir(parents=True, exist_ok=True)
        ok, msg, reported = start_endpoint(local, ep, log)
        print(f"  start: {msg}")
        if not ok:
            _append(dict(run_id=run_id, ts=harness.now_iso(), uid=None,
                         model=ep["name"], model_slug=ep["slug"],
                         endpoint_failed=True, pass_=False,
                         detail=f"endpoint failed to start: {msg}"))
            stop_endpoint(local, ep)
            continue

        for i, unit in enumerate(units, 1):
            out_dir = out_root / ep["slug"] / unit.benchmark / unit.ref
            # a fresh unit must never be graded against the previous run's
            # leftovers in this (run-independent) directory
            shutil.rmtree(out_dir, ignore_errors=True)
            work_dir = (work_root /
                        f"{ep['slug']}-{unit.ref.replace('/', '_')}-{make_run_id()}")
            tr = transcripts / ep["slug"] / unit.benchmark / unit.ref
            tr.parent.mkdir(parents=True, exist_ok=True)
            print(f"  [{i}/{len(units)}] {unit.benchmark}/{unit.ref} "
                  f"({unit.grader}, cap {unit.timeout}s) ...", flush=True)

            rec = run_unit_safe(unit, ep, out_dir, work_dir, tr, unit.timeout,
                                keep_work, run_id, selected_counts[unit.benchmark])
            rec["reported_model"] = reported
            mark = ("PASS" if rec["pass_"]
                    else "TIMEOUT" if rec["timed_out"] else "FAIL")
            print(f"        {mark}  {rec['detail'][:150]}  "
                  f"(wall {rec['wall_s']}s, out {rec.get('output_tokens')} tok, "
                  f"tools {rec.get('tool_calls')})", flush=True)
            _append(rec)
            harness.teardown(unit)

        stop_endpoint(local, ep)
        print(f"  endpoint {ep['name']} stopped")

    print(f"\nDone. Records: {RESULTS_JSONL}")
    print("Next: `python3 -m localbench score`  /  `python3 -m localbench report`")
    return 0


def run_unit_safe(unit: Unit, ep: dict, out_dir: Path, work_dir: Path,
                  transcript: Path, timeout: int, keep_work: bool,
                  run_id: str, expected: int) -> dict:
    rec = harness.run_unit(unit, ep, out_dir, work_dir, transcript, timeout,
                           keep_work)
    rec["run_id"] = run_id
    rec["expected"] = expected
    rec["ts"] = harness.now_iso()
    if not rec["timed_out"]:
        if rec.get("error"):
            rec["detail"] = rec["error"]
        else:
            passed, detail = grade(unit, out_dir)
            rec["pass_"] = bool(passed)
            rec["detail"] = detail
    return rec
