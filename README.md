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

{ "slug": "tailscale-model", "provider": "my-local", "model": "my-model",
  "host": "192.0.2.1",                  // literal IPv4, not loopback
  "port": 8127, "api_key": null,          // bearer key for readiness probes;
                                          // null = reuse the provider's apiKey
                                          // from models.json automatically
  "external": true, "ready": 30 }
```

`"external": true` means *don't manage it*: no conflicting server is stopped,
nothing is started, and it is left running when the run ends. Use it for a
server you started yourself, or for one on another machine.

`"host"` defaults to `127.0.0.1`. A non-loopback host must be a literal IPv4
address — DNS names cannot resolve inside the sandbox, because name resolution
is blocked there by design. The sandbox may reach that host **only** on the
configured TCP port; everything else on that interface stays dropped (see
**Sandboxing**). The `no_proxy` carve-out automatically includes every
configured endpoint host, so the dead-proxy convention never blocks the model
from reaching its own endpoint.

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
- `localbench score --run <run_id>` — one run; default is the **newest run
  per model per benchmark**, so repeated runs never double-count and a
  model's older benchmarks are not silently dropped
- `localbench score --json` — machine-readable
- `localbench netguard status` / `install` / `verify` / `uninstall` — manage
  the kernel egress guard

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
  netguard.py               egress-guard stamp checks + sandbox argv wrapping
  vendor/ifeval/            vendored official IFEval checkers (Apache-2.0)
scripts/
  netguard.sh               the whole privileged surface of the egress guard
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
4. The unit's grader produces `(passed, detail)` — `verify`/`code` graders may
   themselves exec processes, so they run in their own `bwrap` (no network,
   read-only task dir, scrubbed env); `mcq`/`exact`/`math`/`ifeval` are pure.
5. The record is appended to `results/results.jsonl`; teardown runs.

### Contamination controls

- Custom task directories are mounted **whitelist**-style read-only: only
  `prompt.md` and the task's shipped `resources/` exist in the sandbox.
  `SOLUTION.md`, `verify.py`, `teardown.sh`, `tests/` and any file added to the
  directory later simply do not exist in there — they are not masked to
  `/dev/null`, they are never at that path at all. Published tasks ship no
  `meta.json` internals either; the prompt is the entire task view.
- Sandbox `/home /tmp /run /var /opt /srv /mnt /media /boot` are fresh tmpfs
  mounts. Writable paths are only the task's scratch dir and `$OUT_DIR`, so the
  agent cannot read your home directory, model weights, or other tasks.
- `$HOME/.pi/agent/models.json` is a **filtered** copy holding only the
  provider under test (your real registry — with every other provider's API
  key — is never mounted); `--no-session --no-extensions --no-skills
  --no-prompt-templates --no-themes --no-context-files`.
- Egress is **kernel-enforced**, not a proxy convention — see **Sandboxing**.
  (The dead-proxy variables stay set as a second line of defence, but nothing
  depends on the program choosing to honour them.)
- Model-generated code (HumanEval+, MBPP+) is executed with no network
  (`bwrap --unshare-net`) and no view of the host filesystem.
- Custom-task verifiers run the same way: their own `bwrap --unshare-net
  --unshare-pid`, task dir read-only, scrubbed environment.

---

## Graders

All graders are pure functions of the response text — no network, no clock, no
RNG — so the same response always grades the same way.

| Grader | Used by | How it reads the answer |
|---|---|---|
| `verify` | custom tasks | runs the task's own `verify.py` in its own `bwrap` (no network, read-only task dir) |
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
  tasks, or `config/local.json`. The task directory is mounted **whitelist**:
  `prompt.md` and the task's `resources/` are read-only binds; `SOLUTION.md`,
  `verify.py`, `teardown.sh`, `tests/` and any future file simply do not exist
  on the sandbox's filesystem. Writable paths are only the task scratch dir
  and `$OUT_DIR`.
- **Task view.** `--no-session --no-extensions --no-skills
  --no-prompt-templates --no-themes --no-context-files`, a fixed task-neutral
  system prompt, `PI_OFFLINE=1`. The only Pi state available is a **filtered**
  `models.json` containing just the provider under test — the real registry
  lists every provider you have configured, each carrying an API key, and none
  of the others are ever mounted.
- **Process tree.** `--unshare-pid`, `--die-with-parent`, `--new-session`.
  Timing out or interrupting the runner kills the whole process group; a
  runner killed with SIGKILL is backstopped on the next run by clearing the
  guard cgroup via `cgroup.kill`.
- **Generated code.** HumanEval+/MBPP+ output runs under a *second* `bwrap`
  with `--unshare-net`, no host filesystem, a private tmpfs `/tmp`, and a
  180s wall clock.

What is **kernel-enforced about egress**, since the sandbox shares the host net:

- **Egress from the agent itself.** The sandbox must share the host network —
  the model under test lives on `127.0.0.1`, and `bwrap --unshare-net` would
  hand the agent a private loopback that cannot reach it. So enforcement moved
  below the convention entirely: every sandbox process starts inside the
  dedicated cgroup `localbench-sandbox`, and the `inet localbench_guard`
  nftables table (installed once per boot) shapes its packets:

    - *output hook* — the cgroup's loopback packets get mark `0x0b000000`,
      loopback is otherwise passed through, and **every other packet it tries
      to send is dropped** (raw sockets, UDP — anything);
    - *input hook* — of those marked replies, only traffic to a configured
      endpoint port or to a listener *inside the cgroup*, plus established
      flows, is accepted; all other marked loopback traffic is dropped, so
      foreign local services (DNS stub, another LLM, agent APIs) are
      unreachable from the sandbox. Host packets themselves are never marked,
      so none of this ever matches the host.
    - *non-loopback endpoint targets* (a `"host"` that is not loopback, e.g.
      Tailscale) get one explicit output accept each — that IPv4 host, that
      TCP port, and nothing else. Replies need no rule: they can only exist
      if their SYN passed an accept first, and unmarked non-loopback input is
      accepted by chain policy. `localbench netguard verify` proves each
      listed target reachable and a neighbouring unlisted port on the same
      host blocked.

    Entry is race-free: `scripts/netguard.sh` is installed with
    `python3 -m localbench netguard install` once per boot, and each sandbox
    starts via `sudo -n /usr/local/libexec/localbench-netguard exec-as` — a
    root helper that enters the cgroup, drops to the invoking user with
    `setpriv`, *then* execs the sandbox command. One narrow NOPASSWD
    sudoers line, no setuid, no general sudo, and the helper can only ever
    move itself.

  `netguard verify` measures every direction:

  | probe (sandbox side) | result |
  |---|---|
  | → a configured endpoint port | **allowed** |
  | → a service it started itself | **allowed** |
  | → a foreign loopback service | blocked |
  | → the internet | blocked |
  | → the DNS stub | blocked |

  …and from the host: foreign services, endpoint ports, internet untouched.
  The guard survives a crashed runner: the next `run` clears whatever the
  previous one left in the guard cgroup via `cgroup.kill`.

- The dead-proxy environment variables (`http_proxy=127.0.0.1:9`, own-loopback
  `no_proxy` carve-out, `NODE_USE_ENV_PROXY=1` so Node's built-in `fetch`
  honours them) are still set as a second line of defence — with the kernel
  rules they are belt-and-braces, not load-bearing.

- **`/etc` is read-only but visible**, so the hostname and local username are
  readable. They never reach the published repo.

---

## What is and isn't published

| | Published? | Why |
|---|---|---|
| `prompt.md`, `meta.json`, `resources/`, `tests/generate.py`, `tests/check_replay.py` | yes | the benchmark definition |
| `verify.py`, `teardown.sh` | **yes** | a score nobody can audit is worthless; this is how MMLU/BBH/GPQA ship. The model never sees them — whitelist mounts |
| `SOLUTION.md` | **no** (gitignored) | the worked walkthrough is what actually removes the reasoning challenge |
| `tests/expected.json`, `tests/vectors.json` | **no** (gitignored) | the graded answer keys; same withholding reason as `SOLUTION.md` — verifiers reference them, your local copy exists but is never committed |
| `tests/exploit_reference.py` | **no** (gitignored) | a reference solver — same reason as `SOLUTION.md` |
| `benchmarks/known/*/data/` | no (fetched) | licensing + repo size; `bench.json` records the upstream URL and licence |
| `config/local.json` | no (gitignored) | endpoints, serve commands, your local paths |
| `results/` | no (gitignored) | run artifacts |

Note that graders being public means their inputs are auditable. For tasks
whose verifier embeds its rule (e.g. the vault-constraint arithmetic of
`cybersecurity-ctf-502`, the token+work-hash chain of `cybersecurity-offsec-503`)
anyone can re-check a verdict from the script alone. For tasks keyed on
`tests/expected.json` / `tests/vectors.json` those key files are withheld
alongside `SOLUTION.md`, so a reader must re-derive the answer to re-check a
score — which is exactly the reasoning challenge in the first place. The
model under test never sees any of it either way: whitelist mounts keep only
`prompt.md` and `resources/` in the sandbox.

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
