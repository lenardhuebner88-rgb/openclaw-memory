---
title: Mission Control — Pipeline-Tab Live-Experience Plan (2 Sprints)
date: 2026-04-18
author: Principal Product-System Architect (Atlas pre-hand)
status: ready-for-execution
owner: Atlas → all agents (Pixel/Forge/Lens/Spark/James)
version: 1.0
trigger: "Lade 03-Agents/2026-04-18_mission-control-pipeline-tab-2-sprints.md und starte Sprint 1 Pack 1."
---

# Pipeline-Tab Live-Experience — 2-Sprint-Plan

## Mission-Satz
Der Pipeline-Tab soll **fühlen wie ein Live-Monitor auf der Brücke eines Schiffs** — der Operator sieht auf einen Blick was läuft, welcher Agent gerade an welchem Schritt sitzt, wo die Pipeline hakt, und kann direkt aus der Ansicht eingreifen. Heute ist der Tab statisch und verschlafen — morgen pulsiert er.

## Research-Synthese (externe Benchmarks)

| Quelle | Pattern | Für uns relevant |
|---|---|---|
| **Temporal Web UI** | Multi-View (Timeline / Compact / JSON / Workers / Pending Activities) — Operator switcht je nach Frage | ⭐⭐⭐ Workers-Tab als Agent-Attribution-Inspiration |
| **Temporal** | Call-Stack Query: "where am I now?" mit Worker-Response | ⭐⭐⭐ Bootstrap-Status-Probe für MCP-Phase |
| **Temporal** | Event-History chronologisch, State-Transitions-Log | ⭐⭐⭐ Audit-Trail pro Task |
| **Datadog CI Pipelines** | Execution Time / Queue Time / Approval Wait Time pro Step separiert | ⭐⭐⭐ zeigt wo Zeit verloren geht (bei uns: Queue-Wait von 75min heute!) |
| **Datadog** | Critical-Path-Highlight — längster Pfad rot | ⭐⭐ Bottleneck-Analyse (Forge-Concurrency=1 heute) |
| **Datadog** | Waterfall horizontal, Parallelismus sichtbar | ⭐⭐ DAG-Layout-Inspiration |
| **Vercel Deployments** | Filter (Branch/Status/Env) + Redeploy-Action inline | ⭐⭐ Operator-Aktionen direkt aus Liste |
| **GitHub Actions** | Step-Expansion live, Log-Stream inline | ⭐⭐ Inline-Log-Peek ohne Drawer |

**Top-3 Patterns für uns übernehmen:**
1. **Event-Stream SSE** für Live-Transitions (Temporal-Style)
2. **Execution vs Queue vs Wait-Time separiert** (Datadog-Style) — deckt unsere Dispatch-Wait-Problematik auf
3. **Worker/Agent-Attribution pro Step** (Temporal + GitHub) — Operator sieht welcher Agent auf welcher Stufe ist

## Ist-Lage (Live-Analyse Hinweise)

Bekannt aus heutiger Session:
- Kein SSE/WebSocket-Push vom MC — Board pollt
- Pipeline-Tab (falls existent) zeigt vermutlich statische Listen, keine Live-Transitions
- Step-Granularität fehlt: wir sehen nur `status` und `receiptStage` aggregiert, nicht die 7 echten Lifecycle-Phasen
- Agent-Attribution auf Task-Ebene ja, auf Step-Ebene nein
- Queue-Wait-Zeit (heute 75min für 090fdc54!) nirgends visualisiert

Diese Annahmen verifiziert Pack 1 (Ist-Analyse).

## Sprint-Übersicht

### Sprint 1 — "Live Foundation" (~4-5h)
Ziel: Event-Stream live + Base-UI. Nach Sprint 1 sieht der Operator Status-Transitions in Echtzeit.

### Sprint 2 — "Step-Visibility + Action" (~4-5h)
Ziel: Step-Level-DAG pro Task + Operator-Aktionen direkt aus View + Filter.

---

# Sprint 1 — Live Foundation

## Pack 1.0 — Ist-Analyse + Pattern-Brief (Spark + James, parallel, 45min)

### Pack 1.0a — Spark: UX-Concept
- Wireframes für Pipeline-Tab-Haupansicht mit 3 Layout-Optionen:
  - Option A "Track-and-Field": vertikale Spalten pro Stage, Task-Karten wandern horizontal
  - Option B "Waterfall-Timeline": horizontale Zeit-Achse, Tasks als Balken (Datadog-Style)
  - Option C "Live-Grid": Agent-Swimlanes, Tasks als Chips mit Pulse-Animation
