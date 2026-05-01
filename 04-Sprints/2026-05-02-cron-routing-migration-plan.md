# 2026-05-02 Cron Routing Migration Plan

Status: PARTIAL, read-only inventory completed. No cron/config mutation was applied because `pre-flight-sprint-dispatch.sh` is RED.

## Gate State

- Gateway health: live.
- Mission Control health: ok/ok.
- Build process: none running.
- Gateway CPU at inventory time: about 86% while MC reports no active work.
- Preflight: RED.
  - Gate 3: board open_count=8 too high.
  - Gate 6: git has 40 real-dirty Mission Control files.
- `session.maintenance` live config currently has `pruneAfter=2d`, `maxEntries=60`; no live reversion to `14d/150` was observed in this read-only pass.

## Source Inventory

Live scheduling is split across three surfaces, not one list:

- OpenClaw cron jobs: 24 jobs in `/home/piet/.openclaw/cron/jobs.json`.
- User crontab: 50 active entries in `crontab -l`.
- systemd user timers: 22 timers.

The earlier target "54 crons" does not match the current live source-of-truth. The nearest current count is 50 active user-crontab entries plus OpenClaw/systemd timers.

## OpenClaw Jobs

| job | enabled | old owner | proposed owner | tier | risk | decision |
|---|---:|---|---|---|---|---|
| daily-cost-report | yes | main | system-bot | T8 daily | medium | SYSTEM-BOT-CANDIDATE. It is a system cost report, not a user turn. |
| morning-brief | yes | main | main | T8 daily | medium | Keep Atlas-owned; operator-facing narrative. |
| nightly-self-improvement | yes | main | main or system-bot after review | T8 daily | high | Defer. It may create work and needs separate governance. |
| efficiency-auditor-heartbeat | yes | efficiency-auditor | efficiency-auditor | T8 daily | low | USER-AGENT-OWNED. |
| session-cleanup-local | yes | sre-expert | sre-expert | T6 8h | low | Already moved away from main; keep. |
| evening-debrief | yes | main | main | T8 daily | medium | Keep Atlas-owned; operator-facing summary. |
| Security-Weekly-Audit | yes | sre-expert | sre-expert | T8 weekly | low | USER-AGENT-OWNED. |
| validate-models | yes | main | system-bot or sre-expert | T8 daily | medium | SYSTEM-BOT-CANDIDATE. System validation should not bootstrap Atlas. |
| learnings-to-tasks | yes | main | main for now | T8 daily | medium | Defer. It creates drafts and needs operator semantics. |
| memory-rem-backfill | yes | main | no change until Memory review | T8 daily | high | Memory-L1-L6 related; do not migrate blindly. |
| memory-sqlite-vacuum-weekly | yes | worker | worker | T8 weekly | low | NO-DISCORD/maintenance. |
| mc-pending-pickup-smoke-hourly | yes | sre-expert | sre-expert | T7 hourly | low | Defense/worker smoke; keep. |
| mcp-zombie-killer-hourly | yes | sre-expert | sre-expert | T7 hourly | low | Defense; keep. |
| midday-brief | yes | main | main | T8 daily | medium | Keep Atlas-owned; operator-facing summary. |
| daily-ops-digest | yes | main | system-bot or direct script | T8 daily | medium | SYSTEM-BOT-CANDIDATE if generated without user interaction. |
| disabled jobs | no | mixed | no change | n/a | low | Leave disabled. |

## User Crontab Decisions

