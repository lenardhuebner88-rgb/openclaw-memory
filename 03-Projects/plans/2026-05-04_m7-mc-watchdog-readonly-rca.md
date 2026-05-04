# m7-mc-watchdog Read-only RCA — 2026-05-04

Status: read-only RCA complete  
Mutation: none  
Restart: none  
Related runbook: `openclaw-mission-control-stability-runbook.md`

## Verdict

YELLOW legacy noise, not a current Mission Control outage.

`m7-mc-watchdog.service` is failed from 2026-04-30, but:

- `m7-mc-watchdog.timer` is disabled/inactive.
- Mission Control is currently active and healthy.
- Current Mission Control build artifacts exist.
- The failure came from an old Mission Control build-artifact/startup failure window, not from the current beta.4 OpenClaw stabilization work.

## Current State

Unit:

- service: `m7-mc-watchdog.service`
- service state: `failed`
- unit file: `/home/piet/.config/systemd/user/m7-mc-watchdog.service`
- timer: `/home/piet/.config/systemd/user/m7-mc-watchdog.timer`
- timer state: disabled/inactive
- last failed: `Thu 2026-04-30 07:14:37 CEST`
- final status: `status=1/FAILURE`
- systemd failed units: exactly this unit

Current Mission Control:

- `mission-control.service`: active
- ActiveEnterTimestamp: `Mon 2026-05-04 11:09:43 CEST`
- NRestarts: `0`
- `/api/health`: `ok`
- `.next/BUILD_ID`: present
- `.next/prerender-manifest.json`: present

## Purpose of the Watchdog

Script:

```text
/home/piet/.openclaw/scripts/mc-watchdog.sh
```

Documented intent:

- Detect Mission Control "stop without start" incidents.
- If `/api/health` is OK: exit 0.
- If MC is inactive and `.next/BUILD_ID` exists: start Mission Control.
- If MC is failed: `reset-failed` and start Mission Control.
- If MC is activating/reloading/deactivating: skip.

It wraps itself through:

```text
/home/piet/.openclaw/scripts/otel-cron-wrap.sh
```

and sends alerts through:

```text
/home/piet/.openclaw/scripts/alert-dispatcher.sh
```

## Failure Evidence

Systemd service log around final failure:

- repeated starts on 2026-04-30
- repeated `status=3/NOTIMPLEMENTED` earlier in the night
- final repeated `status=1/FAILURE`
- StartLimit hit at `2026-04-30 07:14:37 CEST`

Watchdog log:

```text
/home/piet/.openclaw/workspace/logs/mc-watchdog.log.1
```

Key lines:

- many `CHECK health_failed state=failed`
- many `HEAL reset_failed_and_start`
- many `ALERT MC reset-failed + start did not recover service`
- final phase:
  - `CHECK health_failed state=inactive`
  - `ALERT MC inactive AND no BUILD_ID — build missing, manual intervention needed`

Mission Control logs for the same window showed the root service failure:

```text
ENOENT: no such file or directory, open '/home/piet/.openclaw/workspace/mission-control/.next/prerender-manifest.json'
Could not find a production build in the '.next' directory.
```

So the watchdog was not the primary failure; it was repeatedly trying to recover a Mission Control service that could not start because the production build artifacts were missing/incomplete.

## Root Cause

Root cause of the failed watchdog unit:

Mission Control had missing/incomplete `.next` production build artifacts on 2026-04-30. `mc-watchdog.sh` correctly detected unhealthy/failed Mission Control and attempted recovery, but repeated recovery attempts could not succeed until the build artifacts were rebuilt. Systemd then hit the service start-limit and left `m7-mc-watchdog.service` failed.

Current state is different:

- Mission Control is healthy.
- `.next/BUILD_ID` and `.next/prerender-manifest.json` exist.
- The m7 watchdog timer is disabled, so the failed service is stale systemd state/noise, not an active failing loop.

## Collision Check

No direct conflict found with current OpenClaw Discord/session guards:

- `canary-openclaw-discord-session-stability-guard.timer`
- `canary-openclaw-discord-fallback-chain-watch.timer`
- `canary-atlas-discord-fallback-chain-watch.timer`

Different scope:

- m7-mc-watchdog: Mission Control process liveness/heal
- current guards: OpenClaw Discord session/fallback health

## Recommendation

Do not repair during the current OpenClaw/Atlas stability observation unless the operator wants to clean legacy failed-unit noise.

Recommended action after observation remains GREEN:

1. Keep it as separate small task.
2. Reset failed state and run one controlled service start only after confirming MC health/build artifacts.
3. Enable timer only if the liveness-heal behavior is still desired.

## Proposed Write Plan — Not Executed

Pre-check:

```bash
curl -fsS http://127.0.0.1:3000/api/health
test -f /home/piet/.openclaw/workspace/mission-control/.next/BUILD_ID
test -f /home/piet/.openclaw/workspace/mission-control/.next/prerender-manifest.json
bash -n /home/piet/.openclaw/scripts/mc-watchdog.sh
```

One-shot validation:

```bash
systemctl --user reset-failed m7-mc-watchdog.service
systemctl --user start m7-mc-watchdog.service
systemctl --user status m7-mc-watchdog.service --no-pager -n 40
tail -40 /home/piet/.openclaw/workspace/logs/mc-watchdog.log
```

If service exits success and the operator wants this monitor active:

```bash
systemctl --user enable --now m7-mc-watchdog.timer
systemctl --user list-timers 'm7-mc-watchdog.timer' --no-pager
```

Rollback if noisy:

```bash
systemctl --user disable --now m7-mc-watchdog.timer
systemctl --user reset-failed m7-mc-watchdog.service
```

## Current Operating Decision

Leave as YELLOW legacy backlog while the current OpenClaw/Atlas 24h observation runs. It is not a current blocker because Mission Control health and board consistency are GREEN.
