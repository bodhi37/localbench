"""Turn raw result rows into per-benchmark accuracies and a suite score.

Scoring rules (all visible, no hidden math):

  accuracy(benchmark)  = passed / attempted           on the units actually run
  suite score          = sum(weight_b * accuracy_b) / sum(weight_b)
                         over every benchmark with at least one attempt
  weights              = config/suite.json["weights"]  (missing key -> 1.0)

A benchmark whose attempted count is below the number of units it was selected
with is flagged ``partial`` rather than silently scored as if complete.
"""
from __future__ import annotations

import json
from typing import Optional

from .config import RESULTS_JSONL, load_suite
from .registry import expected_counts


def load_records(path=None) -> list[dict]:
    p = path or RESULTS_JSONL
    if not p.is_file():
        return []
    rows = []
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def available_runs(records: list[dict]) -> list[str]:
    return sorted({r["run_id"] for r in records if r.get("run_id")})


def _newest_key(r: dict) -> tuple:
    """Ordering key for "newest run": wall-clock first, run_id as tiebreak.

    Runner-generated ids (``%Y%m%d-%H%M%S``) already sort chronologically, but
    hand-named ``--run-id`` values (``r9`` vs ``r10``) do not sort
    lexicographically — every record carries a ``ts`` stamp, so time wins
    and the id only breaks ties.
    """
    return (r.get("ts") or "", r.get("run_id") or "")


def latest_run_per_model(records: list[dict]) -> dict[str, str]:
    """model_slug -> newest run_id that contains it."""
    best: dict[str, tuple] = {}
    out: dict[str, str] = {}
    for r in records:
        slug, rid = r.get("model_slug"), r.get("run_id")
        if not slug or not rid:
            continue
        k = _newest_key(r)
        if slug not in best or k > best[slug]:
            best[slug] = k
            out[slug] = rid
    return out


def latest_run_per_model_benchmark(records: list[dict]) -> dict[tuple, str]:
    """(model_slug, benchmark) -> newest run_id containing that pair.

    Run selection must be per *benchmark*, not per model: a model that ran
    math in run A and code in run B needs A's math numbers and B's code
    numbers. The old per-model rule silently dropped every record from the
    older run and under-scored multi-run models.
    """
    out: dict[tuple, str] = {}
    best: dict[tuple, tuple] = {}
    for r in records:
        slug, rid, bench = r.get("model_slug"), r.get("run_id"), r.get("benchmark")
        if not slug or not rid or not bench:
            continue
        key = (slug, bench)
        k = _newest_key(r)
        if key not in best or k > best[key]:
            best[key] = k
            out[key] = rid
    return out


def select(records: list[dict], run: Optional[str] = None,
           models: Optional[list[str]] = None,
           benchmarks: Optional[list[str]] = None,
           all_runs: bool = False) -> list[dict]:
    """Filter + de-duplicate (last record per (model, uid) wins)."""
    rows = records
    if run:
        rows = [r for r in rows if r.get("run_id") == run]
    elif not all_runs:
        by_pair = latest_run_per_model_benchmark(rows)
        by_model = latest_run_per_model(rows)   # records lacking 'benchmark'
        def _kept(r: dict) -> bool:
            slug, rid, bench = (r.get("model_slug"), r.get("run_id"),
                                r.get("benchmark"))
            if not rid:
                return False
            if bench:
                return by_pair.get((slug, bench)) == rid
            return by_model.get(slug) == rid
        rows = [r for r in rows if _kept(r)]
    if models:
        keep = set(models)
        rows = [r for r in rows if r.get("model_slug") in keep
                or r.get("model") in keep]
    if benchmarks:
        keep_b = set(benchmarks)
        rows = [r for r in rows if r.get("benchmark") in keep_b]

    dedup: dict[tuple, dict] = {}
    for r in rows:
        key = (r.get("model_slug"), r.get("uid") or r.get("task"))
        dedup[key] = r
    return list(dedup.values())


