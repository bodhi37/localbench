# Beacon alignment

Three independent navigation beacons begin repeating cycles at the same instant `t = 0`, where `t` is whole seconds elapsed since that instant.

* Beacon ALPHA emits a pulse at every instant `t` with `t ≡ 3 (mod 7)`.
* Beacon BRAVO emits a pulse at every instant `t` with `t ≡ 5 (mod 11)`.
* Beacon CHARLIE emits a pulse at every instant `t` with `t ≡ 9 (mod 13)`.

Each pulse is instantaneous and a beacon that is due at an instant does emit then. All three beacons are silent at `t = 0`.

Report two integers:

* `first`: the smallest positive integer `t` at which all three beacons pulse simultaneously;
* `count`: the number of positive integer instants `t` with `1 ≤ t ≤ 500000` at which all three pulse simultaneously.

End your response with a final line of exactly this form and nothing after it:

FINAL: first=<integer> count=<integer>

The final line is the only part graded. Use plain base-10 integers with no commas, signs, or units.