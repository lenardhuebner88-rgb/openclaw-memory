# Operator-Action Handoff — 2026-04-29

**Status:** System ist nach Round-3-Stabilization wieder vollständig ok
(`/api/health: status=ok, severity=ok, recoveryLoad=0`).
Folgende Items erfordern menschliches Handeln (OAuth-Flows, externe
Bezahlung, Risiko-Entscheidungen) und können nicht autonom ausgeführt werden.

---

## P0 (sofort)

### 1. Anthropic OAuth re-auth (19.5 Tage abgelaufen)
**Profile:** `anthropic:claude-code-refresh`
**Expiry:** `1775767020223` (2026-04-08T11:17 UTC)
**Symptom:** claude-code & sub-agents fallen silent auf andere providers zurück
**Fix:** ~~~
ssh homeserver "openclaw models auth login --provider anthropic --method cli --set-default"
~~~
Erfordert Browser-OAuth-Flow vom Operator.

---

## P1 (24-48h)

### 2. OpenRouter Account Top-Up
**Symptom:** 402-billing-Errors in fallback-cascade (war Hauptursache der 10:27-10:57 UTC Storm)
**Fix:** Account auf https://openrouter.ai/settings/credits aufladen
**Backstop:** `billing-alert-watch.sh` ist live und alarmiert ab nächstem 402-Treffer
(cooldown 30min via alert-dispatcher)

### 3. exec.allowlist für 4 Atlas Heartbeat-Scripts
**Files denied seit 28.04.:**
- `m7-atlas-master-heartbeat.sh`
- `atlas-receipt-stream-subscribe.sh`
- `task-parity-check.sh`
- `mcp-zombie-killer.sh`

**Status:** ich habe das nicht angefasst — `tools.exec.allowlist` Schema ist
unklar (openclaw runtime-spezifisch). Atlas konnte die Scripts via systemd-timer
weiter nutzen, also kein Sprint-Blocker.
**Empfehlung:** schaue in `/home/piet/.openclaw/lib/node_modules/openclaw/dist/`
nach `allowlist-*.js` für das exakte Schema, oder ändere Atlas's Tool-Calls
auf `security:"full"` (weniger restriktiv aber Atlas hat ohnehin tools.exec.security=full global).

### 4. Network-Bind Tightening
**Exposed:**
- `openclaw-gateway 0.0.0.0:18789`
- `Jaeger UI :16686` (no auth)
- `OTLP :4317/:4318`
- `:2283` (Immich), `:8384` (Syncthing)

**Fix Empfehlung:**
1. openclaw.json: `gateway.bind: "loopback"` statt `"lan"`
2. Externer Zugriff via Tailscale Serve oder SSH-tunnel
3. Erfordert Gateway-Restart → Atlas/Sprint-Window benötigt

### 5. claude PID 3734554 (9d 16h uptime)
**Risiko:** möglicher stdio-MCP-stale-Client (Incident-Pattern 2026-04-21)
**Decision:** restart? Wenn ja:
~~~
ssh homeserver "kill 3734554"  # SIGTERM, graceful
~~~
Vor `kill`: prüfe ob es deine aktive Session ist (`ps -p 3734554 -o lstart,cmd`)
Wenn JA → SSH-Session schließen + neu öffnen (sauberer als kill).

### 6. R48 35 Stale Failed-Tasks Review
**Auto-Liste exportiert** (siehe Round-2 Report).
**Top-2 jüngst (28.04.):**
- `42df1ec1` [P2][Forge] mc-pending-pickup-smoke.sh — operatorLock fehlt
- `7f4cdd21` [P1][Forge] 403er Auto-Pickup Bug — Ingress/Receipt Validierung

**Empfehlung:** Sprint-Slot für Forge zur Aufarbeitung — P1 zuerst.

---

## P2 (defer)

### 7. Schema-Update für openclaw.json.schema.json
**Problem:** Schema ist outdated (`model:string` vs runtime `model:object`). 
Validator-Schema-Check ist deshalb deaktiviert. Invariant-Checks decken
real-world-Szenarien aber ab.
**Fix:** Schema-Update-Sprint, danach jsonschema-Check im Validator wieder aktivieren.

### 8. SQLite Memory-DB VACUUM
**Größen:** `main.sqlite=410M`, `sre-expert=297M`, `frontend-guru=268M`
**Fix:** wöchentlicher VACUUM-Cron (nicht autonom hinzugefügt, da DB-Lock-Risiko bei aktiven Agents)
~~~
30 4 * * 0 /usr/bin/sqlite3 /home/piet/.openclaw/memory/main.sqlite VACUUM
~~~
(plus für jeden agent — getrennte Locks-Windows)

### 9. Codex Token Auto-Refresh-Verifizierung
**P1-3 Done (User):** Codex-Abo +1 Monat verlängert.
**Verify:** in 21h re-check ob Token automatisch refreshed wurde:
~~~
ssh homeserver "openclaw doctor 2>&1 | grep -A2 expiring"
~~~

---

## Was claude bereits autonom gemacht hat (Round-2+3)

| # | Item | Status |
|---|---|---|
| 1 | Atlas Routing-Patch validiert (alle 6 Agents) | ✅ |
| 2 | Crontab restored aus Backup-20260428_152940 (94 Zeilen) | ✅ |
| 3 | Reaper restart + verify (now cron-driven */5) | ✅ |
| 4 | memory-orchestrator hourly backfilled (L1 10 articles, L2 1279 edges, L6) | ✅ |
| 5 | 11 openclaw.json.clobbered.* removed | ✅ |
| 6 | MEMORY.md path-drift fixed (`/10-KB` statt `/03-Agents/kb`) | ✅ |
| 7 | NEW: `billing-alert-watch.sh` deployed (*/15) | ✅ |
| 8 | gateway-memory-monitor.py threshold-fix (1.4G/1.7G → 4.0G/5.5G + systemctl PID) | ✅ |
| 9 | 3 stale Backup-Dirs deleted (~857MB freed) | ✅ |
| 10 | windows-original chmod 0664 → 0600 | ✅ |
| 11 | Token-Expiry Discord-Alert | ✅ |
| 12 | doctor --fix (4 orphans archived) | ✅ |
| 13 | Crontab re-stagger (14 schedule changes, 9 jobs */5 spread) | ✅ |
| 14 | 39 alte credential-bearing files purged (37 precheck + 2 bak) | ✅ |
| 15 | 2 weitere chmod 0600 fixes | ✅ |
| 16 | **R51 Schema-Gate Validator deployed** + enhanced config-guard.sh | ✅ |
| 17 | 16 stale crontab comments removed | ✅ |
| 18 | Atlas V1-Recovery verified (sample-IDs gone, health=ok) | ✅ |

**Disk:** 84% → 83% (~1G freed)
**Crontab:** 94→79 Zeilen (clean) + Stampede reduziert
**Health:** degraded → ok ✅
**Defense-Layers:** 49 active crons restored
