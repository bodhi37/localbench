#!/usr/bin/env python3
"""Verifier for cybersecurity-securecode-506.

Grading scope: LAST response line names the fixed file; the file itself is
checked in $OUT_DIR by (a) static bans and (b) functional vectors executed in a
child process with a timeout (stdlib subprocess only, untrusted code never runs
in this process).
"""
import argparse
import ast
import json
import os
import re
import subprocess
import sys
import textwrap

FINAL_LINE = re.compile(r"^FINAL:\s*fixed_file=(\S+)\s*$")

DRIVER = textwrap.dedent("""
    import importlib.util, json, sqlite3, sys
    from unittest import mock
    path = sys.argv[1]
    spec = importlib.util.spec_from_file_location("fixedmod", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    out = {}
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE users (name TEXT)")
    conn.executemany("INSERT INTO users VALUES (?)", [("admin",), ("jdoe",)])
    out["inject_blocked"] = (mod.lookup_user(conn, "admin' OR '1'='1") == [])
    out["exact_match"] = (mod.lookup_user(conn, "admin") == [("admin",)])
    with mock.patch("subprocess.run") as mr:
        mod.run_backup("a; rm -rf /")
        argv, kw = mr.call_args[0][0], mr.call_args[1]
        out["argv_is_list"] = isinstance(argv, list)
        out["host_single_arg"] = ("a; rm -rf /" in argv) if isinstance(argv, list) else False
        out["no_shell"] = (kw.get("shell", False) is False)
    t1, t2 = mod.gen_token(), mod.gen_token()
    out["token_hex32"] = all(isinstance(t, str) and len(t) == 32
                             and all(c in "0123456789abcdef" for c in t) for t in (t1, t2))
    out["token_unique"] = (t1 != t2)
    print(json.dumps(out))
""")


def emit(passed, detail):
    print(json.dumps({"pass": bool(passed), "detail": detail}))
    sys.exit(0 if passed else 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task-dir")
    ap.add_argument("--out-dir")
    ap.add_argument("--response")
    args = ap.parse_args()
    text = None
    for path in (args.response, os.path.join(args.out_dir or "", "response.txt")):
        if path and os.path.isfile(path):
            with open(path, encoding="utf-8", errors="replace") as fh:
                text = fh.read()
    if text is None:
        emit(False, "no response text supplied (pass --response FILE)")
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines or not FINAL_LINE.match(lines[-1]):
        emit(False, "last non-empty line must be FINAL: fixed_file=<name>; got %r"
                    % (lines[-1][:150] if lines else ""))
    fname = FINAL_LINE.match(lines[-1]).group(1)
    fpath = os.path.join(args.out_dir or "", os.path.basename(fname))
    if not os.path.isfile(fpath):
        emit(False, "fixed file not found at %s" % fpath)
    with open(fpath, encoding="utf-8", errors="replace") as fh:
        src = fh.read()
    if re.search(r"shell\s*=\s*True", src):
        emit(False, "banned pattern: shell=True still present")
    if re.search(r"\bimport\s+random\b|\bfrom\s+random\b|\brandom\.", src):
        emit(False, "banned pattern: random module still used (use secrets)")
    for i, ln in enumerate(src.splitlines(), 1):
        if "execute" in ln and any(p in ln for p in ["+", "%", ".format(", 'f"', "f'"]):
            emit(False, "banned pattern: string-built SQL on line %d" % i)
    if "?" not in src:
        emit(False, "missing parameterized placeholder (?)")
    if "secrets" not in src:
        emit(False, "missing secrets module usage")
    if not re.search(r"shell\s*=\s*False", src):
        emit(False, "run_backup must pass shell=False explicitly")
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        emit(False, "fixed file does not parse: %s" % e)
    fns = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    if not {"lookup_user", "run_backup", "gen_token"} <= fns:
        emit(False, "fixed file must define lookup_user, run_backup, gen_token")
    try:
        proc = subprocess.run([sys.executable, "-c", DRIVER, fpath],
                              capture_output=True, text=True, timeout=30)
    except subprocess.TimeoutExpired:
        emit(False, "functional vectors timed out")
    if proc.returncode != 0:
        emit(False, "functional driver failed: %s" % (proc.stderr or proc.stdout)[:300])
    try:
        res = json.loads(proc.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        emit(False, "functional driver produced no JSON")
    bad = [k for k, v in res.items() if not v]
    if bad:
        emit(False, "functional vectors failed: %s" % ",".join(sorted(bad)))
    emit(True, "secure-code fix correct: %s" % ",".join(sorted(res)))


if __name__ == "__main__":
    main()
