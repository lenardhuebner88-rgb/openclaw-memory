---
title: Mission Control Vault — Master Index
date: 2026-04-22
maintained-by: Operator (manuell; auto-generator geplant in S-GOV T9)
purpose: Single Source of Truth für alle aktiven Sprint-Pläne, Cross-Synergien, Owner-Matrix, Overlap-Matrix.
previous-version: _VAULT-INDEX.md.pre-2026-04-22.bak
---

# Vault Master Index — 03-Agents/

## Wie lesen
- **PLANNED** = Plan im Ordner `sprints/`, noch nicht gestartet
- **RUNNING** = Aktuell in Execution
- **DONE** = Abgeschlossen
- **REFERENCE** = Source-Plan für konsolidierten Sprint (historical record)
- **TBD** = Operator-Review nötig (ist das noch relevant?)
- **ARCHIVED** = superseded oder obsolet, in `archive/2026-04/`

Trigger-Phrases: *"Lade `sprints/s-<id>-2026-04-22.md` und starte Sprint S-\<ID\>"*

---

## 🎯 Active Sprints 2026-04-22 (konsolidiert + live-geprüft)

| Sprint-ID | Plan-Doc | Priority | Owner (primary) | Depends-on | Enables | Status |
|---|---|---|---|---|---|---|
| **S-FND** | `sprints/s-fnd-2026-04-22.md` | P0-blocker | Forge + Operator | — | all others | PLANNED |
| **S-RELIAB-P0** | `sprints/s-reliab-p0-2026-04-22.md` | P0 | Forge | S-FND T2+T3 | S-RELIAB-P1, S-INFRA | PLANNED |
| **S-CTX-P0** | `sprints/s-ctx-p0-2026-04-22.md` | P0 | Atlas + Forge | — | S-CTX-P1 | PLANNED |
| **S-RPT** | `sprints/s-rpt-2026-04-22.md` | P1 | Codex + Forge | S-FND T1 | S-GOV, S-RELIAB-P1 Receipt-Chain | PLANNED |
| **S-GOV** | `sprints/s-gov-2026-04-22.md` | P1 | Lens → Atlas → Forge | — (Lens-Review intrinsisch Blocker) | S-RELIAB-P1, S-INTEG-W1 | PLANNED |
| **S-UX** | `sprints/s-ux-2026-04-22.md` | P2 | Forge + Pixel | S-FND T2 | — | PLANNED |
| **S-INFRA** | `sprints/s-infra-2026-04-22.md` | P1 | Forge + Operator + Atlas | S-RELIAB-P0 T2 | — | PLANNED |
| **S-INTEG-W1** | `sprints/s-integ-w1-2026-04-22.md` | P1-strategic | Operator + Forge | S-FND T3 + 7d Pre-Flight | S-INTEG W2-W4 | PLANNED |

## 🚀 Empfohlene Dispatch-Reihenfolge (strikt sequentiell)

1. **S-GOV T0** Lens-Review abschließen (Blocker)
2. **S-FND** Foundation-Bausteine (parallel zu 1)
3. **S-UX** (lowest risk, schnellster Ship)
4. **S-RPT**
5. **S-RELIAB-P0**
6. **S-INFRA** (nach S-RELIAB T2 merged)
7. **S-CTX-P0**
8. **S-INTEG-W1** (nach Windows-SSHFS 7d Pre-Flight)

Parallelisierbar: S-GOV M9/M10 Spikes (T7/T8) während 4-7.

---

## 🔗 Cross-Sprint-Synergien (1× bauen, mehrfach nutzen)

| Building-Block | Gebaut in | Konsumiert von |
|---|---|---|
| **Pydantic `SprintOutcome`-Schema v1** | S-FND T1 | S-RPT T2/T3, S-RELIAB-P1 Receipt-Chain, S-GOV Registry, S-INTEG-W1 T3 |
| **attemptId workflow-ID (sha256)** | S-FND T2 | S-RELIAB-P0 T3, S-UX T1 stateTransitions, S-INFRA T5 FSM-Stall |
| **Config-Integrity-Gate** (validate→snapshot→apply→probe→revert) | S-FND T3 | S-RELIAB-P0 T4/T5 (MemoryTiering/crontab), S-INFRA T4 Saga-Rollback, S-INTEG-W1 T5 Schema-Gate-Hook, S-GOV T2/T3 Drift-Fixes |
| **OpenTelemetry-Spine** | S-FND T4 (MVP) + S-GOV T8 (Proof-Crons) | S-INTEG-W4 (Dashboard), zukünftige Defense-Cron-Erweiterungen |

