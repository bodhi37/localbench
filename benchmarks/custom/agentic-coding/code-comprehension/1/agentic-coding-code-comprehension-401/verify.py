#!/usr/bin/env python3
"""Verifier for agentic-coding-code-comprehension-401.

Grading scope: the last non-empty line of the model's response must be exactly
`FINAL: stdout=<printed line> fix_line=<int>` with the program's exact output and
the 1-based line number of the `int(v / width)` statement in resources/normalize.py.

Pure: reads only the response text (or $OUT_DIR/response.txt).
"""
import argparse
import json
import os
import re
import sys

EXPECTED_STDOUT = "0:3,1:2,2:1"
EXPECTED_FIX_LINE = 4
FINAL_LINE = re.compile(r"^FINAL:\s*stdout=(\S+)\s+fix_line=(\d+)\s*$")


def emit(passed, detail):
    print(json.dumps({"pass": bool(passed), "detail": detail}))
    sys.exit(0 if passed else 1)


def load_response(args):
    for path in (args.response, os.path.join(args.out_dir or "", "response.txt")):
        if path and os.path.isfile(path):
            with open(path, encoding="utf-8", errors="replace") as fh:
                return fh.read()
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task-dir")
    ap.add_argument("--out-dir")
    ap.add_argument("--response")
    args = ap.parse_args()

    text = load_response(args)
    if text is None:
        emit(False, "no response text supplied (pass --response FILE)")

    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        emit(False, "empty response")
    m = FINAL_LINE.match(lines[-1])
    if not m:
        emit(False, "last non-empty line is not of the form "
                    "'FINAL: stdout=<line> fix_line=<int>'; got %r" % lines[-1][:140])

    stdout, fix_line = m.group(1), int(m.group(2))
    if (stdout, fix_line) == (EXPECTED_STDOUT, EXPECTED_FIX_LINE):
        emit(True, "stdout=0:3,1:2,2:1 fix_line=4")
    emit(False, "wrong: stdout=%r (expected %r), fix_line=%d (expected %d)"
                % (stdout, EXPECTED_STDOUT, fix_line, EXPECTED_FIX_LINE))


if __name__ == "__main__":
    main()