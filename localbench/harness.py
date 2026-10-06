"""Run one Unit through the Pi agent inside a bwrap sandbox, then parse stats.

Same harness for both suites: custom tasks expose only the two entries the
prompt may reference — ``prompt.md`` and ``resources/`` — mounted read-only at
their real paths; every other file in the task directory (``meta.json``,
``tests/``, ``verify.py``, ``teardown.sh``, ``SOLUTION.md`` and anything added
later) is simply never mounted, so it does not exist inside the sandbox at all.
Published benchmark items get no task directory at all. Either way the model
only ever sees ``unit.prompt`` plus the task's own inputs.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

from . import netguard
from .config import ep_host, harness_cfg
from .registry import Unit

SYSPROMPT = (
    "You are a careful, pragmatic coding agent working in a minimal sandbox. "
    "Complete exactly the task given; produce concrete deliverables (files when "
    "asked, a final answer line when asked) and nothing extraneous. Do not "
    "invent capabilities you do not have."
)
APPEND_SYSPROMPT = (
    "Method: inspect any files the task ships with, think it through, then "
    "write the deliverable into the output directory ($OUT_DIR if the task "
    "mentions one) and finish. Do not read or reference anything outside the "
    "task folder and your working directory. Stay strictly inside the task "
    "scope."
)

TMPFS_TREES = ["/home", "/tmp", "/run", "/var", "/opt", "/srv",
               "/mnt", "/media", "/boot"]

TASK_VIEW = ("prompt.md", "resources")
"""Whitelist: the only task-folder entries the sandbox ever mounts.

