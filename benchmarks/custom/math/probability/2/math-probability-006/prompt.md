# Cask-draw odds

A cellar urn holds 16 bottle tokens that are identical except for color:
4 ruby, 5 sapphire, and 7 emerald. Three tokens are drawn at random **without
replacement** (one handful of three; every 3-subset is equally likely).

Condition on the event E: **exactly two** of the three drawn tokens share a color
(i.e. the hand is a pair plus one token of a different color). Three-of-a-kind
hands do **not** satisfy E and are excluded from both the numerator and the
denominator. Hands with three different colors likewise do not satisfy E.

Question: given E, what is the probability that the pair is ruby?

Rules that close off shortcuts:

- Draws are without replacement: after each token is taken the urn composition
  changes. A computation that treats the draws as independent with fixed
  probabilities 4/16, 5/16, 7/16 is wrong.
- Ordered and unordered counting give the same ratio, but you must count E as
  "exactly one pair": `P(pair is ruby | E) = (ruby-pair hands) / (all exactly-one-pair hands)`.
  Using "at least one pair" (which would admit triples) in the denominator is wrong.
- Report the answer as a fraction in lowest terms: two positive integers `p_num`
  (numerator) and `p_den` (denominator) with `gcd(p_num, p_den) = 1`. An equivalent
  non-reduced fraction (for example any common multiple of both parts) is wrong.

End your response with a final line of exactly this form and nothing after it:

FINAL: p_num=<integer> p_den=<integer>

The final line is the only part graded. Do not use slashes, decimals, or spaces
inside the values.
