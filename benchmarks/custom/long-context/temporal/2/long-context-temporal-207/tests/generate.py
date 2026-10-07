#!/usr/bin/env python3
"""Deterministic generator for prompt.md of long-context-temporal-207.

Plain mode has no filesystem, so the corpus lives inline in prompt.md.
Re-running this script reproduces prompt.md byte-for-byte (seed 207001).
Stdlib only.
"""
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROMPT = HERE.parent / "prompt.md"
EXPECTED = HERE / "expected.json"

SEED = 207001
N = 150
BIG_GAP = 840  # minutes; normal gaps are 15..180 so the maximum is unique
WORDS = ["intake", "valve", "rotor", "beacon", "flange", "gasket", "pump",
         "sensor", "relay", "hinge", "latch", "cable", "filter", "nozzle",
         "panel", "switch", "turbine", "vent", "winch", "yarn"]

HEADER = """# Timeline gap analysis

A monitor keeps a single event timeline. Every record line has exactly this
form:

```
EVT <4-digit id> | ts=<YYYY-MM-DDTHH:MM> | msg=<two words>
```

Lines that start with `TIMELINE` or `FORMAT` are header lines, not records.
Only lines that start with `EVT ` (with a trailing space) are records.

The record lines below are NOT in time order. Order the events by their
timestamps (all timestamps are distinct), then consider the gaps between
consecutive events in that time order. Exactly one such gap is strictly the
longest. Find the two events that bound it: the earlier event (`from`) and the
later event (`to`), and the gap length in whole minutes.

Timestamps compare chronologically, not as file positions: the neighbour of an
event in the file is usually not its neighbour in time.

## Timeline

```
"""

FOOTER = """```

## Report

End your response with a final line of exactly this form and nothing after it:

FINAL: from=<integer> to=<integer> gap_min=<integer>

* `from` is the EVT id of the earlier bounding event, as a base-10 integer
  (leading zeros are not significant).
* `to` is the EVT id of the later bounding event, as a base-10 integer.
* `gap_min` is the later timestamp minus the earlier timestamp, in whole
  minutes, as a base-10 integer.

The final line is the only part graded; anything else in your response is
ignored.
"""


def main():
    rng = random.Random(SEED)
    gaps = [rng.randint(15, 180) for _ in range(N - 1)]
    slot = rng.randrange(N - 1)
    gaps[slot] = BIG_GAP
    assert sorted(gaps)[-2] < BIG_GAP, "longest gap must be unique"

    stamps = [datetime(2026, 1, 1, 0, 0)]
    for g in gaps:
        stamps.append(stamps[-1] + timedelta(minutes=g))
    msgs = ["%s %s" % (rng.choice(WORDS), rng.choice(WORDS)) for _ in range(N)]
    recs = list(zip(range(1, N + 1), stamps, msgs))
    file_order = recs[:]
    rng.shuffle(file_order)

    by_time = sorted(recs, key=lambda r: r[1])
    best = None
    for a, b in zip(by_time, by_time[1:]):
        g = int((b[1] - a[1]).total_seconds() // 60)
        if best is None or g > best[0]:
            best = (g, a[0], b[0])
    gap_min, from_id, to_id = best
    assert gap_min == BIG_GAP
    second = sorted(int((b[1] - a[1]).total_seconds() // 60)
                    for a, b in zip(by_time, by_time[1:]))[-2]
    assert second < gap_min, "runner-up gap must be strictly smaller"

    body = [
        "TIMELINE MONITOR EVENTS - NOT IN TIME ORDER",
        "FORMAT: EVT <4-digit id> | ts=<YYYY-MM-DDTHH:MM> | msg=<two words>",
        "",
    ]
    for i, ts, m in file_order:
        body.append("EVT %04d | ts=%s | msg=%s" % (i, ts.strftime("%Y-%m-%dT%H:%M"), m))

    PROMPT.write_text(HEADER + "\n".join(body) + "\n" + FOOTER, encoding="utf-8")
    EXPECTED.write_text(json.dumps(
        {"from": from_id, "to": to_id, "gap_min": gap_min}, indent=2) + "\n",
        encoding="utf-8")
    print("answer: from=%d to=%d gap_min=%d" % (from_id, to_id, gap_min))
    print("prompt bytes:", PROMPT.stat().st_size)


if __name__ == "__main__":
    main()
