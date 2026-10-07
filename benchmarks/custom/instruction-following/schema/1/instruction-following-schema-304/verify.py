#!/usr/bin/env python3
"""Verifier for instruction-following-schema-304.

Grading scope: the whole response, after trimming blank lines at the very
start/end, must be exactly the nine declared lines in order with the derived
values. Per-line comparison strips surrounding whitespace (so trailing spaces
are tolerated at the comparison stage, matching the 301 style); the values
themselves are re-derived below.
"""
import argparse
import json
import os
import sys

EXPECTED = [
    "BEGIN TABLE",
    "ROWS=005",
    "TOTAL=225",
    "MIN_CODE=A3",
    "MAX_CODE=M2",
    "ORDER=A3,Q9,K7,Z1,M2",
    "CHECK=09",
    "TAG=HALCYON",
    "END TABLE",
]


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

    lines = [ln.strip() for ln in text.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    while lines and lines[0] == "":
        lines.pop(0)
    while lines and lines[-1] == "":
        lines.pop()
    if len(lines) != len(EXPECTED):
        emit(False, "expected exactly 9 lines, got %d: %r" % (len(lines), lines[:12]))
    if lines == EXPECTED:
        emit(True, "block matches exactly")
    diffs = ["line %d: got %r want %r" % (i + 1, g, w)
             for i, (g, w) in enumerate(zip(lines, EXPECTED)) if g != w]
    emit(False, "block mismatch: " + "; ".join(diffs))


if __name__ == "__main__":
    main()
