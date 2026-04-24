---
sprint-id: S-MC-AUDIT
title: Mission Control — Alerts System + Dashboard Operability Audit
created: 2026-04-23
status: planned
priority: P1
owner:
  lens-audit: efficiency-auditor
  pixel-audit: frontend-guru
  remediation-plan: Atlas
depends-on: []
enables:
  - S-MC-REMEDIATION
source-plans:
  - discord-request-2026-04-23-alerts-dashboard-audit
anti-goals:
  - Keine Broad-Redesigns
  - Keine unnötigen Backend-/UI-Refactors ohne belegten Befund
  - Keine Vermischung von Live-Signalen mit Archiv-/Historie-Nachrichten
pre-flight-gates:
  - Live board/API truth sampled first
  - Archived/closed task signals separated from live signals
  - Audit findings ranked by operator impact
---

# S-MC-AUDIT: Alerts System + Dashboard Operability

## Why
Operator-Signalqualität ist aktuell schwer lesbar: viele rote Marker, Warntexte und Pipeline-Items wirken historisch/archiviert statt live. Ziel ist ein sauberes Audit, das echte Live-Probleme von Altlasten trennt und daraus klare Verbesserungen ableitet.

## Scope
- Alerts-System: rote Marker, Warntexte, Signalzuordnung, Archiv-Noise
- Dashboard-Nutzbarkeit: operative Lesbarkeit, Pipeline-Alter, Klarheit der Live-/Historie-Trennung
- Follow-up: konkrete Verbesserungs-Sprints aus den Befunden

## Workstreams

### T1 — Lens Audit: Alerts System truth check
Owner: efficiency-auditor
DoD:
- Live vs archived alert sources getrennt
- Rote Marker quantitativ eingeordnet
- Befunde mit Priorität + Ursache + Fixrichtung
Return format: resultSummary mit Findings + Recommendation

### T2 — Pixel Audit: Dashboard operability + pipeline freshness
Owner: frontend-guru
DoD:
- Dashboard-Lesbarkeit und operative Klarheit bewertet
- Alte Pipeline-Tasks vs echte aktive Arbeit getrennt
- UI/UX-Fixes priorisiert
Return format: resultSummary mit Findings + Recommendation

### T3 — Follow-up Sprint: remediation plan
Owner: Atlas
DoD:
- Audit-Findings in umsetzbare Sprints geschnitten
- Jede Maßnahme hat Owner, DoD und Reihenfolge
- Keine offenen Ambiguitäten
Return format: Sprint-Backlog + dispatch-ready tasks

## Exit Criteria
- Audit-Sicht auf rote Marker ist live-verifiziert, nicht vermutet
- Archiv-/Historiennoise ist explizit benannt
- Follow-up Sprints sind board-ready
