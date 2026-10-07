#!/usr/bin/env python3
"""Verifier for science-genetics-108.

Grading scope: the last non-empty line of the model's response must be exactly
`FINAL: p1=<fraction> n1=<int> p2=<fraction> n2=<int>` with the trihybrid
expectations (p1=1/32, n1=100, p2=27/64, n2=1350). Fractions must match exactly
in lowest terms.

Pure: reads only the response text (or $OUT_DIR/response.txt).
"""
import argparse
import json
import os
import re
import sys

EXPECTED = ("1/32", "100", "27/64", "1350")
FINAL_LINE = re.compile(
    r"^FINAL:\s*p1=(\d+/\d+)\s+n1=(\d+)\s+p2=(\d+/\d+)\s+n2=(\d+)\s*$")


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
                     "'FINAL: p1=<fraction> n1=<integer> p2=<fraction> n2=<integer>'; "
                     "got %r" % final[:120])

    raw = (m.group(1), m.group(2), m.group(3), m.group(4))
    if raw == EXPECTED:
        emit(True, "p1=1/32 n1=100 p2=27/64 n2=1350")
    emit(False, "wrong values: p1=%s (expected 1/32), n1=%s (expected 100), "
                 "p2=%s (expected 27/64), n2=%s (expected 1350)" % raw)


if __name__ == "__main__":
    main()
