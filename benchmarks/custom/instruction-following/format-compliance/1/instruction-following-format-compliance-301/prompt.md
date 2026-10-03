# Fixed-width status report

A bench rig logs four probe readings. The rig's site token is `merlin`.

Readings, in the order the probes are labelled:

| probe | reading (milli-units) |
|---|---|
| A | 1526 |
| B | 1498 |
| C | 1602 |
| D | 1451 |

Derive the six values below and emit them as a seven-line block.

* `SITE` — the site token written in capital letters.
* `SAMPLES` — the number of probe readings, written with exactly 3 digits (zero-padded).
* `MEAN_MILLI` — the arithmetic mean of the four readings, in milli-units, rounded
  **half-up** to the nearest integer.
* `MAX_LABEL` — the label (`A`, `B`, `C` or `D`) of the probe with the largest reading.
* `CHECK` — the sum of the decimal digits of `MEAN_MILLI`, reduced modulo 256, written
  as exactly 2 capital hexadecimal digits (`00`–`FF`, zero-padded).
* The first line is the literal `BEGIN REPORT` and the last line is the literal `END REPORT`.

## Output contract

Your entire response must be exactly these seven lines, in this order, and nothing
else — no preamble, no explanation, no trailing text, no blank lines:

```
BEGIN REPORT
SITE=<value>
SAMPLES=<value>
MEAN_MILLI=<value>
MAX_LABEL=<value>
CHECK=<value>
END REPORT
```

Replace each `<value>` with the derived value. The whole response is graded, so a
single extra character makes it wrong.