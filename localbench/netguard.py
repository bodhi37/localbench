"""Kernel-enforced egress isolation for the model's sandbox (root-assisted).

Proxy variables (``http_proxy=127.0.0.1:9``) are a *convention*: any program
that ignores them — a raw socket, a hand-rolled TCP stack, a DNS query — walks
straight past them. A 27B agent told "no network" is exactly the adversary
that tries, so the block is enforced by the kernel instead of requested from
the program.

Mechanism (one cgroup, one nftables table, one helper, no daemons):

  * a dedicated cgroup, ``/sys/fs/cgroup/localbench-sandbox``;
  * two hook chains in our own ``inet localbench_guard`` table:

    - **output**: mark the cgroup's loopback packets with ``0x0b000000``,
      pass all loopback, drop every other packet from the cgroup
      (internet, other interfaces, raw sockets, UDP — everything);
    - **input**: of those marked packets, accept the ones to an endpoint
      port, to a listener inside the cgroup, or belonging to an already
      established flow; drop the rest of them on loopback.

    The host's packets are never marked, so no rule ever matches them.
  * the harness starts every sandbox through a small root helper
    (``/usr/local/libexec/localbench-netguard`` via ``sudo -n``): the helper
    enters the guard cgroup as root, drops to the invoking user, and execs —
    so the sandbox is inside the cgroup *before* it execs anything, with no
    window to exploit. Root is needed because cgroup2 is mounted with
    ``nsdelegate``: uid 1000 can only migrate itself into descendants of its
    own cgroup, never into a root-level one.

What the sandbox can reach, and nothing else:

  * the endpoint under test (its port is in the allowlist — it listens on
    127.0.0.1 and the model has to talk to it);
  * services it starts itself (``127.0.0.1:8731`` relay and friends);
  * replies on flows opened through those two doors.

What it cannot reach — kernel-side, for every protocol:

  * the internet (output rule 3 matches on the *sending* cgroup socket);
  * foreign local services: DNS stub, another LLM, an agent API that could
    fetch the web, sync daemons — anything not listening inside its cgroup;
  * other machines entirely — except configured endpoint targets, which get
    one explicit per-target accept (that host, that TCP port, nothing else).

Non-endpoint traffic never leaves the cgroup, whatever the program tries.
(Note: bwrap leaves host ``/sys`` visible — ``/sys/fs/cgroup`` included —
so the model can *see* the cgroup tree; with ``nsdelegate`` it still cannot
move itself out of the guard cgroup, and the nftables match follows the
sending socket, not anything the process claims about itself.)

Installing needs root once per boot; ``scripts/netguard.sh`` is the entire
privileged surface, is idempotent, and proves the policy with a behavioural
self-test after every install.
"""
from __future__ import annotations

import getpass
import hashlib
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

from .config import ConfigError, ROOT

CGROUP_ROOT = Path("/sys/fs/cgroup")
CGROUP_NAME = "localbench-sandbox"
CGROUP_DIR = CGROUP_ROOT / CGROUP_NAME
NFT_TABLE = "localbench_guard"
STAMP = Path("/run/localbench-netguard.stamp")
STAMP_VERSION = "3"
SCRIPT = ROOT / "scripts" / "netguard.sh"
HELPER = Path("/usr/local/libexec/localbench-netguard")
SUDOERS = Path("/etc/sudoers.d/localbench-netguard")

LOOPBACK_HOSTS = {"127.0.0.1", "::1", "localhost"}


class NetguardError(RuntimeError):
    """Raised when the sandbox cannot be placed under kernel enforcement."""


def endpoint_targets() -> list[tuple[str, int]]:
    """Every (host, port) the sandbox must be able to reach.

    Endpoints need not live on loopback: a server on another interface
    (Tailscale, LAN) declares ``"host"`` in config/local.json (default
    ``127.0.0.1``). Loopback targets are covered by the loopback rules;
    anything else gets an explicit per-target nftables accept (TCP only,
    that port only) — the cgroup drop still kills everything not listed.
    """
    from .config import ep_host, load_local
    out: set[tuple[str, int]] = set()
    for ep in load_local().get("endpoints") or []:
        p = ep.get("port")
        if isinstance(p, bool):
            continue
        try:
            port = int(str(p).strip())
        except (ValueError, AttributeError):
            continue
        host = ep_host(ep).strip()
        if host:
            out.add((host, port))
    return sorted(out)


