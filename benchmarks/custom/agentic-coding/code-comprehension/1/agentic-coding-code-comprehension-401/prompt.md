# Bucket-summary trace

This task folder contains `resources/normalize.py`. It is executed as-is, with no edits, from a directory where it is importable.

Answer two questions about that file:

1. `stdout` — the exact single line the program prints when it is executed.
2. `fix_line` — the 1-based line number (counting from 1 at the first line of the file) of the **single statement** that would have to change for the bucketing to use true floor division, so that negative values fall into the mathematically correct lower bucket. Nothing else in the file needs to change.

Report `stdout` exactly as printed, character for character, with no surrounding quotes and no spaces added.

End your response with a final line of exactly this form and nothing after it:

FINAL: stdout=<printed line> fix_line=<integer>

Only that final line is graded.