---

## ⚠️ Overlap-Matrix — Was kollidiert, wenn man nicht koordiniert

| Sprint-A | Sprint-B | Overlap-Punkt | Koordinationsregel |
|---|---|---|---|
| S-RELIAB-P0 T2 Single-Owner pending-pickup | S-INFRA T2 Worker-Monitor Receipt-Discipline | Beide patchen `worker-monitor.py` | **Gemeinsam** implementieren: S-RELIAB T2 → merge → S-INFRA T2 baut drauf auf |
| S-RELIAB-P0 T1 `pickup_claimed`-State | S-INFRA T5 FSM-Stall für `assigned` | State-Machine Konsistenz | FSM-Definition in `worker-fsm.yaml` (S-INFRA T5) muss S-RELIAB T1 States enthalten |
| S-UX T1 stateTransitions | S-RELIAB-P0 T3 attemptId-Integration | stateTransitions beinhaltet attemptId | S-UX T1 wartet auf S-FND T2 + S-RELIAB T3 merged |
| S-CTX-P0 T2 Baseline | S-INFRA T1 Prompt-Preamble | +200-500 Tokens Overhead | S-INFRA T1 Delta wird in S-CTX Baseline gemessen |
| S-RPT T1 Reader-Hygiene | Board-next-action.ts-Consumer | Dual-Path 7d-Soak | Feature-Flag `GOV_SIGNAL_SOURCE=strict|legacy|both` |

---

## 👥 Owner-Matrix

| Owner | Sprint-Verantwortlichkeit |
|---|---|
| **Operator** | S-FND T3 (Config-Gate), S-RELIAB-P0 T4/T5 (MemoryTiering/Reaper), S-GOV T0-T6 (außer T4), S-INFRA T4 (Saga), S-INTEG-W1 T0-T3 |
| **Atlas** | S-FND orchestration, S-RELIAB-P0 T8 (Chaos-Test), S-CTX-P0 T2/T7 (Baseline/Scoring), S-RPT T4 (Backfill), S-GOV T1/T10 (Closeout/Abort-Criterion), S-INFRA T1 (Preamble), S-INTEG-W1 T4 (Cache-Warming) |
| **Forge** | S-FND T1/T2/T4 (Schema/attemptId/OTEL), S-RELIAB-P0 T1-T3+T6-T7 (Worker-Refactor+MCP), S-CTX-P0 T3-T6 (API-Patches), S-RPT T2/T3/T5 (Schema-Integration), S-GOV T4/T7-T9, S-UX T1/T2/T3/T6/T7, S-INFRA T2/T3/T5, S-INTEG-W1 T5 |
| **Pixel** | S-UX T4 (Stale-Agent) + T5 (Data-Confidence-Meter) |
| **Codex** | S-RPT T1 (Reader-Hygiene, Operator-Modus) |
| **Lens** | S-GOV T0 (Review-Blocker!) |

---

## ⏳ Ongoing / Long-Running (nicht in Sprint-Scope)

- **Sprint-L Memory-KB** (`sprint-l-memory-kb-compilation-plan-2026-04-19.md`) — L1-Finalize läuft, MVPs deployed. *Nicht anfassen* laut S-CTX-Abgrenzung.
- **S-MIGR Minions-Migration** (watch-doc `minions-migration-plan.md`) — `minions-pr-watch.sh` Cron tracked PR #68718. Dispatcht bei merge → ersetzt R37/R38/R39/R40.
- **S-RELIAB-P1** (geparkt) — F3 retry-race, F4 Signed Receipt-Chain, F5-F8, P2 Heap-Profiling, P3 Upstream-PRs
- **S-CTX-P1** (geparkt) — CE5 Hard-Truncate+25KB-Cap+mem://, CE6 JSON-Discipline, CE7 Autoread-JIT, CE9 Top-3-Report, CE10 Regression-Cron
- **S-INTEG W2-W4** (geparkt) — Slash-Commands, Claude Design (wartet Anthropic), Observability-Dashboard

