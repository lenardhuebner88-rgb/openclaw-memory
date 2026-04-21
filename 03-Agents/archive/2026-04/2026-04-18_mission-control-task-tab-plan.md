---
title: Mission Control — Task Tab Operator-Cockpit Plan
date: 2026-04-18
author: Principal Product-System Architect (Atlas-pre-hand)
status: ready-for-execution
owner: Atlas → Pixel (UI) + Forge (Projections)
version: 1.0
---

# Mission Control — Task Tab Operator-Cockpit

## Kontext

Das Task-Tab im Mission Control Board existiert und hat Lanes + Agent-Load + Next-Best-Action. Die heutige Live-Analyse (2026-04-18 17:53 UTC) zeigt aber, dass **das eigentliche Problem keine UI-Frage ist, sondern ein Projection-Problem**: Lanes, Agent-Load und Status reflektieren nicht die Wahrheit aus `/api/tasks`. Der Operator sieht eine visuell aufgeräumte Oberfläche, die ihm falsche Ruhe suggeriert.

**Messbare Belege aus Live-System (17:53 UTC):**
- 153 Tasks total. Davon 149 in `boardLane=archive` — aber alle werden im Main-HTML gerendert (748 KB HTML, 237 Script-Tags) → kein echter Hauptansicht-Fokus.
- 1 Task `status=review` landet in `boardLane=stalled` — Operator interpretiert das als "hängt", in Wahrheit wartet es auf Review-Entscheidung.
- `/api/agents/live` meldet Atlas mit `tasks.active=[]` — gleichzeitig zeigt `/api/tasks` Atlas mit einem `in-progress`-Task (c3e0e8d4). **Agent-Load lügt.**
- `receiptStage=failed` hat 63 Tasks, aber nur 2 haben `status=failed`. Die anderen 61 sind `canceled` mit "Receipt kam nie" — das ist aber nicht dasselbe wie "failed".
- `executionState` dupliziert `status` ohne Mehrwert. Vier Status-Dimensionen (`status`, `boardLane`, `executionState`, `dispatchState`, `receiptStage`) gleichzeitig → niemand weiß, welche die Wahrheit ist.

## Hauptprobleme (priorisiert)

### P0 — Wahrheits-Gap in Projections
Das Board berechnet Lanes und Agent-Load aus unklaren Kombinationen. Konkret:
- **review→stalled-Bug**: `boardLane=stalled` wird für `status=review` gesetzt — der Operator sieht einen Review als Incident statt als Review.
- **Agent-Load-Drift**: `/api/agents/live` liefert pro Agent `tasks.active`, aber diese Liste wird nicht aus dem Live-Task-Store gefüttert. Die Active-Anzeige zeigt „monitoring, 0 active" während tatsächlich Arbeit läuft.
- **Status-Dimensions-Overload**: 5 parallele Status-Felder ohne klare Führung. Keine "Single Source of Truth"-Feld, das der Operator liest.

### P1 — Archiv-Rauschen dominiert Main-View
149 von 153 Tasks sind `archive`. Sie werden trotzdem im gleichen HTML mit ausgeliefert. Das erzeugt visuelle Last, Lade-Zeit, und verwässert den Hauptansicht-Fokus auf das Offene.

### P2 — "Next Best Action" ohne Evidenz-Bindung
NBA kommt 1x im HTML vor, aber es gibt keine klare Ableitungsregel aus echten Signalen (stale-over-threshold, review-wait, retry-ready, orphaned). Der Operator weiß nicht, warum gerade diese Aktion vorgeschlagen wird.

### P3 — Receipt vs. Status semantisch verrutscht
`receiptStage=failed` heißt "Receipt kam nie" — das betrifft smoke-canceled-Tasks. Aber die Naming-Konvention suggeriert einen Fehlschlag. Confusing für jede Auswertung.

### P4 — Keine echte "Attention-Required"-Pill
"Attention" kommt 3x im HTML vor, aber es gibt keine zentrale "X Tasks brauchen dich jetzt"-Anzeige, die auf einen Blick sichtbar ist und auf konkrete Tasks deep-linked.

## Zielbild

### Hauptansicht (oberhalb des Folds)
```
┌────────────────────────────────────────────────────────────────────────┐
│ MISSION CONTROL · TASKS                                       🔴 2 ATTN │
│                                                                          │
│  Active Now   Waiting for Pickup   Review   Stalled >30m   Incidents    │
│      1              0                 1          0              0         │
│                                                                          │
│  Next Best Action: Accept review of fe36a3eb (Sprint C-Backend, 48m)    │
└────────────────────────────────────────────────────────────────────────┘
```
Eine Zeile, fünf harte Zahlen, ein Attention-Counter rechts (rot wenn >0), eine NBA-Zeile mit **konkretem Task-Link + Begründung**.

