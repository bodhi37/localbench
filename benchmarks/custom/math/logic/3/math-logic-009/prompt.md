# Vault of Tormsund

On the island of Tormsund each inhabitant is either a knight (always tells the
truth) or a knave (always utters a false statement). A vault holds a code number
`N` with `10 <= N <= 20`. Four inhabitants make the following statements:

- Aldo says: "Bana is a knave AND `N` is even."
- Bana says: "Ciro is a knave OR `N` is greater than 14."
- Ciro says: "Dara is a knight AND `N` is prime."
- Dara says: "`N` equals 16."

Additional facts that close off shortcuts:

- Exactly two of the four inhabitants are knights. Any assignment of types with
  zero, one, three, or four knights is wrong, even if every statement's
  truth value matches the speaker's type.
- A knave's whole statement is false. For Aldo's AND-statement, one false half
  suffices to make it false; for Bana's OR-statement (inclusive or: true when
  either half or both halves hold), both halves must be false to make it false.
  A compound statement that is half-true still counts as a false utterance by a
  knave and a failed utterance by a knight.
- There is exactly one pair (type assignment, `N`) consistent with all four
  utterances and the exactly-two-knights count. You must find it: case-split on
  Dara's type, propagate parity (`N = 16` is even), primality (`16` is not prime:
  `16 = 2 x 8`), and the comparison `16 > 14` (true).
- The vault combination `code` is defined as `100 x K + N`, where `K` is the
  number of knights (so `K = 2` for the true assignment) and `N` is the vault
  number. Report only this single integer.

End your response with a final line of exactly this form and nothing after it:

FINAL: code=<integer>

The final line is the only part graded. Do not report `N` or `K` separately.
