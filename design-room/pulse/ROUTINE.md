# Weekly modernity-pulse routine

The per-run design flow does ZERO web research — it reads the attention canon and the
build-palette. The palette is kept current by this **weekly pulse**: a scheduled job
researches new repos/trends and proposes promotions, so "what's modern" stays fresh
without slowing down every design session.

## What a weekly run does

1. **Research** the hottest new web-design repos this week (GitHub trending + the
   seed sources in `scripts/design_room_pulse.py`): liquid-glass / shaders / scroll /
   Tailwind UI kits / component grab-bags / the design.md ecosystem. ~6-10 candidates.
2. **Write candidates** to `design-room/pulse/candidates-<YYYY-MM-DD>.json`:
   a list of `{repo, stars, category, trend_noise}` (judge `trend_noise` = hype
   without staying power).
3. **Evaluate** (deterministic):
   `python3 scripts/design_room_pulse.py run --candidates <that file>
   --date <YYYY-MM-DD> --palette skill/references/build-palette.md
   --snapshot-dir design-room/pulse`. This writes `snapshot-<date>.json` (promoted +
   rejected, each WITH a reason) and bumps the palette's `Last refreshed:` date.
4. **Review the snapshot** and keep the promotions you want.

## Wiring it up

Run it however you schedule recurring jobs — a cron job, a CI workflow, or a Claude
Code cloud routine (`/schedule`). The deterministic part (evaluate/promote/reject) is
`design_room_pulse.py`; the research step that produces the candidates file is the
only part that touches the web, and it runs weekly, never per design session.

`design_room_pulse.py --selftest` runs the whole evaluate path offline against a
committed fixture, so the logic is testable without a network.
