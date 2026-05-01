# Sprint: Memory System Hardening (Best-in-Class)

- Sprint-ID: S-MEM-HARDENING-2026-05-01
- Erstellt am: 2026-05-01
- Owner: Atlas
- Status: planned
- Priorität: P1

## Ziel
Memory-System für OpenClaw robust, eindeutig und auditierbar machen (Canonical Sources, Freshness, Retrieval-Qualität, Agent-Coverage) und mit Best-in-Class-Praktiken abgleichen.

## Scope
- Canonical Source Map für alle Agenten
- Schließen aller Agent-Memory-Lücken
- Freshness/Bootstrap-Gates
- Retrieval-Policy + Konfliktauflösung (canonical > legacy)
- Best-in-Class-Research + Adaptionsvorschlag für unser Setup

## Anti-Scope
- Keine destruktiven Löschungen ohne separaten Freigabe-Task
- Keine ungeplanten Runtime/Restart/Config-Mutationen

## Workstreams (alle Agenten)
1. Atlas (Orchestrierung): Sprint-Steuerung, Gates, Integration, Final-Decision.
2. Forge (SRE/Backend): Guardrails, Freshness-Gates, technische Verifikation.
3. Pixel (Frontend): UI/Operator-Sichtbarkeit für Memory-Status/Freshness.
4. Lens (Audit/Kosten): KPI-Definition, Wirkungsmessung, Risiko/Kosten-Tradeoffs.
5. Spark (Quick Wins): kleine strukturierte Fixes + Policy-Hygiene.
6. James (Research): Best-in-Class Memory/Context-Setup recherchieren und auf unser System mappen.

## Deliverables
- Canonical Memory Map (final)
- Legacy-Drift Liste mit Risikoklassen
- Best-in-Class Research Memo (James)
- Adaptionsplan für unser System (priorisiert)
- Verifizierter DoD-Report

## Definition of Done
- 6/6 Agenten mit eindeutigem canonical Memory-Pfad
- 0 offene kritische Ambiguitäten
- Bootstrap/Freshness-Gates aktiv und geprüft
- Best-in-Class Empfehlungen priorisiert + als umsetzbare Folgetasks geplant
