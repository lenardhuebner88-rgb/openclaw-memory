---
title: Mission Control Pipeline Live Execution UI Receipt
type: deployment-report
status: done
date: 2026-05-04
tags: [type/deployment-report, status/done, project/mission-control, topic/pipeline, topic/operator-ui, agent/codex]
---

# Mission Control Pipeline Live Execution UI Receipt

## Ergebnis

Die `/kanban` Task-Pipeline wurde live produktiv erweitert, damit Operatoren direkt sehen:

- was eine Task gerade macht,
- wie weit sie ist,
- ob sie stuck oder at-risk ist,
- welcher Worker/Heartbeat/Timeout beteiligt ist,
- was als nächstes getan werden soll.

Hauptbericht:

- [[06-Operations/Audits/mission-control-live-pipeline-audit-2026-05-04]]

## Geänderte Dateien

- `/home/piet/.openclaw/workspace/mission-control/src/lib/task-pipeline-payload.ts`
- `/home/piet/.openclaw/workspace/mission-control/src/app/kanban/components/TaskPipelineCard.tsx`
- `/home/piet/.openclaw/workspace/mission-control/src/app/kanban/PipelineClient.tsx`

## Verification

- `npm run typecheck`: OK
- `FORCE_BUILD=1 FORCE_CLEAN_BUILD=1 npm run -s build`: OK
- `systemctl --user start mission-control`: OK
- `/api/health`: HTTP 200
- `/api/pipeline/tasks?window=24h`: neue Felder live
- Browser `/kanban`: neue Kacheln/Karten/Drawer sichtbar

Live Snapshot nach Deployment:

- `needsOperator = 7`
- `stuck = 7`
- `atRisk = 0`
- `incident = 7`
- `draft = 2`

## Evidence

- ![[00-Inbox/_attachments/mission-control-pipeline-after-2026-05-04.png]]
- ![[00-Inbox/_attachments/mission-control-pipeline-drawer-2026-05-04.png]]

## Recovery

Backup vor Änderung:

- `/home/piet/.openclaw/backups/codex-pipeline-20260504-214100`

Rollback:

1. Die drei geänderten Dateien aus dem Backup zurückkopieren.
2. `npm run typecheck`
3. Sauber bauen und Mission Control kontrolliert starten.

## Rest-Risiken

- Root-Dateisystem war beim Audit bei 93% Nutzung.
- Der erste Safe-Restart-Lauf wurde durch das lokale Ausführungsfenster getrennt; ein anschließender Force-Clean-Build hat die fehlenden Next-Artefakte sauber wiederhergestellt.
- Empfohlen: Build-Artefakt-Gate und Disk-Cleanup als eigener Follow-up.
