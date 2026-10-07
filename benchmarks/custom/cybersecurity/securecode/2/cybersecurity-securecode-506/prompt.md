# Fix three defects in vuln.py (static secure-code task)

The shipped file `resources/vuln.py` contains THREE defects. Do NOT scan any
network or run anything against a live host; edit code only.

1. **SQL injection** in `lookup_user`: the query is built with string
   concatenation. Fix with a parameterized query (`?` placeholder + parameter
   tuple). Keep the function name, signature, and return type.
2. **Shell injection** in `run_backup`: the command is a formatted string run
   with `shell=True`. Fix by passing an argument LIST to `subprocess.run`
   with `shell=False` so `host` stays a single argument.
3. **Weak randomness** in `gen_token`: uses the `random` module. Fix by using
   the `secrets` module (`secrets.token_hex(16)`, i.e. 32 hex chars).

## Deliverable

Write the corrected module to `$OUT_DIR/fixed.py` (same three function names
and signatures, import-safe: only imports plus function defs). Then emit as
the LAST non-empty line of your response:

```
FINAL: fixed_file=fixed.py
```

Grading replays functional vectors against `$OUT_DIR/fixed.py` (injection
string blocked, malicious host kept as one argv element, tokens unique hex)
plus static bans on `shell=True`, the `random` module, and string-built SQL.
