---
name: "design-room"
description: "Codified design tool for product websites and marketing pages. Reviews a page through 7 evidence-bound lenses (first-impression, conversion-usability, decision-psychology, positioning-retell, technical-accuracy, boldness-feasibility, anti-slop), grounds every token in real references, and builds against a vetted palette. Every decision traces to a cited attention/UX principle, a real grounded token, or a founder fork — never to an unsourced opinion. Claude assembles, the founder decides. Use when the user wants to design or redesign a website, landing page, or product marketing page, or mentions 'design room', 'design review', 'lens review', or wants grounded multi-lens feedback on a design. Reads a codified attention canon (no per-run web search); modernity comes from a weekly pulse."
---

# Design Room

A codified design tool. Not a panel of characters who argue. Seven evidence-bound
review **lenses** examine a page; each lens may only cite a principle, fact-check
against grounding, or surface a forced-choice fork. The room produces a fork sheet
and a grounded spec. **Claude assembles, the founder decides.**

## The cut (why this is not personas)

design-room used to voice many characters who argued and "converged." That made
Claude play both sides and call the winner a decision. v2 replaces them with the 7
lenses below. Each lens is bound to evidence: a cited principle from the attention
canon, a fact-check against real grounding tokens, a forced-choice fork the founder
resolves, or a hand-off to the reactive anti-AI gate. The full rationale + the
The lenses are a deliberate cut from an earlier multi-persona-debate design; see the README.

## Lenses

These are exactly the 7 (the machine-readable registry + the contracts that gate
this skill live in this repo at `design-room/`). A lens NEVER originates a
token/color/font/copy line and NEVER resolves its own fork.

| Lens id | What it checks | Bound to |
|---------|----------------|----------|
| `first-impression` | survives the 50ms / first-3-second scan; primary action on the F/Z path in the first screen | cited (Lindgaard 2006, F/Z, hierarchy) |
| `conversion-usability` | interaction cost: target size, choice count, self-evidence, heuristic violations | cited (Fitts, Hick, Krug, Nielsen) |
| `decision-psychology` | a stressed buyer recognises their situation and acts; polish is honoured not faked | cited (aesthetic-usability, recognition-over-recall) |
| `positioning-retell` | which one-sentence retell is the page's spine | **fork** (founder owns positioning) |
| `technical-accuracy` | every technical claim / code sample / screenshot matches a grounding source | grounded fact-check |
| `boldness-feasibility` | where to spend the ONE bold, pattern-breaking moment vs scan-speed + LCP budget | **fork** (Von Restorff + perf) |
| `anti-slop` | generic copy, convergent fonts, gradient-text, emoji icons, "show the situation, don't name the feeling" | the reactive anti-AI **gate** |

Each cited lens reads the **attention canon** ([references/attention-canon.md](references/attention-canon.md)) —
the named, sourced principles and the one testable rule each implies. The lens
does not search the web; the canon is its source of truth.

## Workflow

The line is: ground -> review through the lenses -> assemble a fork sheet ->
the founder resolves the forks -> write a grounded design.md spec -> build ->
pass the gate -> founder's eye. It never originates a decision for the founder.

### Phase 1: Initialize or Load

**New project:** Run `scripts/init_project.py`. Populate `founders-brief.md` with
the product, the founder, and constraints.

**Existing project:** Read `founders-brief.md`, the `decisions.md` ledger (the
compounding record of every prior decision + why), and any prior `grounding/`,
`design.md`, and fork-sheet from the project's `design-room/` directory. The
decisions ledger is how prior sessions' reasoning carries forward.

### Phase 2.0: Grounding (before any lens runs)

Teardown the founder's reference sites into REAL tokens. See
[references/grounding.md](references/grounding.md). Fingerprint each reference
(stack-recon / Figma MCP), extract tokens + the WHY into `grounding/tokens.md`.
Every candidate token the build will use must originate here, not from Claude.

### Phase 2: Lens review (cite or fork, never originate)

Run each lens over the brief + grounding. A lens emits ONLY one of:
- **cited:** "principle X (canon) implies rule Y; the page does/doesn't" — with the canon ref.
- **grounded:** "claim Z on the page matches/does-not-match grounding source S."
- **fork:** "open choice — A vs B; founder picks" (positioning-retell, boldness-feasibility).
- **gate:** hand `anti-slop` to the reactive gate in Phase 6.

Write each lens's output to `review/<lens-id>.md`. A lens that states a preference
without a citation, a grounding source, or a fork is malformed — drop it.

### Phase 3: Synthesis (assemble, do not decide)

