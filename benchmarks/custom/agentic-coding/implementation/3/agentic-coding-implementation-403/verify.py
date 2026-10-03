#!/usr/bin/env python3
"""Verifier for agentic-coding-implementation-403.

Grading scope: $OUT_DIR/calc.py must import cleanly and silently, and
evaluate(expr) must match the prompt's grammar on every fixed vector in
tests/vectors.json, including the required exception types and exact
unbounded-precision integer results.

Pure: reads $OUT_DIR/calc.py and the harness-side tests/vectors.json; runs the
candidate module in a subprocess with a timeout and a scrubbed environment.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile

TIMEOUT_SECONDS = 30
MARKER = "__LOCALBENCH_RESULTS__"

RUNNER = r'''
import importlib.util, json, sys

mod_path, vec_path = sys.argv[1], sys.argv[2]
spec = importlib.util.spec_from_file_location("candidate_calc", mod_path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)                      # import-time output is caught

with open(vec_path, encoding="utf-8") as fh:
    vectors = json.load(fh)["vectors"]

out = []
fn = getattr(mod, "evaluate", None)
for v in vectors:
    rec = {"id": v["id"]}
    if not callable(fn):
        rec["error"] = "module does not define a callable evaluate"
        out.append(rec)
        continue
    try:
        got = fn(v["expr"])
    except Exception as exc:
        if v["expect_error"]:
            rec["ok"] = type(exc).__name__ == v["expect_error"]
            if not rec["ok"]:
                rec["error"] = "raised %s, expected %s" % (type(exc).__name__, v["expect_error"])
        else:
            rec["error"] = "raised %s: %s" % (type(exc).__name__, exc)
        out.append(rec)
        continue
    if v["expect_error"]:
        rec["error"] = "no exception raised (expected %s); returned %r" % (v["expect_error"], got)
    else:
        ok = isinstance(got, int) and not isinstance(got, bool) and got == v["expect"]
        rec["ok"] = ok
        if not ok:
            rec["error"] = "got %r (%s), want %r" % (got, type(got).__name__, v["expect"])
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

    model_path = os.path.join(args.out_dir or "", "calc.py")
    if not os.path.isfile(model_path):
        emit(False, "required deliverable $OUT_DIR/calc.py is missing")

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
        emit(True, "all %d vectors pass (values, truncating division, error types, silent import)"
                   % len(results))
    details = "; ".join("%s: %s" % (r["id"], r.get("error")) for r in failures[:6])
    emit(False, "%d/%d vectors failed: %s" % (len(failures), len(results), details))


if __name__ == "__main__":
    main()