- Mood-Board: Farb-Paletten für State-Farben (ready/active/blocked/review/failed/done), Motion-Philosophie
- **Deliverable**: `/home/piet/vault/03-Agents/spark-pipeline-ux-2026-04-18.md`

### Pack 1.0b — James: Pattern-Benchmark-Report
- Screenshots (oder textuelle Beschreibung) von Temporal, Dagster, Argo, GitHub-Actions Live-Run-Views
- Tabelle: welches UI-Element löst welches Operator-Problem
- 3 konkrete Referenz-Screenshots für Pixel
- **Achtung**: James-Bootstrap hat heute Timeout-Risk — Task mit 30min-Timeout und sicherem Fallback (falls timeout → Forge übernimmt Recherche textuell)
- **Deliverable**: `/home/piet/vault/03-Agents/james-pipeline-benchmark-2026-04-18.md`

## Pack 1.1 — Backend Event-Stream (Forge, 90min)

### Ziel
SSE-Endpoint `/api/pipeline/events` der Task-State-Transitions in Echtzeit pusht. Client öffnet EventSource, empfängt Events bei jedem `status`/`receiptStage`/`dispatchState`-Change.

### Scope
- Event-Bus intern (in-memory ring buffer, 1000 last events)
- SSE-Route mit auth (request-class=read ok)
- Event-Schema:
  ```json
  {
    "eventId": "uuid",
    "at": "ISO8601",
    "taskId": "...",
    "transition": {
      "field": "status" | "receiptStage" | "dispatchState",
      "from": "...",
      "to": "..."
    },
    "agent": "Atlas|Forge|...",
    "stepName": "bootstrap|dispatch|accepted|progress|result|review|archive",
    "durationMs": 42
  }
  ```
- Emit-Hooks in `/api/tasks/:id` PATCH-Handler + Dispatcher + Receipt-Ingestor
- Heartbeat-Event alle 15s wenn keine Transitions (damit Client nicht disconnected)
- Connection-Limit: max 20 gleichzeitig

### Deliverable
- `mission-control/src/app/api/pipeline/events/route.ts` — SSE-Route
- `mission-control/src/lib/pipeline-event-bus.ts` — In-Memory-Bus
- `mission-control/src/lib/pipeline-event-emit.ts` — Hook-Helper
- Unit-Tests: Ring-Buffer-Eviction, Heartbeat, Multi-Client

## Pack 1.2 — Client-Skeleton + Event-Consumer (Pixel, 90min)

### Ziel
Pipeline-Tab-Basis rendert und verbindet sich mit SSE. Auf jedes Event: UI-Update. Keine Fancy-Animations yet — nur "funktioniert und ist live".

### Scope
- Layout gemäss Sparks Empfehlung (eine der 3 Optionen, Atlas entscheidet nach Spark-Deliverable)
- `useSSE` Hook mit Reconnect, Backoff, Network-Status-Badge
- State-Management: Event-Log + abgeleiteter "live board state"
- Minimales Card-Component mit agent + stepName + timeSinceTransition
- "Live-Indikator" oben rechts: grün-pulsierend wenn SSE connected, gelb bei reconnect, rot bei failed-to-connect

### Deliverable
- `mission-control/src/app/pipeline/page.tsx`
- `mission-control/src/components/pipeline/live-indicator.tsx`
- `mission-control/src/components/pipeline/event-feed.tsx`
- `mission-control/src/hooks/use-pipeline-sse.ts`

## Pack 1.3 — Lens Streaming-Cost + Performance-Audit (Lens, 30min)

### Ziel
Sicherstellen dass SSE nicht Kosten oder Server-Load explodiert.

### Scope
- Load-Rechnung: 6 Agenten × max 5 open Connections × 15s Heartbeats = trivial
- Token/Memory-Footprint bei Ring-Buffer 1000 Events
- Empfehlung: Connection-Limit, Backpressure-Strategie
- "Streaming ist günstig" oder "Begrenze auf X" Verdikt

### Deliverable
- `/home/piet/vault/03-Agents/lens-pipeline-streaming-audit-2026-04-18.md`

## Pack 1.4 — Atlas Orchestration + Acceptance (Atlas, parallel)

### Ziel
Reihenfolge koordinieren, blockages ansprechen, Sprint-1-Accept.

