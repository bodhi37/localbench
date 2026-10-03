# Necklace workshop

A workshop strings necklaces. Every necklace has **12 equally spaced positions** around a circle, every position holds exactly one bead, and beads come in three colours: crimson, teal and ochre.

Each necklace in this job uses exactly 4 crimson beads, 4 teal beads and 4 ochre beads.

Two necklaces count as the **same** necklace when one can be rotated by any whole number of positions to match the other exactly. Reflections are **not** identified: a necklace and its mirror image are different necklaces unless a rotation already matches them.

Report two integers:

* `necklaces`: the number of distinct necklaces that use exactly 4 crimson, 4 teal and 4 ochre beads under the sameness rule above;
* `residue`: `necklaces` modulo 97 (the non-negative remainder, `0 ≤ residue ≤ 96`).

End your response with a final line of exactly this form and nothing after it:

FINAL: necklaces=<integer> residue=<integer>

The final line is the only part graded. Use plain base-10 integers with no commas or units.