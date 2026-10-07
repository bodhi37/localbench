# Forge-count recurrence

A forge's spark count on firing `n` follows the sequence defined by:

- `a(1) = 2`,
- `a(n+1) = a(n)^2 - a(n) + 1` for `n >= 1`.

So the second term is `2^2 - 2 + 1 = 3`, the third is `3^2 - 3 + 1 = 7`, and so on.
The sequence grows fast: each step roughly squares the previous term.

Rules that close off shortcuts:

- Indexing starts at 1: `a(1) = 2` is the first term. There is no `a(0)`.
  Computing "the 6th term" of a sequence that starts at `a(0) = 2` gives a
  different (wrong) value.
- Every step must use exact integer arithmetic. By the 5th term the values exceed
  one thousand, and squaring them exceeds one million, so a computation in
  floating point (or any rounded intermediate) risks an off-by-one error. Use
  exact integers throughout: `a(n+1) = a(n) x (a(n) - 1) + 1` is an equivalent
  exact form.
- After finding `a(6)`, also compute its digit sum `digit_sum`: the sum of its
  decimal digits (for example the digit sum of 107 is 8).

Report two integers: `a6` (the 6th term) and `digit_sum` (its digit sum).

End your response with a final line of exactly this form and nothing after it:

FINAL: a6=<integer> digit_sum=<integer>

The final line is the only part graded. Do not use commas, scientific notation,
or extra keys.
