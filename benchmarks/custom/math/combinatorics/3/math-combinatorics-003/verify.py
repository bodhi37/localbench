#!/usr/bin/env python3
"""Verifier for math-combinatorics-003.

Grading scope: the last non-empty line of the model's response must be exactly
`FINAL: necklaces=<int> residue=<int>` where necklaces = 2896 (Burnside over the
rotation group C12 acting on colourings with 4/4/4 beads) and residue = 2896 mod 97.

Pure: reads only the response text (or $OUT_DIR/response.txt).
"""
import argparse
import json
import os
import re
import sys

EXPECTED_NECKLACES = 2896
EXPECTED_RESIDUE = 83
FINAL_LINE = re.compile(r"^FINAL:\s*necklaces=(\d+)\s+residue=(\d+)\s*$")


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
                    "'FINAL: necklaces=<int> residue=<int>'; got %r" % final[:120])

    necklaces, residue = int(m.group(1)), int(m.group(2))
    ok = (necklaces == EXPECTED_NECKLACES) and (residue == EXPECTED_RESIDUE)
    if ok:
        emit(True, "necklaces=2896 residue=83")
    emit(False, "wrong values: necklaces=%d (expected 2896), residue=%d (expected 83)"
                % (necklaces, residue))


if __name__ == "__main__":
    main()