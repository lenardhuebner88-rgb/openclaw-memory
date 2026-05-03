# Bug Report: Discord WS Event Stream Silent Death

**Date:** 2026-05-03  
**Severity:** High  
**Status:** Confirmed  

## Summary

OpenClaw Gateway Discord WS event stream dies silently without automatic reconnect. Gateway HTTP health reports `{"ok":true,"status":"live"}` while the Discord inbound event stream is completely dead. No error logged, no disconnect message — silence is the only signal.

## Symptoms

- Atlas (Discord bot) non-responsive in all channels
- Gateway health endpoint: `{"ok":true,"status":"live"}` ✓
- `openclaw-gateway.service`: `ActiveState=active`, `SubState=running` ✓
- `openclaw-discord-bot.service`: `ActiveState=active`, `SubState=running` ✓
- No `⇄` (WS heartbeats) in journal for hours
- No Discord inbound events (MESSAGE_CREATE, etc.) in gateway logs
- `nativeHook.invoke` errors appear en masse after stream death
- `sessions --active 30`: zero Discord sessions

## Timeline (Incident #2026-05-03-001)

| Time | Event |
|------|-------|
| 2026-05-03 00:34 | Last WS `⇄ res ✓ system-presence` heartbeat |
| 2026-05-03 00:36 | Last `sessions.list` poll |
| 2026-05-03 02:46 | Mass `nativeHook.invoke` errors begin |
| 2026-05-03 ~06:53 | User reports Atlas silent |
| 2026-05-03 07:01 | Gateway restart (stop + start) |
| 2026-05-03 07:01:43 | Discord channels resolved, client initialized |
| 2026-05-03 07:01:54 | Liveness warning (eventLoopDelayP99Ms=41.6, max=6723.5ms) |

## Root Cause Hypothesis

WS connection to Discord Gateway API enters a broken state (likely Discord opcode 7 / Opcode 7: Reconnect or session invalidation) without the gateway recognizing the disconnection. The gateway's WS layer continues to report healthy while the underlying connection is dead. No automatic reconnect triggered.

**Key diagnostic rule from runbook:**  
> The log never shows a "Discord disconnected" message — the silence itself is the signal.

## Workaround

```bash
systemctl --user stop openclaw-gateway.service
sleep 2
systemctl --user start openclaw-gateway.service
```

Note: `systemctl --user restart` can timeout; use explicit `stop` + `start`.

## Fix Requirements (for Atlas)

1. **Detection:** Monitor for absence of Discord WS heartbeats (`⇄`) over a configurable threshold (e.g., 5 min). If no heartbeat in N minutes → trigger reconnect.
2. **Reconnect:** On disconnect detection, close broken WS, create new Discord gateway WS connection, re-resolve channels.
3. **Logging:** Log explicit "Discord WS disconnected, reconnecting..." message so future incidents are unambiguous.
4. **Liveness alert:** The eventLoopDelay spike (max 6723ms) during startup may be a leading indicator — investigate correlation.

## Related Runbooks

- `openclaw-gateway-down.md` (general)  
- `openclaw-discord-commands-broken.md` (symptom)  
- `gateway-discord-provider-401-429.md` (related Discord API auth)

## Tags

`#discord` `#websocket` `#silent-failure` `#openclaw-gateway`
