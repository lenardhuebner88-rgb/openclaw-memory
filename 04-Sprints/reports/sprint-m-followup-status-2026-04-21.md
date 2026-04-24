---
title: Sprint-M Follow-up Status — 2026-04-21
status: report
---

# Sprint-M Follow-up Status — 2026-04-21

## Snapshot

Verdict remains `READY-WITH-KNOWN-GAPS`.

Fresh checks on 2026-04-21:

- `bash /home/piet/.openclaw/scripts/cron-health-audit.sh` produced a fresh run at `2026-04-21T09:29:30Z`.
- `python3 /home/piet/.openclaw/cron/registry-validate.py` is green with `crontab=40`, `systemd-timer=6`, `openclaw-cron=16`.
- `python3 /home/piet/.openclaw/cron/cron-reconciler.py --dry-run` on live crontab is **not** green. Current drift is exactly one entry:
  - `missing_in_registry`
  - live command: `/home/piet/.openclaw/scripts/qmd-native-embed-cron.sh`
  - live schedule: `15,45 * * * *`

## Current Restpunkte

### 1. QMD Registry Drift

Current highest-priority normalization item before further sprint work:

- Live crontab contains `15,45 * * * * /home/piet/.openclaw/scripts/qmd-native-embed-cron.sh`
- `registry.jsonl` contains `qmd-update` and `qmd-pending-monitor`, but no active `qmd-native-embed` cron entry
- Result: reconciler reports one live drift

Decision needed:

- Either model `qmd-native-embed-cron.sh` as an active registry entry
- Or remove the live cron if the runner is no longer meant to be scheduled

Until that is normalized, the scheduler contract is not fully closed.

### 2. Memory Orchestrator

Root cause identified and fixed locally in `/home/piet/.openclaw/workspace/scripts/memory-orchestrator.py`.

Facts:

- The cron wrapper already held `/tmp/memory-orchestrator-<phase>.lock` via `/usr/bin/flock`
- The Python script tried to lock the same file again
- Wrapped runs therefore self-blocked with `[skip] lock busy`

Current status:

- Unwrapped dry-run is green
- Wrapped `hourly --dry-run` is green
- Wrapped `nightly --dry-run` is green and replays the expected 11 legacy steps
- A real live-fire verification for the next hourly slot is still pending

### 3. Audit Residuals

Fresh audit at `2026-04-21T09:29:30Z` shows:

- 4 missing log files
- 4 stale jobs
- 0 logs with errors

Interpretation:

- `build-artifact-cleanup` plus `memory-orchestrator nightly/weekly/quarterly` are still first-fire / cadence issues
- `mc-critical-alert`, `openclaw-config-guard`, and `sprint-debrief-watch` remain audit-side stale artifacts, not confirmed technical outages
- `cpu-runaway-guard` remains utility-style stale and is not currently treated as a sprint blocker

### 4. Versioning Status of memory-orchestrator.py

Path is canonically correct:

- `/home/piet/.openclaw/workspace/scripts/memory-orchestrator.py`

Git status inside `/home/piet/.openclaw/workspace`:

- file is currently untracked
- file is not ignored by git
- file has no git history yet
- other files in `scripts/` are tracked normally

Conclusion:

- The file is **not** intentionally unversioned from git's perspective
- It is in the right runtime location, but repository hygiene is incomplete
- This should be resolved deliberately later together with the broader dirty worktree, not ad hoc

## Recommended Next Order

1. Normalize the `qmd-native-embed` registry drift
2. Verify one real `memory-orchestrator hourly` live-fire
3. Re-run audit and reconciler after the QMD registry decision
4. Defer git hygiene for `memory-orchestrator.py` until the worktree cleanup is intentional
