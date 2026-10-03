#!/usr/bin/env python3
"""Verifier for science-chemistry-101.

Grading scope: the last non-empty line of the model's response must be exactly
`FINAL: koh_g=<3dp> k2so4_g=<3dp>` with the two stoichiometric masses rounded
half-up to 3 decimal places.

Pure: reads only the response text (or $OUT_DIR/response.txt).
"""
import argparse
from decimal import Decimal
import json
import os
import re
import sys

EXPECTED = (Decimal("11.222"), Decimal("17.426"))
FINAL_LINE = re.compile(r"^FINAL:\s*koh_g=(-?\d+\.\d+)\s+k2so4_g=(-?\d+\.\d+)\s*$")


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
                    "'FINAL: koh_g=<3dp> k2so4_g=<3dp>'; got %r" % final[:120])

    raw = (m.group(1), m.group(2))
    if any(len(v.split(".")[1]) != 3 for v in raw):
        emit(False, "masses must be given to exactly 3 decimal places; got %r" % (raw,))

    got = (Decimal(raw[0]), Decimal(raw[1]))
    if got == EXPECTED:
        emit(True, "koh_g=11.222 k2so4_g=17.426")
    emit(False, "wrong values: koh_g=%s (expected 11.222), k2so4_g=%s (expected 17.426)"
                % (raw[0], raw[1]))


if __name__ == "__main__":
    main()