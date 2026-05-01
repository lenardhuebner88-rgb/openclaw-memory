# S-MEM-QUALITY-P1 — Memory System 9/10 → 10/10

Status: active (autonomous execution gestartet 2026-05-01)
Owner: Atlas
Taskboard-ID: b2655725-8f75-4451-ad90-f77c74d4655c
Datum: 2026-05-01

## Zielbild
- Kurzfristig (7 Tage): belastbare **9/10** Memory-Qualität im Tagesbetrieb.
- Langfristig (30–45 Tage): nachhaltige **10/10** mit stabilen Guardrails, Drift-Kontrolle und Auditierbarkeit.

## Messbare Qualitätsgates

### Gate A — Retrieval-Qualität (kurzfristig)
- Top-1 Relevanz bei Standard-Queries >= 85%
- Top-3 Abdeckung >= 95%
- No-Match-Rate < 5%
- Verifikation: Stichprobe über reale Operator-Queries + QMD-Proof

### Gate B — Memory-Hygiene (kurzfristig)
- L1 nur Invarianten, L2 nur Working-Memory (14d-kompatibel)
- 0 ungeklärte Duplikate in aktiven Working-Notizen
- Jede neue dauerhafte Entscheidung mit Source-Pfad abgelegt
- Verifikation: strukturierter Hygiene-Check + Spot-Audit

### Gate C — Operational Robustness (kurzfristig)
- 0 kritische Retrieval-Fehler über 72h
- QMD-Fallback-Pfad dokumentiert und getestet
- 100% Verify-after-write für Memory-relevante Tasks

### Gate D — 10/10 Readiness (langfristig)
- Delta-Review-Routine (täglich/woechentlich) etabliert
- Regression-Set für Memory-Queries vorhanden
- Sprint-Abschluss nur mit Trendverbesserung über mind. 2 Review-Zyklen

## Task-Zuweisung

### Atlas (Orchestrierung)
- Priorisierung, Abnahme der Gates, Final Scorecard
- Daily Decision Log für Memory-Policies

### Lens (Analyse)
- Query-Kohorten definieren (Procurement, SkyWise, Ops)
- Precision/Recall-basierte Auswertung der Retrieval-Treffer
- Drift-Indikatoren wöchentlich reporten

### Spark (Quick Fixes)
- Kleine Retrieval-/Tagging-Fixes
- Duplicate- und Naming-Cleanup in L2

### Forge (nur wenn nötig, low-risk)
- Stabilisierung von Tooling-Pfaden / Proof-Skripten
- Keine Restart/Config/Cron-Mutationen ohne separaten Approval-Task

## Arbeitspakete
1) Baseline messen (D0)
2) Quick-Wins für 9/10 (D1–D3)
3) 72h Stabilitätsfenster (D4–D6)
4) 10/10-Roadmap mit Guardrails (D7)

## Definition of Done (Sprint)
- Alle Gates A–C erfüllt (proof-backed)
- Scorecard dokumentiert (inkl. offener Rest-Risiken)
- 10/10-Roadmap inkl. Owner + Terminachsen im Vault
- Taskboard-Status auf done nur mit Evidenzlinks

## Risiken
- Kontextdrift durch ad-hoc Notizen ohne Layer-Regel
- QMD-Relevanzschwankungen bei unscharfen Queries
- Prioritätskonflikte mit parallelen P1/P0-Streams

## Nächster konkreter Schritt
- Child-Tasks für Lens/Spark erstellen und als bounded P2/P3 dispatchen (nach Operator-Go).

## 30-45 Tage Roadmap-Entwurf (Spark, S-MEM-QG-03)

### Milestone M0 (Tag 0-3) — Baseline + Instrumentation stabil
- Owner: Spark (Execution), Atlas (Abnahme)
- Cadence: täglich kurzer Proof-Check
- Entry Gate: Sprint aktiv, QMD + Memory-Pfade erreichbar
- Exit Gate:
  - Baseline-Report liegt vor (Top-1/Top-3/No-Match + Hygiene)
  - Quick-Hygiene-Proof lauffähig dokumentiert

### Milestone M1 (Tag 4-10) — Retrieval 9/10 sichern
- Owner: Lens (Qualitätsanalyse), Spark (Fix-Umsetzung), Atlas (Priorisierung)
- Cadence: täglich Query-Batch, 2x/Woche Review
- Entry Gate: M0 Exit erfüllt
- Exit Gate:
  - Top-1 >= 85%
  - Top-3 >= 95%
  - No-Match < 5%
  - dokumentierte Query-Kohorten (Procurement/SkyWise/Ops)

