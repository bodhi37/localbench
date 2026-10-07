# Order pricing: refactor the monolith

This task folder contains `resources/monolith.py`. It prices orders correctly
through a single `order_total` function with all logic inline. Split that
logic into the required helper decomposition below without changing the
behaviour.

Deliver the refactored module as `$OUT_DIR/orders.py` with exactly these four
public functions (keep the names, signatures, and docstrings):

* `line_total(qty, price)` — return `qty * price`. Raise `ValueError` when
  `qty` or `price` is negative.
* `discount_rate(subtotal)` — return `0.15` when `subtotal >= 1000`, `0.10`
  when `subtotal >= 500`, `0.05` when `subtotal >= 100`, else `0.0`. Raise
  `ValueError` when `subtotal` is negative.
* `apply_discount(subtotal)` — return
  `round(subtotal * (1 - discount_rate(subtotal)), 2)` (negative inputs raise
  `ValueError` via `discount_rate`).
* `order_total(lines)` — `lines` is a list of `(qty, price)` pairs. Return
  `apply_discount` applied to the sum of `line_total(qty, price)` over every
  pair. An empty `lines` returns `0.0`. Any negative quantity or price raises
  `ValueError`. Must not modify `lines`.

Decomposition is graded by reading your source: `order_total` must actually
call `line_total` and `apply_discount`, and `apply_discount` must actually
call `discount_rate` (inlining the arithmetic instead fails, even when the
numbers are right).

The module must import cleanly **without printing anything and without running
anything at import time** (keep the module-level code to definitions only).
The module must not use third-party imports.

Your file will be imported and every function called with fixed test vectors,
including zero quantities, exact discount thresholds (`100`, `500`, `1000`),
values just below each threshold, negative inputs that must raise
`ValueError`, multi-line orders, and the empty order. Any behaviour that
differs from the specification above fails.
