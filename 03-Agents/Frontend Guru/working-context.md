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
- task: cfe8dbe9-5492-4ced-b0fb-b2b1814656e8 [P1][Follow-up][Pixel] Mobile modal small-viewport Verify (F12)
- stage: DONE
- next: await next assignment
- checkpoint: F12 = Testdrift (falsche testid), kein Produktfehler. Reproduziert und klar eingeordnet. Test in mobile-operative-gates.spec.ts gefixt.
- blocker: -
- updated: 2026-04-15T23:42:50.832Z
<!-- mc:auto-working-context:end -->
