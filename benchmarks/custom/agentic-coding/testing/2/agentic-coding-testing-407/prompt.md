# Statistics module: fix the three seeded bugs

This task folder contains `resources/stats.py`. It summarises telemetry
samples, but its three public functions do **not** all behave as their
docstrings promise.

Deliver a corrected copy of the whole module as `$OUT_DIR/stats.py` with
exactly these three public functions (keep the names, signatures, and
docstrings):

* `mean(xs)` — return `sum(xs) / len(xs)` as a float, or `None` when `xs` is
  empty. Must not modify `xs`.
* `median(xs)` — return the middle value of a sorted copy of `xs` when its
  length is odd (the value itself, not a float conversion), or the average of
  the two middle values — `(s[mid - 1] + s[mid]) / 2` on the sorted copy `s` —
  when its length is even, or `None` when `xs` is empty. Must not modify `xs`.
* `mode(xs)` — return the most frequent value in `xs`, breaking ties in favour
  of the smallest value, or `None` when `xs` is empty. Must not modify `xs`.

The module must import cleanly **without printing anything and without running
anything at import time** (keep the module-level code to definitions only).
The module must not use third-party imports.

Your file will be imported and every function will be called with fixed test
vectors, including empty lists, single elements, negative numbers, even- and
odd-length inputs, two-element inputs, all-identical inputs, frequency ties,
and checks that the input list is never modified. Any behaviour that differs
from the specification above fails.
