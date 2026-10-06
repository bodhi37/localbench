# Security policy

## Threat model

`localbench` runs an untrusted model (the system under test) as a coding
agent on your machine, then executes its output through graders. Assume the
model is adversarial: it can emit arbitrary text, code, tool calls and
filenames, and will try to exfiltrate secrets, reach the network, and escape
the task directory.

Defence in depth:

- Every agent run starts inside the `localbench-sandbox` cgroup via the
  `netguard` root helper; the kernel nftables guard drops non-endpoint
  egress for every protocol. Proxy variables are a second line only.
- The task view is a whitelist (`prompt.md` + `resources/`); verifiers,
  solutions and configs are never mounted.
- Verifiers and model-generated code run under `bwrap --unshare-net
  --unshare-pid` with a scrubbed environment (`PATH/HOME/TMPDIR/LANG/
  LC_ALL/TZ/PYTHONHASHSEED` only).
- The agent parent process, teardown hooks and code runners inherit a minimal
  allowlist environment — never the operator shell's `HF_TOKEN`, cloud or
  git keys.
- Result paths are sanitised (`safe_component`); top-level symlink task
  entries are never mounted.

## Rules for operators

1. **Never run as root.** The harness refuses uid 0 and the `exec-as`
   helper refuses `SUDO_UID` empty/0. Run as a normal user; only
   `netguard install/verify` use sudo (once per boot).
2. **Use dummy local-only API keys** for the provider under test. The active
   provider's `apiKey` is copied into the sandbox `models.json` by design
   (the agent needs it to reach the endpoint) and is readable there.
   Persisted transcripts/results are scrubbed for those values, but treat
   them as model-visible. Never benchmark with a production key that can
   spend money or read private data. Remote providers' keys are never
   mounted — only the provider under test.
3. **Review custom-task PRs.** `verify.py` runs sandboxed, but `teardown.sh`
   runs as your user (network-unshared, env-scrubbed, 60s timeout) so it
   can stop loopback task services. A merged task is arbitrary code you run
   on every invocation — review it like any other PR that executes code.
4. **Keep the guard installed.** If `netguard` is enabled but not installed,
   the run refuses to start rather than running unprotected. Do not set
   `"netguard": false` / `"sandbox": false` except for debugging.

## Reporting

See `CONTRIBUTING.md` for task-PR review notes. For sandbox-escape or
secret-leak reports, open a GitHub issue with `[security]` in the title and
include the `netguard status` output plus the minimal reproducing task.