### Acceptance Sprint 1
1. SSE-Endpoint `/api/pipeline/events` reachable, liefert Transitions
2. Pipeline-Tab lädt, Live-Indikator grün
3. Test-PATCH auf Task triggert sichtbares Event auf Client innerhalb <500ms
4. Reconnect nach MC-Restart innerhalb <5s
5. Spark-UX-Doc + James-Benchmark-Doc in Vault
6. Lens-Streaming-Audit grün

---

# Sprint 2 — Step-Visibility + Action

## Pack 2.1 — Step-DAG pro Task (Pixel + Spark, 2h)

### Ziel
Klickt Operator auf Task-Card → Drawer zeigt **Step-DAG** mit aktueller Position als glowing node + Event-Timeline mit Durations pro Step.

### Step-Phasen (7 canonical)
```
1. draft         → 2. assigned      → 3. pending-pickup  →
4. in-progress[bootstrap → accepted → progress → result]   →
5. review    → 6. done|canceled|failed    → 7. archived
```
Zwischen jedem Step: Delta-Zeit (Datadog-Style Queue vs. Execution vs. Wait).

### Spark-Anteil
- Animation-Spec: Pulse auf aktivem Node, Easing, Color-Transitions
- Typography + Spacing

### Pixel-Anteil
- Step-DAG-Component (SVG oder CSS-Grid)
- Drawer mit Timeline-Tab + JSON-Tab + Actions-Tab
- Deep-Link `/pipeline?task=<id>&tab=timeline`

### Deliverable
- `mission-control/src/components/pipeline/step-dag.tsx`
- `mission-control/src/components/pipeline/task-timeline.tsx`
- `mission-control/src/components/pipeline/pipeline-drawer.tsx`

## Pack 2.2 — Operator-Actions inline (Forge + Pixel, 90min)

### Ziel
Operator kann direkt aus Pipeline-Tab **Retry / Kick-Stalled / Cancel / Accept-Review** ausführen ohne Page-Navigation. Jede Action = authenticated PATCH/POST, UI optimistisch + Rollback bei Fehler.

### Scope
- 4 Action-Buttons kontextabhängig pro Card/Drawer
- Forge: Permissions-Check + Audit-Log-Event
- Pixel: Optimistic UI + Error-Toast + Keyboard-Shortcuts (r=retry, k=kick, c=cancel)

### Deliverable
- `mission-control/src/components/pipeline/task-actions.tsx`
- `mission-control/src/app/api/pipeline/actions/route.ts`

## Pack 2.3 — Filter + Agent-Swimlanes (Pixel, 60min)

### Ziel
Filter-Bar: "show only Forge" / "only stalled" / "only last 15min". Agent-Swimlane-Toggle: Switch zwischen "by-Stage" und "by-Agent" Layout.

### Scope
- URL-State-Sync für Filter (`?agent=Forge&stage=in-progress`)
- Quick-Filter-Chips
- Layout-Toggle persistiert in localStorage

### Deliverable
- `mission-control/src/components/pipeline/filter-bar.tsx`
- `mission-control/src/components/pipeline/swimlane-view.tsx`

## Pack 2.4 — James Accessibility + Keyboard (James, 45min)

### Ziel
Pipeline-Tab voll tastatur-bedienbar, Screen-Reader-tauglich.

### Scope
- Keyboard-Navigation: j/k zwischen Cards, Enter öffnet Drawer, Esc schließt, r/k/c Actions
- ARIA-Labels auf Live-Indikator, Step-DAG-Nodes, Action-Buttons
- Focus-Trap im Drawer
- Tests mit axe-core

### Deliverable
- Keyboard-Shortcut-Reference `mission-control/docs/pipeline-shortcuts.md`
- a11y-Test-Cases in Playwright

## Pack 2.5 — Lens Live-Cost-Badge (Lens, 45min)

### Ziel
Jede aktive Task-Card zeigt **Live-Cost-Badge** (USD oder Tokens, letzte 5min Delta). Operator sieht Runaway-Cost sofort.

### Scope
- Aggregator: cost delta per task over rolling window
- Badge-Component: grün/gelb/rot Thresholds
- SSE-Event `cost-update` für Live-Push

### Deliverable
- `mission-control/src/lib/projections/live-cost.ts`
- `mission-control/src/components/pipeline/cost-badge.tsx`

## Pack 2.6 — Atlas Sprint-2-Accept (Atlas, parallel)

### Acceptance Sprint 2
1. Klick auf Card → Drawer mit Step-DAG, aktiver Node glowt
2. 4 Operator-Actions funktionieren mit Audit-Log
3. Filter + Agent-Swimlane funktioniert, URL-State-Sync
4. Keyboard-Shortcuts funktional, axe-core 0 violations
5. Live-Cost-Badge zeigt Delta über 5min-Rolling-Window

