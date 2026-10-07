#!/usr/bin/env python3
"""Verifier for science-thermo-106.

Grading scope: the last non-empty line of the model's response must be exactly
`FINAL: T_eq=<3dp> q_hot=<3dp>` with the calorimetry equilibrium results
(48.513 C, 22.486 kJ) rounded half-up to 3 decimal places.

Pure: reads only the response text (or $OUT_DIR/response.txt).
"""
import argparse
from decimal import Decimal
import json
import os
import re
import sys

EXPECTED = (Decimal("48.513"), Decimal("22.486"))
FINAL_LINE = re.compile(r"^FINAL:\s*T_eq=(-?\d+\.\d+)\s+q_hot=(-?\d+\.\d+)\s*$")


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
                     "'FINAL: T_eq=<3dp> q_hot=<3dp>'; got %r" % final[:120])

    raw = (m.group(1), m.group(2))
    if any(len(v.split(".")[1]) != 3 for v in raw):
        emit(False, "values must be given to exactly 3 decimal places; got %r" % (raw,))

    got = (Decimal(raw[0]), Decimal(raw[1]))
    if got == EXPECTED:
        emit(True, "T_eq=48.513 q_hot=22.486")
    emit(False, "wrong values: T_eq=%s (expected 48.513), q_hot=%s (expected 22.486)"
                % (raw[0], raw[1]))


if __name__ == "__main__":
    main()
