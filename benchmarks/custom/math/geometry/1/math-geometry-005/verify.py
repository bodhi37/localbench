#!/usr/bin/env python3
"""Verifier for math-geometry-005.

Grading scope: the last non-empty line of the model's response must be exactly
`FINAL: area=<int> cost=<int>` with pi=22/7 composite area and unit cost applied.

Pure: reads only the response text (or $OUT_DIR/response.txt), no network,
no clock, no randomness.
"""
import argparse
import json
import os
import re
import sys

EXPECTED_AREA = 103
EXPECTED_COST = 3811
FINAL_LINE = re.compile(r"^FINAL:\s*area=(\d+)\s+cost=(\d+)\s*$")


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
                     "'FINAL: area=<int> cost=<int>'; got %r" % final[:120])

    area, cost = int(m.group(1)), int(m.group(2))
    if (area, cost) == (EXPECTED_AREA, EXPECTED_COST):
        emit(True, "area=103 cost=3811")
    emit(False, "wrong values: area=%d (expected 103), cost=%d (expected 3811)"
                % (area, cost))


if __name__ == "__main__":
    main()
