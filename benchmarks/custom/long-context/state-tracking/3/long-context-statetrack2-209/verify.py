#!/usr/bin/env python3
"""Verifier for long-context-statetrack2-209.

Grading scope: the last non-empty line of the model's response must be exactly
`FINAL: balance_cents=<int> effective=<int>` giving the final ledger balance
and the count of non-voided postings.

Pure: reads only the response text (or $OUT_DIR/response.txt).
"""
import argparse
import json
import os
import re
import sys

EXPECTED_BALANCE = 41564
EXPECTED_EFFECTIVE = 90
FINAL_LINE = re.compile(r"^FINAL:\s*balance_cents=(\d+)\s+effective=(\d+)\s*$")


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
                    "'FINAL: balance_cents=<integer> effective=<integer>'; "
                    "got %r" % final[:120])

    balance, effective = int(m.group(1)), int(m.group(2))
    if (balance, effective) == (EXPECTED_BALANCE, EXPECTED_EFFECTIVE):
        emit(True, "balance_cents=41564 effective=90")
    emit(False, "wrong ledger: got balance_cents=%d effective=%d "
                "(expected balance_cents=41564 effective=90)"
         % (balance, effective))


if __name__ == "__main__":
    main()
