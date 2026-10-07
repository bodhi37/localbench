# Hohmann-like transfer: first burn and transfer-ellipse period

A satellite is initially in a circular orbit of radius **r1 = 6678 km** about Earth's centre. It performs a prograde burn placing it on an elliptical transfer orbit with periapsis **r1** and apoapsis **r2 = 42164 km** (both measured from Earth's centre). Only the first (periapsis) burn and the transfer-ellipse period are considered here; the circularisation burn at apoapsis is not part of this task.

Use **GM = 398600 km^3/s^2** exactly and **π = 3.14159265358979** exactly. Use these formulas exactly:

```
a_t     = (r1 + r2) / 2
v_circ1 = sqrt(GM / r1)
v_t1    = sqrt(GM * (2 / r1 - 1 / a_t))
dv1     = v_t1 - v_circ1          (positive: the periapsis burn magnitude, in km/s)
T       = 2 * π * sqrt(a_t^3 / GM) (full period of the transfer ellipse, in seconds)
```

Report two quantities:

* `dv1_kms`: the first-burn delta-v in km/s;
* `T_h`: the full transfer-ellipse period converted to hours (**T / 3600**).

Give each value rounded **half-up to exactly 3 decimal places**.

End your response with a final line of exactly this form and nothing after it:

FINAL: dv1_kms=<number to 3 dp> T_h=<number to 3 dp>

Example of the required number format (values are not the answer): `FINAL: dv1_kms=1.234 T_h=5.678`

The final line is the only part graded. Do not include units.
