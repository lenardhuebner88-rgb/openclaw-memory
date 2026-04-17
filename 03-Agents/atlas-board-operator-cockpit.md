---
title: Mission Control Board — Operator Cockpit Target
version: 1.0
status: pilot-ready
owner: Principal Product-System Architect
created: 2026-04-17
depends_on: atlas-worker-system-hardening.md, e2e_orchestrator_run_2026-04-17.md
---

# Mission Control Board — Operator Cockpit Target

Zielentwurf für das MC-Board als echte Kontrollzentrale. 10-Sekunden-Lageerfassung, keine Fake-Ruhe.

## EXECUTIVE JUDGMENT

Das aktuelle Board zeigt Daten, aber kein **Urteil**. Ein Operator sieht Spalten, aber nicht ob der Zustand **gesund, wartend oder gefährlich** ist. "Pending-Pickup" und "In-Progress" sehen visuell gleich aus, obwohl semantisch Welten liegen. Agent-Load ist nirgends sichtbar. Next-Best-Action gibt es nicht — der Operator muss selbst interpretieren. Die Lösung ist nicht mehr UI, sondern **weniger und ehrlicher**: vier Signale, die wirklich tragen, plus ein Handlungs-Hint. Alles andere gehört ins Detail.

Die Backend-Voraussetzungen sind **fast vollständig da** (nach Phase 1/2/F-6). Fehlt: Stall-Klassifikation (kommt mit Worker-Hardening Pack 5), Agent-Load-Aggregat, Next-Best-Action-Regelwerk.

## CURRENT BOARD PROBLEM

1. **Fake-Ruhe durch Spalten-Normalisierung.** Kanban zeigt alle Tasks in Spalten — ein stalled in-progress sieht aus wie gesundes in-progress. Operator muss Task öffnen um zu sehen dass `lastActivityAt` vor 2h war.
2. **Status-Explosion statt Synthese.** 9 Status-Werte + executionState + dispatchState + receiptStage = 4-dimensionales Gitter. Kein Mensch liest das unter Stress.
3. **Agent-Perspektive fehlt.** "Was macht Forge gerade?" geht nur über Filter + manuelles Zählen. Bei Engpass (Forge hat 5 in-progress, Pixel hat 0) keine visuelle Aufforderung zur Umverteilung.
4. **Keine Incident-Urgency-Signale.** Failed vor 2h und failed vor 2min sehen gleich aus. Recovery-Load-Metrik existiert im Health-Endpoint, ist aber nicht im Board.
5. **Next-Best-Action ist implizit.** Operator muss aus Kontext ableiten: "6 pending-pickup > 10min → Dispatch hakt" — sollte stehen, steht nicht.
6. **Kosmetische Fülle.** Canceled-Tasks, Draft-Templates, historische Dones füllen Lane-Höhe und verdrängen operativ relevante Tasks im Viewport.
7. **Dispatch-Observability fehlt in UI** trotz Backend-Feld (dispatchNotificationMessageId seit F-6). Kein Discord-Deep-Link-Knopf.

## TARGET BOARD MODEL

Drei-Zonen-Layout, von oben nach unten in Lese-Priorität:

```
┌──────────────────────────────────────────────────────────────────┐
│  ZONE A — HEARTBEAT STRIP  (immer, 1 Zeile, 4 Lichter)          │
│  [●MC:up] [●Gateway:up] [●Dispatch-Consistency:1.0] [⚠Recovery: 2]│
├──────────────────────────────────────────────────────────────────┤
│  ZONE B — NEXT BEST ACTION  (1 Satz + 1 Button)                 │
│  "3 tasks pending-pickup >5min bei Forge — Agent triggern?"      │
├──────────────────────────────────────────────────────────────────┤
│  ZONE C — LIVE FLOW  (5 Lanes, nur offene+recent-terminal Tasks) │
│  Waiting │ Picked │ Active │ Stalled │ Incident                  │
│  ├──────┼────────┼────────┼─────────┼──────────                  │
│  │ ⏱3m  │ ⏱2m    │ ▶1m    │ ⚠12m    │ ✗just now                  │
│  │ task │ task   │ task   │ task    │ task                       │
├──────────────────────────────────────────────────────────────────┤
│  ZONE D — AGENT LOAD  (rechte Sidebar, 6 Agents)                │
│  Forge  ████▁▁  4/2 ⚠overloaded                                  │
│  Pixel  ▁▁▁▁▁▁  0/2 idle                                         │
└──────────────────────────────────────────────────────────────────┘
```

