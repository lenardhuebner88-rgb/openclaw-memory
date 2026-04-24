# MC Orchestrated Audit Gate

Status: planned
Owner: Atlas
Created: 2026-04-24T13:16:26Z

## Ziel
Mission Control als echten Live-Test auditieren: UI-Bugs, Bedienbarkeit, Datenstabilitaet und Optimierungspotenzial erfassen, ohne direkt Code zu mutieren.

## Scope
- Taskboard/Board-Detail-Flow pruefen, inklusive Details-Buttons und Modal-Stabilitaet.
- Board-Snapshot/API-Payload und normale Refresh-Pfade gegen Full-Load-Regressions pruefen.
- Datenstabilitaet pruefen: `/api/health`, Pickup-Proof, Worker-Proof, Runtime-Soak-Proof, Board Snapshot.
- UI-Bugs in reale Repro-Schritte uebersetzen.
- Daten-/Runtime-Risiken mit Evidence, IDs und konkretem Fix-Vorschlag dokumentieren.

## Anti-Scope
- Keine Provider-/Model-Routing-Aenderung.
- Keine QMD-Architekturarbeit.
- Keine breiten UI-Rewrites.
- Keine mutierenden Reconciler-HTTP-Endpunkte.
- Code-Fixes erst nach Operator-Freigabe in einem separaten Sprint.

## Real Use Cases
- Operator klickt Task-Details auf Desktop und Mobile.
- Board aktualisiert per Snapshot/Heartbeat ohne `/api/tasks` als Normalpfad.
- Pending-Pickup/Worker-Run-Proofs bleiben nach Audit-Dispatch sauber.
- Atlas kann Read-only Sub-Audits an Pixel/Forge koordinieren, wenn noetig.

## Gruen-Gate
- Atlas-Task accepted und terminal `done/result` oder sauber `blocked` mit konkretem Blocker.
- Report liegt unter `03-Projects/reports/audits/`.
- Report enthaelt: UI-Bugliste, Datenstabilitaetsbefund, API/Board-Payload-Befund, naechste 3 Fix-Sprints.
- Nach Task: `/api/health` ok, Pickup active claimTimeouts 0, Worker openRuns 0, Runtime keine Criticals.

## Nachfolgende Umsetzung
Nach Atlas-Report die Fixes nicht direkt breit starten. Erst P4-Sprint schneiden:
- P4.1 UI-Bugfixes mit Repro.
- P4.2 Board/API-Payload-Regressionen.
- P4.3 Data-Stability Proof-Ergaenzungen.
