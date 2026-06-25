#!/usr/bin/env python3
"""Generic conformance engine for the design-room skill.

Why this exists: the design-room skill is a set of markdown files (`skill/SKILL.md`
+ `skill/references/`). This engine is the deterministic proof that the skill
conforms to the committed contracts under `design-room/contracts/`. It reads the
ACTUALLY-LOADED skill copy at `$DESIGN_ROOM_SKILL_DIR` (default: the in-repo
`skill/` dir) — a grep of a separate copy proves nothing — and it FAILS CLOSED: if
the skill dir is absent it exits non-zero, never a silent skip that lets a check
pass without proving anything.

The engine is generic: it auto-discovers `contracts/*.json` and runs each
contract's declarative assertions, so a new check is usually just a JSON contract,
no Python. Assertion kinds: present / absent / registry_ids_present (+ an optional
`section` slice). See design-room/contracts/README.md.

fable-discipline: a passing gate is not trusted until it has been seen to fail.
`--selftest` builds a GOOD in-memory target (passes) and a BAD one (missing a
required id, carries a banned phrase) that MUST trip the engine; exit 2 if the
engine itself is broken.

Subcommands:
  conform [--only NAME]   assert the live skill against every (or one) contract
  snapshot [--check]      copy edited skill files to the committed baseline /
                          verify the baseline matches the live skill
  --selftest              negative self-test (no skill files needed)

Exit 0 = pass. Exit 1 = a conformance check failed. Exit 2 = engine broken or
fail-closed (skill dir absent / self-test failed). Don't trust a 2.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent          # scripts
GTM = SCRIPTS.parent                                 # gtm
REPO = GTM.parent                                    # repo root
DESIGN_ROOM = GTM / "design-room"
CONTRACTS_DIR = DESIGN_ROOM / "contracts"
BASELINE_DIR = DESIGN_ROOM / "skill-baseline" / "live"

DEFAULT_SKILL_DIR = (Path(__file__).resolve().parent.parent / "skill")

# Files the snapshot tracks (the review + rollback anchor): SKILL.md, the reference
# markdown, AND the project scaffolder. (scripts/init_project.py is a real skill
# file the v2 work edited; leaving it out meant the rollback anchor was incomplete.)
# Recursive so a reintroduced nested path (e.g. references/persona-templates/*.md)
# is also captured by snapshot AND swept by freshness (Codex: flat globs missed nesting).
SNAPSHOT_GLOBS = ("SKILL.md", "references/**/*.md", "scripts/**/*.py")

# Old-model (14-persona-debate) phrases the v2 cut removed. The `freshness` check
# sweeps EVERY SNAPSHOT_GLOBS file for these so the cut can't silently regress.
# Phrasings (not bare words) so "lenses, not personas" disclaimers don't false-trip.
# Even a prohibitive quote of a dead phrase is banned — describe what NOT to do
# without quoting it.
BANNED_OLD_MODEL = (
    r"research,?\s+debate,?\s+and\s+converge",
    r"the\s+room\s+debates",
    r"the\s+room('s)?\s+converg",          # the room converges / the room's converged
    r"converged\s+decision",                # Codex blocker: design-md-template drift
    r"research\s+personas?",
    r"persona\s+research",
    r"spin\s+up\b.{0,30}personas",
    r"persona\s+brain\s+file",
    r"customize\s+persona\s+files",
    r"14[\s-](specialized\s+|design-room\s+)?(agent|persona)s?",  # 14 agents / 14-persona table / 14 design-room personas
)


class FailClosed(Exception):
    """Raised when the engine cannot prove conformance (missing skill/dir/file)."""


def skill_dir() -> Path:
    raw = os.environ.get("DESIGN_ROOM_SKILL_DIR")
    return Path(raw).expanduser() if raw else DEFAULT_SKILL_DIR


# ── target reading (fail closed) ─────────────────────────────────────────────
def read_target(sdir: Path, rel: str) -> str:
    if not sdir.is_dir():
        raise FailClosed(
            f"skill dir absent: {sdir} (set DESIGN_ROOM_SKILL_DIR). "
            "Refusing to pass without reading the live skill."
        )
    target = sdir / rel
    if not target.is_file():
        raise FailClosed(f"target file missing in live skill: {rel} (under {sdir})")
    return target.read_text(encoding="utf-8")


# ── markdown section slice ───────────────────────────────────────────────────
def slice_section(text: str, heading: str):
    """Return the body under a markdown `heading` up to the next same/higher
    heading, or None if the heading is absent. Returning None lets the caller
    FAIL CLOSED on a scoped assertion whose section was renamed/removed — an
    empty-string scope would silently pass `absent` checks (false green)."""
    level = len(heading) - len(heading.lstrip("#"))
    lines = text.splitlines()
    out: list[str] = []
    capturing = False
    found = False
    for line in lines:
        stripped = line.strip()
        is_heading = stripped.startswith("#")
        if not capturing:
            if stripped == heading.strip():
                capturing = True
                found = True
            continue
        if is_heading:
            this_level = len(stripped) - len(stripped.lstrip("#"))
            if this_level <= level:
                break
        out.append(line)
    return "\n".join(out) if found else None


# ── json_path: "lenses[].id" -> list of values ───────────────────────────────
def json_path_values(obj, path: str) -> list:
    tokens = path.split(".")

    def walk(node, toks):
        if not toks:
            return [node]
        tok, rest = toks[0], toks[1:]
        if tok.endswith("[]"):
            key = tok[:-2]
            seq = node[key] if key else node
            results = []
            for item in seq:
                results.extend(walk(item, rest))
            return results
        return walk(node[tok], rest)

    return walk(obj, tokens)


# ── assertion runner ─────────────────────────────────────────────────────────
def run_assertion(assertion: dict, target_text: str) -> list[str]:
    """Return a list of human-readable failure strings ([] = pass)."""
    kind = assertion.get("kind")
    section = assertion.get("section")
    where = f" in section {section!r}" if section else ""
    # Fail closed on a renamed/removed section: an empty scope would let an
    # `absent` assertion pass vacuously (false green). A scoped assertion whose
    # section is missing is a violation, not a pass.
    if section:
        scope = slice_section(target_text, section)
        if scope is None:
            return [f"required section missing: {section!r}"]
    else:
        scope = target_text
    fails: list[str] = []

    if kind == "present":
        for pat in assertion["patterns"]:
            if not re.search(pat, scope):
                fails.append(f"missing required pattern{where}: /{pat}/")
    elif kind == "absent":
        for pat in assertion["patterns"]:
            if re.search(pat, scope):
                fails.append(f"banned pattern present{where}: /{pat}/")
    elif kind == "registry_ids_present":
        reg_path = DESIGN_ROOM / assertion["registry"]
        try:
            reg = json.loads(reg_path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return [f"registry not found: {assertion['registry']}"]
        values = json_path_values(reg, assertion["json_path"])
        if not values:
            return [f"registry json_path matched nothing: {assertion['json_path']}"]
        for val in values:
            # word-boundary match: 'anti-slop' must not be satisfied by
            # 'anti-sloppy'. \b around a hyphenated id holds (hyphen is non-word).
            if not re.search(r"\b" + re.escape(str(val)) + r"\b", scope):
                fails.append(f"registry id not referenced{where}: {val!r}")
    else:
        fails.append(f"unknown assertion kind: {kind!r}")
    return fails


# ── contract discovery + conform ─────────────────────────────────────────────
def load_contracts(only: str | None) -> list[tuple[str, dict]]:
    out = []
    for path in sorted(CONTRACTS_DIR.glob("*.json")):
        contract = json.loads(path.read_text(encoding="utf-8"))
        name = contract.get("name", path.stem)
        if only and name != only:
            continue
        out.append((name, contract))
    return out


def conform(only: str | None) -> int:
    contracts = load_contracts(only)
    if only and not contracts:
        print(f"FAIL: no contract named {only!r} under {CONTRACTS_DIR}", file=sys.stderr)
        return 2
    if not contracts:
        print(f"FAIL: no contracts found under {CONTRACTS_DIR}", file=sys.stderr)
        return 2
    sdir = skill_dir()
    total_fails = 0
    for name, contract in contracts:
        try:
            target_text = read_target(sdir, contract["target_file"])
        except FailClosed as exc:
            print(f"[{name}] FAIL CLOSED: {exc}", file=sys.stderr)
            return 2
        contract_fails: list[str] = []
        for assertion in contract.get("assertions", []):
            contract_fails.extend(run_assertion(assertion, target_text))
        if contract_fails:
            total_fails += len(contract_fails)
            print(f"[{name}] {len(contract_fails)} violation(s) against {contract['target_file']}:")
            for f in contract_fails:
                print(f"  - {f}")
        else:
            print(f"[{name}] OK ({contract['target_file']})")
    if total_fails:
        print(f"\nconform: {total_fails} violation(s)", file=sys.stderr)
        return 1
    print("\nconform: all contracts pass")
    return 0


# ── snapshot (review + rollback anchor) ──────────────────────────────────────
def _snapshot_files(sdir: Path) -> list[Path]:
    files: list[Path] = []
    for pat in SNAPSHOT_GLOBS:
        files.extend(sorted(sdir.glob(pat)))
    return files


def snapshot(check: bool) -> int:
    sdir = skill_dir()
    if not sdir.is_dir():
        print(f"FAIL CLOSED: skill dir absent: {sdir}", file=sys.stderr)
        return 2
    live = _snapshot_files(sdir)
    if not live:
        print(f"FAIL: no snapshot-tracked files in {sdir}", file=sys.stderr)
        return 2
    if check:
        mismatches: list[str] = []
        live_rels = {src.relative_to(sdir) for src in live}
        for src in live:
            rel = src.relative_to(sdir)
            baked = BASELINE_DIR / rel
            if not baked.is_file():
                mismatches.append(f"missing from baseline: {rel}")
            elif baked.read_text(encoding="utf-8") != src.read_text(encoding="utf-8"):
                mismatches.append(f"baseline differs from live: {rel}")
        # Symmetric: a baseline file with no live counterpart means the live
        # skill lost a tracked file (e.g. SKILL.md deleted) — the baseline no
        # longer matches live, so --check must NOT pass.
        if BASELINE_DIR.is_dir():
            for baked in BASELINE_DIR.rglob("*"):
                if baked.is_file():
                    rel = baked.relative_to(BASELINE_DIR)
                    if rel not in live_rels:
                        mismatches.append(f"in baseline but absent/untracked in live: {rel}")
        if mismatches:
            print("snapshot --check: baseline does not match live skill:", file=sys.stderr)
            for m in mismatches:
                print(f"  - {m}", file=sys.stderr)
            return 1
        print(f"snapshot --check: baseline matches live ({len(live)} files)")
        return 0
    # write
    BASELINE_DIR.mkdir(parents=True, exist_ok=True)
    for src in live:
        rel = src.relative_to(sdir)
        dest = BASELINE_DIR / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    try:
        shown = BASELINE_DIR.relative_to(REPO)
    except ValueError:
        shown = BASELINE_DIR
    print(f"snapshot: wrote {len(live)} file(s) to {shown}")
    return 0


# ── freshness sweep (old-model drift guard) ──────────────────────────────────
def sweep_text(text: str) -> list[str]:
    """Return the banned old-model phrases present in `text` ([] = clean).
    DOTALL so a phrase wrapped across lines (e.g. 'spin up the\\npersonas') still
    trips (Codex: `.{0,30}` would not cross a newline otherwise)."""
    return [pat for pat in BANNED_OLD_MODEL if re.search(pat, text, re.IGNORECASE | re.DOTALL)]


def freshness() -> int:
    """Sweep EVERY live SNAPSHOT_GLOBS file for old-model phrases. Coverage is
    intrinsic — it reads whatever skill files exist, so a new file is auto-covered.
    Fails closed if the skill dir is absent; exit 1 on any hit."""
    sdir = skill_dir()
    if not sdir.is_dir():
        print(f"FAIL CLOSED: skill dir absent: {sdir} (set DESIGN_ROOM_SKILL_DIR)", file=sys.stderr)
        return 2
    files = _snapshot_files(sdir)
    if not files:
        print(f"FAIL: no skill files to sweep under {sdir}", file=sys.stderr)
        return 2
    total = 0
    for f in files:
        hits = sweep_text(f.read_text(encoding="utf-8"))
        if hits:
            total += len(hits)
            print(f"[{f.relative_to(sdir)}] {len(hits)} old-model phrase(s):")
            for h in hits:
                print(f"  - /{h}/")
    if total:
        print(f"\nfreshness: {total} old-model phrase(s) — the v2 cut regressed", file=sys.stderr)
        return 1
    print(f"freshness: clean ({len(files)} skill files swept)")
    return 0


# ── negative self-test (fable-discipline) ────────────────────────────────────
def selftest() -> int:
    good = (
        "## Lenses\n"
        "first-impression conversion-usability decision-psychology positioning-retell "
        "technical-accuracy boldness-feasibility anti-slop\n"
        "Claude assembles, the founder decides.\n"
    )
    bad_missing = "## Lenses\nfirst-impression only. Claude assembles. founder decides.\n"
    bad_banned = good + "\nThis spins up 14 agents that research, debate, and converge.\n"

    present = {"kind": "present", "patterns": ["(?i)##\\s+Lenses", "(?i)Claude assembles"]}
    absent = {"kind": "absent", "patterns": ["14 agents", "(?i)research,?\\s+debate,?\\s+and converge"]}

    problems: list[str] = []
    # GOOD must pass both
    if run_assertion(present, good):
        problems.append("present-assertion failed on GOOD target")
    if run_assertion(absent, good):
        problems.append("absent-assertion failed on GOOD target")
    # BAD-banned MUST trip absent
    if not run_assertion(absent, bad_banned):
        problems.append("absent-assertion did NOT trip on banned phrase (false green)")
    # registry_ids_present against the real registry: GOOD references all ids,
    # bad_missing references only one -> must trip.
    reg_ids = {"kind": "registry_ids_present", "registry": "lens-registry.json", "json_path": "lenses[].id"}
    if run_assertion(reg_ids, good):
        problems.append("registry_ids_present failed on GOOD target (all 7 ids present)")
    if not run_assertion(reg_ids, bad_missing):
        problems.append("registry_ids_present did NOT trip when ids missing (false green)")
    # section slice sanity
    sliced = slice_section("## A\nkeep\n## B\ndrop\n", "## A")
    if sliced is None or "keep" not in sliced or "drop" in sliced:
        problems.append("slice_section is broken")
    # scoped assertion must FAIL CLOSED when its section is missing (a missing
    # section must not let an `absent` check pass vacuously).
    scoped = {"kind": "absent", "patterns": ["anything"], "section": "## Nonexistent"}
    if not run_assertion(scoped, "## A\nbody\n"):
        problems.append("scoped assertion did NOT fail on a missing section (false green)")
    # word-boundary: 'anti-slop' must not be satisfied by 'anti-sloppy'
    wb = {"kind": "registry_ids_present", "registry": "lens-registry.json", "json_path": "lenses[].id"}
    near = " ".join(
        x if x != "anti-slop" else "anti-sloppy"
        for x in json_path_values(
            json.loads((DESIGN_ROOM / "lens-registry.json").read_text()), "lenses[].id"
        )
    )
    if not run_assertion(wb, near):
        problems.append("registry id matched as a substring of a longer word (false green)")

    if problems:
        print("SELFTEST FAILED — engine not trustworthy:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 2
    print("selftest: engine behaves (good passes, bad trips, slice works)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="design-room conformance engine")
    sub = ap.add_subparsers(dest="cmd")
    c = sub.add_parser("conform")
    c.add_argument("--only", default=None)
    s = sub.add_parser("snapshot")
    s.add_argument("--check", action="store_true")
    sub.add_parser("freshness")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return selftest()
    if args.cmd == "conform":
        return conform(args.only)
    if args.cmd == "snapshot":
        return snapshot(args.check)
    if args.cmd == "freshness":
        return freshness()
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
