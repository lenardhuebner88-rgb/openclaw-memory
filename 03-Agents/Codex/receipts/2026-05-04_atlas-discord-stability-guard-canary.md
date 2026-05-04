# Atlas Discord Stability Guard Canary

Timestamp: 2026-05-04 11:29 CEST
Owner: Codex

## Scope

User requested:

- Recover Atlas after it stopped responding.
- Check whether an existing session guard already covered the timeout/fallback issue.
- Integrate the new Atlas Discord stability guard cleanly into the existing system architecture.

## Incident Summary

Atlas stopped responding because the productive Discord session entered a long fallback/timeout chain.

Observed failing session:

- Session key: `agent:main:discord:channel:1486480128576983070`
- Old session id: `8669821b-48d0-4fa1-9193-cb4ffd9c0b9d`
- Failure pattern:
  - `openai/gpt-5.5` timed out after app-server attempt timeout.
  - `openai/gpt-5.3-codex` timed out.
  - `openai/gpt-5.4` timed out / lane timeout.
  - `openai/gpt-5.4-mini` eventually completed.
- Session store then persisted:
  - `modelOverride=gpt-5.4-mini`
  - `modelOverrideSource=auto`
  - `providerOverride=openai`
- Token state before manual intervention:
  - `cacheRead=191360`
  - `totalTokens=192520`

Conclusion: Atlas was operationally stuck in a large Discord session and then masked by a persistent auto fallback model override.

## Immediate Recovery

Manual recovery performed:

- Backed up session store:
  - `/home/piet/.openclaw/agents/main/sessions/sessions.json.bak-20260504T091336Z-rotate-atlas-discord-session`
- Removed only the affected Discord session-store key:
  - `agent:main:discord:channel:1486480128576983070`
- Did not delete `.jsonl` history.
- Restarted `openclaw-gateway.service`.

Post-recovery validation:

- Gateway active since `2026-05-04 11:13:37 CEST`.
- `/health`: `{"ok":true,"status":"live"}`
- New Atlas Discord session:
  - Session id: `e89a1fe3-825a-48ab-9572-7c663b31f177`
  - `model=gpt-5.5`
  - `modelOverride=null`
  - `modelOverrideSource=null`
  - `providerOverride=null`
  - `cacheRead=26496`
  - `totalTokens=27156`
- User smoke in Discord:
  - Prompt: `Status bitte kurz bestätigen`
  - Atlas replied online, model `gpt-5.5`.

## Existing Guard Architecture Check

Existing guards found:

- `/home/piet/.openclaw/scripts/session-rotation-watchdog.py`
  - Reads `/home/piet/.openclaw/workspace/memory/memory-budget.log`.
  - Emits `/tmp/atlas-rotation-signal.json`.
  - Runs via `canary-session-rotation-watchdog.timer`.
- `/home/piet/.openclaw/scripts/auto-pickup.py`
  - Consumes `/tmp/atlas-rotation-signal.json`.
  - Rotation consumer live mode is enabled through:
    - `/home/piet/.config/systemd/user/m7-auto-pickup.service.d/rotation-live.conf`
- `/home/piet/.openclaw/scripts/session-size-guard.py`
  - Scans session JSONL file size and message count.
  - Runs via `canary-session-size-guard.timer`.

Gap found:

- Existing architecture did not directly inspect `sessions.json` for:
  - `modelOverrideSource=auto`
  - `modelOverride`
  - `providerOverride`
  - `cacheRead`
  - `totalTokens`
  - `status=timeout`
- During the incident, `memory-budget.log` only estimated the old session around `tokens_est=60598`, `pct=40%`.
- The JSONL file size stayed below the session-size-guard rotation threshold.

Conclusion: existing guards were active but blind to the exact fallback-pin/session-store drift that caused this incident.

## New Guard

Atlas implemented:

- `/home/piet/.openclaw/scripts/atlas-discord-stability-guard.py`

Verified behavior:

- Default mode is dry-run.
- Checks only keys matching:
  - `agent:main:discord:*`
- Flags rotation when:
  - `modelOverrideSource == "auto"`
  - `modelOverride` is set
  - `providerOverride` is set
  - `cacheRead > 120000`
  - `totalTokens > 140000`
  - `status == "timeout"`