---

## ❓ Operator-Decision-Pending (TBD)

Die folgenden Alt-Pläne stehen noch im Repository, haben aber keine aktive Dispatch-Zuordnung. Entscheidung: archivieren, in neuen Sprint integrieren, oder weiter eigenständig?

| Doc | Letzter Edit | Offene Items | Empfehlung |
|---|---|---|---|
| `atlas-board-operator-cockpit.md` | 2026-04-17 | Phase 2 Navigation-Refactor (13→7 Tabs), Zone C/D | **Prüfen ob Scope nach S-UX noch steht** |
| `atlas-costs-cockpit-v2.md` | 2026-04-17 | Zone D Agent-Ladder | **Prüfen ob Backend-API dafür schon existiert** |
| `atlas-continuation-orchestrator.md` | 2026-04-17 | Pack B (Seed-Konverter), E (Cron live), F (Retry-Eskalation) | **Wahrscheinlich Großteil durch Sprint-M obsolet** |
| `2026-04-18_mission-control-task-tab-plan-v2.md` | 2026-04-18 | A1 FAILED-Counter, A2 NBA-Regel | **Ist A1/A2 noch gewollt oder überholt?** |

---

## 📘 Reference / Source-Plans (historical record)

Diese Pläne wurden in die konsolidierten Sprints integriert. Sie bleiben als historische Quelle — nicht mehr als "aktive Pläne" behandeln.

### Source für S-RELIAB-P0
- `worker-system-hardening-plan-2026-04-21.md` (F1-F8)
- `atlas-stabilization-plan-mcp-recovery-2026-04-21.md` (P0-P3)
- `sprint-n-e2e-stabilization-2026-04-22.md` (M1-M3)
- `auto-pickup-open-run-guard-fix-2026-04-21.md`
- `atlas-handover-live-failed-task-2026-04-21.md`

### Source für S-CTX-P0
- `sprint-ce-context-efficiency-2026-04-21.md` (CE1-CE10)
- `context-overflow-fix-plan-2026-04-20.md` + `context-overflow-fix-abschluss-2026-04-20.md`

### Source für S-RPT
- `sprint-reporting-next-action-hardening-plan-2026-04-21.md`
- `atlas-sprint-reporting-trigger-2026-04-21.md`

### Source für S-GOV
- `sprint-m-audit-integrity-scheduler-consolidation-plan-2026-04-20-v1.2.1.md` (v1.2.1 canonical)
- `sprint-m-session-closeout-and-forge-verification-2026-04-21.md`
- `sprint-m-followup-status-2026-04-21.md`
- `sprint-m-v1.2-session-handover-2026-04-21.md`
- `sprint-m-night-report-2026-04-21-0022.md`
- `codex-review-sprint-m-2026-04-20-2256.md`
- `codex-review-prompt-sprint-m-LINUX.md`
- `cron-catalog-2026-04-20.md`
- `openclaw-cron-heartbeat-analysis-2026-04-20.md`
- `cron-audit-2026-04-19.md`

### Source für S-UX
- `pipeline-tab-quickwins-plan-2026-04-21.md` (P0/P1/P2)
- `pipeline-tab-quickwins-atlas-dispatch-2026-04-21.md`
- `pipeline-quickwins-monitor-log-2026-04-21.md`
- `sprint-m-p1-pixel-delta-report-2026-04-20.md`
- `pixel-p1-dispatch-plan-2026-04-20.md`
- `pixel-p1-pre-flight-analysis-2026-04-20.md`

