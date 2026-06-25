"""Wiring test for the decision ledger (drd-ledger-wiring).

Codex required this: prove the scaffold init_project.py generates is a VALID ledger,
not just that the checker passes hand-made fixtures.
"""
import os
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
import check_decision_log as d  # noqa: E402

SKILL_DIR = Path(os.environ.get("DESIGN_ROOM_SKILL_DIR",
                                str(Path(__file__).resolve().parent.parent.parent / "skill"))).expanduser()
INIT = SKILL_DIR / "scripts" / "init_project.py"


@pytest.mark.skipif(not INIT.is_file(), reason="design-room skill not present in this env")
def test_scaffolded_decisions_md_is_valid(tmp_path):
    subprocess.run([sys.executable, str(INIT), "TestCo", "--path", str(tmp_path)], check=True)
    ledger = tmp_path / "design-room" / "decisions.md"
    assert ledger.is_file(), "init_project.py did not scaffold decisions.md"
    assert d.check_file(ledger) == [], f"scaffolded ledger is invalid: {d.check_file(ledger)}"


@pytest.mark.skipif(not INIT.is_file(), reason="design-room skill not present in this env")
def test_append_to_scaffold_chains(tmp_path):
    subprocess.run([sys.executable, str(INIT), "TestCo", "--path", str(tmp_path)], check=True)
    ledger = tmp_path / "design-room" / "decisions.md"
    d.append_entry(ledger, "2026-06-26", "first real call", "ship the hero serif",
                   "LENS-CITED", "canon:lindgaard-2006-50ms", "credible at a glance", "none")
    assert d.check_file(ledger) == []
