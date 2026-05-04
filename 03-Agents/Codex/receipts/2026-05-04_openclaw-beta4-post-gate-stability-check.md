# OpenClaw beta.4 Post-Gate Stability Check - 2026-05-04

Window:
- Primary: since Gateway restart `2026-05-04 12:09:24 CEST` / `2026-05-04T10:09:24Z`
- Secondary: last 90 minutes

Mode:
- Read-only checks only.
- No Gateway restart.
- No Mission Control restart.
- No `--live` cleanup.
- No `sessions.json`, `jobs.json`, or `openclaw.json` mutation.
- No `.jsonl` history deletion.

## Verdict

- Gateway: GREEN
- Atlas/main: GREEN
- Forge/sre-expert: GREEN
- Other agents: GREEN
- Session Store: GREEN
- Timers/Guards: YELLOW
- Cronjobs: YELLOW
- Mission Control Board: GREEN
- Logs since Restart: GREEN
- Overall: YELLOW

Yellow reasons:
- `m7-mc-watchdog.service` is in failed state: `ExecMainStatus=1`, `NRestarts=8`.
- Two enabled cron jobs still use Minimax models: `efficiency-auditor-heartbeat`, `mc-pending-pickup-smoke-hourly`.
- Last 90 minutes contain pre-restart Minimax provider errors at `2026-05-04 12:00:01 CEST`; no matching current errors after `12:09:24 CEST`.

## Metrics

- OpenClaw version: `OpenClaw 2026.5.3-beta.4 (c6c64e2)`
- Gateway uptime since: `Mon 2026-05-04 12:09:24 CEST`
- Gateway `NRestarts`: `0`
- Gateway health: `{"ok":true,"status":"live"}`
- Gateway process: `MainPID=882905`, RSS about `571424 KB`
- Timeout/fallback events since restart: `0`
- Current watcher events since `2026-05-04T10:09:24Z`: `0`
- Historical watcher event before restart: Atlas FailoverError at `2026-05-04T09:40:23Z`
- Guard findings: `0`
- Guard load errors: `0`
- Guard scanned stores: `10`
- Enabled cronjobs: `14`
- Enabled Minimax cronjobs: `2`
- Failed systemd user units: `1` (`m7-mc-watchdog.service`)
- Open Mission Control tasks: `0`
- Dispatched tasks: `0`
- In-progress tasks: `0`
- Open worker-runs: `0`
- Duplicate open worker sessions: `0`
- Board consistency issues: `0`
- Runtime failures endpoint, 30m window: `0`

## Evidence

Mission Control:
- `/api/health`: status `ok`; `openTasks=0`, `inProgress=0`, `pendingPickup=0`, `failed=0`, `orphanedDispatches=0`, `staleOpenTasks=0`.
- `/api/board-consistency`: raw and normalized `status=ok`, `issueCount=0`.
- `/api/ops/openclaw/session-health`: 3 sessions, suspected stuck `0`, with errors `0`.
- `/api/ops/openclaw/model-runtime-failures`: `counts={}`, `events=[]`.
- Board data files parsed read-only from `/home/piet/.openclaw/state/mission-control/data`.
- No active matching Board task was found for this post-gate check; Board task recommended if this should become recurring.

Effective config:
- `agents.defaults.timeoutSeconds=600`
- `agents.defaults.agentRuntime.id=codex`
- `agents.defaults.model.primary=openai/gpt-5.4-mini`
- Atlas primary model: `openai/gpt-5.5`
- Forge primary model: `openai/gpt-5.3-codex`
- Agents listed: `main`, `sre-expert`, `frontend-guru`, `efficiency-auditor`, `james`, `system-bot`, `spark`

Session store:
- Atlas key: `agent:main:discord:channel:1486480128576983070`
- Atlas sessionId: `29e5f70f-809f-442d-8f9c-0517500352f9`
- Atlas status: `running`
- Atlas model: `gpt-5.5`
- Atlas cacheRead/totalTokens: `75648` / `76331`
- Atlas override red flag: no
- Forge Discord session count: `0`
- Other Discord agent session counts: `0`
- All-agent guard dry-run: `ok=true`, `rotationNeeded=0`, `wouldRotateSessionKeys=[]`, `loadErrors=[]`

Timers and guards:
- `canary-atlas-discord-fallback-chain-watch.service`: `Result=success`, `ExecMainStatus=0`
- `canary-openclaw-discord-fallback-chain-watch.service`: `Result=success`, `ExecMainStatus=0`
- `canary-session-rotation-watchdog.service`: `Result=success`, `ExecMainStatus=0`
- `canary-atlas-discord-stability-guard.service`: `Result=success`, `ExecMainStatus=0`
- `canary-session-size-guard.service`: `Result=success`, `ExecMainStatus=0`
- `canary-session-janitor.service`: `Result=success`, `ExecMainStatus=0`
- `openclaw-stale-task-run-sweeper.service`: `Result=success`, `ExecMainStatus=0`
- `m7-mc-watchdog.service`: `failed`, `ExecMainStatus=1`, `NRestarts=8`

