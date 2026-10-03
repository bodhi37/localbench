# Counting strings that avoid two patterns

Let a **binary string** be any string over the alphabet `{0, 1}`, including the empty string. A binary string is **admissible** when it does **not** contain `010` as a contiguous substring and does **not** contain `1110` as a contiguous substring. Occurrences are counted as contiguous runs of characters, and overlapping occurrences all count; a string is inadmissible as soon as it contains at least one occurrence of either forbidden pattern. Single characters and the empty string are trivially admissible.

Let `f(n)` be the number of admissible binary strings of length exactly `n` (for `n >= 1`), where two strings are different if they differ in any position.

Report three integers:

* `a` = `f(1000)` modulo `1000000007`;
* `b` = `f(1000000000)` modulo `1000000007`;
* `c` = `f(1000)` modulo `97`.

Each result must be the non-negative remainder, so `0 <= a, b < 1000000007` and `0 <= c < 97`.

End your response with a final line of exactly this form and nothing after it:

FINAL: a=<integer> b=<integer> c=<integer>

The final line is the only part graded. Use plain base-10 integers with no commas, signs, or units.