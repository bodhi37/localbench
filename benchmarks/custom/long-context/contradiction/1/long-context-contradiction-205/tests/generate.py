#!/usr/bin/env python3
"""Deterministic generator for prompt.md of long-context-contradiction-205.

Plain mode has no filesystem, so the corpus lives inline in prompt.md.
Re-running this script reproduces prompt.md byte-for-byte (seed 205001).
Stdlib only.
"""
import json
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROMPT = HERE.parent / "prompt.md"
EXPECTED = HERE / "expected.json"

SEED = 205001
TARGET_AREA = "VAULT-7"
TARGET_LIMITS = (40, 90)
NEAR_AREAS = ["VAULT-1", "VAULT-70", "VAULT7"]
BASE_AREAS = ["ARCHIVE-3", "CACHE-12", "GATE-4", "STORE-8", "DOCK-2",
              "SHELF-11", "BIN-6", "CRATE-9", "LOCKER-5", "DEPOT-14",
              "HOLD-21", "STACK-17", "AISLE-23", "BAY-30", "ROOM-41",
              "CELL-2", "POD-9", "RACK-13", "CASE-7", "DRAWER-4",
              "CABINET-6", "TRUNK-1", "CHEST-8", "BOX-19", "SACK-22",
              "CRIB-5", "STALL-3", "PEN-16", "YARD-10", "FIELD-24",
              "PLOT-31", "MEADOW-2", "GROVE-18", "ORCHARD-6", "PADDOCK-9",
              "CROFT-12", "GARTH-4", "CLOSE-7", "COURT-15", "TERRACE-20",
              "LANE-26", "ALLEY-5", "ROAD-33", "STREET-8", "AVENUE-11",
              "BOULEVARD-2"]
NOTES = ["alpha", "bravo", "cinder", "drift", "ember", "flint", "grove",
         "harbor", "inlet", "juniper", "kelp", "lumen"]

HEADER = """# Policy contradiction hunt

A site keeps a single policy register. Every record line has exactly this form:

```
POL <4-digit id> | AREA <area> | MAX <integer> GB per account | note=<word>
```

Lines that start with `REGISTER` or `FORMAT` are header lines, not records.
Only lines that start with `POL ` (with a trailing space) are records.

Each storage area should have exactly one limit: all records naming the same
area should carry the same `MAX` value. Exactly one unordered pair of records
in the register contradicts this rule: the two records name the same area but
carry different `MAX` values. Every other pair of records that name the same
area agrees. Find that contradicting pair.

Beware near-miss area names (for example `VAULT-1`, `VAULT-70`, and `VAULT7`
are three different areas, and none of them is `VAULT-7`): the area match is
exact and case-sensitive on the whole area field.

## Register

```
"""

FOOTER = """```

## Report

End your response with a final line of exactly this form and nothing after it:

FINAL: area=<AREA> pol_a=<integer> pol_b=<integer>

* `area` is the shared area name exactly as it appears in the register
  (case-sensitive, no extra characters).
* `pol_a` and `pol_b` are the two POL ids as base-10 integers with
  `pol_a` < `pol_b` numerically (leading zeros are not significant).

The final line is the only part graded; anything else in your response is
ignored.
"""


def main():
    rng = random.Random(SEED)
    areas = list(BASE_AREAS) + NEAR_AREAS + [TARGET_AREA]
    assert len(areas) == 50, "need exactly 50 areas x 2 lines = 100 records"
    order = areas[:]
    rng.shuffle(order)
    limits = {}
    for a in areas:
        limits[a] = rng.choice([10, 15, 20, 25, 30, 50, 60, 80, 100, 120, 150, 200])

    recs = []  # (area, limit)
    for a in order:
        if a == TARGET_AREA:
            recs.append((a, TARGET_LIMITS[0]))
            recs.append((a, TARGET_LIMITS[1]))
        else:
            recs.append((a, limits[a]))
            recs.append((a, limits[a]))
    assert len(recs) == 100
    # Exactly one contradicting pair (order-independent property).
    bad = [a for a in areas
           if len({lim for (ar, lim) in recs if ar == a}) > 1]
    assert bad == [TARGET_AREA], bad
    # Shuffle file order so the pair is neither adjacent nor near a boundary.
    rng.shuffle(recs)
    bad = [a for a in areas
           if len({lim for (ar, lim) in recs if ar == a}) > 1]
    assert bad == [TARGET_AREA], bad

    notes = [rng.choice(NOTES) for _ in recs]
    body = [
        "REGISTER STORAGE POLICY - ONE RECORD PER LINE",
        "FORMAT: POL <4-digit id> | AREA <area> | MAX <integer> GB per account | note=<word>",
        "",
    ]
    for i, ((a, lim), n) in enumerate(zip(recs, notes), 1):
        body.append("POL %04d | AREA %s | MAX %d GB per account | note=%s"
                    % (i, a, lim, n))

    PROMPT.write_text(HEADER + "\n".join(body) + "\n" + FOOTER, encoding="utf-8")
    ids = [i for i, (a, _lim) in enumerate(recs, 1) if a == TARGET_AREA]
    assert len(ids) == 2
    ids.sort()
    EXPECTED.write_text(json.dumps(
        {"area": TARGET_AREA, "pol_a": ids[0], "pol_b": ids[1],
         "limits": list(TARGET_LIMITS)}, indent=2) + "\n", encoding="utf-8")
    print("answer: area=%s pol_a=%d pol_b=%d limits=%s"
          % (TARGET_AREA, ids[0], ids[1], list(TARGET_LIMITS)))
    print("prompt bytes:", PROMPT.stat().st_size)


if __name__ == "__main__":
    main()
