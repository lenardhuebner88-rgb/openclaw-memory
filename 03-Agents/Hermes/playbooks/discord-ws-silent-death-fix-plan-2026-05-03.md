# Discord WS Silent Death — Vollständiger Implementierungsplan

**Status:** Phase 1 DONE · Phase 2 READY TO IMPLEMENT
**Erstellt:** 2026-05-03
**Letztes Update:** 2026-05-03
**Owner:** Hermes / Piet
**Upstream:** OpenClaw Discord Provider (Node Module)

---

## Executive Summary

| Phase | Was | Status | Wer |
|-------|-----|--------|-----|
| 1 | Monitor-Fixes (Patch 1A + 1B) | ✅ DONE | Hermes |
| 2 | Gateway Reconnect Bug Fix | 📋 READY | Atlas/OpenClaw Dev |
| 3 | Crontab-Intervall | ⏳ PENDING | Piet |
| 4 | Upstream Bug Report | ⏳ PENDING | Atlas/Piet |

---

## Problem Statement

Discord WS Event Stream stirbt lautlos nach einem **normalen WebSocket Close (Code 1000)**.
Gateway HTTP health meldet `{"ok":true,"status":"live"}`, aber der Discord-Inbound-Stream
ist tot. Kein Error geloggt. Totzeit: bis zu 45 Minuten. Workaround: manueller Gateway-Restart.

**Incident Timeline (2026-05-03):**
```
00:34 — Letzter Discord-Transport (vor Incident)
07:01 — Gateway-Restart (durch Hermes nach Incident-Detection)
07:10 — Letzter transport_activity
07:13 — CommandLaneTaskTimeoutError (330s Task in Discord lane)
07:16 — Gateway websocket closed: 1000  ← NORMAL CLOSE
07:30-08:02 — 45 min Stille — kein reconnect, keine Kanäle
```

---

## Phase 1 — Monitor-Layer (✅ DONE)

### Was war das Problem?

| Bug | Ort | Auswirkung |
|-----|-----|------------|
| Früh-Return bei `rss is None` | `gateway-memory-monitor.py:~300` | Watchdog nie aufgerufen wenn PID nicht gefunden |
| Node-v22 Path existiert nicht im Cron-Env | `load_openclaw_health()` | Health-Check always fails → `discord_watchdog=skip` |

### Angewendete Fixes

**Patch 1A — Discord-Watchdog auch bei fehlender PID:**
```python
# Zeile ~320 — Früh-Return entfernt:
# ALT: if rss is None: return
# NEU: check_discord_gateway_transport(ts) wird IMMER aufgerufen
```

**Patch 1B — HTTP-Fallback für Health-Check:**
```python
# Zeile ~239 — subprocess node durch urllib.request ersetzt:
# Primär: openclaw CLI
# Fallback: HTTP GET http://127.0.0.1:18789/health
# Fallback-of-Fallback: curl
```

### Validierung

```bash
# Syntax Check
python3 -m py_compile gateway-memory-monitor.py  # ✅ PASS

# Test-Mode Run
OPENCLAW_DISCORD_WATCHDOG_TEST_MODE=1 python3 gateway-memory-monitor.py
# Erwartet: discord_watchdog=rss_ok oder discord_watchdog=http_fallback_ok

# Log-Datei
tail -5 ~/.openclaw/workspace/logs/gateway-memory-monitor.log
```

### Backup

```
/home/piet/.openclaw/scripts/gateway-memory-monitor.py.bak-2026-05-03
```

---

## Phase 2 — Gateway Reconnect Bug (📋 READY TO IMPLEMENT)

### Root Cause — Präzise

```
provider-hTInySyN.js — Close-Handler, Zeile 3631-3647

Ablauf bei Close(1000):
1. socket.on("close", code=1000)  →  Zeile 3631
2. if (!this.shouldReconnect) return;  →  Zeile 3639
3. isFatalGatewayCloseCode(1000) → false  →  weiter
4. canResumeAfterGatewayClose(1000) → true  →  weiter
5. scheduleReconnect(true, 1000)  →  Zeile 3647
   → if (!this.shouldReconnect) return;  →  Zeile 3770  ← BUG
6. NICHTS passiert — kein reconnect, kein log
```

**Genauer Bug:** `shouldReconnect` ist `false` zum Zeitpunkt des Close-Events.
Das passiert, weil:
1. Init: `shouldReconnect = false` (Zeile 3545)
2. Connect: `shouldReconnect = true` (Zeile 3584)
3. Irgendwann vor Close(1000): `shouldReconnect = false` (gesetzt durch `disconnect()` oder Error)
4. Close(1000) kommt → `shouldReconnect = false` → early return → kein reconnect

