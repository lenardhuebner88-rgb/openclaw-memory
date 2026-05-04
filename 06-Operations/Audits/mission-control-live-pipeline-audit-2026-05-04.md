---
title: Mission Control Live Pipeline Audit & UI Deployment 2026-05-04
type: audit-report
status: done
date: 2026-05-04
tags: [type/audit-report, status/done, project/mission-control, topic/pipeline, topic/operator-ui, topic/live-data, agent/codex]
---

# Mission Control Live Pipeline Audit & UI Deployment 2026-05-04

## Executive Summary

Am 2026-05-04 wurde das Mission-Control-Board live gegen Browser, API und Homeserver-Zustand geprüft. Der zentrale Befund war: Warnsignale existierten in den Daten, waren im operativen Board aber zu indirekt. Besonders die Pipeline machte nicht sofort sichtbar, ob eine Task gerade wirklich arbeitet, wie weit sie ist, ob sie stuck ist und welche Operator-Aktion als nächstes sinnvoll ist.

Daraufhin wurde die bestehende `/kanban` Task-Pipeline erweitert. Die Pipeline zeigt jetzt pro Task:

- Health: `fresh`, `waiting`, `at-risk`, `stuck`, `terminal`
- Fortschritt: `progressLabel`, Prozent/Stage-Balken und Grundsignal
- Laufzeit: Heartbeat-Alter, Timeout-Restzeit oder Timeout-Überzug
- Ownership: Agent, Worker-Label und Worker-Session
- Operator-Aktion: konkrete `Next action`

Nach Umsetzung, Typecheck, sauberem Produktionsbuild, Restart und Browserprüfung ist Mission Control wieder aktiv und liefert die neuen Felder live aus.

## Scope

- Target: Mission Control auf `http://192.168.178.61:3000`
- Hauptfläche: `/kanban` Pipeline
- Kontextflächen: `/taskboard`, `/alerts`, `/monitoring`, `/costs`, Board-/Ops-APIs
- Server: `piet@192.168.178.61`
- Codepfad: `/home/piet/.openclaw/workspace/mission-control`
- Vault-Root: `/home/piet/vault`

## Vorherige Live-Audit-Befunde

Die ursprüngliche Live-Prüfung zeigte mehrere Daten-/UI-Spannungen:

- Dashboard/Taskboard wirkten zu ruhig, während Alerts, Monitoring, Costs und Worker-Proofs rote Signale zeigten.
- Alerts: mehrere hundert aktive historische/operative Signale, darunter critical/high.
- Monitoring: rote System-/Runtime-Signale sichtbar, aber nicht im Mission-Control-Primärpfad priorisiert.
- Costs: Anomalie-/Budget-Signale vorhanden, aber nicht als unmittelbare Operator-Handlung in der Pipeline sichtbar.
- Worker-/Lifecycle-Proofs: einzelne Stuck-/Timeout-/Claim-/Receipt-Probleme mussten über Detailseiten oder API interpretiert werden.

Operator-Anforderung aus dem Live-Review:

- Warnsignale müssen direkt sichtbar sein.
- Pipeline muss zeigen, was eine Task gerade macht.
- Pipeline muss zeigen, wo die Task steht und wie viel bis zum Ergebnis fehlt.
- Stuck-Zustände müssen sofort auffallen.
- Mission Control soll aus der Pipeline heraus Handlungen ermöglichen.

## Implementierte Änderungen

### Datenmodell

Datei:

- `/home/piet/.openclaw/workspace/mission-control/src/lib/task-pipeline-payload.ts`

Neu im Task-Pipeline-Payload:

- `healthState`
- `healthReason`
- `nextAction`
- `progressPercent`
- `progressLabel`
- `heartbeatAgeMs`
- `heartbeatFresh`
- `timeoutRemainingMs`
- `workerLabel`
- `workerSessionId`
- `lastHeartbeatAt`

Neue Stats:

- `atRisk`
- `stuck`
- `needsOperator`

Ableitung:

