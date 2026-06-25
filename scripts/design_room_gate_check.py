#!/usr/bin/env python3
"""Anti-AI gate verifier for design-room (W3, dr2-anti-ai-gate-verify).

design-room's Phase-6 convergence gate claims to catch AI-slop via eyeball. This
script PROVES that claim instead of asserting it: it runs the real eyeball
`scan.mjs` against a known-slop fixture (must FAIL) and a known-clean fixture
(must PASS), and fails closed if eyeball is missing. If no browser is on disk
eyeball runs in advisory mode — this script reports that honestly rather than
pretending the gate ran.

Layers it reports on (see design-room/gate-status.md):
  1. static dogfood hook (kipi-design dogfood_gate.py) — out of scope here
  2. eyeball render gate (scan.mjs) — VERIFIED here, deterministically
  3. eyeball --vision UX read — reported (needs ANTHROPIC_API_KEY), not required
  4. vercel web-interface-guidelines — manual, reported

Exit 0 = render gate enforced + behaves (or honestly advisory) ; 1 = gate
misbehaved (slop passed or clean failed) ; 2 = fail closed (eyeball/node absent).
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
GTM = SCRIPTS.parent
FIXTURES = GTM / "design-room" / "fixtures" / "gate"
EYEBALL_DIR = Path(os.environ.get("EYEBALL_DIR", str(Path("~/projects/eyeball").expanduser()))).expanduser()
SCAN = EYEBALL_DIR / "web" / "scan.mjs"
ADVISORY_MARK = "no chromium on disk"


def run_scan(path: Path) -> tuple[int, str]:
    proc = subprocess.run(
        ["node", str(SCAN), str(path)],
        capture_output=True, text=True,
    )
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def classify(slop_exit, slop_out, clean_exit, clean_out) -> tuple[bool, str, list[str]]:
    """Pure decision (testable without a browser). Returns (ok, status, reasons)."""
    # Genuine advisory = eyeball printed the no-browser marker AND exited 0 (its
    # advisory path) on BOTH runs. A crash that prints the marker but exits
    # nonzero, or only one run emitting it, is NOT advisory — it falls through to
    # the broken check (Codex: marker-alone false-greened a crashing scan).
    slop_adv = ADVISORY_MARK in slop_out and slop_exit == 0
    clean_adv = ADVISORY_MARK in clean_out and clean_exit == 0
    if slop_adv and clean_adv:
        return True, "advisory", ["no chromium on disk — eyeball render gate is advisory-only here"]
    reasons = []
    if not (slop_exit == 1 and "GATE: FAIL" in slop_out):
        reasons.append(f"slop fixture did NOT fail the gate (exit={slop_exit}); gate not enforcing")
    if not (clean_exit == 0 and "GATE: PASS" in clean_out):
        reasons.append(f"clean fixture did NOT pass the gate (exit={clean_exit}); gate over-blocking")
    return (not reasons), ("enforced" if not reasons else "broken"), reasons


def main() -> int:
    if not SCAN.is_file():
        print(f"FAIL CLOSED: eyeball scan.mjs not found at {SCAN} (set EYEBALL_DIR)", file=sys.stderr)
        return 2
    slop = FIXTURES / "slop.html"
    clean = FIXTURES / "clean.html"
    for f in (slop, clean):
        if not f.is_file():
            print(f"FAIL CLOSED: fixture missing: {f}", file=sys.stderr)
            return 2
    try:
        slop_exit, slop_out = run_scan(slop)
        clean_exit, clean_out = run_scan(clean)
    except FileNotFoundError:
        print("FAIL CLOSED: `node` not on PATH; cannot run eyeball", file=sys.stderr)
        return 2

    ok, status, reasons = classify(slop_exit, slop_out, clean_exit, clean_out)
    vision = "available" if os.environ.get("ANTHROPIC_API_KEY") else "UNAVAILABLE (no ANTHROPIC_API_KEY)"

    print(f"eyeball render gate: {status}")
    print(f"  slop fixture  -> exit {slop_exit} ({'FAIL' if 'GATE: FAIL' in slop_out else 'no-fail'})")
    print(f"  clean fixture -> exit {clean_exit} ({'PASS' if 'GATE: PASS' in clean_out else 'no-pass'})")
    print(f"  --vision UX read: {vision} (reported, not required)")
    for r in reasons:
        print(f"  - {r}")
    if status == "broken":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
