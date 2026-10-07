#!/usr/bin/env python3
# Verifier for agentic-coding-edge-405.
#
# Grading scope: $OUT_DIR/csvparse.py must import cleanly and silently, use only
# the standard library, and match the prompt's specification on every fixed
# vector in tests/vectors.json.
#
# Pure: reads $OUT_DIR/csvparse.py and the harness-side tests/vectors.json; runs
# the candidate module in a subprocess with a timeout and a scrubbed environment.
import argparse
import ast
import copy
import json
import os
import subprocess
import sys
import tempfile

TIMEOUT_SECONDS = 30
LARGE_TIMEOUT_SECONDS = 30
MARKER = "__LOCALBENCH_RESULTS__"
FILENAME = "csvparse.py"

RUNNER = '''
import copy, importlib.util, json, sys

mod_path, vec_path, flag = sys.argv[1], sys.argv[2], sys.argv[3]
only_large = (flag == "1")
spec = importlib.util.spec_from_file_location("candidate_mod", mod_path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

with open(vec_path, encoding="utf-8") as fh:
    vectors = json.load(fh)["vectors"]

out = []
for v in vectors:
    if bool(v.get("large", False)) != only_large:
        continue
    rec = {"id": v["id"]}
    fn = getattr(mod, v["fn"], None)
    if not callable(fn):
        rec["error"] = "missing or non-callable function %s" % v["fn"]
        out.append(rec)
        continue
    args = copy.deepcopy(v["args"])
    before = copy.deepcopy(args)
    try:
        got = fn(*args)
    except Exception as exc:
        if v.get("expect_error") and type(exc).__name__ == v["expect_error"]:
            rec["ok"] = True
        else:
            rec["error"] = "%s: %s" % (type(exc).__name__, exc)
        out.append(rec)
        continue
    if v.get("expect_error"):
        rec["error"] = "expected %s but the call succeeded" % v["expect_error"]
        out.append(rec)
        continue
    if v.get("no_mutation") and args != before:
        rec["error"] = "mutated its input"
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


def check_source_stdlib(source):
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        emit(False, "candidate module has a syntax error: %s" % exc)
    stdlib = getattr(sys, "stdlib_module_names", None) or {
        "math", "functools", "itertools", "collections", "re", "string",
        "decimal", "fractions", "statistics", "typing", "copy", "json",
    }
    for node in ast.walk(tree):
        names = []
        if isinstance(node, ast.Import):
            names = [a.name.split(".")[0] for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                names = [node.module.split(".")[0]]
        for name in names:
            if name not in stdlib:
                emit(False, "third-party import %r is not allowed" % name)
    return tree


def extra_check(tree, source):
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            mods = [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            mods = [node.module or ""]
        else:
            continue
        for m in mods:
            if m.split(".")[0] == "csv":
                emit(False, "the csv module must not be used; parse by hand")
    return None



def run_vectors(model_path, vectors_path, only_large, timeout):
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as fh:
        fh.write(RUNNER)
        runner_path = fh.name
    env = {"PATH": "/usr/bin:/bin", "PYTHONDONTWRITEBYTECODE": "1", "HOME": "/nonexistent"}
    try:
        proc = subprocess.run(
            [sys.executable or "python3", runner_path, model_path, vectors_path,
             "1" if only_large else "0"],
            capture_output=True, text=True, timeout=timeout,
            cwd=os.path.dirname(model_path) or ".", env=env,
        )
    except subprocess.TimeoutExpired:
        emit(False, "candidate module did not finish within %ds%s"
             % (timeout, " on the large input (too slow)" if only_large else ""))
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
    try:
        results = json.loads(payload.strip().splitlines()[0])
    except (ValueError, IndexError):
        emit(False, "could not parse runner output")
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task-dir")
    ap.add_argument("--out-dir")
    ap.add_argument("--response")
    args = ap.parse_args()

    model_path = os.path.join(args.out_dir or "", FILENAME)
    if not os.path.isfile(model_path):
        emit(False, "required deliverable $OUT_DIR/%s is missing" % FILENAME)

    vectors_path = os.path.join(args.task_dir or ".", "tests", "vectors.json")
    if not os.path.isfile(vectors_path):
        emit(False, "harness error: tests/vectors.json not found")

    with open(model_path, encoding="utf-8") as fh:
        source = fh.read()
    tree = check_source_stdlib(source)
    extra_check(tree, source)

    with open(vectors_path, encoding="utf-8") as fh:
        vectors = json.load(fh)["vectors"]
    small = [v for v in vectors if not v.get("large")]
    large = [v for v in vectors if v.get("large")]

    results = run_vectors(model_path, vectors_path, False, TIMEOUT_SECONDS)
    failures = [r for r in results if not r.get("ok")]
    if failures:
        details = "; ".join(
            "%s: %s" % (r["id"], r.get("error") or "got %s want %s" % (r.get("got"), r.get("want")))
            for r in failures[:6])
        emit(False, "%d/%d vectors failed: %s" % (len(failures), len(results), details))

    if large:
        results = run_vectors(model_path, vectors_path, True, LARGE_TIMEOUT_SECONDS)
        failures = [r for r in results if not r.get("ok")]
        if failures:
            details = "; ".join(
                "%s: %s" % (r["id"], r.get("error") or "got %s want %s" % (r.get("got"), r.get("want")))
                for r in failures[:6])
            emit(False, "large-input gate failed: %s" % details)
        emit(True, "all %d vectors pass plus the large-input timing gate (import is silent)" % len(small))
    mut = any(v.get("no_mutation") for v in small)
    emit(True, "all %d vectors pass (import is silent%s)" % (len(results), ", no input mutation" if mut else ""))


if __name__ == "__main__":
    main()
