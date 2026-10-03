#!/usr/bin/env python3
"""Verifier for agentic-coding-debugging-402.

Grading scope: $OUT_DIR/window.py must import cleanly and silently, and all
three functions must match the prompt's specification on every fixed vector in
tests/vectors.json.

Pure: reads $OUT_DIR/window.py and the harness-side tests/vectors.json; runs the
candidate module in a subprocess with a timeout and a scrubbed environment.
"""
import argparse
import copy
import json
import os
import subprocess
import sys
import tempfile

TIMEOUT_SECONDS = 30
MARKER = "__LOCALBENCH_RESULTS__"

RUNNER = r'''
import copy, importlib.util, json, sys

mod_path, vec_path = sys.argv[1], sys.argv[2]
spec = importlib.util.spec_from_file_location("candidate_window", mod_path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)                      # import-time output is caught

with open(vec_path, encoding="utf-8") as fh:
    vectors = json.load(fh)["vectors"]

out = []
for v in vectors:
    rec = {"id": v["id"]}
    fn = getattr(mod, v["fn"], None)
    if not callable(fn):
        rec["error"] = "missing or non-callable function %s" % v["fn"]
        out.append(rec)
        continue
    args = copy.deepcopy(v["args"])
    before = copy.deepcopy(args[0]) if v.get("no_mutation") and args else None
    try:
        got = fn(*args)
    except Exception as exc:
        rec["error"] = "%s: %s" % (type(exc).__name__, exc)
        out.append(rec)
        continue
    if v.get("no_mutation") and args and args[0] != before:
        rec["error"] = "mutated its input list"
        out.append(rec)
        continue
    rec["ok"] = got == v["expect"]
    if not rec["ok"]:
        rec["got"] = repr(got)
        rec["want"] = repr(v["expect"])
    out.append(rec)

print("__LOCALBENCH_RESULTS__" + json.dumps(out))
'''


def emit(passed, detail):
    print(json.dumps({"pass": bool(passed), "detail": detail}))
    sys.exit(0 if passed else 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task-dir")
    ap.add_argument("--out-dir")
    ap.add_argument("--response")
    args = ap.parse_args()

    model_path = os.path.join(args.out_dir or "", "window.py")
    if not os.path.isfile(model_path):
        emit(False, "required deliverable $OUT_DIR/window.py is missing")

    vectors_path = os.path.join(args.task_dir or ".", "tests", "vectors.json")
    if not os.path.isfile(vectors_path):
        emit(False, "harness error: tests/vectors.json not found")

    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as fh:
        fh.write(RUNNER)
        runner_path = fh.name

    env = {"PATH": "/usr/bin:/bin", "PYTHONDONTWRITEBYTECODE": "1", "HOME": "/nonexistent"}
    try:
        proc = subprocess.run(
            [sys.executable or "python3", runner_path, model_path, vectors_path],
            capture_output=True, text=True, timeout=TIMEOUT_SECONDS,
            cwd=args.out_dir or ".", env=env,
        )
    except subprocess.TimeoutExpired:
        emit(False, "candidate module did not finish within %ds" % TIMEOUT_SECONDS)
    finally:
        try:
            os.unlink(runner_path)
        except OSError:
            pass

    stdout = proc.stdout or ""
    if MARKER not in stdout:
        emit(False, "candidate module could not be exercised (rc=%d, stderr=%r)"
                    % (proc.returncode, (proc.stderr or "")[-300:]))
    prefix, payload = stdout.split(MARKER, 1)
    if prefix.strip():
        emit(False, "module printed or executed at import time: %r" % prefix[:160])

    results = json.loads(payload.strip().splitlines()[0])
    failures = [r for r in results if not r.get("ok")]
    if not failures:
        emit(True, "all %d vectors pass (import is silent, no input mutation)" % len(results))
    details = "; ".join(
        "%s: %s" % (r["id"], r.get("error") or "got %s want %s" % (r.get("got"), r.get("want")))
        for r in failures[:6])
    emit(False, "%d/%d vectors failed: %s" % (len(failures), len(results), details))


if __name__ == "__main__":
    main()