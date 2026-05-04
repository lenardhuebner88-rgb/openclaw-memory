# OpenClaw / Mission Control Stability Runbook

Status: active operating runbook  
Created: 2026-05-04  
Primary report: `2026-05-04_openclaw-mission-control-stabilization-final-report.md`

## Purpose

Keep OpenClaw agents and Mission Control stable after the 2026-05-04 beta.4 stabilization work. Prefer observation and scoped cleanup over broad restarts or global session cleanup.

## Current Stabilization Baseline

- OpenClaw Gateway restarted successfully at `2026-05-04 12:09:24 CEST`.
- `agents.defaults.timeoutSeconds` is `600`.
- Embedded lane grace is patched to `10min`.
- Atlas/main runs on `openai/gpt-5.5` with fallbacks.
- Atlas heartbeat is isolated on `agent:main:main:heartbeat`.
- Forge stale/auto-pinned Discord sessions were scoped-rotated.
- Minimax cron provider noise was removed from enabled cron payloads.
- Mission Control live E2E canary passed:
  - `draft -> assigned -> pending-pickup -> in-progress/accepted -> done/result`

## Verdict Rules

### GREEN

- Gateway health is live.
- `NRestarts=0` since the last known green gate.
- No post-baseline timeout/fallback events:
  - `FailoverError`
  - `codex app-server attempt timed out`
  - `candidate_failed`
  - `CommandLaneTaskTimeout`
  - `status 408`
- Session guard reports `rotationNeeded=0`.
- Atlas and Forge have no `modelOverride`, `modelOverrideSource=auto`, or `providerOverride`.
- Mission Control `/api/health` and `/api/board-consistency` are OK.

### YELLOW

- Atlas is `running` and not idle yet.
- Atlas `cacheRead > 120000` or `totalTokens > 140000`, with no timeout/fallback errors.
- Watcher logs include only historical events before the current baseline window.
- A non-core legacy timer/service is failed, while Gateway/MC are healthy.

### RED

- Any new post-baseline `FailoverError`, app-server timeout, 408, or candidate failure on a Discord agent lane.
- Any `modelOverrideSource=auto` or provider override appears on a Discord session.
- Gateway health is not live or Gateway restarts unexpectedly.
- Mission Control health/board consistency fails.
- Open worker-runs or stale/orphaned dispatches appear after a worker lifecycle gate.

## Standard Read-Only Check

Use a concrete time window. For the 2026-05-04 stabilization baseline:

```bash
SINCE='2026-05-04 12:09:24'
systemctl --user is-active openclaw-gateway.service
systemctl --user show openclaw-gateway.service -p ExecMainPID -p NRestarts -p ActiveEnterTimestamp --value
curl -fsS http://127.0.0.1:18789/health
python3 /home/piet/.openclaw/scripts/openclaw-discord-session-stability-guard.py
journalctl --user -u openclaw-gateway.service --since "$SINCE" --no-pager | rg 'FailoverError|codex app-server attempt timed out|candidate_failed|CommandLaneTaskTimeout|status[:=]408|client is closed|Model provider `minimax` not found' || true
```

Mission Control:

```bash
curl -fsS http://127.0.0.1:3000/api/health
curl -fsS http://127.0.0.1:3000/api/board-consistency
```

Cron minimax check:

```bash
python3 - <<'PY'
import json
from pathlib import Path
data=json.loads(Path('/home/piet/.openclaw/cron/jobs.json').read_text())
jobs=data.get('jobs', [])
print([j.get('name') or j.get('id') for j in jobs if j.get('enabled') and str((j.get('payload') or {}).get('model','')).startswith('minimax/')])
PY
```

## Safe Commands

Read-only:

```bash
python3 /home/piet/.openclaw/scripts/openclaw-discord-session-stability-guard.py
python3 /home/piet/.openclaw/scripts/openclaw-discord-session-stability-guard.py --only-session-key agent:sre-expert:discord:channel:1486480146524410028
systemctl --user list-timers 'canary-*' --no-pager
journalctl --user -u openclaw-gateway.service --since '1 hour ago' --no-pager
```

Mutation requires a backup, a scoped key, and an explicit reason:

```bash
python3 /home/piet/.openclaw/scripts/openclaw-discord-session-stability-guard.py \
  --only-session-key <agent:agentId:discord:...> \
  --live
```

