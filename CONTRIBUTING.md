# Contributing

## Adding a custom task

Create `benchmarks/custom/<domain>/<capability>/<tier>/<task-id>/` with:

- `prompt.md` — everything the model sees
- `verify.py` — accepts `--task-dir/--out-dir/--response`, prints a JSON
  line `{"pass": bool, "detail": str}`, exits 0/1
- `meta.json` — `id`, `domain`, `capability`, `tier`, `runs`,
  `expected_duration`, plus `notes` on what the task isolates and how false
  positives were audited
- `teardown.sh` — kept out of the model's view; see below
- `SOLUTION.md` — **never commit** (gitignored, withheld)

`id` must match `^[A-Za-z0-9_.-]+$` — it becomes a `results/` path
component. `prompt.md` + `resources/` are the only entries mounted into the
sandbox; `verify.py`, `teardown.sh`, `meta.json`, `tests/`, `SOLUTION.md`
and any future file are invisible there by construction.

## Review notes (teardown is code execution)

`teardown.sh` runs as the operator user after each unit (network-unshared
via bwrap, scrubbed env, 60s timeout, symlink refused) so it can stop a
loopback task service and remove `__pycache__`. It is trusted code in an
untrusted context:

- keep it to `pkill -f "[x]... --port"` + `find ... -name __pycache__ -delete`;
  no curl/wget, no broad `pkill`, no writes outside the task dir;
- the harness skips symlink teardowns and scrubs the environment — do not
  work around either;
- reviewers: a task PR that changes `teardown.sh`, `verify.py` or
  `resources/` symlinks is a code-execution PR. Check patterns, paths and
  symlink targets before merging.

## Verifiers

- Pure function of `(response, out_dir, task_dir)`: no network, no clock,
  no RNG. Must accept the uniform invocation and always emit a
  `{pass, detail}` JSON line (see `tests/test_verify_contract.py`).
- Assume the model is adversarial; never `eval` response text.
- Reference answers belong in gitignored `tests/expected.json` /
  `vectors.json` / `exploit_reference.py`, not in the published verifier —
  unless the rule itself is the check (document it in `meta.json` notes).

## Checks

```bash
pip install -e '.[fetch,dev]'
pytest -q
python -m localbench list
```

CI runs pytest on 3.10 + 3.14, a CLI smoke test, an answer-key guard
(`SOLUTION.md`/`expected.json`/`vectors.json`/`exploit_reference.py` must
stay gitignored) and a machine-path guard. `LOCALBENCH_ALLOW_ROOT=1` exists
for containerised CI only — never set it for real runs.
