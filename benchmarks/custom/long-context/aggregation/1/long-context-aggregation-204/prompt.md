# Supply ledger aggregation

A site keeps a single expense ledger. Every record line has exactly this form:

```
EXP <4-digit id> | CAT <category> | amt=<dollars>.<2 digits> | vendor=<name>
```

Lines that start with `LEDGER` or `FORMAT` are header lines, not records.
Only lines that start with `EXP ` (with a trailing space) are records.

Your task: add up the amounts of the records whose category field is exactly
`SUPPLIES`. The match is exact and case-sensitive on the whole category field:
near-miss names such as `SUPPLIES-OFFICE`, `SUPPLIES-LAB`, `SUPPLY`, and
`SUPPLIES2` must NOT be counted. Amounts are exact dollars and cents.

## Ledger

```
LEDGER SUPPLY EXPENSES - ONE RECORD PER LINE
FORMAT: EXP <4-digit id> | CAT <category> | amt=<dollars>.<2 digits> | vendor=<name>

EXP 0001 | CAT EQUIPMENT | amt=217.93 | vendor=Farlow
EXP 0002 | CAT SOFTWARE | amt=32.92 | vendor=Farlow
EXP 0003 | CAT SUPPLIES | amt=29.55 | vendor=Coda
EXP 0004 | CAT SUPPLIES | amt=58.77 | vendor=Coda
EXP 0005 | CAT SOFTWARE | amt=73.99 | vendor=Ester
EXP 0006 | CAT LODGING | amt=248.66 | vendor=Ivers
EXP 0007 | CAT MEALS | amt=116.82 | vendor=Korin
EXP 0008 | CAT MEALS | amt=85.05 | vendor=Korin
EXP 0009 | CAT SUPPLY | amt=98.84 | vendor=Biren
EXP 0010 | CAT SUPPLIES | amt=209.52 | vendor=Coda
EXP 0011 | CAT LODGING | amt=77.01 | vendor=Korin
EXP 0012 | CAT SUPPLY | amt=10.49 | vendor=Greer
EXP 0013 | CAT EQUIPMENT | amt=186.45 | vendor=Ester
EXP 0014 | CAT POSTAGE | amt=186.71 | vendor=Holst
EXP 0015 | CAT LODGING | amt=78.89 | vendor=Latsis
EXP 0016 | CAT EQUIPMENT | amt=244.34 | vendor=Latsis
EXP 0017 | CAT SUPPLY | amt=17.24 | vendor=Ivers
EXP 0018 | CAT SOFTWARE | amt=138.47 | vendor=Jalen
EXP 0019 | CAT SOFTWARE | amt=63.88 | vendor=Biren
EXP 0020 | CAT TRAVEL | amt=110.47 | vendor=Greer
EXP 0021 | CAT TRAVEL | amt=38.23 | vendor=Greer
EXP 0022 | CAT EQUIPMENT | amt=15.51 | vendor=Farlow
EXP 0023 | CAT SUPPLIES | amt=44.34 | vendor=Biren
EXP 0024 | CAT SUPPLIES | amt=30.84 | vendor=Korin
EXP 0025 | CAT POSTAGE | amt=210.64 | vendor=Ester
EXP 0026 | CAT SUPPLIES | amt=28.79 | vendor=Jalen
EXP 0027 | CAT SOFTWARE | amt=166.62 | vendor=Ivers
EXP 0028 | CAT SUPPLIES | amt=173.60 | vendor=Doran
EXP 0029 | CAT SUPPLIES | amt=34.09 | vendor=Jalen
EXP 0030 | CAT SUPPLY | amt=159.85 | vendor=Coda
EXP 0031 | CAT EQUIPMENT | amt=117.91 | vendor=Acme
EXP 0032 | CAT LODGING | amt=119.34 | vendor=Korin
EXP 0033 | CAT LODGING | amt=190.38 | vendor=Greer
EXP 0034 | CAT SUPPLIES | amt=225.00 | vendor=Coda
EXP 0035 | CAT SUPPLIES | amt=78.76 | vendor=Biren
EXP 0036 | CAT SUPPLIES2 | amt=131.59 | vendor=Latsis
EXP 0037 | CAT LODGING | amt=185.63 | vendor=Korin
EXP 0038 | CAT SOFTWARE | amt=74.83 | vendor=Jalen
EXP 0039 | CAT SUPPLIES | amt=242.32 | vendor=Farlow
EXP 0040 | CAT SUPPLY | amt=245.54 | vendor=Latsis
EXP 0041 | CAT POSTAGE | amt=145.38 | vendor=Greer
EXP 0042 | CAT SOFTWARE | amt=33.65 | vendor=Farlow
EXP 0043 | CAT EQUIPMENT | amt=28.71 | vendor=Farlow
EXP 0044 | CAT SUPPLIES | amt=182.43 | vendor=Jalen
EXP 0045 | CAT SUPPLIES | amt=92.53 | vendor=Ester
EXP 0046 | CAT LODGING | amt=40.41 | vendor=Latsis
EXP 0047 | CAT SUPPLIES | amt=94.46 | vendor=Holst
EXP 0048 | CAT SUPPLIES-LAB | amt=246.22 | vendor=Jalen
EXP 0049 | CAT LODGING | amt=180.05 | vendor=Holst
EXP 0050 | CAT POSTAGE | amt=19.45 | vendor=Jalen
EXP 0051 | CAT POSTAGE | amt=29.17 | vendor=Doran
EXP 0052 | CAT TRAVEL | amt=109.12 | vendor=Biren
EXP 0053 | CAT MEALS | amt=71.23 | vendor=Acme
EXP 0054 | CAT LODGING | amt=61.02 | vendor=Korin
EXP 0055 | CAT EQUIPMENT | amt=11.53 | vendor=Farlow
EXP 0056 | CAT EQUIPMENT | amt=47.84 | vendor=Latsis
EXP 0057 | CAT SUPPLIES2 | amt=10.50 | vendor=Holst
EXP 0058 | CAT LODGING | amt=160.87 | vendor=Acme
EXP 0059 | CAT POSTAGE | amt=28.77 | vendor=Doran
EXP 0060 | CAT MEALS | amt=115.68 | vendor=Ester
EXP 0061 | CAT TRAVEL | amt=231.77 | vendor=Farlow
EXP 0062 | CAT SUPPLY | amt=200.56 | vendor=Jalen
EXP 0063 | CAT LODGING | amt=194.34 | vendor=Coda
EXP 0064 | CAT MEALS | amt=85.26 | vendor=Holst
EXP 0065 | CAT SUPPLIES | amt=31.67 | vendor=Farlow
EXP 0066 | CAT SOFTWARE | amt=165.97 | vendor=Greer
EXP 0067 | CAT TRAVEL | amt=29.39 | vendor=Acme
EXP 0068 | CAT LODGING | amt=246.27 | vendor=Acme
EXP 0069 | CAT SOFTWARE | amt=44.78 | vendor=Farlow
EXP 0070 | CAT MEALS | amt=39.37 | vendor=Greer
EXP 0071 | CAT LODGING | amt=10.28 | vendor=Ester
EXP 0072 | CAT SUPPLIES | amt=164.43 | vendor=Korin
EXP 0073 | CAT SUPPLIES-OFFICE | amt=144.48 | vendor=Ivers
EXP 0074 | CAT TRAVEL | amt=38.69 | vendor=Latsis
EXP 0075 | CAT SUPPLIES | amt=199.06 | vendor=Korin
EXP 0076 | CAT SOFTWARE | amt=32.73 | vendor=Latsis
EXP 0077 | CAT SUPPLIES | amt=180.22 | vendor=Acme
EXP 0078 | CAT SUPPLIES-LAB | amt=227.61 | vendor=Acme
EXP 0079 | CAT SOFTWARE | amt=178.87 | vendor=Acme
EXP 0080 | CAT SOFTWARE | amt=161.73 | vendor=Ester
EXP 0081 | CAT SOFTWARE | amt=21.18 | vendor=Coda
EXP 0082 | CAT SUPPLY | amt=195.97 | vendor=Acme
EXP 0083 | CAT MEALS | amt=206.96 | vendor=Coda
EXP 0084 | CAT POSTAGE | amt=216.44 | vendor=Biren
EXP 0085 | CAT SUPPLIES | amt=205.38 | vendor=Holst
EXP 0086 | CAT EQUIPMENT | amt=62.51 | vendor=Farlow
EXP 0087 | CAT POSTAGE | amt=37.50 | vendor=Greer
EXP 0088 | CAT SUPPLIES | amt=200.42 | vendor=Biren
EXP 0089 | CAT SOFTWARE | amt=14.62 | vendor=Biren
EXP 0090 | CAT SUPPLIES | amt=24.45 | vendor=Farlow
EXP 0091 | CAT SUPPLIES | amt=140.58 | vendor=Ester
EXP 0092 | CAT SUPPLIES | amt=123.33 | vendor=Jalen
EXP 0093 | CAT SOFTWARE | amt=138.34 | vendor=Acme
EXP 0094 | CAT SUPPLIES2 | amt=243.19 | vendor=Doran
EXP 0095 | CAT TRAVEL | amt=233.50 | vendor=Coda
EXP 0096 | CAT SUPPLIES-OFFICE | amt=140.13 | vendor=Farlow
EXP 0097 | CAT SUPPLIES-LAB | amt=35.68 | vendor=Ester
EXP 0098 | CAT SUPPLIES | amt=142.98 | vendor=Korin
EXP 0099 | CAT MEALS | amt=113.26 | vendor=Latsis
EXP 0100 | CAT SUPPLIES-OFFICE | amt=49.66 | vendor=Greer
EXP 0101 | CAT EQUIPMENT | amt=117.20 | vendor=Korin
EXP 0102 | CAT SUPPLIES | amt=174.90 | vendor=Acme
EXP 0103 | CAT MEALS | amt=6.79 | vendor=Coda
EXP 0104 | CAT SUPPLIES | amt=20.32 | vendor=Holst
EXP 0105 | CAT SUPPLIES | amt=82.13 | vendor=Doran
EXP 0106 | CAT SUPPLIES | amt=215.95 | vendor=Greer
EXP 0107 | CAT SUPPLIES-LAB | amt=144.99 | vendor=Holst
EXP 0108 | CAT SOFTWARE | amt=198.94 | vendor=Jalen
EXP 0109 | CAT SUPPLIES | amt=23.73 | vendor=Doran
EXP 0110 | CAT EQUIPMENT | amt=124.14 | vendor=Holst
EXP 0111 | CAT SUPPLIES | amt=84.31 | vendor=Acme
EXP 0112 | CAT SUPPLIES-LAB | amt=116.47 | vendor=Biren
EXP 0113 | CAT SUPPLIES | amt=25.11 | vendor=Ivers
EXP 0114 | CAT MEALS | amt=209.00 | vendor=Korin
EXP 0115 | CAT LODGING | amt=131.82 | vendor=Coda
EXP 0116 | CAT MEALS | amt=210.57 | vendor=Coda
EXP 0117 | CAT SUPPLIES2 | amt=31.64 | vendor=Ivers
EXP 0118 | CAT MEALS | amt=119.49 | vendor=Farlow
EXP 0119 | CAT EQUIPMENT | amt=122.26 | vendor=Greer
EXP 0120 | CAT SUPPLIES | amt=7.07 | vendor=Latsis
```

## Report

End your response with a final line of exactly this form and nothing after it:

FINAL: total_cents=<integer> count=<integer>

* `total_cents` is the exact sum of the counted records in cents
  (dollars times 100 plus cents). Leading zeros are not significant.
* `count` is how many records were summed, as a base-10 integer (leading zeros
  are not significant).
* Only the exact category `SUPPLIES` counts; the near-miss categories listed
  above never count.

The final line is the only part graded; anything else in your response is
ignored.
