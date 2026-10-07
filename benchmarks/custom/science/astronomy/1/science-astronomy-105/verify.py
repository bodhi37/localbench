#!/usr/bin/env python3
"""Verifier for science-astronomy-105.

Grading scope: the last non-empty line of the model's response must be exactly
`FINAL: d_pc=<int> d_ly=<3dp>` with the distance-modulus distance
(160 pc, 521.920 ly).

Pure: reads only the response text (or $OUT_DIR/response.txt).
"""
import argparse
from decimal import Decimal
import json
import os
import re
import sys

EXPECTED_PC = "160"
EXPECTED_LY = Decimal("521.920")
FINAL_LINE = re.compile(r"^FINAL:\s*d_pc=(\d+)\s+d_ly=(-?\d+\.\d+)\s*$")


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
                     "'FINAL: d_pc=<integer> d_ly=<3dp>'; got %r" % final[:120])

    raw_pc, raw_ly = m.group(1), m.group(2)
    if len(raw_ly.split(".")[1]) != 3:
        emit(False, "d_ly must be given to exactly 3 decimal places; got %r" % (raw_ly,))

    if raw_pc == EXPECTED_PC and Decimal(raw_ly) == EXPECTED_LY:
        emit(True, "d_pc=160 d_ly=521.920")
    emit(False, "wrong values: d_pc=%s (expected 160), d_ly=%s (expected 521.920)"
                % (raw_pc, raw_ly))


if __name__ == "__main__":
    main()
