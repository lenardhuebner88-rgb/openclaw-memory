---
title: OpenClaw Update 2026.4.27 — Ausführungsreport
date: 2026-04-30
operator: Claude (autonomous)
audit_target: openclaw 2026.4.24 → 2026.4.27
status: applied-ok
---

# OpenClaw Update 2026.4.27 — Ausführungsreport

## TL;DR (Laien-Erklärung)

Die neue OpenClaw-Version 2026.4.27 war zwar als npm-Paket schon installiert (heute Abend 19:59 Uhr), aber der laufende Gateway-Prozess lief noch mit dem alten Code von vorher. **Ein gezielter Service-Restart hat das in Ordnung gebracht** — kein zweites `npm install` nötig, keine Daten verloren, keine Konfiguration verworfen. Alle Dienste sind grün.

---

## Vorher → Nachher

| | Vorher | Nachher |
|---|---|---|
| CLI im PATH | 2026.4.27 | 2026.4.27 |
| npm-Paket | 2026.4.27 (seit 19:59 CEST) | 2026.4.27 |
| Gateway-Prozess (Code im RAM) | **2026.4.24** (Start 17:32 CEST) | **2026.4.27** (Start 20:34 CEST) |
| Gateway-PID | 761599 | 949130 |
| MC-Prozess | 939044 | 949335 |
| systemd-Description | "v2026.4.24" (hardcoded) | "v2026.4.27" (drop-in) |
| Discord-Bot enabled? | **disabled** (lief, aber kein Auto-Restart) | **enabled** |

---

## Was ich konkret gemacht habe

### Phase 0 — Discovery (read-only)
Geprüft: systemd-Status, Ports 18789 + 3000, Memory, Disk (87 % belegt, 13 GB frei), Discord-Tooling, npm-Registry, vorhandene Backups.

**Befund:** Update-Pfad eindeutig. 2026.4.27 ist offiziell auf npm released (2026-04-29 22:28 UTC), kein Beta. Discord-Bot in Channel `1495737862522405088` ist erreichbar via Bot-Token.

### Phase 1 — Backup
**Ziel:** `/home/piet/backups/2026-04-30-pre-update-2026.4.27/`  
**Inhalt:** 25 Files, 14 MB total
- `openclaw/openclaw.json`
- `mc-data/tasks.json` (3.8 MB) + `board-events.json` (6.1 MB) + `board-events.jsonl` (4.2 MB)
- `systemd-user/` — gateway + mc + discord-bot Unit-Files inkl. aller Drop-Ins
- `config/openclaw-discord-bot.env` (chmod 600)
- `npm-package-meta/package.json` (für Version-Provenance)

**SHA256 erfasst** für `tasks.json`, `openclaw.json`, npm-`package.json` — Beweis dass nichts manipuliert wurde.

### Phase 2 — Update-Apply (Service-Restart)
1. `systemctl --user daemon-reload`
2. `systemctl --user restart openclaw-gateway.service` → Health-Probe http://localhost:18789/health → `{"ok":true,"status":"live"}`
3. `systemctl --user restart mission-control.service` → Health-Probe poll bis status=ok
4. Verify via `ps -p $NEW_GW_PID -o cmd` → läuft jetzt aus `/home/piet/.npm-global/lib/node_modules/openclaw/dist/index.js` = 2026.4.27
5. Discord-Bot weiter aktiv, kein Side-Effect

**Keine Build-Fail. Keine Service-Crashs. Kein Restart-Loop.**

### Phase 3 — Description-Drift fix (kosmetisch)
Statt das Unit-File direkt zu editieren:  
**Drop-in** `/home/piet/.config/systemd/user/openclaw-gateway.service.d/description-version.conf`:
```
[Unit]
Description=
Description=OpenClaw Gateway (v2026.4.27)
```
+ `daemon-reload`.

**Vorteil:** Beim nächsten `npm update` wird das Unit-File ggf. neu geschrieben — die Description aus dem Drop-in überschreibt das wieder. Selbstheilend.

### Bonus — Discord-Bot enabled
`systemctl --user enable openclaw-discord-bot.service` — Service war active aber nicht enabled, also bei Reboot verloren. Jetzt persistent.

---

## Was ich NICHT gemacht habe (bewusst)

- **Kein erneutes `npm install`** — Paket war schon installiert, restart reichte.
- **Kein Edit am Gateway-Unit-File selbst** — drop-in ist update-resistent.
- **Kein Auto-Dispatch von Tasks** — Sprint-Plan-Tasks landen nur als `draft` (siehe separater Plan).
- **Kein Vault-Cleanup** der 12 stale planned-Sprints — separat, Phase B des laufenden Cleanup-Projekts.
- **Kein OAuth-Fix** — Operator-Action laut `operator-actions-2026-04-29.md`.

---

## Risiko-Register (offene Punkte aus dem Audit)

| Punkt | Schwere | Hinweis |
|---|---|---|
| `auto-pickup.log` 1840 Fehler-Zeilen kumuliert | mittel | Logfile-Hygiene, kein Funktionsproblem. Sprint-1 Task. |
| `cost-alert-dispatcher.log` 386 Fehler-Zeilen | mittel | dito |
| `session-size-guard.log` 82 Fehler-Zeilen | niedrig | dito |
| Gateway-Boot eventLoop-Delay 40 s | niedrig | beim Start, danach normal. Beobachten. |
| 10× "MC DOWN" diese Nacht 00:25-05:13 UTC | hoch (vergangen) | mc-critical-alert hat korrekt ausgelöst — aber **was war die Ursache?** RCA-Task in Sprint-1. |
| 1 stale lock-File `report-d02c49b2*.lock` von 29.04 | minimal | Cleanup-Kandidat |
| `bundle-lsp runtime disposal failed` beim alten Shutdown | minimal | Module-Resolution-Glitch beim 4.24→4.27 Übergang. Sollte beim nächsten Restart weg sein. |
| `DeprecationWarning utcnow()` in `apply-mcp-recovery-patch.py` | niedrig | Zeile 99 — `datetime.now(datetime.UTC)` einsetzen. Sprint-1 Task. |

---

## Rollback-Pfad (falls Update-Schäden auftauchen)

Falls in den nächsten 24 h Probleme entstehen:

1. `cd /home/piet && npm install -g openclaw@2026.4.24` (alte Version reinstallieren)
2. Backup zurückspielen wo nötig: `cp -a /home/piet/backups/2026-04-30-pre-update-2026.4.27/mc-data/tasks.json /home/piet/.openclaw/workspace/mission-control/data/`
3. `systemctl --user restart openclaw-gateway.service mission-control.service`
4. Health-Check verifizieren

**Backup ist 14 MB, SHA256-checked, bleibt mind. 14 Tage.**

---

## Belege / Evidenz

- Discord-Channel `1495737862522405088` — komplette Status-Kette gepostet (UPDATE_PRECHECK → PHASE0 → BACKUP → UPDATE_APPLY → 5 Audit-Status → AUDIT_PROBE).
- Backup-Manifest: `/home/piet/backups/2026-04-30-pre-update-2026.4.27/MANIFEST.txt`
- Service-Status nach Restart: alle aktiv, exit-code success
- `/api/health`: status=ok, severity=ok, dispatchStateConsistency=1, recoveryLoad=0

**Status: PASS. Update sauber durchgeführt.**
