# Integer expression evaluator

Implement a tiny arithmetic evaluator in a single new module, `$OUT_DIR/calc.py`,
exposing exactly one public function:

```python
def evaluate(expr):
    ...
```

`expr` is a Python `str`. The function returns a Python `int`. Nothing else in
the module matters, but the module must import cleanly without printing anything
and without executing anything at import time, and it must use only the standard
library.

## Grammar

```
expression  := term (('+' | '-') term)*
term        := factor (('*' | '/') factor)*
factor      := '-' factor | '(' expression ')' | number
number      := '0'..'9' repeated one or more times
```

Rules:

* `number` is a non-empty run of ASCII digits, with no sign, no decimal point
  and no separator. `1.5`, `+5` and `1e3` are all invalid.
* The four binary operators are `+`, `-`, `*`, `/`. They are all **left
  associative**: `10-2-3` is `5` and `100/10/5` is `2`.
* `*` and `/` bind tighter than `+` and `-`.
* A leading `-` is unary negation and applies to the `factor` immediately after
  it; it may be repeated (`--3` is `3`). Unary `+` is **not** supported.
* Whitespace (spaces and tabs) may appear between tokens and is ignored; it may
  not appear inside a `number`.
* `/` is **integer division truncating toward zero**: `7/2` is `3`, `-7/2` is
  `-3`, `7/-2` is `-3`, `-7/-2` is `3`, `1/-2` is `0`. Results are exact Python
  integers with unbounded precision (no floating point), so
  `12345678901234567890/3` is `4115226300411522630`.
* Dividing by zero must raise `ZeroDivisionError`.
* Any input that does not conform to the grammar above must raise `ValueError`.
  This includes the empty string, a string of only whitespace, `()`, `(1+2`,
  `1+2)`, `1+`, `1++2`, `2^3`, `2 3` and `abc`.

There is no implicit multiplication, no exponentiation, and no other operator.

## Deliverable

Write `calc.py` into the output directory (`$OUT_DIR`). It will be imported and
`evaluate` will be called with each fixed test vector; every result and every
required exception must match exactly. Nothing in your response text is graded.