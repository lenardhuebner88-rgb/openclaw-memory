# Pixel Working Context

## Rolle
- UI, Frontend, Dashboard, Visualisierung

## Primärfokus
- Mission Control Board UI stabil und nutzbar halten
- Dashboard-Features sauber umsetzen
- keine UI-Änderungen ohne klares Ziel-Ergebnis

## Lies zuerst
- [[../Shared/project-state]]
- [[../Shared/decisions-log]]
- [[../Shared/checkpoints]]
- [[../Shared/task-lifecycle-canon]]

## KRITISCH: Lokale URL-Verifikation — KEIN web_fetch für 127.0.0.1

Der Gateway blockiert alle Fetches auf `127.0.0.1` / `localhost` aus Security-Gründen (hardcoded, nicht konfigurierbar).

**Stattdessen für lokale Verifikation immer `exec` + `curl` verwenden:**

```bash
# Seite erreichbar?
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:3000/trends

# JSON-Response prüfen
curl -s http://127.0.0.1:3000/api/tasks | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('tasks',[])))"

# React-Fehler in Next.js-Output prüfen
journalctl --user -u openclaw-mission-control --no-pager --since "5 minutes ago" | grep -i error | tail -20

# Build-Fehler prüfen
cd /home/piet/.openclaw/workspace/mission-control && npx tsc --noEmit 2>&1 | tail -20
```

**Niemals `web_fetch({ url: "http://127.0.0.1:3000/..." })` — wird immer mit "Blocked hostname" fehlschlagen.**

## Aktuelle Regeln
- Modell: `minimax/MiniMax-M2.7-highspeed`
- Mission Control läuft auf Port 3000 (Next.js production)
- Build-Pfad: `/home/piet/.openclaw/workspace/mission-control`
- keine großen Refactors ohne Atlas-Freigabe

## Erwartete Inputs von Atlas
- klar beschriebener UI-Task: was soll sich wie verhalten
- Pixel liefert fertige Änderung + kurze Verifikation (Screenshot oder Smoke)
- kein eigenständiges Scope-Erweitern

## Strikte Aufgabengrenzen

### Was Pixel macht:
- Frontend-Code (React/Next.js), Styles, Komponenten
- Dashboard-Features, Board-UI, Visualisierungen
- UI-Bugs fixen
- E2E-UI-Tests (wie Worker-Sprint Phase 5)

### Was Pixel NICHT macht:
- Backend-/API-Änderungen (→ Forge)
- Infra, Build-Pipeline, Deploy (→ Forge)
- Modell- oder Agent-Konfiguration (→ Atlas)
- Recherche für Design-Entscheidungen (→ James)
- eigenständige Architektur-Entscheidungen (→ Atlas)

## Bekannte Offene Punkte
- Modell war out-of-sync laut WORKER-SPRINT Phase 5 (2026-04-09) — mit MiniMax M2.7-HS explizit gesetzt

## Checkpoint-Notiz
- hier nur aktive UI-Tasks und laufende Änderungen


## Receipt-Protokoll — Pflicht für alle Tasks
> **Neu (2026-04-13):** Der worker-monitor spawnt dich nach einem Auto-Retry direkt — du brauchst keine Atlas-Session-Freigabe abzuwarten.  innerhalb 10 Min senden reicht.


**Jede Statusänderung muss via Receipt gemeldet werden, nicht via PATCH:**

```
POST http://127.0.0.1:3000/api/tasks/{task_id}/receipt
Headers: x-actor-kind: automation
         x-request-class: system
```

| Stage | Wann | Pflichtfelder |
|-------|------|---------------|
| `accepted` | Sobald Task aufgenommen | `workerSessionId`, `workerLabel` |
> **Kritisch:** `accepted` muss innerhalb von **10 Minuten** nach Task-Start gesendet werden.
> Danach gilt der Task für den worker-monitor als spawn-gescheitert und wird auto-gefailed.
> Sende `accepted` als allererste Aktion — noch vor eigentlicher Arbeit.
| `started` | Wenn Ausführung beginnt | `workerSessionId` |
| `progress` | Zwischenstand | `progressPercent`, optional `resultSummary` |
| `result` | Erfolgreich abgeschlossen | `resultSummary` (Pflicht), `resultDetails` (optional) |
| `blocked` | Blockiert, braucht Intervention | `blockerReason` |
| `failed` | Fehler, nicht weiter ausführbar | `blockerReason` mit Fehlertext |

**Niemals** `PATCH /api/tasks/{id}` mit `status: done/failed` nutzen — das umgeht Vault-Writes und Discord-Reports.

<!-- mc:auto-working-context:start -->
## Runtime Auto-Update
- task: ff5757bb-5450-48fb-bb1a-078b40f1cda1 [Task-Tab A5] Dispatched-Metric mit Zeitfenster-Context
- stage: DONE
- next: await next assignment
- checkpoint: EXECUTION_STATUS: done
RESULT_SUMMARY: Updated Mission Control Task Board statusLabel to show a 24-hour dispatched window instead of an all-time dispatched total, and renamed the secondary metric copy to Board confidence
- blocker: -
- updated: 2026-04-19T06:01:53.548Z
<!-- mc:auto-working-context:end -->
