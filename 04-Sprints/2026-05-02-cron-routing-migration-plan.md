# 2026-05-02 Cron Routing Migration Plan

## Status

READ-ONLY PARTIAL. Live inventory completed, but mutations wait on preflight green. Preflight blocker: board open_count=8 and dirty Mission Control worktree.

## Live Counts

- User crontab active jobs: 50

- OpenClaw native cron jobs: 24

- Prompt expected 54 jobs, but live system exposes a larger combined surface; plan follows live truth.

## User Crontab Inventory

| cron-name | freq-old -> freq-new | owner-old -> owner-new | tier/risk | route | rationale |
| --- | --- | --- | --- | --- | --- |
| `flock` | `* * * * *` -> REDUCIBLE 1m->2m | MC-API | LOW | WEBHOOK/ALERT-or-DISCORD | Heartbeat can reduce to */2 if MC health remains ok. |
| `openclaw-config-guard.sh` | `* * * * *` -> KEEP-FREQ | KEEP-FREQ / DEFENSE | MEDIUM | NO-DISCORD | Defense/validator path; keep owner and frequency unless separate RCA. |
| `cost-alert-dispatcher.py` | `*/2 * * * *` -> REDUCIBLE */2->*/5 | WEBHOOK-ONLY | MEDIUM | WEBHOOK/ALERT-or-DISCORD | Webhook now set; reduce cadence after smoke, no Atlas route needed. |
| `mc-critical-alert.py` | `1-59/2 * * * *` -> REDUCIBLE */2->*/5 | SYSTEM-BOT-CANDIDATE | MEDIUM | WEBHOOK/ALERT-or-DISCORD | Alert path should be notify/system-bot, not Atlas fallback. |
| `memory-budget-meter.sh` | `*/5 * * * *` -> KEEP-FREQ | NO-DISCORD | LOW | NO-DISCORD | No obvious Atlas route; keep unless logs prove bootstraps. |
| `sprint-debrief-watch.sh` | `1-59/5 * * * *` -> KEEP-FREQ | NO-DISCORD | LOW | NO-DISCORD | No obvious Atlas route; keep unless logs prove bootstraps. |
| `atlas-orphan-detect.sh` | `*/10 * * * *` -> KEEP-FREQ | KEEP-FREQ / DEFENSE | MEDIUM | NO-DISCORD | Defense/validator path; keep owner and frequency unless separate RCA. |
| `session-health-monitor.py` | `*/10 * * * *` -> KEEP-FREQ | KEEP-FREQ / DEFENSE | MEDIUM | NO-DISCORD | Defense/validator path; keep owner and frequency unless separate RCA. |
| `self-optimizer.py` | `*/15 * * * *` -> KEEP-FREQ | NO-DISCORD | LOW | NO-DISCORD | No obvious Atlas route; keep unless logs prove bootstraps. |
| `r49-claim-validator.py` | `5-59/15 * * * *` -> KEEP-FREQ | KEEP-FREQ / DEFENSE | HIGH | NO-DISCORD | Defense/validator path; keep owner and frequency unless separate RCA. |
| `r48-board-hygiene-cron.sh` | `0 */1 * * *` -> KEEP-FREQ | KEEP-FREQ / DEFENSE | HIGH | OPENCLAW-CLI | Defense/validator path; keep owner and frequency unless separate RCA. |
| `memory-orchestrator.py` | `30 * * * *` -> KEEP-FREQ | KEEP-FREQ / DEFENSE | MEDIUM | NO-DISCORD | Defense/validator path; keep owner and frequency unless separate RCA. |
| `memory-orchestrator.py` | `45 2 * * *` -> KEEP-FREQ | KEEP-FREQ / DEFENSE | MEDIUM | NO-DISCORD | Defense/validator path; keep owner and frequency unless separate RCA. |
| `memory-orchestrator.py` | `0 5 * * 0` -> KEEP-FREQ | KEEP-FREQ / DEFENSE | MEDIUM | NO-DISCORD | Defense/validator path; keep owner and frequency unless separate RCA. |
| `memory-orchestrator.py` | `0 4 1 */3 *` -> KEEP-FREQ | KEEP-FREQ / DEFENSE | MEDIUM | NO-DISCORD | Defense/validator path; keep owner and frequency unless separate RCA. |
| `mc-ops-monitor.sh` | `0 * * * *` -> KEEP-FREQ | NO-DISCORD | LOW | NO-DISCORD | No obvious Atlas route; keep unless logs prove bootstraps. |
| `memory-size-guard.sh` | `7 */6 * * *` -> KEEP-FREQ | NO-DISCORD | LOW | NO-DISCORD | No obvious Atlas route; keep unless logs prove bootstraps. |
| `session-size-alert.sh` | `23,53 * * * *` -> KEEP-FREQ | REVIEW | LOW | WEBHOOK/ALERT-or-DISCORD | No obvious Atlas route; keep unless logs prove bootstraps. |
| `script-integrity-check.sh` | `0 */6 * * *` -> KEEP-FREQ | NO-DISCORD | LOW | NO-DISCORD | No obvious Atlas route; keep unless logs prove bootstraps. |
| `openclaw` | `0 */6 * * *` -> KEEP-FREQ | REVIEW | LOW | OPENCLAW-CLI | No obvious Atlas route; keep unless logs prove bootstraps. |
| `rules-render.sh` | `0 * * * *` -> KEEP-FREQ | NO-DISCORD | LOW | NO-DISCORD | No obvious Atlas route; keep unless logs prove bootstraps. |
| `qmd` | `*/30 * * * *` -> KEEP-FREQ | REVIEW | LOW | OPENCLAW-CLI | No obvious Atlas route; keep unless logs prove bootstraps. |
| `qmd-pending-monitor.sh` | `5 * * * *` -> KEEP/REDUCE case-by-case | NO-DISCORD | MEDIUM | NO-DISCORD | System notification/watch path; migrate Discord/agent-targeting to system-bot or webhook. |
| `pr68846-patch-check.sh` | `5-59/30 * * * *` -> KEEP/REDUCE case-by-case | NO-DISCORD | MEDIUM | NO-DISCORD | System notification/watch path; migrate Discord/agent-targeting to system-bot or webhook. |
| `minions-pr-watch.sh` | `23 * * * *` -> KEEP/REDUCE case-by-case | NO-DISCORD | MEDIUM | NO-DISCORD | System notification/watch path; migrate Discord/agent-targeting to system-bot or webhook. |
| `cleanup.sh` | `0 3 * * *` -> KEEP-FREQ | NO-DISCORD | LOW | NO-DISCORD | No obvious Atlas route; keep unless logs prove bootstraps. |
| `config-snapshot-to-vault.sh` | `0 3 * * *` -> KEEP-FREQ | NO-DISCORD | LOW | NO-DISCORD | No obvious Atlas route; keep unless logs prove bootstraps. |
| `build-artifact-cleanup.sh` | `0 3 * * 0` -> KEEP-FREQ | REVIEW | LOW | OPENCLAW-CLI | No obvious Atlas route; keep unless logs prove bootstraps. |
| `cron-health-audit.sh` | `10-59/30 * * * *` -> KEEP-FREQ | REVIEW | LOW | OPENCLAW-CLI | No obvious Atlas route; keep unless logs prove bootstraps. |
| `alert-dispatcher.sh` | `0 */6 * * *` -> KEEP/REDUCE case-by-case | SYSTEM-BOT-CANDIDATE | MEDIUM | WEBHOOK/ALERT-or-DISCORD | System notification/watch path; migrate Discord/agent-targeting to system-bot or webhook. |
| `session-janitor.py` | `15-59/30 * * * *` -> KEEP-FREQ | NO-DISCORD | LOW | NO-DISCORD | No obvious Atlas route; keep unless logs prove bootstraps. |
| `cpu-runaway-guard.sh` | `2-59/5 * * * *` -> KEEP-FREQ | KEEP-FREQ / DEFENSE | MEDIUM | NO-DISCORD | Defense/validator path; keep owner and frequency unless separate RCA. |
| `agents-md-size-check.sh` | `0 6 * * *` -> KEEP-FREQ | NO-DISCORD | LOW | NO-DISCORD | No obvious Atlas route; keep unless logs prove bootstraps. |
| `session-size-guard.py` | `3-59/5 * * * *` -> KEEP-FREQ | KEEP-FREQ / DEFENSE | MEDIUM | NO-DISCORD | Defense/validator path; keep owner and frequency unless separate RCA. |
| `session-size-guard.py` | `* * * * *` -> KEEP-FREQ | KEEP-FREQ / DEFENSE | MEDIUM | NO-DISCORD | Defense/validator path; keep owner and frequency unless separate RCA. |
| `qmd-native-embed-cron.sh` | `15,45 * * * *` -> KEEP-FREQ | REVIEW | LOW | OPENCLAW-CLI | No obvious Atlas route; keep unless logs prove bootstraps. |
| `mcp-qmd-reaper.sh` | `4-59/5 * * * *` -> KEEP-FREQ | KEEP-FREQ / DEFENSE | MEDIUM | NO-DISCORD | Defense/validator path; keep owner and frequency unless separate RCA. |
| `vault-search-daily-checkpoint.sh` | `0 8 * * *` -> KEEP-FREQ | NO-DISCORD | LOW | NO-DISCORD | No obvious Atlas route; keep unless logs prove bootstraps. |
| `mcp-taskboard-reaper.sh` | `*/5 * * * *` -> KEEP-FREQ | KEEP-FREQ / DEFENSE | MEDIUM | NO-DISCORD | Defense/validator path; keep owner and frequency unless separate RCA. |
| `session-rotation-watchdog.py` | `*/2 * * * *` -> REDUCIBLE */2->*/5 candidate | KEEP-FREQ / DEFENSE | MEDIUM | NO-DISCORD | Rotation guard should reduce only after session-size stability proof. |
| `per-tool-byte-meter.py` | `1-59/5 * * * *` -> KEEP-FREQ | NO-DISCORD | LOW | NO-DISCORD | No obvious Atlas route; keep unless logs prove bootstraps. |
| `architecture-snapshot-generator.py` | `20-59/30 * * * *` -> KEEP-FREQ | NO-DISCORD | LOW | NO-DISCORD | No obvious Atlas route; keep unless logs prove bootstraps. |
| `state-collector.py` | `* * * * *` -> REDUCIBLE 1m->2m | NO-DISCORD | LOW | NO-DISCORD | Collector only; can reduce to */2. |
| `arch-deploy-readiness-check.sh` | `2-59/5 * * * *` -> KEEP-FREQ | NO-DISCORD | LOW | NO-DISCORD | No obvious Atlas route; keep unless logs prove bootstraps. |
| `daily-ops-digest.py` | `05 21 * * *` -> KEEP/REDUCE case-by-case | NO-DISCORD | MEDIUM | NO-DISCORD | System notification/watch path; migrate Discord/agent-targeting to system-bot or webhook. |
| `gateway-memory-monitor.py` | `3-59/5 * * * *` -> KEEP/REDUCE case-by-case | SYSTEM-BOT-CANDIDATE | MEDIUM | OPENCLAW-CLI | System notification/watch path; migrate Discord/agent-targeting to system-bot or webhook. |
| `billing-alert-watch.sh` | `10-59/15 * * * *` -> KEEP/REDUCE case-by-case | SYSTEM-BOT-CANDIDATE | MEDIUM | WEBHOOK/ALERT-or-DISCORD | System notification/watch path; migrate Discord/agent-targeting to system-bot or webhook. |
| `crontab-schema-gate.sh` | `* * * * *` -> KEEP-FREQ | KEEP-FREQ / DEFENSE | MEDIUM | OPENCLAW-CLI | Defense/validator path; keep owner and frequency unless separate RCA. |
| `vault-frontmatter-validator.py` | `30 */6 * * *` -> KEEP-FREQ | REVIEW | LOW | OPENCLAW-CLI | No obvious Atlas route; keep unless logs prove bootstraps. |
| `cron-runs-tracker.py` | `*/15 * * * *` -> KEEP-FREQ | REVIEW | LOW | OPENCLAW-CLI | No obvious Atlas route; keep unless logs prove bootstraps. |

