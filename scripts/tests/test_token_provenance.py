"""Tests for the grounded-mode token-provenance checker (W4, dr2-grounded-mode).

fable-discipline: the checker is not trusted until it has been seen to fail. The
positive fixture must pass; the negative fixture (one sourceless token) must fail.
"""
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
import check_token_provenance as p  # noqa: E402


def test_positive_fixture_passes():
    assert p.check_file(p.FIXTURES / "sample-design.md") == []


def test_negative_fixture_trips():
    violations = p.check_file(p.FIXTURES / "negative-design.md")
    assert violations and any("accent" in v for v in violations)


def test_missing_tokens_section_is_a_violation():
    f = Path(__file__).resolve().parent / "_tmp_no_tokens.md"
    f.write_text("# x\n## Identity\n- a: b\n")
    try:
        assert p.check_file(f) != []
    finally:
        f.unlink()


def test_inline_source_required(tmp_path):
    f = tmp_path / "d.md"
    f.write_text("## Tokens\n- bg: #000  source: grounding/t.md#bg\n- fg: #fff\n")
    violations = p.check_file(f)
    assert len(violations) == 1 and "fg" in violations[0]


def test_fork_source_is_valid(tmp_path):
    f = tmp_path / "d.md"
    f.write_text("## Tokens\n- primary: #5b8cff  source: fork:primary-hue\n")
    assert p.check_file(f) == []


def test_multiword_token_name_is_checked(tmp_path):
    # Codex catch #1: multi-word labels must not skip the source check.
    f = tmp_path / "d.md"
    f.write_text("## Tokens\n- spacing rhythm: 8px\n")
    violations = p.check_file(f)
    assert violations and "spacing rhythm" in violations[0]


def test_bogus_or_incidental_source_rejected(tmp_path):
    # Codex catch #2: anchorless / prose-buried / no-anchor sources are not provenance.
    cases = [
        "## Tokens\n- accent: #fff  (no source: grounding/foo)\n",   # buried in prose, trailing )
        "## Tokens\n- accent: #fff  source: grounding/noanchor\n",    # grounding ref lacks #anchor
        "## Tokens\n- accent: #fff  source: bogus:thing\n",           # not grounding/ or fork:
    ]
    for text in cases:
        f = tmp_path / "d.md"
        f.write_text(text)
        assert p.check_file(f), f"should reject: {text!r}"


def test_builtin_selftest_passes():
    assert p.selftest() == 0
