#!/usr/bin/env python3
"""Verifier for math-sequences-007.

Grading scope: the last non-empty line of the model's response must be exactly
`FINAL: a6=<int> digit_sum=<int>` with the exact 6th term of the nonlinear
recurrence and its digit sum.

Pure: reads only the response text (or $OUT_DIR/response.txt), no network,
no clock, no randomness.
"""
import argparse
import json
import os
import re
import sys

EXPECTED_A6 = 3263443
EXPECTED_DIGIT_SUM = 25
FINAL_LINE = re.compile(r"^FINAL:\s*a6=(\d+)\s+digit_sum=(\d+)\s*$")


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
                     "'FINAL: a6=<int> digit_sum=<int>'; got %r" % final[:120])

    a6, digit_sum = int(m.group(1)), int(m.group(2))
    if (a6, digit_sum) == (EXPECTED_A6, EXPECTED_DIGIT_SUM):
        emit(True, "a6=3263443 digit_sum=25")
    emit(False, "wrong values: a6=%d (expected 3263443), digit_sum=%d (expected 25)"
                % (a6, digit_sum))


if __name__ == "__main__":
    main()
