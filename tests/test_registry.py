import json

import pytest

from localbench import registry
from localbench.config import CUSTOM_ROOT


def test_discovers_all_18_custom_tasks():
    got = registry.discover_custom()
    assert len(got) == 18
    assert len({d["ref"] for d in got}) == 18


def test_custom_benchmarks_are_the_domains():
    got = {d["benchmark"] for d in registry.discover_custom()}
    assert got == {"math", "science", "long-context",
                   "instruction-following", "agentic-coding", "cybersecurity"}


def test_every_custom_task_has_the_full_contract():
    for d in registry.discover_custom():
        for name in ("prompt.md", "verify.py", "meta.json"):
            assert (d["task_dir"] / name).is_file(), f"{d['ref']} missing {name}"


def test_tier_ordering_puts_easy_first():
    tiers = [d["tier"] for d in registry.discover_custom()]
    assert tiers == sorted(tiers)


def test_timeouts_are_derived_and_capped():
    for d in registry.discover_custom():
        assert 600 <= d["timeout"] <= 3600


def test_explicit_timeout_wins():
    assert registry._timeout_from_meta({"expected_duration": "1-3",
                                        "timeout_s": 999}) == 999


def test_load_units_custom_only():
    units = registry.load_units(benchmarks=["math"])
    assert len(units) == 3
    assert {u.benchmark for u in units} == {"math"}
    assert all(u.grader == "verify" for u in units)
    assert all(u.task_dir is not None for u in units)
    assert all(u.prompt for u in units)


def test_task_filter_by_ref():
    units = registry.load_units(benchmarks=["math"],
                                tasks=["math-arithmetic-001"])
    assert [u.ref for u in units] == ["math-arithmetic-001"]


def test_expected_counts_matches_load_units_for_custom():
    for name in ("math", "science"):
        assert registry.expected_counts([name])[name] == \
            len(registry.load_units(benchmarks=[name]))


def test_unknown_benchmark_is_reported():
    with pytest.raises(RuntimeError):
        registry.load_units(benchmarks=["nope-not-real"])


def test_fetched_benchmark_yields_items(tmp_path, monkeypatch):
    bench = tmp_path / "known" / "toy"
    (bench / "data").mkdir(parents=True)
    (bench / "bench.json").write_text(json.dumps(
        dict(id="toy", name="Toy", grader="mcq", timeout=60)))
    rows = [dict(id=f"{i:03d}", prompt=f"q{i}?", answer="A") for i in range(5)]
    (bench / "data" / "items.jsonl").write_text(
        "\n".join(json.dumps(r) for r in rows) + "\n")

    monkeypatch.setattr(registry, "KNOWN_ROOT", tmp_path / "known")
    units = registry.load_units(benchmarks=["toy"])
    assert len(units) == 5
    assert units[0].uid == "item/toy/000"
    assert units[0].grader == "mcq"

    # limit truncates in file order (the fetcher shuffles at ingest)
    assert len(registry.load_units(benchmarks=["toy"], limit=2)) == 2
    assert registry.expected_counts(["toy"], limit=2)["toy"] == 2


def test_per_item_grader_overrides_bench_grader(tmp_path, monkeypatch):
    bench = tmp_path / "known" / "mixed"
    (bench / "data").mkdir(parents=True)
    (bench / "bench.json").write_text(json.dumps(
        dict(id="mixed", name="Mixed", grader="exact")))
    rows = [dict(id="a", prompt="p", answer="B", grader="mcq"),
            dict(id="b", prompt="p", answer="yes")]
    (bench / "data" / "items.jsonl").write_text(
        "\n".join(json.dumps(r) for r in rows) + "\n")
    monkeypatch.setattr(registry, "KNOWN_ROOT", tmp_path / "known")

    graders = {u.ref: u.grader for u in registry.load_units(benchmarks=["mixed"])}
    assert graders == {"a": "mcq", "b": "exact"}


def test_custom_root_is_where_we_think_it_is():
    assert CUSTOM_ROOT.is_dir()


def test_load_units_warns_on_partially_unknown_benchmark(capsys):
    units = registry.load_units(benchmarks=["math", "nope-not-real"])
    assert units, "valid benchmarks must still load"
    assert "nope-not-real" in capsys.readouterr().err
