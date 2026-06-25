# Grounding — teardown reference sites into real tokens (Phase 2.0)

Runs BEFORE the lens review. The point: the lenses weigh REAL designs and REAL
tokens, not imagined ones, and every token the build uses originates here — not
from Claude. This is the gap every competing design skill has (generation-time
guessing with no visual grounding). Fix it at the front.

## Inputs
- Reference sites the founder loves (URLs). Ask for 2-4 if none given.
- Optional: a Figma file (if the founder has one).

## The move

### 1. Fingerprint each reference site (stack + motion)
Use the installed **stack-recon** skill (or `scripts` teardown if present) to
fingerprint each reference URL:
- Network libs + JS globals (GSAP? Lenis? Three.js? Rive?)
- DOM structure of the hero
- Fonts (foundry vs system)
- The one signature motion moment

Write each teardown to `grounding/<site-slug>-teardown.md`. Steal technique, never
pixels.

### 2. Extract taste into tokens
For each reference, pull concrete tokens + the WHY behind them:
- Color palette (hex), type scale, spacing rhythm, radius, shadow language, motion
  timing/easing.
- The opinionated trade-off each choice makes (e.g. "tight tracking + heavy weight
  = authority over friendliness").

If a Figma file exists, use the **Figma MCP** (figma/mcp-server-guide) to pull real
frames/tokens/components instead of eyeballing.

Write to `grounding/tokens.md` — the candidate token set the lenses weigh and the
founder's forks resolve.

### 3. Hand grounding to the lenses
Every cited/grounded lens reads `grounding/tokens.md` + the teardowns before it
runs. Each token a lens references must trace back to here. The job is "validate /
push / refine these real tokens" — never "invent from scratch."

## Output
```
grounding/
  <site>-teardown.md     -- stack + motion fingerprint per reference
  tokens.md              -- candidate tokens + rationale the lenses weigh
```

## Rule
Grounding is candidate input, not a decision. The lenses still weigh in and the
founder still decides. Layer, never replace.
