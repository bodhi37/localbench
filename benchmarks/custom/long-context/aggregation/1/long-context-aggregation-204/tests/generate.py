#!/usr/bin/env python3
"""Deterministic generator for prompt.md of long-context-aggregation-204.

Plain mode has no filesystem, so the corpus lives inline in prompt.md.
Re-running this script reproduces prompt.md byte-for-byte (seed 204001).
Stdlib only.
"""
import json
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROMPT = HERE.parent / "prompt.md"
EXPECTED = HERE / "expected.json"

SEED = 204001
N = 120
TARGET = "SUPPLIES"
NEAR = ["SUPPLIES-OFFICE", "SUPPLIES-LAB", "SUPPLY", "SUPPLIES2"]
OTHER = ["TRAVEL", "MEALS", "LODGING", "EQUIPMENT", "SOFTWARE", "POSTAGE"]
VENDORS = ["Acme", "Biren", "Coda", "Doran", "Ester", "Farlow",
           "Greer", "Holst", "Ivers", "Jalen", "Korin", "Latsis"]

HEADER = """# Supply ledger aggregation

A site keeps a single expense ledger. Every record line has exactly this form:

```
EXP <4-digit id> | CAT <category> | amt=<dollars>.<2 digits> | vendor=<name>
```

Lines that start with `LEDGER` or `FORMAT` are header lines, not records.
Only lines that start with `EXP ` (with a trailing space) are records.

Your task: add up the amounts of the records whose category field is exactly
`SUPPLIES`. The match is exact and case-sensitive on the whole category field:
near-miss names such as `SUPPLIES-OFFICE`, `SUPPLIES-LAB`, `SUPPLY`, and
`SUPPLIES2` must NOT be counted. Amounts are exact dollars and cents.

## Ledger

```
"""

FOOTER = """```

## Report

End your response with a final line of exactly this form and nothing after it:

FINAL: total_cents=<integer> count=<integer>

* `total_cents` is the exact sum of the counted records in cents
  (dollars times 100 plus cents). Leading zeros are not significant.
* `count` is how many records were summed, as a base-10 integer (leading zeros
  are not significant).
* Only the exact category `SUPPLIES` counts; the near-miss categories listed
  above never count.

The final line is the only part graded; anything else in your response is
ignored.
"""


def main():
    rng = random.Random(SEED)
    cats = []
    for _ in range(N):
        r = rng.random()
        if r < 0.24:
            cats.append(TARGET)
        elif r < 0.40:
            cats.append(rng.choice(NEAR))
        else:
            cats.append(rng.choice(OTHER))
    # Guarantee a healthy target set and every near-miss present as a trap.
    while cats.count(TARGET) < 24:
        cats[rng.randrange(N)] = TARGET
    for i, name in enumerate(NEAR):
        if name not in cats:
            cats[(7 + 29 * i) % N] = name
    amounts = [rng.randrange(500, 25000) for _ in range(N)]
    vendors = [rng.choice(VENDORS) for _ in range(N)]

    total = sum(a for c, a in zip(cats, amounts) if c == TARGET)
    count = sum(1 for c in cats if c == TARGET)
    assert count >= 10, "need a sizable target set"
    assert all(nm in cats for nm in NEAR), "each near-miss must appear"
    assert total != sum(amounts), "all-lines sum must differ from the answer"

    body = [
        "LEDGER SUPPLY EXPENSES - ONE RECORD PER LINE",
        "FORMAT: EXP <4-digit id> | CAT <category> | amt=<dollars>.<2 digits> | vendor=<name>",
        "",
    ]
    for i, (c, a, v) in enumerate(zip(cats, amounts, vendors), 1):
        body.append("EXP %04d | CAT %s | amt=%d.%02d | vendor=%s"
                    % (i, c, a // 100, a % 100, v))

    PROMPT.write_text(HEADER + "\n".join(body) + "\n" + FOOTER, encoding="utf-8")
    EXPECTED.write_text(json.dumps(
        {"total_cents": total, "count": count}, indent=2) + "\n", encoding="utf-8")
    print("answer: total_cents=%d count=%d" % (total, count))
    print("prompt bytes:", PROMPT.stat().st_size)


if __name__ == "__main__":
    main()
