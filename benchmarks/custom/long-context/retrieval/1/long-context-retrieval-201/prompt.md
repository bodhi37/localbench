# Atlas drift logbook

A station network keeps a single drift logbook. In the logbook below, every
record line has exactly this form:

```
ENTRY <4-digit id> | STATION <name> | drift=<4-decimal value> | bearing=<1-decimal value> | op=<surname>
```

Lines that start with `ATLAS` or `FORMAT` are header lines, not records.

Exactly one record line in the logbook carries the drift value `0.0093`. Find
that record.

## Logbook

```
ATLAS DRIFT LOGBOOK - STATION NETWORK - ONE RECORD PER LINE
FORMAT: ENTRY <4-digit id> | STATION <name> | drift=<4-decimal> | bearing=<1-decimal> | op=<surname>

ENTRY 0001 | STATION HOLLOWAY-9 | drift=0.0380 | bearing=57.1 | op=Iyer
ENTRY 0002 | STATION SABLE-11   | drift=0.0204 | bearing=208.6 | op=Farrow
ENTRY 0003 | STATION MARROW-4   | drift=0.0401 | bearing=53.4 | op=Lindqvist
ENTRY 0004 | STATION SABLE-11   | drift=0.0582 | bearing=44.5 | op=Marchetti
ENTRY 0005 | STATION MARROW-4   | drift=0.0034 | bearing=33.7 | op=Novak
ENTRY 0006 | STATION ORION-7    | drift=0.0248 | bearing=215.8 | op=Farrow
ENTRY 0007 | STATION GARNET-12  | drift=0.0561 | bearing=241.7 | op=Lindqvist
ENTRY 0008 | STATION KESTREL-2  | drift=0.0035 | bearing=205.7 | op=Halvorsen
ENTRY 0009 | STATION WILLOW-5   | drift=0.0565 | bearing=226.6 | op=Petrov
ENTRY 0010 | STATION KESTREL-2  | drift=0.0000 | bearing=239.5 | op=Iyer
ENTRY 0011 | STATION SABLE-11   | drift=0.0405 | bearing=60.4 | op=Petrov
ENTRY 0012 | STATION SABLE-11   | drift=0.0113 | bearing=316.3 | op=Farrow
ENTRY 0013 | STATION SABLE-11   | drift=0.0532 | bearing=234.5 | op=Okafor
ENTRY 0014 | STATION MARROW-4   | drift=0.0440 | bearing=165.3 | op=Lindqvist
ENTRY 0015 | STATION REDFERN-8  | drift=0.0149 | bearing=114.7 | op=Kowalski
ENTRY 0016 | STATION SABLE-11   | drift=0.0404 | bearing=274.4 | op=Okafor
ENTRY 0017 | STATION ORION-7    | drift=0.0160 | bearing=74.8 | op=Dlamini
ENTRY 0018 | STATION PELICAN-6  | drift=0.0579 | bearing=177.1 | op=Iyer
ENTRY 0019 | STATION MARROW-4   | drift=0.0348 | bearing=357.7 | op=Kowalski
ENTRY 0020 | STATION GARNET-12  | drift=0.0332 | bearing=61.7 | op=Halvorsen
ENTRY 0021 | STATION THORNE-3   | drift=0.0092 | bearing=230.3 | op=Okafor
ENTRY 0022 | STATION MARROW-4   | drift=0.0333 | bearing=226.2 | op=Dlamini
ENTRY 0023 | STATION WILLOW-5   | drift=0.0240 | bearing=206.1 | op=Almeida
ENTRY 0024 | STATION ORION-7    | drift=0.0023 | bearing=338.4 | op=Okafor
ENTRY 0025 | STATION ORION-7    | drift=0.0331 | bearing=227.9 | op=Marchetti
ENTRY 0026 | STATION KESTREL-2  | drift=0.0465 | bearing=12.4 | op=Almeida
ENTRY 0027 | STATION GARNET-12  | drift=0.0323 | bearing=51.3 | op=Petrov
ENTRY 0028 | STATION SABLE-11   | drift=0.0257 | bearing=223.8 | op=Lindqvist
ENTRY 0029 | STATION ORION-7    | drift=0.0551 | bearing=186.4 | op=Lindqvist
ENTRY 0030 | STATION WILLOW-5   | drift=0.0418 | bearing=337.6 | op=Iyer
ENTRY 0031 | STATION GARNET-12  | drift=0.0343 | bearing=229.1 | op=Novak
ENTRY 0032 | STATION THORNE-3   | drift=0.0139 | bearing=200.8 | op=Almeida
ENTRY 0033 | STATION SABLE-11   | drift=0.0217 | bearing=202.9 | op=Halvorsen
ENTRY 0034 | STATION MARROW-4   | drift=0.0390 | bearing=148.8 | op=Farrow
ENTRY 0035 | STATION MARROW-4   | drift=0.0020 | bearing=12.9 | op=Kowalski
ENTRY 0036 | STATION MARROW-4   | drift=0.0080 | bearing=274.5 | op=Almeida
ENTRY 0037 | STATION ORION-7    | drift=0.0523 | bearing=269.3 | op=Iyer
ENTRY 0038 | STATION WILLOW-5   | drift=0.0300 | bearing=41.7 | op=Farrow
ENTRY 0039 | STATION ORION-7    | drift=0.0042 | bearing=75.6 | op=Lindqvist
ENTRY 0040 | STATION PELICAN-6  | drift=0.0521 | bearing=52.9 | op=Almeida
ENTRY 0041 | STATION WILLOW-5   | drift=0.0234 | bearing=206.3 | op=Lindqvist
ENTRY 0042 | STATION REDFERN-8  | drift=0.0395 | bearing=201.1 | op=Marchetti
ENTRY 0043 | STATION WILLOW-5   | drift=0.0273 | bearing=206.3 | op=Kowalski
ENTRY 0044 | STATION SABLE-11   | drift=0.0509 | bearing=185.4 | op=Novak
ENTRY 0045 | STATION SABLE-11   | drift=0.0493 | bearing=244.1 | op=Lindqvist
ENTRY 0046 | STATION PELICAN-6  | drift=0.0187 | bearing=54.7 | op=Almeida
ENTRY 0047 | STATION HOLLOWAY-9 | drift=0.0264 | bearing=113.0 | op=Lindqvist
ENTRY 0048 | STATION KESTREL-2  | drift=0.0128 | bearing=260.1 | op=Iyer
ENTRY 0049 | STATION SABLE-11   | drift=0.0150 | bearing=93.1 | op=Bencik
ENTRY 0050 | STATION GARNET-12  | drift=0.0202 | bearing=340.7 | op=Okafor
ENTRY 0051 | STATION SABLE-11   | drift=0.0085 | bearing=0.8 | op=Lindqvist
ENTRY 0052 | STATION GARNET-12  | drift=0.0068 | bearing=266.7 | op=Okafor
ENTRY 0053 | STATION REDFERN-8  | drift=0.0165 | bearing=61.9 | op=Lindqvist
ENTRY 0054 | STATION ORION-7    | drift=0.0522 | bearing=314.3 | op=Okafor
ENTRY 0055 | STATION ORION-7    | drift=0.0285 | bearing=282.4 | op=Kowalski
ENTRY 0056 | STATION ORION-7    | drift=0.0336 | bearing=257.8 | op=Lindqvist
ENTRY 0057 | STATION KESTREL-2  | drift=0.0393 | bearing=349.7 | op=Iyer
ENTRY 0058 | STATION THORNE-3   | drift=0.0088 | bearing=89.2 | op=Lindqvist
ENTRY 0059 | STATION REDFERN-8  | drift=0.0145 | bearing=7.2 | op=Petrov
ENTRY 0060 | STATION KESTREL-2  | drift=0.0452 | bearing=301.7 | op=Okafor
ENTRY 0061 | STATION REDFERN-8  | drift=0.0224 | bearing=343.5 | op=Farrow
ENTRY 0062 | STATION SABLE-11   | drift=0.0599 | bearing=312.3 | op=Halvorsen
ENTRY 0063 | STATION ORION-7    | drift=0.0414 | bearing=348.5 | op=Okafor
ENTRY 0064 | STATION HOLLOWAY-9 | drift=0.0044 | bearing=344.6 | op=Kowalski
ENTRY 0065 | STATION GARNET-12  | drift=0.0277 | bearing=251.9 | op=Farrow
ENTRY 0066 | STATION ORION-7    | drift=0.0030 | bearing=46.1 | op=Bencik
ENTRY 0067 | STATION ORION-7    | drift=0.0156 | bearing=320.7 | op=Okafor
ENTRY 0068 | STATION GARNET-12  | drift=0.0461 | bearing=239.1 | op=Dlamini
ENTRY 0069 | STATION THORNE-3   | drift=0.0236 | bearing=131.1 | op=Petrov
ENTRY 0070 | STATION THORNE-3   | drift=0.0319 | bearing=165.7 | op=Okafor
ENTRY 0071 | STATION THORNE-3   | drift=0.0177 | bearing=236.5 | op=Marchetti
ENTRY 0072 | STATION GARNET-12  | drift=0.0567 | bearing=179.5 | op=Marchetti
ENTRY 0073 | STATION KESTREL-2  | drift=0.0547 | bearing=316.2 | op=Petrov
ENTRY 0074 | STATION ORION-7    | drift=0.0207 | bearing=302.7 | op=Okafor
ENTRY 0075 | STATION KESTREL-2  | drift=0.0106 | bearing=225.0 | op=Almeida
ENTRY 0076 | STATION ORION-7    | drift=0.0159 | bearing=344.9 | op=Marchetti
ENTRY 0077 | STATION PELICAN-6  | drift=0.0250 | bearing=319.6 | op=Petrov
ENTRY 0078 | STATION ORION-7    | drift=0.0402 | bearing=155.9 | op=Dlamini
ENTRY 0079 | STATION KESTREL-2  | drift=0.0417 | bearing=150.3 | op=Kowalski
ENTRY 0080 | STATION THORNE-3   | drift=0.0075 | bearing=35.7 | op=Marchetti
ENTRY 0081 | STATION HOLLOWAY-9 | drift=0.0066 | bearing=83.6 | op=Okafor
ENTRY 0082 | STATION THORNE-3   | drift=0.0449 | bearing=112.4 | op=Petrov
ENTRY 0083 | STATION THORNE-3   | drift=0.0286 | bearing=129.8 | op=Halvorsen
ENTRY 0084 | STATION ORION-7    | drift=0.0543 | bearing=164.1 | op=Farrow
ENTRY 0085 | STATION GARNET-12  | drift=0.0032 | bearing=188.6 | op=Dlamini
ENTRY 0086 | STATION REDFERN-8  | drift=0.0129 | bearing=208.6 | op=Okafor
ENTRY 0087 | STATION PELICAN-6  | drift=0.0136 | bearing=193.5 | op=Novak
ENTRY 0088 | STATION PELICAN-6  | drift=0.0315 | bearing=83.0 | op=Marchetti
ENTRY 0089 | STATION PELICAN-6  | drift=0.0505 | bearing=311.7 | op=Iyer
ENTRY 0090 | STATION GARNET-12  | drift=0.0307 | bearing=246.3 | op=Bencik
ENTRY 0091 | STATION PELICAN-6  | drift=0.0304 | bearing=153.5 | op=Iyer
ENTRY 0092 | STATION KESTREL-2  | drift=0.0262 | bearing=184.8 | op=Iyer
ENTRY 0093 | STATION GARNET-12  | drift=0.0427 | bearing=340.6 | op=Bencik
ENTRY 0094 | STATION THORNE-3   | drift=0.0568 | bearing=218.5 | op=Petrov
ENTRY 0095 | STATION SABLE-11   | drift=0.0324 | bearing=65.4 | op=Petrov
ENTRY 0096 | STATION WILLOW-5   | drift=0.0241 | bearing=355.2 | op=Petrov
ENTRY 0097 | STATION KESTREL-2  | drift=0.0403 | bearing=105.2 | op=Dlamini
ENTRY 0098 | STATION PELICAN-6  | drift=0.0024 | bearing=149.8 | op=Halvorsen
ENTRY 0099 | STATION WILLOW-5   | drift=0.0430 | bearing=125.4 | op=Marchetti
ENTRY 0100 | STATION ORION-7    | drift=0.0345 | bearing=342.9 | op=Lindqvist
ENTRY 0101 | STATION ORION-7    | drift=0.0515 | bearing=284.8 | op=Novak
ENTRY 0102 | STATION THORNE-3   | drift=0.0223 | bearing=96.4 | op=Lindqvist
ENTRY 0103 | STATION PELICAN-6  | drift=0.0419 | bearing=292.2 | op=Halvorsen
ENTRY 0104 | STATION SABLE-11   | drift=0.0061 | bearing=290.4 | op=Okafor
ENTRY 0105 | STATION GARNET-12  | drift=0.0018 | bearing=110.6 | op=Petrov
ENTRY 0106 | STATION REDFERN-8  | drift=0.0366 | bearing=23.7 | op=Okafor
ENTRY 0107 | STATION MARROW-4   | drift=0.0548 | bearing=92.1 | op=Marchetti
ENTRY 0108 | STATION HOLLOWAY-9 | drift=0.0168 | bearing=310.4 | op=Almeida
ENTRY 0109 | STATION MARROW-4   | drift=0.0598 | bearing=324.4 | op=Petrov
ENTRY 0110 | STATION GARNET-12  | drift=0.0415 | bearing=243.0 | op=Dlamini
ENTRY 0111 | STATION WILLOW-5   | drift=0.0512 | bearing=175.1 | op=Novak
ENTRY 0112 | STATION KESTREL-2  | drift=0.0009 | bearing=84.3 | op=Dlamini
ENTRY 0113 | STATION ORION-7    | drift=0.0535 | bearing=86.7 | op=Dlamini
ENTRY 0114 | STATION WILLOW-5   | drift=0.0469 | bearing=332.6 | op=Farrow
ENTRY 0115 | STATION WILLOW-5   | drift=0.0408 | bearing=271.4 | op=Marchetti
ENTRY 0116 | STATION PELICAN-6  | drift=0.0082 | bearing=103.6 | op=Petrov
ENTRY 0117 | STATION REDFERN-8  | drift=0.0368 | bearing=354.3 | op=Okafor
ENTRY 0118 | STATION GARNET-12  | drift=0.0448 | bearing=289.1 | op=Iyer
ENTRY 0119 | STATION SABLE-11   | drift=0.0387 | bearing=91.0 | op=Iyer
ENTRY 0120 | STATION SABLE-11   | drift=0.0374 | bearing=85.5 | op=Marchetti
ENTRY 0121 | STATION THORNE-3   | drift=0.0586 | bearing=47.5 | op=Kowalski
ENTRY 0122 | STATION WILLOW-5   | drift=0.0467 | bearing=222.1 | op=Petrov
ENTRY 0123 | STATION GARNET-12  | drift=0.0394 | bearing=299.6 | op=Halvorsen
ENTRY 0124 | STATION REDFERN-8  | drift=0.0378 | bearing=258.8 | op=Petrov
ENTRY 0125 | STATION WILLOW-5   | drift=0.0163 | bearing=67.2 | op=Dlamini
ENTRY 0126 | STATION REDFERN-8  | drift=0.0151 | bearing=65.0 | op=Kowalski
ENTRY 0127 | STATION ORION-7    | drift=0.0306 | bearing=18.9 | op=Halvorsen
ENTRY 0128 | STATION THORNE-3   | drift=0.0305 | bearing=78.6 | op=Lindqvist
ENTRY 0129 | STATION GARNET-12  | drift=0.0325 | bearing=298.8 | op=Bencik
ENTRY 0130 | STATION ORION-7    | drift=0.0283 | bearing=278.1 | op=Novak
ENTRY 0131 | STATION THORNE-3   | drift=0.0594 | bearing=15.5 | op=Dlamini
ENTRY 0132 | STATION REDFERN-8  | drift=0.0456 | bearing=219.4 | op=Iyer
ENTRY 0133 | STATION THORNE-3   | drift=0.0438 | bearing=173.3 | op=Novak
ENTRY 0134 | STATION ORION-7    | drift=0.0416 | bearing=134.0 | op=Petrov
ENTRY 0135 | STATION THORNE-3   | drift=0.0453 | bearing=312.7 | op=Lindqvist
ENTRY 0136 | STATION THORNE-3   | drift=0.0519 | bearing=338.6 | op=Marchetti
ENTRY 0137 | STATION PELICAN-6  | drift=0.0238 | bearing=59.7 | op=Almeida
ENTRY 0138 | STATION PELICAN-6  | drift=0.0105 | bearing=171.3 | op=Iyer
ENTRY 0139 | STATION REDFERN-8  | drift=0.0191 | bearing=43.8 | op=Iyer
ENTRY 0140 | STATION MARROW-4   | drift=0.0073 | bearing=79.9 | op=Kowalski
ENTRY 0141 | STATION KESTREL-2  | drift=0.0054 | bearing=330.6 | op=Almeida
ENTRY 0142 | STATION REDFERN-8  | drift=0.0431 | bearing=41.2 | op=Petrov
ENTRY 0143 | STATION GARNET-12  | drift=0.0041 | bearing=52.7 | op=Marchetti
ENTRY 0144 | STATION ORION-7    | drift=0.0126 | bearing=203.0 | op=Petrov
ENTRY 0145 | STATION PELICAN-6  | drift=0.0335 | bearing=104.3 | op=Marchetti
ENTRY 0146 | STATION KESTREL-2  | drift=0.0353 | bearing=94.2 | op=Lindqvist
ENTRY 0147 | STATION HOLLOWAY-9 | drift=0.0038 | bearing=93.3 | op=Iyer
ENTRY 0148 | STATION REDFERN-8  | drift=0.0347 | bearing=312.0 | op=Farrow
ENTRY 0149 | STATION HOLLOWAY-9 | drift=0.0210 | bearing=303.4 | op=Kowalski
ENTRY 0150 | STATION WILLOW-5   | drift=0.0047 | bearing=300.8 | op=Petrov
ENTRY 0151 | STATION GARNET-12  | drift=0.0208 | bearing=36.0 | op=Almeida
ENTRY 0152 | STATION HOLLOWAY-9 | drift=0.0479 | bearing=98.3 | op=Marchetti
ENTRY 0153 | STATION REDFERN-8  | drift=0.0471 | bearing=254.7 | op=Iyer
ENTRY 0154 | STATION KESTREL-2  | drift=0.0341 | bearing=96.4 | op=Okafor
ENTRY 0155 | STATION GARNET-12  | drift=0.0026 | bearing=43.3 | op=Okafor
ENTRY 0156 | STATION PELICAN-6  | drift=0.0593 | bearing=196.2 | op=Kowalski
ENTRY 0157 | STATION REDFERN-8  | drift=0.0039 | bearing=264.1 | op=Marchetti
ENTRY 0158 | STATION KESTREL-2  | drift=0.0595 | bearing=317.4 | op=Halvorsen
ENTRY 0159 | STATION WILLOW-5   | drift=0.0249 | bearing=146.5 | op=Almeida
ENTRY 0160 | STATION ORION-7    | drift=0.0186 | bearing=277.6 | op=Kowalski
ENTRY 0161 | STATION PELICAN-6  | drift=0.0553 | bearing=306.0 | op=Petrov
ENTRY 0162 | STATION THORNE-3   | drift=0.0573 | bearing=30.1 | op=Iyer
ENTRY 0163 | STATION SABLE-11   | drift=0.0437 | bearing=227.1 | op=Halvorsen
ENTRY 0164 | STATION GARNET-12  | drift=0.0454 | bearing=278.3 | op=Farrow
ENTRY 0165 | STATION THORNE-3   | drift=0.0083 | bearing=180.4 | op=Petrov
ENTRY 0166 | STATION ORION-7    | drift=0.0101 | bearing=303.8 | op=Marchetti
ENTRY 0167 | STATION THORNE-3   | drift=0.0495 | bearing=1.6 | op=Bencik
ENTRY 0168 | STATION PELICAN-6  | drift=0.0176 | bearing=349.6 | op=Marchetti
ENTRY 0169 | STATION THORNE-3   | drift=0.0121 | bearing=30.8 | op=Halvorsen
ENTRY 0170 | STATION GARNET-12  | drift=0.0592 | bearing=200.1 | op=Halvorsen
ENTRY 0171 | STATION GARNET-12  | drift=0.0350 | bearing=244.5 | op=Iyer
ENTRY 0172 | STATION HOLLOWAY-9 | drift=0.0131 | bearing=5.0 | op=Dlamini
ENTRY 0173 | STATION HOLLOWAY-9 | drift=0.0382 | bearing=253.8 | op=Kowalski
ENTRY 0174 | STATION MARROW-4   | drift=0.0169 | bearing=250.7 | op=Novak
ENTRY 0175 | STATION KESTREL-2  | drift=0.0391 | bearing=96.8 | op=Petrov
ENTRY 0176 | STATION KESTREL-2  | drift=0.0255 | bearing=162.3 | op=Novak
ENTRY 0177 | STATION WILLOW-5   | drift=0.0577 | bearing=6.9 | op=Bencik
ENTRY 0178 | STATION THORNE-3   | drift=0.0218 | bearing=268.0 | op=Farrow
ENTRY 0179 | STATION PELICAN-6  | drift=0.0423 | bearing=50.1 | op=Bencik
ENTRY 0180 | STATION PELICAN-6  | drift=0.0497 | bearing=237.1 | op=Marchetti
ENTRY 0181 | STATION ORION-7    | drift=0.0556 | bearing=160.9 | op=Lindqvist
ENTRY 0182 | STATION ORION-7    | drift=0.0406 | bearing=225.3 | op=Okafor
ENTRY 0183 | STATION MARROW-4   | drift=0.0334 | bearing=306.3 | op=Petrov
ENTRY 0184 | STATION WILLOW-5   | drift=0.0373 | bearing=148.3 | op=Kowalski
ENTRY 0185 | STATION SABLE-11   | drift=0.0425 | bearing=58.2 | op=Halvorsen
ENTRY 0186 | STATION KESTREL-2  | drift=0.0301 | bearing=236.0 | op=Dlamini
ENTRY 0187 | STATION SABLE-11   | drift=0.0019 | bearing=13.4 | op=Bencik
ENTRY 0188 | STATION KESTREL-2  | drift=0.0272 | bearing=138.3 | op=Kowalski
ENTRY 0189 | STATION KESTREL-2  | drift=0.0470 | bearing=29.6 | op=Dlamini
ENTRY 0190 | STATION HOLLOWAY-9 | drift=0.0093 | bearing=326.4 | op=Iyer
ENTRY 0191 | STATION REDFERN-8  | drift=0.0103 | bearing=180.7 | op=Marchetti
ENTRY 0192 | STATION REDFERN-8  | drift=0.0384 | bearing=204.2 | op=Bencik
ENTRY 0193 | STATION PELICAN-6  | drift=0.0158 | bearing=139.9 | op=Petrov
ENTRY 0194 | STATION GARNET-12  | drift=0.0385 | bearing=278.7 | op=Iyer
ENTRY 0195 | STATION MARROW-4   | drift=0.0265 | bearing=219.4 | op=Dlamini
ENTRY 0196 | STATION PELICAN-6  | drift=0.0120 | bearing=0.4 | op=Lindqvist
ENTRY 0197 | STATION WILLOW-5   | drift=0.0357 | bearing=57.8 | op=Lindqvist
ENTRY 0198 | STATION SABLE-11   | drift=0.0464 | bearing=312.2 | op=Kowalski
ENTRY 0199 | STATION ORION-7    | drift=0.0242 | bearing=90.4 | op=Farrow
ENTRY 0200 | STATION WILLOW-5   | drift=0.0094 | bearing=8.8 | op=Okafor
ENTRY 0201 | STATION HOLLOWAY-9 | drift=0.0052 | bearing=310.2 | op=Iyer
ENTRY 0202 | STATION THORNE-3   | drift=0.0529 | bearing=82.2 | op=Okafor
ENTRY 0203 | STATION REDFERN-8  | drift=0.0147 | bearing=109.7 | op=Farrow
ENTRY 0204 | STATION HOLLOWAY-9 | drift=0.0314 | bearing=214.7 | op=Bencik
ENTRY 0205 | STATION REDFERN-8  | drift=0.0084 | bearing=0.6 | op=Marchetti
ENTRY 0206 | STATION GARNET-12  | drift=0.0183 | bearing=337.5 | op=Kowalski
ENTRY 0207 | STATION HOLLOWAY-9 | drift=0.0194 | bearing=329.3 | op=Kowalski
ENTRY 0208 | STATION WILLOW-5   | drift=0.0585 | bearing=63.3 | op=Petrov
ENTRY 0209 | STATION HOLLOWAY-9 | drift=0.0040 | bearing=90.1 | op=Almeida
ENTRY 0210 | STATION ORION-7    | drift=0.0089 | bearing=313.6 | op=Halvorsen
ENTRY 0211 | STATION REDFERN-8  | drift=0.0426 | bearing=231.6 | op=Dlamini
ENTRY 0212 | STATION MARROW-4   | drift=0.0498 | bearing=165.2 | op=Almeida
ENTRY 0213 | STATION GARNET-12  | drift=0.0510 | bearing=333.1 | op=Lindqvist
ENTRY 0214 | STATION KESTREL-2  | drift=0.0188 | bearing=105.3 | op=Novak
ENTRY 0215 | STATION REDFERN-8  | drift=0.0170 | bearing=9.6 | op=Lindqvist
ENTRY 0216 | STATION SABLE-11   | drift=0.0225 | bearing=351.9 | op=Almeida
ENTRY 0217 | STATION KESTREL-2  | drift=0.0481 | bearing=6.2 | op=Okafor
ENTRY 0218 | STATION PELICAN-6  | drift=0.0198 | bearing=224.7 | op=Farrow
ENTRY 0219 | STATION WILLOW-5   | drift=0.0288 | bearing=331.7 | op=Iyer
ENTRY 0220 | STATION HOLLOWAY-9 | drift=0.0445 | bearing=116.0 | op=Marchetti
ENTRY 0221 | STATION PELICAN-6  | drift=0.0377 | bearing=145.1 | op=Almeida
ENTRY 0222 | STATION GARNET-12  | drift=0.0031 | bearing=329.8 | op=Iyer
ENTRY 0223 | STATION PELICAN-6  | drift=0.0339 | bearing=268.6 | op=Kowalski
ENTRY 0224 | STATION SABLE-11   | drift=0.0570 | bearing=90.4 | op=Halvorsen
ENTRY 0225 | STATION REDFERN-8  | drift=0.0379 | bearing=348.7 | op=Iyer
ENTRY 0226 | STATION SABLE-11   | drift=0.0235 | bearing=272.3 | op=Lindqvist
ENTRY 0227 | STATION GARNET-12  | drift=0.0460 | bearing=243.9 | op=Iyer
ENTRY 0228 | STATION MARROW-4   | drift=0.0496 | bearing=44.6 | op=Bencik
ENTRY 0229 | STATION ORION-7    | drift=0.0244 | bearing=151.6 | op=Bencik
ENTRY 0230 | STATION THORNE-3   | drift=0.0189 | bearing=343.2 | op=Marchetti
ENTRY 0231 | STATION WILLOW-5   | drift=0.0503 | bearing=61.6 | op=Iyer
ENTRY 0232 | STATION REDFERN-8  | drift=0.0295 | bearing=283.8 | op=Halvorsen
ENTRY 0233 | STATION ORION-7    | drift=0.0359 | bearing=63.5 | op=Halvorsen
ENTRY 0234 | STATION ORION-7    | drift=0.0457 | bearing=242.3 | op=Dlamini
ENTRY 0235 | STATION GARNET-12  | drift=0.0363 | bearing=294.3 | op=Farrow
ENTRY 0236 | STATION PELICAN-6  | drift=0.0930 | bearing=181.4 | op=Novak
ENTRY 0237 | STATION WILLOW-5   | drift=0.0287 | bearing=69.0 | op=Almeida
ENTRY 0238 | STATION KESTREL-2  | drift=0.0560 | bearing=17.5 | op=Almeida
ENTRY 0239 | STATION GARNET-12  | drift=0.0004 | bearing=277.3 | op=Farrow
ENTRY 0240 | STATION MARROW-4   | drift=0.0289 | bearing=135.3 | op=Lindqvist
```

## Report

End your response with a final line of exactly this form and nothing after it:

FINAL: entry=<integer> bearing=<number> op=<surname>

* `entry` is that record's ENTRY id written as a base-10 integer (leading zeros
  are not significant).
* `bearing` is that record's bearing value exactly as it appears in the logbook.
* `op` is that record's `op` surname exactly as it appears in the logbook.

The final line is the only part graded; anything else in your response is
ignored.
