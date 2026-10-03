#!/usr/bin/env python3
"""Deterministic generator for prompt.md of long-context-retrieval-201.

This task runs in `plain` mode (no tools, no filesystem), so the corpus must be
inline in the prompt. The committed prompt.md is the source of truth; re-running
this script reproduces it byte-for-byte (fixed seed).
"""
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROMPT = HERE.parent / "prompt.md"

STATIONS = ["ORION-7", "KESTREL-2", "HOLLOWAY-9", "MARROW-4", "SABLE-11",
            "THORNE-3", "PELICAN-6", "REDFERN-8", "WILLOW-5", "GARNET-12"]
OPS = ["Halvorsen", "Okafor", "Lindqvist", "Marchetti", "Dlamini", "Novak",
       "Petrov", "Iyer", "Bencik", "Farrow", "Almeida", "Kowalski"]
NEEDLE = "0.0093"
DISTRACTORS = ["0.0930", "0.0094", "0.0039", "0.0103", "0.0092"]
N = 240

HEADER = """# Atlas drift logbook

A station network keeps a single drift logbook. In the logbook below, every
record line has exactly this form:

```
ENTRY <4-digit id> | STATION <name> | drift=<4-decimal value> | bearing=<1-decimal value> | op=<surname>
```

Lines that start with `ATLAS` or `FORMAT` are header lines, not records.

Exactly one record line in the logbook carries the drift value `0.0093`. Find
that record.

## Logbook

```
"""

FOOTER = """```

## Report

End your response with a final line of exactly this form and nothing after it:

FINAL: entry=<integer> bearing=<number> op=<surname>

* `entry` is that record's ENTRY id written as a base-10 integer (leading zeros
  are not significant).
* `bearing` is that record's bearing value exactly as it appears in the logbook.
* `op` is that record's `op` surname exactly as it appears in the logbook.

The final line is the only part graded; anything else in your response is
ignored.
"""


def main():
    rng = random.Random(20240919)
    used = set(DISTRACTORS)
    recs = []
    for i in range(1, N + 1):
        while True:
            d = "%0.4f" % (rng.randrange(0, 600) / 10000.0)
            if d not in used and NEEDLE not in d and d not in NEEDLE:
                break
        used.add(d)
        recs.append([i, rng.choice(STATIONS), d,
                     "%0.1f" % (rng.randrange(0, 3600) / 10.0), rng.choice(OPS)])
    # Plant the needle and the near-miss drifts as real records so fuzzy/prefix
    # matching is actively punished, and so no near-miss value is ever absent
    # from the file.
    spots = rng.sample(range(N), len(DISTRACTORS) + 1)
    for pos, d in zip(spots, DISTRACTORS):
        recs[pos][2] = d
    needle_pos = spots[-1]
    recs[needle_pos][2] = NEEDLE
    assert all(sum(1 for r in recs if r[2] == v) == 1 for v in [NEEDLE] + DISTRACTORS)
    assert NEEDLE not in {r[2] for r in recs if r[2] != NEEDLE}

    body = ["ATLAS DRIFT LOGBOOK - STATION NETWORK - ONE RECORD PER LINE",
            "FORMAT: ENTRY <4-digit id> | STATION <name> | drift=<4-decimal> | bearing=<1-decimal> | op=<surname>",
            ""]
    for i, st, d, b, op in recs:
        body.append("ENTRY %04d | STATION %-10s | drift=%s | bearing=%s | op=%s" % (i, st, d, b, op))

    PROMPT.write_text(HEADER + "\n".join(body) + "\n" + FOOTER, encoding="utf-8")
    hit = [r for r in recs if r[2] == NEEDLE][0]
    print("needle: entry=%d bearing=%s op=%s station=%s" % (hit[0], hit[3], hit[4], hit[1]))
    print("prompt bytes:", PROMPT.stat().st_size)


if __name__ == "__main__":
    main()
