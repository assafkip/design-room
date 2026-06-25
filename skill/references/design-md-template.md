# design.md spec template (Phase 4 output)

The resolved design decision (lenses assembled, forks picked by the founder) is
written in this format, NOT prose. A coding agent
(Claude Code) consumes it directly to build the site. Follows the design.md pattern
(google-labs-code/design.md) so it lints + exports to Tailwind/CSS tokens.

Write the filled version to the project's `design.md` (replaces the old prose
`design-spec.md`). Keep `design-spec.md` only as a human-readable rationale log if
wanted.

---

```markdown
# <Project> — Design Spec

## Identity
- Name-first concept: <the one idea the site is built around>
- One-sentence test: <what a visitor can retell after the site>
- Feeling (cold-truth sentence): <the single emotional target>

## Tokens

GROUNDED MODE: every token line carries a `source:` — a `grounding/` reference or a
`fork:<id>` the founder resolved. Claude may NOT originate a token. A token with no
source is rejected by `check_token_provenance.py`. Format per line:
`- <name>: <value>  source: grounding/<file>#<anchor>` OR `source: fork:<fork-id>`.

### Color
- background: #0a0a0a  source: grounding/tokens.md#bg
- surface: #14141a  source: grounding/tokens.md#surface
- text: #f4f4f5  source: grounding/tokens.md#text
- text-muted: #a1a1aa  source: grounding/tokens.md#text-muted
- primary: #5b8cff  source: fork:primary-hue
- accent: #ff7a59  source: fork:accent-hue
- border: #27272a  source: grounding/tokens.md#border
(semantic, not raw — name by role; the values above are placeholders, the `source:`
discipline is the point)

### Type
- font-display: <foundry/family>  source: grounding/<ref>   (NOT Inter/Roboto/Arial/Space Grotesk)
- font-body: <family>  source: grounding/<ref>
- scale: <e.g. 1.250 major third>, base 16px  source: grounding/<ref>
- tracking-weight: <...>  source: grounding/<ref>

### Space & shape
- spacing: <e.g. 4/8/16/32/64>  source: grounding/<ref>
- radius: <...>  source: grounding/<ref>
- shadow: <...>  source: grounding/<ref>

### Motion
- signature: <the ONE hero motion, which repo from build-palette>  source: fork:signature-moment
- scroll: <lenis? GSAP ScrollTrigger?>  source: grounding/<ref>
- timing-easing: <...>  source: grounding/<ref>

## Layout
- Hero: <structure, primary action position — must be in first screen>
- Sections (in order): <...>
- Responsive intent: <...>

## Build palette (chosen)
- <repo> for <what>  (from references/build-palette.md)
- ...

## Rationale (the WHY — for humans, not the agent)
- Why these tokens: <tie to grounding/tokens.md + the resolved forks>
- Conflicts surfaced + how resolved: <...>
- What this deliberately is NOT: <...>

## Gate criteria
- Passes dogfood/eyeball gate (no AI-slop fingerprint, primary action in first screen)
- Passes impeccable detectors + vercel web-interface-guidelines audit
```

---

## Validation
After writing, optionally run `npx design-md` against the file to lint and export
tokens to Tailwind/CSS. Tokens section MUST be complete; rationale section is for
humans. A spec missing tokens is not done.
