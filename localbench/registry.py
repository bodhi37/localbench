"""Discover benchmarks and flatten them into a uniform stream of Units.

Two sources, one shape:

  * ``benchmarks/custom/<domain>/<capability>/<tier>/<task-id>/`` — a hand-built
    task directory. ``prompt.md`` is the prompt, ``verify.py`` grades it. One
    task directory == one Unit. The directory is mounted read-only into the
    sandbox so the model can read its shipped ``resources/``.

  * ``benchmarks/known/<bench-id>/`` — a published dataset already normalised
    into ``bench.json`` + ``data/items.jsonl`` by ``scripts/fetch_known.py``.
    One JSONL row == one Unit; the grader named in ``bench.json`` scores it.

Both run through the same agentic harness, so a Unit only ever needs: a prompt,
a timeout, where to find its files, and how to grade it.
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator, Optional

from .config import CUSTOM_ROOT, KNOWN_ROOT, load_suite

DEFAULT_TIMEOUT_S = 600
MAX_TIMEOUT_S = 3600


@dataclass
class Unit:
    uid: str                # globally unique: "task/<id>" or "item/<bench>/<id>"
    suite: str              # "custom" | "known"
    benchmark: str          # scoring group (domain for custom, bench id for known)
    kind: str               # "task" | "item"
    ref: str                # task id or item id
    prompt: str
    timeout: int
    grader: str             # "verify" | "mcq" | "exact" | "math" | "code" | "ifeval"
    task_dir: Optional[Path] = None
    answer: Any = None
    meta: dict = field(default_factory=dict)

    def to_record(self) -> dict:
        """Stable, JSON-safe description for result rows (prompt excluded)."""
        return dict(uid=self.uid, suite=self.suite, benchmark=self.benchmark,
                    kind=self.kind, ref=self.ref, grader=self.grader,
                    timeout=self.timeout, task=str(self.task_dir) if self.task_dir else None)


# --------------------------------------------------------------------------- #
# custom task directories
# --------------------------------------------------------------------------- #

def _timeout_from_meta(meta: dict) -> int:
    """Derive a wall-clock cap from meta['expected_duration'] ("1-3" minutes).

    meta['timeout_s'] always wins. The derived cap is 2x the upper bound with a
    600s floor, so tier-1/2/3 tasks land on roughly 600/720/1200s.
    """
    explicit = meta.get("timeout_s")
    if isinstance(explicit, (int, float)) and explicit > 0:
        return min(int(explicit), MAX_TIMEOUT_S)
    dur = str(meta.get("expected_duration", "")).strip()
    try:
        upper = float(dur.split("-")[-1])
    except (ValueError, IndexError):
        return DEFAULT_TIMEOUT_S
    return min(max(DEFAULT_TIMEOUT_S, int(upper * 60 * 2)), MAX_TIMEOUT_S)


def discover_custom() -> list[dict]:
    """Metadata for every custom task dir, ordered by (tier, task id)."""
    out = []
    for meta_path in sorted(CUSTOM_ROOT.glob("*/*/*/*/meta.json")):
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            raise RuntimeError(f"unreadable {meta_path}: {e}") from e
        tid = meta.get("id")
        if not tid:
            raise RuntimeError(f"{meta_path} has no 'id'")
        task_dir = meta_path.parent
        if not (task_dir / "prompt.md").is_file():
            raise RuntimeError(f"{task_dir} has no prompt.md")
        if not (task_dir / "verify.py").is_file():
            raise RuntimeError(f"{task_dir} has no verify.py")
        out.append(dict(
            suite="custom",
            benchmark=meta.get("domain") or task_dir.parent.parent.name,
            kind="task",
            ref=tid,
            task_dir=task_dir,
            timeout=_timeout_from_meta(meta),
            grader="verify",
            meta=meta,
            tier=int(meta.get("tier", 0)),
        ))
    out.sort(key=lambda d: (d["tier"], d["ref"]))
    return out


def _load_custom_unit(d: dict) -> Unit:
    return Unit(
        uid=f"task/{d['ref']}",
        suite=d["suite"],
        benchmark=d["benchmark"],
        kind=d["kind"],
        ref=d["ref"],
        prompt=(d["task_dir"] / "prompt.md").read_text(encoding="utf-8"),
        timeout=d["timeout"],
        grader=d["grader"],
        task_dir=d["task_dir"],
        meta=d["meta"],
    )


# --------------------------------------------------------------------------- #
# known benchmark datasets
# --------------------------------------------------------------------------- #

def discover_known() -> list[dict]:
    """Metadata for every known benchmark that has been fetched."""
    out = []
    for bench_json in sorted(KNOWN_ROOT.glob("*/bench.json")):
        cfg = json.loads(bench_json.read_text(encoding="utf-8"))
        for key in ("id", "name", "grader"):
            if key not in cfg:
                raise RuntimeError(f"{bench_json} is missing '{key}'")
        data_file = bench_json.parent / "data" / "items.jsonl"
        out.append(dict(
            suite="known",
            benchmark=cfg["id"],
            kind="item",
            bench=cfg,
            data_file=data_file,
            timeout=int(cfg.get("timeout", DEFAULT_TIMEOUT_S)),
            grader=cfg["grader"],
            fetched=data_file.is_file(),
        ))
    out.sort(key=lambda d: d["benchmark"])
    return out


def _load_known_units(d: dict, limit: int) -> list[Unit]:
    """Read items.jsonl. ``limit`` truncates in file order; the fetch script
    shuffles with a fixed seed at ingest, so a prefix is a stable sample."""
    bench = d["bench"]
    units: list[Unit] = []
    with d["data_file"].open(encoding="utf-8") as fh:
        for idx, line in enumerate(fh):
            if limit and idx >= limit:
                break
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            ref = str(row.get("id", idx))
            units.append(Unit(
                uid=f"item/{bench['id']}/{ref}",
                suite="known",
                benchmark=bench["id"],
                kind="item",
                ref=ref,
                prompt=row["prompt"],
                timeout=d["timeout"],
                grader=row.get("grader") or d["grader"],
                answer=row.get("answer"),
                meta={**row.get("meta", {}), "bench": bench},
            ))
    return units


# --------------------------------------------------------------------------- #
# selection
# --------------------------------------------------------------------------- #

def discover(include_unfetched: bool = False) -> list[dict]:
    """Everything the suite knows about, custom first then known."""
    known = discover_known()
    if not include_unfetched:
        known = [k for k in known if k["fetched"]]
    return discover_custom() + known


def load_units(benchmarks: Optional[list[str]] = None,
               tasks: Optional[list[str]] = None,
               limit: int = 0,
               include_unfetched: bool = False) -> list[Unit]:
    """Flatten selected benchmarks into Units.

    benchmarks : benchmark names to include (None -> suite.json defaults)
    tasks      : restrict to specific refs (custom task ids or item ids)
    limit      : per-benchmark item cap; 0 = everything (custom tasks unaffected)
    """
    suite = load_suite()
    wanted = list(benchmarks) if benchmarks else list(suite.get("default_benchmarks", []))
    wanted_set = set(wanted)

    specs = [d for d in discover(include_unfetched=include_unfetched)
             if d["benchmark"] in wanted_set]

    known_present = {d["benchmark"] for d in specs if d["suite"] == "known"}
    unknown = [b for b in wanted if b not in {d["benchmark"] for d in specs}]
    if unknown and not known_present and not specs:
        raise RuntimeError(f"no benchmarks matched {unknown}")
    if unknown:
        # A typo next to a valid name must not silently narrow the run.
        print(f"WARNING: unknown benchmark(s) ignored: {unknown}",
              file=sys.stderr)

    units: list[Unit] = []
    for d in specs:
        if d["suite"] == "custom":
            units.append(_load_custom_unit(d))
        else:
            units.extend(_load_known_units(d, limit))

    if tasks:
        keep = set(tasks)
        units = [u for u in units if u.ref in keep or u.uid in keep]
    return units


def expected_counts(benchmarks: Optional[list[str]] = None,
                    limit: int = 0) -> dict[str, int]:
    """How many units each selected benchmark *should* contribute.

    Mirrors :func:`load_units` selection without reading prompts, so scoring can
    tell a complete benchmark from a partially-run one.
    """
    suite = load_suite()
    wanted = set(benchmarks or suite.get("default_benchmarks", []))
    counts: dict[str, int] = {}
    for d in discover():
        name = d["benchmark"]
        if name not in wanted:
            continue
        if d["suite"] == "custom":
            counts[name] = counts.get(name, 0) + 1
        else:
            with d["data_file"].open(encoding="utf-8") as fh:
                n = 0
                for n, line in enumerate(fh, 1):
                    if limit and n >= limit:
                        break
            counts[name] = counts.get(name, 0) + n
    return counts


def benchmarks_available() -> dict[str, dict]:
    """benchmark name -> {suite, count|'unfetched', grader, ...}"""
    suite = load_suite()
    info: dict[str, dict] = {}
    for d in discover_custom():
        info.setdefault(d["benchmark"], dict(suite="custom", grader="verify"))
        info[d["benchmark"]]["tasks"] = info[d["benchmark"]].get("tasks", 0) + 1
    for d in discover_known():
        b = d["bench"]
        entry = dict(suite="known", grader=d["grader"], name=b.get("name"),
                     source=b.get("source"), license=b.get("license"),
                     fetched=d["fetched"])
        if d["fetched"]:
            with d["data_file"].open(encoding="utf-8") as fh:
                entry["items"] = sum(1 for line in fh if line.strip())
        entry["weight"] = suite["weights"].get(b["id"], 1.0)
        info[b["id"]] = entry
    return info


def iter_custom_units() -> Iterator[Unit]:
    for d in discover_custom():
        yield _load_custom_unit(d)