**Mögliche Trigger zwischen 07:10 und 07:16:**
- `CommandLaneTaskTimeoutError` löst vermutlich einen `disconnect()`-Call aus
- Oder: ein `InvalidSession` mit `d=false` Payload setzt `shouldReconnect = false`

### Fix-Optionen

#### Option A — Fix im Close-Handler (Empfohlen)

**Datei:** `provider-hTInySyN.js`
**Zeilen:** ~3636-3647

```javascript
// VORHER (Bug):
socket.on("close", (code) => {
    if (socket !== this.ws) return;
    this.stopHeartbeat();
    this.outboundLimiter.clear();
    this.isConnecting = false;
    this.isConnected = false;
    this.emitter.emit("debug", `Gateway websocket closed: ${code}`);
    if (!this.shouldReconnect) return;  // ← BUG: early return verhindert reconnect
    if (isFatalGatewayCloseCode(closeCode)) {
        this.shouldReconnect = false;
        this.emitter.emit("error", new Error(`Fatal gateway close code: ${code}`));
        return;
    }
    const canResume = canResumeAfterGatewayClose(closeCode);
    if (!canResume) this.resetSessionState();
    this.scheduleReconnect(canResume, closeCode);
});

// NACHHER (Fix):
socket.on("close", (code) => {
    if (socket !== this.ws) return;
    this.stopHeartbeat();
    this.outboundLimiter.clear();
    this.isConnecting = false;
    this.isConnected = false;
    this.emitter.emit("debug", `Gateway websocket closed: ${code}`);
    
    // If this was a fatal close, stop reconnect attempts
    if (isFatalGatewayCloseCode(closeCode)) {
        this.shouldReconnect = false;
        this.emitter.emit("error", new Error(`Fatal gateway close code: ${code}`));
        return;
    }
    
    // For non-fatal closes: ALWAYS attempt reconnect, regardless of shouldReconnect flag
    // The shouldReconnect flag is only authoritative for client-initiated disconnect()
    const canResume = canResumeAfterGatewayClose(closeCode);
    if (!canResume) this.resetSessionState();
    this.scheduleReconnect(canResume, closeCode);
});
```

**Diff:**
```diff
- if (!this.shouldReconnect) return;
- if (isFatalGatewayCloseCode(closeCode)) {
-     this.shouldReconnect = false;
-     this.emitter.emit("error", ...);
-     return;
- }
- const canResume = canResumeAfterGatewayClose(closeCode);
- if (!canResume) this.resetSessionState();
- this.scheduleReconnect(canResume, closeCode);
+ if (isFatalGatewayCloseCode(closeCode)) {
+     this.shouldReconnect = false;
+     this.emitter.emit("error", ...);
+     return;
+ }
+ const canResume = canResumeAfterGatewayClose(closeCode);
+ if (!canResume) this.resetSessionState();
+ this.scheduleReconnect(canResume, closeCode);
```

#### Option B — Reset shouldReconnect in Error-Handlern (Alternative)

Prüfen ob `shouldReconnect` in Error-Pfaden (z.B. `InvalidSession` mit `d=false`) korrekt
zurückgesetzt wird. Das ist aber weniger robust als Option A.

### Implementierungs-Schritte (Atlas/Dev)

````markdown
### Task 1: Fix Close-Handler in provider-hTInySyN.js

**Ziel:** Non-fatal Close (1000, 1001, etc.) reconnectet immer

**Datei:** /home/piet/.npm-global/lib/node_modules/openclaw/dist/extensions/discord/provider-hTInySyN.js

**Step 1: Zeilen 3636-3647 lesen und verstehen**
```bash
sed -n '3636,3647p' provider-hTInySyN.js
```

**Step 2: Patch anwenden**
Die Zeile `if (!this.shouldReconnect) return;` (3639) entfernen.
Stattdessen: `isFatalGatewayCloseCode` Check VOR `scheduleReconnect`.

**Step 3: Test-Setup — Discord WS Close simulieren**
```bash
# Starte Gateway mit aktiver Discord-Verbindung
systemctl --user status openclaw-gateway.service

# Beobachte Logs während des Tests
journalctl --user -u openclaw-gateway.service -f | grep -E "discord|close|reconnect"
```

