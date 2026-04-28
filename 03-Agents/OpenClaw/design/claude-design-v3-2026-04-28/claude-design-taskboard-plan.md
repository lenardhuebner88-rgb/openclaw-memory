---
date: 2026-04-28
type: design-handoff-plan
status: ready-for-claude-design
owner: codex-desktop
scope: planning-only
code_changes: none
live_status: SAFE_TO_PLAN
implementation_status: WAIT_FOR_WORKER_BEFORE_CODE
---

# Claude Design Taskboard Plan

## 1. Live-Einordnung

Status: SAFE_TO_PLAN fuer Research, Briefing und Vault-Dokumentation.

Wichtig: Terminal-Codex arbeitet parallel weiter und fuehrt Build/Restart/Deploy-Gates aus. Deshalb ist jede spaetere Code-Implementierung WAIT_FOR_WORKER, bis Terminal-Codex seine aktive Gate-Arbeit beendet hat und die geaenderten Dateien sauber geklaert sind.

Aktiver UI-Task zur Beobachtungszeit:
- MC-T03 Alerts / frontend-guru / Pixel war zuletzt done/result und Terminal-Codex fuehrte danach ein echtes Deploy-Gate aus.
- Keine aktive Taskboard/Kanban-Implementierung gefunden.
- Kein Edit an Taskboard/Kanban-Dateien durch Codex Desktop.

Aktuell tabu fuer Codex Desktop:
- Alle Mission-Control-Codeaenderungen.
- Alle Build/Restart/Deploy-Aktionen.
- data/tasks.json und Board-Daten.
- Dateien, die Terminal-Codex/Pixel zuletzt angefasst haben:
  - /home/piet/.openclaw/workspace/mission-control/src/app/dashboard/page.tsx
  - /home/piet/.openclaw/workspace/mission-control/src/app/layout.tsx
  - /home/piet/.openclaw/workspace/mission-control/src/components/overview-dashboard.tsx
  - /home/piet/.openclaw/workspace/mission-control/src/components/alerts/alerts-client.tsx
  - /home/piet/.openclaw/workspace/mission-control/src/components/alerts/alert-group.tsx
  - /home/piet/.openclaw/workspace/mission-control/src/app/api/alerts/route.ts
  - /home/piet/.openclaw/workspace/mission-control/src/app/api/models/health/route.ts
  - /home/piet/.openclaw/workspace/mission-control/src/app/api/tasks/route.ts
  - /home/piet/.openclaw/workspace/mission-control/src/app/api/tasks/[id]/receipt/route.ts
  - /home/piet/.openclaw/workspace/mission-control/src/lib/fallback-check.ts
  - data/board-events.json, data/board-events.jsonl, data/tasks.json, data/worker-runs.json, data/locks/

Relevante Taskboard/Kanban UI-Dateien:
- src/app/taskboard/page.tsx
- src/app/taskboard/layout.tsx
- src/app/taskboard/loading.tsx
- src/components/taskboard/taskboard-client.tsx
- src/components/taskboard/task-card.tsx
- src/components/taskboard/task-detail-modal.tsx
- src/components/taskboard/agent-load-panel.tsx
- src/components/taskboard/MorningStatusHero.tsx
- src/components/taskboard/system-pulse.tsx
- src/components/taskboard/activity-feed.tsx
- src/components/board-filters.tsx
- src/app/kanban/page.tsx
- src/app/kanban/PipelineClient.tsx
- src/app/kanban/components/TaskPipelineCard.tsx
- src/app/kanban/components/StageStepper.tsx
- src/app/kanban/components/NextUpPreview.tsx
- src/app/kanban/components/ViewToggle.tsx
- src/app/kanban/components/WaitingReasonBadge.tsx

Relevante Taskboard/Kanban Daten-/Logik-Dateien:
- src/lib/task-board-lane.ts
- src/lib/taskboard-control-view.ts
- src/lib/taskboard-data.ts
- src/lib/taskboard-intelligence.ts
- src/lib/taskboard-now-view.ts
- src/lib/taskboard-projection.ts
- src/lib/taskboard-types.ts
- src/lib/task-status-presentation.ts
- src/lib/task-operator-state.ts
- src/lib/task-runtime-truth.ts
- src/lib/task-dispatch.ts
- src/lib/task-dispatch-gate.ts
- src/lib/task-drilldown.ts
- src/lib/projections/task-lane.ts