def endpoint_ports() -> list[int]:
    """Every configured endpoint port — the nftables loopback port set.

    This deliberately includes ports whose endpoint lives off-loopback: a
    Tailscale-local address routes via ``dev lo`` (``ip route get`` proves
    it), so that traffic is marked loopback traffic on the way back in and
    must match the port set. A loopback listener on an endpoint port was
    reachable by design anyway ("destined to an endpoint port → accept").
    """
    return sorted({port for _, port in endpoint_targets()})


def _targets_key(targets: Optional[list[tuple[str, int]]] = None) -> str:
    return ",".join(f"{h}:{p}" for h, p in sorted(targets or []))


def _enabled() -> bool:
    """``harness.netguard`` in config/local.json (default: on)."""
    try:
        from .config import load_local
        return bool((load_local().get("harness") or {}).get("netguard", True))
    except ConfigError:
        return True


def _script_sha() -> str:
    try:
        return hashlib.sha256(SCRIPT.read_bytes()).hexdigest()
    except OSError:
        return ""


def _stamp_ok(targets: Optional[list[tuple[str, int]]] = None) -> bool:
    """Stamp exists, is current — right version, right targets, right helper."""
    try:
        text = STAMP.read_text(encoding="utf-8")
    except OSError:
        return False
    lines = dict(
        ln.split("=", 1) for ln in text.splitlines() if "=" in ln)
    if lines.get("version") != STAMP_VERSION:
        return False
    if targets is not None:
        want = sorted(f"{h}:{p}" for h, p in targets)
        have_raw = lines.get("targets", "")
        have = sorted(have_raw.split(",")) if have_raw else []
        if have != want:
            return False
    sha = _script_sha()
    if not sha or lines.get("helper_sha") != sha:
        # the installed helper + rules no longer match this checkout: the
        # script changed since install, so reinstall before trusting it
        return False
    return True


def _loopback_only(targets: list[tuple[str, int]]) -> bool:
    return all(h in LOOPBACK_HOSTS for h, _ in targets)


def installed(targets: Optional[list[tuple[str, int]]] = None) -> bool:
    """Cheap, unprivileged: guard cgroup + helper present, fresh, and ours?

    The sudoers entry cannot be checked from here — ``/etc/sudoers.d`` is not
    readable by unprivileged users — so :func:`ensure` probes it functionally
    (``sudo -n ... exec-as true``) at run start instead.
    """
    return CGROUP_DIR.is_dir() and HELPER.is_file() and _stamp_ok(targets)


def _sudo(args: list[str], interactive: bool) -> subprocess.CompletedProcess:
    cmd = ["sudo"] + ([] if interactive else ["-n"]) + args
    return subprocess.run(cmd, capture_output=True, text=True,
                          input=None if interactive else "")


def _run_script(sub: str, args: list[str],
                label: str) -> tuple[bool, str]:
    """Run scripts/netguard.sh *sub* as root: passwordless first, then prompt."""
    if not SCRIPT.is_file():
        return False, f"netguard helper missing: {SCRIPT}"
    if not os.access(SCRIPT, os.X_OK):
        return False, (f"netguard helper is not executable: {SCRIPT} "
                       f"— run `chmod +x {SCRIPT}`")

    argv = [str(SCRIPT), sub] + args
    r = _sudo(argv, interactive=False)
    if r.returncode == 0:
        return True, (r.stdout or "").strip() or f"netguard {sub} ok"

    if sys.stdin.isatty() and sys.stderr.isatty():
        print(f"  netguard: {label} (sudo password required once per boot) ...")
        r = _sudo(argv, interactive=True)
        out = ((r.stdout or "") + (r.stderr or "")).strip()
        if r.returncode == 0:
            return True, out or f"netguard {sub} ok"
        return False, out or f"{SCRIPT} {sub} exited {r.returncode}"

    hint = (f"  Fix once:  sudo {SCRIPT} {sub} {' '.join(args)}\n"
            f"  Then rerun: python3 -m localbench run ...")
    msg = ((r.stderr or "") + (r.stdout or "")).strip()
    return False, (msg + "\n" + hint) if msg else hint


def cull() -> None:
    """Best-effort: kill anything left behind in the guard cgroup.

    A runner killed with SIGKILL (OOM, ``kill -9``) cannot clean up after
    itself, so the next run clears the cgroup before starting: only sandboxes
    ever live there, and none may survive their runner.
    """
    try:
        (CGROUP_DIR / "cgroup.kill").write_text("1", encoding="ascii")
    except OSError:
        pass


