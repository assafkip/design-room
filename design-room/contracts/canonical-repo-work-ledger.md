# Canonical Repo Work Ledger

Updated: 2026-07-01
Owner: Assaf Kipnis
Working repo for this ledger: `assafkip/design-room`

## Purpose

This file is the canonical memory for the repo sweep and update work.

Use it to resume from any repo without re-discovering:

- what was checked
- what was changed
- which branch, commit, and PR contain the work
- which tests passed
- what still needs a later pass

Keep this file append-only unless correcting a factual error.

## Resume Contract

For every repo, record:

- Repo name
- Local path or worktree path
- What the repo does
- Current GitHub state
- Decision
- Changes made
- Branch
- Commit
- PR
- Verification
- Dirty worktree caveats
- Remaining work

## GitHub Account State

- GitHub CLI is authenticated as `assafkip`.
- Visible personal repos: 65.
- Visible org: `KTLYST-Labs`.
- `KTLYST-Labs` had 0 visible repos during this pass.
- Initial GitHub repo checked: `assafkip/design-room`.
- `assafkip/design-room` had no open PRs, no open issues, and no GitHub Actions runs at inspection time.

## Source Reddit Mechanism

Canonical source repo:

- Repo: `assafkip/reddit-build-radar`
- Local path: `/Users/assafkipnis/projects/reddit-build-radar`
- Source branch: `feat/arctic-shift-collector`

Important source commits:

- `b0a693c` - Add Arctic Shift + PullPush Reddit collector
- `488850f` - Add 2-week backfill; drop redundant collect-time comment fetching
- `14166e2` - Speed up deep-read: concurrency + comment threshold

Canonical behavior:

- Use Arctic Shift first:
  - `https://arctic-shift.photon-reddit.com/api/posts/search`
- Use PullPush as fallback:
  - `https://api.pullpush.io/reddit/search/submission`
- Do not depend on direct Reddit `/hot.json`.
- Do not depend on Reddit RSS.
- Do not require Apify for Reddit collection.
- Keep repo-local query, subreddit, and scoring logic intact unless it is broken.

## Repo: assafkip/vc-signals

Local path:

- `/Users/assafkipnis/projects/_codex-worktrees/vc-signals-schedule`
- `/Users/assafkipnis/projects/_codex-worktrees/vc-signals-reddit`

What it does:

- VC and security investor signal dashboard.
- Large static data source in `signals-data.json`.
- Includes RSS, social, Reddit, and GTM-related collection paths.

GitHub state seen:

- No open PRs at first inspection.
- Open issue `#1`: stale daily scan reminder.
- Open issue `#2`: generic spam-looking quick question.
- `Signal Monitor` workflow last successful run seen on 2026-07-01.

Operational findings:

- `signals-data.json` had about 49,195 rows and was about 40 MB.
- Security-related signal data had 996 rows.
- LinkedIn/social scan metadata last run was 2026-02-05.
- GTM matching looked unused, with `pipeline_matches = 0`.
- Frequent bot commits were being produced by scheduled automation.

Decision:

- Keep the repo as the VC/security investor dashboard.
- Stop daily scheduled runs for now.
- Keep manual run functionality.
- Update the broken Reddit mechanism to the canonical Arctic Shift plus PullPush pattern.

Schedule pause change:

- Branch: `codex/pause-vc-signals-schedule`
- Commit: `5d89149` - Pause signal monitor schedule
- PR: `https://github.com/assafkip/vc-signals/pull/3`
- PR state: draft
- File changed: `.github/workflows/monitor.yml`
- Change: removed scheduled trigger, kept `workflow_dispatch`.
- Verification:
  - `schedule:` absent from workflow
  - `workflow_dispatch:` present

Reddit change:

- Branch: `codex/reddit-arctic-collector`
- Commit: `2df8bfa` - Use Arctic Reddit collection
- PR: `https://github.com/assafkip/vc-signals/pull/4`
- PR state: draft
- Main file changed: `scripts/live_monitor.py`
- Test file added: `scripts/test_reddit_collector.py`
- Verification:
  - `python3 scripts/test_reddit_collector.py` passed
  - `python3 -m py_compile scripts/live_monitor.py scripts/test_reddit_collector.py` passed
