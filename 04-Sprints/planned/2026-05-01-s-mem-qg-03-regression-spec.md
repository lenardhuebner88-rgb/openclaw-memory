# S-MEM-QG-03 — Regression Set + Review-Loop Spec
**Task:** S-MEM-QG-03-REGRESSION-SPEC  
**Owner:** Lens (efficiency-auditor)  
**Date:** 2026-05-01  
**Parent:** S-MEM-QUALITY-P1 (d9427be8)  
**Status:** done

---

## Evidence Baseline (2026-05-01)

| Signal | Value | Status |
|---|---|---|
| QMD total docs | 1982 | OK |
| QMD pending embedding | 18 | watch |
| memory-budget CRITICAL sessions | ~4-6/hr | FAIL |
| Root file count | 139 | watch |
| Backup/log noise at root | 23 | FAIL |
| Stale L2 files (>14d) | 0 | OK |
| L1 invariants count | 8 | OK |
| L2 working files | 17 recent | OK |

---

## REGRESSION_OUTPUT

### Regression Suite — Named Tests with Purpose + Threshold

#### Gate A — Retrieval Quality

| ID | Test Name | Purpose | Pass Threshold | Fail Threshold | Alert Level |
|---|---|---|---|---|---|
| R-RET-01 | Top-1 Precision | Ist das Top-1-Ergebnis bei Standard-Queries relevant? | ≥ 85% | < 80% | WARN |
| R-RET-02 | Top-3 Coverage | Sind die Top-3 Ergebnisse ausreichend? | ≥ 95% | < 90% | WARN |
| R-RET-03 | No-Match Rate | Wird korrekt "kein Treffer" geliefert, wenn nichts passt? | < 5% | ≥ 10% | CRITICAL |
| R-RET-04 | QMD Fallback Health | Funktioniert der direkte File-Read-Fallback wenn QMD hakt? | 100% | < 100% | CRITICAL |
| R-RET-05 | Embedding Lag | Sind neue Dokumente innerhalb von 24h indexiert? | ≤ 18 docs pending | ≥ 30 pending | WARN |

#### Gate B — Memory Hygiene

| ID | Test Name | Purpose | Pass Threshold | Fail Threshold | Alert Level |
|---|---|---|---|---|---|
| R-HYG-01 | Root Clutter | Keine Backup/Log-Dateien direkt im workspace root | ≤ 5 noise files | ≥ 10 noise files | WARN |
| R-HYG-02 | L2 Retention | Working-Memory-Dateien werden nach 14d archiviert | 0 files >14d active | ≥ 1 file >14d | CRITICAL |
| R-HYG-03 | L1/L2 Boundary | Invarianten ausschliesslich in L1, nie in L2 | 0 L1-invariants in L2 | any | CRITICAL |
| R-HYG-04 | Duplicate Rate | Keine ungeklaerten thematischen Duplikate in aktiven Notizen | 0 duplicates | ≥ 1 unresolved | WARN |
| R-HYG-05 | Decision Provenance | Jede dauerhafte Entscheidung hat einen Source-Pfad | 100% with path | < 100% | WARN |

#### Gate C — Operational Robustness

| ID | Test Name | Purpose | Pass Threshold | Fail Threshold | Alert Level |
|---|---|---|---|---|---|
| R-OPS-01 | Session Overflow Rate | CRITICAL session budget events pro Stunde | < 2/hr | ≥ 4/hr | CRITICAL |
| R-OPS-02 | QMD Index Health | Embedding-Backlog bleibt unter Schwelle | ≤ 18 pending | ≥ 30 pending | WARN |
| R-OPS-03 | Verify-After-Write Compliance | Memory-relevante Tasks haben verifizierende GET-Checks | 100% | < 100% | WARN |
| R-OPS-04 | MC Endpoint Responsiveness | /api/tasks responded in < 500ms | ≥ 95% | < 90% | WARN |

#### Gate D — 10/10 Readiness (Trend-based, 2+ cycles)

| ID | Test Name | Purpose | Pass Threshold | Fail Threshold | Alert Level |
|---|---|---|---|---|---|
| R-D10-01 | Regression Coverage | Alle 4 Gates haben min. 3 tests deployed | 100% coverage | < 100% | CRITICAL |
| R-D10-02 | Review Loop Adherence | Täglich/Weekly Reviews finden laut Cadence statt | ≥ 90% on-time | < 80% | WARN |
| R-D10-03 | Trend Improvement | Retrieval KPIs verbessern sich über 2 Review-Zyklen | improving | degrading | WARN |
| R-D10-04 | Drift Stability | Keine neuen Drift-Indikatoren über 72h | 0 new drift | ≥ 1 new | WARN |

