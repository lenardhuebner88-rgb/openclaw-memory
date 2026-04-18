---
title: Mission Control Vault — Master Index
date: 2026-04-19
maintained-by: Operator (manuell nach sessions)
purpose: Single Source of Truth für alle Pläne, Audits, Agent-Outputs im Vault. Status pro Dokument, Trigger-Phrases für aktive Pläne.
---

# Vault Master Index — 03-Agents/

## Wie lesen
- **ACTIVE** = Plan wird heute/morgen ausgeführt oder ist in laufender Execution
- **REFERENCE** = Foundation-Dokument, keine direkten Actions, wird von Plänen zitiert
- **COMPLETED** = Durchgeführt oder superseded, nur für History-Lookup
- **OUTPUT** = Agent-Research-Report, eingefroren als Snapshot

Trigger-Phrases verwenden genau den Wortlaut *"Lade `…` und starte …"* — Atlas erkennt das als Execution-Request.

---

## 🔴 ACTIVE — heute/morgen laufende Pläne

### 1. `atlas-stabilization-plan-2026-04-19.md` (7.9 KB, 151 Zeilen) — **P0**
**Status:** ready-for-execution, erster Morgen-Pack
**Warum P0:** Closes 6 systemische Schwächen aus gestriger Stress-Session (konkurrierende Mutation-Channels, keine Build-Gates, Root-Cause-Fix-Timing). Muss vor allen neuen Features laufen.
**Scope:** 6 Phasen, ~4-5h — Cleanup, Operator-Lock-Feature, Build-Gate, task-assignees Refactor, Legacy re-POST, Kosten-Routing.
**Trigger:** *"Lade Stabilization-Plan 2026-04-19 und starte Phase 1."*

### 2. `2026-04-18_pipeline-tab-plan-v3.md` (6.1 KB) — teilweise live
**Status:** Sprint 1 LIVE deployed (Stage-Stepper, Task-First, View-Toggle, Route-Alias `/pipeline → /kanban`), Sprint 2 (Step-DAG in Drawer, Inline-Actions, Filter, Mobile-Polish) offen.
**Trigger:** *"Lade Pipeline-Tab-Plan v3 und starte Sprint 2."*

### 3. `2026-04-18_mission-control-task-tab-plan-v2.md` (8.0 KB) — teilweise live
**Status:** A4 (Later→Archive), A5 (Dispatched-Metric), C3 (Route-Alias), B2 (Receipt-Rename), Mobile C4/C5/C6 LIVE. A1/A2 (FAILED-Counter, NBA-Regel) offen, 4 Legacy-Tasks (P1-A/C, P2-A, Spark-UX) zu re-POSTen nach Stabilization-Plan Phase 5.
**Trigger:** *"Lade Task-Tab-Plan v2 und starte A1."*

### 4. `atlas-worker-system-hardening.md` (16.1 KB)
**Status:** Packs 1/3/7 done. **Offen:** Pack 2 (Receipt-Sequence), Pack 4 (Dispatch-Idempotency mit dispatchToken), Pack 5 (Stall-Detector), Pack 8 (Retry-Single-Path). Wichtiges Thema: heutige Ghost-Fail-Probleme berühren Pack 2+8.
**Trigger:** *"Lade Worker-Hardening und starte Pack 2."*

### 5. `atlas-continuation-orchestrator.md` (18.5 KB)
**Status:** Packs A/C/D/G done. **Offen:** Pack B (Seed-Konverter Vault→YAML), Pack E (Cron live `DRY_RUN=0`), Pack F (Retry-Eskalation).
**Trigger:** *"Lade Continuation-Orchestrator und starte Pack B."*

### 6. `atlas-costs-cockpit-v2.md` (28.6 KB)
**Status:** ~90% done — Phase 1 + Packs 1-5 Backend + Zone A/B UI + Pack 8 Modal live. **Offen:** Zone D Agent-Ladder.
**Trigger:** *"Lade Costs-Cockpit-v2 und starte Zone D."*

### 7. `atlas-board-operator-cockpit.md` (15.4 KB)
**Status:** Pack 1 + Zone A (Heartbeat) + Zone B (NBA) + Pack 8 (Cost-Story-Modal) done. **Offen:** Phase 2 Navigation-Refactor (13→7 Tabs), Zone C/D Fortsetzung, Pack 7 SSE.
**Trigger:** *"Lade Board-Cockpit und starte Phase 2 Navigation."*

---

## 📘 REFERENCE — Foundation-Dokumente

### `atlas-session-memory-operating-model.md` (10.7 KB)
Session-Typen, Memory-Schichten (LTM/Working/Archive), Handoff-Template. Foundation für alle Atlas-Sessions.