### Milestone M2 (Tag 11-21) — Guardrails + Drift-Kontrolle
- Owner: Atlas (Policy), Forge nur low-risk Tooling bei Bedarf
- Cadence: wöchentlich Drift-Review + täglicher Hygiene-Sweep
- Entry Gate: M1 Exit erfüllt
- Exit Gate:
  - Delta-Review-Routine aktiv (daily + weekly)
  - 0 ungeklaerte L2-Duplikate
  - Fallback-Pfad fuer QMD getestet + dokumentiert

### Milestone M3 (Tag 22-30) — Regression-Set produktionsnah
- Owner: Lens (Set-Design), Spark (Tagging/Naming-Fixes), Atlas (Sign-off)
- Cadence: 3x/Woche Regression-Lauf
- Entry Gate: M2 Exit erfüllt
- Exit Gate:
  - Regression-Set mit festen Abnahmequeries vorhanden
  - Trend über mindestens 2 Zyklen stabil/verbessert

### Milestone M4 (Tag 31-45) — 10/10 Readiness & Handover
- Owner: Atlas (Final Scorecard), Lens (Trendbeleg), Spark (Rest-Fixes)
- Cadence: wöchentlich Executive Review
- Entry Gate: M3 Exit erfüllt
- Exit Gate:
  - Gates A-C dauerhaft erfüllt
  - 72h ohne kritische Retrieval-Fehler
  - finale 10/10-Roadmap inkl. Owner+Terminen im Vault abgenommen

## D1-D3 Quick-Wins umgesetzt (Spark, S-MEM-QG-02)

### Win 1 — Hygiene-Proof Script eingefuehrt
- Neu: `scripts/memory-quick-hygiene-check.py`
- Output: `reports/memory-hygiene/2026-05-01-quickcheck.json`
- Zweck: root-clutter, backup/log-noise und L2 >14d Drift in einem schnellen Check messbar machen.

### Win 2 — Query-Naming vereinheitlicht
- Neu: `memory/working/QUERY-NAMING-QUICK-GUIDE.md`
- Zweck: bessere Retrieval-Treffer durch konsistente Domain/Intent-Pattern.

### Win 3 — Vor/Nach-Hinweis fuer Gate B
- Quickcheck-Resultat (2026-05-01):
  - `memory_root_file_count=139`
  - `backup_or_log_root_count=23`
  - `stale_working_count_gt14d=0`
- Interpretation:
  - Positiv: L2-Retention aktuell ohne >14d Drift.
  - Offene Hygiene-Chance: hoher Root-Noise durch Backup/Log-Dateien; priorisiert fuer naechsten Cleanup-Schritt.

## S-MEM-QG-03 Konsolidierung — 10/10 Guardrail-Roadmap (30-45 Tage)

Status: done (2026-05-01)
Owner: Atlas
Child-Artefakte:
- Roadmap: Abschnitt `30-45 Tage Roadmap-Entwurf (Spark, S-MEM-QG-03)` in diesem Dokument
- Regression: `vault/04-Sprints/planned/2026-05-01-s-mem-qg-03-regression-spec.md`

### Konsolidiertes Operating Model
- Daily 09:00 Berlin: Lens sammelt Regression-/Hygiene-/Budget-Signale; Atlas reviewt in <=10min.
- Weekly Monday 09:00 Berlin: Atlas + Lens prüfen Trend, offene Aktionen und Drift; Ergebnis ins Decision Log.
- Sprint D7: Atlas erstellt Full Scorecard gegen Gates A-D.

### 30-45 Tage Milestone-Pfad
- M0 Tag 0-3: Baseline + Instrumentation stabil; Exit: Baseline-Report + lauffähiger Hygiene-Proof.
- M1 Tag 4-10: Retrieval 9/10 sichern; Exit: Top-1 >=85%, Top-3 >=95%, No-Match <5%.
- M2 Tag 11-21: Guardrails + Drift-Kontrolle; Exit: Daily/Weekly Delta-Review aktiv, 0 ungeklärte L2-Duplikate, QMD-Fallback getestet.
- M3 Tag 22-30: Regression-Set produktionsnah; Exit: feste Abnahmequeries + positiver Trend über >=2 Zyklen.
- M4 Tag 31-45: 10/10 Readiness + Handover; Exit: Gates A-C sustained, 72h keine kritischen Retrieval-Fehler, Final Scorecard abgenommen.

### Regression-Set Summary
- 17 Tests über 4 Gates: Retrieval (5), Hygiene (5), Ops (4), 10/10 Readiness (4).
- Bekannte aktuelle FAILs: R-HYG-01 Root Noise (23 Dateien), R-OPS-01 Session Overflow (~4-6 CRITICAL/hr; separater P0-Track).
- Nächste bounded Follow-ups: Regression runner, Root-noise cleanup, Retrieval threshold calibration, erster Daily Review Run.
