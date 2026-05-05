# Gateway Runtime Signal Watchdog Receipt — 2026-05-05

## Result

Applied the approved next hardening step: the existing `gateway-memory-monitor.py` watchdog now also scans the recent Gateway journal for early Discord/event-loop instability signals and reports them as `gateway_runtime_signal=...`.

This is report-only. No Gateway restart, no Mission Control restart, no OpenClaw config edit, no timer/service unit edit.

## Live evidence before change

Green baseline:

- Mission Control `/api/health`: `status=ok`, `staleOpenTasks=0`, `recoveryLoad=0`, `orphanedDispatches=0`.
- Gateway `/health`: `{ ok: true, status: live }`.
- `openclaw-gateway.service`: `active/running`, `NRestarts=0`.
- Session health 360 minutes: `suspectedStuck=0`, `withErrors=0`.
- Model runtime failures 6h via MC endpoint: `counts={}`, `events=[]`.
- Existing `gateway-memory-monitor.timer`: active every ~2 minutes; pre-change output already showed `gateway_memory=ok` and `discord_watchdog=ok connected=True`.

Detected gap:

- Gateway journal showed real early instability signals not surfaced by the watchdog:
  - `Gateway heartbeat ACK timeout`
  - `[fetch-timeout] ... discord.com/api/v10/users/@me`
  - `liveness warning: reasons=event_loop_delay ... eventLoopDelayP99Ms=2594.2 ... eventLoopDelayMaxMs=4508.9 ... eventLoopUtilization=0.738`

## Plan document

`/home/piet/vault/03-Agents/Hermes/gateway-runtime-signal-watchdog-plan-2026-05-05.md`

## Backup

Created before editing:

`/home/piet/.openclaw/scripts/gateway-memory-monitor.py.bak-20260505T122346Z`

SHA256 before edit:

```text
266a2cb7f5f178c7f3b798c3c283c768059da0f92f0cb5cadf64ae0f8d4df344  /home/piet/.openclaw/scripts/gateway-memory-monitor.py
266a2cb7f5f178c7f3b798c3c283c768059da0f92f0cb5cadf64ae0f8d4df344  /home/piet/.openclaw/scripts/gateway-memory-monitor.py.bak-20260505T122346Z
```

## Exact file changed

`/home/piet/.openclaw/scripts/gateway-memory-monitor.py`

## Exact change summary

Added:

- `re` import.
- Runtime signal constants:
  - `OPENCLAW_RUNTIME_SIGNAL_LOOKBACK_MIN`, default `10`.
  - `OPENCLAW_RUNTIME_SIGNAL_COOLDOWN_SEC`, default `1800`.
  - cooldown file `/tmp/openclaw-gateway-runtime-signal.cooldown`.
- Read-only pattern detection for:
  - `discord_heartbeat_ack_timeout`
  - `discord_fetch_timeout`
  - `event_loop_delay`
- New function: `check_gateway_runtime_journal_signals(ts)`.
- Calls to the new function in both normal and no-PID paths of `main()`.

Report format examples:

```text
gateway_runtime_signal=ok lookback_min=10 count=0
gateway_runtime_signal=warning action=report-only lookback_min=180 count=4 classes=discord_fetch_timeout,discord_heartbeat_ack_timeout,event_loop_delay latest="..."
```

## Verification

1. Syntax/compile:

```text
python3 -m py_compile /home/piet/.openclaw/scripts/gateway-memory-monitor.py
PASS
```

2. Direct normal run:

```text
[2026-05-05T12:26:03Z] gateway_memory=ok rss_kb=681372 threshold_warning_kb=4000000 threshold_critical_kb=5500000
[2026-05-05T12:26:03Z] discord_watchdog=ok connected=True transport_age_sec=27 threshold_sec=600
[2026-05-05T12:26:03Z] gateway_runtime_signal=ok lookback_min=10 count=0
```

3. Positive detection test with wider read-only lookback:

```text
OPENCLAW_RUNTIME_SIGNAL_LOOKBACK_MIN=180 OPENCLAW_RUNTIME_SIGNAL_COOLDOWN_SEC=0 /usr/bin/python3 /home/piet/.openclaw/scripts/gateway-memory-monitor.py
```

Result:

```text
gateway_runtime_signal=warning action=report-only lookback_min=180 count=4 classes=discord_fetch_timeout,discord_heartbeat_ack_timeout,event_loop_delay latest="... event_loop_delay ..."
```

4. Test cooldown artifact removed after positive test:

```text
runtime_signal_cooldown_removed
```

5. Timer picked up changed script without restart:

```text
2026-05-05T14:26:28+02:00 ... gateway_memory=ok ...
2026-05-05T14:26:28+02:00 ... discord_watchdog=ok connected=True ...
2026-05-05T14:26:28+02:00 ... gateway_runtime_signal=ok lookback_min=10 count=0
```

6. Timer remains scheduled:

```text
gateway-memory-monitor.timer NEXT Tue 2026-05-05 14:28:26 CEST
```

7. Failed user units:

```text
0 loaded units listed.
```

8. Gateway post-check:

```text
{"ok":true,"status":"live"}
NRestarts=0
ActiveState=active
SubState=running
```

## Rollback

If needed:

```bash
cp /home/piet/.openclaw/scripts/gateway-memory-monitor.py.bak-20260505T122346Z /home/piet/.openclaw/scripts/gateway-memory-monitor.py
```

## Residual risk / next observation

The monitor now detects the exact signal class that was previously invisible in watchdog output. The next useful observation is whether future `Gateway heartbeat ACK timeout`, Discord `fetch-timeout`, or `event_loop_delay` lines appear and correlate with large Atlas/Forge turns, systemJobs, or Discord reconnect behavior.
