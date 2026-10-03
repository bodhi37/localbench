# localbench

Benchmark **local LLM endpoints** against a hybrid suite of published academic
benchmarks and hand-crafted agentic tasks, then score them against the whole
suite or any individual benchmark.

Everything runs through **one harness**: the Pi coding agent inside a `bwrap`
sandbox, one model resident on the GPU at a time. A GPQA question and a
multi-file debugging task are graded by the same machinery, so their scores are
directly comparable.

```
localbench list                         # what's in the suite
localbench fetch                        # download published benchmarks
localbench run --dry-run                # what would run, and how much
localbench run --models my-model-a      # one model, default selection
localbench score                        # suite score + per-benchmark table
localbench score --bench bbh            # just one benchmark
localbench report                       # results/REPORT.md + results.json
```

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

Published datasets are **fetched, not vendored** — each has its own licence and
the raw text would dominate the repo. `benchmarks/known/<id>/bench.json` holds
the manifest (upstream URL, licence read from the dataset card, grader, timeout);
`benchmarks/known/<id>/data/items.jsonl` holds the data and is gitignored.

---

## Quickstart

```bash
# 1. dependencies (only `fetch` needs anything beyond the stdlib)
pip install -e '.[fetch,dev]'

# 2. machine-local config — endpoints, server units, harness paths
cp config/local.json.example config/local.json   # then edit it
#    this file is gitignored: it holds your model paths and serve commands

# 3. pull the published datasets
localbench fetch
#    NOTE: GPQA Diamond is gated. If it 403s, accept the terms at
#    https://huggingface.co/datasets/idavidrein/gpqa, export HF_TOKEN, and
#    re-run `localbench fetch gpqa-diamond`. Everything else fetches anonymously.

# 4. check what a bare run would do
localbench run --dry-run

# 5. run it
localbench run --models my-model-a --bench math,bbh --limit 50

# 6. score and report
localbench score
localbench report
```

`python3 -m localbench …` works identically if you'd rather not install.

---

## Endpoints

Endpoints live in `config/local.json` (gitignored). Two shapes:

```jsonc
{ "slug": "my-model", "provider": "my-local", "model": "my-model",
  "port": 8080,
  "units": ["my-model.service"],          // systemd --user units to start
  "serve_cmd": null,                      // or a script instead of a unit
  "proc_kill": ["\\bft serve --model "],  // patterns killed for VRAM hygiene
  "ready": 600 }                          // seconds to wait for weights

{ "slug": "already-running", "provider": "my-local", "model": "my-model",
  "port": 8105, "external": true, "ready": 30 }
```

`"external": true` means *don't manage it*: no conflicting server is stopped,
nothing is started, and it is left running when the run ends. Use it for a
server you started yourself, or for one on another machine.

`localbench` refuses to run against an endpoint until `/v1/models` reports the
configured model **and** a 1-token completion succeeds — so a half-loaded or
wrong model never silently scores. Servers that host exactly one model and
report some other id (llama.cpp reports the GGUF path) are accepted on that
basis; the id actually reported is written to every result row as
`reported_model`.

---

## Scoring

The formula is deliberately boring and fully visible:

```
accuracy(benchmark) = passed / attempted          on the units actually run
suite score         = Σ(weight × accuracy) / Σ(weight)   over benchmarks with ≥1 attempt
```

Weights live in [`config/suite.json`](config/suite.json) — edit them, they are
not hidden in code. A benchmark whose `attempted` count is below the number of
units it was selected with is flagged `⚠partial` rather than silently scored as
if it had completed.

- `localbench score` — whole suite, one table
- `localbench score --bench bbh` — score scoped to one benchmark
- `localbench score --models a,b` — a subset of models
- `localbench score --run <run_id>` — one run; default is the **newest run per
  model**, so a model is never double-counted by repeated runs
- `localbench score --json` — machine-readable

Every result row carries its own `expected` denominator, so scores stay correct
even when `--limit` or `--tasks` changes how much of a benchmark was run.

---

## Repository layout

```
localbench/                 the package
  registry.py               discovers tasks + datasets, flattens them to Units
  harness.py                bwrap sandbox + Pi agent, transcript parsing
  graders.py                mcq / exact / math / code / ifeval / verify
  runner.py                 endpoint lifecycle + the run loop
  scoring.py                per-benchmark accuracy, weighted suite score
  report.py                 results/REPORT.md
  fetch.py                  dataset download + normalisation
  vendor/ifeval/            vendored official IFEval checkers (Apache-2.0)
config/
  suite.json                committed: weights, default selection, default_limit
  local.json                gitignored: endpoints, harness paths
  local.json.example        committed: template for the above
benchmarks/
  custom/<domain>/<capability>/<tier>/<task-id>/
                            prompt.md  meta.json  verify.py
                            teardown.sh  [resources/]  [tests/]
                            SOLUTION.md               gitignored (withheld)
  known/<bench-id>/
                            bench.json            committed (manifest)
                            data/items.jsonl      gitignored (the dataset)
results/                    run artifacts, gitignored
tests/                      pytest suite
```