Never run broad cleanup when Atlas or Forge has a current active/recent session finding.

## Atlas High-Cache Rotation Gate

Do not rotate while Atlas is active.

Rotate only if all are true:

- Session key: `agent:main:discord:channel:1486480128576983070`
- status is not `running`, `in-progress`, `queued`, or `pending`
- `updatedAt` is older than 10 minutes
- `cacheRead > 120000` or `totalTokens > 140000`
- no current timeout/fallback chain is in progress

Action:

```bash
python3 /home/piet/.openclaw/scripts/openclaw-discord-session-stability-guard.py \
  --only-session-key agent:main:discord:channel:1486480128576983070 \
  --live
```

Post-check:

```bash
python3 /home/piet/.openclaw/scripts/openclaw-discord-session-stability-guard.py
curl -fsS http://127.0.0.1:18789/health
```

## Forge / Other Agent Auto-Pin Cleanup Gate

Use scoped cleanup only.

Proceed only if the dry-run for the exact session key reports:

- `modelOverrideSource=auto`, `modelOverride-set`, or `providerOverride-set`; or
- stale running older than the configured threshold; and
- `recentActive=false`.

Example:

```bash
KEY='agent:sre-expert:discord:channel:1486480146524410028'
python3 /home/piet/.openclaw/scripts/openclaw-discord-session-stability-guard.py --only-session-key "$KEY"
python3 /home/piet/.openclaw/scripts/openclaw-discord-session-stability-guard.py --only-session-key "$KEY" --live
```

## Mission Control Canary Gate

Run after Mission Control worker lifecycle changes, board state changes, or OpenClaw/Mission Control upgrades.

Expected state chain:

```text
draft -> assigned -> pending-pickup -> in-progress/accepted -> done/result
```

Required postconditions:

- `/api/health`: OK
- `/api/board-consistency`: OK
- open worker-runs: `0`
- duplicate claim returns `409`
- board events include:
  - `receipt accepted`
  - `receipt result`
  - `task-status-change in-progress -> done`

Use the documented E2E canary receipt as the implementation reference:

```text
/home/piet/vault/03-Agents/Codex/receipts/2026-05-04_mission-control-e2e-draft-to-done-canary.md
```

## Prompt Hygiene

To prevent high cache growth:

- Store long reports in the Vault.
- Send Atlas only a short summary, a path, and a concrete next action.
- Avoid pasting full logs/reports into Discord when a file path is sufficient.
- After long operator/report turns, check cache and rotate only after idle >10min if thresholds are exceeded.

## 24h Observation Standard

Every 2-3 hours or after a suspicious event:

```bash
SINCE='<last GREEN timestamp>'
curl -fsS http://127.0.0.1:18789/health
python3 /home/piet/.openclaw/scripts/openclaw-discord-session-stability-guard.py
journalctl --user -u openclaw-gateway.service --since "$SINCE" --no-pager | rg 'FailoverError|codex app-server attempt timed out|candidate_failed|CommandLaneTaskTimeout|status[:=]408|Model provider `minimax` not found' || true
curl -fsS http://127.0.0.1:3000/api/health
curl -fsS http://127.0.0.1:3000/api/board-consistency
```

Do not count historical watcher entries before the selected baseline window as current RED.

## Known Separate Backlog

Treat these as separate tasks after a stable observation period:

- Legacy `m7-mc-watchdog.service failed`.
- Confirm desired `openai-codex/gpt-5.4-mini` cron route.
- Continue watching OpenClaw beta.4 upstream fixes/issues.

## Key Evidence Links

- Final report: `/home/piet/vault/03-Projects/plans/2026-05-04_openclaw-mission-control-stabilization-final-report.md`
- Global timeout/lane stability: `/home/piet/vault/03-Agents/Codex/receipts/2026-05-04_openclaw-global-timeout-lane-stability.md`
- All-agent session guard: `/home/piet/vault/03-Agents/Codex/receipts/2026-05-04_openclaw-all-agent-session-stability-guard.md`
- Forge scoped rotation: `/home/piet/vault/03-Agents/Codex/receipts/2026-05-04_forge-scoped-timeout-pin-rotation.md`
- Mission Control E2E canary: `/home/piet/vault/03-Agents/Codex/receipts/2026-05-04_mission-control-e2e-draft-to-done-canary.md`