## OpenClaw Native Jobs

| job | id | sessionKey | delivery | owner decision | rationale |
| --- | --- | --- | --- | --- | --- |
| `daily-cost-report` | `69c22318-dfef-4905-a394-f3796fd496d9` | `agent:main:cron:daily-cost-report:run` | `announce/alerts` | SYSTEM-BOT-CANDIDATE | Native job targets main; migrate to system-bot if system/briefing, keep only if genuine Atlas user brief. |
| `morning-brief` | `8f69541c-6add-4da2-960c-d34f36f51eac` | `agent:main:cron:morning-brief:run` | `announce/atlas-main` | SYSTEM-BOT-CANDIDATE | Native job targets main; migrate to system-bot if system/briefing, keep only if genuine Atlas user brief. |
| `nightly-self-improvement` | `19047953-220e-4354-936d-be046b68723e` | `agent:main:cron:nightly-self-improvement:run` | `announce/other` | SYSTEM-BOT-CANDIDATE | Native job targets main; migrate to system-bot if system/briefing, keep only if genuine Atlas user brief. |
| `efficiency-auditor-heartbeat` | `5b6e3416-3164-4625-b04a-d806be4baeff` | `-` | `announce/alerts` | REVIEW | No explicit main route; inspect run log before migration. |
| `session-cleanup-local` | `19cd1425-5ba5-4cdf-abea-c13c46305e7a` | `agent:sre-expert:cron:session-cleanup-local:run` | `announce/alerts` | USER-AGENT-OWNED | Forge/SRE-owned cron; keep owner. |
| `evening-debrief` | `7ff84751-bd1d-4780-ac50-3b92b761d009` | `agent:main:cron:evening-debrief:run` | `announce/atlas-main` | SYSTEM-BOT-CANDIDATE | Native job targets main; migrate to system-bot if system/briefing, keep only if genuine Atlas user brief. |
| `Security-Weekly-Audit` | `security-weekly-audit` | `-` | `announce/alerts` | REVIEW | No explicit main route; inspect run log before migration. |
| `validate-models` | `881bd75e-191e-4f1e-b605-b9f8ec95795a` | `agent:main:cron:validate-models:run` | `announce/alerts` | SYSTEM-BOT-CANDIDATE | Native job targets main; migrate to system-bot if system/briefing, keep only if genuine Atlas user brief. |
| `learnings-to-tasks` | `learnings-to-tasks-001` | `agent:main:discord:channel:1486480128576983070` | `announce/other` | MAIN-REVIEW | Native job targets main; migrate to system-bot if system/briefing, keep only if genuine Atlas user brief. |
| `memory-rem-backfill` | `c49eb440-6a6d-49fb-9809-225d6ccfa463` | `-` | `none/none` | REVIEW | No explicit main route; inspect run log before migration. |
| `memory-sqlite-vacuum-weekly` | `af681204-978f-46cf-b793-a50376580291` | `agent:worker:openai:97426171-00c0-472b-aa23-8ac9fa759388` | `none/none` | REVIEW | No explicit main route; inspect run log before migration. |
| `mc-pending-pickup-smoke-hourly` | `0f9d0f2e-9839-4a14-ad18-cb75ff7f49c7` | `-` | `none/none` | REVIEW | No explicit main route; inspect run log before migration. |
| `mc-task-parity-check-10min` | `772cd431-dbfb-4d1b-8cc6-a0d25844c813` | `agent:sre-expert:main` | `none/none` | NO-DISCORD/SYSTEMJOB | Already migrated to shell/systemjob; keep. |
| `mcp-zombie-killer-hourly` | `26ed095e-a77a-4b3d-8b50-9ff06635cf92` | `agent:sre-expert:main` | `none/none` | USER-AGENT-OWNED | Forge/SRE-owned cron; keep owner. |
| `analytics-alert-watch` | `89cf60f9-40dd-4ee6-aaef-70e1048dd5c2` | `-` | `none/none` | REVIEW | No explicit main route; inspect run log before migration. |
| `check-forge-mini-fix-accept` | `a5a3d765-e9fd-454f-ab52-7e4f9687f701` | `agent:main:discord:channel:1486480128576983070` | `none/none` | MAIN-REVIEW | Native job targets main; migrate to system-bot if system/briefing, keep only if genuine Atlas user brief. |
| `check-direct-nudge-analysis-dispatch` | `467ebb07-bb0d-4621-b4a2-55c961111c11` | `agent:main:discord:channel:1486480128576983070` | `none/none` | MAIN-REVIEW | Native job targets main; migrate to system-bot if system/briefing, keep only if genuine Atlas user brief. |
| `streamable-http-soak-24h` | `streamable-http-soak-24h-1776863142` | `-` | `announce/alerts` | REVIEW | No explicit main route; inspect run log before migration. |
| `atlas-control-heartbeat-v1` | `0c96e2c6-2656-4947-ab4d-e565e4b44471` | `agent:main:cron:atlas-control-heartbeat-v1:disabled` | `-/none` | SYSTEM-BOT-CANDIDATE | Native job targets main; migrate to system-bot if system/briefing, keep only if genuine Atlas user brief. |
| `midday-brief` | `539c9a3d-f887-44e9-9a9b-6c009d16d107` | `agent:main:cron:midday-brief:run` | `announce/atlas-main` | SYSTEM-BOT-CANDIDATE | Native job targets main; migrate to system-bot if system/briefing, keep only if genuine Atlas user brief. |
| `daily-ops-digest` | `6d677504-db0a-42fc-bd4b-7c83f3896f22` | `agent:main:discord:channel:1486480128576983070` | `announce/atlas-main` | MAIN-REVIEW | Native job targets main; migrate to system-bot if system/briefing, keep only if genuine Atlas user brief. |
| `v3-sprint-watch-5min` | `cc21dba9-1f4d-43ce-a5a1-8bccaa7eb619` | `agent:main:discord:channel:1486480128576983070` | `none/none` | MAIN-REVIEW | Native job targets main; migrate to system-bot if system/briefing, keep only if genuine Atlas user brief. |
| `m7-atlas-master-heartbeat.timer` | `a61b4afe-c61b-4019-b4a5-1da4fad52b59` | `agent:sre-expert:main` | `none/none` | NO-DISCORD/SYSTEMJOB | Already migrated to shell/systemjob; keep. |
| `atlas-receipt-stream-subscribe` | `e74a9d69-8e83-42e2-bef4-4616e108187e` | `agent:sre-expert:main` | `none/none` | NO-DISCORD/SYSTEMJOB | Already migrated to shell/systemjob; keep. |

## Initial System-Bot Candidates

- `alert-dispatcher.sh`
- `atlas-control-heartbeat-v1`
- `billing-alert-watch.sh`
- `daily-cost-report`
- `evening-debrief`
- `gateway-memory-monitor.py`
- `mc-critical-alert.py`
- `midday-brief`
- `morning-brief`
- `nightly-self-improvement`
- `validate-models`

## Waits On Green

- Apply frequency reductions only after preflight blocker is cleared or incident override is documented.
- Apply routing migration only after Channel 1491 schema discovery and system-bot agent definition.
- No Defense-Cron disabled in this partial pass.