### Lane View (5 Lanes, archive verlinkt)
```
READY / PICKED          ACTIVE              BLOCKED / STALLED       REVIEW              INCIDENT
(assigned +             (in-progress +      (blocked OR             (status=review,     (status=failed,
 pending-pickup)         receipt=progress)   stalled>30m)            waiting-accept)     last 24h)

[card] [card]           [card]              [card]                  [card]              [card]

  →  Archive (149) ▸     — link, nicht Lane —
```
Harter Regel-Contract (siehe unten). Jede Karte lebt in **genau einer** Lane, berechnet aus einer deterministischen Funktion.

### Task-Karte (Hauptansicht)
Pflicht-Elemente:
- Title (Einzeiler, truncate)
- Agent-Alias + Priority-Pill
- Alter seit `dispatchedAt` ODER seit letzter Statusänderung (je nach Lane)
- Lane-spezifisches Badge:
  - **Active**: pulsierender Dot + "Running Nms"
  - **Review**: "Review needed by ops"
  - **Stalled**: ⏰-Icon + "Stalled 38m"
  - **Incident**: 🔥 + exit-code oder letzte Fehlerzeile (truncated)
- 1 Primary-Action pro Lane (Review → Accept/Reject; Stalled → Kick/Cancel; Incident → Retry/Close)

Weg von der Karte (in Drawer):
- Description, Handoff-Marker, resultDetails, Events-Timeline, Raw-JSON

### Agent-Load-Sektion
```
Atlas   ████░░░░░░  1/3 WIP · 1 active · 0 queued
Forge   ░░░░░░░░░░  0/2 WIP · 0 active · 0 queued     ⏸ idle
Pixel   ░░░░░░░░░░  0/2 WIP · 0 active · 0 queued     ⏸ idle
Lens    ░░░░░░░░░░  0/1 WIP · 0 active · 0 queued     ⏸ idle
Spark   ░░░░░░░░░░  0/1 WIP · 0 active · 0 queued     ⏸ idle
James   ░░░░░░░░░░  0/2 WIP · 0 active · 0 queued     ⏸ idle
```
- WIP-Limit pro Agent aus `openclaw.json` (config-gebunden, nicht hardcoded).
- "active" zählt nur `status=in-progress + receiptStage ∈ {accepted,progress}`.
- "queued" zählt `status=pending-pickup`.
- `idle`-Tag wenn 0/WIP und lastActivity > 30min.
- Rot-Badge wenn `queued > WIP` (Overload).

### Next Best Action
Regel-Engine, nicht Heuristik. Priorität von oben:
1. Incident offen → "Investigate incident <id>" (→ task-detail)
2. Review seit >30min → "Accept/Reject review <id>" (→ task-detail mit action-buttons)
3. Stalled >30min → "Kick stalled task <id>" (→ retry oder cancel)
4. pending-pickup >15min → "Pickup-Cron verzögert — prüfen" (→ log-tail)
5. Overload-Agent → "Overload on <agent> — pause dispatch" (→ config)
6. Sonst: "Alles ruhig — 24h-Durchsatz N Tasks"

Jede NBA-Zeile enthält Grund (evidenz-gebunden), Task-ID, Primary-Action-Button.

## Required Data / States (Projection-Contract)

Eine **kanonische Projection** pro Task, als neues Feld `lane` im API-Response berechnet:

| Lane | Regel |
|---|---|
| `ready` | `status ∈ {assigned, pending-pickup}` AND `age(dispatchedAt) ≤ 15min` |
| `overdue-pickup` | `status=pending-pickup` AND `age(dispatchedAt) > 15min` |
| `active` | `status=in-progress` AND `receiptStage ∈ {accepted, progress}` |
| `stalled` | `status=in-progress` AND `age(lastActivityAt) > 30min` |
| `review` | `status=review` |
| `incident` | `status=failed` AND `age(resolvedAt) < 24h` |
| `blocked` | `status=blocked` (nur wenn tatsächlich gesetzt) |
| `archive` | `status ∈ {done, canceled}` OR `status=failed AND age>24h` |

Kein Task ist in >1 Lane. Archive wird im Main-View als Link ausgeliefert, nicht als Lane.

