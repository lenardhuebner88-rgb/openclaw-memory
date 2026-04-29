---
status: planned
owner: codex
created: 2026-04-29
priority: P1
---

# SystemJob Cron Migration

## Problem
Several recurring OpenClaw cron jobs were `agentTurn` jobs even though their
prompt only executed a deterministic shell script and returned `NO_REPLY` or a
single OK line. That creates model usage, isolated cron sessions, and worker-run
noise for work that does not need an LLM.

## Decision
Do not add hard token blocking. Move deterministic `RUN script` jobs to shell
execution while keeping OpenClaw run history compatible.

OpenClaw 2026.4.24 only supports native cron payload kinds `systemEvent` and
`agentTurn`. `systemEvent` injects text into the main session; it does not run
shell commands. Therefore this migration uses a small user-systemd runner:

- runner: `/home/piet/.openclaw/scripts/openclaw-systemjob-runner.py`
- source of truth: disabled OpenClaw jobs annotated with top-level `systemJob`
- run logs: `/home/piet/.openclaw/cron/runs/<jobId>.jsonl`
- usage: `input_tokens=0`, `output_tokens=0`, `total_tokens=0`

## Scope
Initial migrated jobs:

- `atlas-receipt-stream-subscribe`
- `m7-atlas-master-heartbeat.timer`
- `mc-task-parity-check-10min`

## Test Plan
- Python syntax check for the runner and tests.
- Unit tests:
  - runner writes a zero-token run log and updates job state.
  - runner fails if the configured success pattern is missing.
- Manual force run for each migrated job.
- Verify run logs contain `systemJob: true`, `provider: system`, `model: shell`,
  and `usage.total_tokens: 0`.
- Verify Mission Control health, worker proof, pickup proof, and failed
  `mc-worker-*` units after migration.

## Rollback
1. Stop and disable the three `openclaw-systemjob-*` timers.
2. Restore `/home/piet/.openclaw/cron/jobs.json` from the matching backup in
   `/home/piet/.openclaw/backups/`.
3. Run `systemctl --user daemon-reload`.
4. Confirm OpenClaw cron jobs are enabled again with `openclaw cron list`.

## Acceptance
- No OpenClaw `agentTurn` run is created for the migrated jobs after their next
  scheduled tick.
- Systemd timers execute the scripts successfully.
- Run logs continue to exist under the same job IDs with zero token usage.
- No Mission Control health regression.
