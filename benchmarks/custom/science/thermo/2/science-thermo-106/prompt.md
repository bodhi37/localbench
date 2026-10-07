# Calorimetry with a phase change

An insulated (adiabatic) calorimeter contains **40.00 g** of ice initially at **-12.0 °C**. **250.00 g** of liquid water initially at **70.0 °C** is added. The system equilibrates at atmospheric pressure with no heat exchange with the surroundings and no evaporation.

Use these constants exactly:

* specific heat of liquid water: **c_w = 4.186 J/(g·°C)**
* specific heat of ice: **c_i = 2.090 J/(g·°C)**
* latent heat of fusion of ice (at 0.0 °C): **L_f = 334.0 J/g**

The equilibrium state is a single liquid phase with **0.0 °C < T_eq < 70.0 °C** (all of the ice melts; nothing boils). Energy conservation gives:

```
m_w * c_w * (T_w - T_eq) = m_i * c_i * (0.0 - T_i) + m_i * L_f + m_i * c_w * (T_eq - 0.0)
```

where m_w = 250.00 g, T_w = 70.0 °C, m_i = 40.00 g, T_i = -12.0 °C.

Report two quantities:

* `T_eq`: the equilibrium temperature in °C;
* `q_hot`: the heat lost by the initially hot water, in kJ, i.e. `m_w * c_w * (T_w - T_eq) / 1000`.

Give each value rounded **half-up to exactly 3 decimal places**.

End your response with a final line of exactly this form and nothing after it:

FINAL: T_eq=<number to 3 dp> q_hot=<number to 3 dp>

Example of the required number format (values are not the answer): `FINAL: T_eq=12.345 q_hot=6.789`

The final line is the only part graded. Do not include units.
