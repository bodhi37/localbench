#!/usr/bin/env python3
"""Verifier for instruction-following-procedure-307.

Grading scope: the last non-blank line only. It must match
FINAL: A=<int> B=<int> STEPS=8 CHECK=<hex>, where A/B/CHECK are re-derived by
simulating the 8-step procedure from the prompt. Pure.
"""
import argparse
import json
import os
import re
import sys

PAT = re.compile(r"^FINAL: A=(\S+) B=(\S+) STEPS=(\S+) CHECK=(\S+)$")


def emit(passed, detail):
    print(json.dumps({"pass": bool(passed), "detail": detail}))
    sys.exit(0 if passed else 1)


def load_response(args):
    for path in (args.response, os.path.join(args.out_dir or "", "response.txt")):
        if path and os.path.isfile(path):
            with open(path, encoding="utf-8", errors="replace") as fh:
                return fh.read()
    return None


def simulate():
    a, b = 4, 7
    a = a + 10          # step 1 -> 14
    b = b * 2           # step 2 -> 14
    if a >= b:          # step 3 -> 14>=14 true
        a = a + 5       # -> 19
    else:
        b = b + 5
    b = b + a           # step 4 -> 33
    if b > 30:          # step 5 -> true
        a = a * 2       # -> 38
    else:
        a = a + 1
    b = b - 6           # step 6 -> 27
    if a % 2 == 0:      # step 7 -> 38 even
        b = b + 2       # -> 29
    else:
        b = b + 3
    b = b + 1           # step 8 -> 30
    check = "%02X" % (sum(int(d) for d in str(a + b)) % 256)
    return a, b, 8, check


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
    m = PAT.match(lines[-1])
    if not m:
        emit(False, "last line must match 'FINAL: A=<int> B=<int> STEPS=8 CHECK=<hex>', got %r" % lines[-1])
    ea, eb, es, ec = simulate()
    try:
        ga = int(m.group(1))
    except ValueError:
        emit(False, "A must be a base-10 integer, got %r" % m.group(1))
    try:
        gb = int(m.group(2))
    except ValueError:
        emit(False, "B must be a base-10 integer, got %r" % m.group(2))
    if m.group(3) != str(es):
        emit(False, "STEPS must be %s, got %r" % (es, m.group(3)))
    if m.group(4) != ec:
        emit(False, "CHECK must be %s, got %r" % (ec, m.group(4)))
    if ga != ea or gb != eb:
        emit(False, "registers wrong: got A=%d B=%d, procedure gives A=%d B=%d" % (ga, gb, ea, eb))
    emit(True, "registers match re-executed procedure A=%d B=%d STEPS=%d CHECK=%s" % (ea, eb, es, ec))


if __name__ == "__main__":
    main()
