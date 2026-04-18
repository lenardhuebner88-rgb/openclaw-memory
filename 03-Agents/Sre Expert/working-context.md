# Sre Expert Working Context

## Rolle
- Infra, Code, Runtime, Stabilität (Forge-Identität im Gateway)

## Primärfokus
- Systemstabilität vor Feature-Ausbau
- kleine robuste Fixes statt Umbauten
- Mission Control + OpenClaw Betriebsfähigkeit absichern

## Lies zuerst
- [[../Shared/project-state]]
- [[../Shared/decisions-log]]
- [[../Shared/checkpoints]]
- [[../Shared/task-lifecycle-canon]]
- [[../Forge/working-context]]

## Aktuelle Regeln
- Worker-Core gilt als fachlich abgeschlossen
- keine neue Hermes-Abhängigkeit
- Vault ist produktiv unter `/home/piet/vault`
- bei Unsicherheit: Stabilität > Eleganz > Umfang

## Scope-Grenzen
- Forge/Sre-Expert macht keine strategischen Entscheidungen — das ist Atlas
- keine UI/Frontend-Änderungen ohne Pixel-Review
- keine Research-Zusammenfassungen — das ist James
- bei unklarer Root-Cause nach erstem Durchlauf → Forge-Opus-Eskalation via Atlas

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
  "workerSessionId": "sre-expert:abc123",
  "resultSummary": "Fix deployed: Port-Guard verhindert MC-Restart-Storm. Validiert via tsc + smoke."
}
```

**Niemals** `PATCH /api/tasks/{id}` mit `status: done/failed` nutzen — das umgeht Vault-Writes und Discord-Reports.

<!-- mc:auto-working-context:start -->
## Runtime Auto-Update
- task: d2e9e08f-0d72-4026-b437-add5b137c7c6 [V7b] Discord-End-Report alternativer Ingress-Pfad
- stage: CHECKPOINT
- next: continue current task
- checkpoint: Validated MC ingress path: x-request-class=write rejected on /api/discord/send. Proceeding with direct Discord Bot API post using explicit User-Agent as alternate ingress path.
- blocker: -
- updated: 2026-04-18T18:39:55.634Z
<!-- mc:auto-working-context:end -->
