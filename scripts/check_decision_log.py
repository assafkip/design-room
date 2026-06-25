#!/usr/bin/env python3
"""Decision-ledger checker for design-room (drd-ledger-checker).

A design-room project keeps a compounding, canonical `decisions.md`: one dated,
hash-chained entry per decision (what / why / supersedes / origin tag). The chain
catches accidental edits, deletions, and reorders of prior decisions. It is NOT
cryptographic tamper-proofing: a determined editor can rewrite an entry and recompute
every downstream `prev`. Two things close that: pin the head hash with `--head` (the
trusted terminal commitment, recorded in git) and commit each decision — GIT HISTORY
is the authoritative append-only audit. Origin tags carry resolvable provenance (a
real canon id, and a fork/grounding/brief target that must exist in the project), not
just a label.

Entry format:
  ## 2026-06-25 — serif-over-sans   <!-- id:2026-06-25-serif-over-sans prev:GENESIS -->
  - **Decision:** use the serif display face, not the sans.
  - **Why:** [LENS-CITED canon:lindgaard-2006-50ms] reads credible at a 50ms glance.
  - **Supersedes:** none

Commands:
  check <file>     validate the WHOLE ledger (exit 0 ok / 1 violations)
  append <file> --date --title --decision --tag --ref --why [--supersedes none]
                   write a well-formed, correctly-chained entry (agent never hand-hashes)
  --selftest       positive + every negative fixture + an append round-trip

fable-discipline: --selftest proves the checker FAILS on a rewritten prior entry,
an impossible date, a stray heading, a bogus tag, an empty field, and a dangling
supersedes — not just that a good file passes.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import re
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
DESIGN_ROOM = SCRIPTS.parent / "design-room"
LENS_REGISTRY = DESIGN_ROOM / "lens-registry.json"

HEADING_RE = re.compile(
    r"^##\s+(\d{4}-\d{2}-\d{2})\s+—\s+(.+?)\s+<!--\s*id:(\S+)\s+prev:(\S+)\s*-->\s*$"
)
DECISION_RE = re.compile(r"^\s*-\s*\*\*Decision:\*\*\s*(\S.*)$")
WHY_RE = re.compile(r"^\s*-\s*\*\*Why:\*\*\s*\[([A-Z-]+)\s+([^\]]+?)\]\s*(\S.*)$")
SUPERSEDES_RE = re.compile(r"^\s*-\s*\*\*Supersedes:\*\*\s*(\S.*)$")

# origin tag -> regex its provenance ref must match
TAG_REF = {
    "FOUNDER-DECIDED": re.compile(r"^(founder|brief:[\w./-]+)$"),
    "FORK-RESOLVED": re.compile(r"^fork:[\w-]+$"),
    "LENS-CITED": re.compile(r"^canon:[\w-]+$"),
    "GROUNDED": re.compile(r"^grounding/[\w./-]+$"),
}


def canon_ids() -> set[str]:
    reg = json.loads(LENS_REGISTRY.read_text(encoding="utf-8"))
    ids: set[str] = set()
    for lens in reg["lenses"]:
        ids.update(lens.get("canon_refs", []))
    return ids


def slug(title: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", title.lower())).strip("-")


def hash_entry(entry_text: str) -> str:
    canonical = "\n".join(ln.rstrip() for ln in entry_text.strip().splitlines())
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:12]


# ── parsing: split into (heading_line, full_text) blocks ─────────────────────
def split_entries(text: str) -> list[str]:
    """Return each entry's full text (heading through body). Preamble before the
    first '## ' is ignored; every '## ' starts an entry."""
    lines = text.splitlines()
    starts = [i for i, ln in enumerate(lines) if ln.startswith("## ")]
    blocks = []
    for n, start in enumerate(starts):
        end = starts[n + 1] if n + 1 < len(starts) else len(lines)
        blocks.append("\n".join(lines[start:end]))
    return blocks


# ── validation ───────────────────────────────────────────────────────────────
def _one(body: str, loose: str) -> tuple[int, str | None]:
    """Count body lines starting with a field marker; return (count, the single line)."""
    hits = [ln for ln in body.splitlines() if re.match(loose, ln)]
    return (len(hits), hits[0] if len(hits) == 1 else None)


def _resolve_ref(tag: str, ref: str, known_canon: set[str], root: Path) -> list[str]:
    """Resolve a provenance ref. LENS-CITED always (canon is repo-side); the others
    resolve against the project's sibling files WHEN they exist (project-time);
    fixtures with no siblings get shape-only validation."""
    if tag == "LENS-CITED":
        return [] if ref.split(":", 1)[1] in known_canon else \
            [f"[LENS-CITED] canon id {ref!r} is not a real canon principle"]
    if tag == "GROUNDED" and (root / "grounding").is_dir():
        target = root / ref.split("#", 1)[0]
        return [] if target.is_file() else [f"[GROUNDED] {ref!r} does not resolve to a grounding file"]
    if tag == "FORK-RESOLVED" and (root / "forks.md").is_file():
        fid = ref.split(":", 1)[1]
        return [] if fid in (root / "forks.md").read_text(encoding="utf-8") else \
            [f"[FORK-RESOLVED] fork {fid!r} not found in forks.md"]
    if tag == "FOUNDER-DECIDED" and ref.startswith("brief:") and (root / "founders-brief.md").is_file():
        anchor = ref.split(":", 1)[1]
        return [] if anchor in (root / "founders-brief.md").read_text(encoding="utf-8") else \
            [f"[FOUNDER-DECIDED] brief anchor {anchor!r} not found in founders-brief.md"]
    return []


def _check_why(body: str, known_canon: set[str], root: Path) -> list[str]:
    count, line = _one(body, r"^\s*-\s*\*\*Why:\*\*")
    if count != 1:
        return [f"expected exactly one **Why:** line, found {count}"]
    m = WHY_RE.match(line)
    if not m:
        return ["malformed **Why:** line (expected [TAG ref] non-empty prose)"]
    tag, ref, prose = m.group(1), m.group(2).strip(), m.group(3).strip()
    if tag not in TAG_REF:
        return [f"unknown origin tag [{tag}] (allowed: {', '.join(sorted(TAG_REF))})"]
    out = []
    if not TAG_REF[tag].match(ref):
        out.append(f"[{tag}] ref {ref!r} does not match its required provenance form")
    else:
        out.extend(_resolve_ref(tag, ref, known_canon, root))
    if not prose:
        out.append("Why prose is empty")
    return out


def _check_entry(block: str, prior_ids: set[str], known_canon: set[str], root: Path) -> tuple[list[str], str | None]:
    """Validate one entry block. Return (violations, id-or-None)."""
    head = block.splitlines()[0]
    m = HEADING_RE.match(head)
    if not m:
        return ([f"stray/malformed heading: {head!r}"], None)
    date_s, title, eid, _prev = m.groups()
    out: list[str] = []
    try:
        datetime.datetime.strptime(date_s, "%Y-%m-%d")
    except ValueError:
        out.append(f"impossible calendar date: {date_s}")
    if eid != f"{date_s}-{slug(title)}":
        out.append(f"id {eid!r} != <date>-<slug(title)> ({date_s}-{slug(title)})")
    if eid in prior_ids:
        out.append(f"duplicate entry id: {eid}")
    body = "\n".join(block.splitlines()[1:])
    dcount, _ = _one(body, r"^\s*-\s*\*\*Decision:\*\*\s*\S")
    if dcount != 1:
        out.append(f"expected exactly one non-empty **Decision:** line, found {dcount}")
    out.extend(_check_why(body, known_canon, root))
    scount, sline = _one(body, r"^\s*-\s*\*\*Supersedes:\*\*")
    if scount != 1:
        out.append(f"expected exactly one **Supersedes:** line, found {scount}")
    else:
        sup = SUPERSEDES_RE.match(sline)
        sup = sup.group(1).strip() if sup else ""
        if sup != "none" and sup not in prior_ids:
            out.append(f"Supersedes {sup!r} does not resolve to an earlier entry id")
    return (out, eid)


def check_file(path: Path, head: str | None = None) -> list[str]:
    """Validate the ledger. `head`, if given, is the externally-pinned hash of the
    LAST entry (e.g. recorded in git) — the trusted terminal commitment that makes a
    full-rewrite detectable. WITHOUT a pinned head, the chain catches accidental
    edits, deletions, and reorders, but a determined editor who recomputes every
    downstream prev can forge an internally-consistent chain; git history is the
    authoritative append-only audit."""
    if not path.is_file():
        return [f"decisions.md not found: {path}"]
    blocks = split_entries(path.read_text(encoding="utf-8"))
    if not blocks:
        return ["no decision entries found (expected '## <date> — <title>' headings)"]
    known_canon = canon_ids()
    root = path.parent
    violations: list[str] = []
    prior_ids: set[str] = set()
    prev_hash = "GENESIS"
    for block in blocks:
        errs, eid = _check_entry(block, prior_ids, known_canon, root)
        m = HEADING_RE.match(block.splitlines()[0])
        if m and m.group(4) != prev_hash:
            errs.append(f"broken chain at {eid}: prev:{m.group(4)} != expected {prev_hash}")
        violations.extend(f"[{eid or block.splitlines()[0][:40]}] {e}" for e in errs)
        if eid:
            prior_ids.add(eid)
        prev_hash = hash_entry(block)
    if head is not None and head != prev_hash:
        violations.append(f"head mismatch: pinned {head} != actual last-entry hash {prev_hash} "
                          "(the ledger was rewritten or truncated)")
    return violations


# ── append (deterministic; the agent never hand-hashes) ──────────────────────
def append_entry(path: Path, date_s: str, title: str, decision: str,
                 tag: str, ref: str, why: str, supersedes: str) -> str:
    prev = "GENESIS"
    if path.is_file():
        blocks = split_entries(path.read_text(encoding="utf-8"))
        if blocks:
            prev = hash_entry(blocks[-1])
    eid = f"{date_s}-{slug(title)}"
    entry = (
        f"## {date_s} — {title}   <!-- id:{eid} prev:{prev} -->\n"
        f"- **Decision:** {decision}\n"
        f"- **Why:** [{tag} {ref}] {why}\n"
        f"- **Supersedes:** {supersedes}\n"
    )
    with path.open("a", encoding="utf-8") as fh:
        fh.write(("\n" if path.stat().st_size else "") + entry)
    return eid


# ── selftest (fable-discipline) ──────────────────────────────────────────────
GOOD = """# Decisions — TestCo

