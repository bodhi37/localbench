# Crew-to-shift assignment at minimum cost

A yard must cover six shifts, `S1` through `S6`, each with exactly one worker. There are exactly six workers: `ADA`, `BO`, `CAI`, `DEE`, `EMU`, `FAY`. Every worker takes exactly one shift, and every shift gets exactly one worker.

The cost, in credits, of putting a given worker on a given shift:

| worker | S1 | S2 | S3 | S4 | S5 | S6 |
|---|---|---|---|---|---|---|
| ADA | 14 | 11 | — | 9 | 18 | 12 |
| BO | 12 | 17 | 13 | 16 | — | 10 |
| CAI | 19 | 14 | 12 | 15 | 13 | — |
| DEE | 11 | — | 17 | 12 | 16 | 15 |
| EMU | 16 | 13 | 18 | — | 11 | 14 |
| FAY | 13 | 15 | 11 | 18 | 17 | — |

A dash means that worker cannot take that shift at all.

One further restriction: `DEE` must work an even-numbered shift (`S2`, `S4` or `S6`).

Among all assignments that satisfy every rule above, the one with the **smallest total cost** is unique. The total cost of an assignment is the sum of its six listed costs. (There is no cost for the one forbidden pairing; forbidden pairings are simply not allowed.)

Report that unique minimum-cost assignment.

End your response with a final line of exactly this form and nothing after it:

FINAL: S1=<worker> S2=<worker> S3=<worker> S4=<worker> S5=<worker> S6=<worker> total=<integer>

Use the worker names exactly as spelled above (capital letters), the shift labels exactly as above, and the total as a base-10 integer. The final line is the only part graded.