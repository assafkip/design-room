# decisions.md — the compounding canonical record (template)

Every design-room project keeps a `decisions.md`: an **append-only, dated** ledger of
every design decision, so the trail of WHAT was decided, WHEN, WHY, and what it
SUPERSEDED compounds across sessions instead of being overwritten in `design.md`.
This is a canonical decision log: the trail of what was decided and why, kept across sessions.

Read it at the start of every session (Phase 1). Append one entry per resolved fork
at synthesis (Phase 3). **Never rewrite or delete a prior entry** — supersede it.

## Entry format (hash-chained)

```
## 2026-06-25 — serif-over-sans   <!-- id:2026-06-25-serif-over-sans prev:d3c391fd6dd0 -->
- **Decision:** switch the display face to a serif.
- **Why:** [LENS-CITED canon:lindgaard-2006-50ms] reads more credible at a 50ms glance.
- **Supersedes:** 2026-06-18-sans-default
```

- `id` is `<date>-<slug-of-title>`, unique. `prev` chains to the previous entry's hash
  (`GENESIS` for the first).
- **Why** carries an origin tag + its provenance ref (not just a label):
  - `[LENS-CITED canon:<principle-id>]` — a real id from the attention canon.
  - `[FORK-RESOLVED fork:<id>]` — a fork from `forks.md`.
  - `[GROUNDED grounding/<path>]` — a real grounding file.
  - `[FOUNDER-DECIDED founder]` or `[FOUNDER-DECIDED brief:<anchor>]`.
- **Supersedes** is `none` or an earlier entry's id.

## How to append (do not hand-edit)

Use the deterministic appender so the hash chain stays valid:

```
python3 scripts/check_decision_log.py append <project>/design-room/decisions.md \
  --date 2026-06-25 --title "serif over sans" \
  --decision "switch the display face to a serif" \
  --tag LENS-CITED --ref canon:lindgaard-2006-50ms \
  --why "reads more credible at a 50ms glance" \
  --supersedes 2026-06-18-sans-default
```

Validate any time: `python3 scripts/check_decision_log.py check <...>/decisions.md`.

## What the chain does (honest)

The chain catches accidental edits, deletions, and reorders of prior entries. It is
NOT cryptographic tamper-proofing — a determined editor could rewrite an entry and
recompute the downstream chain. **Commit `decisions.md` to git after each entry: git
history is the authoritative append-only audit.** The appender prints the new head
hash; pin it (`check --head <hash>`) for a terminal commitment.