Lane-Semantik (nicht identisch mit status):
- **Waiting**: status ∈ {draft, assigned} — noch kein Dispatch.
- **Picked**: status==pending-pickup — dispatched, kein Receipt.
- **Active**: status==in-progress AND executionState==active AND lastActivityAt<10min.
- **Stalled**: status==in-progress AND (executionState==stalled-warning OR lastActivityAt>10min) OR status==blocked.
- **Incident**: status==failed AND (completedAt<1h ago OR unacknowledged).

Alles andere (done >1h, canceled, templates) → nur in Archiv-Tab, nicht Hauptansicht.

## INFORMATION ARCHITECTURE

### Hauptansicht (Cockpit)
Genau 4 Zonen. Keine Tabs, kein Akkordeon, kein Scroll unterhalb Fold bis der Operator aktiv navigiert. Ziel: 10-Sekunden-Erfassung.

### Detail-Ansicht (Task Drill-down)
Öffnet sich als Side-Panel (nicht Modal — Cockpit bleibt sichtbar). Inhalt:
- **Lifecycle-Timeline** mit Zeitstempeln t0…t3 und Latenzen (aus E2E-Report-Schema).
- **Receipt-Chain** mit allen empfangenen Stages.
- **Dispatch-Trace**: Discord-Deep-Link (`dispatchNotificationMessageId`), Notification-Status, failureReason.preservedFrom falls vorhanden.
- **Retry-History** (wenn Pack 8 aus Worker-Hardening live).
- **Raw JSON** (collapsible, für Debug — nie Default).

### Archiv-Tab
Done, canceled, failed >1h, failureReason-Search. Getrennt, weil Operator-irrelevant im Normalbetrieb.

## PRIMARY OPERATOR SIGNALS

Diese vier Signale decken 95 % der Cockpit-Fragen:

1. **System-Heartbeat** (4 Lichter). Grün/Gelb/Rot aus Health-Endpoint, kein neuer Data-Pipeline.
2. **Live-Flow-Lane-Counts** (5 Zahlen). Ehrliche Klassifikation nach Lane-Semantik oben.
3. **Agent-Load** (6 Balken). `in_progress + pending_pickup` pro Agent, Schwelle `maxConcurrent` aus Agent-Config → Ampel.
4. **Next-Best-Action** (1 Satz). Regel-abgeleitet, s. nächste Sektion.

Alles andere ist Dekoration und gehört ins Detail.

### Next-Best-Action — Regelwerk

Priorisiert, erste Match gewinnt:

| Prio | Bedingung | NBA-Text | Button |
|---|---|---|---|
| 1 | Heartbeat RED | `System-Incident — {component} down` | "Open logs" |
| 2 | recovery-load > 3 | `{n} orphaned dispatches — worker-monitor dry-run inspizieren` | "Open monitor plan" |
| 3 | ≥1 stalled (>30min) | `{n} stalled tasks — failure oder Intervention?` | "Review stalled" |
| 4 | ≥1 agent overloaded AND ≥1 idle | `Forge 4/2 überladen, Pixel idle — umverteilen?` | "Reassign" |
| 5 | ≥3 pending-pickup >5min bei gleichem Agent | `{agent} picked 0/3 in 5min — Agent-Pickup triggern?` | "Trigger agent" |
| 6 | failed <10min ago, unacknowledged | `Task {id} just failed — Root-Cause prüfen` | "Open task" |
| 7 | nichts von 1–6 | `All clear — {n} active, {avg}min avg lifecycle` | — |

Regeln sind **im Backend** berechnet (`/api/board/next-action`), UI rendert nur.

## MAIN VIEW VS DETAIL VIEW

### In Hauptansicht (Pflicht)
- Lane-Zuordnung (nicht status direkt!)
- Age-im-aktuellen-State (⏱3m — wie lange schon picked)
- Agent-Avatar + Kürzel
- Priority-Dot (nur wenn != medium)
- Discord-Notified-Check (✓ bei `dispatchNotificationMessageId` gesetzt, sonst grau)

### Nur in Detail
- Task-ID
- Raw-Timestamps (ISO)
- executionState, dispatchState, receiptStage (3 Felder, collapsible)
- Description (Execution-Contract-Block)
- Retry-Count + Next-Retry-At
- failureReason inkl. preservedFrom
- workerSessionId-Prefix
- Raw JSON

### Nie in Board
- `updatedAt` (rauschend, irrelevant für Operator)
- `autoGenerated`, `autoSource` (UX-Kosmetik)
- `recordType`, `securityRequired` (nur filter-relevant, in Archiv-Tab)
- Canceled-Tasks in Hauptansicht

## REQUIRED DATA / EVENTS

