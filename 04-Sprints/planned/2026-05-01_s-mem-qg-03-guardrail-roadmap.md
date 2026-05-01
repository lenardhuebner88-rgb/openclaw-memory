# S-MEM-QG-03 — 10/10 Guardrail Roadmap (30–45 Tage)

Stand: 2026-05-01
Owner: Atlas (orchestrator)
Parent Task: d9427be8-b613-46b1-8251-cf9465d0f41c

## Milestones + Owner + Gates

### M0 (Tag 0–3): Baseline & Governance Freeze
- Owner: Atlas + Lens
- Deliverables:
  - Finalisierte KPI-Baseline (Top-1/Top-3/No-Match, Hygiene, Ops-Robustness)
  - Feste Query-Kohorten (Procurement, SkyWise, Ops)
- Exit-Gates:
  - KPI-Baseline im Vault dokumentiert
  - Daily/Weekly Review-Owner benannt

### M1 (Tag 4–10): 9/10 Stabilisierung absichern
- Owner: Spark + Atlas
- Deliverables:
  - Root-noise Cleanup-Backlog priorisiert
  - Verify-after-write Nachweisquote 100% auf Memory-relevanten Tasks
- Exit-Gates:
  - L2 Drift >14d bleibt bei 0
  - Hygiene-Quickcheck in zwei Läufen ohne neue kritische Funde

### M2 (Tag 11–20): Regression Set v1 aktiv
- Owner: Lens
- Deliverables:
  - Regression-Query-Set (mind. 20 Queries) mit Soll-Expected-Hits
  - Schwellenwerte pro Testfall (pass/warn/fail)
- Exit-Gates:
  - Top-1 >=85% und Top-3 >=95% über Regression-Lauf
  - No-Match <5%

### M3 (Tag 21–30): Drift- und Alarm-Pfad härten
- Owner: Forge (nur low-risk tooling) + Atlas
- Deliverables:
  - Automatischer Drift-Report (wöchentlich)
  - Eskalationspfad bei KPI-Verletzung (owner + Reaktionszeit)
- Exit-Gates:
  - 0 kritische Retrieval-Fehler über 7 Tage
  - Fallback-Pfad dokumentiert und getestet

### M4 (Tag 31–45): 10/10 Readiness-Abnahme
- Owner: Atlas (Abnahme)
- Deliverables:
  - Zwei vollständige Review-Zyklen mit Trendverbesserung
  - Abschluss-Scorecard inkl. Restrisiken + Next Actions
- Exit-Gates:
  - Alle Gates A–D erfüllt
  - Taskboard Abschluss nur mit Evidence-Links

## Regression Set (v1)

1. Retrieval-Precision-Set
- KPI-1: Top-1 Relevanz >=85%
- KPI-2: Top-3 Abdeckung >=95%
- KPI-3: No-Match-Rate <5%

2. Hygiene-Set
- KPI-4: L2 stale >14d = 0
- KPI-5: ungeklärte Duplikate aktiv = 0
- KPI-6: Source-Pfad für neue dauerhafte Entscheidungen = 100%

3. Operational-Set
- KPI-7: kritische Retrieval-Fehler (rolling 72h) = 0
- KPI-8: Verify-after-write Quote = 100%
- KPI-9: QMD-Fallback-Proof vorhanden = ja

## Review Loops

### Daily (15 min)
- Owner: Atlas
- Scope: KPI-Deltas, neue Incidents, kurzfristige Countermeasures
- Trigger: jede KPI-Verletzung -> P2 Follow-up innerhalb 24h

### Weekly (45 min)
- Owner: Atlas + Lens
- Scope: Trend, Drift-Indikatoren, Threshold-Tuning, Owner-Load
- Trigger: 2x rote KPI in Folge -> Operator-Eskalation + Korrekturplan

## Restrisiko (aktuell)
- Parallel laufende P1/P0 Streams können Weekly-Reviews verzögern.
- Worker pickup-latency kann Orchestrierungsdurchsatz begrenzen; Countermeasure: bounded redispatch + timeout-gesteuerte Partial-Consolidation.
