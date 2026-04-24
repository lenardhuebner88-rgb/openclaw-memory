---
status: active
owner: codex
started: 2026-04-24T20:55:00Z
scope:
  - /home/piet/.openclaw/workspace/mission-control/src/lib/pipeline-data.ts
  - /home/piet/.openclaw/workspace/mission-control/src/app/kanban/PipelineClient.tsx
  - /home/piet/.openclaw/workspace/mission-control/src/app/taskboard/page.tsx
  - /home/piet/.openclaw/workspace/mission-control/tests/
---

# MC Board + Pipeline UI Live-Test Sprint

## Ziel
Während des laufenden Autonomy-Monitorings einen kleinen, reversiblen UI-Stabilitäts-Sprint einschieben:

1. Pipeline-API gegen große Session-Dateien härten.
2. Pipeline-Tab eine höhere Übersichtsebene geben, bevor Raw-Details geöffnet werden.
3. Taskboard-Header robuster machen, damit "last updated" nicht von unsortierter Task-Reihenfolge abhängt.

## Quality Gates
- [x] Targeted Vitest: Pipeline + Taskboard Payload.
- [x] `npm run typecheck`.
- [x] Production Build.
- [x] Kontrollierter MC-Restart.
- [x] Live-Probes: `/api/pipeline`, `/kanban`, `/api/board/snapshot?view=live`, `/api/health`.
- [x] Discord Abschlussbericht in `1495737862522405088`.

## Log
- 2026-04-24T20:55Z: Sprint aufgenommen. Live-Monitoring bleibt parallel aktiv.
- 2026-04-24T20:57Z: Pipeline-Sessiontail begrenzt, Pipeline-Summary ergänzt, Taskboard-LastUpdated auf neuesten Timestamp umgestellt.
- 2026-04-24T20:57Z: Targeted Vitest grün: `pipeline-tab-phase1-truth`, `pipeline-agent-attention-ssot`, `pipeline-events-sse-route`, `taskboard-compact-payload`.
- 2026-04-24T20:57Z: `npm run typecheck` grün.
- 2026-04-24T21:01Z: Production Build grün, `mc-restart-safe` erfolgreich.
- 2026-04-24T21:02Z: Live-Probes grün: `/api/health` ok, `/api/pipeline` summary `agentCount=6 eventCount=32 activeToolCount=6 sessionTailBytes=131072`, `/kanban` 200, Board-Snapshot 200/1023 bytes, Service active.
- 2026-04-24T21:03Z: Discord-Bericht gesendet: `1497342027195748352`.
