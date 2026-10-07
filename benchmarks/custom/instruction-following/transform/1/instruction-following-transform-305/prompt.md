# Normalise three lines

Normalise each of the three source sentences below with exactly this procedure,
in this order:

1. Convert every capital letter (`A`–`Z`) to its lowercase form.
2. Delete every character that is not a lowercase letter (`a`–`z`) or a space.
   (This removes punctuation such as `!`, `,` and `.`.)
3. Collapse every run of one or more spaces into a single space, and remove any
   leading or trailing space.
4. Split on spaces into words and rejoin the words with a single hyphen (`-`).

Source sentences:

* S1: `Solar Panels Generate Power`
* S2: `Quiet Rivers Flow North!`
* S3: `Brisk Winds, Lift Kites.`

Derive:

* `L1`, `L2`, `L3` — the normalised forms of S1, S2, S3.
* `COUNT` — the number of source sentences, written with exactly 3 digits
  (zero-padded).
* `CHECK` — the total number of characters across the three normalised values
  (count the characters in `L1` plus `L2` plus `L3`, not counting the `L1=` prefixes),
  written with exactly 3 digits (zero-padded).

## Output contract

Your entire response must be exactly these seven lines, in this order, and nothing
else — no preamble, no explanation, no trailing text, no blank lines:

```
BEGIN LINES
L1=<value>
L2=<value>
L3=<value>
COUNT=<value>
CHECK=<value>
END LINES
```

Replace each `<value>` with the derived value. The whole response is graded, so a
single extra character makes it wrong.
