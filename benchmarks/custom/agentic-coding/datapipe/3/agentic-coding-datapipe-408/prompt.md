# Shift-log pipeline: normalize, dedupe, aggregate

This task folder contains `resources/starter.py`. It declares one stub
function. Implement the three-stage pipeline described below.

Deliver a complete module as `$OUT_DIR/pipeline.py` with exactly this public
function (keep the name, signature, and docstring):

* `run_pipeline(rows)` — `rows` is a list of shift-log rows. Process them in
  three strict stages and return
  `{"depts": {dept: {"total_hours": t, "count": n}}, "errors": e}`.

  Stage 1 — normalize (in input order; any failure marks the row an *error
  row*: skip it and count it in `errors`):
  - A row must be a `dict` with `"name"`, `"dept"`, and `"hours"` keys;
    anything else (including extra keys, which are ignored) is an error row.
  - `"name"` must be a string: strip it, collapse every internal whitespace
    run to a single space, and lowercase it. Empty after stripping is an
    error row.
  - `"dept"` must be a string: strip it, collapse every internal whitespace
    run to a single space, and uppercase it. Empty after stripping is an
    error row.
  - `"hours"` is either a number (`int`/`float`, but **not** `bool`) or a
    numeric string (surrounding whitespace allowed, parsed with `float()`).
    It must be finite (so `nan`/`inf`, including the strings `"nan"` and
    `"inf"`, are error rows) and `>= 0`. Round it with `round(h, 2)`.

  Stage 2 — dedupe: rows with an identical `(name, dept, hours)` triple after
  normalization are duplicates; keep only the first occurrence (in input
  order) and drop the rest silently (dropped duplicates are **not** errors).

  Stage 3 — aggregate: group the surviving rows by `dept`. Each group's
  `total_hours` is `round(sum of its row hours in first-occurrence order, 2)`
  and `count` is its number of rows. `errors` is the total number of error
  rows from stage 1.

  Must not modify `rows` or any dict inside it.

The module must import cleanly **without printing anything and without running
anything at import time** (keep the module-level code to definitions and
imports only). The module must not use third-party imports.

Your file will be imported and `run_pipeline` called with fixed test vectors,
including the empty list, whitespace/case variants, numeric strings,
booleans, negative/`nan`/`inf` hours, missing keys, non-dict rows, empty
names, duplicates that differ only in case or spacing, multi-department
aggregation, and all-error inputs. Any behaviour that differs from the
specification above fails.
