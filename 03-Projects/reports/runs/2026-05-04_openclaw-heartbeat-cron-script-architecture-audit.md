# OpenClaw Heartbeat/Cron/Script Architecture Audit

Timestamp: 2026-05-04T22:00:57+02:00  
Scope: OpenClaw Gateway, agent heartbeats, systemd timers, OpenClaw cron jobs, stability scripts, Mission Control health gates  
Mode: controlled live audit with small stabilizing changes

## Verdict

Overall: YELLOW -> GREEN for the implemented stabilization slice.

The core system is healthy after the changes:

- OpenClaw Gateway: GREEN, `/health` live.
- Mission Control: GREEN at final check, `/api/health` ok and board consistency ok.
- Atlas/main heartbeat configuration: GREEN and explicitly prioritized.
- Productive agent heartbeat coverage: GREEN in config for Atlas, Forge, Pixel, Lens, James, System Bot, Spark.
- Runtime heartbeat proof after cleanup: YELLOW pending the next scheduled 30m heartbeat cycle. Old heartbeat sessions were cleared so the next run starts from the new minimal prompt.
- Scripts/cron/systemd hygiene: YELLOW; several legacy/monitoring surfaces remain but the immediate unsafe auto-repair path was removed.

## What Changed

### 1. All productive agents now have explicit safe heartbeat config

Affected agents:

- `main` / Atlas
- `sre-expert` / Forge
- `frontend-guru` / Pixel
- `efficiency-auditor` / Lens
- `james` / James
- `system-bot` / System Bot
- `spark` / Spark

Heartbeat block now used by all:

```json
{
  "every": "30m",
  "isolatedSession": true,
  "skipWhenBusy": true,
  "lightContext": true,
  "target": "none",
  "model": "openai-codex/gpt-5.4-mini",
  "timeoutSeconds": 120,
  "ackMaxChars": 80,
  "suppressToolErrorWarnings": true,
  "prompt": "Liveness check only. Do not read files, do not use tools, do not call APIs, do not inspect tasks, and do not continue previous work. Reply exactly HEARTBEAT_OK."
}
```

Rationale:

- `isolatedSession`: prevents heartbeat context/model bleed into productive Discord sessions.
- `skipWhenBusy`: avoids competing with active Atlas/Forge/etc. work.
- `lightContext`: avoids pulling the large working context into a liveness check.
- `target: none`: no user-visible heartbeat noise.
- Minimal prompt: prevents the earlier Lens behavior where a heartbeat attempted operational checks while Mission Control was offline.

### 2. Old heartbeat session keys were surgically removed

Removed only `:heartbeat` keys from `sessions.json`; no `.jsonl` history was deleted.

Removed session keys:

- `agent:efficiency-auditor:main:heartbeat` (old running Lens heartbeat)
- `agent:frontend-guru:main:heartbeat`
- `agent:main:main:heartbeat`
- `agent:system-bot:main:heartbeat`

Purpose: clear the old broad-prompt heartbeat state and let the new minimal prompt start cleanly on the next scheduled heartbeat cycle.

### 3. Forge heartbeat script changed to alert-only

File:

- `/home/piet/.openclaw/scripts/forge-heartbeat.sh`

Changed behavior:

- Before: after three gateway health failures it ran `openclaw doctor --fix` and sent a direct Discord API message.
- Now: it logs `ALERT_ONLY` and uses the central `alert-dispatcher.sh`; no automatic repair and no direct Discord token/API path.

Purpose: a health heartbeat must not mutate OpenClaw configuration automatically during transient gateway issues.

### 4. Stale failed `m7-mc-watchdog.service` was reset

Action:

- `systemctl --user reset-failed m7-mc-watchdog.service`

Result:

- Service is now inactive/dead and disabled, not failed.
- No service was started.

Purpose: remove stale failed-unit noise without changing Mission Control behavior.

### 5. Mission Control build side-effect was reverted

During investigation a temporary `mission-control.service.d/build-ready-check.conf` was created before the user clarified another Codex app owns the Pipeline UI build. That file was removed again and not kept as part of this audit.

No Mission Control build/restart ownership remains in this heartbeat audit.

## Evidence

