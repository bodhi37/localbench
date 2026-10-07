#!/usr/bin/env python3
"""Deterministic generator for prompt.md of long-context-versiondiff-208.

Plain mode has no filesystem, so the corpus lives inline in prompt.md.
Re-running this script reproduces prompt.md byte-for-byte (seed 208001).
Stdlib only.
"""
import json
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROMPT = HERE.parent / "prompt.md"
EXPECTED = HERE / "expected.json"

SEED = 208001
NCLAUSE = 40
V1_TO_V2 = ["C05", "C12", "C27", "C33"]  # decoys: changed before v2, stable after
V2_TO_V3 = ["C07", "C19", "C31"]  # the true answer set
WORDS = ["amber", "basalt", "circuit", "dorsal", "embark", "fathom", "granite",
         "harbor", "inlet", "juniper", "kelp", "lagoon", "magnet", "nickel",
         "onyx", "pumice", "quartz", "ridge", "saddle", "thicket",
         "umbra", "vortex", "willow", "xenon", "yarrow", "zephyr", "cobalt",
         "dune", "ember", "fjord", "grove", "heath", "iris", "jetty",
         "kiosk", "larch", "meadow", "north", "opal", "prairie"]

HEADER = """# Specification version diff

A specification is restated in full at three versions. Each version section
starts with a header line (`SPEC v1`, `SPEC v2`, `SPEC v3`) followed by 40
clause lines, each of exactly this form:

```
C<two digits>: <eight words>
```

Only lines that start with `C` followed by two digits are clause lines; the
`SPEC` lines are section headers, not clauses. Within one version every clause
id `C01`..`C40` appears exactly once.

Clauses change between versions: some clauses were rewritten from v1 to v2,
and some (a different set) were rewritten from v2 to v3. Your task covers ONLY
the v2 -> v3 step: list the ids of the clauses whose text differs between the
`SPEC v2` section and the `SPEC v3` section. Clauses that changed from v1 to
v2 but are identical in v2 and v3 must NOT be listed. Clause comparison is
exact and case-sensitive on the full eight-word text.

## Specification

```
"""

FOOTER = """```

## Report

End your response with a final line of exactly this form and nothing after it:

FINAL: changed=<C..>,<C..>,<C..>

* List every clause id whose v2 text differs from its v3 text, and no other id.
* Sort ascending (C07 before C19), separate with single commas, no spaces.
* Each id is the literal clause id exactly as it appears (e.g. `C07`).

The final line is the only part graded; anything else in your response is
ignored.
"""


def sentence(rng):
    return " ".join(rng.choice(WORDS) for _ in range(8))


def main():
    rng = random.Random(SEED)
    v1 = {("C%02d" % i): sentence(rng) for i in range(1, NCLAUSE + 1)}
    v2 = dict(v1)
    for c in V1_TO_V2:
        v2[c] = sentence(rng)
    v3 = dict(v2)
    for c in V2_TO_V3:
        v3[c] = sentence(rng)
    assert {c for c in v1 if v1[c] != v2[c]} == set(V1_TO_V2)
    changed = sorted(c for c in v2 if v2[c] != v3[c])
    assert changed == sorted(V2_TO_V3), changed
    assert not (set(V1_TO_V2) & set(V2_TO_V3)), "decoys must be disjoint"

    body = []
    for ver, snap in (("v1", v1), ("v2", v2), ("v3", v3)):
        body.append("SPEC %s" % ver)
        for i in range(1, NCLAUSE + 1):
            cid = "C%02d" % i
            body.append("%s: %s" % (cid, snap[cid]))
        body.append("")

    PROMPT.write_text(HEADER + "\n".join(body) + "\n" + FOOTER, encoding="utf-8")
    EXPECTED.write_text(json.dumps(
        {"changed": changed}, indent=2) + "\n", encoding="utf-8")
    print("answer: changed=%s" % ",".join(changed))
    print("prompt bytes:", PROMPT.stat().st_size)


if __name__ == "__main__":
    main()
