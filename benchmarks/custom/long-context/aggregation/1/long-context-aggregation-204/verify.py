#!/usr/bin/env python3
"""Verifier for long-context-aggregation-204.

Grading scope: the last non-empty line of the model's response must be exactly
`FINAL: total_cents=<int> count=<int>` giving the exact-cent sum and the count
of records whose category is exactly SUPPLIES.

Pure: reads only the response text (or $OUT_DIR/response.txt).
"""
import argparse
import json
import os
import re
import sys

EXPECTED_TOTAL = 357104
EXPECTED_COUNT = 32
FINAL_LINE = re.compile(r"^FINAL:\s*total_cents=(\d+)\s+count=(\d+)\s*$")


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
                    "'FINAL: total_cents=<integer> count=<integer>'; got %r"
             % final[:120])

    total, count = int(m.group(1)), int(m.group(2))
    if (total, count) == (EXPECTED_TOTAL, EXPECTED_COUNT):
        emit(True, "total_cents=357104 count=32")
    emit(False, "wrong aggregation: got total_cents=%d count=%d "
                "(expected total_cents=357104 count=32)" % (total, count))


if __name__ == "__main__":
    main()
