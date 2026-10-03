# Order build-up across three files

This task folder contains a `resources/` directory with three files:

* `parts_catalog.md` — a Markdown table of parts. The columns, in order, are
  `part_code`, `description`, `supplier_code`, `unit_mass_g`,
  `unit_price_cents`, `units_per_case`. The row beginning with `#` and the
  `|---|` separator are not data rows; every data row starts and ends with `|`.
* `suppliers.csv` — CSV whose header row is
  `supplier_code,supplier_name,country,lead_time_days`.
* `orders.csv` — CSV whose header row is
  `order_id,line_no,part_code,uom,quantity`.

Quantity semantics: a line's `uom` is either `unit` or `case`. For a `unit`
line the effective number of units is `quantity`. For a `case` line the
`quantity` is a number of cases and each case holds that part's
`units_per_case` units, so the effective number of units is
`quantity * units_per_case`. All quantities are exact integers and `uom` is
never blank.

Consider order `O-4471` only. Parts appear in the catalog exactly once each.
Suppliers in `orders.csv` are reached through the catalog: a part's supplier is
its `supplier_code`, and that code's `lead_time_days` is in `suppliers.csv`.

Compute four values:

* `total_mass_g` — over order `O-4471`'s lines, the sum of effective units times
  that part's `unit_mass_g` (a bare integer number of grams).
* `total_cost_cents` — over order `O-4471`'s lines, the sum of effective units
  times that part's `unit_price_cents` (a bare integer number of cents).
* `max_lead_time_days` — the largest `lead_time_days` among the distinct
  suppliers that supply the parts appearing in order `O-4471`.
* `heaviest_line_part` — the `part_code` of the line whose total mass
  (effective units times `unit_mass_g`) is greatest. That maximum is unique.

## Deliverable

Write exactly one file named `answer.json` into the output directory
(`$OUT_DIR`). It must contain a single JSON object with exactly these five keys
and no others:

```
{"order_id": "O-4471", "total_mass_g": <integer>, "total_cost_cents": <integer>, "max_lead_time_days": <integer>, "heaviest_line_part": "<string>"}
```

The three numeric values must be JSON integers (not strings, not floats), the
`order_id` value must be the literal string `O-4471`, and `heaviest_line_part`
must be the part code string exactly as it appears in the catalog. Key order
inside the object does not matter. Nothing in your response text is graded;
only the file is.