#!/usr/bin/env python3
"""Deterministic generator for prompt.md of long-context-statetrack2-209.

Plain mode has no filesystem, so the corpus lives inline in prompt.md.
Re-running this script reproduces prompt.md byte-for-byte (seed 209001).
Stdlib only.
"""
import json
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROMPT = HERE.parent / "prompt.md"
EXPECTED = HERE / "expected.json"

SEED = 209001
START = 50000  # cents
NBASE = 96
MEMOS = ["rent", "payroll", "refund", "invoice", "rebate", "fee", "order",
         "grant", "tax", "bonus", "freight", "parts"]

HEADER = """# Ledger with voids and corrections

A cash ledger starts at a balance of 50000 cents. Every ledger line has one of
these exact forms (`<id>` and `<target>` are 4-digit ids, amounts are bare
integer cents):

```
TX <id> | CREDIT amt=<cents> | memo=<word>
TX <id> | DEBIT amt=<cents> | memo=<word>
TX <id> | VOID <target> | memo=<word>
TX <id> | CORRECT <target> new=<cents> | memo=<word>
```

Lines that start with `CASH` or `FORMAT` are header lines, not records. Only
lines that start with `TX ` (with a trailing space) are records. Records are
processed in ascending TX id order.

Posting rules:

* `CREDIT` adds its amount to the balance; `DEBIT` subtracts it.
* `VOID <target>` cancels the target record entirely, as if it had never
  posted (including cancelling any correction previously applied to it).
  A VOID is a no-op unless its target is a `CREDIT` or `DEBIT` record that has
  not already been voided. In particular, voiding an already-voided record, or
  voiding a `VOID` or `CORRECT` line, does nothing.
* `CORRECT <target> new=<cents>` replaces the target's posted amount with the
  new amount. A CORRECT is a no-op unless its target is a `CREDIT` or `DEBIT`
  record that has not been voided (a correction aimed at an already-voided
  record, or at a `VOID`/`CORRECT` line, does nothing).

Some VOID and CORRECT lines in the ledger are traps: they look operative but
are no-ops under these rules. No live (non-voided) record is ever both
corrected and voided, so each live record posts exactly one final amount.

Your task: compute the final balance in cents and count the effective records
(the CREDIT/DEBIT records that are not voided).

## Ledger

```
"""

FOOTER = """```

## Report

End your response with a final line of exactly this form and nothing after it:

FINAL: balance_cents=<integer> effective=<integer>

* `balance_cents` is the exact final balance as a bare integer number of cents
  (leading zeros are not significant; it may be any non-negative integer).
* `effective` is the count of non-voided CREDIT/DEBIT records, as a base-10
  integer (leading zeros are not significant).

The final line is the only part graded; anything else in your response is
ignored.
"""


def main():
    rng = random.Random(SEED)
    kind = [rng.choice(["CREDIT", "DEBIT"]) for _ in range(NBASE)]
    amt = [rng.randrange(100, 20000) for _ in range(NBASE)]
    memo = [rng.choice(MEMOS) for _ in range(NBASE)]

    base_ids = list(range(1, NBASE + 1))
    void_targets = rng.sample(base_ids, 6)
    remaining = [i for i in base_ids if i not in void_targets]
    correct_targets = rng.sample(remaining, 4)
    assert not (set(void_targets) & set(correct_targets))

    ops = []  # (txid, text, effect)
    for i in range(1, NBASE + 1):
        ops.append((i, "TX %04d | %s amt=%d | memo=%s"
                    % (i, kind[i - 1], amt[i - 1], memo[i - 1])))
    tx = NBASE + 1
    correct_new = {}
    for t in correct_targets:
        new = rng.randrange(100, 20000)
        correct_new[t] = new
        ops.append((tx, "TX %04d | CORRECT %04d new=%d | memo=%s"
                    % (tx, t, new, rng.choice(MEMOS))))
        tx += 1
    for t in void_targets:
        ops.append((tx, "TX %04d | VOID %04d | memo=%s"
                    % (tx, t, rng.choice(MEMOS))))
        tx += 1
    # Traps (all no-ops): correct an already-voided record; correct a VOID line;
    # void an already-voided record; void a CORRECT line.
    trap_correct_line = NBASE + 1  # first CORRECT line id
    trap_void_line = NBASE + 5  # first VOID line id
    ops.append((tx, "TX %04d | CORRECT %04d new=%d | memo=%s"
                % (tx, void_targets[0], rng.randrange(100, 20000),
                   rng.choice(MEMOS))))
    tx += 1
    ops.append((tx, "TX %04d | CORRECT %04d new=%d | memo=%s"
                % (tx, trap_void_line, rng.randrange(100, 20000),
                   rng.choice(MEMOS))))
    tx += 1
    ops.append((tx, "TX %04d | VOID %04d | memo=%s"
                % (tx, void_targets[1], rng.choice(MEMOS))))
    tx += 1
    ops.append((tx, "TX %04d | VOID %04d | memo=%s"
                % (tx, trap_correct_line, rng.choice(MEMOS))))
    tx += 1
    assert tx - 1 == NBASE + 14 == 110

    voided = set(void_targets)
    balance = START
    effective = 0
    for i in range(1, NBASE + 1):
        if i in voided:
            continue
        effective += 1
        a = correct_new.get(i, amt[i - 1])
        balance += a if kind[i - 1] == "CREDIT" else -a
    assert effective == NBASE - len(void_targets)
    assert balance >= 0, "keep the balance non-negative by construction check"

    body = [
        "CASH LEDGER - START 50000 CENTS - ONE RECORD PER LINE",
        "FORMAT: TX <id> | CREDIT/DEBIT amt=<cents> | VOID <target> | CORRECT <target> new=<cents>",
        "",
    ]
    body += [text for _tx, text in sorted(ops)]

    PROMPT.write_text(HEADER + "\n".join(body) + "\n" + FOOTER, encoding="utf-8")
    EXPECTED.write_text(json.dumps(
        {"balance_cents": balance, "effective": effective}, indent=2) + "\n",
        encoding="utf-8")
    print("answer: balance_cents=%d effective=%d" % (balance, effective))
    print("prompt bytes:", PROMPT.stat().st_size)


if __name__ == "__main__":
    main()
