# Trihybrid cross: genotype and phenotype expectations

In a plant, three autosomal loci **A/a**, **B/b**, **C/c** assort independently (no linkage, Mendelian segregation, no selection, no mutation). Two plants both of genotype **Aa Bb Cc** are crossed (Aa Bb Cc × Aa Bb Cc).

For a single offspring, use the per-locus probabilities from this cross:

* P(AA) = 1/4, P(Aa) = 1/2, P(aa) = 1/4 (and likewise for B/b and C/c);
* dominant phenotype at one locus (e.g. A_): 3/4.

Because the loci are independent, joint probabilities are products of per-locus probabilities.

Compute:

* `p1`: the probability that an offspring has the exact genotype **AA Bb cc** (homozygous dominant at locus 1, heterozygous at locus 2, homozygous recessive at locus 3). Report as an exact fraction in lowest terms (e.g. 1/8).
* `n1`: the expected number of offspring with genotype AA Bb cc among **3200** offspring (3200 × p1). This is an exact integer.
* `p2`: the probability that an offspring shows the dominant phenotype at **all three** loci (A_ B_ C_). Report as an exact fraction in lowest terms.
* `n2`: the expected number of such offspring among **3200** offspring (3200 × p2). This is an exact integer.

Fractions must be in lowest terms with a single `/` and no spaces (e.g. `27/64`). Integers have no decimal point and no thousands separators.

End your response with a final line of exactly this form and nothing after it:

FINAL: p1=<fraction> n1=<integer> p2=<fraction> n2=<integer>

Example of the required format (values are not the answer): `FINAL: p1=1/8 n1=400 p2=9/16 n2=1800`

The final line is the only part graded.
