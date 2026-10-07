#!/usr/bin/env python3
"""Verifier for long-context-versiondiff-208.

Grading scope: the last non-empty line of the model's response must be exactly
`FINAL: changed=<C..>,...` listing the clauses changed between v2 and v3.

Pure: reads only the response text (or $OUT_DIR/response.txt).
"""
import argparse
import json
import os
import re
import sys

EXPECTED = "C07,C19,C31"
FINAL_LINE = re.compile(r"^FINAL:\s*changed=([A-Z0-9]+(?:,[A-Z0-9]+)*)\s*$")


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
                    "'FINAL: changed=<C..>,...'; got %r" % final[:120])

    got = m.group(1)
    if got == EXPECTED:
        emit(True, "changed=C07,C19,C31")
    emit(False, "wrong diff: got changed=%s (expected changed=C07,C19,C31)"
         % got[:120])


if __name__ == "__main__":
    main()
