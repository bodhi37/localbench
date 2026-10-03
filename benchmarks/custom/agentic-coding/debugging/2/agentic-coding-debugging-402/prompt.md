# Window helpers: fix the module

This task folder contains `resources/window.py`. It is a small module used by a
reporting pipeline. Its three public functions do **not** all behave as their
docstrings promise.

Deliver a corrected copy of the whole module as `$OUT_DIR/window.py`.

## Required behaviour (exact)

For a list of integers `values` and an integer `k`:

* `max_window_sums(values, k)` — the largest sum over every contiguous window of
  exactly `k` elements of `values`. Returns `None` when `k <= 0` or
  `k > len(values)`. Must not modify `values`.
* `count_windows_over(values, k, threshold)` — how many contiguous windows of
  exactly `k` elements have a sum **strictly greater** than `threshold`. Returns
  `None` when `k <= 0` or `k > len(values)`. Must not modify `values`.
* `window_starts(values, k)` — the starting indices of all contiguous windows of
  exactly `k` elements, in increasing order. Returns `[]` when `k <= 0` or
  `k > len(values)`. Must not modify `values`.

Every contiguous window counts, including the last one that fits. All three
functions keep their current names and signatures, keep their docstrings, and
the module must import cleanly **without printing anything and without running
anything at import time** (keep the module-level code to definitions only). The
module must not use third-party imports.

Your file will be imported and every function will be called with fixed test
vectors, including empty lists, `k` equal to the list length, `k` greater than
the list length, `k <= 0`, all-negative lists, and thresholds exactly equal to a
window sum. Any behaviour that differs from the specification above fails.