#!/usr/bin/env python3
"""Verifier for math-optimization-008.

Grading scope: the last non-empty line of the model's response must be exactly
`FINAL: chosen=<letters> total=<int>` with the unique optimal 0/1 knapsack
subset (alphabetical) and its value.

Pure: reads only the response text (or $OUT_DIR/response.txt), no network,
no clock, no randomness.
"""
import argparse
import json
import os
import re
import sys

EXPECTED_CHOSEN = "B,C,F"
EXPECTED_TOTAL = 57
FINAL_LINE = re.compile(r"^FINAL:\s*chosen=([A-F](?:,[A-F])*)\s+total=(\d+)\s*$")


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
                     "'FINAL: chosen=<letters> total=<int>'; got %r" % final[:120])

    chosen, total = m.group(1), int(m.group(2))
    if chosen == EXPECTED_CHOSEN and total == EXPECTED_TOTAL:
        emit(True, "chosen=B,C,F total=57")
    emit(False, "wrong values: chosen=%s (expected B,C,F), total=%d (expected 57)"
                % (chosen, total))


if __name__ == "__main__":
    main()
