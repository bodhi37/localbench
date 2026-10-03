#!/usr/bin/env python3
"""Verifier for cybersecurity-defsec-501.

Grading scope: the last non-empty line of the model's response must be exactly
`FINAL: accepted=<int> accepted_id_sum=<int> f017_rule=<id|DEFAULT> f017_action=<accept|reject>`
with the values produced by the first-match filter semantics in prompt.md.

Pure: reads only the response text (or $OUT_DIR/response.txt).
"""
import argparse
import json
import os
import re
import sys

EXPECTED_ACCEPTED = 12
EXPECTED_ID_SUM = 104
EXPECTED_F017_RULE = "R16"
EXPECTED_F017_ACTION = "reject"
FINAL_LINE = re.compile(
    r"^FINAL:\s*accepted=(\d+)\s+accepted_id_sum=(\d+)\s+f017_rule=([A-Za-z0-9#-]+)\s+f017_action=(accept|reject)\s*$")


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
    m = FINAL_LINE.match(lines[-1])
    if not m:
        emit(False, "last non-empty line is not of the required FINAL: form; got %r"
                    % lines[-1][:150])

    accepted = int(m.group(1))
    id_sum = int(m.group(2))
    rule = m.group(3)
    action = m.group(4)
    if (accepted, id_sum, rule, action) == (
            EXPECTED_ACCEPTED, EXPECTED_ID_SUM, EXPECTED_F017_RULE, EXPECTED_F017_ACTION):
        emit(True, "accepted=12 accepted_id_sum=104 f017=R16 reject")
    emit(False, "wrong: accepted=%d (expected 12), accepted_id_sum=%d (expected 104), "
                "f017_rule=%s (expected R16), f017_action=%s (expected reject)"
                % (accepted, id_sum, rule, action))


if __name__ == "__main__":
    main()