| cron line / name | old freq -> proposed freq | owner old -> new | tier | risk | decision |
|---|---|---|---|---|---|
| mc-heartbeat-main | `* * * * *` -> `*/2 * * * *` | MC API -> MC API | T2 -> T3 | low | REDUCIBLE. Health API is already live-polled elsewhere. |
| openclaw-config-guard | `* * * * *` -> keep | config guard -> config guard | T2 | high | Defense/schema guard; do not touch. |
| cost-alert-dispatcher | `*/2 * * * *` -> `*/5 * * * *` | webhook-only -> webhook-only | T3 -> T4 | medium | REDUCIBLE. It uses webhook path when configured; no Atlas bootstrap needed. |
| mc-critical-alert | `1-59/2 * * * *` -> `*/5 * * * *` | alert-dispatcher -> alert-dispatcher | T3 -> T4 | medium | REDUCIBLE after smoke. Direct alert path remains. |
| memory-budget-meter | keep | file/log -> file/log | T4 | medium | Defense signal for session rotation; keep. |
| sprint-debrief-watch | keep | script -> Discord/summary | T4 | medium | Existing operator loop; keep until result-watcher consolidation review. |
| atlas-orphan-detect | keep | defense -> defense | T5 | high | Explicitly protected by sprint rules. |
| session-health-monitor | keep | defense -> defense | T5 | high | Defense; keep. |
| self-optimizer | keep | dry-run -> dry-run | T6 | medium | Already low frequency. |
| r49-claim-validator | keep | defense -> defense | T6 | high | Protected validator. |
| r48-board-hygiene-cron | keep | defense -> defense | T7 | high | Protected validator. |
| memory-orchestrator hourly/nightly/weekly/quarterly | keep | memory -> memory | T7/T8 | high | Memory-L1-L6 protected. |
| mc-ops-monitor | keep | monitor -> monitor | T7 | low | Hourly, not bootstrap-heavy. |
| memory-size-guard/session-size-alert | keep | guard -> guard | T7 | medium | Low frequency. |
| script-integrity-check | keep | integrity -> integrity | T6 | high | Defense. |
| openclaw sessions cleanup | keep until Phase A | maintenance -> maintenance | T6 | medium | Relevant to session lock/maintenance drift; Phase A owns it. |
| rules-render | keep | rules -> rules | T7 | medium | Rules path; not routing. |
| qmd-update | keep | qmd -> qmd | T6 | medium | QMD maintenance; not routing. |
| qmd-pending-monitor | keep | alert-dispatcher -> alert-dispatcher | T7 | medium | Alert-only; no agent bootstrap observed. |
| pr68846-patch-check | keep | webhook-only -> webhook-only | T6 | low | Webhook-only. |
| minions-pr-watch | keep | webhook-only -> webhook-only | T7 | low | Webhook-only. |
| cleanup/config-snapshot/build-artifact-cleanup | keep | maintenance -> maintenance | T8 | low | Daily/weekly only. |
| cron-health-audit | keep | log/report -> log/report | T6 | medium | Auditing. |
| canary-alert | keep | alert-dispatcher -> alert-dispatcher | T6 | low | Webhook/MC alert only. |
| session-janitor | keep | maintenance -> maintenance | T6 | medium | Session hygiene. |
| cpu-runaway-guard | keep | defense -> defense | T4 | high | Protected defense cron. |
| agents-md-size-check | keep | size check -> size check | T8 | low | Daily. |
| session-size-guard | keep | defense -> defense | T4 | high | Protected defense cron. |
| session-size-guard-immediate | `* * * * *` -> `*/5 * * * *` | log-only -> log-only | T2 -> T4 | low | REDUCIBLE. There is already a 5-min guard. |
| qmd-native-embed-cron | keep | qmd -> qmd | T6 | medium | Not routing. |
| mcp-qmd-reaper | keep | defense -> defense | T4 | high | Protected reaper. |
| vault-search-daily-checkpoint | keep | vault -> vault | T8 | low | Daily. |
| mcp-taskboard-reaper | keep | defense -> defense | T4 | high | Protected reaper. |
| session-rotation-watchdog | `*/2 * * * *` -> `*/5 * * * *` only after lock RCA | session defense -> session defense | T3 -> T4 | high | Do not change before Phase C; it is directly involved in session symptoms. |
| per-tool-byte-meter | keep | meter -> meter | T4 | medium | Observability. |
| architecture-snapshot | keep | snapshot -> snapshot | T6 | low | Every 30 minutes. |
| state-collector | `* * * * *` -> `*/2 * * * *` | state -> state | T2 -> T3 | low | REDUCIBLE. File-only collector. |
| arch-readiness | keep | readiness -> readiness | T4 | medium | Observability. |
| daily-ops-digest.py | keep schedule; route review | direct MC Discord -> audit/main depending mode | T8 | medium | Candidate for system-bot/direct script semantics, not Atlas bootstrap. |
| gateway-memory-monitor | keep | webhook-only -> webhook-only | T4 | medium | Monitor relevant to Phase B. |
| billing-alert-watch | keep | alert-dispatcher -> alert-dispatcher | T6 | low | Alert-only. |
| crontab-schema-gate | `* * * * *` -> no change now | schema guard -> schema guard | T2 | high | Prompt suggested reduction, but sprint hard rules protect self-validation. |
| vault-frontmatter-validator | keep | validator -> validator | T6 | medium | Every 6h. |
| cron-runs-tracker | keep | tracker/alert -> tracker/alert | T6 | medium | Useful for this sprint. |