def _probe() -> tuple[bool, str]:
    """Prove *functionally* that this user can start guarded processes.

    Runs the helper with ``sudo -n`` (never prompts). The cached sudo ticket is
    dropped first so a stale timestamp cannot mask a missing sudoers entry —
    the sandbox's per-unit launches are passwordless too, so anything that
    would need a prompt there must fail here instead, at run start.
    """
    subprocess.run(["sudo", "-k"], capture_output=True)
    try:
        r = subprocess.run(["sudo", "-n", str(HELPER), "exec-as", "true"],
                           capture_output=True, text=True, input="")
    except OSError as e:
        return False, f"cannot run sudo: {e}"
    if r.returncode == 0:
        return True, ""
    msg = ((r.stderr or "") + (r.stdout or "")).strip()
    hint = (f"  Fix once:  sudo {SCRIPT} install {getpass.getuser()} "
            f"{','.join(str(p) for _, p in endpoint_targets())} "
            f"{_targets_key(endpoint_targets())}\n"
            f"  (restores {SUDOERS}; then rerun this command)")
    return False, (msg + "\n" + hint) if msg else hint


def ensure() -> tuple[bool, str]:
    """Make sure the kernel guard is active for *this* config. Idempotent."""
    if not _enabled():
        return True, "netguard disabled (harness.netguard=false in config)"
    targets = endpoint_targets()
    if installed(targets):
        cull()
        ok, msg = _probe()
        if not ok:
            return False, msg
        return True, f"netguard active (endpoints: {_targets_key(targets) or 'none'})"
    ok, msg = _run_script("install", [getpass.getuser(),
                                      ",".join(str(p) for _, p in targets),
                                      _targets_key(targets)],
                          "installing kernel egress rules")
    if not ok:
        return False, msg
    if not installed(targets):
        return False, (msg + "\n  installer reported success but the guard is "
                       "not usable by this user")
    ok, probe_msg = _probe()
    if not ok:
        return False, probe_msg
    return True, msg


def verify() -> tuple[bool, str]:
    """Behavioural self-test: spawn a process in the cgroup and attack."""
    targets = endpoint_targets() if _enabled() else []
    return _run_script("verify", [",".join(str(p) for _, p in targets),
                                  _targets_key(targets)],
                       "verifying kernel egress rules")


def uninstall() -> tuple[bool, str]:
    return _run_script("uninstall", [], "removing kernel egress rules")


def status() -> dict:
    cgroup = CGROUP_DIR.is_dir()
    stamp = None
    try:
        stamp = {ln.split("=", 1)[0]: ln.split("=", 1)[1]
                 for ln in STAMP.read_text(encoding="utf-8").splitlines()
                 if "=" in ln}
    except OSError:
        stamp = None
    return {
        "enabled": _enabled(),
        "installed": bool(cgroup and HELPER.is_file() and _stamp_ok()),
        "cgroup": str(CGROUP_DIR),
        "nft_table": NFT_TABLE,
        "stamp": str(STAMP),
        "stamp_targets": (stamp or {}).get("targets", ""),
        "helper": str(HELPER),
        "sudoers": str(SUDOERS),
        "script": str(SCRIPT),
    }


def wrap_argv(cfg: dict, argv: list[str]) -> list[str]:
    """Start the sandbox through the root attach helper.

    Returns ``argv`` unchanged only when the guard is disabled in config;
    when it is enabled but not installed, this raises — a sandbox that cannot
    be attached must not run silently unprotected.

    The helper (see ``scripts/netguard.sh exec-as``) enters the guard cgroup
    as root, drops privileges to the invoking user and execs ``argv``. The
    drop happens *before* exec, so the model never runs as root, and the
    cgroup entry happens first, so the model never runs outside the guard.
    """
    if not cfg.get("netguard", True):
        return list(argv)
    if not installed():
        # endpoint_targets() needs config/local.json, which a fresh clone
        # does not have yet — the guard hint must not crash with ConfigError
        # instead of the intended fail-closed NetguardError.
        try:
            targets = endpoint_targets()
        except ConfigError:
            targets = []
        raise NetguardError(
            "kernel egress guard is not installed — refusing to run the "
            f"model without it. Fix once: sudo {SCRIPT} install "
            f"{getpass.getuser()} "
            f"{','.join(str(p) for _, p in targets)} "
            f"{_targets_key(targets)}"
            f"  (or set \"netguard\": false in the harness section of "
            f"config/local.json to opt out)")
    return ["sudo", "-n", str(HELPER), "exec-as"] + list(argv)