---

## How a unit runs

1. The endpoint is started: every conflicting server unit stopped, VRAM drained,
   then `/v1/models` must report the expected model id **and** a 1-token
   completion must succeed (weights fully loaded). An endpoint marked
   `"external": true` skips the start/stop cycle — it is polled only, and left
   running afterwards — so you can benchmark a server you started yourself.
   Servers that host a single model and report some other id (llama.cpp reports
   the GGUF path) are accepted on that basis; the id actually reported is
   recorded on every result row as `reported_model`.
2. The unit runs through the Pi agent in a `bwrap` sandbox with a fixed
   task-neutral system prompt and thinking level `high`.
3. The final assistant message is written to `$OUT_DIR/response.txt`.
4. The unit's grader produces `(passed, detail)` **outside** the sandbox.
5. The record is appended to `results/results.jsonl`; teardown runs.

### Contamination controls

- Custom task directories are mounted read-only with `SOLUTION.md`,
  `verify.py` and `teardown.sh` masked out with `/dev/null` — the model sees
  only `prompt.md` and the task's shipped `resources/`.
- Sandbox `/home /tmp /run /var /opt /srv /mnt /media /boot` are fresh tmpfs
  mounts. Writable paths are only the task's scratch dir and `$OUT_DIR`, so the
  agent cannot read your home directory, model weights, or other tasks.
- `$HOME/.pi/agent/models.json` is a **filtered** copy holding only the
  provider under test (your real registry — with every other provider's API
  key — is never mounted); `--no-session --no-extensions --no-skills
  --no-prompt-templates --no-themes --no-context-files`.
- Published benchmark items get no task directory at all — just the prompt.
- Outbound HTTP is pointed at a dead proxy with loopback exempted (see
  **Sandboxing** below for exactly how strong that is).
- Model-generated code (HumanEval+, MBPP+) is executed with no network
  (`bwrap --unshare-net`) and no view of the host filesystem.

---

## Graders

All graders are pure functions of the response text — no network, no clock, no
RNG — so the same response always grades the same way.

| Grader | Used by | How it reads the answer |
|---|---|---|
| `verify` | custom tasks | runs the task's own `verify.py` against `$OUT_DIR` |
| `mcq` | MMLU, MMLU-Pro, GPQA, ARC, HellaSwag, WinoGrande, TruthfulQA | option letter from `FINAL: <letter>` |
| `exact` | BBH | last line / `FINAL:`, normalised (case, articles, punctuation) |
| `math` | MATH-500, GSM8K, AIME | `FINAL:` or `\boxed{}`; numeric compare first (`1/2` == `0.5`), normalised symbolic second |
| `code` | HumanEval+, MBPP+ | extracts the program and runs the benchmark's own test suite |
| `ifeval` | IFEval | strict all-constraints-satisfied, via the vendored official checkers |

Every published prompt is given the same answer-format instruction at ingest,
so the prompt stored in `items.jsonl` is byte-for-byte what the model sees.
IFEval is the one exception: it gets **no** suffix, because extra text would
violate the very constraints being tested.

---

## Adding to the suite

**A custom task** — create
`benchmarks/custom/<domain>/<capability>/<tier>/<task-id>/` with:

- `prompt.md` — everything the model sees
- `verify.py` — accepts `--task-dir/--out-dir/--response`, prints a JSON line
  `{"pass": bool, "detail": str}` and exits 0/1
- `meta.json` — `id`, `domain`, `capability`, `tier`, `runs`,
  `expected_duration` (drives the timeout), plus a `notes` field documenting
  what the task isolates and how false positives were audited
