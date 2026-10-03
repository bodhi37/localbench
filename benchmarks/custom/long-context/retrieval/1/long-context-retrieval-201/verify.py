#!/usr/bin/env python3
"""Verifier for long-context-retrieval-201.

Grading scope: the last non-empty line of the model's response must be exactly
`FINAL: entry=<int> bearing=<1dp> op=<surname>` identifying the single logbook
record whose drift value is 0.0093.

Pure: reads only the response text (or $OUT_DIR/response.txt).
"""
import argparse
from decimal import Decimal
import json
import os
import re
import sys

EXPECTED_ENTRY = 190
EXPECTED_BEARING = Decimal("326.4")
EXPECTED_OP = "Iyer"
FINAL_LINE = re.compile(r"^FINAL:\s*entry=(\d+)\s+bearing=(\d+\.\d)\s+op=([A-Za-z][A-Za-z'\-]*)\s*$")


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
                    "'FINAL: entry=<int> bearing=<1dp> op=<surname>'; got %r" % final[:120])

    entry = int(m.group(1))
    bearing = Decimal(m.group(2))
    op = m.group(3)
    if (entry, bearing, op) == (EXPECTED_ENTRY, EXPECTED_BEARING, EXPECTED_OP):
        emit(True, "entry=190 bearing=326.4 op=Iyer")
    emit(False, "wrong record: got entry=%d bearing=%s op=%s "
                "(expected entry=190 bearing=326.4 op=Iyer)" % (entry, bearing, op))


if __name__ == "__main__":
    main()