### Bereits vorhanden (nach 2026-04-17-Session)
- `/api/health` mit `pendingPickup, inProgress, failed, staleOpenTasks, orphanedDispatches, recoveryLoad, dispatchStateConsistency` ✓
- `/api/tasks` mit allen Statuses + `assigned_agent` ↔ `assignee` ✓ (Phase 1)
- `dispatchNotificationMessageId` ✓ (F-6)
- `lastActivityAt` im Task-Schema ✓

### Neu benötigt (minimaler Backend-Change)

**B1 — Lane-Klassifikation im Response.**
In `getTasks`-Projektion ein synthetisches Feld `boardLane: 'waiting'|'picked'|'active'|'stalled'|'incident'|'archive'` nach oben beschriebener Regel. Ein-Liner in `src/app/api/tasks/route.ts`, ausgelagert in `src/lib/task-board-lane.ts`. Kein Schema-Change.

**B2 — Agent-Load-Aggregat.**
Neuer Endpoint `GET /api/board/agent-load` → `[{agent, activeCount, pickedCount, maxConcurrent, state: 'idle'|'ok'|'loaded'|'overloaded'}]`. Aggregiert aus readTasks. Cache 5s.

**B3 — Next-Best-Action-Endpoint.**
`GET /api/board/next-action` → `{priority, text, action, actionPayload}`. Liest Tasks + Health, wendet Regel-Matrix an. Pure Function, testbar.

**B4 — Stall-Marker.**
Voraussetzung: Worker-Hardening Pack 5 (stalled-warning + stalled-failed). Board blockt ohne das nur auf lastActivityAt-Heuristik — akzeptabel als Zwischenzustand.

**B5 — SSE/WebSocket-Live-Update.**
Cockpit polled aktuell. Für echte Live-Erfahrung: `GET /api/board/events` als SSE mit board-event-log Entries. Polling-Fallback bei Disconnect.

## IMPLEMENTATION PACK

Sieben Packs, UI + Backend getrennt. Jedes Pack standalone wertvoll — kein Big-Bang.

### Pack 1 — Lane-Klassifikation (Backend, B1)
`src/lib/task-board-lane.ts` + Projektion in `/api/tasks`. Tests: einen Task pro Lane, Klassifikator deterministisch. Kein UI-Change noch.

### Pack 2 — Heartbeat-Strip (UI, Zone A)
Kleine Komponente `<BoardHeartbeat/>` oben im Taskboard-Tab. Liest `/api/health`, 4 Ampeln. Keine neuen Daten, nur neue Darstellung. PR-Größe < 200 LoC.

### Pack 3 — Live-Flow-Lanes (UI, Zone C)
Bestehende Kanban-Spalten durch Lane-basierte Spalten ersetzen. Nutzt `boardLane` aus Pack 1. Age-Badge (⏱) aus `lastActivityAt`/`dispatchedAt`. Archive-Tab als separater Route-Eintrag.

### Pack 4 — Agent-Load-Sidebar (UI + Backend, B2)
`/api/board/agent-load` + `<AgentLoadPanel/>`. Rechts an Board, responsive — bei schmalem Viewport oben.

### Pack 5 — Next-Best-Action-Banner (UI + Backend, B3)
`/api/board/next-action` + `<NextActionBanner/>`. Text + Button + aktionierbare Link. Button-Clicks loggen `board-event:nba-acted` für Audit.

### Pack 6 — Task-Detail-Panel (UI)
Side-Panel mit Timeline, Receipt-Chain, Discord-Deep-Link, Retry-History. Nutzt vorhandene Task-Daten + Board-Event-Log.

### Pack 7 — Live-Updates via SSE (Backend + UI, B5)
SSE-Stream + Client-Hook `useBoardStream`. Polling als Fallback. Nur nach Pack 1–6 stabil.

### Reihenfolge
1 → 2 → 3 → 4 → 5 → 6 → 7. Nach jedem Pack ist Cockpit funktional einsetzbar — User kann nach Pack 3 schon produktiv arbeiten, Pack 4+ sind Upgrades.

## RISKS

1. **Lane-Fehlklassifikation maskiert Probleme.** Wenn Stall-Threshold zu groß, sieht stalled wie active aus → Fake-Ruhe. Mitigation: Threshold-ENV-Var, monitor-Audit mit Lens, konservativer Startwert (10min warn, 30min hard laut Worker-Hardening).
2. **NBA-Regeln verdrängen echten Operator-Judgment.** Wenn Operator Regel-Hints blind folgt, lernt er System nicht mehr. Mitigation: NBA ist Suggestion, nicht Auto-Action; jeder Button-Click braucht Bestätigung mit Kontext-Display.
3. **SSE bricht hinter Reverse-Proxy.** Wenn Proxy Buffering forciert, hängt Stream. Mitigation: Pack 7 mit Polling-Fallback, chunked-response-Header explizit.
4. **Archive-Tab wird nie besucht.** Operative Lernkurve verliert History-Kontext. Mitigation: Detail-Panel zeigt History-Link auf Task-ID, Archive-Tab ist 1 Click.
5. **Agent-Load-Signal ungenau** wenn maxConcurrent falsch konfiguriert. Mitigation: Load-State explizit zeigen, nicht nur Ampel; Baseline-Messung durch Lens vor Rollout.
6. **Mobile/Schmal-Viewport vernachlässigt.** Cockpit ist Desktop-Primary. Mitigation: Zone D kollabiert als Chips oben, Zone A/B/C bleiben.