Backups:

- `/home/piet/backups/2026-05-04-heartbeat-architecture-20260504T194227Z`
- `/home/piet/backups/2026-05-04-heartbeat-architecture-final-20260504T195634Z`

Validation:

- `openclaw config validate` -> valid.
- OpenClaw Gateway active since `Mon 2026-05-04 21:57:05 CEST`.
- Gateway `/health` -> `{"ok":true,"status":"live"}`.
- Mission Control `/api/health` -> `status=ok`, `openTasks=0`, `pendingPickup=0`, `staleOpenTasks=0`, `orphanedDispatches=0`.
- Mission Control `/api/board-consistency` -> `status=ok`, raw and normalized issue count `0`.
- `m7-mc-watchdog.service` -> inactive/dead, disabled, `Result=success`.
- `forge-heartbeat.sh` syntax OK and no remaining `doctor --fix`, direct Discord API, or `Authorization: Bot` path.

Current heartbeat session state after cleanup:

- No stale `:heartbeat` session keys remain in the seven productive agent stores.
- Next proof point is the next scheduled 30m heartbeat cycle.

## Root Cause Notes

### H1: Heartbeat prompt was too broad

Confirmed. The old default heartbeat prompt told agents to read `HEARTBEAT.md` and follow context. Lens used that freedom to inspect Mission Control while it was unavailable. A liveness heartbeat should not do operational checks.

Fix: minimal prompt and `target:none`.

### H2: Explicit heartbeat agents changed scheduling semantics

Confirmed. OpenClaw uses `hasExplicitHeartbeatAgents(cfg)`: once any agent has an explicit heartbeat, only agents with explicit heartbeat blocks are scheduled. That is why the productive agents now all have explicit blocks.

### H3: Heartbeat sessions can block later agents

Likely. The first all-agent rollout showed Lens stuck in `running` and later agents had not yet received heartbeat sessions. Clearing old heartbeat keys plus minimal prompts should reduce this risk. The next scheduled cycle must be observed.

### H4: Legacy watchdogs can cause hidden mutations

Confirmed for Forge heartbeat. Automatic `doctor --fix` from a health heartbeat was too aggressive and is now removed.

### H5: Cron/systemJob source-of-truth is mixed

Still open. Some OpenClaw cron jobs are disabled but their migrated `systemJob` timers are active. This can be valid, but it must be documented as "systemd is canonical" for those jobs.

## Open Follow-Ups

1. Observe the next 30m heartbeat cycle and verify that all seven productive agents complete `HEARTBEAT_OK`.
2. Decide canonical ownership for migrated systemJobs:
   - `openclaw-systemjob-m7-atlas-master-heartbeat.timer`
   - `openclaw-systemjob-atlas-receipt-stream-subscribe.timer`
   - `openclaw-systemjob-mc-task-parity-check.timer`
   - `openclaw-systemjob-mcp-zombie-killer-10min.timer`
3. Review enabled OpenClaw cron jobs with `lightContext: null`; some daily reports may be fine, but smoke/heartbeat-like jobs should generally use lightweight context.
4. Treat Mission Control build/start behavior as separate Pipeline UI ownership; do not mix it into heartbeat changes.

## Recommended Next Gate

At the next heartbeat cycle:

```bash
python3 - <<'PY'
import json,pathlib,time
now=int(time.time()*1000)
for agent in ['main','sre-expert','frontend-guru','efficiency-auditor','james','system-bot','spark']:
    p=pathlib.Path('/home/piet/.openclaw/agents')/agent/'sessions/sessions.json'
    data=json.loads(p.read_text()) if p.exists() else {}
    keys=[(k,v) for k,v in data.items() if ':heartbeat' in k]
    print(agent, len(keys))
    for k,v in keys:
        print(' ', k, v.get('status'), v.get('model'), v.get('abortedLastRun'), v.get('updatedAt'))
PY
```

Pass criteria:

- Each productive agent has a `:heartbeat` key.
- Each heartbeat is `done`.
- Model is `gpt-5.4-mini`.
- No `abortedLastRun`.
- Gateway logs show no heartbeat timeout, tool/curl/read drift, or fallback chain.
