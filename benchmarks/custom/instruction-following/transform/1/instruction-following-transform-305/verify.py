#!/usr/bin/env python3
"""Verifier for instruction-following-transform-305.

Grading scope: the whole response, after trimming blank lines at the very
start/end, must be exactly the seven declared lines in order with the derived
values. Pure: reads only the response text.
"""
import argparse
import json
import os
import sys

EXPECTED = [
    "BEGIN LINES",
    "L1=solar-panels-generate-power",
    "L2=quiet-rivers-flow-north",
    "L3=brisk-winds-lift-kites",
    "COUNT=003",
    "CHECK=072",
    "END LINES",
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
        emit(False, "expected exactly 7 lines, got %d: %r" % (len(lines), lines[:12]))
    if lines == EXPECTED:
        emit(True, "block matches exactly")
    diffs = ["line %d: got %r want %r" % (i + 1, g, w)
             for i, (g, w) in enumerate(zip(lines, EXPECTED)) if g != w]
    emit(False, "block mismatch: " + "; ".join(diffs))


if __name__ == "__main__":
    main()