## RECOMMENDED EXECUTION AGENT

- **Pixel (frontend-guru)** — primary UI. Packs 2, 3, 4-UI, 5-UI, 6, 7-UI.
- **Forge (sre-expert)** — backend. Packs 1, 4-API, 5-API, 7-SSE.
- **Lens (efficiency-auditor)** — Signal-Truth-Audit. Misst: stimmen Lane-Zählungen mit manueller Stichprobe? NBA-Regeln fire korrekt in Edge-Cases? Stall-Threshold-Kalibrierung.
- **Atlas (main)** — Pack-Promotion-Gate, koordiniert UI↔Backend-Paare.

Rollen-Invariante: Pixel und Forge arbeiten paarweise pro Pack. Lens reviewt vor Live-Schaltung. Kein UI-Pack geht live ohne Backend-Sign-off und umgekehrt.

## ACCEPTANCE CRITERIA

10-Sekunden-Test ist Haupt-Gate. Zusätzlich messbar:

1. **10-Sekunden-Test** mit neuem Operator: erkennt aus dem kalten Cockpit korrekt (a) ob System gesund, (b) was wartet, (c) wo engpass-Agent, (d) was die nächste Aktion ist. Pass-Schwelle: 4/4 korrekt in ≤10s bei 5 zufälligen Board-Zuständen.
2. **Keine Fake-Ruhe**: Chaos-Test injiziert stalled + failed + overloaded — Cockpit rendert Stalled-Lane und NBA korrekt. Keine grüne Fehlanzeige.
3. **NBA-Korrektheit**: aus 20 synthetisch generierten Board-States erzeugt Backend korrekte NBA-Regel-Auswahl in ≥19/20.
4. **Agent-Load-Genauigkeit**: manuelle Stichprobe vs Sidebar-Zahlen → 100 % Match (Zählung ist deterministisch, darf nicht abweichen).
5. **Discord-Deep-Link funktioniert** in Detail-Panel für 100 % der Tasks mit dispatchNotificationMessageId.
6. **Lane-Klassifikations-Stabilität**: keine Lane-Flapping (Task springt Lane innerhalb 1min hin+zurück) außer bei echtem State-Wechsel.
7. **Archive-Tab ausgelagert**: Hauptansicht hat 0 canceled + 0 done >1h.
8. **Performance**: Cockpit Time-to-Interactive <1.5s auf Homeserver-LAN.
9. **Regel-Audit-Trail**: jede NBA-Button-Action erzeugt board-event mit Regel-Nummer.
10. **Happy-Path-Regression**: Smoke-Suite weiter 10/10.

Pass = 9/10. Hard-Stop: #1 (10-Sekunden-Test) oder #2 (Fake-Ruhe).

---

## Abhängigkeits-Karte

```
Worker-Hardening Pack 5 (stalled-warning)   ← benötigt für Lane "Stalled" ehrlich
         │
         ▼
Board Pack 1 (Lane-Klassifikation)          ← Foundation für UI
         │
         ├─▶ Board Pack 2 (Heartbeat)
         ├─▶ Board Pack 3 (Live-Flow)
         │
         ▼
Board Pack 4 (Agent-Load) + Pack 5 (NBA)
         │
         ▼
Board Pack 6 (Detail-Panel)
         │
         ▼
Board Pack 7 (SSE-Live)
```

Session-Modell (aus `atlas-session-memory-operating-model.md`): Board-Packs sind **Umsetzungs-Sessions** mit max 40 Tool-Calls, scope = ein Pack.

## Referenzen

- `/home/piet/vault/03-Agents/atlas-worker-system-hardening.md` — Pack 5 als Stall-Voraussetzung
- `/home/piet/vault/03-Agents/atlas-session-memory-operating-model.md` — Session-Kontrakt für Umsetzung
- `src/lib/operational-health.ts` — bestehende Health-Metriken
- `src/lib/taskboard-types.ts` — Task-Schema inkl. dispatchNotificationMessageId (F-6)
- `src/lib/executive-metrics.ts` + `executive-trends.ts` — bestehende KPI-Funktionen (Archiv-Tab-Material)
