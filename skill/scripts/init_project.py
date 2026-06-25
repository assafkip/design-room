#!/usr/bin/env python3
"""Initialize a new Design Room project: founders brief + grounding/review/build
scaffold + a grounded design.md stub. (design-room v2 — lenses, not personas.)"""

import argparse
import datetime
import os
import sys

DECISIONS_HEADER = """# Decisions — {project}

Append-only, dated, hash-chained record of every design decision. Newest at the
bottom. Append via check_decision_log.py (never hand-edit). See
references/decisions-template.md.

## {today} — project initialized   <!-- id:{today}-project-initialized prev:GENESIS -->
- **Decision:** Design Room initialized for {project}.
- **Why:** [FOUNDER-DECIDED founder] starting the design from the founder's brief.
- **Supersedes:** none
"""

FOUNDERS_BRIEF_TEMPLATE = """# Founder's Brief -- Accumulated Inputs (Canonical)

Every lens reads this file first. These are the founder's actual words and reactions
across the whole design process. They are LAYERS, not replacements. All are
simultaneously true. New input is appended, never overwritten.

---

## Product Description
[FILL IN: What does your product do? Be specific. Include what it IS and what it is NOT.]

## Founder Identity & Perspective
[FILL IN: Who are you? What's your background? What perspective do you bring?]

## Accumulated Design Constraints
### Visual
[FILL IN: What should the site look/feel like? What must it NOT look like?]
### Tone
[FILL IN: How should the site talk to the reader? What voice?]
### Product Positioning
[FILL IN: What is the product? What is it NOT? How should it be framed?]
### Target Audience Psychology
[FILL IN: Who is the buyer? What do they care about? What triggers them to leave?]

## What Has Failed Before
[FILL IN: previous attempts + what went wrong with each.]

## Tests
### The One-Sentence Test
[FILL IN: Can someone retell what you do in one sentence after visiting the site?]
### The 8-Second Test
[FILL IN: In 8 seconds: What does this do? Is there a demo? Are these people credible?]
"""

DESIGN_MD_STUB = """# {project} -- Design Spec (design.md)

GROUNDED MODE: every token carries a `source:` (grounding/<file>#<anchor> or
fork:<id>). No token is invented. See references/design-md-template.md.

## Identity
- Name-first concept: [FILL]
- One-sentence test: [FILL]

## Tokens
### Color
- background: [#]  source: grounding/tokens.md#bg

## Build palette (chosen)
- [repo] for [what] (from references/build-palette.md)

## Rationale
- Why these tokens (tie to grounding/tokens.md + the resolved forks): [FILL]
- What this deliberately is NOT: [FILL]
"""

FORKS_STUB = """# Forks -- open choices the founder resolves

Phase 3 assembles every open design choice here as a forced-choice. Claude does
NOT pick. The founder resolves each; the pick is appended to founders-brief.md.

## Example
- [ ] Fork: headline boldness vs scan-speed (Von Restorff vs Hick)
  - A: one large pattern-breaking headline
  - B: quieter headline, faster scan
  - Founder pick:
"""


def init_project(project_name: str, output_path: str) -> None:
    project_dir = os.path.join(output_path, "design-room")
    if os.path.exists(project_dir):
        print(f"Error: {project_dir} already exists. Use existing files or delete first.")
        sys.exit(1)

    # v2 structure: grounding (every token starts here) / review (one file per lens)
    # / build. No personas/, no research/ -- those were the old debate model.
    for d in ("grounding", "review", "build"):
        os.makedirs(os.path.join(project_dir, d), exist_ok=True)

    writes = {
        "founders-brief.md": FOUNDERS_BRIEF_TEMPLATE,
        "design.md": DESIGN_MD_STUB.format(project=project_name),
        "forks.md": FORKS_STUB,
        "decisions.md": DECISIONS_HEADER.format(
            project=project_name, today=datetime.date.today().isoformat()),
    }
    for name, content in writes.items():
        path = os.path.join(project_dir, name)
        with open(path, "w") as f:
            f.write(content)
        print(f"Created {path}")

    print(f"\nDesign Room initialized for '{project_name}' at {project_dir}")
    print("\nNext steps:")
    print("1. Fill in founders-brief.md with your product and founder details")
    print("2. Add reference-site URLs you love -> Phase 2.0 grounding teardown (grounding/)")
    print("3. Run the lens review: each lens cites the attention canon, fact-checks")
    print("   grounding, or raises a fork -- it never originates a decision")
    print("4. Resolve the forks in forks.md (Claude assembles, you decide)")


def main():
    ap = argparse.ArgumentParser(description="Initialize a Design Room project")
    ap.add_argument("project_name")
    ap.add_argument("--path", default=".")
    args = ap.parse_args()
    init_project(args.project_name, args.path)


if __name__ == "__main__":
    main()
