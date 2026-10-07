#!/usr/bin/env python3
"""Verifier for long-context-contradiction-205.

Grading scope: the last non-empty line of the model's response must be exactly
`FINAL: area=<AREA> pol_a=<int> pol_b=<int>` naming the single contradicting
area and its two record ids in ascending numeric order.

Pure: reads only the response text (or $OUT_DIR/response.txt).
"""
import argparse
import json
import os
import re
import sys

EXPECTED_AREA = "VAULT-7"
EXPECTED_A = 62
EXPECTED_B = 92
FINAL_LINE = re.compile(r"^FINAL:\s*area=([A-Za-z0-9][A-Za-z0-9\-]*)\s+pol_a=(\d+)\s+pol_b=(\d+)\s*$")


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
                    "'FINAL: area=<AREA> pol_a=<integer> pol_b=<integer>'; got %r"
             % final[:120])

    area, a, b = m.group(1), int(m.group(2)), int(m.group(3))
    if a >= b:
        emit(False, "ids must be in ascending numeric order (pol_a < pol_b); "
                    "got pol_a=%d pol_b=%d" % (a, b))
    if (area, a, b) == (EXPECTED_AREA, EXPECTED_A, EXPECTED_B):
        emit(True, "area=VAULT-7 pol_a=62 pol_b=92")
    emit(False, "wrong pair: got area=%s pol_a=%d pol_b=%d "
                "(expected area=VAULT-7 pol_a=62 pol_b=92)" % (area, a, b))


if __name__ == "__main__":
    main()