- `progressPercent` wird bevorzugt, sonst Receipt-Stage-Heuristik.
- `pending-pickup` wird als sichtbares Warten auf Worker-Pickup angezeigt.
- `stuck` entsteht u.a. bei failed/blocked/stalled, abgelaufenem Timeout, überfälligem Pickup oder stale Heartbeat.
- `at-risk` entsteht u.a. bei altem Heartbeat, langer Progress-Pause oder nahem Timeout.
- `nextAction` wird aus Status, Operator-Lock, Review, Blocker, Failed und Timeout abgeleitet.

### Task-Karten

Datei:

- `/home/piet/.openclaw/workspace/mission-control/src/app/kanban/components/TaskPipelineCard.tsx`

Neu sichtbar:

- Health-Chip: `Stuck`, `At risk`, `Waiting`, `Fresh`, `Terminal`
- Progress-Box mit Fortschrittslabel und Health-Grund
- Laufzeit-Kacheln: `Heartbeat`, `Timeout`, `Worker`
- Footer mit `Next action`
- Stuck/Incident-Karten haben deutlich rote Priorisierung.

### Pipeline-Übersicht und Drawer

Datei:

- `/home/piet/.openclaw/workspace/mission-control/src/app/kanban/PipelineClient.tsx`

Neu sichtbar:

- Top-Kacheln: `Needs operator`, `Stuck`, `At risk`, `Review`, `Incident`
- Filter: `stuck`, `at-risk`
- Quick-Jump-Text: Working/Stuck/At-risk statt nur Working/Review/Dispatched
- Drawer erweitert um `Live execution`, Progress, Health-Grund, Heartbeat, Timeout, Worker, Session und Operator Action.

## Live Verification

### Typecheck

Ergebnis:

- `npm run typecheck`: OK

### Produktionsbuild

Ergebnis:

- `FORCE_BUILD=1 FORCE_CLEAN_BUILD=1 npm run -s build`: OK
- Next.js 15.5.15 compiled successfully.
- `/kanban`: 14.3 kB route, 175 kB first load.

Hinweis:

- Der erste Safe-Restart-Lauf wurde durch das lokale SSH-Zeitfenster getrennt, während der Build noch lief.
- Danach fehlte kurzzeitig `.next/prerender-manifest.json`, wodurch Mission Control nicht starten konnte.
- Das wurde durch einen sauberen Force-Clean-Produktionsbuild behoben.
- Danach wurde `mission-control` erfolgreich gestartet und `/api/health` antwortete wieder mit HTTP 200.

### Live API

Endpoint:

- `GET http://127.0.0.1:3000/api/pipeline/tasks?window=24h`

Bestätigte neue Felder:

- `healthState`
- `progressLabel`
- `nextAction`
- `heartbeatAgeMs`
- `timeoutRemainingMs`
- `atRisk`
- `stuck`
- `needsOperator`

Aktueller Snapshot nach Deployment:

- `draft = 2`
- `dispatched = 0`
- `working = 0`
- `review = 0`
- `incident = 7`
- `atRisk = 0`
- `stuck = 7`
- `needsOperator = 7`

### Browser Verification

Headless Browser gegen echte Produktionsseite:

- URL: `http://127.0.0.1:3000/kanban`
- Titel: `Mission Control`
- Sichtbare DOM-Prüfung:
  - `Needs operator`: vorhanden
  - `Stuck`: vorhanden
  - `At risk`: vorhanden
  - `Progress`: vorhanden
  - `Next action:`: vorhanden
  - `Heartbeat`: vorhanden
  - `Timeout`: vorhanden
  - `Worker`: vorhanden
- Drawer-Prüfung:
  - `Live execution`: vorhanden
  - `Operator action`: vorhanden
  - `Heartbeat`: vorhanden
  - `Timeout`: vorhanden
  - `Session`: vorhanden
  - `Retry, inspect failure`: vorhanden

Screenshots:

