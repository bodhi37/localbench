# Policy contradiction hunt

A site keeps a single policy register. Every record line has exactly this form:

```
POL <4-digit id> | AREA <area> | MAX <integer> GB per account | note=<word>
```

Lines that start with `REGISTER` or `FORMAT` are header lines, not records.
Only lines that start with `POL ` (with a trailing space) are records.

Each storage area should have exactly one limit: all records naming the same
area should carry the same `MAX` value. Exactly one unordered pair of records
in the register contradicts this rule: the two records name the same area but
carry different `MAX` values. Every other pair of records that name the same
area agrees. Find that contradicting pair.

Beware near-miss area names (for example `VAULT-1`, `VAULT-70`, and `VAULT7`
are three different areas, and none of them is `VAULT-7`): the area match is
exact and case-sensitive on the whole area field.

## Register

```
REGISTER STORAGE POLICY - ONE RECORD PER LINE
FORMAT: POL <4-digit id> | AREA <area> | MAX <integer> GB per account | note=<word>

POL 0001 | AREA GROVE-18 | MAX 10 GB per account | note=grove
POL 0002 | AREA ROAD-33 | MAX 150 GB per account | note=lumen
POL 0003 | AREA CHEST-8 | MAX 200 GB per account | note=inlet
POL 0004 | AREA DEPOT-14 | MAX 200 GB per account | note=alpha
POL 0005 | AREA VAULT-70 | MAX 60 GB per account | note=bravo
POL 0006 | AREA SHELF-11 | MAX 10 GB per account | note=alpha
POL 0007 | AREA LANE-26 | MAX 100 GB per account | note=flint
POL 0008 | AREA MEADOW-2 | MAX 120 GB per account | note=flint
POL 0009 | AREA GROVE-18 | MAX 10 GB per account | note=drift
POL 0010 | AREA CRATE-9 | MAX 20 GB per account | note=grove
POL 0011 | AREA LOCKER-5 | MAX 15 GB per account | note=ember
POL 0012 | AREA CLOSE-7 | MAX 120 GB per account | note=cinder
POL 0013 | AREA DOCK-2 | MAX 60 GB per account | note=lumen
POL 0014 | AREA STALL-3 | MAX 20 GB per account | note=flint
POL 0015 | AREA BOX-19 | MAX 120 GB per account | note=bravo
POL 0016 | AREA ORCHARD-6 | MAX 80 GB per account | note=grove
POL 0017 | AREA VAULT-1 | MAX 50 GB per account | note=juniper
POL 0018 | AREA DEPOT-14 | MAX 200 GB per account | note=inlet
POL 0019 | AREA VAULT7 | MAX 15 GB per account | note=flint
POL 0020 | AREA COURT-15 | MAX 100 GB per account | note=bravo
POL 0021 | AREA CROFT-12 | MAX 30 GB per account | note=bravo
POL 0022 | AREA ALLEY-5 | MAX 25 GB per account | note=cinder
POL 0023 | AREA PADDOCK-9 | MAX 150 GB per account | note=juniper
POL 0024 | AREA BIN-6 | MAX 150 GB per account | note=lumen
POL 0025 | AREA CELL-2 | MAX 200 GB per account | note=juniper
POL 0026 | AREA HOLD-21 | MAX 20 GB per account | note=ember
POL 0027 | AREA SACK-22 | MAX 20 GB per account | note=alpha
POL 0028 | AREA ALLEY-5 | MAX 25 GB per account | note=ember
POL 0029 | AREA PLOT-31 | MAX 15 GB per account | note=juniper
POL 0030 | AREA ARCHIVE-3 | MAX 30 GB per account | note=juniper
POL 0031 | AREA BAY-30 | MAX 30 GB per account | note=lumen
POL 0032 | AREA ROOM-41 | MAX 60 GB per account | note=harbor
POL 0033 | AREA PEN-16 | MAX 15 GB per account | note=harbor
POL 0034 | AREA YARD-10 | MAX 100 GB per account | note=ember
POL 0035 | AREA SACK-22 | MAX 20 GB per account | note=grove
POL 0036 | AREA TRUNK-1 | MAX 120 GB per account | note=flint
POL 0037 | AREA BIN-6 | MAX 150 GB per account | note=flint
POL 0038 | AREA FIELD-24 | MAX 50 GB per account | note=bravo
POL 0039 | AREA PLOT-31 | MAX 15 GB per account | note=harbor
POL 0040 | AREA AISLE-23 | MAX 120 GB per account | note=cinder
POL 0041 | AREA LANE-26 | MAX 100 GB per account | note=lumen
POL 0042 | AREA CELL-2 | MAX 200 GB per account | note=juniper
POL 0043 | AREA POD-9 | MAX 50 GB per account | note=lumen
POL 0044 | AREA CHEST-8 | MAX 200 GB per account | note=bravo
POL 0045 | AREA CACHE-12 | MAX 80 GB per account | note=juniper
POL 0046 | AREA STREET-8 | MAX 30 GB per account | note=flint
POL 0047 | AREA ROOM-41 | MAX 60 GB per account | note=lumen
POL 0048 | AREA STACK-17 | MAX 100 GB per account | note=alpha
POL 0049 | AREA CROFT-12 | MAX 30 GB per account | note=flint
POL 0050 | AREA MEADOW-2 | MAX 120 GB per account | note=inlet
POL 0051 | AREA DOCK-2 | MAX 60 GB per account | note=inlet
POL 0052 | AREA TERRACE-20 | MAX 25 GB per account | note=lumen
POL 0053 | AREA PEN-16 | MAX 15 GB per account | note=harbor
POL 0054 | AREA BOX-19 | MAX 120 GB per account | note=drift
POL 0055 | AREA BOULEVARD-2 | MAX 150 GB per account | note=cinder
POL 0056 | AREA CABINET-6 | MAX 60 GB per account | note=inlet
POL 0057 | AREA VAULT7 | MAX 15 GB per account | note=alpha
POL 0058 | AREA CLOSE-7 | MAX 120 GB per account | note=drift
POL 0059 | AREA YARD-10 | MAX 100 GB per account | note=flint
POL 0060 | AREA GATE-4 | MAX 10 GB per account | note=cinder
POL 0061 | AREA GARTH-4 | MAX 120 GB per account | note=bravo
POL 0062 | AREA VAULT-7 | MAX 90 GB per account | note=cinder
POL 0063 | AREA BAY-30 | MAX 30 GB per account | note=bravo
POL 0064 | AREA COURT-15 | MAX 100 GB per account | note=grove
POL 0065 | AREA CASE-7 | MAX 150 GB per account | note=kelp
POL 0066 | AREA CRIB-5 | MAX 20 GB per account | note=bravo
POL 0067 | AREA CRIB-5 | MAX 20 GB per account | note=harbor
POL 0068 | AREA RACK-13 | MAX 80 GB per account | note=alpha
POL 0069 | AREA TERRACE-20 | MAX 25 GB per account | note=bravo
POL 0070 | AREA CABINET-6 | MAX 60 GB per account | note=lumen
POL 0071 | AREA DRAWER-4 | MAX 30 GB per account | note=bravo
POL 0072 | AREA CRATE-9 | MAX 20 GB per account | note=inlet
POL 0073 | AREA GARTH-4 | MAX 120 GB per account | note=bravo
POL 0074 | AREA SHELF-11 | MAX 10 GB per account | note=bravo
POL 0075 | AREA STREET-8 | MAX 30 GB per account | note=harbor
POL 0076 | AREA ORCHARD-6 | MAX 80 GB per account | note=bravo
POL 0077 | AREA RACK-13 | MAX 80 GB per account | note=lumen
POL 0078 | AREA STALL-3 | MAX 20 GB per account | note=drift
POL 0079 | AREA GATE-4 | MAX 10 GB per account | note=juniper
POL 0080 | AREA STORE-8 | MAX 120 GB per account | note=ember
POL 0081 | AREA AVENUE-11 | MAX 60 GB per account | note=flint
POL 0082 | AREA STACK-17 | MAX 100 GB per account | note=alpha
POL 0083 | AREA AVENUE-11 | MAX 60 GB per account | note=juniper
POL 0084 | AREA LOCKER-5 | MAX 15 GB per account | note=bravo
POL 0085 | AREA PADDOCK-9 | MAX 150 GB per account | note=alpha
POL 0086 | AREA ROAD-33 | MAX 150 GB per account | note=bravo
POL 0087 | AREA STORE-8 | MAX 120 GB per account | note=grove
POL 0088 | AREA POD-9 | MAX 50 GB per account | note=ember
POL 0089 | AREA TRUNK-1 | MAX 120 GB per account | note=grove
POL 0090 | AREA VAULT-1 | MAX 50 GB per account | note=cinder
POL 0091 | AREA BOULEVARD-2 | MAX 150 GB per account | note=ember
POL 0092 | AREA VAULT-7 | MAX 40 GB per account | note=cinder
POL 0093 | AREA ARCHIVE-3 | MAX 30 GB per account | note=ember
POL 0094 | AREA CACHE-12 | MAX 80 GB per account | note=ember
POL 0095 | AREA AISLE-23 | MAX 120 GB per account | note=grove
POL 0096 | AREA DRAWER-4 | MAX 30 GB per account | note=ember
POL 0097 | AREA VAULT-70 | MAX 60 GB per account | note=kelp
POL 0098 | AREA FIELD-24 | MAX 50 GB per account | note=ember
POL 0099 | AREA CASE-7 | MAX 150 GB per account | note=harbor
POL 0100 | AREA HOLD-21 | MAX 20 GB per account | note=kelp
```

## Report

End your response with a final line of exactly this form and nothing after it:

FINAL: area=<AREA> pol_a=<integer> pol_b=<integer>

* `area` is the shared area name exactly as it appears in the register
  (case-sensitive, no extra characters).
* `pol_a` and `pol_b` are the two POL ids as base-10 integers with
  `pol_a` < `pol_b` numerically (leading zeros are not significant).

The final line is the only part graded; anything else in your response is
ignored.