### Agent-Load-Projection
Server-Side Aggregation aus Live-Tasks, **nicht** aus Agent-Heartbeat:
```
for agent in agents:
  agent.activeCount = count(t for t in tasks if t.assigned_agent == agent AND lane == 'active')
  agent.queuedCount = count(t for t in tasks if t.assigned_agent == agent AND lane in {'ready','overdue-pickup'})
  agent.wipLimit = config.agents[agent.id].wipLimit  # aus openclaw.json
  agent.overload = agent.queuedCount > agent.wipLimit
  agent.idle = agent.activeCount == 0 AND age(lastActivity) > 30min
```

### Projection-Lücken (müssen zuerst geschlossen werden)
1. **`task.lane` als canonical field** — berechnet on-read in `/api/tasks` + `/api/tasks/:id`. Kein UI-Client darf Lane-Logik selbst machen.
2. **`/api/agents/live.tasks.active` muss aus Live-Task-Store abgeleitet werden**, nicht aus Agent-Heartbeat.
3. **Stale-Detection-Timer** in Minuten, aus Config: `STALLED_AFTER_MIN=30`, `OVERDUE_PICKUP_MIN=15`, `INCIDENT_WINDOW_H=24`.
4. **`receiptStage=failed` Rename** → `receiptStage=no-receipt` oder `receiptStage=unknown` wenn Task canceled ohne Receipt. `failed` reserviert für echte Failure-Receipts.

## Main View vs Detail View

### Zwingend Hauptansicht
- Lane-Counter (5 Zahlen + Attention-Count)
- NBA-Zeile
- 5 Lanes mit je max 10 Karten (scroll-snap horizontal wenn mehr)
- Agent-Load-Leiste
- Archive-Link

### Zwingend Details-Drawer
- Description/Handoff-Block
- resultDetails / Files-Liste
- Events-Timeline
- Retry-History
- Cost-Context (Tokens/USD)
- Raw-JSON-Fallback
- Dispatch-Route-Info (target, gateway-model, bootstrap-hint)

### Grenzfälle
- Priority-Pill auf Karte, Priority-Begründung nur in Drawer.
- Blocker-Grund als Tooltip auf Lane-Badge, voller Text im Drawer.

## Priorisierte Maßnahmen & Umsetzungsreihenfolge

| # | Pack | Typ | Agent | Est. | Risiko |
|---|---|---|---|---|---|
| **T1** | Projection `task.lane` kanonisch berechnen + in API-Response exponieren | Backend | Forge | 60 min | niedrig — additive |
| **T2** | `/api/agents/live` Load aus Live-Tasks ableiten (nicht Heartbeat) | Backend | Forge | 45 min | mittel — agent-status ändert sich |
| **T3** | WIP-Limits in `openclaw.json` pro Agent definieren + Schema | Config | Forge | 20 min | niedrig |
| **T4** | `receiptStage=failed`-Rename auf `no-receipt` für canceled-ohne-Receipt | Backend | Forge | 30 min | mittel — Migration + UI-Abhängigkeiten |
| **T5** | Main-View Refactor: Archive raus aus Main-Render, als Link | Frontend | Pixel | 45 min | niedrig |
| **T6** | 5 Lanes statt N: Projection `lane` direkt rendern | Frontend | Pixel | 90 min | mittel — viele Test-Fälle |
| **T7** | Task-Karte neue Signatur (Badge je Lane, Primary-Action) | Frontend | Pixel | 60 min | niedrig |
| **T8** | Agent-Load-Komponente aus T2-Daten | Frontend | Pixel | 45 min | niedrig |
| **T9** | NBA-Engine mit Regel-Prioritäten (server-side) | Backend | Forge | 60 min | mittel — Evidence-Logik |
| **T10** | NBA-Zeile im Header der Main-View | Frontend | Pixel | 20 min | niedrig |
| **T11** | Attention-Counter + Deep-Link-Filter `/taskboard?focus=<lane>` | Frontend | Pixel | 30 min | niedrig |
| **T12** | Drawer: Description, Events, resultDetails, Raw-JSON | Frontend | Pixel | 60 min | niedrig |
| **T13** | Playwright-Smoke für alle 5 Lanes + NBA-States | Test | Pixel+Forge | 45 min | niedrig |

**Reihenfolge:** T1 → T3 → T2 → T4 → T6 → T7 → T5 → T8 → T9 → T10 → T11 → T12 → T13. Projection-Foundation vor UI-Refactor, damit UI gegen stabile Datenschicht baut.

