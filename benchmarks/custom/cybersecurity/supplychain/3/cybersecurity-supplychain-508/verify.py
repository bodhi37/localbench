#!/usr/bin/env python3
"""Verifier for cybersecurity-supplychain-508. Rechecks the upgrade set against pins and advisories."
Pure: reads only the response text (or $OUT_DIR/response.txt); the upgrade set is additionally rechecked pin-by-pin.
Answers live in harness-side tests/expected.json, never in prompt.md.
"""
import argparse
import json
import os
import re
import sys

FINAL_LINE = re.compile(r"^FINAL:\s*upgrades=(\S+)\s+residual_critical=(\d+)\s+residual_high=(\d+)\s*$")


def emit(passed, detail):
    print(json.dumps({"pass": bool(passed), "detail": detail}))
    sys.exit(0 if passed else 1)


def load_response(args):
    for path in (args.response, os.path.join(args.out_dir or "", "response.txt")):
        if path and os.path.isfile(path):
            with open(path, encoding="utf-8", errors="replace") as fh:
                return fh.read()
    return None


def load_expected(task_dir):
    base = task_dir or os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base, "tests", "expected.json")
    if not os.path.isfile(path):
        emit(False, "harness misconfigured: tests/expected.json not found")
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task-dir")
    ap.add_argument("--out-dir")
    ap.add_argument("--response")
    args = ap.parse_args()
    expected = load_expected(args.task_dir)
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
    import re as _re
    lock = json.load(open(os.path.join(args.task_dir or ".", "resources", "lock.json")))
    advs = json.load(open(os.path.join(args.task_dir or ".", "resources", "advisories.json")))
    pins = json.load(open(os.path.join(args.task_dir or ".", "resources", "pins.json")))
    locked = {p["name"]: p["version"] for p in lock["packages"]}
    def _vt(v):
        return tuple(int(x) for x in v.split("."))
    raw = m.group(1)
    items = [] if raw == "none" else raw.split(",")
    seen = {}
    for it in items:
        if not _re.match(r"^[A-Za-z0-9_.-]+==\d+\.\d+\.\d+$", it):
            emit(False, "bad upgrade entry %r" % it[:60])
        n, v = it.split("==")
        if n not in locked:
            emit(False, "unknown package %s" % n)
        if n in seen:
            emit(False, "duplicate upgrade for %s" % n)
        seen[n] = v
        if n in pins.get("exact", []):
            emit(False, "pinned package %s must not be upgraded" % n)
        if pins.get("same_major") and _vt(v)[0] != _vt(locked[n])[0]:
            emit(False, "major-version change forbidden for %s" % n)
        if _vt(v) < _vt(locked[n]):
            emit(False, "downgrade forbidden for %s" % n)
    def _final(n):
        return seen.get(n, locked[n])
    crit = high = 0
    for a in advs:
        if _vt(_final(a["pkg"])) < _vt(a["fixed_in"]):
            if a["severity"] == "critical":
                crit += 1
            elif a["severity"] == "high":
                high += 1
    if crit != int(m.group(2)) or high != int(m.group(3)):
        emit(False, "recomputed residuals critical=%d high=%d disagree with response" % (crit, high))
    raw = m.group(1)
    got_set = [] if raw == "none" else sorted(raw.split(","))
    for item in got_set:
        if "==" not in item:
            emit(False, "bad upgrade entry %r (want name==version)" % item[:60])
    got = {"upgrades_str": ",".join(got_set), "residual_critical": int(m.group(2)),
           "residual_high": int(m.group(3))}
    if got["upgrades_str"] != expected["upgrades_str"]:
        emit(False, "upgrade set mismatch: got %s" % got["upgrades_str"][:200])
    if (got["residual_critical"], got["residual_high"]) != (
            expected["residual_critical"], expected["residual_high"]):
        emit(False, "residual mismatch: got critical=%d high=%d" % (
            got["residual_critical"], got["residual_high"]))
    emit(True, "supply-chain upgrade set correct: %s" % got["upgrades_str"])


if __name__ == "__main__":
    main()
