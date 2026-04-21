---
title: Sprint Reporting / Next-Action Hardening Plan 2026-04-21
date: 2026-04-21 20:40 CEST
author: Codex im Operator-Modus (Lenard-Rolle)
scope: Execution-report posting bleibt Human-Output; Folgeaktionen werden auf strukturierte Felder umgestellt
status: Ready for Atlas Sprint Dispatch
---

# Sprint Reporting / Next-Action Hardening Plan

## Kurzfazit

Der naechste echte Engpass liegt nicht mehr im eigentlichen Posting der Execution Reports, sondern in der Ableitung von Folgeaktionen.

Stand heute:

- Der terminale Report-Pfad ist wieder gruen.
- Der kompakte Execution Report ist bereits kurz und operator-tauglich.
- Das verbleibende Architekturproblem ist, dass Governance-/Next-Action-Hinweise noch teilweise aus langen narrativen Ergebnisfeldern gelesen werden.

Konsequenz:

- `execution-report` bleibt Human-Output.
- Machine-Entscheidungen muessen aus strukturierten Task-/Outcome-Feldern kommen.
- `resultSummary` und `resultDetails` bleiben Audit-/Narrativ-Felder, aber sind keine primaere Eingabe fuer Orchestrierung.

## Live-Evidenz

### E1 - Posting-Pfad ist nach Fix wieder sauber

Live-Pruefung am 2026-04-21:

- Vor Fix zeigte Task `5928b301-e003-470d-94d8-57528b9ee19e` den alten False-Dedup-Zustand:
  - `lastReportedStatus=result`
  - `finalReportSentAt=null`
- Nach Fix und Rebuild zeigte Task `0689b9de-4cbe-4326-8844-2244e728c46d`:
  - `lastReportedStatus=result`
  - `finalReportSentAt=2026-04-21T18:29:41.069Z`
- Fuer terminale Tasks im Post-Fix-Fenster ab `2026-04-21T18:29:41.069Z` gilt aktuell:
  - `4` terminale Tasks
  - `0` ohne `finalReportSentAt`

### E2 - Execution Report ist bereits kurz gebaut

Der kompakte Human-Report entsteht in:

- `/home/piet/.openclaw/workspace/mission-control/src/lib/task-reports.ts:163`

Er enthält nur:

- `Problem`
- `Task`
- `Status`
- `Aktion`
- optional `Grund`

Damit ist das Posting-Format selbst nicht der Hauptengpass.

### E3 - Governance-Signale lesen noch narrative Ergebnisfelder

Aktueller Engpass:

- `/home/piet/.openclaw/workspace/mission-control/src/lib/task-governance-signals.ts:16`

Dort wird `blockerText` aus diesen Feldern zusammengesetzt:

- `blockerReason`
- `blockedReason`
- `failureReason`
- `lastFailureReason`
- `resultSummary`
- `resultDetails`

Das ist fuer Follow-up-Ableitungen zu breit und zu rauschig.

### E4 - Live-Daten bestaetigen das Rauschproblem

Momentaufnahme aus `tasks.json`:

- `270` terminale Tasks insgesamt
- `136` terminale Tasks mit ueberlangen `resultSummary` oder `resultDetails`

Das bedeutet: wenn Governance-/Next-Action-Pfade diese Felder lesen, lesen sie haeufig lange freie Narrative statt eines kanonischen Maschinenzustands.

### E5 - Board Next Action ist bereits weitgehend strukturiert

Die Board-Next-Action-Logik in:

- `/home/piet/.openclaw/workspace/mission-control/src/lib/board-next-action.ts:47`

arbeitet ueberwiegend mit:

- `status`
- `executionState`
- `dispatchState`
- Zeitfeldern
- `finalReportSentAt`
- `lastReportedAt`

Das ist die richtige Richtung und soll nicht wieder vertextet werden.

## Zielbild

Das Reporting-/Orchestrierungsmodell soll auf drei Schichten getrennt werden:

1. **Human Report**
   - kurz
   - scanbar
   - operator-tauglich
   - keine Maschinenlogik aus Discord-Nachrichten

2. **Canonical Outcome**
   - strukturierte Felder auf dem Task
   - eindeutig fuer Status, Handlungsbedarf, Owner und naechsten Schritt

3. **Narrative Audit**
   - `resultSummary`
   - `resultDetails`
   - Threads
   - Artefakte
   - nur fuer Menschen und Nachvollziehbarkeit

## Design-Prinzipien

