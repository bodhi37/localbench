#!/usr/bin/env python3
"""Verifier for math-arithmetic-001.

Grading scope: the last non-empty line of the model's response must be exactly
`FINAL: batches=<int> cost_cents=<int>` and both integers must equal the values
computed by the strategy fixed in prompt.md.

Pure: reads only the response text (or $OUT_DIR/response.txt), no network,
no clock, no randomness.
"""
import argparse
import json
import os
import re
import sys

EXPECTED_BATCHES = 19
EXPECTED_COST_CENTS = 9215
FINAL_LINE = re.compile(r"^FINAL:\s*batches=(\d+)\s+cost_cents=(\d+)\s*$")


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
                    "'FINAL: batches=<int> cost_cents=<int>'; got %r" % final[:120])

    batches, cost_cents = int(m.group(1)), int(m.group(2))
    if (batches, cost_cents) == (EXPECTED_BATCHES, EXPECTED_COST_CENTS):
        emit(True, "batches=19 cost_cents=9215")
    emit(False, "wrong values: batches=%d (expected 19), cost_cents=%d (expected 9215)"
                % (batches, cost_cents))


if __name__ == "__main__":
    main()