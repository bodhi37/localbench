# Pair-sum counter: correct and linear

This task folder contains `resources/starter.py`. It declares one stub
function. Implement a pair-sum counter that is both correct on edge cases and
fast enough for large inputs.

Deliver a complete module as `$OUT_DIR/pairsum.py` with exactly this public
function (keep the name, signature, and docstring):

* `count_pairs(values, target)` — `values` is a list of integers and `target`
  is an integer. Return the number of index pairs `(i, j)` with `i < j` such
  that `values[i] + values[j] == target`. An empty list or a single element
  returns `0`. Duplicate values are counted combinatorially (e.g. `[1, 1, 1]`
  with target `2` gives `3`). Must not modify `values`.

  The function must run in linear time: grading includes a 50,000-element
  input that must finish within 5 seconds (a quadratic double loop will not
  pass).

The module must import cleanly **without printing anything and without running
anything at import time** (keep the module-level code to definitions and
imports only). The module must not use third-party imports.

Your file will be imported and `count_pairs` called with fixed test vectors,
including empty and singleton lists, no-match inputs, duplicates, zeros,
negative numbers, negative targets, large values, unsorted input, and the
large timing-gate input. Any behaviour that differs from the specification
above fails.
