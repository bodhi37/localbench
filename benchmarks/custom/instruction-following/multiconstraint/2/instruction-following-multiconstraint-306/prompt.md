# Five-job schedule at minimum makespan

A depot must schedule five jobs, `J1` through `J5`, into five slots, `S1`
through `S5`. Each job takes exactly one slot, and each slot gets exactly one
job.

The energy cost of putting a given job in a given slot:

| job | S1 | S2 | S3 | S4 | S5 |
|---|---|---|---|---|---|
| J1 | 9 | — | 12 | 7 | 14 |
| J2 | 8 | 11 | — | 10 | 13 |
| J3 | 12 | 9 | 8 | 13 | 11 |
| J4 | — | 13 | 10 | 12 | 9 |
| J5 | 11 | 10 | 14 | 9 | — |

A dash means that job cannot use that slot at all (its time window is closed).

Two further restrictions:

* `J3` must use an even-numbered slot (`S2` or `S4`).
* `J1` and `J4` share one fixture and may not both be scheduled late: it is
  forbidden that `J1` is in {`S4`, `S5`} at the same time as `J4` is in
  {`S4`, `S5`}. At least one of the two must be in `S1`–`S3`.

Among all schedules that satisfy every rule above, the one with the **smallest
makespan** is unique. The makespan of a schedule is the sum of its five listed
costs.

Report that unique minimum-makespan schedule.

End your response with a final line of exactly this form and nothing after it:

FINAL: J1=<slot> J2=<slot> J3=<slot> J4=<slot> J5=<slot> makespan=<integer>

Use the job labels exactly as above in `J1`–`J5` order, the slot labels exactly
as above, single spaces between fields, and the makespan as a base-10 integer.
You may write reasoning before the final line. Only the final line is graded,
but it must satisfy every rule and carry the true minimum makespan.
