#!/usr/bin/env python3
"""Verifier for math-number-theory-002.

Grading scope: the last non-empty line of the model's response must be exactly
`FINAL: first=<int> count=<int>` with the CRT solution and the in-range count.

Pure: reads only the response text (or $OUT_DIR/response.txt).
"""
import argparse
import json
import os
import re
import sys

EXPECTED_FIRST = 269
EXPECTED_COUNT = 500
FINAL_LINE = re.compile(r"^FINAL:\s*first=(\d+)\s+count=(\d+)\s*$")


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
                    "'FINAL: first=<int> count=<int>'; got %r" % final[:120])

    first, count = int(m.group(1)), int(m.group(2))
    if (first, count) == (EXPECTED_FIRST, EXPECTED_COUNT):
        emit(True, "first=269 count=500")
    emit(False, "wrong values: first=%d (expected 269), count=%d (expected 500)"
                % (first, count))


if __name__ == "__main__":
    main()