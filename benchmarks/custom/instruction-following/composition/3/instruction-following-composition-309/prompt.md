# Single-line sensor summary object

A mast uses the site token `cobalt` and logs three sensor readings:

* sensor `A` = 42
* sensor `B` = 57
* sensor `C` = 36

Derive these values:

* `total` — the sum of the three readings (base-10 integer).
* `mean` — the arithmetic mean of the three readings, rounded half-up to the
  nearest integer (base-10 integer).
* `max_label` — the label (`A`, `B` or `C`) with the largest reading
  (all readings are distinct).
* `order` — the three labels sorted in ascending order of reading (smallest
  first), as a JSON array of strings.
* `check` — the sum of the decimal digits of `total`, reduced modulo 256,
  written as exactly 2 capital hexadecimal digits (JSON string).
* `tier` — the string `"HIGH"` if `total` > 100, otherwise the string `"LOW"`
  (nested conditional rule 1).
* `alert` — the JSON boolean `true` if the largest reading is > 50, otherwise
  `false` (nested conditional rule 2; a bare boolean, not a string).
* `site` — the site token in capital letters (JSON string).
* `stats` — a nested JSON object with exactly these keys: `max` (= `max_label`
  string), `mean` (= `mean` integer), `total` (= `total` integer).

## Output contract

Your entire response must be exactly one line: a single JSON object with exactly
these nine top-level keys (no more, no fewer):

`alert`, `check`, `max_label`, `mean`, `order`, `site`, `stats`, `tier`, `total`

Rules:

* Top-level keys appear in this exact alphabetical order; the nested `stats`
  keys appear in alphabetical order (`max`, `mean`, `total`).
* Separators are `:` and `,` with nothing around them: no spaces, no tabs, no
  newlines inside the line. The line contains no space or tab character at all.
* Strings use double quotes; numbers are bare; `alert` is a bare `true`/`false`.
  No trailing comma.
* No leading or trailing whitespace (one trailing newline in the file is
  tolerated and ignored), no preamble, no explanation, no second line.

Example shape (values are placeholders, not the answer):

{"alert":false,"check":"00","max_label":"A","mean":0,"order":["A"],"site":"X","stats":{"max":"A","mean":0,"total":0},"tier":"LOW","total":0}

Replace every placeholder with the derived value. The whole response is graded,
so one misplaced comma, space, or key breaks it.
