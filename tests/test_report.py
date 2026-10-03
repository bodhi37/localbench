import json

from localbench import scoring, report


def _rows():
    n = [0]

    def r(slug, name, bench, suite, passed, run="r2", expected=4, **kw):
        n[0] += 1
        d = dict(run_id=run, model=name, model_slug=slug, uid=f"{bench}/u{n[0]}",
                 benchmark=bench, suite=suite, grader="mcq",
                 pass_=passed, timed_out=False, expected=expected)
        d.update(kw)
        return d
    return [
        # model "top": two runs — the newest (r2) must win
        r("top", "Top Model", "math", "custom", True, run="r1", expected=3),
        r("top", "Top Model", "math", "custom", True, expected=3),
        r("top", "Top Model", "math", "custom", True, expected=3),
        r("top", "Top Model", "math", "custom", False, expected=3),
        r("top", "Top Model", "bbh", "known", True, expected=4),
        r("top", "Top Model", "bbh", "known", True, expected=4),
        # model "bot": older run partly better, newest run scores zero
        r("bot", "Weak Model", "math", "custom", True, run="r1", expected=3),
        r("bot", "Weak Model", "math", "custom", True, run="r1", expected=3),
        r("bot", "Weak Model", "math", "custom", False, expected=3),
        r("bot", "Weak Model", "math", "custom", False, expected=3),
        dict(run_id="r2", model="Weak Model", model_slug="bot", uid=None,
             endpoint_failed=True, pass_=False, detail="port in use"),
    ]


def test_scoring_uses_newest_run_per_model():
    out = scoring.score(scoring.select(_rows()), weights={"math": 1.0, "bbh": 1.0},
                        expected={})
    m = out["models"]["top"]
    assert m["benchmarks"]["math"]["attempted"] == 3   # r2 rows only
    assert m["benchmarks"]["math"]["passed"] == 2


def test_partial_flag_uses_the_denominator_stamped_on_the_run():
    rows = [dict(run_id="r2", model="m", model_slug="m", uid="x/1",
                 benchmark="bbh", suite="known", pass_=True, timed_out=False,
                 expected=9)]
    out = scoring.score(rows, weights={}, expected={})
    b = out["models"]["m"]["benchmarks"]["bbh"]
    assert b["status"] == "partial" and b["expected"] == 9


def test_suite_score_and_ranking():
    out = scoring.score(scoring.select(_rows()),
                        weights={"math": 1.0, "bbh": 2.0}, expected={})
    assert out["order"][0] == "top"
    assert out["models"]["bot"]["endpoint_error"] == "port in use"
    assert out["models"]["top"]["by_suite"] == {"custom": 66.67, "known": 100.0}


def test_report_renders_without_crashing(tmp_path, monkeypatch):
    monkeypatch.setattr(scoring, "RESULTS_JSONL", tmp_path / "r.jsonl")
    rows = _rows()
    (tmp_path / "r.jsonl").write_text("\n".join(json.dumps(x) for x in rows))
    sel = scoring.load_records(tmp_path / "r.jsonl")
    structure = scoring.score(scoring.select(sel),
                              weights={"math": 1.0, "bbh": 2.0}, expected={})
    structure.update(run="r2", runs_available=["r1", "r2"],
                     selected_records=len(sel))
    md = report.build_report(structure, info={
        "math": {"suite": "custom"}, "bbh": {"suite": "known"}})
    assert "# localbench report" in md
    assert "Top Model" in md and "Weak Model" in md
    assert "SUITE SCORE" not in md          # headline table wording
    assert "math" in md and "bbh" in md


def test_report_with_no_results(tmp_path):
    structure = dict(models={}, order=[], weights={}, expected={},
                     run="none", runs_available=[], selected_records=0)
    md = report.build_report(structure)
    assert "No results yet" in md
