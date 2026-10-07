# Courtyard paving

A courtyard is built from three parts, all dimensions in metres:

1. A rectangle 14 m by 9 m (area 126 sq m).
2. A right-triangular flower bed with legs 9 m and 12 m (hypotenuse 15 m),
   attached externally along the rectangle's 9-m side: the triangle's 9-m leg
   coincides exactly with that side, the triangle lies fully outside the
   rectangle, and there is no other overlap.
3. A semicircular pond of radius 7 m cut out of the rectangle's interior: the
   pond lies fully inside the rectangle and does not touch the shared 9-m edge,
   so it removes area without affecting the triangle.

The usable paved area is `rectangle + triangle - semicircle`.

Rules that close off shortcuts:

- Use `pi = 22/7` exactly for this task. Any other value of pi (3.14, 3.14159...,
  or a calculator default) is incorrect for grading, even if more accurate in
  general. With `pi = 22/7` every quantity below is an exact integer.
- The triangle contributes its full area `(9 x 12)/2`; do not subtract the shared
  edge (an edge has no area). Do not add the pond back: a cut-out hole is removed.
- Paving costs 37 credits per square metre of usable area. One credit is one unit;
  report the total cost as an integer number of credits.

Report two integers: `area` (usable square metres) and `cost` (credits).

End your response with a final line of exactly this form and nothing after it:

FINAL: area=<integer> cost=<integer>

The final line is the only part graded. Do not use commas, units, or decimals.
