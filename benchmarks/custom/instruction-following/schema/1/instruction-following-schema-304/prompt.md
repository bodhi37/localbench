# Five-node inventory table

A depot uses the site token `halcyon`.

It logs five crate counts:

| code | count |
|---|---|
| K7 | 41 |
| A3 | 17 |
| M2 | 88 |
| Z1 | 53 |
| Q9 | 26 |

Derive the seven values below:

* `ROWS` — the number of crate rows, written with exactly 3 digits (zero-padded).
* `TOTAL` — the sum of the five counts, in base 10.
* `MIN_CODE` — the code with the smallest count (all counts are distinct).
* `MAX_CODE` — the code with the largest count.
* `ORDER` — the five codes sorted in ascending order of count (smallest first),
  joined with single commas and no spaces.
* `CHECK` — the sum of the decimal digits of `TOTAL`, reduced modulo 256, written
  as exactly 2 capital hexadecimal digits (`00`–`FF`, zero-padded).
* `TAG` — the site token written in capital letters.

## Output contract

Your entire response must be exactly these nine lines, in this order, and nothing
else — no preamble, no explanation, no trailing text, no blank lines:

```
BEGIN TABLE
ROWS=<value>
TOTAL=<value>
MIN_CODE=<value>
MAX_CODE=<value>
ORDER=<value>
CHECK=<value>
TAG=<value>
END TABLE
```

Replace each `<value>` with the derived value. The whole response is graded, so a
single extra character makes it wrong.