---

## Review Loop Mechanics

### Daily Review (Lens + Atlas)

**Trigger:** Every business day at 09:00 Berlin  
**Owner:** Lens (data collection) → Atlas (review)  
**Runtime:** ≤ 5 min automated + 5 min human review

**Checks:**
1. Run `scripts/memory-quick-hygiene-check.py` → JSON report
2. Check `memory-budget.log` for CRITICAL events in last 24h
3. Check QMD pending-embedding count
4. Log summary to `memory/metrics/daily/YYYY-MM-DD.md`

**KPIs captured daily:**
- `critical_session_count_24h`
- `qmd_pending_docs`
- `root_noise_files`
- `stale_l2_count`

**Escalation (daily → Atlas):**
- R-OPS-01 CRITICAL (≥ 4 critical/hr): Atlas alert immediately, session review within 2h
- R-RET-03 CRITICAL: Lens investigates same day
- R-HYG-02 CRITICAL: Spark dispatched for same-day fix

---

### Weekly Review (Atlas + Lens)

**Trigger:** Monday 09:00 Berlin  
**Owner:** Atlas (chair) + Lens (presenter)  
**Runtime:** 30 min

**Agenda:**
1. Week-over-week KPI trend (retrieve from daily logs)
2. Gate A retrieval quality: Top-1 / Top-3 / No-Match rates
3. Gate B hygiene scorecard
4. Gate C operational health
5. Open action items from daily escalations
6. Update `vault/04-Sprints/planned/2026-05-01-s-mem-quality-p1.md` with findings

**KPIs reviewed weekly:**
- Retrieval trend (R-RET-01, R-RET-02, R-RET-03)
- Session overflow rate trend (R-OPS-01)
- Hygiene scorecard (R-HYG-01 to R-HYG-05)
- Regression set coverage (R-D10-01)

**Escalation (weekly → Operator):**
- R-D10-01 FAIL: regression set gaps require tool/script work
- 2+ consecutive weeks of R-OPS-01 > threshold: root-cause task dispatched
- Any CRITICAL persisted > 72h: P0 escalation

---

### Sprint Review (Atlas → Operator)

**Trigger:** End of Sprint (D7 for this sprint)  
**Owner:** Atlas  
**Scope:** Full scorecard against Gates A–D

**Pass criteria for sprint:**
- Gates A, B, C: all tests GREEN or ≤ 1 WARN (no CRITICAL)
- Gate D: R-D10-01 = GREEN, R-D10-02 ≥ 80%
- Trend: R-D10-03 must show improvement over 2 cycles

---

## Alerting + Escalation Matrix

| Alert Level | Condition | Channel | Owner | SLA |
|---|---|---|---|---|
| CRITICAL | R-OPS-01 ≥ 4/hr OR any hygiene CRITICAL | #alerts (Discord) | Atlas immediately | < 15 min |
| WARN | Any WARN threshold breached | #status-reports | Lens next business day | < 24h |
| INFO | R-HYG-01 at 5-9 files noise | memory log only | Spark next sprint | < 1 week |
| Operator Escalation | CRITICAL persisted > 72h OR R-D10-01 FAIL | #atlas-main + Telegram | Atlas | < 2h decision |

---

## Open Items / Residual Risks

1. **Exact thresholds for R-RET-01/02** — based on 1-day baseline; revisit after week 1 with more query data
2. **R-HYG-01 current state: 23 noise files** — needs Spark cleanup dispatch before gate can pass
3. **Session overflow (R-OPS-01) current: ~4-6/hr** — pre-existing; root-cause is separate P0 task already tracked
4. **Regression automation** — tests defined but not yet scripted; next action is to implement runner script

---

## Next Actions (from this spec)

| ID | Action | Owner | Priority | Definition of Done |
|---|---|---|---|---|
| NA-1 | Script R-RET-01 to R-RET-05 as automated test runner | Lens | P1 | `scripts/memory-regression-runner.py` exists, runnable, produces JSON |
| NA-2 | Dispatch Spark cleanup for R-HYG-01 (23 root noise files) | Atlas | P2 | Root noise ≤ 5 files |
| NA-3 | Session overflow root-cause P0 (already in board) | Forge | P0 | R-OPS-01 < 2/hr sustained |
| NA-4 | First daily review run (2026-05-02 09:00) | Lens | P1 | metrics logged to memory/metrics/daily/ |
| NA-5 | Week-1 threshold calibration for R-RET-01/02 | Lens | P2 | Thresholds confirmed with real query data |