Geschätztes Gesamtbudget: **~8–9h**, verteilbar auf 2–3 Sessions.

## Betroffene Dateien

### Backend / Projections (Forge)
- `mission-control/src/lib/projections/task-lane.ts` — **neu**
- `mission-control/src/lib/projections/agent-load.ts` — **neu**
- `mission-control/src/lib/projections/next-best-action.ts` — **neu**
- `mission-control/src/app/api/tasks/route.ts` — `lane`-Feld in Response
- `mission-control/src/app/api/tasks/[id]/route.ts` — `lane`-Feld in Response
- `mission-control/src/app/api/agents/live/route.ts` — Load aus Tasks ableiten
- `mission-control/src/app/api/health/route.ts` — Attention-Counter exponieren
- `openclaw.json` — `agents.<id>.wipLimit` Schema-Erweiterung
- `mission-control/src/lib/receipts/stage.ts` — `no-receipt` statt `failed` für canceled-no-receipt (Migration-Flag)

### Frontend (Pixel)
- `mission-control/src/app/taskboard/page.tsx` — Main-View-Struktur
- `mission-control/src/app/taskboard/TaskboardClient.tsx` (oder equivalent)
- `mission-control/src/components/board/header-bar.tsx` — **neu oder refactor**
- `mission-control/src/components/board/lane-grid.tsx` — **neu**
- `mission-control/src/components/board/task-card.tsx` — Signatur-Änderung
- `mission-control/src/components/board/agent-load.tsx` — Datenquelle wechseln
- `mission-control/src/components/board/nba-line.tsx` — **neu**
- `mission-control/src/components/board/attention-counter.tsx` — **neu**
- `mission-control/src/components/board/task-drawer.tsx` — **neu**
- `mission-control/src/components/board/archive-link.tsx` — **neu**

### Config / Schema
- `openclaw.json` Schema-Datei
- `mission-control/config/defaults.ts` — WIP-Defaults

## Test-/Validierungsplan

### Unit-Tests (Forge, Pflicht)
- `task-lane.ts` 20 Testfälle: jede Lane-Regel-Kombination, Grenzwerte (15min, 30min, 24h).
- `agent-load.ts` 8 Testfälle: WIP-Overload, idle-threshold, queued-without-active.
- `next-best-action.ts` 12 Testfälle: Prioritäts-Ranking, leerer-Board-State, Overload-Fall.

### Playwright-Smoke (Pixel, T13)
Szenarien:
1. Board lädt, 5 Lane-Header sichtbar + Archive-Link.
2. Mit seeded Fixture: Task in jeder Lane → Karte in korrekter Lane.
3. Agent-Load zeigt WIP-Bar korrekt für Overload-Seed.
4. NBA zeigt Review-Task wenn Review-Seed existiert.
5. Attention-Counter stimmt mit Lane-Summen.
6. Drawer öffnet bei Card-Click.

### E2E Smoke (Forge)
- seeded Board-Fixture → `/api/tasks` → Lane-Verteilung stimmt mit Projection-Test.
- Agent-Load-API = Aggregat aus Task-API (Property-based check).
- Stale-Task seeden (in-progress, lastActivity = -40min) → erscheint in `stalled` Lane.

### Live-Verify nach Deploy
- GET `/api/tasks?includeLane=1` → jeder Task hat `lane`-Feld.
- Health-Check: `actionUrl` korreliert mit NBA.
- Manuell: fe36a3eb muss in `review` Lane erscheinen (nicht `stalled`).

## Risiken

| Risiko | Mitigation |
|---|---|
| T2 bricht bestehende Agent-Heartbeat-Anzeige | Feature-Flag `AGENT_LOAD_FROM_TASKS=1` (default off, dann Flip) |
| T4 Migration-Pfad für alte Records | Einmal-Migration-Skript `migrate-receipt-stage-rename.ts` mit Dry-Run |
| T6 Viele parallele UI-Tests brechen | T13 zwingend vor Merge, Pre-Merge-Playwright auf CI |
| T1 `lane`-Feld kollidiert mit bestehender Projection | Namespace: `projection.lane` oder `meta.lane` |
| Performance: 153 Tasks auf jedem GET neu projizieren | Memoize pro Request; Cache-Schlüssel = task.updatedAt; Archive nicht projizieren |

## UI / UX Guardrails

