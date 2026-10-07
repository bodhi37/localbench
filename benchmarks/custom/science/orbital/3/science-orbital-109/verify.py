#!/usr/bin/env python3
"""Verifier for science-orbital-109.

Grading scope: the last non-empty line of the model's response must be exactly
`FINAL: dv1_kms=<3dp> T_h=<3dp>` with the transfer-orbit results
(2.426 km/s, 10.550 h) rounded half-up to 3 decimal places.

Pure: reads only the response text (or $OUT_DIR/response.txt).
"""
import argparse
from decimal import Decimal
import json
import os
import re
import sys

EXPECTED = (Decimal("2.426"), Decimal("10.550"))
FINAL_LINE = re.compile(r"^FINAL:\s*dv1_kms=(-?\d+\.\d+)\s+T_h=(-?\d+\.\d+)\s*$")


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
                     "'FINAL: dv1_kms=<3dp> T_h=<3dp>'; got %r" % final[:120])

    raw = (m.group(1), m.group(2))
    if any(len(v.split(".")[1]) != 3 for v in raw):
        emit(False, "values must be given to exactly 3 decimal places; got %r" % (raw,))

    got = (Decimal(raw[0]), Decimal(raw[1]))
    if got == EXPECTED:
        emit(True, "dv1_kms=2.426 T_h=10.550")
    emit(False, "wrong values: dv1_kms=%s (expected 2.426), T_h=%s (expected 10.550)"
                % (raw[0], raw[1]))


if __name__ == "__main__":
    main()
