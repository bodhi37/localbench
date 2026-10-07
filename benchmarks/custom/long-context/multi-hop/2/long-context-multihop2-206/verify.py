#!/usr/bin/env python3
"""Verifier for long-context-multihop2-206.

Grading scope: the last non-empty line of the model's response must be exactly
`FINAL: team=<TEAM> vessel=<VESSEL> port=<PORT>` tracing Rosa Aldana's
member -> team -> vessel -> port chain.

Pure: reads only the response text (or $OUT_DIR/response.txt).
"""
import argparse
import json
import os
import re
import sys

EXPECTED_TEAM = "K-7"
EXPECTED_VESSEL = "SS-MERIDIAN"
EXPECTED_PORT = "LUMEN"
FINAL_LINE = re.compile(r"^FINAL:\s*team=(\S+)\s+vessel=(\S+)\s+port=(\S+)\s*$")


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
                    "'FINAL: team=<TEAM> vessel=<VESSEL> port=<PORT>'; got %r"
             % final[:120])

    team, vessel, port = m.group(1), m.group(2), m.group(3)
    if (team, vessel, port) == (EXPECTED_TEAM, EXPECTED_VESSEL, EXPECTED_PORT):
        emit(True, "team=K-7 vessel=SS-MERIDIAN port=LUMEN")
    emit(False, "wrong chain: got team=%s vessel=%s port=%s "
                "(expected team=K-7 vessel=SS-MERIDIAN port=LUMEN)"
         % (team, vessel, port))


if __name__ == "__main__":
    main()
