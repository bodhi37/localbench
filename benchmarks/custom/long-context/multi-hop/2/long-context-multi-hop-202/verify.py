#!/usr/bin/env python3
"""Verifier for long-context-multi-hop-202.

Grading scope: $OUT_DIR/answer.json must be a JSON object with exactly the five
declared keys and the values obtained by the three-file hop chain
(order -> catalog part -> supplier lead time) described in prompt.md.

Pure: reads only $OUT_DIR/answer.json.
"""
import argparse
import json
import os
import sys

EXPECTED = {
    "order_id": "O-4471",
    "total_mass_g": 100798,
    "total_cost_cents": 1047380,
    "max_lead_time_days": 14,
    "heaviest_line_part": "PC-1022",
}
INT_KEYS = ("total_mass_g", "total_cost_cents", "max_lead_time_days")


def emit(passed, detail):
    print(json.dumps({"pass": bool(passed), "detail": detail}))
    sys.exit(0 if passed else 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task-dir")
    ap.add_argument("--out-dir")
    ap.add_argument("--response")
    args = ap.parse_args()

    path = os.path.join(args.out_dir or "", "answer.json")
    if not os.path.isfile(path):
        emit(False, "required deliverable $OUT_DIR/answer.json is missing")
    with open(path, encoding="utf-8", errors="replace") as fh:
        raw = fh.read()
    try:
        obj = json.loads(raw)
    except Exception as exc:
        emit(False, "answer.json is not valid JSON: %s" % exc)
    if not isinstance(obj, dict):
        emit(False, "answer.json must contain a single JSON object, got %s" % type(obj).__name__)

    missing = [k for k in EXPECTED if k not in obj]
    extra = [k for k in obj if k not in EXPECTED]
    if missing or extra:
        emit(False, "wrong key set: missing=%s extra=%s" % (sorted(missing), sorted(extra)))

    bad_types = [k for k in INT_KEYS if isinstance(obj[k], bool) or not isinstance(obj[k], int)]
    if bad_types:
        emit(False, "these keys must be JSON integers: %s" % sorted(bad_types))

    wrong = {k: obj[k] for k in EXPECTED if obj[k] != EXPECTED[k]}
    if not wrong:
        emit(True, "answer.json matches: mass=100798 cost=1047380 lead=14 heaviest=PC-1022")
    emit(False, "wrong values: %s (expected %s)"
                % (json.dumps(wrong), json.dumps({k: EXPECTED[k] for k in wrong})))


if __name__ == "__main__":
    main()