- Cleanup:
  - Removed own generated `scripts/__pycache__` after verification.

Remaining work:

- Decide whether issue `#1` should be closed by PR `#3` after merge.
- Decide whether issue `#2` should be closed as spam.
- Later pass can reduce or externalize the large `signals-data.json`.
- Later pass can revive or remove stale social and GTM paths.

## Repo: assafkip/competitive-analysis

Local path:

- `/Users/assafkipnis/projects/_codex-worktrees/competitive-analysis-reddit`

What it does:

- Competitive intelligence collection and analysis.
- Includes Reddit collection in the competitive intel pipeline.

Decision:

- Replace broken Reddit RSS collection with canonical Arctic Shift plus PullPush collection.

Reddit change:

- Branch: `codex/reddit-arctic-collector`
- Commit: `1b42b9f` - Use Arctic Reddit collection
- PR: `https://github.com/assafkip/competitive-analysis/pull/1`
- PR state: draft
- Main behavior changed:
  - Replaced `reddit_rss` collection path with Arctic Shift first, PullPush fallback.
  - Preserved existing collector output shape.

Verification:

- `PYTHONPATH=src uv run python -m pytest tests/test_competitive_intel.py -q`
- Result: 19 passed.

Dirty worktree caveat:

- Pre-existing untracked `output/` directory was present and ignored.

Remaining work:

- Review PR.
- Merge after checks or local review.

## Repo: assafkip/notebooklm-daily-podcast

Local path:

- `/Users/assafkipnis/projects/_codex-worktrees/notebooklm-daily-podcast-reddit`

What it does:

- Fetches sources for a NotebookLM daily podcast workflow.
- Had Reddit paths that were expected to stop working.

Decision:

- Route Reddit fetching through canonical Arctic Shift plus PullPush collection.
- Keep the existing CLI and self-test behavior.

Reddit change:

- Branch: `codex/reddit-arctic-collector`
- Commit: `a537ae9` - Use Arctic Reddit collection
- PR: `https://github.com/assafkip/notebooklm-daily-podcast/pull/1`
- PR state: draft
- Main file changed: `fetch_sources.py`
- Main behavior changed:
  - `fetch_reddit` now uses Arctic Shift first, PullPush fallback.
  - `reddit_apify` route also uses the same canonical fallback path.

Verification:

- `python3 fetch_sources.py selftest` passed.
- `bash tests/run_selftests.sh` passed.
- `python3 -m py_compile fetch_sources.py` passed.

Remaining work:

- Review PR.
- Merge after checks or local review.

## Repo: assafkip/random-stuff-ideas

Local path:

- `/Users/assafkipnis/projects/_codex-worktrees/random-stuff-ideas-reddit`

Base branch:

- `origin/feat/design-room-v2`

What it does:

- Mixed ideas repo with a GTM podcast source-fetching path.
- Contains another Reddit collection path under GTM scripts.

Decision:

- Patch the GTM podcast Reddit fetcher to use the canonical Reddit mechanism.

Reddit change:

- Branch: `codex/reddit-arctic-collector`
- Commit: `02465e6` - Use Arctic Reddit collection
- PR: `https://github.com/assafkip/random-stuff-ideas/pull/2`
- PR state: draft
- Main file changed: `gtm/scripts/podcast/fetch_sources.py`

Verification:

- `python3 gtm/scripts/podcast/fetch_sources.py selftest` passed.
- `python3 -m py_compile gtm/scripts/podcast/fetch_sources.py` passed.

Remaining work:

- Review PR.
- Merge after checks or local review.

## Repo: local kipi-system

Local path:

- `/Users/assafkipnis/projects/kipi-system`
- `/Users/assafkipnis/projects/_codex-worktrees/kipi-system-ci`

