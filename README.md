# localbench

Benchmark **local LLM endpoints** against published academic benchmarks and
hand-crafted agentic tasks, through one harness so the scores are comparable.

```
localbench list                         # what's in the suite
localbench fetch                        # download published benchmarks
localbench run --dry-run                # what would run, and how much
localbench run --models my-model-a      # one model, default selection
localbench score                        # suite score + per-benchmark table
localbench score --bench bbh            # just one benchmark
localbench report                       # results/REPORT.md + results.json
```

One model on the GPU at a time. A GPQA question and a multi-file debugging
task go through the same Pi coding agent in a `bwrap` sandbox.

---

## The suite

| Source | Benchmarks | Items | Grader |
|---|---|---:|---|
| **Custom** | math, science, long-context, instruction-following, agentic-coding, cybersecurity | 18 tasks | each task's own `verify.py` |
| **Published** | MMLU, MMLU-Pro, GPQA Diamond, ARC-Challenge, HellaSwag, WinoGrande, TruthfulQA MC1 | 39,570 | `mcq` |
| | MATH-500, GSM8K, AIME 2024 | 1,849 | `math` |
| | HumanEval+, MBPP+ | 542 | `code` |
| | BIG-Bench Hard | 6,511 | `exact` |
| | IFEval | 541 | `ifeval` (official Google checkers) |

Published datasets are **fetched, not vendored**: `benchmarks/known/<id>/bench.json`
is the committed manifest (upstream URL, licence, grader, timeout);
`benchmarks/known/<id>/data/items.jsonl` is downloaded and gitignored.

---

## Quickstart

```bash
pip install -e '.[fetch,dev]'

cp config/local.json.example config/local.json   # then edit it
# config/local.json is gitignored: endpoints, serve commands, local paths

localbench fetch
# GPQA Diamond is gated: if it 403s, accept the terms at
# https://huggingface.co/datasets/idavidrein/gpqa, export HF_TOKEN,
# re-run `localbench fetch gpqa-diamond`. The rest fetch anonymously.

localbench run --dry-run
localbench run --models my-model-a --bench math,bbh --limit 50

localbench score
localbench report
```

`python3 -m localbench …` works the same without installing.

---

## Endpoints

Defined in `config/local.json` (gitignored):

```jsonc
{ "slug": "my-model", "provider": "my-local", "model": "my-model",
  "port": 8080, "units": ["my-model.service"], "ready": 600 }
{ "slug": "already-running", "provider": "my-local", "model": "my-model",
  "port": 8105, "external": true, "ready": 30 }
{ "slug": "tailscale-model", "provider": "my-local", "model": "my-model",
  "host": "192.0.2.1", "port": 8127, "external": true, "ready": 30 }
```

- `external: true` means don't manage it: only polled, left running after.
- `host` defaults to `127.0.0.1`. A remote server must be a literal IPv4
  address (no DNS inside the sandbox). The sandbox can reach that host
  **only** on the configured port.
- Before scoring, the endpoint must report the expected model on
  `/v1/models` **and** pass a 1-token completion. Single-model servers that
  report a different id (llama.cpp reports the GGUF path) are accepted; the
  reported id is stored as `reported_model`.

Use a **dummy local-only key** for the provider under test — its single-entry
`models.json` is visible to the model by design (other providers never are).
Never run as root. See `SECURITY.md`.

---

## Scoring

```
accuracy(benchmark) = passed / attempted
suite score         = Σ(weight × accuracy) / Σ(weight)
```

Weights live in `config/suite.json`. Under-covered benchmarks are flagged
`⚠partial` instead of scored as complete.

- `localbench score` — whole suite; `--bench`, `--models`, `--run` scope it
- default is the **newest run per model per benchmark**, so reruns never
  double-count
- `localbench score --json` — machine-readable
- `localbench netguard status` / `install` / `verify` / `uninstall` — egress guard

---

## How a unit runs

1. Start the endpoint (or poll it if `external`), confirm model id + 1-token
   completion.
2. Run the prompt through the Pi agent in `bwrap` (`--no-session
   --no-extensions --no-skills --no-prompt-templates --no-themes
   --no-context-files`, fixed system prompt, thinking `high`).
