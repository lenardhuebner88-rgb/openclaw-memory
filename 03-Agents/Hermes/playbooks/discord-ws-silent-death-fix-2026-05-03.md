# Fix-Plan: Discord WS Silent Death — Nachhaltige Lösung

**Status:** Phase 1 DONE — Phase 2 Open
**Datum:** 2026-05-03
**Betroffene Systeme:** OpenClaw Gateway, gateway-memory-monitor.py, provider-hTInySyN.js

---

## Problem

Discord WS Event Stream stirbt lautlos. Gateway HTTP health meldet `ok/live`, aber der Discord-
Inbound-Stream ist tot. Kein Error geloggt. Workaround: manueller Gateway-Restart.

### Root Cause (verifiziert durch Codex + Claude, 2026-05-03)

| Layer | Ort | Bug |
|-------|-----|-----|
| L1 — Gateway Reconnect Bug | `provider-hTInySyN.js:3770` | `shouldReconnect=false` → `scheduleReconnect()` macht sofort `return` bei Code 1000 (Normal Close) — **kein Reconnect nach sauberem Close** |
| L2 — Monitor Gap | `gateway-memory-monitor.py:300` | Discord-Watchdog hängt hinter Früh-Return bei `rss is None` → **nie aufgerufen** wenn PID nicht gefunden wird |
| L3 — Crontab | Piet's crontab | 5-Min-Intervall = bis zu 5min Totzeit nach Recovery |

### L1 Detail — Der Reconnect-Bug

```
07:16:47 — [discord] gateway: Gateway websocket closed: 1000
→ socket.on("close", code=1000) in Zeile 3631
→ this.scheduleReconnect(true, 1000) in Zeile 3647
→ scheduleReconnect() Zeile 3769: if (!this.shouldReconnect) return ← BUG: shouldReconnect=false
→ 45 min Stille — kein reconnect, keine Kanäle
```

Code 1000 = normal close. `isFatalGatewayCloseCode(1000)` → `false`. Aber `shouldReconnect` ist `false`
irgendwann vor dem Close gesetzt worden (z.B. nach vorherigem fatal close oder initial ohne Reset).

**Alternative Hypothese (Claude):** `shouldReconnect` wird nach `close(1000)` auf `false` gesetzt —
ohne es je auf `true` zurückzusetzen — sodaas der nächste `scheduleReconnect()`-Call sofort returned.

---

## Fix-Phasen

### Phase 1 — Kurzfristig: Monitor-Patch (sofort, geringes Risiko)

**Ziel:** Discord-Watchdog muss **immer** laufen, unabhängig vom Memory-Check.

#### Patch 1A — Früh-Return bei rss is None entfernen
**Datei:** `/home/piet/.openclaw/scripts/gateway-memory-monitor.py`
**Zeile:** ~300 (`main()`)

```diff
  if rss is None:
      msg = f"[{ts}] gateway_memory=unknown reason=no_pid_found"
      print(msg)
      LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
      LOG_PATH.open("a").write(msg + "\n")
-     return 1
+     check_discord_gateway_transport(ts)
+     return 0
```

#### Patch 1B — PID-Fallback härten
**Datei:** `/home/piet/.openclaw/scripts/gateway-memory-monitor.py`
**Zeile:** ~55

Fallback-Kette erweitern:
1. `systemctl --user show openclaw-gateway -p MainPID --value` (primary, already used)
2. `pgrep -af 'openclaw.*gateway|node.*openclaw'` mit `/proc/<pid>/cmdline`-Validierung
3. Optional: Port-Match `ss -tlnp | grep 18789`

#### Patch 1C — Health-Fehler differenzierter loggen
**Datei:** `/home/piet/.openclaw/scripts/gateway-memory-monitor.py`
**Zeile:** ~180-200

Fehler werden momentan alle als `health_command_failed` aggregated. Unterscheiden:
- `health_command_failed` — openclaw CLI fehlgeschlagen
- `health_json_decode_error` — Output ist kein JSON
- `no_discord_health` — kein Discord-Account in Health

---

### Phase 2 — Mittelfristig: Gateway Idle-Detection (braucht OpenClaw-Update)

