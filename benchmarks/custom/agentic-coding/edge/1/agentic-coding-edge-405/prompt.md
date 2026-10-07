# CSV edge cases: fix the parser

This task folder contains `resources/csvparse.py`. It is a naive CSV parser
used by an ingest pipeline, and it mishandles several edge cases described
below.

Deliver a corrected copy of the whole module as `$OUT_DIR/csvparse.py` with
exactly this public function (keep the name, signature, and docstring):

* `parse_csv(text)` — `text` is a CSV document as a single string. Return a
  list of rows, where each row is a list of field strings, following these
  rules exactly:
  1. An empty string returns `[]`.
  2. `\r\n` line endings are treated exactly like `\n`. (A lone `\r` is
     ordinary data, not a line break.)
  3. A single trailing newline does **not** add an extra row: `"a,b\n"`
     parses to `[["a", "b"]]`. But `"a\n\n"` parses to `[["a"], [""]]`,
     and `"\n"` parses to `[[""]]`.
  4. Fields are separated by commas. A field may be wrapped in double quotes;
     a quoted field may contain commas and newlines literally.
  5. Inside a quoted field, two consecutive quotes `""` mean one literal
     `"` character.
  6. After a closing quote, only a comma, a newline, or the end of input may
     follow — anything else is a `ValueError`.
  7. An unterminated quoted field is a `ValueError`.
  8. Whitespace is significant and must be preserved: `" a ,b "` parses to
     `[[" a ", "b "]]` — never strip fields or lines.

  You must parse by hand: the `csv` module must not be used.

The module must import cleanly **without printing anything and without running
anything at import time** (keep the module-level code to definitions only).
The module must not use third-party imports.

Your file will be imported and `parse_csv` called with fixed test vectors,
including the empty document, trailing newlines, `\r\n` endings, empty
fields, quoted commas, escaped quotes, empty quoted fields, significant
spaces, quoted embedded newlines, blank middle lines, and malformed inputs
that must raise `ValueError`. Any behaviour that differs from the
specification above fails.
