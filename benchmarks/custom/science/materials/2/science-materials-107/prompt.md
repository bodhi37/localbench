# Loaded rod: stress plus thermal expansion

A straight cylindrical steel rod has initial length **L0 = 2.500 m** and diameter **d = 12.00 mm** at the reference temperature. It is subjected simultaneously to:

* a static axial tensile load of **F = 25.0 kN** (uniform uniaxial stress, small strains); and
* a uniform temperature increase of **ΔT = +35.0 K**.

Use these constants exactly:

* Young's modulus: **E = 200 GPa** (use 200 × 10^9 Pa);
* linear thermal-expansion coefficient: **α = 12.0 × 10^-6 /K**;
* **π = 3.14159265358979** for the cross-sectional area **A = π (d/2)^2**.

Assume the mechanical and thermal elongations add linearly (small-strain superposition), end effects are negligible, and the modulus and expansion coefficient are constant over this range.

Report two quantities:

* `sigma_MPa`: the engineering axial stress **F / A** (using the original cross-section), in MPa;
* `dL_total_mm`: the total change in length **ΔL_mech + ΔL_th**, in mm, where **ΔL_mech = (F / A) × L0 / E** and **ΔL_th = α × L0 × ΔT**.

Give each value rounded **half-up to exactly 3 decimal places**.

End your response with a final line of exactly this form and nothing after it:

FINAL: sigma_MPa=<number to 3 dp> dL_total_mm=<number to 3 dp>

Example of the required number format (values are not the answer): `FINAL: sigma_MPa=100.000 dL_total_mm=1.234`

The final line is the only part graded. Do not include units.