---

## Agent-Zuweisung (Übersicht)

| Agent | Sprint 1 | Sprint 2 | Gesamt |
|---|---|---|---|
| **Atlas** | 1.4 Orchestration | 2.6 Accept | ~1h |
| **Forge** | 1.1 SSE Backend | 2.2 Actions + 2.5 Cost-Projection | ~3.5h |
| **Pixel** | 1.2 UI Skeleton | 2.1 DAG + 2.2 UI + 2.3 Filter | ~5h |
| **Spark** | 1.0a UX-Concept | 2.1 Animation-Spec | ~1.5h |
| **Lens** | 1.3 Streaming-Audit | 2.5 Live-Cost | ~1h |
| **James** | 1.0b Benchmark | 2.4 A11y + Keyboard | ~1h |

Total Agent-Time ~13h (über 2 Sprints), Wall-Clock ~8-10h bei paralleler Ausführung.

## Reihenfolge

**Sprint 1:**
1. Parallel: Pack 1.0a (Spark) + 1.0b (James) + 1.3 (Lens)
2. Nach 1.0a: Atlas entscheidet Layout → Pack 1.2 startet Pixel
3. Parallel zu Pixel: Pack 1.1 Forge SSE Backend
4. Merge Backend+Frontend, Atlas-Accept

**Sprint 2:**
1. Parallel: 2.1 Spark Animation-Spec + 2.5 Lens Cost + 2.4 James A11y
2. Pixel 2.1 Step-DAG (wartet auf Sparks Animation-Spec ~30min-Teil-Deliverable)
3. Forge 2.2 Actions-Backend parallel
4. Pixel 2.2 Actions-UI + 2.3 Filter sequentiell
5. 2.5 Cost-Badge-Integration
6. Atlas-Accept

## Dateien (Master-Liste)

### Neu (Backend)
- `mission-control/src/app/api/pipeline/events/route.ts`
- `mission-control/src/app/api/pipeline/actions/route.ts`
- `mission-control/src/lib/pipeline-event-bus.ts`
- `mission-control/src/lib/pipeline-event-emit.ts`
- `mission-control/src/lib/projections/live-cost.ts`

### Neu (Frontend)
- `mission-control/src/app/pipeline/page.tsx`
- `mission-control/src/hooks/use-pipeline-sse.ts`
- `mission-control/src/components/pipeline/` (8 Components)

### Geändert
- Receipt-Ingestor-Handler → emit event
- Dispatcher-Handler → emit event
- PATCH `/api/tasks/:id` → emit event
- Existing Pipeline-Tab-Page (wenn vorhanden) → redirect oder refactor

### Vault/Docs (neu)
- `spark-pipeline-ux-2026-04-18.md`
- `james-pipeline-benchmark-2026-04-18.md`
- `lens-pipeline-streaming-audit-2026-04-18.md`
- `mission-control/docs/pipeline-shortcuts.md`

## Test-/Validierungsplan

### Sprint 1
- Unit: event-bus eviction, SSE-auth, emit-hook
- E2E Playwright: open /pipeline → assert live-indicator green → trigger PATCH via test-hook → assert card updates within 1s
- Load: 20 parallel SSE-Clients, 1000 events/min, memory bounded

### Sprint 2
- Unit: step-dag node-state logic, cost-projection window-math
- E2E: click card → drawer opens with DAG, active step glowing
- a11y: axe-core 0 violations on pipeline-page
- Keyboard-only flow: navigate + act without mouse

## Risiken

| Risiko | Mitigation |
|---|---|
| SSE-Connection-Leaks bei Browser-Navigation | cleanup im useEffect return, Connection-Limit am Server |
| WK-19 Build-Storm durch 13 neue Files | Sprint in **2 Merges** deployen (Sprint 1 = 1 Merge, Sprint 2 = 1 Merge), Build-Batch-Fenster einplanen |
| James-Bootstrap-Timeout (heute 3x passiert) | 30min-Timeout + Forge-Fallback für 1.0b und 2.4 |
| Live-Animations verbrauchen CPU | CSS-Transforms bevorzugt, keine JS-RAF-Loops, prefers-reduced-motion respektieren |
| Cost-Projection triggers Race gegen Ingestor | event-driven statt polling, idempotent aggregation |
| Step-DAG bei komplexen Task-Retry-Chains | erstmal linear, Branches als Edge-Case in Sprint 3 |

