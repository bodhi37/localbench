#!/usr/bin/env python3
"""Verifier for instruction-following-composition-309.

Grading scope: the whole response (single line). Checks: exactly one
non-blank line, no space/tab characters, strict JSON parse, exact key sets,
alphabetical key order in the raw text (top level and nested stats), and
re-derived values (total/mean/max/order/check/tier/alert/site/stats).
Pure.
"""
import argparse
import json
import os
import re
import sys

EXPECTED_OBJ = {
    "alert": True,
    "check": "09",
    "max_label": "B",
    "mean": 45,
    "order": ["C", "A", "B"],
    "site": "COBALT",
    "stats": {"max": "B", "mean": 45, "total": 135},
    "tier": "HIGH",
    "total": 135,
}
TOP_ORDER = ["alert", "check", "max_label", "mean", "order", "site", "stats", "tier", "total"]
STATS_ORDER = ["max", "mean", "total"]


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

    norm = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = norm.split("\n")
    while lines and lines[0].strip() == "":
        lines.pop(0)
    while lines and lines[-1].strip() == "":
        lines.pop()
    # tolerate a single trailing newline only: after trimming outer blanks,
    # exactly one line must remain
    if len(lines) != 1:
        emit(False, "expected exactly one line, got %d" % len(lines))
    raw = lines[0]
    if raw != raw.strip():
        emit(False, "leading/trailing whitespace on the line")
    if " " in raw or "\t" in raw:
        emit(False, "line must contain no spaces or tabs (separators ':' and ',' with nothing around them)")
    try:
        obj = json.loads(raw)
    except Exception as exc:
        emit(False, "strict JSON parse failed: %s" % exc)
    if not isinstance(obj, dict):
        emit(False, "top level must be a JSON object")
    if list(obj.keys()) != TOP_ORDER:
        emit(False, "top-level keys must appear in alphabetical order %r, got %r" % (TOP_ORDER, list(obj.keys())))
    if not isinstance(obj.get("stats"), dict):
        emit(False, "stats must be an object")
    if list(obj["stats"].keys()) != STATS_ORDER:
        emit(False, "stats keys must appear in alphabetical order %r, got %r" % (STATS_ORDER, list(obj["stats"].keys())))
    if obj != EXPECTED_OBJ:
        # precise diff
        diffs = []
        for k in TOP_ORDER:
            if obj.get(k) != EXPECTED_OBJ[k]:
                diffs.append("%s: got %r want %r" % (k, obj.get(k), EXPECTED_OBJ[k]))
        emit(False, "value mismatch: " + "; ".join(diffs))
    emit(True, "single-line JSON matches values, key order, and whitespace spec")


if __name__ == "__main__":
    main()
