#!/usr/bin/env python3
"""Verifier for instruction-following-multiconstraint-306.

Grading scope: the last non-blank line of the response only. It must match
FINAL: J1=<slot> ... J5=<slot> makespan=<int>, satisfy all constraints
(bijection, forbidden cells, J3-even, J1/J4 late-exclusion), carry the correct
summed makespan, and be the unique minimum (recomputed by brute force over all
120 bijections). Pure: reads only the response text.
"""
import argparse
import itertools
import json
import os
import re
import sys

COSTS = {
    "J1": {"S1": 9, "S2": None, "S3": 12, "S4": 7, "S5": 14},
    "J2": {"S1": 8, "S2": 11, "S3": None, "S4": 10, "S5": 13},
    "J3": {"S1": 12, "S2": 9, "S3": 8, "S4": 13, "S5": 11},
    "J4": {"S1": None, "S2": 13, "S3": 10, "S4": 12, "S5": 9},
    "J5": {"S1": 11, "S2": 10, "S3": 14, "S4": 9, "S5": None},
}
JOBS = ["J1", "J2", "J3", "J4", "J5"]
SLOTS = ["S1", "S2", "S3", "S4", "S5"]
PAT = re.compile(r"^FINAL: J1=(\S+) J2=(\S+) J3=(\S+) J4=(\S+) J5=(\S+) makespan=(\S+)$")


def emit(passed, detail):
    print(json.dumps({"pass": bool(passed), "detail": detail}))
    sys.exit(0 if passed else 1)


def load_response(args):
    for path in (args.response, os.path.join(args.out_dir or "", "response.txt")):
        if path and os.path.isfile(path):
            with open(path, encoding="utf-8", errors="replace") as fh:
                return fh.read()
    return None


def feasible(assign):
    """Return (ok, reason, total). assign: dict job->slot."""
    if sorted(assign.values()) != SLOTS:
        return False, "slots must be a bijection over S1..S5", None
    total = 0
    for j in JOBS:
        c = COSTS[j].get(assign[j])
        if c is None:
            return False, "forbidden cell %s=%s" % (j, assign[j]), None
        total += c
    if assign["J3"] not in ("S2", "S4"):
        return False, "J3 must be even (S2/S4), got %s" % assign["J3"], None
    if assign["J1"] in ("S4", "S5") and assign["J4"] in ("S4", "S5"):
        return False, "J1 and J4 may not both be late (S4/S5)", None
    return True, "feasible", total


def optimum():
    best = None
    best_list = []
    feas = []
    for perm in itertools.permutations(SLOTS):
        a = dict(zip(JOBS, perm))
        ok, _, tot = feasible(a)
        if not ok:
            continue
        feas.append((tot, a))
    feas.sort(key=lambda x: x[0])
    return feas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task-dir")
    ap.add_argument("--out-dir")
    ap.add_argument("--response")
    args = ap.parse_args()

    text = load_response(args)
    if text is None:
        emit(False, "no response text supplied (pass --response FILE)")

    lines = [ln.strip() for ln in text.replace("\r\n", "\n").split("\n")]
    while lines and lines[-1] == "":
        lines.pop()
    if not lines or lines[-1] == "":
        emit(False, "empty response: no FINAL line")
    final = lines[-1]
    m = PAT.match(final)
    if not m:
        emit(False, "last line must match 'FINAL: J1=<slot> J2=<slot> J3=<slot> J4=<slot> J5=<slot> makespan=<int>', got %r" % final)
    assign = dict(zip(JOBS, m.groups()[:5]))
    try:
        claimed = int(m.group(6))
    except ValueError:
        emit(False, "makespan must be a base-10 integer, got %r" % m.group(6))
    for j, s in assign.items():
        if s not in SLOTS:
            emit(False, "unknown slot %r for %s" % (s, j))
    ok, reason, total = feasible(assign)
    if not ok:
        emit(False, "infeasible: " + reason)
    if claimed != total:
        emit(False, "makespan %d disagrees with listed assignment (true sum %d)" % (claimed, total))
    feas = optimum()
    if not feas:
        emit(False, "internal error: no feasible schedule")
    best_total = feas[0][0]
    if total != best_total:
        emit(False, "makespan %d is feasible but not minimal (minimum is %d)" % (total, best_total))
    winners = [a for t, a in feas if t == best_total]
    if len(winners) != 1:
        emit(False, "internal error: minimum not unique")
    if assign != winners[0]:
        emit(False, "makespan is minimal but assignment is not the unique optimum")
    emit(True, "unique minimum makespan %d with feasible assignment" % total)


if __name__ == "__main__":
    main()
