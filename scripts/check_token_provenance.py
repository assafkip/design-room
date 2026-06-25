#!/usr/bin/env python3
"""Token-provenance checker for design-room grounded mode (W4, dr2-grounded-mode).

The thesis of design-room v2 is "Claude assembles, the founder decides." The
concrete, testable form of that: in a produced `design.md`, EVERY token under
`## Tokens` must carry a `source:` that resolves to either a `grounding/` reference
or a `fork:<id>` the founder picked. A token with no source means Claude invented a
value to make the page work — the exact thing grounded mode forbids.

This is the REAL test Codex demanded (not structure-only): it runs against a
produced design.md and proves provenance, and `--selftest` proves it FAILS on a
design.md with a sourceless token (no false green).

Scope: this enforces provenance SHAPE — every token has a syntactically valid,
end-anchored source (grounding/<file>#<anchor> or fork:<id>). RESOLVING that the
grounding file/anchor actually exists requires the project's `grounding/` dir and
is a project-time check; the gate here guarantees no token ships without a real
source field of valid shape.

Usage:
  check_token_provenance.py <design.md>   check one file (exit 0 ok / 1 violations)
  check_token_provenance.py --selftest     positive + negative fixtures + live template
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
GTM = SCRIPTS.parent
FIXTURES = GTM / "design-room" / "fixtures" / "grounded"
DEFAULT_SKILL_DIR = (Path(__file__).resolve().parent.parent / "skill")

# A token line under ## Tokens: "- <label>: <value> ...". The label is anything up
# to the first colon, so multi-word labels ('spacing rhythm', 'signature moment')
# are caught too (Codex: a narrow [A-Za-z][\w-]* label let multi-word tokens skip
# the source check). Subheadings (###) and notes without a colon are not tokens.
TOKEN_RE = re.compile(r"^\s*-\s*([^:]+?):\s+\S")
# A valid source must be the TRAILING field of the line and have a strict shape:
# grounding/<path>#<anchor> or fork:<id>. End-anchored + shape so that a bare
# `grounding/x` (no anchor) or an incidental `(no source: grounding/x)` in prose
# does NOT count as provenance (Codex: unanchored search false-greened).
SOURCE_RE = re.compile(r"(?:^|\s)source:\s+(grounding/[\w./-]+#[\w./-]+|fork:[\w.-]+)\s*$")


def _tokens_section(text: str) -> str | None:
    lines = text.splitlines()
    out, capturing = [], False
    for line in lines:
        s = line.strip()
        if not capturing:
            if re.match(r"^##\s+Tokens\b", s):
                capturing = True
            continue
        if re.match(r"^##\s+", s):  # next H2 ends the section
            break
        out.append(line)
    return "\n".join(out) if capturing else None


def check_file(path: Path) -> list[str]:
    """Return a list of provenance violations ([] = every token sourced)."""
    if not path.is_file():
        return [f"design.md not found: {path}"]
    section = _tokens_section(path.read_text(encoding="utf-8"))
    if section is None:
        return ["no '## Tokens' section found"]
    token_lines = [ln for ln in section.splitlines() if TOKEN_RE.match(ln.strip())]
    if not token_lines:
        return ["'## Tokens' section has no token lines"]
    violations = []
    for ln in token_lines:
        name = TOKEN_RE.match(ln.strip()).group(1)
        if not SOURCE_RE.search(ln):
            violations.append(f"token {name!r} has no resolvable source (grounding/ or fork:)")
    return violations


def selftest() -> int:
    problems: list[str] = []
    pos = FIXTURES / "sample-design.md"
    neg = FIXTURES / "negative-design.md"
    if check_file(pos):
        problems.append(f"positive fixture should pass but has violations: {check_file(pos)}")
    if not check_file(neg):
        problems.append("negative fixture should FAIL (sourceless token) but passed — false green")
    # the live template must document the source convention (fail closed if absent)
    raw = os.environ.get("DESIGN_ROOM_SKILL_DIR")
    sdir = Path(raw).expanduser() if raw else DEFAULT_SKILL_DIR
    tmpl = sdir / "references" / "design-md-template.md"
    if not tmpl.is_file():
        problems.append(f"FAIL CLOSED: live design.md template missing: {tmpl}")
    else:
        t = tmpl.read_text(encoding="utf-8")
        if "source:" not in t or not re.search(r"(?i)may not originate|cannot originate|not originate", t):
            problems.append("live design.md template does not document the grounded source rule")
    if problems:
        print("SELFTEST FAILED — provenance checker not trustworthy:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 2
    print("selftest: positive passes, negative trips, live template documents the rule")
    return 0


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print(__doc__, file=sys.stderr)
        return 2
    if args[0] == "--selftest":
        return selftest()
    violations = check_file(Path(args[0]))
    if violations:
        print(f"provenance: {len(violations)} violation(s) in {args[0]}:", file=sys.stderr)
        for v in violations:
            print(f"  - {v}", file=sys.stderr)
        return 1
    print(f"provenance: every token in {args[0]} has a resolvable source")
    return 0


if __name__ == "__main__":
    sys.exit(main())
