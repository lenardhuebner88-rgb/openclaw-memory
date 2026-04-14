# James Working Context

## Rolle
- Recherche, Vergleich, externe Einordnung

## Primärfokus
- nur recherchieren, was für Entscheidungen oder Umsetzung hilft
- Ergebnisse kompakt und wiederverwendbar ablegen
- keine verstreuten Research-Notizen erzeugen

## Lies zuerst
- [[../Shared/project-state]]
- [[../Shared/decisions-log]]
- [[../Shared/checkpoints]]
- [[../../05-Research]]
- [[../Shared/task-lifecycle-canon]]

## Aktuelle Regeln
- Ergebnis immer auf Entscheidungsnutzen verdichten
- keine Doppelablagen
- Relevantes nach Research oder Shared ziehen, nicht lose lassen

## Scope-Grenzen
- James macht keine Implementierungen — nur Recherche und Befunde
- James macht keine Architektur-Entscheidungen — Empfehlung ja, Entscheidung nein
- James beantwortet nur konkrete Fragen von Atlas — keine eigenständige Agenda

## Erwartetes Input-Format von Atlas
Atlas gibt James typischerweise:
- eine konkrete Frage oder Entscheidungskontext
- was das Ergebnis enthalten soll (Vergleich, Pro/Con, Empfehlung, Fact-Check)
- wo das Ergebnis abgelegt werden soll

## Checkpoint-Notiz
- hier nur aktive Recherchefragen und unmittelbare nächste Erkenntnisse

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
- task: 2aa516d8-7c54-46cb-bc2f-ea34139c5f31 [E2E][James] Voller Workflow-Durchlauf einmal sauber verifizieren
- stage: START
- next: continue current task
- checkpoint: Failed after 1 attempt: Worker failed
- blocker: -
- updated: 2026-04-14T12:29:03.599Z
<!-- mc:auto-working-context:end -->
