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

## 🆕 TODAY 2026-04-21 — Pipeline-Tab Quick-Wins (Audit + Fix-Sprint)

### Plan + Sprint-Dispatch
- **`pipeline-tab-quickwins-plan-2026-04-21.md`** — Audit gegen Live-Pipeline-Tab + 4-Phasen-Fix-Plan (ca. 10 Tasks, ~2 AT Aufwand). Adressiert 3 P0-Daten-Falschdarstellungen (KPI-Subtitle lügt, Zeitfilter auf falschem Feld, currentStage≠status), 5 P1-UI-Widersprüche, 3 P2-Performance-Punkte.
- **`pipeline-tab-quickwins-atlas-dispatch-2026-04-21.md`** — Copy/Paste-Prompt für Atlas-Sprint-Start. Pre-Flight-Gate, Phasenreihenfolge, Acceptance-Tests.

**Trigger:** *Lade `pipeline-tab-quickwins-plan-2026-04-21.md` und starte Sprint-N Pipeline-Tab Quick-Wins.*

---

## 🆕 TODAY 2026-04-19 — Stabilization + Memory-Level-Up

Operator-direkte Session (pieter_pan ohne Atlas, wegen R30 Atlas-Orphan). Alle Deliverables dieser Session sind hier gebündelt.

### Reports & RCAs (chronologisch)
- **`e2e-worker-audit-report-2026-04-19.md`** — 5-Scenario-Audit (76/76 done mit resultSummary, 4 Ghost-Fails als Gateway-Issue identifiziert)
- **`e2e-live-worker-test-2026-04-19.md`** — 15/15 PASS API-Contract-Test (Naming, Lifecycle, Receipt-Sequence, Operator-Lock persist)
- **`atlas-remaining-plan-2026-04-19.md`** — Sprint-2 ENRICHED + Sprint-3 Spec nach no-go Sprint-1
- **`sprint-2-3-autonomous-report-2026-04-19.md`** — Atlas-Autonomous-Run Ergebnis: Sprint-1 no-go-close, Sprint-2 partial (3/5 deployed), Sprint-3 full done (A1+A2+Pipeline-v3 Sprint 2)
- **`final-report-autonomous-run-2026-04-19.md`** — End-of-Run Summary + R30-Incident-Recovery
- **`rca-2026-04-19-incident-cluster.md`** — Deep RCA der 7 Incident-Klassen + 5-Schichten-Analyse + 5 Minimal-Fixes + Roadmap
- **`stabilization-day-2026-04-19.md`** — 6 Fixes deployed: PR #68846 cherry-pick, Stall 2/5min, R37-Markers, Healthcheck-URL, Atlas-Orphan-Detect-Cron, MCP-Reaper-Alert
- **`memory-system-level-up-2026-04-19.md`** — QMD-Integration (3 Collections, 1042 docs indexed, MCP :8181) + Cost-Guard Dreaming + Session-Maintenance enforce

### Deployed Fixes (Code + Config)
| # | Deliverable | File | Backup |
|---|---|---|---|
| F1 | Stall-Thresholds 10/30 → 2/5 min | `worker-monitor.py` L49-50 | `.bak-2026-04-19-stall-fix` |
| F2 | Gateway-Healthcheck /api/health → /healthz | `worker-monitor.py` L2039 | (inkl. F1) |
| F3 | PR #68846 cleanupBundleMcpOnRunEnd | `attempt-execution.runtime-*.js:371` | `.bak-2026-04-19-pr68846` |
| F4 | R37 REAL_TASK + ORCHESTRATOR_MODE Markers | `auto-pickup.py` trigger_worker() | `.bak-2026-04-19-r37` |
| F5 | MCP-Reaper Discord-Alert | `mcp-taskboard-reaper.sh` | (inline edit) |
| F6 | Atlas-Orphan-Detect-Cron | `atlas-orphan-detect.sh` (NEW) | (new file) |
| F7 | Session-Maintenance enforce + 500MB/150 entries cap | `openclaw.json`.session.maintenance | `.bak-2026-04-19-session-maintenance` |
| F8 | QMD collections + MCP-Daemon + memory.qmd config | `openclaw.json`.memory.qmd + mcp.servers.qmd | `.bak-2026-04-19-qmd-integrate` |
| F9 | Dreaming cost-guard: phase-limits light=30/deep=10/rem=5 | `openclaw.json`.plugins.entries.memory-core | (inkl. F8) |
| F10 | Agent defaults.memorySearch.qmd extraCollections | `openclaw.json`.agents.defaults.memorySearch | (inkl. F8) |

