#!/usr/bin/env python3
"""Verifier for science-biology-104.

Grading scope: the last non-empty line of the model's response must be exactly
`FINAL: n_het=<int> conc=<int>` with the Hardy-Weinberg heterozygote count
(910) and the diluted concentration (80000 cells/mL).

Pure: reads only the response text (or $OUT_DIR/response.txt).
"""
import argparse
import json
import os
import re
import sys

EXPECTED = ("910", "80000")
FINAL_LINE = re.compile(r"^FINAL:\s*n_het=(\d+)\s+conc=(\d+)\s*$")


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
                     "'FINAL: n_het=<integer> conc=<integer>'; got %r" % final[:120])

    raw = (m.group(1), m.group(2))
    if raw == EXPECTED:
        emit(True, "n_het=910 conc=80000")
    emit(False, "wrong values: n_het=%s (expected 910), conc=%s (expected 80000)"
                % (raw[0], raw[1]))


if __name__ == "__main__":
    main()
