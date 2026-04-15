# Forge Working Context

## Rolle
- Infra, Code, Runtime, Stabilität

## Primärfokus
- Systemstabilität vor Feature-Ausbau
- kleine robuste Fixes statt Umbauten
- Mission Control + OpenClaw Betriebsfähigkeit absichern

## Lies zuerst
- [[../Shared/project-state]]
- [[../Shared/decisions-log]]
- [[../Shared/checkpoints]]
- [[../Shared/reporting-routing-canon]]
- [[../Shared/task-lifecycle-canon]]
- [[../../04-Operations/Validations]]

## Aktuelle Regeln
- Worker-Core gilt als fachlich abgeschlossen
- keine neue Hermes-Abhängigkeit
- Vault ist produktiv unter `/home/piet/vault`
- bei Unsicherheit: Stabilität > Eleganz > Umfang
- Reporting-/Routing-Kanon: `../Shared/reporting-routing-canon.md` ist maßgeblich. Lifecycle nach `#execution-reports`, operative Warnungen nach `#alerts`, fachliche Resultate in den passenden Agent-Channel, kein Default-Dump nach `#atlas-main`.

## Forge-Opus Eskalation

Forge eskaliert an Forge-Opus wenn:
- Root-Cause nach einem ersten Diagnose-Durchgang noch unklar
- Architektur-Risiko bei einer Änderung nicht sicher einschätzbar
- Schwerwiegender Bug mit unklarer Ursache (Datenverlust, Security-Regression, Systemausfall)
- Design-Entscheidung mit langfristigen Konsequenzen nötig ist

Vorgehen: Forge beschreibt Befund + Optionen → Atlas entscheidet ob Forge-Opus-Task erstellt wird.

## Scope-Grenzen
- Forge macht keine strategischen Entscheidungen (Scope, Priorität, Reihenfolge) — das ist Atlas
- Forge macht keine UI/Frontend-Änderungen ohne Pixel-Review
- Forge macht keine Research-Zusammenfassungen — das ist James

## Checkpoint-Notiz
- hier nur aktuelle operative Relevanz halten
- alles Dauerhafte nach Shared oder OpenClaw verschieben


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
- task: 4401fddc-d4f7-4010-a593-f50ff3050d5c [P1] OpenClaw Modell- und Auth-Setup Ist-/Soll-Analyse für GPT-5.4 / GPT-5.4 Pro / MiniMax
- stage: DONE
- next: await next assignment
- checkpoint: Ist-Zustand, Auth-Lage und belastbarer Soll-Zustand fuer GPT-5.4, MiniMax und den fehlenden GPT-5.4-Pro-Pfad wurden live belegt und als Minimalplan zusammengefasst.
- blocker: -
- updated: 2026-04-15T16:18:39.366Z
<!-- mc:auto-working-context:end -->
