#!/usr/bin/env python3
"""Weekly modernity pulse for design-room (W2, dr2-modernity-pulse).

Why: "what's modern" must not be a per-run web search (slow, nondeterministic) and
must not silently rot. This job runs WEEKLY, evaluates candidate repos/trends, and
promotes/rejects them into the build-palette, stamping a last-refreshed date. The
per-run design flow then reads the palette + the attention canon and does ZERO web
research.

Separation of concerns:
- GATHER (web, weekly only): a research step produces a candidates JSON. The seam is
  documented (SEED_SOURCES); live gathering is the founder's scheduled research, not
  this script's deterministic core.
- EVALUATE (deterministic, tested here): promote/reject each candidate with a reason
  (trend-noise and too-niche are REJECTED, logged, never silently dropped), write a
  dated snapshot, and update the palette date + promoted list.

fable-discipline: `--selftest` runs the evaluate path FULLY OFFLINE against a
committed fixture (no network, no credentials) and proves rejected trends are kept
with reasons; it also asserts the live SKILL.md guarantees zero per-run web research.

Usage:
  design_room_pulse.py run --candidates <file> [--date YYYY-MM-DD] [--palette <p>] [--snapshot-dir <d>]
  design_room_pulse.py --selftest
"""
from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
GTM = SCRIPTS.parent
PULSE_DIR = GTM / "design-room" / "pulse"
DEFAULT_SKILL_DIR = (Path(__file__).resolve().parent.parent / "skill")
DEFAULT_PALETTE = DEFAULT_SKILL_DIR / "references" / "build-palette.md"

MIN_STARS = 1000  # below this a repo is too niche to promote into the palette

# Documented seed sources the weekly research sweep should cover (the GATHER seam).
# The pulse does not crawl these itself in the deterministic core; a research step
# fills the candidates file from them. Listed so the sources are reviewable, not magic.
SEED_SOURCES = [
    "github topic:react-components trending this week",
    "github topic:webgl + topic:shaders new repos",
    "github topic:tailwindcss UI kits",
    "github search: liquid glass / lenis / gsap scroll",
    "awesome-design-md + design.md ecosystem releases",
]


def evaluate(candidate: dict, existing_repos: set[str]) -> tuple[str, str]:
    """Return (decision, reason). decision in {'promote','reject'}."""
    repo = candidate.get("repo", "")
    if candidate.get("trend_noise"):
        return "reject", "flagged trend-noise (hype without staying power)"
    if repo in existing_repos:
        return "reject", "already in palette"
    stars = candidate.get("stars", 0)
    if stars < MIN_STARS:
        return "reject", f"too niche (stars {stars} < {MIN_STARS})"
    if not candidate.get("category"):
        return "reject", "no palette category — cannot place it"
    return "promote", "meets bar (stars + real category + not noise)"


def _existing_repos(palette_text: str) -> set[str]:
    # repos appear as github.com/<owner>/<name> links in the palette
    return set(re.findall(r"github\.com/([\w.-]+/[\w.-]+)", palette_text))


def run(candidates: list[dict], date: str, palette_path: Path, snapshot_dir: Path) -> dict:
    palette_text = palette_path.read_text(encoding="utf-8") if palette_path.is_file() else ""
    existing = _existing_repos(palette_text)
    decisions = []
    for c in candidates:
        decision, reason = evaluate(c, existing)
        decisions.append({"repo": c.get("repo"), "decision": decision, "reason": reason,
                          "stars": c.get("stars"), "category": c.get("category")})
    promoted = [d for d in decisions if d["decision"] == "promote"]
    rejected = [d for d in decisions if d["decision"] == "reject"]

    snapshot = {
        "date": date,
        "sources": SEED_SOURCES,
        "n_candidates": len(candidates),
        "promoted": promoted,
        "rejected": rejected,  # kept WITH reasons, never dropped
        "palette_date_bumped": None,
    }

    # update the palette: bump the last-refreshed date (and append promoted, if any)
    if palette_text:
        new_text, n = re.subn(
            r"(?i)(last[ -]refreshed:?\s*)\d{4}-\d{2}-\d{2}",
            rf"\g<1>{date}",
            palette_text,
            count=1,
        )
        snapshot["palette_date_bumped"] = bool(n)
        if n == 0:
            # Contract is to bump the date line; its absence is a real signal, not
            # a silent success (Codex). Warn loudly; keep content + snapshot.
            print(f"WARNING: no 'Last refreshed: <date>' line in {palette_path} — date NOT bumped",
                  file=sys.stderr)
            new_text = palette_text
        if promoted:
            # Append as github.com links so a later run's _existing_repos() sees
            # them and rejects re-promotion (Codex: plain-text appends were
            # invisible to dedup, causing duplicate promotes on rerun).
            block = "\n".join(
                f"- [{p['repo']}](https://github.com/{p['repo']}) ({p['category']}, {p['stars']}★) — pulse {date}"
                for p in promoted)
            marker = "## Pulse-promoted (auto)"
            if marker in new_text:
                new_text = re.sub(rf"({re.escape(marker)}\n)", rf"\1{block}\n", new_text, count=1)
            else:
                new_text = new_text.rstrip() + f"\n\n{marker}\n{block}\n"
        palette_path.write_text(new_text, encoding="utf-8")

    snapshot_dir.mkdir(parents=True, exist_ok=True)
    snap_path = snapshot_dir / f"snapshot-{date}.json"
    snap_path.write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")

    return snapshot