## 2026-06-18 — sans-default   <!-- id:2026-06-18-sans-default prev:GENESIS -->
- **Decision:** start with a neutral sans.
- **Why:** [FOUNDER-DECIDED founder] founder's first instinct.
- **Supersedes:** none
"""


def _with_second_entry(tmp: Path) -> Path:
    f = tmp / "decisions.md"
    f.write_text(GOOD, encoding="utf-8")
    append_entry(f, "2026-06-25", "serif over sans", "use the serif display face",
                 "LENS-CITED", "canon:lindgaard-2006-50ms",
                 "reads credible at a 50ms glance", "2026-06-18-sans-default")
    return f


def selftest() -> int:
    import tempfile
    problems: list[str] = []
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        # positive: a good chained 2-entry ledger (built via append) passes
        good = _with_second_entry(tmp)
        if check_file(good):
            problems.append(f"positive ledger failed: {check_file(good)}")
        good_text = good.read_text(encoding="utf-8")

        negatives = {
            "stray undated H2": good_text + "\n## not a real entry\n- **Decision:** x\n",
            "impossible date": good_text.replace("2026-06-25", "2026-99-99"),
            "rewritten prior entry": good_text.replace("neutral sans", "a bold sans"),
            "bad origin tag": good_text.replace("[LENS-CITED canon:lindgaard-2006-50ms]", "[MADE-UP-TAG x]"),
            "fake canon id": good_text.replace("canon:lindgaard-2006-50ms", "canon:not-a-real-principle"),
            "empty decision": good_text.replace("use the serif display face", ""),
            "dangling supersedes": good_text.replace("2026-06-18-sans-default\n", "2099-01-01-ghost\n", 1),
            "duplicate why line": good_text.replace(
                "- **Supersedes:** 2026-06-18-sans-default",
                "- **Why:** [FORK-RESOLVED fork:x] sneaky second why\n- **Supersedes:** 2026-06-18-sans-default", 1),
        }
        for name, bad in negatives.items():
            f = tmp / "bad.md"
            f.write_text(bad, encoding="utf-8")
            if not check_file(f):
                problems.append(f"negative '{name}' did NOT fail (false green)")

        # head pin: correct head passes, wrong head fails (the terminal commitment)
        good_head = hash_entry(split_entries(good.read_text(encoding="utf-8"))[-1])
        if check_file(good, head=good_head):
            problems.append("correct head pin should pass")
        if not check_file(good, head="000000000000"):
            problems.append("wrong head pin did NOT fail (no terminal commitment)")

        # append round-trip: a third entry keeps the chain valid
        append_entry(good, "2026-07-02", "accent warm", "warm accent",
                     "FORK-RESOLVED", "fork:accent-hue", "founder picked warm", "none")
        if check_file(good):
            problems.append(f"append round-trip broke the chain: {check_file(good)}")

    if problems:
        print("SELFTEST FAILED — decision-log checker not trustworthy:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 2
    print("selftest: positive passes, every negative trips, append round-trips clean")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="design-room decision-ledger checker")
    ap.add_argument("--selftest", action="store_true")
    sub = ap.add_subparsers(dest="cmd")
    c = sub.add_parser("check")
    c.add_argument("file")
    c.add_argument("--head", default=None, help="externally-pinned hash of the last entry (from git)")
    a = sub.add_parser("append")
    a.add_argument("file")
    for flag in ("--date", "--title", "--decision", "--tag", "--ref", "--why"):
        a.add_argument(flag, required=True)
    a.add_argument("--supersedes", default="none")
    args = ap.parse_args()

    if args.selftest:
        return selftest()
    if args.cmd == "check":
        violations = check_file(Path(args.file), head=args.head)
        if violations:
            print(f"decision-log: {len(violations)} violation(s) in {args.file}:", file=sys.stderr)
            for v in violations:
                print(f"  - {v}", file=sys.stderr)
            return 1
        print(f"decision-log: valid, chain intact ({args.file})")
        return 0
    if args.cmd == "append":
        path = Path(args.file)
        eid = append_entry(path, args.date, args.title, args.decision,
                           args.tag, args.ref, args.why, args.supersedes)
        head = hash_entry(split_entries(path.read_text(encoding="utf-8"))[-1])
        print(f"appended entry {eid}  head:{head}")  # pin this head in git for tamper-evidence
        return 0
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
