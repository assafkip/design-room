"""Tests for the anti-AI gate verifier (W3, dr2-anti-ai-gate-verify).

The pure classify() is tested without a browser (enforced / advisory / broken).
A live test runs the real eyeball gate only when eyeball + a browser are present.
"""
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
import design_room_gate_check as g  # noqa: E402


def test_classify_enforced():
    ok, status, reasons = g.classify(1, "GATE: FAIL — AI-design 100", 0, "GATE: PASS")
    assert ok and status == "enforced" and not reasons


def test_classify_advisory_when_no_browser():
    adv = "eyeball: no chromium on disk; gate is advisory (skipped)."
    ok, status, reasons = g.classify(0, adv, 0, adv)   # marker + exit 0 on BOTH runs
    assert ok and status == "advisory"


def test_classify_marker_with_nonzero_exit_is_not_advisory():
    # Codex catch: a crash that prints the marker but exits nonzero is NOT advisory.
    adv = "eyeball: no chromium on disk; gate is advisory (skipped)."
    ok, status, reasons = g.classify(2, adv, 2, adv)
    assert not ok and status == "broken"


def test_classify_broken_when_slop_passes():
    # the worst failure: slop did NOT fail the gate
    ok, status, reasons = g.classify(0, "GATE: PASS", 0, "GATE: PASS")
    assert not ok and status == "broken" and any("slop" in r for r in reasons)


def test_classify_broken_when_clean_fails():
    ok, status, reasons = g.classify(1, "GATE: FAIL", 1, "GATE: FAIL")
    assert not ok and any("clean" in r for r in reasons)


@pytest.mark.skipif(not g.SCAN.is_file(), reason="eyeball not installed in this env")
def test_live_gate_runs_or_is_advisory():
    # real run: must be enforced-and-correct OR honestly advisory, never broken.
    assert g.main() == 0