- Live mode aborts if an active run is detected.
- Live mode removes only the affected `agent:main:discord:*` session-store key.
- Does not delete `.jsonl` history.
- Creates backup before mutation.
- Validates JSON.
- Checks gateway health.

Dry-run verification on current live session:

- `wouldRotateSessionKeys=[]`
- `rotationNeeded=false`
- `modelOverrideSourceAuto=false`
- `modelOverrideSet=false`
- `providerOverrideSet=false`

## Systemd Integration

Integrated as canary dry-run, following the existing `canary-session-*` pattern.

Created:

- `/home/piet/.config/systemd/user/canary-atlas-discord-stability-guard.service`
- `/home/piet/.config/systemd/user/canary-atlas-discord-stability-guard.timer`

Service:

- Type: `oneshot`
- Uses `flock`:
  - `/tmp/canary-atlas-discord-stability-guard.lock`
- Command:
  - `/home/piet/.openclaw/scripts/atlas-discord-stability-guard.py`
- Log:
  - `/home/piet/.openclaw/workspace/logs/canary-atlas-discord-stability-guard.log`

Timer:

- `OnBootSec=2min`
- `OnUnitActiveSec=2min`
- `Persistent=true`

Validation:

- `systemctl --user daemon-reload`: completed.
- `systemctl --user enable --now canary-atlas-discord-stability-guard.timer`: completed.
- Manual service run: `status=0/SUCCESS`.
- First automatic timer run: `status=0/SUCCESS`.
- Timer active/waiting.
- Next trigger observed in `systemctl --user list-timers`.

## Current State

At completion:

- OpenClaw Gateway:
  - `/health`: `{"ok":true,"status":"live"}`
- Mission Control:
  - `/api/health`: `status=ok`
  - `pendingPickup=0`
  - `attentionCount=0`
  - `recoveryLoad=0`
- Atlas Discord session:
  - Session id: `e89a1fe3-825a-48ab-9572-7c663b31f177`
  - `status=done`
  - `model=gpt-5.5`
  - `modelOverride=null`
  - `modelOverrideSource=null`
  - `providerOverride=null`
  - `cacheRead=26496`
  - `totalTokens=27156`

## Next Gate

Observe for 30-60 minutes.

Pass criteria:

- `canary-atlas-discord-stability-guard.service` keeps exiting `0/SUCCESS`.
- Log continues to show:
  - `wouldRotateSessionKeys=[]`
  - `staleOverrideOrRotationSignalsPresent=false`
- Atlas Discord remains on `gpt-5.5`.
- No fresh persistent `modelOverrideSource=auto`.
- No fresh `codex app-server attempt timed out` chain on Atlas Discord lane.

Recommended commands:

```bash
systemctl --user status canary-atlas-discord-stability-guard.timer --no-pager
systemctl --user status canary-atlas-discord-stability-guard.service --no-pager -n 30
tail -120 /home/piet/.openclaw/workspace/logs/canary-atlas-discord-stability-guard.log
python3 - <<'PY'
import json
p='/home/piet/.openclaw/agents/main/sessions/sessions.json'
with open(p) as f: data=json.load(f)
for k,v in sorted(data.items()):
    if k.startswith('agent:main:discord:'):
        print(k, {x:v.get(x) for x in ['sessionId','status','model','modelOverride','modelOverrideSource','providerOverride','cacheRead','totalTokens','abortedLastRun']})
PY
journalctl --user -u openclaw-gateway.service --since '2026-05-04 11:13:37 CEST' --no-pager | rg 'codex app-server attempt timed out|FailoverError|model fallback decision|CommandLaneTaskTimeout'
```

## Rollback

Disable the canary only:

```bash
systemctl --user disable --now canary-atlas-discord-stability-guard.timer
rm -f /home/piet/.config/systemd/user/canary-atlas-discord-stability-guard.service
rm -f /home/piet/.config/systemd/user/canary-atlas-discord-stability-guard.timer
systemctl --user daemon-reload
```

No OpenClaw config rollback is needed because the canary integration did not change `openclaw.json`.