Vorhandene Vault-/Sprint-/Design-Artefakte:
- /home/piet/vault/04-Sprints/planned/2026-04-27_mc-ui-audit-claude-design-prep.md
- /home/piet/vault/07-Research/design-handoffs/2026-04-20-taskboard/design-canvas.jsx
- /home/piet/vault/07-Research/design-handoffs/2026-04-20-taskboard/Taskboard v2 - Mobile Redesign.html
- /home/piet/vault/02-Docs/Design-Packs/claude-design-packs/mc-design-pack-taskboard-2026-04-20-0742.zip
- /home/piet/vault/_agents/codex/plans/2026-04-24_mc-board-pipeline-ui-live-test-sprint.md

Aktuelle Screenshots/UI-Beschreibungen:
- In-app Browser Zugriff funktioniert wieder; Taskboard und Task-Detailpanel wurden visuell geprueft.
- Lokale Screenshots im Desktop-Workspace:
  - C:\Users\Lenar\OneDrive\Dokumente\New project\mission-control-taskboard.png
  - C:\Users\Lenar\OneDrive\Dokumente\New project\mission-control-taskboard-full.png
  - C:\Users\Lenar\OneDrive\Dokumente\New project\mission-control-dashboard.png
- Wichtigste visuelle Beobachtung: Mobile Taskboard und Detaildrawer sind funktional, aber zu schwergewichtig. Der Summary-Block dominiert, wichtige Operator-Entscheidungen werden durch Rohtext, Chips und Sticky-Aktionen konkurrierend praesentiert.

## 2. Claude Design Research Summary

Quellen:
- Claude Design Tutorial: https://claude.com/resources/tutorials/using-claude-design-for-prototypes-and-ux
- Claude Artifacts Tutorial: https://claude.com/resources/tutorials/prototype-ai-powered-apps-with-claude-artifacts
- Claude Artifacts Help: https://support.claude.com/en/articles/9487310-what-are-artifacts-and-how-do-i-use-them
- Claude Prompting Best Practices: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
- Anthropic Artifacts Announcement: https://claude.com/blog/artifacts

Best Practices fuer Claude Design in unserem Fall:
- Einen klaren, begrenzten Produktbereich waehlen: Taskboard + Kanban + Detaildrawer, nicht ganz Mission Control.
- Screenshot plus kurze Produktbeschreibung geben.
- Reale, aber reduzierte Taskdaten geben: 6-8 Beispiel-Tasks reichen.
- Claude Design soll interaktive Prototypen/Varianten erzeugen, nicht Produktionscode.
- Drei Varianten sind genug fuer Design Review.
- Edge States explizit abfragen: loading, empty, stale, blocked, review, failed, active worker, long summary, mobile overflow.
- Handoff immer mit Komponentenstruktur, Designentscheidungen und Akzeptanzkriterien verlangen.
- Wenn Codebase-Kontext genutzt wird, nur relevante Ordner/Komponenten attachen, nicht komplette Repo, .git oder node_modules.
- Designentscheidungen in der Chat-Historie dokumentieren, weil diese in Claude-Code-Handoffs wertvoll sind.

Do:
- Screenshot vom aktuellen Taskboard und Task-Detaildrawer hochladen.
- Kurz erklaeren, dass Mission Control ein Operator-Cockpit fuer autonome Agents ist.
- Zielzustand, Lanes und Task-Card-Daten exakt definieren.
- Reduzierte JSON-Beispiele fuer Tasks mit echten Feldnamen geben.
- Nicht-Ziele explizit setzen: kein Marketing-SaaS-Look, keine dekorativen Hero-Sektionen, keine falschen Gruen-Zustaende.
- Claude nach 3 Varianten + Empfehlung + Handoff-Spec fragen.
- Nach einer Variante nur Noise reduzieren und Scanbarkeit schaerfen.