What it does:

- Founder OS skeleton and Kipi tooling.
- Includes local staged work for a competitive intel MCP path.

GitHub state seen:

- Public repo.
- Default branch: `main`.
- Open PR `#1`: `fix/portable-sed-inplace`.
- Open PR `#3`: `chore/sanitize-ktlyst-flavor`.
- Open issue `#2`: eliminate hardcoded paths, GitHub URLs, and instance-specific patterns.
- Recent `Skeleton Validation` runs on `main` were failing before PR `#4`.

Important caveat:

- The relevant competitive-intel files existed only as broad local staged `A` or `AM` work in the active dirty worktree.
- A clean worktree from `origin/main` did not contain:
  - `plugins/kipi-core/kipi-mcp/src/kipi_mcp/competitive_intel.py`
- Because of that, no branch, commit, or PR was created for this repo.
- The local dirty work was patched in place without staging ownership of unrelated changes.

Decision:

- Patch only the relevant local files.
- Do not stage, commit, or PR until the existing dirty worktree is intentionally organized.

Reddit change:

- Patched:
  - `/Users/assafkipnis/projects/kipi-system/plugins/kipi-core/kipi-mcp/src/kipi_mcp/competitive_intel.py`
  - `/Users/assafkipnis/projects/kipi-system/plugins/kipi-core/kipi-mcp/tests/test_competitive_intel.py`
- Status after patch showed both files as `AM`.

Verification:

- `PYTHONPATH=plugins/kipi-core/kipi-mcp/src uv run --with pyyaml --with pytest python -m pytest plugins/kipi-core/kipi-mcp/tests/test_competitive_intel.py -q -k reddit_uses_arctic`
- Result: 1 passed, 13 deselected, 1 warning.

CI fix:

- Clean worktree: `/Users/assafkipnis/projects/_codex-worktrees/kipi-system-ci`
- Branch: `codex/fix-skeleton-validation-lessons-scrub`
- Commit: `96f72d7` - fix: exempt lessons scrubber from skeleton leak scan
- PR: `https://github.com/assafkip/kipi-system/pull/4`
- PR state: draft
- Root cause:
  - `validate-separation.py 1 --verbose` failed because two intentional leak-detector files named blocked KTLYST tokens.
  - The validator already exempted `lessons-validator`, but not the newer `lessons_scrub` denylist and its test.
- File changed:
  - `validate-separation.py`
- Verification:
  - Before patch: `python3 validate-separation.py 1 --verbose` failed with 2 failures.
  - After patch: `python3 validate-separation.py 1 --verbose` passed with 60 pass, 0 fail, 1 advisory warning.
  - GitHub PR check `validate` passed on run `28545494154`.

Remaining work:

- Split or commit the broader staged local kipi-system work intentionally.
- Then create a clean branch and PR for the Reddit collector change if this code is meant to ship.
- Decide whether PR `#4` should be merged before or after the older portability/sanitization PRs.

## Repo: assafkip/qep-agent

Local path:

- `/Users/assafkipnis/projects/_codex-worktrees/qep-agent-inspect`

What it does:

- PureSpectrum QEP investigation agent.
- PSID context report generator using a local MongoDB stub and a 5-phase investigation flow.
- Includes webapp, Obsidian integration, reporting, learning store, and evaluation tests.

GitHub state seen:

- Private repo.
- Default branch: `main`.
- No open PRs.
- No open issues.
- No GitHub Actions runs were exposed by `gh run list`.
- Latest pushed commit seen in shallow clone: `3d382c8` - Commit the read-all-formats OE work into the qep repo (unbreak HEAD)

Aggregator scan:

- Searched for Reddit, RSS, LinkedIn, Twitter, X, social, GTM, feed, Apify, PullPush, Arctic, workflow dispatch, and schedule markers.
- No Reddit, RSS, GTM, Apify, Arctic, or PullPush collector path was found.
- Matches for `feed` and `social` were domain-language references inside the QEP investigation/product code, not external aggregators.

