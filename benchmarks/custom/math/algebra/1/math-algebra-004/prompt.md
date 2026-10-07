# Cracked-mixer settings

A food-plant mixer has three dial settings, all whole numbers of turns: `x`, `y`, `z`.
A technician records three calibration readings that the settings must satisfy simultaneously:

1. `2x + 3y - z = 14`
2. `x - y + 2z = 7`
3. `3x + y + z = 19`

Facts that close off shortcuts:

- There is exactly one triple `(x, y, z)` satisfying all three equations, and every
  component is an integer. Do not report rounded decimals: a decimal answer such as
  `x = 4.99` is wrong, not "close enough".
- Gaussian elimination on this system produces non-integer intermediate fractions
  (for example the first normalization step divides by 2). You must keep every
  intermediate result exact (as a fraction) until the final integer values drop out.
  Rounding any intermediate to 2 decimals changes the answer.
- After solving, compute the wear index `w = x^2 + 2*y^2 + 3*z^2`, evaluated with the
  exact integer values (squaring before any division; there is no division in `w`).

Report four integers: `x`, `y`, `z`, and `w`.

End your response with a final line of exactly this form and nothing after it:

FINAL: x=<integer> y=<integer> z=<integer> w=<integer>

The final line is the only part graded. Do not use commas, spaces inside the values,
units, or extra keys.
