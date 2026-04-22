# Atlas Trigger - Sprint Reporting

```text
Atlas nun Sprint Reporting.

Lies zuerst diese Datei als kanonischen Kontext:
- /home/piet/vault/03-Agents/sprint-reporting-next-action-hardening-plan-2026-04-21.md

Arbeitsmodus:
- Kein Broad Review
- Keine Neudiskussion des bereits gefixten terminalen Report-Pfads
- Kein Umbau des Discord-Execution-Report-Formats
- Keine UI-Nebenbaustellen
- Kein schemaweiter Umbau in diesem ersten Block
- Fokus nur auf den ersten produktiven Block P0.1 Reader Hygiene

Aktueller Wahrheitsstand:
- Der terminale Execution-Report-Pfad ist wieder gruen.
- Der kompakte Human-Report in task-reports.ts ist akzeptabel und nicht der aktuelle Engpass.
- Das naechste Problem ist, dass task-governance-signals noch narrative Ergebnisfelder als Signalquelle liest.
- board-next-action ist weitgehend strukturiert und soll nicht vertextet werden.

Deine Aufgabe:
1. Verifiziere kurz, dass P0.1 der naechste enge Block ist.
2. Bearbeite genau P0.1 und nichts darueber hinaus.
3. Delegiere die minimale Codeaenderung an Forge.
4. Verifiziere mit gezielten Tests.
5. Liefere einen knappen Abschluss mit dem naechsten Block, aber ohne Themenvermischung.

P0.1 Ziel:
- Governance-Signale duerfen nicht mehr primaer aus resultSummary/resultDetails kommen.

P0.1 Scope:
- /home/piet/.openclaw/workspace/mission-control/src/lib/task-governance-signals.ts
- zugehoerige Tests in mission-control/tests

P0.1 DoD:
- resultSummary/resultDetails sind aus dem Primaerpfad fuer Governance-Signale entfernt
- Tests sind gruen
- Execution-Report-Format unveraendert
- board-next-action nicht unnoetig angefasst

P0.1 Verify:
- mission-control/tests/task-governance-signals.test.ts
- mission-control/tests/taskboard-governance-overview.test.ts
- kurzer Sanity-Check, dass Security-/Review-/Manual-Recovery-Signale weiterhin korrekt erkannt werden

Nicht Teil dieses Blocks:
- neues Outcome-Schema
- Follow-up-Objektmodell
- lifecycle-report-sent Event
- UI-Redesign
- Discord-Report-Text

Antwortformat:
- EXECUTION_STATUS
- RESULT_SUMMARY
- CHANGED_FILES
- VERIFICATION
- RESIDUAL_RISK
- NEXT_BLOCK
```
