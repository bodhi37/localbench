#!/usr/bin/env python3
"""Verifier for math-algebra-004.

Grading scope: the last non-empty line of the model's response must be exactly
`FINAL: x=<int> y=<int> z=<int> w=<int>` and all four integers must equal the
exact solution of the linear system plus the wear index defined in prompt.md.

Pure: reads only the response text (or $OUT_DIR/response.txt), no network,
no clock, no randomness.
"""
import argparse
import json
import os
import re
import sys

EXPECTED = (5, 2, 2, 45)
FINAL_LINE = re.compile(
    r"^FINAL:\s*x=(-?\d+)\s+y=(-?\d+)\s+z=(-?\d+)\s+w=(-?\d+)\s*$"
)


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

    final = lines[-1]
    m = FINAL_LINE.match(final)
    if not m:
        emit(False, "last non-empty line is not of the form "
                     "'FINAL: x=<int> y=<int> z=<int> w=<int>'; got %r" % final[:120])

    got = tuple(int(m.group(i)) for i in range(1, 5))
    if got == EXPECTED:
        emit(True, "x=5 y=2 z=2 w=45")
    emit(False, "wrong values: x=%d y=%d z=%d w=%d (expected x=5 y=2 z=2 w=45)" % got)


if __name__ == "__main__":
    main()
