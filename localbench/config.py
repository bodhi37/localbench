"""Repo layout, and the two config files (committed vs machine-local)."""
from __future__ import annotations

import json
import os
from pathlib import Path


def _repo_root() -> Path:
    env = os.environ.get("LOCALBENCH_ROOT")
    if env:
        return Path(env).expanduser().resolve()
    # <root>/localbench/config.py -> <root>
    return Path(__file__).resolve().parent.parent


ROOT = _repo_root()
BENCHMARKS = ROOT / "benchmarks"
CUSTOM_ROOT = BENCHMARKS / "custom"
KNOWN_ROOT = BENCHMARKS / "known"
CONFIG_DIR = ROOT / "config"
SUITE_FILE = CONFIG_DIR / "suite.json"
LOCAL_FILE = CONFIG_DIR / "local.json"
LOCAL_EXAMPLE = CONFIG_DIR / "local.json.example"
RESULTS_DIR = ROOT / "results"
RESULTS_JSONL = RESULTS_DIR / "results.jsonl"


class ConfigError(RuntimeError):
    """Raised for missing/invalid configuration, with a fix-it hint."""


def load_json(path: Path) -> dict:
    if not path.is_file():
        raise ConfigError(f"missing config file: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ConfigError(f"{path} is not valid JSON: {e}") from e


def load_suite() -> dict:
    """Committed suite definition: weights + default benchmark selection."""
    cfg = load_json(SUITE_FILE)
    if not isinstance(cfg.get("weights"), dict):
        raise ConfigError(f"{SUITE_FILE} must contain a 'weights' object")
    return cfg


def load_local() -> dict:
    """Machine-local config: harness paths, endpoints, conflict units.

    Gitignored on purpose — a fresh clone only ships config/local.json.example.
    """
    if not LOCAL_FILE.is_file():
        raise ConfigError(
            f"missing {LOCAL_FILE}\n"
            f"  This file holds your endpoints and local harness paths and is "
            f"gitignored.\n"
            f"  Fix: cp {LOCAL_EXAMPLE} {LOCAL_FILE}  # then edit it"
        )
    cfg = load_json(LOCAL_FILE)
    if not isinstance(cfg.get("endpoints"), list):
        raise ConfigError(f"{LOCAL_FILE} must contain an 'endpoints' array")
    return cfg


def harness_cfg() -> dict:
    defaults = dict(pi_tree="", pi_cli="", models_json="", npm_global="",
                    sandbox=True, netguard=True, thinking="high")
    defaults.update(load_local().get("harness") or {})
    missing = [k for k in ("pi_tree", "models_json", "npm_global")
               if not defaults.get(k)]
    if missing:
        raise ConfigError(f"harness config missing {missing} in {LOCAL_FILE}")
    return defaults


def ep_host(ep: dict) -> str:
    """Where an endpoint listens. Loopback unless the config says otherwise
    (a Tailscale/LAN server declares ``"host"`` as a literal IP — DNS is
    blocked inside the sandbox by design, so hostnames cannot work there)."""
    return str(ep.get("host") or "127.0.0.1")