### `spark-agent-display-guide-2026-04-18.md` (8.4 KB) 🆕 heute
Agent-Signatur-Tabelle: Runtime-ID × Display × Emoji × Color × Short-Code. Implementation-Hint für `src/lib/agent-ui.ts`. Anti-Drift-Regel §0.

### `atlas-weakness-audit-2026-04-17.md` (15.4 KB)
13 Findings, 7-Pack-Fix-Plan — **100% abgeschlossen** inkl. P1-P7. Wichtige Reference-History für Incident-Analyse.

---

## ✅ COMPLETED — Abgeschlossene oder superseded Pläne

### Heute (2026-04-18) Abend/Nacht abgeschlossen
- `atlas-verify-consolidation-2026-04-18-night.md` — 7-Pack Verify-Sprint, completed-with-warnings (V3 via retry-task)
- `2026-04-18_night_3h_active_sprint.md` — 10 Packs durch in 3h (Pipeline-Tab v3, A4/A5/C3, Naming-P1/P2, B1/B2, C1-C6)
- `atlas-stabilization-sprint-2026-04-18.md` — 6 P0/P1-Fixes + P1-4 Playwright-Framework = 100%
- `atlas-mc-board-tab-expansion-2026-04-18-evening.md` — 4/5 Sprints done, Sprint C-UI done via Atlas-Heartbeat

### Superseded (durch neuere Versionen ersetzt)
- `2026-04-18_mission-control-task-tab-plan.md` (v1) → durch `…-v2.md` ersetzt
- `2026-04-18_mission-control-pipeline-tab-2-sprints.md` (v1) → durch `…-v3.md` ersetzt
- `atlas-next-level-plan-2026-04-19.md` → durch `atlas-stabilization-plan-2026-04-19.md` ersetzt (Stabilization priorisiert)

---

## 🗞️ SESSION-REPORTS (archival)

- `atlas-session-report-2026-04-18-morning.md` (16.2 KB) — Crisis-Response + Pack-Welle
- `atlas-session-report-2026-04-18-evening.md` (8.5 KB) — End-Of-Day 22+ Deliveries

---

## 🎯 AGENT-OUTPUTS — Research-Snapshots

### James (Research/Navigation)
- `james-operator-dashboard-research-2026-04-18.md` (24 KB)
- `james-navigation-patterns-2026-04-18.md` (12 KB)

### Spark (UX-Concepts)
- `spark-overview-hero-concept-2026-04-18.md` (12 KB) — Zone A/B/C/D Hero
- `spark-mobile-ui-audit-2026-04-18.md` (5.3 KB)
- `spark-cost-story-modal-interaction-2026-04-18.md` (6.1 KB)
- `spark-cost-story-ux-concept.md` (4.7 KB)
- `spark-pending-pickup-recovery-research.md` (6.0 KB)

---

## 📂 SUB-AGENTS (Worker-Workspaces — nicht Pläne)

`03-Agents/` enthält auch Worker-Workspaces von:
- `Forge/`, `Pixel Cockpit Pack3/`, `Pixel Cockpit Pack5/`, `Lens/`, `James/`, `Spark Relief/`, `Smoke Bot/`, `OpenClaw/`, `Researcher/`, `Sre Expert/`, `Worker/`, `Shared/`, `Test Mini/`, `Unassigned/`, `Forge Memory Truncation Fix/`, `Forge Ac06 Ac07 Messluecken/`

Das sind kein Planungs-Content sondern Worker-Data. Nicht durchsuchen für Plan-Context.

---

## Empfohlene Morgen-Reihenfolge (2026-04-19)

1. **Stabilization-Plan** (P0, ~4-5h) — bevor alles andere
2. Dann parallel:
   - **Pipeline-Tab-v3 Sprint 2** (UI-Finishing, Pixel)
   - **Task-Tab-v2 A1/A2** (FAILED-Counter + NBA-Regel, Forge)
3. Wenn beide durch:
   - **Worker-Hardening Pack 2** (Receipt-Sequence) — schließt Ghost-Fail-Root-Cause
   - **Costs-v2 Zone D** (Agent-Ladder)
4. Abends:
   - **Continuation-Orchestrator Pack B** (Seed-Konverter, für L3 Self-Improving)

---

## Anti-Drift: dieser Index wird gepflegt
Jede neue Plan-Creation oder Abschluss eines Plans = Update dieses Index. Alte Index-Files (`atlas_plans_index.md` in Memory) sind Pointer hierher.

## Stabilization & Pipeline Plans
| Date | Plan | Status |
|------|------|--------|
| 2026-04-19 | stabilization-plan-2026-04-19.md | Aktiv — Mo 09:00 start |