### Source für S-INFRA
- `sprint-k-infra-hardening-plan-2026-04-19.md` (H6/H7/H10 — H6 L2 + H7 + H10 L1 already done; H10 L2-L5 superseded)
- `sprint-k-dispatch-prompt-2026-04-19.md`
- `sprint-k-h9-contrast-audit-report-2026-04-20.md`
- `sprint-k-h11-session-lock-governance-report-2026-04-20.md`
- `sprint-k-h12-board-state-machine-fix-report-2026-04-20.md`
- `sprint-k-h13-defense-layers-report-2026-04-20.md`

### Source für S-INTEG-W1
- `claude-code-openclaw-integration-roadmap-2026-04-20.md`

### Foundation-References
- `atlas-session-memory-operating-model.md` — Foundation Session-Types
- `spark-agent-display-guide-2026-04-18.md` — Agent-UI-Signaturen
- `memory-system-level-up-2026-04-19.md` — Memory-Architecture L1-L6
- `memory-dashboard.md` — Auto-generiert L6-Lite Portal
- `safeguard-verify-2026-04-19.md`
- `atlas-weakness-audit-2026-04-17.md`
- `r47-scope-lock-design-2026-04-19.md`
- `minions-migration-plan.md` — S-MIGR watch-doc

---

## 📊 Research & Audit Reports (archival)

### Research-Snapshots (Agents)
- `james-operator-dashboard-research-2026-04-18.md`
- `james-operator-dashboard-research-v2-2026-04-19.md`
- `james-navigation-patterns-2026-04-18.md`
- `james-mobile-typography-system-2026-04-19.md`
- `lens-mobile-ui-audit-2026-04-19.md`
- `lens-g2-alert-dedupe-2026-04-19.md`
- `lens-script-inventory-audit-2026-04-19.md`
- `lens-route-state-coverage-audit-v2-2026-04-19.md`
- `forge-scheduler-graph-audit-2026-04-19.md`
- `forge-g1-broken-scheduler-fix-2026-04-19.md`
- `spark-overview-hero-concept-2026-04-18.md`
- `spark-mobile-ui-audit-2026-04-18.md`
- `spark-cost-story-modal-interaction-2026-04-18.md`
- `spark-cost-story-ux-concept.md`
- `spark-pending-pickup-recovery-research.md`

### RCA / Audit Reports
- `rca-2026-04-19-incident-cluster.md`
- `morning-recovery-report-2026-04-20.md`
- `atlas-weakness-audit-2026-04-17.md`
- `infra-files-cleanup-2026-04-19.md`
- `e2e-worker-audit-report-2026-04-19.md`
- `e2e-live-worker-test-2026-04-19.md`
- `cost-anomaly-analysis-2026-04-19.md`
- `DREAMS-2026-04-20.md` (L2 Dreaming output)
- `dreaming-verify-2026-04-20.md`
- `qmd-openrouter-embed-plan-2026-04-20.md` + `...abschlussbericht...`

### End-of-Day / Multi-Sprint-Reports (archival, für history)
- `atlas-session-report-2026-04-18-morning.md`
- `atlas-session-report-2026-04-18-evening.md`
- `atlas-stabilization-sprint-2026-04-18.md`
- `atlas-mc-board-tab-expansion-2026-04-18-evening.md`
- `atlas-verify-consolidation-2026-04-18-night.md`
- `2026-04-18_night_3h_active_sprint.md`
- `stabilization-day-2026-04-19.md`
- `sprint-2-3-autonomous-report-2026-04-19.md`
- `final-report-autonomous-run-2026-04-19.md`
- `sprint-abc-final-report-2026-04-19.md`
- `sprint-abc-real-endreport-2026-04-19.md`
- `atlas-sprints-abc-plan-2026-04-19.md`
- `sprint-e-final-report-2026-04-19.md`
- `sprint-f-f3-synthesis-sprint-g-plan-2026-04-19.md`
- `sprint-h-board-analytics-plan-2026-04-19.md`
- `sprint-h-h1-rca-2026-04-19.md`
- `sprint-i-comprehensive-mobile-audit-2026-04-19.md`
- `sprint-i-mobile-polish-plan-2026-04-19.md`
- `sprint-j-cascade-postmortem-plan-2026-04-19.md`
- `sprint-j-j5-infra-files-preclassification-2026-04-19.md`
- `sprint-gh-consolidation-report-2026-04-19.md`
- `autonomous-cascade-endreport-sprints-efgh-2026-04-19.md`
- `end-of-day-report-2026-04-19.md`
- `board-ux-levelup-plan-2026-04-19.md`
- `atlas-board-ux-levelup-phase2-plan-2026-04-19.md`
- `ops-inventory-plan-2026-04-19.md`
- `sprint-l-memory-kb-compilation-plan-2026-04-19.md`
- `sprint-n-sprint-o-closure-2026-04-20.md`

