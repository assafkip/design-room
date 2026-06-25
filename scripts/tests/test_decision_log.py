"""Tests for the decision-ledger checker (drd-ledger-checker).

The ledger's promise is "append-only, never rewritten." These prove the checker
actually enforces that (tamper-evident chain) plus per-entry provenance — not just
that a good file passes.
"""
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
import check_decision_log as d  # noqa: E402

FIX = SCRIPTS.parent / "design-room" / "fixtures" / "decisions"


def test_sample_fixture_passes():
    assert d.check_file(FIX / "sample-decisions.md") == []


def test_tampered_prior_entry_breaks_chain():
    v = d.check_file(FIX / "negative-broken-chain.md")
    assert v and any("chain" in x for x in v)


def test_builtin_selftest_passes():
    assert d.selftest() == 0


def test_slug_is_kebab():
    assert d.slug("Serif Over Sans!") == "serif-over-sans"


def test_hash_is_deterministic_and_sensitive():
    a = "## x\n- **Decision:** one"
    assert d.hash_entry(a) == d.hash_entry(a + "\n")          # trailing ws normalized
    assert d.hash_entry(a) != d.hash_entry(a.replace("one", "two"))


def test_append_chains_and_validates(tmp_path):
    f = tmp_path / "decisions.md"
    f.write_text("# Decisions\n")
    d.append_entry(f, "2026-06-18", "first pick", "do A",
                   "FOUNDER-DECIDED", "founder", "gut", "none")
    d.append_entry(f, "2026-06-25", "second pick", "do B",
                   "FORK-RESOLVED", "fork:b", "founder picked B", "2026-06-18-first-pick")
    assert d.check_file(f) == []


def test_fake_canon_id_rejected(tmp_path):
    f = tmp_path / "decisions.md"
    f.write_text("# D\n")
    d.append_entry(f, "2026-06-25", "x", "do x",
                   "LENS-CITED", "canon:not-real", "because", "none")
    v = d.check_file(f)
    assert v and any("canon id" in x for x in v)


def test_head_pin_detects_rewrite(tmp_path):
    # Codex blocker: with a pinned head, a full rewrite is detectable.
    f = tmp_path / "decisions.md"
    f.write_text("# D\n")
    d.append_entry(f, "2026-06-18", "a", "do a", "FOUNDER-DECIDED", "founder", "gut", "none")
    head = d.hash_entry(d.split_entries(f.read_text())[-1])
    assert d.check_file(f, head=head) == []                       # honest head passes
    f.write_text(f.read_text().replace("do a", "do something else"))
    assert d.check_file(f, head=head) != []                       # rewrite caught by the pin


def test_grounded_ref_resolves_against_project(tmp_path):
    # Codex: provenance resolves when the project siblings exist.
    root = tmp_path
    (root / "grounding").mkdir()
    f = root / "decisions.md"
    f.write_text("# D\n")
    d.append_entry(f, "2026-06-25", "g", "use teardown token",
                   "GROUNDED", "grounding/tokens.md", "from the teardown", "none")
    assert d.check_file(f) != []                                  # grounding/tokens.md missing -> fail
    (root / "grounding" / "tokens.md").write_text("bg: #000")
    assert d.check_file(f) == []                                  # now it resolves


def test_duplicate_why_line_rejected(tmp_path):
    f = tmp_path / "decisions.md"
    f.write_text("# D\n")
    d.append_entry(f, "2026-06-25", "x", "do x", "FOUNDER-DECIDED", "founder", "a", "none")
    f.write_text(f.read_text().replace(
        "- **Supersedes:** none",
        "- **Why:** [FORK-RESOLVED fork:y] second\n- **Supersedes:** none", 1))
    v = d.check_file(f)
    assert v and any("Why" in x for x in v)
