# S-MEM-QUALITY-P1 — Memory System 9/10 → 10/10

Status: planned (operator-review)
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