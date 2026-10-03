# Stock reconciliation from an event log

This task folder contains `resources/warehouse_events.log`, a warehouse event log.

## Log format

* A line beginning `INITIAL <bin> <sku> <qty>` gives opening stock: bin `<bin>`
  holds `<qty>` units of SKU `<sku>`. Bins hold different SKUs independently;
  any `(bin, sku)` pair with no `INITIAL` line starts at 0 units.
* Every other non-blank line is an event: `<seq> <OP> <arguments...>`, where
  `<seq>` is a positive integer. Events are processed **in the order they appear
  in the file**. Seqs are strictly increasing but are not necessarily
  contiguous, and a seq identifies exactly one event.
* Any other non-blank line is prose and carries no state.

## Operations

Each operation names the `(bin, sku)` pair(s) it affects.

* `RECEIVE <bin> <sku> <qty>` — add `<qty>` units to `(bin, sku)`.
* `PICK <bin> <sku> <qty>` — subtract `<qty>` units from `(bin, sku)`.
* `TRANSFER <from_bin> <to_bin> <sku> <qty>` — subtract `<qty>` from
  `(from_bin, sku)` and add `<qty>` to `(to_bin, sku)`.
* `RECOUNT <bin> <sku> <qty>` — set `(bin, sku)` to exactly `<qty>` units.
* `VOID <seq>` — cancel the effect of the event whose seq is `<seq>`, by
  applying that event's inverse to the **current** counts at the moment the
  `VOID` is processed. History is not replayed.
  * Only `RECEIVE`, `PICK` and `TRANSFER` events can be voided.
  * An effective `VOID` of a `RECEIVE` subtracts what that `RECEIVE` added; of a
    `PICK` adds back what that `PICK` removed; of a `TRANSFER` moves the same
    quantity back from its `to_bin` to its `from_bin`.
  * A `VOID` has **no effect at all** when its target is a `RECOUNT`, is a
    `VOID`, does not exist in the file, has not yet been applied (its seq
    appears later in the file), or has already been voided.
  * Each event can be voided at most once.
* Counts are signed and may go below zero. No operation is ever rejected or
  clamped.

## Report (SKU `NX-4471` only)

* `final_bins` — an object mapping each of the bins `A-01`, `A-02` and `B-07` to
  its final count of `NX-4471`.
* `effective_voids` — how many `VOID` lines in the file actually cancelled an
  event.
* `net_change` — (sum of those three final counts) minus (sum of the opening
  counts of `NX-4471` in those same three bins).

## Deliverable

Write exactly one file named `answer.json` into the output directory
(`$OUT_DIR`). It must contain a single JSON object with exactly these three keys
and no others:

```
{"final_bins": {"A-01": <integer>, "A-02": <integer>, "B-07": <integer>}, "effective_voids": <integer>, "net_change": <integer>}
```

All values must be JSON integers (not strings, not floats). Nothing in your
response text is graded; only the file is.