A blacklist has to name every secret and silently fails open the moment a new
file appears in a task directory (an ``expected.json``, a ``SOLUTION.md``, a
scratch note). This list inverts that: only these names are mounted, so an
unknown file is invisible by construction. The prompts reference nothing else —
inputs always live under ``resources/``, deliverables under ``$OUT_DIR``.
"""


def now_iso() -> str:
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


def _bwrap_cmd(cfg: dict, unit: Unit, out_dir: Path, work_dir: Path,
               home: Path, no_proxy_hosts: tuple = ()) -> list[str]:
    pi_tree = cfg["pi_tree"]
    task_dir = unit.task_dir
    cmd = [
        "bwrap",
        "--ro-bind", "/usr", "/usr",
        "--ro-bind", "/etc", "/etc",
        "--dev", "/dev", "--proc", "/proc",
    ]
    cmd += sum((["--tmpfs", t] for t in TMPFS_TREES), [])
    # binds into tmpfs-shadowed trees must come AFTER the tmpfs mounts,
    # otherwise the tmpfs hides them (this is why npm_global used to be inert)
    cmd += [
        "--symlink", "usr/lib64", "/lib64",
        "--ro-bind", cfg["npm_global"], cfg["npm_global"],
        "--ro-bind", pi_tree, "/pi",
        "--bind", str(work_dir), str(work_dir),
        "--bind", str(out_dir), str(out_dir),
    ]
    if task_dir:
        # Whitelist mount: only prompt.md + resources/ are mounted, each at its
        # real path (bwrap creates the missing parents inside the /home tmpfs).
        # meta.json / tests/ / verify.py / teardown.sh / SOLUTION.md — and any
        # file a future edit adds — are never mounted, so they do not exist
        # inside the sandbox rather than merely being masked.
        for name in TASK_VIEW:
            entry = task_dir / name
            if entry.exists():
                cmd += ["--ro-bind", str(entry), str(entry)]
    cmd += [
        "--unshare-pid",
        "--die-with-parent", "--new-session",
        "--chdir", str(work_dir),
        "--setenv", "HOME", str(home),
        "--setenv", "TMPDIR", str(work_dir / ".tmp"),
        "--setenv", "OUT_DIR", str(out_dir),
        "--setenv", "PATH",
        "/pi/node:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
        "--setenv", "LANG", "C.UTF-8",
        "--setenv", "NO_COLOR", "1",
        "--setenv", "PI_OFFLINE", "1",
    ]
    cmd += _network_env(cfg, no_proxy_hosts)
    cmd += ["--", "node", str(Path("/pi") / cfg["pi_cli"])]
    return cmd


def write_models_shim(source: Path, provider: str, home: Path) -> Path:
    """Give the agent the *one* provider under test, not the whole registry.

    ``models.json`` lists every configured provider, and each entry can carry a
    real API key — a remote provider's key has no business being readable by a
    model we are actively trying to measure, and it is exactly the kind of
    material a benchmarking run should not hand to an untrusted process. Pi is
    invoked with ``--provider <one>``, so a single-entry registry is all it can
    ever use.

    Lives at ``$HOME/.pi/agent/models.json`` inside ``work_dir``, which the
    sandbox already binds — no bind of the real registry is ever mounted.
    """
    dest = home / ".pi" / "agent" / "models.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        raw = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        raise RuntimeError(f"cannot read {source}: {e}") from e
    provs = raw.get("providers") or {}
    if provider not in provs:
        print(f"  WARNING: provider {provider!r} not in {source}; "
              f"available: {sorted(provs)[:8]}... — Pi will not start",
              file=sys.stderr)
    dest.write_text(json.dumps({"providers": {provider: provs[provider]}}
                               if provider in provs else {"providers": {}},
                               indent=2), encoding="utf-8")
    return dest


def _network_env(cfg: dict, extra_no_proxy: tuple = ()) -> list[str]:
    """Keep the sandbox off the public internet while leaving loopback alone.

    The sandbox MUST share the host network namespace — the model under test
    lives on 127.0.0.1 (or a configured ``host``), and ``bwrap --unshare-net``
    would give it a private loopback that cannot reach the host. So egress is blocked by pointing every
    well-behaved HTTP client at a dead proxy, with ``no_proxy`` carved out for
    loopback so the endpoint stays reachable.

    This stops curl / wget / python requests / urllib from fetching answers.
    It is NOT a kernel-level guarantee: raw sockets are not intercepted. See
    README "Sandboxing" for the honest limits.
    """
    if not cfg.get("block_network", True):
        return []
    dead = "http://127.0.0.1:9"
    out = []
    for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY"):
        out += ["--setenv", k, dead]
    for k in ("all_proxy", "ALL_PROXY"):
        out += ["--setenv", k, "socks5://127.0.0.1:9"]
    seen = ["127.0.0.1", "localhost", "::1"]
    for h in extra_no_proxy:
        if h and h not in seen:
            seen.append(h)
    for k in ("no_proxy", "NO_PROXY"):
        out += ["--setenv", k, ",".join(seen)]
    # Node's built-in fetch (undici) ignores the proxy variables above on
    # Node < 24; from 24 it honours them only when this is set. Pi is a Node
    # app, so without it the agent's own HTTP client would sail straight past
    # the block. On older Node the flag is simply unknown and harmless.
    out += ["--setenv", "NODE_USE_ENV_PROXY", "1"]
    return out


def _agent_args(cfg: dict, endpoint: dict) -> list[str]:
    return [
        "--provider", endpoint["provider"],
        "--model", endpoint["model"],
        "--system-prompt", SYSPROMPT,
        "--append-system-prompt", APPEND_SYSPROMPT,
        "--no-session", "--no-extensions", "--no-skills",
        "--no-prompt-templates", "--no-themes", "--no-context-files",
        "--thinking", str(cfg.get("thinking", "high")),
        "-p", "--mode", "json",
    ]


def _parse_transcript(ndjson: Path, out_dir: Path, res: dict) -> None:
    """Pull wall-clock, token and tool-use stats out of Pi's NDJSON stream."""
    try:
        events = [json.loads(ln) for ln in
                  ndjson.read_text(errors="replace").splitlines()
                  if ln.strip().startswith("{")]
    except Exception as e:
        res["error"] = f"transcript parse failed: {e}"
        return

    final_msg = None
    t_first = None
    tool_starts = 0
    for ev in events:
        typ = ev.get("type")
        if typ == "message_end" and ev.get("message", {}).get("role") == "user":
            t_first = ev.get("message", {}).get("timestamp")
        elif typ == "turn_end":
            final_msg = ev.get("message")
        elif typ == "message_update":
            aev = ev.get("assistantMessageEvent", {})
            if str(aev.get("type", "")).startswith("tool"):
                tool_starts += 1

    res["turn_count"] = sum(1 for ev in events if ev.get("type") == "turn_end")
    res["tool_calls"] = tool_starts
    if not final_msg:
        res["error"] = res.get("error") or "no final message in transcript"
        return

    parts = final_msg.get("content", [])
    text = "".join(p.get("text", "") for p in parts if p.get("type") == "text")
    thinking = "".join(p.get("thinking", "") for p in parts if p.get("type") == "thinking")
    ntool = len([p for p in parts if str(p.get("type", "")).startswith("tool")])
    res["tool_calls"] = max(res["tool_calls"], ntool)
    res["reasoning_chars"] = len(thinking)
    try:
        (out_dir / "response.txt").write_text(text, encoding="utf-8")
    except OSError:
        res["error"] = "could not write response.txt"
    usage = final_msg.get("usage", {}) or {}
    res["output_tokens"] = usage.get("output")
    res["input_tokens"] = usage.get("input")
    if t_first and final_msg.get("timestamp"):
        res["turn_s"] = round((final_msg["timestamp"] - t_first) / 1000.0, 1)