Script compile gate:
- `/home/piet/.openclaw/scripts/apply-embedded-lane-grace-patch.py`: OK
- `/home/piet/.openclaw/scripts/openclaw-discord-session-stability-guard.py`: OK
- `/home/piet/.openclaw/scripts/openclaw-discord-fallback-chain-watch.py`: OK
- `/home/piet/.openclaw/scripts/atlas-discord-fallback-chain-watch.py`: OK
- `/home/piet/.openclaw/scripts/atlas-discord-stability-guard.py`: OK

Logs:
- Gateway journal since `2026-05-04 12:09:24 CEST`: no hits for timeout, fallback, 408, client-closed, minimax provider-not-found, runtime, OOM, or event-loop degradation patterns.
- `atlas-discord-fallback-chain-watch.log`: no current hits at or after `2026-05-04T10:09:24Z`; historical FailoverError sample at `2026-05-04T09:40:23Z`.
- `openclaw-discord-fallback-chain-watch.log`: no hits.
- `session-rotation-watchdog.log`: present, no tail content in checked output.
- Last 90 minutes include pre-restart Atlas timeout/fallback at `2026-05-04 11:40:23 CEST` and pre-restart Minimax provider failure at `2026-05-04 12:00:01 CEST`.

## Root Cause Status

- H1 Heartbeat/Discord race: mitigated/observing. No current post-restart timeout/fallback signals.
- H2 stale modelOverride/session pin: mitigated. Guard dry-run has no findings; Forge stale Discord key remains removed; Atlas has no overrides.
- H3 timeout budget/lane cap: improved/observing. Default timeout is `600s`; no current CommandLaneTaskTimeout or 408 after restart.
- H4 minimax cron noise: unresolved risk. Current post-restart logs are clean, but enabled Minimax cronjobs remain and the 90-minute window contains a pre-restart provider-not-found failure.
- H5 Mission Control worker lifecycle: healthy. Board health and consistency are OK; no open tasks, no open worker-runs, no duplicate open worker sessions.

## Primary Next Action

`fix cron/minimax`

## Write Plan, Not Executed

Goal: remove Minimax cron noise without touching Gateway/session state.

1. Backup:
   - `cp -a /home/piet/.openclaw/cron/jobs.json /home/piet/.openclaw/cron/jobs.json.bak-$(date -u +%Y%m%dT%H%M%SZ)-minimax-cron-fix`

2. Edit:
   - File: `/home/piet/.openclaw/cron/jobs.json`
   - Target enabled jobs:
     - `5b6e3416-3164-4625-b04a-d806be4baeff` (`efficiency-auditor-heartbeat`)
     - `0f9d0f2e-9839-4a14-ad18-cb75ff7f49c7` (`mc-pending-pickup-smoke-hourly`)
   - Either change `payload.model` to a known working OpenAI/Codex model or repair the Minimax provider mapping after a config validation pass.

3. Validate:
   - `python3 -m json.tool /home/piet/.openclaw/cron/jobs.json >/dev/null`
   - Parse `data["jobs"]` and confirm enabled job count and payload models.
   - Run a read-only Gateway journal check after the next scheduled cron window.

4. Rollback:
   - Restore the backup to `/home/piet/.openclaw/cron/jobs.json`.

## Minimax Cron Fix Executed

Executed at: `2026-05-04T10:49:37Z`

Scope:
- Mutated only `/home/piet/.openclaw/cron/jobs.json`.
- No Gateway restart.
- No session cleanup.
- No agent model changes.
- No `openclaw.json` mutation.

Backup:
- `/home/piet/.openclaw/cron/jobs.json.bak-20260504T104937Z-minimax-cron-fix`

Changes:
- `efficiency-auditor-heartbeat`
  - id: `5b6e3416-3164-4625-b04a-d806be4baeff`
  - payload.model: `minimax/MiniMax-M2.7-highspeed` -> `openai-codex/gpt-5.4-mini`
- `mc-pending-pickup-smoke-hourly`
  - id: `0f9d0f2e-9839-4a14-ad18-cb75ff7f49c7`
  - payload.model: `minimax/MiniMax-M2.7` -> `openai-codex/gpt-5.4-mini`

Validation:
- `python3 -m json.tool /home/piet/.openclaw/cron/jobs.json >/dev/null`: OK
- Target jobs found via `data["jobs"]`: 2
- Target jobs remain enabled: yes
- Enabled `minimax/*` payload models remaining: 0
- Gateway unchanged: `ActiveEnterTimestamp=Mon 2026-05-04 12:09:24 CEST`, `NRestarts=0`, `SubState=running`

Rollback:
- `cp -a /home/piet/.openclaw/cron/jobs.json.bak-20260504T104937Z-minimax-cron-fix /home/piet/.openclaw/cron/jobs.json`

## Canonical Final Report

- [[../../../03-Projects/plans/2026-05-04_openclaw-mission-control-stabilization-final-report|OpenClaw/Mission-Control Stabilization Final Report]]
- This receipt remains the detailed post-gate evidence source; the linked project report is the cross-agent/operator SSOT.
