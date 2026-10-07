# Rover sample manifest

A sample-return rover can carry at most 20 kg. Six candidate instruments each
exist once (take it or leave it; no fractions, no repeats):

| item | mass (kg) | science value |
|------|-----------|---------------|
| A | 7 | 21 |
| B | 6 | 18 |
| C | 5 | 14 |
| D | 4 | 10 |
| E | 3 | 7 |
| F | 9 | 25 |

Choose a subset with total mass at most 20 kg maximizing total science value.
The optimum is unique: exactly one feasible subset attains the maximum value.

Rules that close off shortcuts:

- Each item is 0/1: taken at most once. Taking the same high-ratio item twice
  (for example "A twice") is forbidden.
- Greedy by value-per-mass is not optimal here: the two highest-ratio items
  (A and B, both 3.0/kg) do not both belong to the optimal manifest, and the
  manifest of the three greedily top-ranked feasible picks is beaten by the true
  optimum. You must compare complete feasible subsets, not stop at ratios.
- A manifest that is merely full (mass exactly 20) is not automatically optimal;
  two different full manifests score below the optimum.
- List the chosen items in alphabetical order, comma-separated with no spaces
  (for example `chosen=A,D,F`), and the integer total value.

End your response with a final line of exactly this form and nothing after it:

FINAL: chosen=<letters> total=<integer>

The final line is the only part graded. Only the letters A-F (each at most once,
alphabetical, comma-separated, no spaces) and one integer are accepted.