def _load_candidates(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data["candidates"] if isinstance(data, dict) else data


def selftest() -> int:
    import tempfile
    problems: list[str] = []
    fixture = PULSE_DIR / "_fixture-candidates.json"
    if not fixture.is_file():
        print(f"SELFTEST FAILED: fixture missing: {fixture}", file=sys.stderr)
        return 2
    candidates = _load_candidates(fixture)

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        palette = tmp / "build-palette.md"
        palette.write_text(
            "# Build Palette\n\nLast refreshed: 2000-01-01\n\n"
            "[darkroomengineering/lenis](https://github.com/darkroomengineering/lenis)\n",
            encoding="utf-8",
        )
        snap = run(candidates, "2026-06-25", palette, tmp / "pulse")

        # 1. both promoted and rejected present, each rejection has a reason
        if not snap["promoted"]:
            problems.append("nothing promoted from the fixture (expected at least one)")
        if not snap["rejected"]:
            problems.append("nothing rejected (fixture has trend-noise + niche that must reject)")
        if any(not r["reason"] for r in snap["rejected"]):
            problems.append("a rejected trend has no reason (trends must be kept WITH reasons)")
        # 2. trend-noise candidate must be rejected (not promoted)
        noise = [c["repo"] for c in candidates if c.get("trend_noise")]
        if any(p["repo"] in noise for p in snap["promoted"]):
            problems.append("a trend-noise candidate was promoted (false promote)")
        # 3. an already-in-palette repo must be rejected as duplicate
        if not any(r["reason"] == "already in palette" for r in snap["rejected"]):
            problems.append("duplicate (lenis already in palette) was not rejected as duplicate")
        # 4. palette date bumped
        if "Last refreshed: 2026-06-25" not in palette.read_text():
            problems.append("palette last-refreshed date was not bumped")
        # 5. snapshot file written
        if not (tmp / "pulse" / "snapshot-2026-06-25.json").is_file():
            problems.append("snapshot file not written")

    # 6. live per-run guarantee: SKILL.md does zero web research
    import os
    raw = os.environ.get("DESIGN_ROOM_SKILL_DIR")
    sdir = Path(raw).expanduser() if raw else DEFAULT_SKILL_DIR
    skill = sdir / "SKILL.md"
    if not skill.is_file():
        problems.append(f"FAIL CLOSED: live SKILL.md missing: {skill}")
    else:
        t = skill.read_text(encoding="utf-8")
        if re.search(r"WebSearch|WebFetch", t):
            problems.append("SKILL.md references WebSearch/WebFetch — per-run flow is not zero-web")
        if "## Modernity (no per-run web search)" not in t:
            problems.append("SKILL.md missing the Modernity (no per-run web search) section")

    if problems:
        print("SELFTEST FAILED — pulse not trustworthy:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 2
    print("selftest: evaluate promotes/rejects with reasons, palette bumped, per-run is zero-web")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="design-room weekly modernity pulse")
    ap.add_argument("--selftest", action="store_true")
    sub = ap.add_subparsers(dest="cmd")
    r = sub.add_parser("run")
    r.add_argument("--candidates", required=True)
    r.add_argument("--date", default=datetime.date.today().isoformat())
    r.add_argument("--palette", default=str(DEFAULT_PALETTE))
    r.add_argument("--snapshot-dir", default=str(PULSE_DIR))
    args = ap.parse_args()

    if args.selftest:
        return selftest()
    if args.cmd == "run":
        snap = run(_load_candidates(Path(args.candidates)), args.date,
                   Path(args.palette), Path(args.snapshot_dir))
        print(json.dumps({"date": snap["date"], "promoted": len(snap["promoted"]),
                          "rejected": len(snap["rejected"])}))
        return 0
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
