#!/usr/bin/env python3
"""Verifier for instruction-following-constraint-satisfaction-302.

Grading scope: the last non-empty line of the model's response must be exactly
`FINAL: S1=.. S2=.. S3=.. S4=.. S5=.. S6=.. total=..` reporting the unique
minimum-cost feasible crew-to-shift assignment.

Pure: reads only the response text (or $OUT_DIR/response.txt). The verifier also
re-checks feasibility so that a wrong verdict always carries a precise reason.
"""
import argparse
import json
import os
import re
import sys

COST = {
    "S1": {"ADA": 14, "BO": 12, "CAI": 19, "DEE": 11, "EMU": 16, "FAY": 13},
    "S2": {"ADA": 11, "BO": 17, "CAI": 14, "DEE": None, "EMU": 13, "FAY": 15},
    "S3": {"ADA": None, "BO": 13, "CAI": 12, "DEE": 17, "EMU": 18, "FAY": 11},
    "S4": {"ADA": 9, "BO": 16, "CAI": 15, "DEE": 12, "EMU": None, "FAY": 18},
    "S5": {"ADA": 18, "BO": None, "CAI": 13, "DEE": 16, "EMU": 11, "FAY": 17},
    "S6": {"ADA": 12, "BO": 10, "CAI": None, "DEE": 15, "EMU": 14, "FAY": None},
}
SHIFTS = ["S1", "S2", "S3", "S4", "S5", "S6"]
WORKERS = ["ADA", "BO", "CAI", "DEE", "EMU", "FAY"]
EXPECTED_ASSIGN = {"S1": "FAY", "S2": "ADA", "S3": "CAI", "S4": "DEE", "S5": "EMU", "S6": "BO"}
EXPECTED_TOTAL = 69
FINAL_LINE = re.compile(
    r"^FINAL:\s*S1=([A-Z]+)\s+S2=([A-Z]+)\s+S3=([A-Z]+)\s+S4=([A-Z]+)\s+S5=([A-Z]+)\s+S6=([A-Z]+)\s+total=(-?\d+)\s*$")


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
        emit(False, "last non-empty line is not of the required FINAL: form; got %r" % lines[-1][:140])

    assign = dict(zip(SHIFTS, m.groups()[:6]))
    total = int(m.group(7))

    unknown = sorted({w for w in assign.values() if w not in WORKERS})
    if unknown:
        emit(False, "unknown worker name(s): %s" % unknown)
    if sorted(assign.values()) != sorted(WORKERS):
        emit(False, "each of the six workers must take exactly one shift; got %s"
                    % json.dumps(assign, sort_keys=True))
    forbidden = [s for s in SHIFTS if COST[s][assign[s]] is None]
    if forbidden:
        emit(False, "forbidden pairings used on shift(s): %s" % forbidden)
    if assign["S4"] != "DEE" and assign["S2"] != "DEE" and assign["S6"] != "DEE":
        emit(False, "DEE must work an even-numbered shift; DEE is on an odd shift")
    real_total = sum(COST[s][assign[s]] for s in SHIFTS)
    if total != real_total:
        emit(False, "reported total=%d but the listed assignment costs %d" % (total, real_total))

    if assign == EXPECTED_ASSIGN and total == EXPECTED_TOTAL:
        emit(True, "unique optimum: cost 69, S1=FAY S2=ADA S3=CAI S4=DEE S5=EMU S6=BO")
    emit(False, "feasible but not optimal: total=%d (the unique minimum is 69); "
                "assignment=%s" % (total, json.dumps(assign, sort_keys=True)))


if __name__ == "__main__":
    main()