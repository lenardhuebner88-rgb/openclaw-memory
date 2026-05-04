# OpenClaw / Mission Control 24h Stability Observation

Started: 2026-05-04T12:17:33Z / 2026-05-04 14:17:33 CEST  
Baseline: post Forge scoped cleanup, no new failures since 2026-05-04 14:04:37 CEST  
Runbook: `openclaw-mission-control-stability-runbook.md`

## Start Verdict

Overall: GREEN for current post-cleanup window.

- Gateway: GREEN
- Atlas/main: GREEN with active run
- Forge/sre-expert: GREEN
- Session Store: GREEN
- Timers/Guards: GREEN
- Cron/Minimax: GREEN
- Mission Control: GREEN
- Logs since current observation baseline: GREEN

Note: the full post-Gateway-restart window contains the known Forge timeout/fallback chain at 2026-05-04 13:28 CEST. That incident was already remediated by scoped Forge session rotation at 2026-05-04T12:04:37Z and is treated as historical for this observation.

## Gateway

- OpenClaw: `2026.5.3-beta.4 (c6c64e2)`
- Service: `openclaw-gateway.service`
- Active: `active`
- ActiveEnterTimestamp: `Mon 2026-05-04 12:09:24 CEST`
- NRestarts: `0`
- PID: `882905`
- MemoryCurrent: `2413760512` bytes
- Health: `{"ok":true,"status":"live"}`

## Mission Control

- `/api/health`: `status=ok`
- `/api/board-consistency`: `status=ok`
- Health metrics:
  - `openTasks=0`
  - `inProgress=0`
  - `pendingPickup=0`
  - `staleOpenTasks=0`
  - `orphanedDispatches=0`
  - `attentionCount=0`
- Raw `tasks.json` still contains 2 historical draft/queued items, but Mission Control health and board consistency report no stale/open board problem.
- `worker-runs.json`: open runs `0`

## Session Guard Start State

Command:

```bash
python3 /home/piet/.openclaw/scripts/openclaw-discord-session-stability-guard.py
```

Summary:

- scannedSessionStores: `10`
- discordSessions: `1`
- activeRuns: `1`
- rotationNeeded: `0`
- staleRunning: `0`
- loadErrors: `0`
- wouldRotateSessionKeys: `[]`
- mutation: `none`
- gatewayRestart: `not-attempted`

Current Atlas/main Discord session:

- sessionKey: `agent:main:discord:channel:1486480128576983070`
- sessionId: `29e5f70f-809f-442d-8f9c-0517500352f9`
- status: `running`
- updatedAt: `2026-05-04T12:16:22Z`
- model: `gpt-5.5`
- modelOverride: none
- providerOverride: none
- cacheRead: `86912`
- totalTokens: `89370`
- below rotation thresholds: yes

Forge/sre-expert:

- No current Discord session key found by the guard.
- No model/provider override finding.
- No stale running finding.

## Timers / Guards

Active relevant timers:

- `canary-atlas-discord-fallback-chain-watch.timer`
- `canary-atlas-discord-stability-guard.timer`
- `canary-openclaw-discord-fallback-chain-watch.timer`
- `canary-openclaw-discord-session-stability-guard.timer`

Last checked service statuses:

- `canary-atlas-discord-fallback-chain-watch.service`: `success|0|inactive`
- `canary-openclaw-discord-fallback-chain-watch.service`: `success|0|inactive`
- `canary-openclaw-discord-session-stability-guard.service`: `success|0|inactive`

Session store hash diff before/after first read-only timer run was empty. This confirms the timer wrote logs only and did not mutate `sessions.json`.

## Cron / Minimax

- Enabled cron jobs: `14`
- Enabled `minimax/*` payload model refs: `0`
- Fixed target jobs remain enabled:
  - `efficiency-auditor-heartbeat`: `openai-codex/gpt-5.4-mini`
  - `mc-pending-pickup-smoke-hourly`: `openai-codex/gpt-5.4-mini`

## Log Checks

Full gateway-restart window since `2026-05-04 12:09:24 CEST`:

- Historical Forge/sre-expert timeout/fallback chain:
  - 2026-05-04 13:28:22 CEST: `codex app-server attempt timed out`, `FailoverError`, `candidate_failed`
  - 2026-05-04 13:30:25 CEST: `candidate_succeeded`
  - Already remediated by scoped Forge session rotation.

Current observation window since `2026-05-04 14:04:37 CEST`:

- `FailoverError`: 0
- `codex app-server attempt timed out`: 0
- `candidate_failed`: 0
- `candidate_succeeded`: 0
- `CommandLaneTaskTimeout`: 0
- `status 408`: 0
- `client is closed`: 0
- `Model provider minimax not found`: 0
- `ExecStartPre failure`: 0
- `RuntimeError`: 0
- `OOM/out of memory`: 0
- `event loop degraded`: 0

## Observation Gates

### GREEN if all remain true

- Gateway health live and `NRestarts=0`.
- No new timeout/fallback event after 2026-05-04 14:04:37 CEST.
- Session guard `rotationNeeded=0`.
- Atlas has no model/provider overrides.
- Forge has no new auto-pin or stale running session.
- Enabled minimax cron payload refs stay `0`.
- Mission Control health and board consistency stay OK.

### YELLOW if

- Atlas cache exceeds `cacheRead > 120000` or `totalTokens > 140000` without errors.
- Atlas is active/running and not idle enough for scoped rotation.
- A non-core legacy timer remains failed while Gateway/MC are healthy.

### RED if

- Any new post-baseline `FailoverError`, app-server timeout, 408, or candidate failure appears.
- Any Discord session gets `modelOverrideSource=auto` or `providerOverride`.
- Gateway restarts unexpectedly or health is not live.
- Mission Control health/board consistency fails.

## Next Check

Recommended next read-only check: within 2-3 hours, or immediately after any slow/failed Atlas or Forge response.

Command set:

```bash
SINCE='2026-05-04 14:04:37'
curl -fsS http://127.0.0.1:18789/health
python3 /home/piet/.openclaw/scripts/openclaw-discord-session-stability-guard.py
journalctl --user -u openclaw-gateway.service --since "$SINCE" --no-pager | rg 'FailoverError|codex app-server attempt timed out|candidate_failed|CommandLaneTaskTimeout|status[:=]408|Model provider `minimax` not found' || true
curl -fsS http://127.0.0.1:3000/api/health
curl -fsS http://127.0.0.1:3000/api/board-consistency
```

## Snapshot 1 — 2026-05-04T12:19:20Z / 14:19:20 CEST

Verdict: GREEN.

- Gateway:
  - active: yes
  - ActiveEnterTimestamp: `Mon 2026-05-04 12:09:24 CEST`
  - NRestarts: `0`
  - PID: `882905`
  - MemoryCurrent: `1825320960` bytes
  - Health: `{"ok":true,"status":"live"}`
- Mission Control:
  - `/api/health`: `ok`
  - `/api/board-consistency`: `ok`
  - `openTasks=0`, `inProgress=0`, `pendingPickup=0`, `staleOpenTasks=0`, `orphanedDispatches=0`
- Session guard:
  - `rotationNeeded=0`
  - `staleRunning=0`
  - `loadErrors=0`
  - `wouldRotateSessionKeys=[]`
  - `scannedSessionStores=10`
- Atlas/main:
  - sessionKey: `agent:main:discord:channel:1486480128576983070`
  - sessionId: `29e5f70f-809f-442d-8f9c-0517500352f9`
  - status: `running`
  - updatedAt: `2026-05-04T12:16:22Z`
  - model: `gpt-5.5`
  - model/provider overrides: none
  - cacheRead/totalTokens: `86912 / 89370`
  - below rotation thresholds: yes
- Forge/sre-expert:
  - no current Discord session finding
  - no override/stale-running finding
- Logs since current baseline `2026-05-04 14:04:37 CEST`:
  - `FailoverError`: 0
  - `codex app-server attempt timed out`: 0
  - `candidate_failed`: 0
  - `candidate_succeeded`: 0
  - `CommandLaneTaskTimeout`: 0
  - `status 408`: 0
  - `Model provider minimax not found`: 0

Action: continue observation. No fixes, restarts, cleanups, or config changes.