1. Eine Folgeentscheidung hat genau eine kanonische Quelle.
2. Alerts, Reports und Folgeaktionen muessen actionable sein.
3. Kein primaerer Regex-/Keyword-Pfad ueber freie Ergebnisnarrative.
4. Jeder naechste Schritt braucht mindestens:
   - `kind`
   - `owner`
   - `reasonCode`
5. Lange Details gehoeren in Thread/Artefakte, nicht in den Primary Decision Path.
6. Erfolgreiches Report-Senden muss im Datenmodell oder Event-Log explizit beobachtbar sein.

## Priorisierter Plan

## Phase P0.1 - Reader Hygiene

Prioritaet: P0
Ziel: Den aktuellen Rauschpfad sofort verkleinern, ohne schon das volle neue Outcome-Schema einzufuehren.

Scope:

- `src/lib/task-governance-signals.ts`
- bestehende Tests rund um Governance-/Overview-Signale

Massnahmen:

- `resultSummary` und `resultDetails` aus dem primaeren Governance-Signal-Pfad entfernen
- Governance-Signale nur noch aus strukturierten oder semistrukturierten Statusfeldern lesen:
  - `status`
  - `executionState`
  - `security*`
  - `maxRetriesReached`
  - `blockerReason`
  - `blockedReason`
  - `failureReason`
  - `lastFailureReason`
- einen Regressionstest ergaenzen:
  - langes `resultSummary` mit Woertern wie `approval` oder `review` darf alleine kein Governance-Signal ausloesen

Definition of Done:

- `task-governance-signals.ts` liest keine `resultSummary`/`resultDetails` mehr fuer Primaersignale
- Tests sind gruen
- `board-next-action` bleibt unveraendert oder nur testseitig beruehrt
- Execution-Report-Format bleibt unveraendert

Verify:

- gezielte Tests:
  - `tests/task-governance-signals.test.ts`
  - `tests/taskboard-governance-overview.test.ts`
- kurzer Sanity-Run, dass bestehende Security-/Review-/Manual-Recovery-Signale weiter korrekt zaehlen

Nicht Teil von P0.1:

- neues Outcome-Schema
- neue Follow-up-Tabelle
- UI-Redesign
- Discord-Report-Umbau

## Phase P0.2 - Canonical Outcome Contract

Prioritaet: P0
Ziel: Ein minimales, typisiertes Outcome-/Next-Action-Schema festziehen.

Geplante Felder:

- `outcome`
- `actionability`
- `nextActionKind`
- `nextActionOwner`
- `reasonCode`
- `runbookRef`
- `evidenceRefs`
- `followUpRequired`
- `followUpPriority`

Definition of Done:

- Felder und Semantik schriftlich fixiert
- Producer-/Consumer-Mapping klar
- keine offene Mehrdeutigkeit zwischen Human-Narrativ und Machine-State

## Phase P1 - Writer Normalization

Prioritaet: P1
Ziel: Alle terminalen und blocked/result/failed-Pfade schreiben die kanonischen Outcome-Felder konsistent.

Scope:

- `/api/tasks/[id]/complete`
- `/api/tasks/[id]/fail`
- `/api/tasks/[id]/receipt`
- ggf. `admin-close`/`finalize`

Definition of Done:

- alle Writer setzen dasselbe minimale Outcome-Modell
- keine Folgeableitung braucht `resultSummary` als Primaerquelle

## Phase P1.5 - Follow-up als First-Class Object

Prioritaet: P1
Ziel: Follow-ups nicht mehr aus Fliesstext ableiten, sondern explizit fuehren.

Definition of Done:

- Follow-up hat Owner, Status, Prioritaet und Source-Task
- spaetere Tracker-Synchronisation ist moeglich, aber nicht Blocker

## Phase P2 - Report Observability

Prioritaet: P2
Ziel: Erfolgreicher Report-Send ist explizit sichtbar.

Massnahmen:

- Erfolgsevent wie `lifecycle-report-sent`
- Payload mit `messageId`, `threadId`, `sentAt`, `stage`

Definition of Done:

- Operator kann Send-Erfolg im Event-Log direkt sehen
- nicht nur Error-/Dedup-Faelle sind sichtbar

## Warum diese Reihenfolge

Diese Reihenfolge folgt dem kleinsten sicheren Fixpfad:

1. Erst den noisy Reader-Pfad abstellen.
2. Dann den kanonischen Contract definieren.
3. Dann die Writer umstellen.
4. Dann Follow-ups formalisieren.
5. Erst danach mehr Observability oder UI.

So wird zuerst der eigentliche Fehlanreiz entfernt: naechste Schritte aus Freitext zu erraten.

## Risiken

### R1 - Zwischenphase mit weniger heuristischen Treffern

