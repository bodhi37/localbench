#!/usr/bin/env python3
"""Verifier for cybersecurity-access-507."
Pure: reads only the response text (or $OUT_DIR/response.txt).
Answers live in harness-side tests/expected.json, never in prompt.md.
"""
import argparse
import json
import os
import re
import sys

FINAL_LINE = re.compile(r"^FINAL:\s*allowed=(\d+)\s+denied=(\d+)\s+r017=(allow|deny)\s*$")


def emit(passed, detail):
    print(json.dumps({"pass": bool(passed), "detail": detail}))
    sys.exit(0 if passed else 1)


def load_response(args):
    for path in (args.response, os.path.join(args.out_dir or "", "response.txt")):
        if path and os.path.isfile(path):
            with open(path, encoding="utf-8", errors="replace") as fh:
                return fh.read()
    return None


def load_expected(task_dir):
    base = task_dir or os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base, "tests", "expected.json")
    if not os.path.isfile(path):
        emit(False, "harness misconfigured: tests/expected.json not found")
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task-dir")
    ap.add_argument("--out-dir")
    ap.add_argument("--response")
    args = ap.parse_args()
    expected = load_expected(args.task_dir)
    text = load_response(args)
    if text is None:
        emit(False, "no response text supplied (pass --response FILE)")
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        emit(False, "empty response")
    m = FINAL_LINE.match(lines[-1])
    if not m:
        emit(False, "last non-empty line is not of the required FINAL: form; got %r"
                    % lines[-1][:150])
    got = {"allowed": int(m.group(1)), "denied": int(m.group(2)), "r017": m.group(3)}
    if got["allowed"] + got["denied"] != 30:
        emit(False, "allowed+denied must equal 30; got %s" % got)
    if got == {k: expected[k] for k in got}:
        emit(True, "RBAC audit correct: %s" % got)
    emit(False, "mismatch: got %s" % got)


if __name__ == "__main__":
    main()