---

## 🗄️ Archive 2026-04

`vault/03-Agents/archive/2026-04/` (13 Docs):

1. `atlas-worker-system-hardening.md` (v-2026-04-17 → superseded by `worker-system-hardening-plan-2026-04-21.md` + S-RELIAB-P0)
2. `atlas-stabilization-plan-2026-04-19.md` → superseded by `atlas-stabilization-plan-mcp-recovery-2026-04-21.md` + S-RELIAB-P0
3. `2026-04-18_pipeline-tab-plan-v3.md` → superseded by `pipeline-tab-quickwins-plan-2026-04-21.md` + S-UX
4. `2026-04-18_mission-control-pipeline-tab-2-sprints.md` (v1, v3 supersedes)
5. `2026-04-18_mission-control-task-tab-plan.md` (v1, v2 supersedes)
6. `sprint-m-audit-integrity-scheduler-consolidation-plan-2026-04-20.md` (v1.0)
7. `sprint-m-audit-integrity-scheduler-consolidation-plan-2026-04-20-v1.1.md` (v1.1)
8. `sprint-m-audit-integrity-scheduler-consolidation-plan-2026-04-20-v1.2.md` (v1.2)
9. `stabilization-plan-2026-04-19.md` (Duplikat von atlas-stabilization-plan; 3.8 KB vs. 7.9 KB — geringerer war verwaister Entwurf)
10. `plan-2026-04-20.md` (Morgen-Plan vom 20.04., obsolet)
11. `atlas-remaining-plan-2026-04-19.md` (superseded)
12. `atlas-next-level-plan-2026-04-19.md` (superseded by stabilization-plan)
13. `pipeline-tab-phase1-atlas-dispatch-2026-04-21.md` (Phase 1 dispatched+complete, konsolidiert in S-UX)

---

## 🗂️ Lokale Memory-Files

Directory: `C:\Users\Lenar\.claude\projects\C--Users-Lenar-Neuer-Ordner\memory\`

- `MEMORY.md` (master-index, persistent über /compact)
- `session_2026-04-19_full_day.md` + `session_2026-04-18_full_day.md`
- `feedback_system_rules.md` (R1-R50)
- `atlas_plans_index.md` (pointer hierher)
- `monitoring_2026-04-18_night.md` + `monitoring_2026-04-19_morning.md`
- 7 Archiv-Files (Sessions/Incidents 2026-04-16/-17)

---

## 🔧 Maintenance-Prinzip

- **`_VAULT-INDEX.md`** = Single-Entry-Point (Ziel: <15 KB)
- **`sprints/s-*.md`** = canonical active plans, YAML-frontmatter + status-field
- **`archive/2026-04/`** = superseded, nur für history-lookup
- **Source-plans bleiben im Root** (historical record, referenced im Frontmatter der neuen Sprints)
- Neue Sprint-Dispatches = Frontmatter-status `RUNNING`
- Sprint-Close = Frontmatter-status `DONE` + eventuell move zu `archive/done/` (später)
- S-GOV T9 **Vault-Index-Generator** wird diesen Index frontmatter-driven auto-generieren

## 🕒 Changelog

- **2026-04-22**: Full re-write. 13 superseded Docs archiviert, 8 dedizierte Sprints in `sprints/`, Owner-Matrix + Overlap-Matrix + Cross-Synergies eingefügt.
- **2026-04-21**: (siehe `_VAULT-INDEX.md.pre-2026-04-22.bak`)