Decision:

- No Reddit migration needed.
- No daily schedule change needed.
- Record as inspected and continue the repo sweep.

Changes made:

- None.

Verification:

- `rg -n "reddit|rss|linkedin|twitter|x\\.com|social|gtm|feed|apify|pullpush|arctic|workflow_dispatch|schedule:" -S .`
- Result: only non-aggregator matches found.

Remaining work:

- None for this RSS/social/GTM/Reddit pass.

## Repo: assafkip/safe-autonomous-learning

Local path:

- `/Users/assafkipnis/projects/_codex-worktrees/safe-autonomous-learning-inspect`

What it does:

- Small public toolkit for safe cross-project autonomous learning.
- Contains three independent Python stdlib tools:
  - `client-data-gate`
  - `job-watchdog`
  - `auto-learn`

GitHub state seen:

- Public repo.
- Default branch: `master`.
- No open PRs.
- No open issues.
- No GitHub Actions runs were exposed by `gh run list`.
- Latest pushed commit seen in shallow clone: `3effcc4` - chore: ignore local marketing drafts (.drafts/)

Aggregator scan:

- Searched for Reddit, RSS, LinkedIn, Twitter, X, social, GTM, feed, Apify, PullPush, Arctic, workflow dispatch, schedule, and cron markers.
- No Reddit, RSS, social-media, GTM, Apify, Arctic, or PullPush collector path was found.
- `cron` appeared only in job-watchdog docs as an example platform reader.

Decision:

- No Reddit migration needed.
- No schedule pause needed.
- Record as inspected and continue the repo sweep.

Changes made:

- None.

Verification:

- `rg -n "reddit|rss|linkedin|twitter|x\\.com|social|gtm|feed|apify|pullpush|arctic|workflow_dispatch|schedule:|cron" -S .`
- Result: only job-watchdog cron documentation matched.

Remaining work:

- None for this RSS/social/GTM/Reddit pass.

## Repo: assafkip/design-room

Local path:

- `/Users/assafkipnis/projects/design-room`

What it does:

- Claude Code skill for evidence-bound web design.
- Includes deterministic checks for design contracts, grounded token provenance, decision logs, freshness, and anti-slop fixtures.

GitHub state seen:

- Public repo.
- Default branch: `master`.
- No open PRs.
- No open issues.
- No GitHub Actions runs were exposed by `gh run list`.
- Latest pushed commit seen locally: `2acd510` - design-room: design websites from evidence, not vibes

Aggregator scan:

- Searched for Reddit, RSS, LinkedIn, Twitter, X, social, GTM, feed, Apify, PullPush, Arctic, workflow dispatch, schedule, and cron markers.
- No Reddit, RSS, social-media, Apify, Arctic, or PullPush collector path was found.
- `GTM` appears only as a local path variable name in scripts.
- `cron` and schedule references appear only in the weekly pulse routine docs.
- The new canonical ledger itself contains many aggregator terms by design, so scan results should exclude this ledger file when checking repo behavior.

Decision:

- No Reddit migration needed.
- No daily schedule pause needed.
- Add this canonical repo work ledger as the durable cross-repo memory file.

Changes made:

- Added `design-room/contracts/canonical-repo-work-ledger.md`.
- Branch: `codex/canonical-repo-work-ledger`
- Commit: `421d259` - docs: add canonical repo work ledger
- PR: `https://github.com/assafkip/design-room/pull/1`
- PR state: draft

Verification:

- `rg -n "reddit|rss|linkedin|twitter|x\\.com|social|gtm|feed|apify|pullpush|arctic|workflow_dispatch|schedule:|cron" -S . -g '!design-room/contracts/canonical-repo-work-ledger.md'`
- Result: only `GTM` local variable names and pulse scheduling docs matched.
- `python3 -m pytest scripts/tests/ -q`
- Result: 58 passed.
- Non-ASCII dash and arrow check passed.

Remaining work:

- Keep appending repo findings to this ledger as the sweep continues.

## Repo: assafkip/interview-coach