def _pct(x: Optional[float]) -> Optional[float]:
    return None if x is None else round(100.0 * x, 2)


def score(records: list[dict], weights: Optional[dict] = None,
          expected: Optional[dict] = None,
          benchmarks: Optional[list[str]] = None,
          limit: int = 0) -> dict:
    """Aggregate selected records into the full scoring structure."""
    suite = load_suite()
    weights = weights if weights is not None else suite["weights"]
    if expected is None:
        try:
            expected = expected_counts(benchmarks, limit)
        except Exception:
            expected = {}

    models: dict[str, dict] = {}
    for r in records:
        if not r.get("uid") and not r.get("task"):
            # endpoint never came up — record it, it is not a scored unit
            m = models.setdefault(r.get("model_slug", "?"), {
                "name": r.get("model", "?"), "benchmarks": {},
                "endpoint_error": r.get("detail", "")})
            m["endpoint_error"] = r.get("detail", "")
            continue
        m = models.setdefault(r.get("model_slug", "?"), {
            "name": r.get("model", "?"), "benchmarks": {}})
        b = m["benchmarks"].setdefault(
            r.get("benchmark", "?"),
            {"attempted": 0, "passed": 0, "timeouts": 0, "suite": r.get("suite", "?")})
        b["attempted"] += 1
        if r.get("pass_"):
            b["passed"] += 1
        if r.get("timed_out"):
            b["timeouts"] += 1
        if isinstance(r.get("expected"), int) and r["expected"] > 0:
            b["expected"] = max(b.get("expected", 0), r["expected"])

    for m in models.values():
        total_w = 0.0
        total = 0.0
        scored = []
        for name, b in sorted(m["benchmarks"].items()):
            if not b["attempted"]:
                continue
            acc = b["passed"] / b["attempted"]
            w = float(weights.get(name, 1.0))
            # prefer the denominator the run itself stamped on its records
            want = b.get("expected") or expected.get(name)
            status = "ok"
            if want and b["attempted"] < want:
                status = "partial"
            b.update(accuracy=_pct(acc), accuracy_raw=acc, weight=w,
                     status=status, expected=want)
            total += w * acc
            total_w += w
            scored.append(name)
        m["scored_benchmarks"] = scored
        m["suite_score"] = _pct(total / total_w) if total_w else None
        m["weights_sum"] = round(total_w, 3)
        # subtotals per source suite
        for src in ("custom", "known"):
            bs = [b for b in m["benchmarks"].values()
                  if b.get("suite") == src and b.get("attempted")]
            if bs:
                num = sum(b["weight"] * b["accuracy_raw"] for b in bs)
                den = sum(b["weight"] for b in bs)
                m.setdefault("by_suite", {})[src] = _pct(num / den)

    ranked = sorted(models.items(),
                    key=lambda kv: (kv[1].get("suite_score") is not None,
                                    kv[1].get("suite_score") or -1),
                    reverse=True)
    denom = {name: b.get("expected")
             for m in models.values()
             for name, b in m["benchmarks"].items()
             if b.get("expected")}
    return {
        "weights": weights,
        # denominator each benchmark's `attempted` was compared against —
        # what the run stamped on its records, not the full dataset size
        "denominators": dict(sorted(denom.items())),
        "models": dict(ranked),
        "order": [k for k, _ in ranked],
    }


def score_structure(run: Optional[str] = None, models: Optional[list[str]] = None,
                    benchmarks: Optional[list[str]] = None,
                    all_runs: bool = False, limit: int = 0) -> dict:
    records = load_records()
    sel = select(records, run=run, models=models, benchmarks=benchmarks,
                 all_runs=all_runs)
    out = score(sel, benchmarks=benchmarks, limit=limit)
    out["run"] = run or ("all" if all_runs else "latest-per-model-benchmark")
    out["runs_available"] = available_runs(records)
    out["selected_records"] = len(sel)
    return out