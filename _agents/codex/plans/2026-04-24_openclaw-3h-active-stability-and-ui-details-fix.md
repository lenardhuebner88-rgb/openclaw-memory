# OpenClaw 3h Active Stability + Task Details Fix

Datum: 2026-04-24
Owner: Codex
Scope: Mission Control live stabilisieren, kontrollierte Mini-Last, clientseitige Task-Details-Exception fixen.

## Arbeitsmodus
- Aktiv statt passiv: Root Cause identifizieren und kleine Fixes umsetzen, wenn Live-Gates kippen.
- Kleine Worker-Tasks einzeln, nie parallel fluten.
- Keine breiten Rewrites, keine QMD-Architekturänderung, keine Provider-/Routing-Mutation.
- Mutationen nur gezielt und belegbar; lokale Scripts bleiben Dry-run default.

## Priorität 0
- Client-side Exception beim Task-Details-Klick reproduzieren, Root Cause isolieren, Fix testen und deployen.

## Danach 3h Ablauf
- Alle 5 Minuten: Health, Runtime-Soak, Pickup-Proof, Worker-Proof, Health-Reconciliation, Service-Status.
- Nach grünen Gates: kleine real-use Worker-Tasks einzeln starten.
- Nach jedem Task: Pickup/Worker/Health prüfen.
- Bei Rot: keine weiteren Tasks, Root Cause sammeln/fixen, erst dann weiter.

## Stop-Regeln
- `/api/health` degraded durch neue Recovery-Last.
- `pickup-proof.criticalFindings > 0`.
- `worker-reconciler-proof.openRuns > 0` bleibt nach Taskende hängen.
- neuer Claim-Timeout.
- Mission Control oder Gateway nicht active.
- Session-/Output-Guard kritische neue Aktivsignale.

## Statuslog
- 2026-04-24T09:51:15Z gestartet; UI-Details-Exception ist erster Root-Cause/Fix-Fokus.
- 2026-04-24T09:53:48Z Root Cause reproduziert: Task-Details-Klick erzeugte React Error #310. Ursache: `useSwipe()` wurde in `TaskDetailModal` nach `if (!open) return null` aufgerufen, wodurch sich beim Öffnen die Hook-Anzahl änderte. Fix: Hook vor den Early-Return verschoben. Regressionstest `tests/task-detail-modal-hook-order.test.ts` passed; `npm run typecheck` passed. Ein älterer Mobile-Layout-Source-Test fällt separat auf eine bestehende `href`-Erwartung für Lane-Jump-Buttons.
- 2026-04-24T10:00:35Z Zweiter Root Cause aus Browser-Probe: Taskboard-SSE replayte ohne Cursor alle historischen Board-Events und triggert dadurch Snapshot-Sturm. Fix: neuer Cursor-Resolver startet ohne expliziten Cursor am aktuellen Event-Tail; Reconnect-Cursor replayt weiterhin. Tests `tests/task-detail-modal-hook-order.test.ts tests/board-events-sse-cursor.test.ts` passed; `npm run typecheck` passed.
- 2026-04-24T10:06:52Z Deployed und live verifiziert: Build passed, `mission-control.service` und `openclaw-gateway.service` active. Browser-Flow `Taskboard -> Details` öffnet Modal ohne React PageError (`pageerror=0`) und ohne Snapshot-Fail-Sturm (`snapshotFailed=0`, `refreshWarnings=0`). Health/Pickup/Worker/Health-Reconciliation ok. Runtime-Soak blockiert aktuell nur durch Context active critical bei James Output-Caps (`context-active-critical-clear`).