**Ziel:** Idle-Detector direkt im Discord-Provider, der bei >N min ohne Inbound-Payload
(einschliesslich Dispatch-Events) einen reconnect triggert.

**Datei:** `/home/piet/.npm-global/lib/node_modules/openclaw/dist/extensions/discord/provider-hTInySyN.js`

**Neue Methode in der DiscordGatewayClient-Klasse:**

```js
// In handlePayload(), nach jedem Dispatch-Event:
this.lastInboundAt = Date.now();

// In setupWebSocket():
startIdleWatch() {
  this.stopIdleWatch();
  const IDLE_TIMEOUT_MS = Number(process.env.OPENCLAW_DISCORD_GATEWAY_IDLE_TIMEOUT_MS ?? 180e3);
  this.idleTimer = setInterval(() => {
    if (!this.isConnected || !this.ws || this.ws.readyState !== 1) return;
    if (Date.now() - this.lastInboundAt > IDLE_TIMEOUT_MS) {
      this.emitter.emit("error", new Error(`Discord gateway idle timeout after ${Date.now() - this.lastInboundAt}ms`));
      this.scheduleReconnect(true);
    }
  }, 30e3);
  this.idleTimer.unref?.();
}

stopIdleWatch() {
  if (this.idleTimer) { clearInterval(this.idleTimer); this.idleTimer = undefined; }
}

// Aufruf in:
// - socket.on("open")    → startIdleWatch()
// - socket.on("close")   → stopIdleWatch()
// - disconnect()          → stopIdleWatch()
```

**Wichtig:** `lastInboundAt` muss auch in `pushStatus()` an `lastTransportActivityAt` gemapped werden,
damit der externe Monitor denselben Wert sieht.

---

### Phase 3 — Crontab-Intervall

**Datei:** Piet's crontab  
**Änderung:** `*/5 * * * *` → `*/2 * * * *` für gateway-memory-monitor.py  
**Risiko:** Sehr gering — mehr Runs, aber idempotent und mit flock-Lock geschützt

---

## Quality Gates

### Gate 1 — Pre-Flight
- [ ] Backup: `cp /home/piet/.openclaw/scripts/gateway-memory-monitor.py /home/piet/.openclaw/scripts/gateway-memory-monitor.py.bak-2026-05-03`
- [ ] Syntax-Check: `python3 -m py_compile /home/piet/.openclaw/scripts/gateway-memory-monitor.py`
- [ ] GPT: Read-back der relevanten Zeilen nach Patch

### Gate 2 — Test-Mode
- [ ] `OPENCLAW_DISCORD_WATCHDOG_TEST_MODE=1 python3 /home/piet/.openclaw/scripts/gateway-memory-monitor.py`
- [ ] Erwartet: Log-Zeile `discord_watchdog=stale action=test-mode` ODER `discord_watchdog=ok`
- [ ] Bei `rss is None`-Simulation: Watchdog-Logzeile muss erscheinen

### Gate 3 — Dry-Run ohne Effekt
- [ ] Monitor läuft 2x hintereinander, kein Gateway-Restart getriggert (Cooldown)
- [ ] Log zeigt korrekte `transport_age_sec` Werte

### Gate 4 — Integration
- [ ] Nach Fix: Gateway-Restart um 07:01 — seither keine neuen Stale-Events
- [ ] Monitor-Log zeigt `discord_watchdog=ok` für die nächsten 3 Runs (15 min)

---

## Validierung nach Deployment

```bash
# 1. Log beobachten
tail -f /home/piet/.openclaw/workspace/logs/gateway-memory-monitor.log

# 2. Test-Mode
OPENCLAW_DISCORD_WATCHDOG_TEST_MODE=1 python3 /home/piet/.openclaw/scripts/gateway-memory-monitor.py

# 3. Gateway-Health checken
curl -s http://127.0.0.1:18789/health

# 4. Letzte Discord-Inbound-Zeit im Health prüfen (nach Phase 2)
openclaw status --json | grep -i discord
```

---

## Dokumente

- Bug-Report: `/home/piet/vault/03-Agents/Hermes/lessons/bug-2026-05-03-discord-ws-silent-death.md`
- Dieses Fix-Dokument
- Monitor-Log: `/home/piet/.openclaw/workspace/logs/gateway-memory-monitor.log`