Don't:
- Keine komplette Codebase hochladen.
- Keine langen Logs, Board-Events oder Session-JSONLs in Claude Design kippen.
- Keine Secrets, Dispatch Tokens in voller Laenge, private Serverdetails oder echte Sessiondateien hochladen.
- Keine unklaren Ziele wie "mach es moderner".
- Keine Endlos-Iteration: maximal 2 Design-Runden, dann Codex/Frontend-Guru.
- Nicht verlangen, dass Claude Design Produktionslogik, API-Routen oder Task-Lifecycle-Semantik neu erfindet.

Token sparen:
- Ein Screenshot + ein Brief + 6-8 Beispiel-Tasks.
- Nur Feldnamen, die fuer UI-Entscheidungen relevant sind.
- Lange Beschreibungen auf 1-2 Zeilen kuerzen.
- WorkerSessionId/DispatchToken nur als gekuerzte Beispiele oder Platzhalter.
- Bestehende Komponenten nur als Namen nennen, nicht ganzen Code einfuegen.
- In Iteration 2 nur Delta-Anweisungen geben, keine Wiederholung des ganzen Briefs.

## 3. Produktziel Taskboard/Kanban

Ziel: Ein schlankes Operator-Control-Board, das Atlas und Menschen in unter 10 Sekunden beantwortet:
1. Was braucht jetzt Aufmerksamkeit?
2. Welcher Agent arbeitet woran?
3. Was ist stale, blocked oder review-ready?
4. Welche Aufgabe kann sicher dispatched, reviewed oder geschlossen werden?
5. Welche Details brauche ich nur bei Drilldown?

Taskboard soll:
- Schlanker und schneller erfassbar werden.
- Weniger technische Details direkt auf Cards zeigen.
- Kanban-Lanes klar und robust anzeigen.
- Worker- und Blocker-Zustaende sofort sichtbar machen.
- Atlas-Steuerung und Follow-up-Tasks unterstuetzen.
- Review/Blocked/Stale deutlich, aber ruhig hervorheben.
- Keine falschen Zustaende suggerieren.

Ziel-Lanes:
- Draft
- Ready / Waiting
- Assigned
- Active
- Review Needed
- Done
- Failed / Blocked

Task Card High-Signal only:
- Titel
- Agent/Worker
- Status/Lane
- Priority/Risk
- Age/Staleness
- Receipt Stage
- eine kurze Blocker- oder Result-Zeile

Details Drawer/Modal enthaelt:
- Lifecycle t0-t3
- Receipt Chain
- Dispatch Token gekuerzt
- Worker Session gekuerzt
- Acceptance Criteria
- Events
- Logs/History
- Parent/Follow-up Beziehung
- Raw Metadata optional collapsed

## 4. Empfohlener Claude-Design-Workflow

Iteration 1: Exploration
- Input: Screenshot vom aktuellen Taskboard + Detaildrawer, Brief, 6-8 Beispiel-Tasks.
- Output: 3 Varianten.
- Varianten-Vorschlag:
  1. Dense Operator Board: Tabelle/Kanban-Hybrid, schnelle Scans.
  2. Command Queue: Fokus auf Next Best Action und aktive Worker.
  3. Split Drilldown: Kanban links, Details rechts, Mobile bottom drawer.

Iteration 2: Auswahl schaerfen
- Eine Variante waehlen.
- Claude Design soll Noise reduzieren, Scanbarkeit verbessern, Mobile-First pruefen.
- Output: finale Komponentenstruktur + Edge States + Handoff-Spec.

Iteration 3 optional: Handoff finalisieren
- Nur wenn Variante noch unklar ist.
- Keine visuelle Polishing-Schleife.

Regel: Nach maximal 2 Design-Iterationen uebernimmt Codex/Frontend-Guru.

## 5. Handoff-Prinzip fuer Codex/Frontend-Guru

Claude Design liefert kein direktes Produktionsmandat. Handoff muss uebersetzen in:
- Komponenten-Slices
- betroffene Dateien
- Risiko
- Akzeptanzkriterien
- Stop Conditions
- Visual Validation per Browser/Screenshot

Implementierung erst starten, wenn Terminal-Codex nicht mehr dieselben UI-/Build-Flaechen besitzt.
