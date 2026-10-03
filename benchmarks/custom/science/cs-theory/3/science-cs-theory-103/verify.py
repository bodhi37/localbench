#!/usr/bin/env python3
"""Verifier for science-cs-theory-103.

Grading scope: the last non-empty line of the model's response must be exactly
`FINAL: a=<int> b=<int> c=<int>` with
  a = f(1000)          mod 1000000007,
  b = f(1000000000)    mod 1000000007,
  c = f(1000)          mod 97,
where f counts binary strings avoiding the contiguous substrings 010 and 1110.

Pure: reads only the response text (or $OUT_DIR/response.txt).
"""
import argparse
import json
import os
import re
import sys

EXPECTED = (533167111, 451009448, 15)
FINAL_LINE = re.compile(r"^FINAL:\s*a=(\d+)\s+b=(\d+)\s+c=(\d+)\s*$")
PATTERNS = ("010", "1110")
MOD_A = 1000000007
STATES = ["", "0", "1"] + [x + y for x in "01" for y in "01"] \
         + [x + y + z for x in "01" for y in "01" for z in "01"]


def count_avoiding(n):
    """Independent reference: exact count of admissible strings of length n."""
    cur = {"": 1}
    for _ in range(n):
        nxt = {}
        for s, cnt in cur.items():
            for c in "01":
                t = s + c
                if t.endswith(PATTERNS[0]) or t.endswith(PATTERNS[1]):
                    continue
                key = t[-3:] if len(t) >= 3 else t
                nxt[key] = nxt.get(key, 0) + cnt
        cur = nxt
    return sum(cur.values())


def count_avoiding_mod(n, m):
    """Reference count modulo m via transfer matrix + fast exponentiation."""
    idx = {s: i for i, s in enumerate(STATES)}
    size = len(STATES)
    mat = [[0] * size for _ in range(size)]
    for s in STATES:
        for c in "01":
            t = s + c
            if t.endswith(PATTERNS[0]) or t.endswith(PATTERNS[1]):
                continue
            key = t[-3:] if len(t) >= 3 else t
            mat[idx[key]][idx[s]] += 1

    def mul(a, b):
        out = [[0] * size for _ in range(size)]
        for i in range(size):
            ai, oi = a[i], out[i]
            for k in range(size):
                v = ai[k]
                if v:
                    bk = b[k]
                    for j in range(size):
                        oi[j] = (oi[j] + v * bk[j]) % m
        return out

    def mpow(a, e):
        r = [[int(i == j) for j in range(size)] for i in range(size)]
        while e:
            if e & 1:
                r = mul(r, a)
            a = mul(a, a)
            e >>= 1
        return r

    powered = mpow(mat, n)
    return sum(powered[i][idx[""]] for i in range(size)) % m


def selftest(task_dir):
    vectors_path = os.path.join(task_dir or ".", "tests", "vectors.json")
    with open(vectors_path, encoding="utf-8") as fh:
        raw = json.load(fh)
    vectors = {int(k): int(v) for k, v in raw.items() if k.lstrip("-").isdigit()}
    for n, want in sorted(vectors.items()):
        assert count_avoiding(n) == want, ("vector mismatch", n, want)
    assert count_avoiding_mod(1000, MOD_A) == EXPECTED[0], "f(1000) mismatch"
    assert count_avoiding_mod(10 ** 9, MOD_A) == EXPECTED[1], "f(1e9) mismatch"
    assert EXPECTED[0] % 97 == EXPECTED[2], "a mod 97 != c"
    print(json.dumps({"selftest": "pass", "vectors": len(vectors)}))
    return 0


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
    ap.add_argument("--selftest", action="store_true",
                    help="harness-side: validate the shipped expected constants "
                         "against tests/vectors.json and an independent reference")
    args = ap.parse_args()

    if args.selftest:
        sys.exit(selftest(args.task_dir))

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
                    "'FINAL: a=<int> b=<int> c=<int>'; got %r" % final[:120])

    got = tuple(int(g) for g in m.groups())
    if got == EXPECTED:
        emit(True, "a=533167111 b=451009448 c=15")
    emit(False, "wrong values: a=%d (expected 533167111), b=%d (expected 451009448), "
                "c=%d (expected 15)" % got)


if __name__ == "__main__":
    main()