- `SOLUTION.md` (gitignored — withheld from the published repo),
  `teardown.sh` (kept out of the model's view)

**A published benchmark** — add a `Spec` in
[`localbench/fetch.py`](localbench/fetch.py) with a `build_*()` function that
returns rows shaped `{"id", "prompt", "answer", "meta", "grader"}`, then
`localbench fetch <id>` and add it to `default_benchmarks`/`weights` in
`config/suite.json`.

---

## Sandboxing — what it does and doesn't guarantee

The agent runs under `bwrap`. What is enforced:

- **Filesystem.** `/home /tmp /run /var /opt /srv /mnt /media /boot` are fresh
  `tmpfs`, so the agent cannot see your home directory, model weights, other
  tasks, or `config/local.json`. The task directory is a read-only bind with
  `SOLUTION.md`, `verify.py` and `teardown.sh` masked to `/dev/null`. Writable
  paths are only the task scratch dir and `$OUT_DIR`.
- **Task view.** `--no-session --no-extensions --no-skills
  --no-prompt-templates --no-themes --no-context-files`, a fixed task-neutral
  system prompt, `PI_OFFLINE=1`. The only Pi state available is a **filtered**
  `models.json` containing just the provider under test — the real registry
  lists every provider you have configured, each carrying an API key, and none
  of the others are ever mounted.
- **Generated code.** HumanEval+/MBPP+ output runs under a *second* `bwrap`
  with `--unshare-net`, no host filesystem, a private tmpfs `/tmp`, and a
  180s wall clock.

What is **not** kernel-enforced:

- **Egress from the agent itself.** The sandbox must share the host network —
  the model under test lives on `127.0.0.1`, and `bwrap --unshare-net` would
  hand the agent a private loopback that cannot reach it. So outbound HTTP is
  blocked *by convention*: `http_proxy`/`https_proxy`/`all_proxy` point at a
  dead port while `no_proxy` carves out loopback, and `NODE_USE_ENV_PROXY=1`
  makes Node's built-in `fetch` honour those variables (it ignores them by
  default, and Pi is a Node app).

  Measured from inside the real harness argv, against a host that *does* have
  internet:

  | probe | result | mechanism |
  |---|---|---|
  | `curl http://example.com` | blocked (`000`) | proxy → `ECONNREFUSED` |
  | Python `urllib` | blocked (`URLError`) | proxy |
  | Node `fetch` | blocked (`ECONNREFUSED`) | proxy, via `NODE_USE_ENV_PROXY` |
  | `http://127.0.0.1:8105/health` | **200** | loopback stays reachable |

  Name resolution also fails inside the sandbox, but *incidentally*: `/run` is
  a fresh `tmpfs`, and on systemd hosts `/etc/resolv.conf` is a symlink into
  `/run/systemd/resolve/`. That will not hold on a host whose `resolv.conf` is
  a plain file, so do not count on it.

  **Raw sockets are not intercepted.** Treat this whole mechanism as an
  anti-footgun, not a guarantee. If a hard guarantee matters for your eval, run
  the job on a machine whose only route is to `127.0.0.1`. `localbench` invokes
  `bwrap` unprivileged — no setuid helper, no `sudo`, no added capabilities —
  so it composes with whatever network policy you apply outside it.

- **`/etc` is read-only but visible**, so the hostname and local username are
  readable. They never reach the published repo.

---

## What is and isn't published

| | Published? | Why |
|---|---|---|
| `prompt.md`, `meta.json`, `resources/`, `tests/` | yes | the benchmark itself — nobody can run or audit it otherwise |
| `verify.py` | **yes** | a score nobody can audit is worthless; this is how MMLU/BBH/GPQA ship |
| `SOLUTION.md` | **no** (gitignored) | the worked walkthrough is what actually removes the reasoning challenge |
| `benchmarks/known/*/data/` | no (fetched) | licensing + repo size; `bench.json` records the upstream URL and licence |
| `config/local.json` | no (gitignored) | endpoints, serve commands, your local paths |
| `results/` | no (gitignored) | run artifacts |

Note that the graders being public means the expected values for the custom
tasks are visible in-repo. That is deliberate: they are the *output* of solving
a problem stated in `prompt.md`, so anyone willing to read them could equally
just solve it — while hiding them would make your scores unauditable. The model
under test never sees them either way, because the sandbox masks them.

Dataset licences are recorded per benchmark in `bench.json`; the datasets
themselves are not redistributed. `localbench/vendor/ifeval/NOTICE` carries the
Apache-2.0 attribution for the vendored Google checkers.

---

## Development

```bash
pip install -e '.[fetch,dev]'
pytest            # graders, registry, scoring, report, sandbox invariants
```

CI (`.github/workflows/ci.yml`) runs the suite on Python 3.10 and 3.14, smoke-tests
the CLI, and fails the build if an answer key ever becomes tracked or an absolute
machine path leaks into a tracked file. None of it needs network, fetched datasets
or bubblewrap.

## Licence

MIT — see [LICENSE](LICENSE).
