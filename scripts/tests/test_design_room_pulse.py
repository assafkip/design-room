"""Tests for the weekly modernity pulse (W2, dr2-modernity-pulse).

fable-discipline: prove the evaluate path both promotes AND rejects, and that
rejected trends are kept with reasons (never silently dropped).
"""
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
import design_room_pulse as dp  # noqa: E402


def test_promote_clean_candidate():
    decision, reason = dp.evaluate(
        {"repo": "a/b", "stars": 9000, "category": "spec"}, existing_repos=set())
    assert decision == "promote"


def test_reject_trend_noise():
    decision, reason = dp.evaluate(
        {"repo": "a/b", "stars": 9000, "category": "spec", "trend_noise": True}, set())
    assert decision == "reject" and "trend-noise" in reason


def test_reject_too_niche():
    decision, reason = dp.evaluate({"repo": "a/b", "stars": 50, "category": "x"}, set())
    assert decision == "reject" and "niche" in reason


def test_reject_duplicate():
    decision, reason = dp.evaluate(
        {"repo": "a/b", "stars": 9000, "category": "x"}, existing_repos={"a/b"})
    assert decision == "reject" and "already" in reason


def test_reject_no_category():
    decision, reason = dp.evaluate({"repo": "a/b", "stars": 9000, "category": ""}, set())
    assert decision == "reject" and "category" in reason


def test_run_writes_dated_snapshot_and_keeps_rejections(tmp_path):
    candidates = dp._load_candidates(dp.PULSE_DIR / "_fixture-candidates.json")
    palette = tmp_path / "p.md"
    palette.write_text("# P\nLast refreshed: 2000-01-01\n"
                       "[lenis](https://github.com/darkroomengineering/lenis)\n")
    snap = dp.run(candidates, "2026-06-25", palette, tmp_path / "pulse")
    assert (tmp_path / "pulse" / "snapshot-2026-06-25.json").is_file()
    assert snap["promoted"] and snap["rejected"]
    assert all(r["reason"] for r in snap["rejected"])          # every rejection has a reason
    assert "Last refreshed: 2026-06-25" in palette.read_text()  # date bumped


def test_rerun_does_not_re_promote(tmp_path):
    # Codex catch: a repo promoted last run must be rejected as duplicate next run.
    palette = tmp_path / "p.md"
    palette.write_text("# P\nLast refreshed: 2000-01-01\n")
    cand = [{"repo": "new/repo", "stars": 9000, "category": "spec"}]
    first = dp.run(cand, "2026-06-25", palette, tmp_path / "pulse")
    assert len(first["promoted"]) == 1
    second = dp.run(cand, "2026-07-02", palette, tmp_path / "pulse")
    assert not second["promoted"]
    assert any("already" in r["reason"] for r in second["rejected"])


def test_date_bump_flag_false_when_no_line(tmp_path):
    # Codex catch: missing date line must be signalled, not silently passed.
    palette = tmp_path / "p.md"
    palette.write_text("# P\n(no refresh line here)\n")
    snap = dp.run([{"repo": "a/b", "stars": 9000, "category": "x"}], "2026-06-25",
                  palette, tmp_path / "pulse")
    assert snap["palette_date_bumped"] is False


def test_builtin_selftest_passes():
    assert dp.selftest() == 0
