# Gateway Runtime Signal Watchdog Plan — 2026-05-05

## Scope

Exactly one approved hardening step: extend the existing read-only `gateway-memory-monitor.py` watchdog so it reports recent Gateway runtime instability signals that are currently visible in the journal but not represented in the watchdog output.

## Live evidence

System health is currently green, so this is hardening rather than incident recovery:

- Mission Control `/api/health`: `status=ok`, `staleOpenTasks=0`, `recoveryLoad=0`, `orphanedDispatches=0`.
- Gateway `/health`: `{ ok: true, status: live }`.
- `openclaw-gateway.service`: `active/running`, `NRestarts=0`.
- Session health 360 minutes: `suspectedStuck=0`, `withErrors=0`.
- Model runtime failures 6h via MC endpoint: `counts={}`, `events=[]`.
- Existing `gateway-memory-monitor.timer`: active every ~2 minutes; recent outputs show `gateway_memory=ok` and `discord_watchdog=ok connected=True`.

But Gateway journal still contains early instability signals:

- `2026-05-05T11:55:15+02:00 [discord] gateway error: Error: Gateway heartbeat ACK timeout`
- `2026-05-05T11:59:53+02:00 [fetch-timeout] fetch timeout after 10000ms ... url=https://discord.com/api/v10/users/@me`
- `2026-05-05T12:22:30+02:00 [discord] gateway error: Error: Gateway heartbeat ACK timeout`
- `2026-05-05T12:23:00+02:00 [diagnostic] liveness warning: reasons=event_loop_delay ... eventLoopDelayP99Ms=2594.2 eventLoopDelayMaxMs=4508.9 eventLoopUtilization=0.738 cpuCoreRatio=0.815`

## Intended implementation

File:

`/home/piet/.openclaw/scripts/gateway-memory-monitor.py`

Add a read-only journal-signal scan that:

1. Uses `journalctl --user -u openclaw-gateway.service --since <N minutes ago>`.
2. Detects these exact classes:
   - `discord_heartbeat_ack_timeout`
   - `discord_fetch_timeout`
   - `event_loop_delay`
3. Prints one concise warning line when signals are found:
   - `gateway_runtime_signal=warning count=... classes=... latest=...`
4. Uses a cooldown file so the 2-minute timer does not spam repeated alerts for the same short window.
5. Does **not** restart Gateway and does **not** mutate OpenClaw config.

## Backup

Before editing:

`/home/piet/.openclaw/scripts/gateway-memory-monitor.py.bak-20260505T122346Z`

## Restart needed

No Gateway restart. No Mission Control restart. No timer restart required. The next timer invocation will use the changed script.

## Verification

1. `python3 -m py_compile /home/piet/.openclaw/scripts/gateway-memory-monitor.py`
2. Direct monitor run:
   - `/usr/bin/python3 /home/piet/.openclaw/scripts/gateway-memory-monitor.py`
3. Confirm output still contains:
   - `gateway_memory=ok`
   - `discord_watchdog=ok` or a specific skip reason
   - `gateway_runtime_signal=...`
4. Confirm no failed user units:
   - `systemctl --user --failed --no-pager`
5. Confirm timer still listed:
   - `systemctl --user list-timers 'gateway-memory-monitor.timer' --all --no-pager`

## Rollback

If syntax/direct run fails:

```bash
cp /home/piet/.openclaw/scripts/gateway-memory-monitor.py.bak-20260505T122346Z /home/piet/.openclaw/scripts/gateway-memory-monitor.py
```