Collect the lens outputs into a single **fork sheet** (`forks.md`): every open
choice, each as a forced-choice with the evidence on each side. Claude **assembles**
this sheet. Claude does not pick. The founder resolves each fork. This is the line:
**Claude assembles, the founder decides.** Record the founder's picks back into
`founders-brief.md` (layered, never replacing). Then APPEND one entry per resolved
fork to `decisions.md` via the deterministic appender (never hand-edit the ledger):
`python3 scripts/check_decision_log.py append <project>/design-room/decisions.md
--date <today> --title "<short>" --decision "<what>" --tag <FOUNDER-DECIDED|FORK-RESOLVED|
LENS-CITED|GROUNDED> --ref <founder|fork:id|canon:id|grounding/path> --why "<why>"
--supersedes <none|prior-id>`. See [references/decisions-template.md](references/decisions-template.md).

### Phase 4: Grounded mode — the design.md spec

Write the resolved decision to `design.md` (tokens + rationale), NOT prose. See
[references/design-md-template.md](references/design-md-template.md) and the
grounded-mode rule below. Every token MUST carry a `source:` pointing at a
`grounding/` entry or a founder fork. A token with no source is rejected — Claude
may not originate one to make the page work.

### Phase 5: Build (wire the vetted palette)

Build the real page from `design.md`. The build palette
([references/build-palette.md](references/build-palette.md)) is the vetted menu;
it carries a **last-refreshed date** maintained by the weekly modernity pulse (see
"Modernity" below). Install only the repos the spec names. Wire the ONE signature
moment, assemble sections, run it with zero console errors.

### Phase 6: Convergence gate (the anti-slop lens, made real)

Run the gate before showing the founder. See
[references/convergence-gate.md](references/convergence-gate.md): the eyeball
render gate + impeccable detectors + vercel guidelines, then cross-check the spec.
This is where the `anti-slop` lens actually fires. Write `build/gate-report.md`.
Never call the design "good" to the founder — the gate is the floor, the founder
is the eye.

## Grounded mode (Claude assembles, the founder decides)

This is the core rule, enforced by `verify_design_room.py` + `check_token_provenance.py`
in this repo:

1. **No originated tokens.** Every color/font/spacing/radius/motion token in
   `design.md` carries a `source:` — a `grounding/` reference or a founder fork.
   Claude may not invent a token. If grounding lacks a needed token, that is a
   fork for the founder, not a gap Claude fills.
2. **No originated copy.** Headlines and body copy trace to the founder's words,
   the brief, or grounding. Claude assembles and arranges; it does not write the
   positioning.
3. **Every open choice is a forced-choice fork.** When the evidence does not
   decide, the lens emits A-vs-B and the founder picks. Claude never resolves its
   own fork.
4. **Synthesis assembles, never originates.** Phase 3 collects and arranges. It
   adds no new decision.

## Modernity (no per-run web search)

The per-run workflow does **zero web research**. What is "modern" comes from the
**weekly modernity pulse** (`design_room_pulse.py` in this repo): a scheduled
job researches new repos/trends, writes a dated snapshot, and promotes/rejects
into `references/build-palette.md`, which carries a last-refreshed date. At run
time the room reads the canon and the palette — it does not search.

## Critical Rules

1. **Layer, never replace.** New founder inputs ADD to the brief. Keep all context.
2. **Cite, ground, or fork.** Every lens output is a cited principle, a grounding
   fact-check, or a forced-choice fork. Never an unsourced opinion.
3. **Claude assembles, the founder decides.** No originated tokens, no originated
   copy, no self-resolved forks.
4. **The gate is the floor, the founder is the eye.** Never report a page as
   "good" — report what the gate said and hand it to the founder.
5. **Decisions compound — append-only, dated, never rewritten.** Every decision is
   appended to `decisions.md` with its date, why (lens/fork/cited principle), and what
   it supersedes. Never edit or delete a prior entry; supersede it. This is the record
   that carries across sessions.

## File Structure

```
<project>/design-room/
  founders-brief.md     -- Canonical. All founder inputs layered.
  decisions.md          -- Compounding canonical record: append-only, dated, hash-chained decisions
  grounding/            -- Reference-site teardowns + candidate tokens (every token starts here)
  review/               -- One file per lens (cited / grounded / fork output)
  forks.md              -- The assembled fork sheet the founder resolves
  design.md             -- Grounded spec (tokens + source per token, agent-readable)
  build/                -- The built page + gate-report.md
```

## References

- [references/lens definitions + the attention canon](references/attention-canon.md)
- [references/grounding.md](references/grounding.md) — Phase 2.0 teardown -> tokens
- [references/build-palette.md](references/build-palette.md) — vetted repo menu (weekly-refreshed)
- [references/design-md-template.md](references/design-md-template.md) — the grounded spec format
- [references/decisions-template.md](references/decisions-template.md) — the compounding decision ledger format
- [references/convergence-gate.md](references/convergence-gate.md) — the ship gate
