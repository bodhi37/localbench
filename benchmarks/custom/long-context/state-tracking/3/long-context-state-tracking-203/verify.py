#!/usr/bin/env python3
"""Verifier for long-context-state-tracking-203.

Grading scope: $OUT_DIR/answer.json must be a JSON object with exactly the three
declared keys holding the state reached by applying the log's events in file
order under the prompt's VOID semantics.

Pure: reads only $OUT_DIR/answer.json.
"""
import argparse
import json
import os
import sys

EXPECTED = {
    "final_bins": {"A-01": 89, "A-02": 20, "B-07": -175},
    "effective_voids": 4,
    "net_change": -261,
}


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

    fb = obj["final_bins"]
    if not isinstance(fb, dict) or sorted(fb) != sorted(EXPECTED["final_bins"]):
        emit(False, "final_bins must be an object with exactly the keys A-01, A-02, B-07; got %r" % (fb,))
    bad = [k for k, v in list(fb.items()) + [("effective_voids", obj["effective_voids"]),
                                             ("net_change", obj["net_change"])]
           if isinstance(v, bool) or not isinstance(v, int)]
    if bad:
        emit(False, "these values must be JSON integers: %s" % sorted(bad))

    if obj == EXPECTED:
        emit(True, "final_bins A-01=89 A-02=20 B-07=-175, effective_voids=4, net_change=-261")
    wrong = {k: obj[k] for k in EXPECTED if obj[k] != EXPECTED[k]}
    emit(False, "wrong values: %s (expected %s)"
                % (json.dumps(wrong, sort_keys=True),
                   json.dumps({k: EXPECTED[k] for k in wrong}, sort_keys=True)))


if __name__ == "__main__":
    main()