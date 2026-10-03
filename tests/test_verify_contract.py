"""Every shipped verify.py must accept the harness's uniform invocation.

grade_verify always runs ``verify.py --task-dir D --out-dir D --response F``.
Any argparse rejection here means grading silently scores the task zero
(the rc=2 class of bug that used to zero out every cybersecurity task), so
this contract is asserted for *every* task dir under benchmarks/, not just
the custom ones we know about.
"""
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
VERIFIES = sorted((ROOT / "benchmarks").glob("**/verify.py"))


def test_verifies_were_found():
    assert len(VERIFIES) >= 18, f"expected >=18 verifiers, found {len(VERIFIES)}"


@pytest.mark.parametrize("verify", VERIFIES, ids=[p.parent.name for p in VERIFIES])
def test_verify_accepts_uniform_invocation(verify: Path, tmp_path):
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    (out_dir / "response.txt").write_text("", encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(verify), "--task-dir", str(verify.parent),
         "--out-dir", str(out_dir), "--response",
         str(out_dir / "response.txt")],
        capture_output=True, text=True, timeout=30, cwd=tmp_path)
    if proc.returncode == 2 and "unrecognized arguments" in proc.stderr:
        pytest.fail(f"{verify.parent.name} rejects --response")


@pytest.mark.parametrize("verify", VERIFIES, ids=[p.parent.name for p in VERIFIES])
def test_every_verifier_emits_a_json_verdict(verify: Path, tmp_path):
    """With a garbage response each verify must resolve out-dir/response from
    argv (not cwd), emit {pass, detail} on stdout — never an argparse crash —
    and never just exit without a verdict line. On a fresh clone the withheld
    expected.json/key files are absent: a clean error mentioning them is a
    valid verdict-side failure, an unhandled traceback for anything else is
    not."""
    import json as _json
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    (out_dir / "response.txt").write_text("not a real answer\n", encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(verify), "--task-dir", str(verify.parent),
         "--out-dir", str(out_dir), "--response",
         str(out_dir / "response.txt")],
        capture_output=True, text=True, timeout=30, cwd=tmp_path)
    assert proc.returncode in (0, 1), proc.stderr[-300:]
    for line in reversed(proc.stdout.strip().splitlines()):
        if line.startswith("{"):
            obj = _json.loads(line)
            assert "pass" in obj and isinstance(obj["pass"], bool)
            return
    # no verdict line at all — only acceptable when the local clone is
    # missing the withheld expected/vector files, and then it must say so
    missing = ("expected.json", "vectors.json", "key.txt", "token.txt",
               "FileNotFoundError")
    assert any(m in proc.stderr + proc.stdout for m in missing), proc.stderr[-300:]
