from localbench.scoring import latest_run_per_model, score, select


def rec(model, uid, bench, passed, suite="known", run="r1", **kw):
    d = dict(run_id=run, model=model, model_slug=model, uid=uid,
             benchmark=bench, suite=suite, pass_=passed, timed_out=False)
    d.update(kw)
    return d


def test_accuracy_is_passed_over_attempted():
    rows = [rec("m", "a", "math-500", True),
            rec("m", "b", "math-500", False),
            rec("m", "c", "math-500", True)]
    out = score(rows, weights={}, expected={})
    b = out["models"]["m"]["benchmarks"]["math-500"]
    assert (b["passed"], b["attempted"]) == (2, 3)
    assert abs(b["accuracy"] - 66.67) < 0.01


def test_suite_score_is_the_weighted_mean():
    rows = [
        rec("m", "1", "easy", True), rec("m", "2", "easy", True),   # 100%
        rec("m", "3", "hard", False), rec("m", "4", "hard", False),  # 0%
    ]
    out = score(rows, weights={"easy": 3.0, "hard": 1.0}, expected={})
    # (3*1.0 + 1*0.0) / 4 = 75
    assert out["models"]["m"]["suite_score"] == 75.0


def test_unweighted_defaults_to_one():
    rows = [rec("m", "1", "a", True), rec("m", "2", "b", False)]
    out = score(rows, weights={}, expected={})
    assert out["models"]["m"]["suite_score"] == 50.0


def test_benchmark_with_no_attempts_is_excluded_from_the_score():
    rows = [rec("m", "1", "ran", True)]
    out = score(rows, weights={"ran": 1.0, "never": 99.0}, expected={})
    assert out["models"]["m"]["suite_score"] == 100.0
    assert "never" not in out["models"]["m"]["benchmarks"]


def test_partial_benchmark_is_flagged():
    rows = [rec("m", "1", "bench", True)]
    out = score(rows, weights={}, expected={"bench": 10})
    b = out["models"]["m"]["benchmarks"]["bench"]
    assert b["status"] == "partial" and b["expected"] == 10


def test_by_suite_subtotals():
    rows = [rec("m", "1", "math", True, suite="custom"),
            rec("m", "2", "bbh", False, suite="known")]
    out = score(rows, weights={}, expected={})
    assert out["models"]["m"]["by_suite"] == {"custom": 100.0, "known": 0.0}


def test_endpoint_failure_is_not_a_scored_unit():
    rows = [dict(run_id="r1", model="m", model_slug="m", uid=None,
                 endpoint_failed=True, pass_=False, detail="boom"),
            rec("m", "1", "a", True)]
    out = score(rows, weights={}, expected={})
    m = out["models"]["m"]
    assert m["endpoint_error"] == "boom"
    assert m["suite_score"] == 100.0
    assert m["benchmarks"]["a"]["attempted"] == 1


def test_select_dedupes_last_record_wins():
    rows = [rec("m", "u", "b", False), rec("m", "u", "b", True)]
    assert [r["pass_"] for r in select(rows, all_runs=True)] == [True]


def test_select_defaults_to_latest_run_per_model():
    rows = [rec("m", "u", "b", False, run="r1"),
            rec("m", "u", "b", True, run="r2")]
    assert [r["run_id"] for r in select(rows)] == ["r2"]


def test_select_run_filter_and_benchmark_filter():
    rows = [rec("m", "u", "b", True, run="r1"),
            rec("m", "u", "c", True, run="r1")]
    assert len(select(rows, run="r1", benchmarks=["b"])) == 1
    assert select(rows, run="nope") == []


def test_latest_run_per_model_spans_models():
    rows = [rec("a", "u", "b", True, run="r1"),
            rec("b", "u", "b", True, run="r2")]
    assert latest_run_per_model(rows) == {"a": "r1", "b": "r2"}


def test_select_defaults_to_newest_run_per_model_benchmark():
    # run r2 has a newer math result for m, but m's code numbers only exist
    # in r1 — selection must keep r1's code rows, not drop the whole run
    rows = [rec("m", "u1", "math", False, run="r1"),
            rec("m", "u2", "code", True, run="r1"),
            rec("m", "u1", "math", True, run="r2"),
            rec("n", "u1", "math", True, run="r1")]
    sel = select(rows)
    assert sorted((r["benchmark"], r["run_id"]) for r in sel) == [
        ("code", "r1"), ("math", "r1"), ("math", "r2")]


def test_select_falls_back_to_per_model_for_records_without_benchmark():
    rows = [rec("m", "u", "b", False, run="r1"),
            dict(run_id="r2", model="m", model_slug="m", uid=None,
                 endpoint_failed=True, pass_=False, detail="boom")]
    # r1's unit row is kept via the per-(model, benchmark) rule, and the
    # benchmark-less endpoint-failure row via the per-model rule — dropping
    # it would silently hide that the endpoint never came up
    assert sorted(r["run_id"] for r in select(rows)) == ["r1", "r2"]
    assert {r["run_id"] for r in select(rows, all_runs=True)} == {"r1", "r2"}


def test_models_are_ranked_by_suite_score():
    rows = [rec("top", "1", "b", True), rec("top", "2", "b", True),
            rec("bot", "1", "b", False), rec("bot", "2", "b", True)]
    assert score(rows, weights={}, expected={})["order"] == ["top", "bot"]


def test_newest_run_prefers_wall_clock_over_lexicographic_id():
    from localbench.scoring import latest_run_per_model_benchmark
    rows = [dict(run_id="r9", model_slug="m", benchmark="b", ts="2026-10-01T00:00:00"),
            dict(run_id="r10", model_slug="m", benchmark="b", ts="2026-10-02T00:00:00")]
    assert latest_run_per_model_benchmark(rows) == {("m", "b"): "r10"}
    assert [r["run_id"] for r in select(rows)] == ["r10"]
