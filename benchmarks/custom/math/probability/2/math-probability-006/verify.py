#!/usr/bin/env python3
"""Verifier for math-probability-006.

Grading scope: the last non-empty line of the model's response must be exactly
`FINAL: p_num=<int> p_den=<int>` equal to the reduced conditional probability
72/371 derived in prompt.md.

Pure: reads only the response text (or $OUT_DIR/response.txt), no network,
no clock, no randomness.
"""
import argparse
import json
import os
import re
import sys

EXPECTED_NUM = 72
EXPECTED_DEN = 371
FINAL_LINE = re.compile(r"^FINAL:\s*p_num=(\d+)\s+p_den=(\d+)\s*$")


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
                     "'FINAL: p_num=<int> p_den=<int>'; got %r" % final[:120])

    num, den = int(m.group(1)), int(m.group(2))
    if (num, den) == (EXPECTED_NUM, EXPECTED_DEN):
        emit(True, "p_num=72 p_den=371")
    emit(False, "wrong values: p_num=%d (expected 72), p_den=%d (expected 371)"
                % (num, den))


if __name__ == "__main__":
    main()