## systemd User Timers

| timer | cadence | decision |
|---|---:|---|
| m7-auto-pickup.timer | ~1 min | Keep. Auto-pickup is protected. |
| m7-plan-runner.timer | ~1 min | Keep until separate plan-runner audit. |
| openclaw-systemjob-atlas-receipt-stream-subscribe.timer | 5 min | Keep but include in Phase B/C profiling; recent logs show cleanup timeout. |
| openclaw-systemjob-m7-atlas-master-heartbeat.timer | 5 min | Keep but include in Phase B/C profiling; recent logs show cleanup timeout. |
| anomaly-watch.timer/result-watcher.timer | 5 min | Keep. Operator-awareness path. |
| m7-session-freeze-watcher/stale-lock-cleaner/worker-monitor | 5 min | Keep. Defense/worker path. |
| openclaw-systemjob-mc-task-parity-check.timer | 10 min | Keep. Defense parity. |
| canary-session-rotation-watchdog/canary-session-size-guard | 10 min | Keep. Canary path. |
| forge-heartbeat.timer | hourly | Keep Forge-owned. |
| daily/session health/logrotate/researcher timers | daily or longer | Keep. |

## Routing Notes

- `/home/piet/.openclaw/workspace/discord-routing.json` has fallback `{agent: main, model: openrouter/moonshotai/kimi-k2.5}`.
- Channel `1491148986109661334` is not mapped there, so it is still a routing hazard if used as inbound user/system event.
- `/home/piet/.openclaw/openclaw.json` currently does not contain channel `1491148986109661334` under `channels.discord.guilds.1486464140246520068.channels`.
- No `system-bot` agent exists in current live `openclaw.json`.
- Existing channel bindings for Atlas/Forge/Pixel are in `workspace/discord-routing.json`, not in `openclaw.json`.

## Proposed Migration Sequence

1. Do not mutate cron while preflight is RED.
2. Resolve or explicitly waive Gate 3 and Gate 6 before config/script mutations.
3. In the A-E RCA sprint, first isolate Gateway CPU/lock/bootstrap hot path.
4. Only after the hot path is known, apply the low-risk frequency reductions:
   - `mc-heartbeat-main`: 1min -> 2min.
   - `state-collector`: 1min -> 2min.
   - `session-size-guard-immediate`: 1min -> 5min.
   - `cost-alert-dispatcher`: 2min -> 5min.
   - `mc-critical-alert`: 2min -> 5min after smoke.
5. Keep protected defense/self-validation crons unchanged unless a later RCA proves they are the hot loop.
6. Add explicit safe handling for `1491148986109661334` only after schema discovery; preferred target is a lightweight notify-only/system path, not Atlas.

## Rollback Plan

- Crontab changes: restore from timestamped `crontab.bak-*`.
- OpenClaw job changes: restore `/home/piet/.openclaw/cron/jobs.json` backup.
- `openclaw.json` changes: restore timestamped backup, run `openclaw doctor`, restart gateway only if schema clean.
- Routing JSON changes: restore timestamped routing backup and restart only the affected service.