**Step 4: Validierung nach Patch**
- Discord-Kanal anschreiben → sollte funktionieren
- Gateway-Log prüfen: kein "Gateway websocket closed: 1000" ohne anschliessenden Reconnect
- Nach Close(1000): innerhalb von 30s muss ein neuer CONNECT-Log erscheinen

**Step 5: Upstream-Commit vorbereiten**
Änderung in `src/` (nicht `dist/`) machen:
`src/extensions/discord/src/internal/gateway.ts` oder ähnlich.
````

### Verification Steps

Nach Fix (Atlas oder Developer):

```bash
# 1. Gateway neustarten
systemctl --user restart openclaw-gateway.service

# 2. Warten bis Discord verbunden
sleep 30
journalctl --user -u openclaw-gateway.service --since "1 minute ago" | grep -E "discord|ready|connected"

# 3. Discord-Kanal anschreiben
# Erwartet: Bot antwortet

# 4. Manuell WebSocket-Close triggern (simulieren via Gateway-Neustart oder Discord-Disconnect)
# Im Log prüfen: nach close(1000) kommt reconnect

# 5. Monitor-Log prüfen
tail -20 ~/.openclaw/workspace/logs/gateway-memory-monitor.log
```

---

## Phase 3 — Crontab-Intervall (⏳ PENDING — Piet)

**Aktion:** Piet muss manuell ausführen:

```bash
# Aktuelles Intervall prüfen
crontab -l | grep gateway-memory-monitor

# Von */5 auf */2 min ändern
crontab -e
# ALT: */5 * * * * /usr/bin/python3 /home/piet/.openclaw/scripts/gateway-memory-monitor.py
# NEU: */2 * * * * /usr/bin/python3 /home/piet/.openclaw/scripts/gateway-memory-monitor.py
```

**Warum 2 min?** Weniger Totzeit nach Incident. 5 min heisst: bis zu 5 min
bis zum nächsten Check nach einem Discord-Ausfall.

---

## Phase 4 — Upstream Bug Report (⏳ PENDING — Atlas/Piet)

** Ziel:** Offizielles Issue im OpenClaw-Repo öffnen

**Issue-Template:**
```
Title: Discord Gateway: No reconnect after normal WebSocket close (code 1000)

## Problem
When Discord Gateway websocket closes with code 1000 (normal close), the provider
does not reconnect. shouldReconnect flag is false at the time of close event,
causing an early return in scheduleReconnect().

## Steps to Reproduce
1. OpenClaw Gateway running with Discord provider active
2. Discord websocket closes normally (code 1000)
3. Expected: reconnect within 30s
4. Actual: no reconnect, Discord inbound silent for 45+ minutes

## Root Cause
In provider-hTInySyN.js close handler (line ~3639):
  if (!this.shouldReconnect) return;
This early return fires even for non-fatal close codes (1000, 1001),
preventing scheduleReconnect() from being called.

## Environment
- OpenClaw version: [from openclaw --version]
- Node: [from node --version]
- OS: huebners (Linux)
```

---

## Offene Fragen

1. **Warum war `shouldReconnect = false` vor dem Close(1000)?**
   Hypothese: `CommandLaneTaskTimeoutError` um 07:13 triggert implizit `disconnect()`.
   → Muss durch Log-Analyse oder Code-Review verifiziert werden.

2. **Warum hat der Monitor nicht früher erkannt?**
   Monitor Crontab ist 5 min. Nach 07:16:47 close wäre der nächste Check ~07:20.
   Bis dahin war schon 45 min Stille — also selbst mit 2-min-Intervall wäre
   das frühestens um ~07:20 erkannt worden.
   → Monitor-Check ist NUR ein Backup. Der Gateway-Reconnect-Fix (Phase 2) ist der PRIMARY Fix.

---

## Abhängigkeiten

```
Phase 2 (Gateway Fix)
  └─› Phase 4 (Upstream Bug Report) — hängt NICHT ab, kann parallel

Phase 3 (Crontab)
  └─› Piet muss manuell machen — keine technische Abhängigkeit
```

---

## Risiken und Mitigations

| Risiko | Wahrscheinlichkeit | Mitigation |
|--------|-------------------|------------|
| Fix in Node Module geht bei OpenClaw-Update verloren | Hoch | Scripts in `/scripts/`, nicht in Node Modules. Gateway-Fix: Upstream-Commit |
| Reconnect-Loop bei instabilem Netz | Niedrig | `maxAttempts=50` in `scheduleReconnect()` begrenzt |
| Monitor produziert false positives | Niedrig | Test-Mode verifiziert before/after |
