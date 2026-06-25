# Convergence Gate (Phase 6) — the built page must pass before it ships

The room can agree on something slop. The gate is the deterministic referee that
fires AFTER the page is built. Three layers, run in order. A page is not done until
all three pass (or the founder explicitly signs off on an exception).

## Layer 1 — dogfood / eyeball gate (deterministic floor)
The repo's own AI-slop detector. Run the real render:
```
node ~/projects/eyeball/web/scan.mjs <url-or-file>        # add --vision for the UX read
```
Fails (GATE: FAIL) when the AI-design score is too high OR the primary action is not
in the first screen. This is the same gate every public page in the system passes.
If a static `dogfood_gate.py` hook fires on Write, fix it before continuing.

## Layer 2 — impeccable detectors (44 rules)
Run the impeccable skill's detectors against the built page (brand mode for a
landing/marketing page, product mode for app UI). Catches the design tells the
fast tripwire misses. Fix each flagged rule.

## Layer 3 — vercel web-interface-guidelines audit
Run the `/web-interface-guidelines` audit (vercel-labs/web-interface-guidelines):
100+ UI/UX + accessibility rules, framework-agnostic. Resolve violations.

## Cross-check against the spec
- Every token in `design.md` is actually used on the page (no drift).
- The ONE signature motion moment exists and is the only hero effect (not five).
- The one-sentence test + 8-second test still pass on the rendered page.

## Output
Write `build/gate-report.md`: each layer, pass/fail, what was fixed. Then present to
the founder (the founder is the final eye — the gate is the floor, not the ceiling).

## Rule
Never report the page as "done" or "good-looking" to the founder. Report what the
gate said + that it's ready for the founder's eye. Taste verdict is the founder's.
