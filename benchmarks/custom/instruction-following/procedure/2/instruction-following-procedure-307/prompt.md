# Register procedure with conditional branches

A controller holds two integer registers, `A` and `B`.

Initial state: `A` = 4, `B` = 7.

Execute Steps 1–8 in order, exactly as written. Each step reads the current
register values left by the previous step:

* Step 1: `A` = `A` + 10.
* Step 2: `B` = `B` × 2.
* Step 3: If `A` >= `B` then `A` = `A` + 5, otherwise `B` = `B` + 5.
* Step 4: `B` = `B` + `A`.
* Step 5: If `B` > 30 then `A` = `A` × 2, otherwise `A` = `A` + 1.
* Step 6: `B` = `B` − 6.
* Step 7: If `A` is even (divisible by 2) then `B` = `B` + 2,
  otherwise `B` = `B` + 3.
* Step 8: `B` = `B` + 1.

Then derive `CHECK`: the sum of the decimal digits of (`A` + `B`), reduced
modulo 256, written as exactly 2 capital hexadecimal digits (`00`–`FF`,
zero-padded).

`STEPS` is the number of steps executed (8).

Report the final register values.

End your response with a final line of exactly this form and nothing after it:

FINAL: A=<integer> B=<integer> STEPS=8 CHECK=<2 hex digits>

Use base-10 integers for `A` and `B` and exactly 2 capital hex digits for
`CHECK`. You may write reasoning before the final line. Only the final line is
graded, but the verifier re-executes the procedure, so any skipped step or
mis-taken branch fails.