### Crons Added / Modified
| Cron | Schedule | Purpose |
|---|---|---|
| **openclaw sessions cleanup** | `0 */6 * * *` | Session-Maintenance enforcement |
| **qmd update** | `*/30 * * * *` | QMD re-index refresh |
| **qmd mcp --daemon (respawn)** | `@reboot` | QMD MCP-Daemon auto-start |
| **atlas-orphan-detect.sh** | `*/10 * * * *` | R39 Atlas-Orphan-Detection |
| **dreaming-cost-guard.sh** | (manual) | External circuit-breaker (Issue #65550) |
| **mcp-taskboard-reaper.sh (existing)** | `*/15 * * * *` | + NEW Discord-Alert on kill |

### Rules R38/R39/R40 (neu)
- **R38** MCP-Zombie-Defense-in-depth (existierender Reaper + Discord-Alert Patch)
- **R39** Atlas-main braucht Session-Resume-Pattern (CLI ist One-Shot)
- **R40** Stall-Thresholds sind Kern-Infra (2/5min nicht 10/30min)

### System-State at Session-End
- MC: 200 OK, active
- Gateway: 200 OK, RSS 1.5 GB (Peak war 4.3 GB im Incident, danach clean)
- QMD-MCP-Daemon: :8181 live, 1042 docs indexed (BM25)
- Session-Usage: main 410 MB (war 705 MB, -42%)
- Patch-Tracker: `/home/piet/.openclaw/patches/PR68846-applied.md`

### Trigger-Phrases für heute aktive Content
- *"Lade Stabilization-Day 2026-04-19 Report"* → `stabilization-day-2026-04-19.md`
- *"Lade RCA Incident-Cluster"* → `rca-2026-04-19-incident-cluster.md`
- *"Lade Memory-Level-Up"* → `memory-system-level-up-2026-04-19.md`
- *"Zeige mir alle today's Fixes"* → Query via QMD: `qmd search '2026-04-19 fix' -n 10`

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


---

## 🗓️ Added 2026-04-19 (Sprint-Cluster-Day)

Massive Day: **Sprint-E (Board UX), F (Ops-Inventory), G (Scheduler+Ops-Dashboard), H (Atlas Analytics), J (Cascade Post-Mortem), Memory-Level-3 Deployments, 5 new Rules R45-R49.**

### Sprint-Plans + Endreports

| Doc | Scope | Status |
|---|---|---|
| `atlas-sprints-abc-plan-2026-04-19.md` | Sprint-A+B+C planning | done |
| `atlas-board-ux-levelup-phase2-plan-2026-04-19.md` | Sprint-E Planning | done |
| `sprint-abc-real-endreport-2026-04-19.md` | Sprint-ABC Endreport | done |
| `sprint-abc-final-report-2026-04-19.md` | Sprint-ABC Final | done |
| `board-ux-levelup-plan-2026-04-19.md` | Sprint-D Planning | done |
| `sprint-e-final-report-2026-04-19.md` | Sprint-E Endreport | Atlas-written, E1-E5 |
| `ops-inventory-plan-2026-04-19.md` | Sprint-F Planning | F1+F2 autonomous |
| `sprint-f-f3-synthesis-sprint-g-plan-2026-04-19.md` | Sprint-F→G bridge | done |
| `sprint-h-board-analytics-plan-2026-04-19.md` | Atlas Sprint-H Analytics | done autonomous |
| `sprint-h-h1-rca-2026-04-19.md` | H1 False-Failure RCA | **R45 Live-Case** |
| `autonomous-cascade-endreport-sprints-efgh-2026-04-19.md` | Mega-Endreport E+F+G+H | 199 Zeilen |
| `sprint-j-cascade-postmortem-plan-2026-04-19.md` | Sprint-J Governance | done |
| `sprint-j-j5-infra-files-preclassification-2026-04-19.md` | J5 Forge-Helper | used |
| `sprint-gh-consolidation-report-2026-04-19.md` | Forge 4-commit consolidation | done |
| `sprint-i-mobile-polish-plan-2026-04-19.md` | Sprint-I v2 in-depth | **RUNNING now** (Trigger "Atlas nun nächster Sprint follow #42") |
| `sprint-k-infra-hardening-plan-2026-04-19.md` | Sprint-K (renamed from H) | queued |
| `sprint-k-dispatch-prompt-2026-04-19.md` | Sprint-K ready-to-fire | ready |
| `sprint-l-memory-kb-compilation-plan-2026-04-19.md` | Sprint-L Memory-L3 | **MVPs deployed** (L1-L6) |

### Governance + Rules

| Doc | Purpose |
|---|---|
| `r47-scope-lock-design-2026-04-19.md` | R47 3-Layer-Enforcement Design (Forge J2) |
| `cron-audit-2026-04-19.md` | **338 Zeilen** Deep-Audit 51 schedules + best-practice-research (systemd vs cron + Kestra) |
| `infra-files-cleanup-2026-04-19.md` | Forge J5 per-file disposition report |

### Research Reports

| Doc | Agent | Topic |
|---|---|---|
| `james-operator-dashboard-research-v2-2026-04-19.md` | James | Sprint-D Best-in-Class UX research |
| `james-mobile-typography-system-2026-04-19.md` 🆕 | James | **Sprint-I I2 typography pre-audit** |
| `lens-mobile-ui-audit-2026-04-19.md` | Lens | Sprint-D Playwright mobile audit |
| `lens-script-inventory-audit-2026-04-19.md` | Lens | Sprint-F F1 86-scripts catalog |
| `lens-g2-alert-dedupe-2026-04-19.md` | Lens | Sprint-G G2 alert dedupe chain |
| `lens-route-state-coverage-audit-v2-2026-04-19.md` 🆕 | Lens | **Sprint-I I3 state-coverage pre-audit** |
| `forge-scheduler-graph-audit-2026-04-19.md` | Forge | Sprint-F F2 scheduler graph |
| `forge-g1-broken-scheduler-fix-2026-04-19.md` | Forge | Sprint-G G1 broken scheduler fix |

### Memory-Level-3 Assets

| Doc / Asset | Scope |
|---|---|
| `kb/*.md` | **10 Karpathy-KB articles** (Sprint-L L1) — sprint-orchestration, receipt-discipline, deploy-contracts, atlas-hallucination-prevention, board-hygiene, memory-architecture, scope-governance, sub-agent-coordination, incident-response, build-deploy-regeln |
| `memory-dashboard.md` | **Static L6-Lite Portal** — auto-refresh 04:30 UTC, 237 Zeilen (Stack-Overview, Rules, Facts, KB, Graph, Retrieval, Budget, Crons, Reflections) |
| `atlas-snapshots/` | **L5-Deep Atlas-State-Snapshots** — für post-/reset-recovery |

### Infra-Docs (in workspace/, not Vault)
- `workspace/memory/SCHEMA.md` — canonical facts v2 + rules schema docs
- `workspace/memory/graph.jsonl` — 1024 memory-graph edges
- `workspace/HEARTBEAT.md` Section "Cron-Inventory" (218→377 Zeilen)
- `workspace/memory/rules.jsonl` — 49 rules (R1-R49)

---

## Trigger-Phrases (2026-04-19)

- **"Atlas nun nächster Sprint follow #42"** → Sprint-I Mobile-Polish v2 (currently RUNNING)
- **"Atlas Sprint-K Infra-Hardening starten"** → Sprint-K (queued after Sprint-I)
- **"Atlas Sprint-L Memory-KB starten"** → Sprint-L Deep (Forge, optional — MVPs already deployed)

## Anti-Drift Update

40+ neue Vault-Docs heute. Index-Maintenance: diese Section wird bei Sprint-K H10 in einen Index-Generator überführt (`vault-index-generator.py`, analog `memory-dashboard-generator.py`).
