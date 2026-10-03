# Dough-batch planning

An artisanal bakery has accepted a single order for exactly **137 gift boxes**, and every box must hold exactly 12 cookies.

How the bakery bakes:

1. Cookies bake on trays that hold 24 cookies each.
2. Every baked tray loses exactly 2 cookies to breakage. Broken cookies are discarded and can never be used.
3. The baker first chooses the **smallest whole number of trays** whose unbroken cookies cover the order, and bakes exactly that many trays.
4. Dough is then mixed in whole batches. One dough batch supplies exactly enough dough for 96 cookies, measured against the cookies actually baked in step 3 (broken cookies count here, because their dough was used). The baker mixes the **smallest whole number of batches** whose capacity covers all cookies baked in step 3.
5. One dough batch costs 4.85 credits. One credit is 100 cents.

Report two integers:

- `batches`: the number of dough batches mixed;
- `cost_cents`: the total dough cost as an integer number of cents.

End your response with a final line of exactly this form and nothing after it:

FINAL: batches=<integer> cost_cents=<integer>

The final line is the only part graded. Do not use commas, currency symbols, or units.
