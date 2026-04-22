---
title: Pipeline-Tab Plan v3 — Task-First Live-Monitor (Operator-Produktreif)
date: 2026-04-18 22:20 UTC
author: Operator-Architect (direct-execution mode via SSH)
status: in-execution
owner: Operator (self) parallel zu Atlas-Stream (Task-Tab v2)
version: 3.0
supersedes: 2026-04-18_mission-control-pipeline-tab-2-sprints.md (v1/v2)
---

# Pipeline-Tab v3 — Task-First-Produkt

## Warum v3
v1/v2 waren "Refactor-Pläne". Live-Code-Analyse (PipelineClient 437 LOC Agent-zentrisch, KanbanBoard 130 LOC dead code) + Best-in-Class-Research zeigen:
- Bestehender Pipeline-Tab ist Agent-Pulse-View - technisch korrekt, für Nicht-Coder unlesbar
- Tool-Call-Events sind Forensik, nicht Produkt-UI
- Research-Konsens: **Task ist die mentale Einheit, nicht Agent**

v3 baut Task-First-Cockpit mit Stage-Stepper-Metapher. Agent-View bleibt als 2. Toggle.

## Research-Übernahmen (Best-in-Class)
Aus 5 Mustern (Linear, Stripe, Uber, Height, Zapier):
1. **Horizontal Stage-Stepper** (Stripe PaymentIntent-Lifecycle)
2. **"Wer & Was jetzt"-Einzeiler** (Uber ETA-Pattern)
3. **Waiting-Reason explizit** (Height-Retry / Dagster Steps)
4. **Next-Up Ghost-Node** (Zapier History)
5. **Eine Card pro Task** (Linear Issue-Paradigma)

## Zielbild

### Task-Pipeline-Card (Hero)
```
┌─────────────────────────────────────────────────────────────┐
│ [Sprint C-Backend] Automations-API — Kill-Switch            │
│ Mission Control · Priority High                              │
│                                                              │
│ ●━━━●━━━◐━━━○━━━○      Next: Review by QA                   │
│ Draft  Dispatched  Working*  Review   Done                   │
│                                                              │
│ 👤 Forge · Security-Check · seit 3m · ETA ~2m              │
│ ⚠️ Waiting on: security-gate-pass                           │
│                                                              │
│ [ Details ▼ ]                                                │
└─────────────────────────────────────────────────────────────┘
```

### 5 kanonische Stages
| # | Stage | Status-Regel | Farbe |
|---|---|---|---|
| 1 | Draft | status in draft,assigned | grau hohl |
| 2 | Dispatched | status=pending-pickup | blau |
| 3 | Working | status=in-progress | blau pulsierend (2s) |
| 4 | Review | status=review | amber |
| 5 | Done | status=done | grün gefüllt |

**Sondermodi:**
- Failed: Card-Border rot, Stage wo es failed markiert
- Blocked: Amber-Waiting-Reason-Badge
- Canceled: nicht in Pipeline (Archive)

### "Wer macht was"-Zeile (Uber-Style)
```
👤 <Agent-Alias> · <Friendly-Tool-Name> · seit <Elapsed> · ETA <Estimate>
```
- Agent-Alias (Forge, nicht sre-expert)
- Tool-Name humanized ("Security-Check", nicht "security_gate_check")
- Relative time
- ETA via einfacher Durchschnitt ähnlicher Tasks

### Waiting-Reason (Height-Style)
Wenn blocked/stalled: Amber-Badge mit Klartext:
- "⚠️ Waiting on: security-gate-pass"
- "⏱ Rate-limit: 30s"
- "🚦 Queue-delay: Forge busy"

Nie stumm pulsieren — immer Grund nennen.

### Next-Up Ghost-Node
Rechts im Stepper als 40% opacity:
- "Next: Review by QA"
- "Next: Ship to production"

Zeigt Mentalmodell der Vorhersagbarkeit.

## View-Toggle (Product-Switch)

Oben rechts Toggle:
```
[ Tasks | Agents ]
```
- **Tasks** (default, neu) — Task-Pipeline-Cards
- **Agents** (legacy) — bisheriger Agent-Pulse-View

## Datei-Struktur

### Neu
- `src/app/kanban/components/StageStepper.tsx` — 5-Node horizontaler Stepper
- `src/app/kanban/components/TaskPipelineCard.tsx` — Task-Card mit Stepper + Wer-Was + Waiting + Next
- `src/app/kanban/components/ViewToggle.tsx` — Tasks | Agents Switch
- `src/app/kanban/components/WaitingReasonBadge.tsx`
- `src/app/kanban/components/NextUpPreview.tsx`
- `src/lib/task-pipeline-payload.ts` — Server-side Payload für Task-View

### Modify
- `src/app/kanban/page.tsx` — beide Payloads laden
- `src/app/kanban/PipelineClient.tsx` — View-Toggle + Default auf Tasks-View
- `src/app/api/pipeline/route.ts` — optional neuer Endpoint /api/pipeline/tasks

### Delete
- `src/app/kanban/components/KanbanBoard.tsx` — dead code, weg
- `src/app/kanban/components/KanbanBoard.tsx.bak-2026-04-17-spot` — backup weg
- `src/app/kanban/components/KanbanColumn.tsx` — mit raus (unused)
- `src/app/kanban/components/KanbanCard.tsx` — mit raus (unused)

## Umsetzungs-Reihenfolge

1. **Datenschicht** (task-pipeline-payload.ts) — Mapping Task-Status → Stage
2. **StageStepper.tsx** — 5-Node horizontal, CSS-only Animation
3. **TaskPipelineCard.tsx** — nutzt Stepper + Wer-Was + Waiting + Next
4. **ViewToggle.tsx** — Tabs-UI
5. **Modify PipelineClient.tsx** — Toggle + Render beider Views
6. **Cleanup dead code** KanbanBoard/Card/Column
7. **Build + Deploy atomar** (R15)
8. **Screenshot-Verify** Desktop + Mobile

Gesamt ~2h Wall-Clock.

## Akzeptanz
- ☐ /kanban lädt, Default-View = Tasks
- ☐ Task-Cards zeigen Stepper mit 5 Nodes
- ☐ Aktuelle Stage pulsiert (nur sie)
- ☐ Wer-Was-Zeile lesbar ohne Coding-Wissen
- ☐ Waiting-Reason als Amber-Badge wenn zutreffend
- ☐ Next-Up als Ghost-Node
- ☐ View-Toggle zu Agents funktioniert
- ☐ Mobile-Layout: Stepper stackbar oder scrollbar
- ☐ Playwright-Smoke grün

## Rollback
- Feature-Flag `PIPELINE_TASK_VIEW=1` (default on)
- Bei Flag off: alter Agent-Pulse-View ist Default
- git revert möglich bis zum Commit-Hash vor Deploy

## Parallel-Koordination
- Atlas-Orchestrate läuft Task-Tab v2 Welle 1-4
- Forge ist belegt mit Welle 1 (A1/A2/A3) — **ich wähle Pixel-freie Components-Only-Implementation**
- Kein Konflikt, weil Task-Tab und Pipeline-Tab getrennte Files
- Build-Koordination: ich merge NACH Atlas-Welle-1-Deploy (WK-19 Schutz)