def _kill_sandbox(proc: subprocess.Popen) -> None:
    """Kill the sandbox's whole process group (helper, bwrap, agent, ...).

    The group was created by ``start_new_session=True``, so it contains
    everything spawned below sudo — killing only the direct child could leave
    the model's process running.
    """
    try:
        os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
    except (ProcessLookupError, PermissionError, OSError):
        pass


def run_unit(unit: Unit, endpoint: dict, out_dir: Path, work_dir: Path,
             transcript: Path, timeout: int, keep_work: bool = False) -> dict:
    """Execute one unit. Returns a record with execution stats; *not* graded."""
    cfg = harness_cfg()
    res = dict(
        uid=unit.uid, ref=unit.ref, suite=unit.suite, benchmark=unit.benchmark,
        grader=unit.grader, kind=unit.kind,
        model=endpoint["name"], model_slug=endpoint["slug"],
        pass_=False, detail="", timed_out=False, error=None,
        wall_s=0.0, output_tokens=None, input_tokens=None,
        reasoning_chars=0, tool_calls=0, turn_count=0, rc=None,
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    work_dir.mkdir(parents=True, exist_ok=True)
    home = work_dir / ".home"
    (home / ".pi" / "agent").mkdir(parents=True, exist_ok=True)
    (work_dir / ".tmp").mkdir(parents=True, exist_ok=True)
    write_models_shim(Path(cfg["models_json"]), endpoint["provider"], home)

    if cfg.get("sandbox", True):
        cmd = _bwrap_cmd(cfg, unit, out_dir, work_dir, home,
                         (ep_host(endpoint),))
    else:
        cmd = []
    cmd += _agent_args(cfg, endpoint)

    t0 = time.time()
    ndjson = transcript.with_suffix(".ndjson")
    errf = transcript.with_suffix(".stderr")
    # kernel-enforced egress: start through the root attach helper, which
    # enters the guard cgroup *before* exec (raises here, in the parent, if
    # the guard is enabled but not installed)
    cmd = netguard.wrap_argv(cfg, cmd)
    proc = subprocess.Popen(
        cmd, stdin=subprocess.PIPE, stdout=open(ndjson, "wb"),
        stderr=open(errf, "wb"), start_new_session=True)
    try:
        proc.communicate(unit.prompt.encode("utf-8"), timeout=timeout)
        res["rc"] = proc.returncode
    except subprocess.TimeoutExpired:
        res["timed_out"] = True
        res["detail"] = f"TIMEOUT after {timeout:.0f}s"
        _kill_sandbox(proc)
        try:
            proc.wait(timeout=20)
        except subprocess.TimeoutExpired:
            pass
        res["rc"] = -99
    except BaseException:
        # interrupt or crash: never leave a sandbox running behind us
        _kill_sandbox(proc)
        raise
    res["wall_s"] = round(time.time() - t0, 1)

    if not res["timed_out"]:
        _parse_transcript(ndjson, out_dir, res)

    if not keep_work:
        shutil.rmtree(work_dir, ignore_errors=True)
    return res


def teardown(unit: Unit) -> None:
    """Run a custom task's teardown hook, if it has one."""
    if unit.task_dir is None:
        return
    script = unit.task_dir / "teardown.sh"
    if script.is_file():
        try:
            subprocess.run(["/bin/sh", str(script)], capture_output=True, timeout=60)
        except (subprocess.TimeoutExpired, OSError):
            pass