Local path:

- `/Users/assafkipnis/projects/_codex-worktrees/interview-coach-inspect`

What it does:

- Claude Code interview coach.
- Runs mock interview practice, scores answers against cited techniques, and tracks weaknesses across sessions.

GitHub state seen:

- Public repo.
- Default branch: `master`.
- No open PRs.
- No open issues.
- No GitHub Actions runs were exposed by `gh run list`.
- Latest pushed commit seen in shallow clone: `8145437` - Add claudedaddy funnel footer

Aggregator scan:

- Searched for Reddit, RSS, LinkedIn, Twitter, X, social, GTM, feed, Apify, PullPush, Arctic, workflow dispatch, schedule, and cron markers.
- No Reddit, RSS, social-media, GTM, Apify, Arctic, or PullPush collector path was found.
- Matches were ordinary interview-coach text, mostly feedback language and example content.

Decision:

- No Reddit migration needed.
- No schedule pause needed.
- Record as inspected and continue the repo sweep.

Changes made:

- None.

Verification:

- `python3 test_score_answer.py`
- Result: passed.
- `python3 test_goal_tracker.py`
- Result: passed.

Remaining work:

- None for this RSS/social/GTM/Reddit pass.

## Repo: assafkip/Pure-spectrum-Q

Local path:

- `/Users/assafkipnis/projects/_codex-worktrees/Pure-spectrum-Q-inspect`

What it does:

- Private PureSpectrum Q-system engagement repo.
- Contains QEP project notes, PureSpectrum deliverables, Q-system skeleton files, marketing templates, and PRD/archive trails.

GitHub state seen:

- Private repo.
- Default branch: `main`.
- Open PR `#1`: `prd-os: QEP ticket-upload PRD + 3 issue specs + progress`.
- PR `#1` is mergeable and very large, about 66,415 additions and 495 deletions at inspection time.
- No open issues.
- No GitHub Actions runs were exposed by `gh run list`.
- Latest pushed commit seen in shallow clone: `9f16ec1` - QEP V1.5 webapp shipped: FastAPI + vanilla JS, full agent parity, demo-ready UI

Aggregator scan:

- Searched for Reddit, RSS, LinkedIn, Twitter, X, social, GTM, feed, Apify, PullPush, Arctic, workflow dispatch, schedule, and cron markers.
- Full-text scan found many marketing templates and Q-system docs mentioning Reddit, LinkedIn, X, RSS, and schedules.
- Executable-file scan did not find a live Reddit or RSS collector path.
- No Arctic or PullPush code path was found on `main`.

Decision:

- No Reddit migration needed on the inspected `main` checkout.
- No schedule pause needed.
- Open PR `#1` should be treated separately as a broad PRD/archive trail, not part of the Reddit migration.

Changes made:

- None.

Verification:

- Executable scan:
  - `rg -n "reddit|rss|linkedin|twitter|x\\.com|social|gtm|feed|apify|pullpush|arctic|workflow_dispatch|schedule:|cron" -S -g '*.py' -g '*.sh' -g '*.js' -g '*.ts' -g '*.yml' -g '*.yaml' .`
- Result:
  - Only design/template/helper references matched.
  - No collector migration target found.

Remaining work:

- Decide separately whether to review or merge PR `#1`.
- None for this RSS/social/GTM/Reddit pass.

## Repo: assafkip/kipi-accountant

Local path:

- `/Users/assafkipnis/projects/_codex-worktrees/kipi-accountant-inspect`

What it does:

- Private personal finance/accounting app and Q-system instance.
- Includes a Tauri app, finance provider code, Q-system content, and a Kipi MCP harvest plugin.

GitHub state seen:

- Private repo.
- Default branch: `master`.
- No open PRs before this pass.
- No open issues.
- Latest exposed workflow: `Dependency Graph`, success on 2026-06-29.
- Latest pushed commit seen before patch: 2026-06-30 on `master`.

Aggregator scan:

- Full-text scan found many Q-system marketing templates and source configs mentioning Reddit, LinkedIn, X, RSS, and social workflows.
- Live source configs existed under `plugins/kipi-core/kipi-mcp/sources/`.
- Two Reddit sources were live and used the broken Reddit MCP mechanism:
  - `reddit-leads.yaml`
  - `reddit-subs.yaml`
- Both used:
  - `method: mcp`
  - `server: reddit`
  - `tool: fetch_hot_threads`

Decision:

- Migrate the live Reddit source manifests off the Reddit MCP path.
- Keep existing source names, environment-driven subreddit configuration, full-text output, and schedule metadata.
- Add a repo-local `reddit_archive` source method that executes in Python.

Reddit change:

- Branch: `codex/reddit-arctic-sources`
- Commit: `bf2423b` - fix: use archive Reddit sources
- PR: `https://github.com/assafkip/kipi-accountant/pull/1`
- PR state: draft
- GitHub checks: none reported on the branch.

Files changed:

- `plugins/kipi-core/kipi-mcp/sources/reddit-leads.yaml`
- `plugins/kipi-core/kipi-mcp/sources/reddit-subs.yaml`
- `plugins/kipi-core/kipi-mcp/src/kipi_mcp/source_registry.py`
- `plugins/kipi-core/kipi-mcp/src/kipi_mcp/harvest_orchestrator.py`
- `plugins/kipi-core/kipi-mcp/src/kipi_mcp/executors/reddit_archive_executor.py`
- `plugins/kipi-core/kipi-mcp/tests/test_source_registry.py`
- `plugins/kipi-core/kipi-mcp/tests/test_reddit_archive_executor.py`

Verification:

- Targeted Reddit/schema tests:
  - `PYTHONPATH=src uv run --with pytest --with pytest-asyncio --with httpx --with pyyaml --with pydantic --with tenacity --with feedparser python -m pytest tests/test_reddit_archive_executor.py tests/test_source_registry.py -q`
  - Result: 25 passed.
- Python compile:
  - `PYTHONPATH=src python3 -m py_compile src/kipi_mcp/source_registry.py src/kipi_mcp/harvest_orchestrator.py src/kipi_mcp/executors/reddit_archive_executor.py tests/test_reddit_archive_executor.py tests/test_source_registry.py`
  - Result: passed.
- Harvest orchestrator tests:
  - `PYTHONPATH=src uv run --with pytest --with pytest-asyncio --with httpx --with pyyaml --with pydantic --with tenacity --with feedparser python -m pytest tests/test_harvest_orchestrator.py -q`
  - Result: 11 passed.
- Broad suite excluding known stale integration harness:
  - `PYTHONPATH=src uv run --with pytest --with pytest-mock --with pytest-asyncio --with httpx --with pyyaml --with pydantic --with tenacity --with feedparser --with apify-client --with google-analytics-data --with google-auth python -m pytest tests -q --ignore=tests/test_server_integration.py`
  - Result: 661 passed.

Known existing harness drift:

- Full Kipi MCP suite still fails in `tests/test_server_integration.py`.
- Failure 1: hardcoded cwd `/Users/ike/code/kipi-system/kipi-mcp` does not exist here.
- Failure 2: expected tool count is stale by 3 LinkedIn tools.
- These failures are unrelated to the Reddit archive source change.

Remaining work:

- Decide separately whether to fix the stale integration harness.
- Review and merge PR `#1`.

## Repo: assafkip/facebook-ads-library-search

Local path:

- `/Users/assafkipnis/projects/_codex-worktrees/facebook-ads-library-search-inspect`

What it does:

- Private ad-library search and normalization toolkit.
- Captures public Meta Ad Library evidence and includes scaffolded TikTok, Google Ads, and X Ads Repository probes.

GitHub state seen:

- Private repo.
- Default branch: `main`.
- No open PRs.
- No open issues.
- No GitHub Actions runs were exposed by `gh run list`.
- Latest pushed commit seen in shallow clone: `0a44326` - Add cross-platform ad detail enrichment

