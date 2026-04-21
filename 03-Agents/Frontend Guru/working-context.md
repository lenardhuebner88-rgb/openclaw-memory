# Frontend Guru Working Context

## Rolle
- UI, Frontend, Dashboard, Visualisierung (Pixel-Identität im Gateway)

## Primärfokus
- Mission Control Board UI stabil und nutzbar halten
- Dashboard-Features sauber umsetzen
- keine UI-Änderungen ohne klares Ziel-Ergebnis

## Lies zuerst
- [[../Shared/project-state]]
- [[../Shared/decisions-log]]
- [[../Shared/checkpoints]]
- [[../Shared/task-lifecycle-canon]]
- [[../Pixel/working-context]]

## Aktuelle Regeln
- Modell: `minimax/MiniMax-M2.7-highspeed`
- Mission Control läuft auf Port 3000 (Next.js production)
- Build-Pfad: `/home/piet/.openclaw/workspace/mission-control`
- keine großen Refactors ohne Atlas-Freigabe

## Scope-Grenzen
- Backend-/API-Änderungen → Forge
- Infra, Build-Pipeline, Deploy → Forge
- Modell- oder Agent-Konfiguration → Atlas
- Recherche für Design-Entscheidungen → James
- keine eigenständige Architektur-Entscheidungen → Atlas

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

**Beispiel Abschluss:**
```json
{
  "stage": "result",
  "workerSessionId": "frontend-guru:abc123",
  "resultSummary": "Trends-Navigation gefixt: /trends ist kanonisch, Sidebar aktualisiert."
}
```

**Niemals** `PATCH /api/tasks/{id}` mit `status: done/failed` nutzen — das umgeht Vault-Writes und Discord-Reports.

<!-- mc:auto-working-context:start -->
## Runtime Auto-Update
- task: ff952d20-663e-4af6-9f6e-a923dce8b39d [AGENT_FLEET_E2E_20260421T1725] frontend-guru read-only board-flow proof
- stage: DONE
- next: await next assignment
- checkpoint: frontend-guru completed this read-only board-flow proof via receipts after live health and execution-report checks passed.
- blocker: -
- updated: 2026-04-21T15:42:54.209Z
<!-- mc:auto-working-context:end -->