Wenn `resultSummary`/`resultDetails` nicht mehr gelesen werden, koennen einzelne bisher zufaellig erkannte Signale wegfallen.

Bewertung:

- akzeptabel
- besser ein bewusst engeres Signal als ein unzuverlaessiges

### R2 - Reader/Writer laufen kurz asynchron

Nach P0.1 und vor P1 gibt es noch keinen vollstaendigen neuen Outcome-Contract.

Bewertung:

- akzeptabel
- weil `board-next-action` bereits weitgehend strukturiert ist

### R3 - Operator verwechselt Human-Report mit Machine-State

Wenn diese Trennung nicht klar kommuniziert wird, kommt die gleiche Diskussion spaeter wieder.

Mitigation:

- diesen Plan als kanonische Trennung verwenden
- Atlas explizit auf `Human Output != Machine Decision Path` scharfen

## Externe Best Practices, auf die sich der Plan stuetzt

1. **PagerDuty Alerting Principles**
   - Alerts muessen actionable sein.
   - Alerts sollen genug Kontext und potenzielle Remediation-Schritte enthalten.

2. **AWS Well-Architected**
   - `Have a process per alert`
   - `Create actionable alerts`

3. **PagerDuty SRE Agent**
   - nur den Kontext ziehen, der den naechsten Schritt wirklich aendert
   - keine spekulative Datensammlung

4. **incident.io**
   - Actions und Follow-ups sind eigene, trackbare Objekte
   - nicht nur Text im Incident-Stream

5. **GitHub structured issue metadata**
   - typed fields statt label-/body-basierten Workarounds

6. **OpenClaw Community**
   - State machine
   - progress feedback
   - verification
   - activity visibility
   - kein stilles "Output goes nowhere"

## Atlas Initial Block

Der erste Sprintblock fuer Atlas ist **nicht** "Reporting komplett neu bauen", sondern nur:

**P0.1 - Reader Hygiene**

Warum genau dieser Block zuerst:

- kleinster Blast Radius
- hoechster semantischer Gewinn
- keine UI-Abhaengigkeit
- keine Datenmigration
- direkt testbar

## Stop-Bedingungen fuer Atlas

Atlas stoppt und meldet zurueck, wenn:

1. `task-governance-signals` an mehr Stellen konsumiert wird als aktuell sichtbar und der Block unkontrolliert groesser wird.
2. Bestehende Tests zeigen, dass Business-kritische Signale nur ueber Freitext ueberlebt haben.
3. Die Aenderung wuerde einen Schema- oder API-Contract erzwingen.

Dann kein breiter Umbau, sondern Rueckmeldung mit exakter Blockade.

## Atlas Startprompt

Den folgenden Prompt kannst du direkt an Atlas schicken. Der Trigger ist bewusst kurz gehalten und startet mit der kanonischen Phrase.

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
- board-next-action nicht unnötig angefasst

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

## Quellen

- AWS Well-Architected - Have a process per alert
  - https://docs.aws.amazon.com/wellarchitected/latest/framework/ops_event_response_process_per_alert.html
- AWS Well-Architected - Create actionable alerts
  - https://docs.aws.amazon.com/wellarchitected/latest/framework/ops_workload_observability_create_alerts.html
- PagerDuty Alerting Principles
  - https://response.pagerduty.com/oncall/alerting_principles/
- PagerDuty - Context Over Cleverness: Building PagerDuty's SRE Agent
  - https://www.pagerduty.com/eng/context-over-cleverness-building-pagerdutys-sre-agent/
- PagerDuty Automation Actions
  - https://support.pagerduty.com/main/docs/automation-actions
- incident.io Follow-ups
  - https://docs.incident.io/post-incident/follow-ups
- incident.io Task Tracking
  - https://docs.incident.io/incidents/task-tracking
- GitHub - Structured issue metadata
  - https://github.blog/changelog/2026-03-12-issue-fields-structured-issue-metadata-is-in-public-preview/
- OpenClaw issue #45522 - Long-Running Task Orchestration with Real-Time Progress Feedback
  - https://github.com/openclaw/openclaw/issues/45522
- OpenClaw issue #60810 - Real-time agent activity dashboard
  - https://github.com/openclaw/openclaw/issues/60810
- OpenClaw issue #8995 - Spawn Verification & Worker Health Monitoring
  - https://github.com/openclaw/openclaw/issues/8995
- OpenClaw issue #50038 - Multi-Agent & Sub-Agent Workflows
  - https://github.com/openclaw/openclaw/issues/50038
- Reddit SRE - Alert fatigue is killing me
  - https://www.reddit.com/r/sre/comments/1nm7sbi/alert_fatigue_is_killing_me/