## Rollback

- SSE-Endpoint hinter Feature-Flag `PIPELINE_LIVE=1`
- Alter Pipeline-Tab bleibt parallel erreichbar unter `/pipeline-legacy` für 1 Woche
- DB-Schema unverändert (rein additive in-memory Event-Bus)

## Abhängigkeiten zu parallelen Plänen

- **Task-Tab-Plan** (Lanes T1-T13): Projection `task.lane` aus T1 wird von Pipeline-Tab-Filter ebenfalls genutzt — T1 muss live sein, bevor Sprint 2 Pack 2.3 startet. T1 ist heute Abend live (gerade done).
- **WK-19 Build-Batching**: muss vor Sprint 2 Deploy live sein, sonst 3-4 MC-Downtimes pro Sprint-Commit-Welle.

## ATLAS HANDOFF

### Pack-Split für Atlas
Atlas schneidet in 2 dispatchbare Wellen:

**Welle 1 (Sprint 1):**
- Task A: Spark Pack 1.0a
- Task B: James Pack 1.0b (30min timeout, Forge-Fallback-Flag)
- Task C: Forge Pack 1.1 Backend (kann direkt parallel)
- Task D: Lens Pack 1.3 Streaming-Audit (parallel)
- Task E: Pixel Pack 1.2 (wartet auf Spark Layout-Entscheidung)

**Welle 2 (Sprint 2):**
- Task F: Spark Pack 2.1 Animation-Spec
- Task G: Lens Pack 2.5 Cost-Projection
- Task H: James Pack 2.4 A11y
- Task I: Forge Pack 2.2 Actions-Backend
- Task J: Pixel Pack 2.1 DAG (nach Spark) + Pack 2.2 Actions-UI (nach Forge) + Pack 2.3 Filter

Atlas dispatched Welle 2 **erst nachdem Sprint 1 deployed und geverifiziert** ist.

### Acceptance-Kriterien (Gesamt, Pipeline-Tab ist "live-tauglich")
**Beides muss gelten:**
1. ☐ SSE push < 500ms latency für State-Transition
2. ☐ Operator sieht per Task: agent + aktueller step-name + timeSinceTransition
3. ☐ Operator sieht Queue-Wait (dispatch→pickup) + Execution (pickup→result) separiert
4. ☐ Drawer-DAG zeigt 7-Step-Canonical-Pfad mit aktiver Node glow
5. ☐ 4 Operator-Actions (retry/kick/cancel/accept-review) funktionieren direkt aus View
6. ☐ Filter + Agent-Swimlane funktional, URL-State
7. ☐ Keyboard-Shortcuts + a11y axe-0
8. ☐ Live-Cost-Badge mit 5min-Rolling-Delta
9. ☐ SSE reconnect nach MC-Restart < 5s
10. ☐ Playwright-Smoke grün für `/pipeline` inkl. drawer-open

## Atlas Retrieval Summary

**Zweck:** Pipeline-Tab vom statischen Listenblatt zum echten Live-Monitor mit Step-Level-Agent-Attribution und Inline-Actions erheben.

**Top-3 Research-Findings:**
1. Temporal Multi-View-System + Workers-Tab → Agent-Attribution inspirieren
2. Datadog Execution vs Queue vs Wait-Time → Dispatch-Queue-Wait-Pattern (heute 75min für 090fdc54)
3. SSE statt Polling → <500ms-Feel

**Aktion:** 2 Sprints, 12 Packs, alle 6 Agenten, Split-Acceptance. Foundation-First (SSE + Base-UI), dann Experience (DAG + Actions + Filter).

**Acceptance:** 10 Kriterien, Playwright-Smoke grün, a11y axe-0, SSE latency <500ms.

**Bootstrap:**
- Dieser Plan: `/home/piet/vault/03-Agents/2026-04-18_mission-control-pipeline-tab-2-sprints.md`
- Ground-Truth: `/home/piet/.openclaw/workspace/docs/operations/WORKSPACE-GROUND-TRUTH.md`
- Task-Tab-Plan (Sister): `/home/piet/vault/03-Agents/2026-04-18_mission-control-task-tab-plan.md`

**Prerequisites:**
- Task-Tab T1 Lane-Projection live (heute Abend ✅)
- WK-19 Build-Batching für Sprint 2 Welle

**Empfohlener Ausführungs-Agent:** Atlas (Orchestrator). Packs an Spark, James, Forge, Pixel, Lens, James verteilt.
