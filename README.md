# Design Room

A Claude Code skill that turns web design from "the AI guessed" into decisions that
trace to evidence. Every design call comes from one of three places: a cited
attention/UX principle, a real token pulled from a reference you chose, or a
forced-choice you resolve. Claude assembles. You decide.

It is built to do four things, and to **prove** it does them with deterministic
checks (not vibes):

1. **Follow codified attention/UX literature.** A cited canon (Lindgaard 50ms,
   F/Z scan, Fitts, Hick, Von Restorff, aesthetic-usability, recognition-over-recall,
   Krug, Nielsen), each with the one testable rule it implies. The workflow reads the
   canon; it does not Google mid-task.
2. **Stay current without a per-run web search.** A weekly "modernity pulse" researches
   new repos and trends, then promotes or rejects them into the build palette (trend
   noise rejected with a reason). The palette carries a last-refreshed date.
3. **Not look AI-generated.** A reactive gate runs an AI-slop render check on the built
   page (slop fails, clean passes), reported honestly when a layer cannot run.
4. **Not let Claude originate decisions.** A grounded mode where every token resolves
   to a reference or a fork, enforced by a provenance checker.

## The cut: lenses, not personas

Earlier versions spun up a room of personas that "debated" and "converged." That made
the model play every side and call the winner a decision. This version replaces them
with **7 codified review lenses**, each bound to evidence:

| Lens | What it checks | Bound to |
|------|----------------|----------|
| `first-impression` | survives the 50ms / first-screen scan | cited (Lindgaard, F/Z, hierarchy) |
| `conversion-usability` | interaction cost: target size, choices, self-evidence | cited (Fitts, Hick, Krug, Nielsen) |
| `decision-psychology` | a stressed buyer recognises the situation and acts | cited (aesthetic-usability, recognition) |
| `positioning-retell` | which one-sentence retell is the page's spine | fork (you decide) |
| `technical-accuracy` | every claim/code/screenshot matches a grounding source | grounded fact-check |
| `boldness-feasibility` | where to spend the one bold moment vs scan speed + LCP | fork (Von Restorff + perf) |
| `anti-slop` | generic copy, convergent fonts, gradient text, emoji icons | the reactive gate |

A lens may only cite, fact-check against grounding, or raise a fork. It never invents
a token, font, or copy line, and never resolves its own fork.

## Compounding decision record

Each project keeps a `decisions.md`: an append-only, dated, hash-chained ledger. One
entry per decision, with what was decided, why (a real canon id, a fork, or a
grounding path), and what it superseded. The reasoning compounds across sessions
instead of being overwritten. The chain catches accidental edits, deletions, and
reorders; commit it to git for the authoritative append-only audit.

## Install

Copy the skill into your Claude Code skills directory:

```bash
cp -R skill ~/.claude/skills/design-room
```

Then start a session and say "design room" (or "design review my landing page"). Or
scaffold a project directly:

```bash
python3 skill/scripts/init_project.py MyProduct --path .
```

## How it runs

```
ground (teardown references into real tokens)
  -> lens review (each lens cites, fact-checks, or raises a fork)
  -> assemble a fork sheet (you resolve the forks)
  -> grounded design.md spec (every token has a source)
  -> build
  -> anti-slop gate
  -> your eye
```

## The checks (run them)

The tools under `scripts/` are the deterministic backbone. Everything has a negative
self-test (a gate is not trusted until it has been seen to fail):

```bash
python3 -m pytest scripts/tests/ -q                    # the whole suite

# the skill conforms to its contracts, and carries no old-model drift:
DESIGN_ROOM_SKILL_DIR=skill python3 scripts/verify_design_room.py conform
DESIGN_ROOM_SKILL_DIR=skill python3 scripts/verify_design_room.py freshness

python3 scripts/check_token_provenance.py --selftest   # grounded mode
python3 scripts/check_decision_log.py    --selftest    # the decision ledger
python3 scripts/design_room_pulse.py     --selftest    # the weekly pulse (offline)
```

The anti-slop render gate (`scripts/design_room_gate_check.py`) wraps
[eyeball](https://github.com/) or any render-based AI-slop checker; set `EYEBALL_DIR`
to point at it. It fails closed if the checker is absent.

## Layout

```
skill/            the skill itself (SKILL.md + references/ + the project scaffolder)
scripts/          the deterministic tools + their tests
design-room/      contracts, the lens registry, fixtures, the pulse
```

## License

MIT. See [LICENSE](LICENSE).


---

## Built by Assaf

I spent 12 years in threat intelligence watching teams find the same failure and fix it four times. The learning never stuck. I build tools that make it stick.

This is the free version. The paid kits live at [claudedaddy.io](https://claudedaddy.io).

**Want this wired into your team's repo, or a heavier spec-and-review pipeline?** That's the consulting. [Book a call.](https://calendar.app.google/cMFvhvDsfi9iyWYy9)