Aggregator scan:

- Searched for Reddit, RSS, LinkedIn, Twitter, X, social, GTM, feed, Apify, PullPush, Arctic, workflow dispatch, schedule, and cron markers.
- The repo has collector-style scripts for Meta, TikTok, Google Ads, and X Ads Repository.
- No Reddit source or Reddit collector path was found.
- X/Twitter matches are for X Ads Repository capture, not the broken Reddit mechanism.

Decision:

- No Reddit migration needed.
- No schedule pause needed.
- Record as inspected and continue the repo sweep.

Changes made:

- None.

Verification:

- `python3 -m pytest tests -q`
- Result: 5 passed.

Remaining work:

- None for this RSS/social/GTM/Reddit pass.

## Current Sweep Cursor

Last active repo focus:

- `assafkip/facebook-ads-library-search`

Next repo to inspect in the original GitHub repo sweep:

- `assafkip/ti-weekly-agent`

Current global open loop:

- Continue repo-by-repo inspection.
- For each RSS, social media, GTM, or Reddit aggregator, compare against:
  - `assafkip/vc-signals`
  - `assafkip/reddit-build-radar`
  - any other aggregator already patched in this ledger
- Keep daily schedule functionality disabled where the founder asked for it, but preserve manual execution.
- Migrate broken Reddit mechanisms to Arctic Shift plus PullPush.

## PR Index

- `assafkip/vc-signals` schedule pause: `https://github.com/assafkip/vc-signals/pull/3`
- `assafkip/vc-signals` Reddit migration: `https://github.com/assafkip/vc-signals/pull/4`
- `assafkip/competitive-analysis` Reddit migration: `https://github.com/assafkip/competitive-analysis/pull/1`
- `assafkip/notebooklm-daily-podcast` Reddit migration: `https://github.com/assafkip/notebooklm-daily-podcast/pull/1`
- `assafkip/random-stuff-ideas` Reddit migration: `https://github.com/assafkip/random-stuff-ideas/pull/2`
- `assafkip/kipi-system` CI fix: `https://github.com/assafkip/kipi-system/pull/4`
- `assafkip/design-room` canonical ledger: `https://github.com/assafkip/design-room/pull/1`
- `assafkip/kipi-accountant` Reddit migration: `https://github.com/assafkip/kipi-accountant/pull/1`

## Verification Index

- `vc-signals`: Reddit unit script passed.
- `vc-signals`: Python compile passed.
- `vc-signals`: schedule trigger check passed.
- `competitive-analysis`: targeted pytest passed, 19 tests.
- `notebooklm-daily-podcast`: selftest passed.
- `notebooklm-daily-podcast`: shell selftests passed.
- `notebooklm-daily-podcast`: Python compile passed.
- `random-stuff-ideas`: selftest passed.
- `random-stuff-ideas`: Python compile passed.
- `kipi-system`: targeted pytest passed, 1 selected test.
- `kipi-system`: `validate-separation.py 1 --verbose` passed after CI fix.
- `kipi-system`: PR `#4` GitHub check `validate` passed.
- `design-room`: scripts test suite passed, 58 tests.
- `interview-coach`: score-answer test passed.
- `interview-coach`: goal-tracker test passed.
- `kipi-accountant`: targeted Reddit/schema tests passed, 25 tests.
- `kipi-accountant`: harvest orchestrator tests passed, 11 tests.
- `kipi-accountant`: broad Kipi MCP suite passed with stale integration harness excluded, 661 tests.
- `facebook-ads-library-search`: pytest suite passed, 5 tests.

## Canonical Next-Step Checklist

- Inspect `assafkip/ti-weekly-agent`.
- Identify whether it is RSS, social, GTM, Reddit, or unrelated.
- Record findings in this ledger before switching repos.
- If it needs code work, create a scoped branch from the correct base.
- Patch only the broken mechanism.
- Run deterministic verification.
- Open a draft PR.
- Append the branch, commit, PR, and verification here.
