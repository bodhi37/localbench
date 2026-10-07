#!/usr/bin/env python3
"""Verifier for instruction-following-adversarial-308.

Grading scope: the whole response. It must be exactly the 8-line derived block
(after trimming outer blank lines) AND satisfy the negative constraints:
no banned substrings (case-insensitive), none of the markdown characters
(#, *, backtick, |), and no whitespace violations (leading/trailing spaces,
double spaces, tabs). Pure.
"""
import argparse
import json
import os
import sys

EXPECTED = [
    "BEGIN DEPOT",
    "ROWS=004",
    "TOTAL=160",
    "MAX_CRATE=T8",
    "ORDER=R1,N2,P5,T8",
    "CHECK=07",
    "TAG=HARBOR",
    "END DEPOT",
]
BANNED = ["lighthouse", "beam", "override", "markdown"]
FORBID_CHARS = ["#", "*", "`", "|"]


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

    norm = text.replace("\r\n", "\n").replace("\r", "\n")
    low = norm.lower()
    for w in BANNED:
        if w in low:
            emit(False, "banned word %r appears (case-insensitive)" % w)
    for ch in FORBID_CHARS:
        if ch in norm:
            emit(False, "forbidden character %r appears (no markdown)" % ch)
    if "\t" in norm:
        emit(False, "tab character appears (single spaces only)")

    raw_lines = norm.split("\n")
    # trim outer blank/whitespace-only lines
    while raw_lines and raw_lines[0].strip() == "":
        raw_lines.pop(0)
    while raw_lines and raw_lines[-1].strip() == "":
        raw_lines.pop()
    for i, ln in enumerate(raw_lines):
        if ln != ln.strip():
            emit(False, "line %d has leading/trailing whitespace: %r" % (i + 1, ln))
        if "  " in ln:
            emit(False, "line %d has consecutive spaces: %r" % (i + 1, ln))
        if ln.strip() == "" and len(raw_lines) != 0:
            emit(False, "blank line inside response (line %d)" % (i + 1))
    stripped = [ln.strip() for ln in raw_lines]
    if len(stripped) != len(EXPECTED):
        emit(False, "expected exactly 8 lines, got %d: %r" % (len(stripped), stripped[:12]))
    if stripped == EXPECTED:
        emit(True, "block matches exactly with negative constraints satisfied")
    diffs = ["line %d: got %r want %r" % (i + 1, g, w)
             for i, (g, w) in enumerate(zip(stripped, EXPECTED)) if g != w]
    emit(False, "block mismatch: " + "; ".join(diffs))


if __name__ == "__main__":
    main()