- ![[00-Inbox/_attachments/mission-control-pipeline-after-2026-05-04.png]]
- ![[00-Inbox/_attachments/mission-control-pipeline-drawer-2026-05-04.png]]

## Operational Result

Die Pipeline ist jetzt operator-first:

- Rot heißt nicht mehr nur "irgendwo Incident", sondern zeigt in der Task-Karte den Grund.
- Jede sichtbare Task sagt, ob sie wartet, festhängt oder nur beobachtet werden muss.
- Der nächste sinnvolle Operator-Schritt steht direkt auf der Karte.
- Der Drawer erlaubt Handlung im Kontext, ohne aus der Pipeline herauszuspringen.

Beispiel aus Live-Daten:

- Failed/Timeout-Tasks zeigen `Stuck`, `Stopped before completion`, Heartbeat-Alter, Timeout-Überzug und `Next action: Retry, inspect failure, or admin-close.`
- Draft-Tasks zeigen `Waiting`, `Not dispatched yet`, `No timeout`, `No worker yet` und `Next action: Dispatch when ready.`
- Operator-Lock wird als nächste Handlung sichtbar: Lock lösen, wenn Arbeit weiterlaufen darf.

## Backups und Recovery

Vor dem Rückspielen der drei betroffenen Dateien wurde ein Server-Backup angelegt:

- `/home/piet/.openclaw/backups/codex-pipeline-20260504-214100`

Betroffene Dateien:

- `src/lib/task-pipeline-payload.ts`
- `src/app/kanban/components/TaskPipelineCard.tsx`
- `src/app/kanban/PipelineClient.tsx`

Recovery-Hinweis:

1. Falls Rollback nötig ist, die drei Dateien aus dem Backup zurückkopieren.
2. Danach `npm run typecheck`.
3. Dann sauberer Produktionsbuild und kontrollierter Restart.

## Risiken und Follow-ups

### Disk Pressure

Beim Audit war `/` zu 93% belegt, nur ca. 7.3G frei.

Risiko:

- Next-Produktionsbuilds sind empfindlich gegenüber unvollständigen Artefakten, wenn wenig Platz oder unterbrochene Builds auftreten.

Empfehlung:

- Separater Cleanup-Sprint für alte `.next-*`, temporäre Audit-Artefakte, Logs und Build-Backups.
- Build-Safe-Gate sollte nach Build zusätzlich prüfen, dass `BUILD_ID`, `prerender-manifest.json`, `required-server-files.json` und die wichtigsten route artifacts existieren.

### Safe-Restart Timeout

Der vorhandene `mc-restart-safe --refresh-build` ist grundsätzlich richtig, aber der Build dauerte länger als das lokale Ausführungsfenster.

Empfehlung:

- Timeout für Build-Refresh-Jobs erhöhen oder Build-Refresh in zwei Phasen führen:
  - Stop
  - Force-Clean-Build mit Artefakt-Gate
  - Start
  - Health/API/Browser-Proof

### Pipeline-Semantik

Die neue Health-Ableitung ist bewusst konservativ.

Nächste Verbesserung:

- Worker-Proof-API und Pipeline-Payload stärker zusammenführen, damit `at-risk` auch Fälle erkennt, bei denen Worker-Runs offen sind, aber Tasks noch nicht eindeutig stale markiert wurden.
- In `taskboard` V3 dieselbe Operator-Health-Sprache spiegeln, damit Pipeline und Taskboard dieselben roten Begriffe verwenden.

## Related Links

- [[03-Agents/Codex/receipts/2026-05-04_mission-control-pipeline-live-execution-ui]]
- [[03-Projects/plans/pipeline-tab-quickwins-plan-2026-04-21]]
- [[03-Agents/OpenClaw/task-lifecycle]]
- [[03-Agents/OpenClaw/operational-state]]
- [[06-Operations/Audits/system-audit-playbook]]

## Final Verdict

GREEN for deployment and live verification.

YELLOW for surrounding operational risk because disk pressure remains high and the safe restart path exposed a missing-artifact failure mode when the build window was interrupted.
