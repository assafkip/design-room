"""Tests for the freshness sweep (drf-freshness-sweep): old-model drift guard.

Codex hardened this: it's not enough to trip on one string. Prove EVERY banned
phrase trips, the current live skill is clean, the 'lenses, not personas'
disclaimer does NOT false-trip, and coverage spans every SNAPSHOT_GLOB.
"""
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
import verify_design_room as v  # noqa: E402

# One real old-model phrase per banned pattern, aligned by index.
EXAMPLES = [
    "they research, debate, and converge on it",   # research,? debate,? and converge
    "the room debates the palette",                 # the room debates
    "the room's converged decision",                # the room('s)? converg
    "the converged decision is written here",       # converged decision
    "every research persona reads the brief",       # research personas?
    "runs before persona research begins",          # persona research
    "spin up the personas to launch agents",        # spin up ... personas
    "read the persona brain file first",            # persona brain file
    "customize persona files for your industry",    # customize persona files
    "14 specialized personas debate",               # 14 (specialized )?(agents|personas)
]


def test_examples_aligned_to_patterns():
    assert len(EXAMPLES) == len(v.BANNED_OLD_MODEL)


def test_every_banned_phrase_trips_its_pattern():
    for pat, ex in zip(v.BANNED_OLD_MODEL, EXAMPLES):
        hits = v.sweep_text(ex)
        assert pat in hits, f"pattern {pat!r} did not trip on {ex!r} (got {hits})"


def test_disclaimer_does_not_false_trip():
    disclaimer = ("design-room v2 — lenses, not personas. "
                  "No personas/, no research/ -- those were the old debate model.")
    assert v.sweep_text(disclaimer) == []


def test_clean_text_is_clean():
    assert v.sweep_text("The lenses cite the canon; the founder resolves each fork.") == []


@pytest.mark.skipif(not v.skill_dir().is_dir(), reason="live skill not present in this env")
def test_live_skill_is_clean():
    assert v.freshness() == 0


def test_coverage_spans_every_snapshot_glob(tmp_path, monkeypatch):
    # a file under EACH glob carrying a banned phrase must be swept -> caught.
    sdir = tmp_path / "skill"
    (sdir / "references").mkdir(parents=True)
    (sdir / "scripts").mkdir()
    (sdir / "SKILL.md").write_text("the room debates")
    (sdir / "references" / "x.md").write_text("persona research here")
    (sdir / "scripts" / "y.py").write_text("# spin up the personas\n")
    monkeypatch.setenv("DESIGN_ROOM_SKILL_DIR", str(sdir))
    files = v._snapshot_files(sdir)
    assert len(files) == 3                      # one per glob
    assert v.freshness() == 1                   # all three drifted files caught


def test_fails_closed_when_skill_absent(tmp_path, monkeypatch):
    monkeypatch.setenv("DESIGN_ROOM_SKILL_DIR", str(tmp_path / "nope"))
    assert v.freshness() == 2


def test_newline_wrapped_phrase_trips(tmp_path):
    # Codex: DOTALL so a phrase wrapped across lines still trips.
    assert v.sweep_text("we spin up the\npersonas here") != []


def test_14_persona_variants_trip():
    # Codex: broadened to catch hyphen + qualifier forms.
    for s in ["the 14-persona table", "14 design-room personas", "14 agents"]:
        assert v.sweep_text(s) != [], f"missed: {s!r}"


def test_recursive_glob_sweeps_nested(tmp_path, monkeypatch):
    # Codex: a reintroduced nested skill file must be swept.
    sdir = tmp_path / "skill"
    (sdir / "references" / "persona-templates").mkdir(parents=True)
    (sdir / "SKILL.md").write_text("clean")
    (sdir / "references" / "persona-templates" / "maya.md").write_text("the room debates")
    monkeypatch.setenv("DESIGN_ROOM_SKILL_DIR", str(sdir))
    assert any("persona-templates" in str(f) for f in v._snapshot_files(sdir))
    assert v.freshness() == 1