1. **Kein Status-Label ohne Datenquelle.** Wenn ein Label gerendert wird, muss es 1:1 aus der Projection kommen — nicht client-side abgeleitet.
2. **Archive gehört nicht in die Hauptansicht.** Link, nicht Lane, nicht Accordion, nicht Sektion.
3. **Maximal 5 Lanes.** Keine "Sub-Lanes". Keine Accordion-Nesting.
4. **Agent-Load zeigt niemals mehr als WIP-Limit ohne roten Badge.**
5. **NBA zeigt immer konkrete Task-ID + evidence-Grund.** Niemals "Consider reviewing some tasks".
6. **Attention-Counter = Summe aus `{overdue-pickup, stalled, review, incident}`.** Nichts anderes.
7. **Keine Card > 4 Zeilen im Main-View.** Alles weitere in Drawer.
8. **Status-Dimensions-Reduktion:** die UI liest NUR `status` + `lane`. `executionState`, `dispatchState`, `receiptStage` nur in Drawer/Raw.

## ATLAS HANDOFF

### Primary-Agent
- **Atlas** plant + splittet in Tasks
- **Forge** executes T1-T4, T9, Tests
- **Pixel** executes T5-T8, T10-T13

### Empfohlener Pack-Split für Atlas
Atlas sollte den Plan in **3 Sub-Pläne** splitten:

- **Sub-Plan A: Projection-Foundation** (T1+T2+T3+T4) → Forge Solo, 2h
- **Sub-Plan B: Main-View + Lanes + Karten** (T5+T6+T7+T8+T11) → Pixel Solo, 4h
- **Sub-Plan C: NBA + Drawer + Smoke** (T9+T10+T12+T13) → Forge+Pixel parallel, 2h

Sub-Plan A muss zuerst merged + deployed sein, bevor B startet. B + C können sich überlappen.

### Acceptance-Kriterien (Operator-tauglich)
**Task-Tab gilt als operator-tauglich, wenn gleichzeitig erfüllt:**
1. ☐ In <10 Sekunden erkennbar: Anzahl (a) Active, (b) Review-needed, (c) Stalled, (d) Incident, (e) Waiting-for-Pickup.
2. ☐ NBA zeigt konkrete Task-ID mit Evidenz-Grund, nicht generisch.
3. ☐ Review-Tasks erscheinen in Review-Lane, nicht in Stalled.
4. ☐ Agent-Load matcht `/api/tasks`-Realität (property-based test grün).
5. ☐ Keine Archive-Tasks im Main-View-HTML (HTML-Size <200 KB).
6. ☐ Attention-Counter = rot wenn >0, sonst Neutral.
7. ☐ Stale-Tasks (in-progress >30min ohne Activity) werden visuell als Stalled dargestellt — nicht als Active.
8. ☐ Alle 5 Lanes haben mind. 1 Playwright-Smoke-Case grün.

## Atlas Retrieval Summary

**Zweck:** Task-Tab vom visuellen Dashboard zum echten Operator-Cockpit heben. Kernproblem ist Projection-Gap, nicht UI.

**Top-3 Findings (aus Live-State 2026-04-18 17:53 UTC):**
1. Review-Tasks landen in Stalled-Lane → falsches Risikosignal.
2. Agent-Load wird aus Heartbeat gelesen, nicht aus Tasks → Drift.
3. 97% der Tasks sind Archive, werden trotzdem mitgerendert → Rauschen.

**Aktion:** 13 Packs T1–T13, in 3 Sub-Plänen A/B/C. Foundation-First. Projection vor UI. Keine kosmetischen Änderungen.

**Acceptance:** 8 Kriterien, Playwright-Smoke grün, Agent-Load property-based verifiziert, HTML <200 KB.

**Bootstrap:**
- Dieser Plan: `/home/piet/vault/03-Agents/2026-04-18_mission-control-task-tab-plan.md`
- Ground-Truth: `/home/piet/.openclaw/workspace/docs/operations/WORKSPACE-GROUND-TRUTH.md`
- Task-Schema-Beispiel: GET `/api/tasks/1733f39d-f1e9-4c63-91aa-e778a6c79545`

**Reihenfolge:** T1 → T3 → T2 → T4 → T6 → T7 → T5 → T8 → T9 → T10 → T11 → T12 → T13.

**Prerequisites:**
- Verify-Consolidation Nacht-Sprint (c3e0e8d4) sollte abgeschlossen sein, bevor T1 startet — V6 liefert evtl. zusätzliches Finding zur KPI-Projection.
- WK-19 Build-Batching sollte live sein, bevor 13 Packs deployed werden (sonst Build-Storm).
