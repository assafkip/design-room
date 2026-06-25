"""Tests for the design-room conformance engine (W0, dr2-engine-lenses).

Covers the engine logic directly (assertion kinds, section slice, json_path,
fail-closed) without depending on the live skill dir, plus the built-in negative
self-test. fable-discipline: a gate is not trusted until it has been seen to fail,
so every check here has a passing AND a tripping case.
"""
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
import verify_design_room as v  # noqa: E402


def test_present_pass_and_fail():
    a = {"kind": "present", "patterns": ["(?i)hello", "world"]}
    assert v.run_assertion(a, "Hello world") == []
    fails = v.run_assertion(a, "Hello there")
    assert len(fails) == 1 and "world" in fails[0]


def test_absent_pass_and_trip():
    a = {"kind": "absent", "patterns": ["14 agents", "(?i)debate"]}
    assert v.run_assertion(a, "seven lenses") == []
    fails = v.run_assertion(a, "they debate and converge")
    assert any("debate" in f for f in fails)


def test_section_scopes_match():
    text = "## Keep\nWebFetch is fine here\n## Other\nclean\n"
    inside = {"kind": "absent", "patterns": ["WebFetch"], "section": "## Other"}
    outside = {"kind": "absent", "patterns": ["WebFetch"], "section": "## Keep"}
    assert v.run_assertion(inside, text) == []          # not in ## Other
    assert v.run_assertion(outside, text) != []         # is in ## Keep


def test_registry_ids_present_against_real_registry():
    reg = v.json_path_values(
        __import__("json").loads((v.DESIGN_ROOM / "lens-registry.json").read_text()),
        "lenses[].id",
    )
    assert len(reg) == 7  # the 7 lenses, no more no less
    good = " ".join(reg)
    a = {"kind": "registry_ids_present", "registry": "lens-registry.json", "json_path": "lenses[].id"}
    assert v.run_assertion(a, good) == []
    missing = v.run_assertion(a, reg[0])  # only the first id present
    assert len(missing) == 6


def test_scoped_assertion_fails_closed_on_missing_section():
    # Codex catch #2: a missing section must NOT let `absent` pass vacuously.
    a = {"kind": "absent", "patterns": ["WebFetch"], "section": "## Nope"}
    fails = v.run_assertion(a, "## Real\nWebFetch\n")
    assert fails and "missing" in fails[0].lower()


def test_slice_section_returns_none_when_absent():
    assert v.slice_section("## A\nx\n", "## Missing") is None


def test_registry_id_word_boundary():
    # Codex catch #3: 'anti-slop' must not be satisfied by 'anti-sloppy'.
    a = {"kind": "registry_ids_present", "registry": "lens-registry.json", "json_path": "lenses[].id"}
    ids = v.json_path_values(
        __import__("json").loads((v.DESIGN_ROOM / "lens-registry.json").read_text()),
        "lenses[].id",
    )
    near = " ".join(x if x != "anti-slop" else "anti-sloppy" for x in ids)
    fails = v.run_assertion(a, near)
    assert any("anti-slop" in f for f in fails)


def test_snapshot_check_symmetric(tmp_path, monkeypatch):
    # Codex catch #1: a baseline file with no live counterpart must trip --check.
    sdir = tmp_path / "skill"
    (sdir / "references").mkdir(parents=True)
    (sdir / "SKILL.md").write_text("live skill")
    (sdir / "references" / "a.md").write_text("ref a")
    baseline = tmp_path / "baseline" / "live"
    monkeypatch.setenv("DESIGN_ROOM_SKILL_DIR", str(sdir))
    monkeypatch.setattr(v, "BASELINE_DIR", baseline)
    assert v.snapshot(check=False) == 0          # write baseline
    assert v.snapshot(check=True) == 0           # matches
    (sdir / "SKILL.md").unlink()                  # live loses a tracked file
    assert v.snapshot(check=True) != 0            # must NOT false-green


def test_json_path_values():
    obj = {"lenses": [{"id": "a"}, {"id": "b"}]}
    assert v.json_path_values(obj, "lenses[].id") == ["a", "b"]


def test_slice_section_bounds():
    text = "## A\nkeep1\nkeep2\n## B\ndrop\n"
    s = v.slice_section(text, "## A")
    assert "keep1" in s and "keep2" in s and "drop" not in s


def test_read_target_fails_closed(tmp_path):
    with pytest.raises(v.FailClosed):
        v.read_target(tmp_path / "nope", "SKILL.md")          # dir absent
    with pytest.raises(v.FailClosed):
        v.read_target(tmp_path, "SKILL.md")                    # file absent


def test_builtin_selftest_passes():
    assert v.selftest() == 0


def test_registry_has_exactly_seven_lenses_with_valid_source():
    import json
    reg = json.loads((v.DESIGN_ROOM / "lens-registry.json").read_text())
    lenses = reg["lenses"]
    assert len(lenses) == 7
    valid = {"cited", "fork", "grounded", "gate"}
    for lens in lenses:
        assert lens["source"] in valid
        # cited lenses must name at least one canon ref; forks/gate need not
        if lens["source"] == "cited":
            assert lens["canon_refs"], f"{lens['id']} is cited but names no canon_refs"
