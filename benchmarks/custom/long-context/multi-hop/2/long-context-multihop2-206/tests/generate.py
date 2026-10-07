#!/usr/bin/env python3
"""Deterministic generator for prompt.md of long-context-multihop2-206.

Plain mode has no filesystem, so the corpus lives inline in prompt.md.
Re-running this script reproduces prompt.md byte-for-byte (seed 206001).
Stdlib only.
"""
import json
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROMPT = HERE.parent / "prompt.md"
EXPECTED = HERE / "expected.json"

SEED = 206001
TARGET_MEMBER = "Rosa Aldana"
TARGET_TEAM = "K-7"
TARGET_VESSEL = "SS-MERIDIAN"
TARGET_DATE = "2026-03-14"
TARGET_PORT = "LUMEN"
TRAP_VESSEL = "SS-MERIDIAN-II"
TRAP_PORT = "HARBOR-9"

TEAMS = ["K-3", "K-5", "K-7", "K-9", "K-11", "K-13", "K-15", "K-17",
         "K-19", "K-21", "K-23", "K-25", "K-27", "K-29", "K-71", "K-77"]
VESSELS = {"K-3": "SS-CONTRAIL", "K-5": "SS-HALCYON", "K-7": TARGET_VESSEL,
           "K-9": "SS-PEREGRINE", "K-11": "SS-KITE", "K-13": "SS-TERN",
           "K-15": "SS-ALBATROSS", "K-17": "SS-FULMAR", "K-19": "SS-SKUA",
           "K-21": "SS-GANNET", "K-23": "SS-CORMORANT", "K-25": "SS-PETREL",
           "K-27": "SS-SHEARWATER", "K-29": "SS-GUILLEMOT",
           "K-71": TRAP_VESSEL, "K-77": "SS-MERIDIANA"}
PORTS = ["LUMEN", "HARBOR-9", "KESTREL-BAY", "NORTH-QUAY", "SALT-REACH",
         "GULL-ROAD", "TIDEWATER", "SHINGLE-2", "BREAKWATER", "FAIRLEE",
         "DUNMORE", "SKERRIES"]
FIRST = ["Anya", "Bram", "Celia", "Dmitri", "Elif", "Farah", "Gus", "Hana",
         "Ivo", "Jana", "Kofi", "Lena", "Marco", "Nadia", "Omar", "Priya",
         "Quinn", "Ruth", "Sven", "Tara", "Umar", "Vera", "Wren", "Yusuf"]
LAST = ["Bakker", "Costa", "Duarte", "Ellery", "Fontaine", "Grady", "Holt",
        "Ibarra", "Jensen", "Kovac", "Lund", "Moss", "Nolan", "Osman",
        "Pike", "Reyes", "Sorel", "Thane", "Ulfsson", "Vane", "Wick",
        "Xu", "Yanez", "Zeller"]
DISTRACTOR_MEMBERS = [("Rosa Aldano", "K-71"), ("Rose Aldana", "K-77"),
                      ("Rosa Aldama", "K-9")]

HEADER = """# Crew rotation trace (three hops)

Three inline tables follow. Line prefixes determine the table; lines starting
with `FLEET`, `FORMAT`, or `QUERY` are headers, not records.

* ROSTER records look like `MEMBER <First Last> | TEAM <code>` and assign each
  crew member to exactly one team. Member names match exactly and
  case-sensitively on the full name: `Rosa Aldana` is a different member from
  `Rosa Aldano`, `Rose Aldana`, and `Rosa Aldama`.
* ASSIGN records look like `TEAM <code> | VESSEL <vessel>` and assign each team
  to exactly one vessel. Team and vessel codes match exactly: `K-7` is not
  `K-71`, and `SS-MERIDIAN` is not `SS-MERIDIAN-II`.
* LOG records look like `LOG <4-digit id> | VESSEL <vessel> | PORT <port> |
  date=<YYYY-MM-DD>` and state where a vessel was on a date.

QUERY: member `Rosa Aldana`. Follow the chain member -> team -> vessel, then
find which port that vessel was at on date `2026-03-14`. That vessel has
exactly one LOG record on that date; other vessels (including the similar
`SS-MERIDIAN-II`) also sail that day, so all three hops must be exact.

## Tables

```
"""

FOOTER = """```

## Report

End your response with a final line of exactly this form and nothing after it:

FINAL: team=<TEAM> vessel=<VESSEL> port=<PORT>

* `team` is Rosa Aldana's team code exactly as it appears in ROSTER.
* `vessel` is that team's vessel exactly as it appears in ASSIGN.
* `port` is that vessel's port on 2026-03-14 exactly as it appears in LOG.

The final line is the only part graded; anything else in your response is
ignored.
"""


def main():
    rng = random.Random(SEED)
    members = [(TARGET_MEMBER, TARGET_TEAM)] + DISTRACTOR_MEMBERS[:]
    used = {TARGET_MEMBER} | {m for m, _t in DISTRACTOR_MEMBERS}
    while len(members) < 30:
        name = "%s %s" % (rng.choice(FIRST), rng.choice(LAST))
        if name in used:
            continue
        used.add(name)
        members.append((name, rng.choice(TEAMS)))
    rng.shuffle(members)
    assert len({m for m, _t in members}) == 30
    assert [t for m, t in members if m == TARGET_MEMBER] == [TARGET_TEAM]

    logs = []
    n = 0
    while n < 88:
        v = rng.choice(sorted(VESSELS.values()))
        d = "2026-03-%02d" % rng.randint(1, 28)
        if v == TARGET_VESSEL and d == TARGET_DATE:
            continue  # planted below, exactly once
        logs.append((v, PORTS[rng.randrange(len(PORTS))], d))
        n += 1
    logs.append((TARGET_VESSEL, TARGET_PORT, TARGET_DATE))
    logs.append((TRAP_VESSEL, TRAP_PORT, TARGET_DATE))
    assert sum(1 for v, _p, d in logs
               if v == TARGET_VESSEL and d == TARGET_DATE) == 1
    rng.shuffle(logs)

    body = [
        "FLEET CREW ROTATION - ROSTER, ASSIGN, LOG TABLES",
        "FORMAT: MEMBER <First Last> | TEAM <code> // TEAM <code> | VESSEL <vessel> // LOG <id> | VESSEL <vessel> | PORT <port> | date=<YYYY-MM-DD>",
        "",
    ]
    for m, t in members:
        body.append("MEMBER %s | TEAM %s" % (m, t))
    body.append("")
    for t in TEAMS:
        body.append("TEAM %s | VESSEL %s" % (t, VESSELS[t]))
    body.append("")
    for i, (v, p, d) in enumerate(logs, 1):
        body.append("LOG %04d | VESSEL %s | PORT %s | date=%s" % (i, v, p, d))

    PROMPT.write_text(HEADER + "\n".join(body) + "\n" + FOOTER, encoding="utf-8")
    EXPECTED.write_text(json.dumps(
        {"team": TARGET_TEAM, "vessel": TARGET_VESSEL, "port": TARGET_PORT,
         "date": TARGET_DATE}, indent=2) + "\n", encoding="utf-8")
    print("answer: team=%s vessel=%s port=%s date=%s"
          % (TARGET_TEAM, TARGET_VESSEL, TARGET_PORT, TARGET_DATE))
    print("prompt bytes:", PROMPT.stat().st_size)


if __name__ == "__main__":
    main()
