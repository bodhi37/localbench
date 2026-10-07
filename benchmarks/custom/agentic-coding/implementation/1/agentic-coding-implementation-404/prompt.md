# Interval helpers: implement the module

This task folder contains `resources/starter.py`. It declares two stub
functions with docstrings. Implement them.

Deliver a complete module as `$OUT_DIR/intervals.py` with exactly these two
public functions (keep the names, signatures, and docstrings):

* `merge_intervals(intervals)` — `intervals` is a list of 2-element
  `[start, end]` lists or tuples of integers with `start <= end`. Return a NEW
  list of `[start, end]` lists (plain lists, even if the input used tuples),
  sorted by start, merging every pair of overlapping **or touching** intervals
  (touching means the next start is `<=` the current end, so `[1, 3]` and
  `[3, 5]` merge into `[1, 5]`, while `[1, 2]` and `[4, 5]` stay separate). An
  empty input returns `[]`. Must not modify `intervals` or any pair inside it.
* `is_covered(intervals, point)` — return `True` when at least one interval
  contains `point` (inclusive on both ends: `start <= point <= end`), else
  `False`. An empty `intervals` returns `False`. Must not modify `intervals`.

The module must import cleanly **without printing anything and without running
anything at import time** (keep the module-level code to definitions only).
The module must not use third-party imports.

Your file will be imported and both functions will be called with fixed test
vectors, including empty lists, a single interval, unsorted input, nested
intervals, touching endpoints, gaps, negative numbers, duplicate intervals,
and points exactly on endpoints. Any behaviour that differs from the
specification above fails.