3. Write the final message to `$OUT_DIR/response.txt`.
4. Grade it: `verify`/`code` run in their own `bwrap` (no network, read-only
   task dir, scrubbed env); `mcq`/`exact`/`math`/`ifeval` are pure functions.
5. Append the record to `results/results.jsonl`; run `teardown.sh`.

---

## Sandboxing

- **Filesystem.** `/home /tmp /run /var /opt /srv /mnt /media /boot` are fresh
  tmpfs. Only `prompt.md` + `resources/` are mounted (read-only, whitelist);
  `verify.py`, `teardown.sh`, `SOLUTION.md`, `tests/`, `meta.json` never exist
  inside. Only the scratch dir and `$OUT_DIR` are writable.
- **Network.** Kernel-enforced via cgroup + nftables (`localbench-sandbox` /
  `localbench_guard`, installed once per boot): the sandbox reaches the
  configured endpoint port and services it started itself, nothing else —
  no internet, no DNS stub, no foreign local services. Proxy variables plus
  `NODE_USE_ENV_PROXY=1` remain as a second line of defence.
- **Secrets.** The agent parent, verifiers, model code and teardowns all run
  with a scrubbed environment. Endpoint keys echoed by the model are redacted
  from persisted transcripts/results. `/etc` stays read-only but visible
  (hostname/username readable, never published).

`teardown.sh` is trusted task code: no network, scrubbed env, 60s timeout,
symlinks refused. Review task PRs — a merged teardown runs as your user
(see `CONTRIBUTING.md`).

---

## Graders

| Grader | Used by | How it reads the answer |
|---|---|---|
| `verify` | custom tasks | task's `verify.py` in its own `bwrap` |
| `mcq` | MMLU, MMLU-Pro, GPQA, ARC, HellaSwag, WinoGrande, TruthfulQA | option letter from `FINAL: <letter>` |
| `exact` | BBH | last line / `FINAL:`, normalised |
| `math` | MATH-500, GSM8K, AIME | `FINAL:` or `\boxed{}`; `1/2` == `0.5` |
| `code` | HumanEval+, MBPP+ | extracts the program, runs the test suite |
| `ifeval` | IFEval | strict all-constraints, vendored Google checkers |

Published prompts get the same answer-format suffix at ingest (byte-for-byte
what the model sees), except IFEval, which gets none.

---

## Adding to the suite

Custom task at `benchmarks/custom/<domain>/<capability>/<tier>/<task-id>/`:

- `prompt.md` — what the model sees
- `verify.py` — `--task-dir/--out-dir/--response` → `{"pass", "detail"}`, exit 0/1
- `meta.json` — `id`, `domain`, `capability`, `tier`, `expected_duration`, `notes`
- `teardown.sh`, gitignored `SOLUTION.md`

Published benchmark: add a `Spec` + `build_*()` in `localbench/fetch.py`,
`localbench fetch <id>`, list it in `config/suite.json`.

---

## What ships

| Ships? | Files | Why |
|---|---|---|
| yes | `prompt.md`, `meta.json`, `resources/`, `tests/generate.py` | the benchmark definition |
| yes | `verify.py`, `teardown.sh` | scores must be auditable; the model never sees them |
| no | `SOLUTION.md`, `tests/expected.json`, `tests/vectors.json`, `tests/exploit_reference.py` | answer keys (gitignored) |
| no | `benchmarks/known/*/data/`, `config/local.json`, `results/` | datasets fetched; config/results local-only |

Some verifiers embed their rule; keyed tasks withhold `expected.json` /
`vectors.json` so re-checking means re-deriving the answer. Licences per
dataset in `bench.json`; IFEval attribution in `localbench/vendor/ifeval/NOTICE`
(full text in `LICENSES/Apache-2.0.txt`).

---

## Development

```bash
pip install -e '.[fetch,dev]'
pytest
```

CI runs pytest on Python 3.10 and 3.14, smoke-tests the CLI, and fails on
tracked answer keys or machine paths. No network, datasets, or bubblewrap needed.

## Licence

MIT — see [LICENSE](LICENSE).
