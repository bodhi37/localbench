#!/usr/bin/env python3
"""Verifier for long-context-temporal-207.

Grading scope: the last non-empty line of the model's response must be exactly
`FINAL: from=<int> to=<int> gap_min=<int>` bounding the single longest gap in
time order.

Pure: reads only the response text (or $OUT_DIR/response.txt).
"""
import argparse
import json
import os
import re
import sys

EXPECTED_FROM = 65
EXPECTED_TO = 66
EXPECTED_GAP = 840
FINAL_LINE = re.compile(r"^FINAL:\s*from=(\d+)\s+to=(\d+)\s+gap_min=(\d+)\s*$")


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
                    "'FINAL: from=<integer> to=<integer> gap_min=<integer>'; "
                    "got %r" % final[:120])

    frm, to, gap = int(m.group(1)), int(m.group(2)), int(m.group(3))
    if (frm, to, gap) == (EXPECTED_FROM, EXPECTED_TO, EXPECTED_GAP):
        emit(True, "from=65 to=66 gap_min=840")
    emit(False, "wrong gap: got from=%d to=%d gap_min=%d "
                "(expected from=65 to=66 gap_min=840)" % (frm, to, gap))


if __name__ == "__main__":
    main()
