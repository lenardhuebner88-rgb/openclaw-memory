---
title: Hermes Co-Orchestrator — Vertical-Slicing Integration Plan
created: 2026-05-05
updated: 2026-05-06
status: reviewed-and-hardened-for-morning-start
owner: Lenard
source:
  - 03-Projects/plans/2026-05-05_hermes-co-orchestrator-decision-brief.md
related:
  - Hermes Co-Orchestrator 1-day pilot
agents:
  - Hermes
  - Atlas
  - Forge
  - Pixel
  - Spark
  - James
  - Lens
---

# Hermes Co-Orchestrator — Vertical-Slicing Integration Plan

## 1. Ziel dieses Plans

Dieser Plan übersetzt den genehmigten Hermes Decision Brief in eine schrittweise Integration nach Vertical Slices.

Ziel ist nicht, Hermes „groß“ einzubauen, sondern nach und nach kleine, beweisbare Fähigkeiten produktiv zu machen:

1. Jede Slice liefert echten operativen Nutzen.
2. Jede Slice hat klare Grenzen.
3. Jede Slice ist testbar.
4. Jede Slice kann gestoppt oder zurückgerollt werden.
5. Mission Control bleibt die verbindliche Audit-Spur.

## 2. Leitentscheidung aus dem Decision Brief

Hermes wird als Co-Orchestrator eingeführt.

Hermes darf operative MC-Arbeit übernehmen, aber nur innerhalb harter Guardrails:

- MC ist Audit-SSOT.
- `done` braucht immer Receipt.
- maximal 2 Agents pro Hermes-Task.
- kein direkter Restart/Deploy durch Hermes.
- kein `sudo` durch Hermes.
- kein Modellrouting durch Hermes.
- bei MC-Ausfall nur Analysemodus, keine operative Mutation.

Atlas bleibt Governance-/Fallback-Instanz und Operator-Interface.
Forge bleibt Default-Executor für Restart/Deploy und runtime-nahe Arbeiten.

## 3. Integrationsprinzip: Vertical Slicing

Jede Slice soll einen vollständigen kleinen Nutzungsfluss abdecken:

- Eingang: Operator- oder MC-Task
- Hermes-Entscheidung: Zerlegung, Spec, Dispatch oder Closure
- MC-Spur: Task, Status, Receipt, Evidence
- Guardrail-Prüfung: Was ist erlaubt/verboten?
- Verification: Test, API-Proof, Build, Curl, Receipt oder Plausicheck
- Review: Was lernen wir für die nächste Slice?

Nicht gewünscht:

- erst große Frameworks bauen
- viele abstrakte Regeln ohne Live-Proof einführen
- Autonomie ausweiten, bevor die vorherige Slice stabil ist
- paralleler Fanout über mehrere Subsysteme

## 4. Teststrategie als Grundregel

Tests werden nicht nachträglich angehängt, sondern pro Slice als Akzeptanzbedingung definiert.

### 4.1 Testebenen

Pro Slice wird geprüft, welche Ebenen nötig sind:

1. Unit-Tests
   - Guardrails
   - Spec-Validatoren
   - Fanout-Limits
   - Receipt-Pflicht
   - erlaubte/verbotene Aktionen

2. Integrationstests
   - MC API create/update/get
   - Dispatch-State
   - Task-Metadaten
   - Worker-Receipt-Felder
   - Deny-Fälle gegen MC-Mutation bei MC-Ausfall

3. E2E-/Smoke-Tests
   - ungefährlicher Pilot-Task von Anlage bis Closure
   - Agent-Beauftragung mit Evidence
   - `done` nur mit Receipt

4. Negative Tests
   - mehr als 2 Agents wird blockiert
   - `done` ohne Receipt wird blockiert
   - Restart/Deploy durch Hermes wird blockiert
   - Modellrouting wird blockiert
   - MC-down plus Mutation wird blockiert

5. Operational Proofs
   - `npm run typecheck`
   - `npm run lint`
   - relevante Vitest-Suite
   - relevante Playwright-/Smoke-Proofs nur bei UI-/E2E-Slices
   - `curl`/API-Proof gegen MC bei Live-Mutation

### 4.2 Aktuell vorhandene MC-Test-Gates

Im Mission-Control-Repo existieren u. a. diese Gates:

- `npm run typecheck`
- `npm run lint`
- `npm run build`
- `npm run test:worker-lifecycle`
- `npm run test:smoke`
- `npm run test:readonly-audit`
- `npm run test:e2e`
- `npm run monitor:readonly-health-proof`

Empfehlung:

- Für kleine Guardrail-/Backend-Slices: `typecheck`, `lint`, gezielte Vitest-Tests.
- Für Dispatch-/Worker-Slices: zusätzlich `test:worker-lifecycle`.
- Für UI-/Board-Sichtbarkeit: zusätzlich Smoke/Playwright.
- Für Restart/Deploy-Slices: Build/Test vorab, sicherer Restart durch Forge, danach Health-/Curl-Proof.

## 5. Phase 0 — Baseline und Sicherheitsrahmen

### Ziel

Vor der ersten Hermes-Mutation wird der Ist-Zustand festgehalten.

### Nutzen

Wir wissen, ob MC erreichbar ist, ob es offene Worker-Probleme gibt und welche Test-Gates grün sind.

### Umsetzung

- MC Health prüfen.
- Worker-Reconciler-/Pickup-Proof prüfen.
- aktuelle Hermes-/Agent-Konfiguration lesen, aber nicht ändern.
- klare Pilot-Grenzen in MC oder Vault referenzieren.
- einen ungefährlichen Pilot-Task auswählen.

### Tests / Proofs

- `curl http://127.0.0.1:3000/api/health`
- `curl /api/ops/worker-reconciler-proof?limit=20`
- `curl /api/ops/pickup-proof?limit=20`
- kein Schreibzugriff in dieser Phase

### Akzeptanzkriterien

- MC ist erreichbar oder Pilot wird nicht gestartet.
- keine offenen kritischen Worker-Probleme.
- Pilot-Scope ist benannt.
- Abbruchkriterien sind dokumentiert.

### Rollback

Nicht nötig, da read-only.

## 6. Slice 1 — Hermes-Pilot als MC-Task mit festen Guardrails

### Ziel

Hermes-Pilot wird als eigener MC-Task angelegt oder sauber referenziert.

### User Value

Der Pilot ist auditierbar, nicht nur eine Discord-/Vault-Abrede.

### Umfang

- MC-Task: „Hermes 1-day Co-Orchestrator Pilot“
- Task-Spec enthält:
  - Ziel / DoD
  - Anti-Scope
  - Risiko-Level
  - Verification-Gates
  - Eskalationspunkte
  - Link oder Vollzitat der Betriebsregeln

### Nicht enthalten

- noch keine Autonomie-Ausweitung
- kein Restart/Deploy
- keine Config-/Cron-Mutation
- kein Modellrouting

### Tests / Proofs

- MC Task via API anlegen/prüfen.
- Danach `GET /api/tasks/<id>` verifizieren.
- Prüfen, ob Spec vollständig ist.

### Akzeptanzkriterien

- Pilot-Task existiert in MC.
- Spec referenziert Guardrails.
- Status ist eindeutig.
- Owner ist klar.

### Rollback

Task auf canceled setzen mit Receipt: „Pilot-Task zurückgezogen, keine operative Mutation erfolgt.“

## 7. Slice 2 — Task-Spec-Validator für Hermes-Beauftragungen

### Ziel

Hermes darf nur dann Agents beauftragen, wenn die Task-Spec vollständig ist.

### User Value

Keine Bauchgefühl-Prompts; jeder Agent bekommt eine brauchbare Arbeitsanweisung.

### Validierungsregeln

Jede Beauftragung braucht:

- Ziel / DoD
- Anti-Scope
- Risiko-Level
- Verification-Gate
- Eskalationspunkt
- maximal 2 Agents

### Umsetzung

- Validator als kleine isolierte Funktion/Modul.
- Test-Fixtures für gültige und ungültige Specs.
- Fehlermeldungen so formulieren, dass Hermes/Atlas direkt nachbessern kann.

### Tests

Unit-Tests:

- gültige Spec wird akzeptiert
- fehlendes DoD wird abgelehnt
- fehlender Anti-Scope wird abgelehnt
- fehlendes Verification-Gate wird abgelehnt
- fehlender Eskalationspunkt wird abgelehnt
- 3 Agents werden abgelehnt
- unbekanntes Risiko-Level wird abgelehnt

Integration:

- MC-Task mit unvollständiger Hermes-Spec kann nicht dispatcht werden, falls technisch angebunden.

### Akzeptanzkriterien

- Hermes kann keine Agent-Beauftragung ohne vollständige Spec erzeugen.
- Validator ist getestet.
- Fehlerfälle sind bewusst getestet.

### Rollback

Validator deaktivieren oder nur als Warnung schalten; Pilot dann zurück auf manuelle Atlas-Prüfung.

## 8. Slice 3 — MC-Mutation nur über Hermes Guarded Adapter

### Ziel

Hermes erhält einen kontrollierten Weg für MC-Task-Erstellung und Statusupdates.

### User Value

Hermes kann operativ helfen, aber alle Writes laufen durch dieselben Regeln.

### Umfang

Erlaubt:

- Task anlegen
- Task aktualisieren
- Dispatch-State setzen
- Status auf done setzen, wenn Receipt-Regel erfüllt ist

Blockiert:

- done ohne Receipt
- mehr als 2 Agents
- Restart/Deploy-Ausführung
- sudo
- Modellrouting
- MC-Ausfall-Mutation

### Umsetzung

- Guarded Adapter vor MC-Write.
- Jede Mutation erzeugt nachvollziehbaren Receipt-/Audit-Text.
- Adapter prüft MC-Erreichbarkeit vor Write.
- Nach jedem Write: `GET /api/tasks/<id>` Verification.

### Tests

Unit:

- Action-Allowlist
- Action-Denylist
- done-without-receipt denied
- mc-down-mutation denied

Integration:

- create task -> get task -> fields korrekt
- update task -> get task -> status korrekt
- done mit Receipt -> akzeptiert
- done ohne Receipt -> abgelehnt

### Akzeptanzkriterien

- Keine direkte Hermes-Mutation ohne Guard.
- Jeder Write wird verifiziert.
- Negative Cases sind getestet.

### Rollback

Adapter auf read-only setzen; Hermes darf nur briefen, Atlas übernimmt MC-Writes.

## 9. Slice 4 — Controlled Dispatch: erst 1 Agent, dann 2 Agents

### Ziel

Hermes darf einen ungefährlichen Task an maximal 1 Agent dispatchen; nach erfolgreichem Proof maximal 2 Agents.

### User Value

Der Co-Orchestrator übernimmt echte Koordination, ohne Fanout-Chaos.

### Startvariante

Pilot 4A:

- maximal 1 Agent
- bevorzugt Spark oder Lens für low-risk task
- kein Code-Deploy
- kein Restart

Erweiterung 4B:

- maximal 2 Agents
- nur wenn 4A sauber abgeschlossen wurde

### Beispiel-Pilot-Task

„Analyse und Verbesserung einer vorhandenen Task-Spec-Vorlage für Hermes-Beauftragungen.“

Warum gut:

- low-risk
- kein Runtime-Eingriff
- guter Test der Spec-Qualität
- Ergebnis kann in MC/Vault dokumentiert werden

### Tests / Proofs

- Dispatch erzeugt korrekten `dispatchState=dispatched`.
- Agent erhält vollständige Spec.
- Agent liefert Evidence.
- Hermes schließt nur mit Receipt.
- Fanout-Zähler verhindert dritten Agent.

### Akzeptanzkriterien

- Ein Task wird sauber dispatched.
- Keine unvollständigen Prompts.
- Keine Fanout-Überschreitung.
- Abschluss enthält Receipt.

### Rollback

Dispatch-Recht zurücknehmen; Hermes darf nur Task-Specs vorbereiten.

## 10. Slice 5 — Done-Entscheidung mit harter Gate- oder Plausicheck-Regel

### Ziel

Hermes darf Tasks schließen, aber nie ohne Begründung.

### User Value

Board-Hygiene wird besser, ohne blinde Done-Closures.

### Closure-Typen

1. Hard Gate Done
   - Test/Build/Curl/API-Proof/Worker-Receipt liegt vor.

2. Plausicheck Done
   - Scope erfüllt.
   - keine offenen Blocker erkennbar.
   - keine technische Gate sinnvoll oder nötig.
   - Receipt sagt explizit „Done per Plausicheck“.

### Tests

Unit:

- done ohne Receipt denied
- hard gate done accepted
- plausicheck done accepted, wenn Begründung vorhanden
- plausicheck done denied, wenn Risiko-Level high ist

Integration:

- MC update done + receipt -> get task -> Status/Receipt korrekt
- MC update done ohne receipt -> blocked

### Akzeptanzkriterien

- Kein `done` ohne Receipt möglich.
- Plausicheck ist sichtbar unterscheidbar von Hard-Gate-Done.
- High-risk Tasks brauchen harte Evidence oder Eskalation.

### Rollback

Plausicheck-Closure deaktivieren; nur Hard-Gate-Done erlauben.

## 11. Slice 6 — Restart-/Deploy-Handoff an Forge

### Ziel

Hermes darf Restart/Deploy vorbereiten, aber nicht selbst ausführen.

### User Value

Hermes kann koordinieren, Forge führt sicher aus.

### Umfang

Hermes erstellt:

- Decision Brief
- Task-Spec
- Runbook
- Rollback-Hinweis
- Verification-Gate
- Eskalationspunkt

Forge führt aus und liefert Evidence.

### Tests

Negative Tests:

- Hermes command/action `restart` denied
- Hermes command/action `deploy` denied
- Hermes versucht service restart -> denied
- Hermes versucht sudo -> denied

Integration:

- Hermes erstellt Forge-Task mit vollständigem Runbook.
- Forge-Task enthält Build/Test/Health-Gates.
- Abschluss erst nach Forge-Receipt.

Operational Gates:

- vor Ausführung: Build/Test oder begründeter Skip
- safe restart path
- nach Ausführung: Health-/Curl-Proof
- MC-Receipt

### Akzeptanzkriterien

- Hermes löst keinen Restart/Deploy selbst aus.
- Handoff an Forge ist vollständig.
- Restart/Deploy wird nur mit Evidence abgeschlossen.

### Rollback

Hermes darf Restart/Deploy nur noch an Atlas eskalieren; kein Forge-Direktauftrag.

## 12. Slice 7 — Config-/Cron-Arbeiten ohne sudo und ohne Modellrouting

### Ziel

Hermes darf ungefährliche Config-/Cron-Arbeiten durchführen, sofern kein sudo, kein Modellrouting und keine unklare Service-Auswirkung betroffen sind.

### User Value

Kleine operative Pflege kann schneller erledigt werden.

### Voraussetzungen

Diese Slice erst nach erfolgreichem Pilot und stabilen Guardrails.

### Pflichtfelder

Vor Änderung:

- Risiko-Einschätzung
- Backup/Rückkehrpfad
- erwarteter Effekt
- Validierungsmethode

Nach Änderung:

- Validation-Proof
- MC-Receipt

### Tests

Unit:

- sudo denied
- model-routing denied
- unknown service impact denied
- no-backup denied for mutable config

Integration:

- dry-run config patch validiert
- Backup erzeugt
- Validation erfolgreich
- Rollback-Pfad dokumentiert

Operational:

- Schema-/JSON-Validation
- service impact check
- kein Restart ohne Forge-Handoff

### Akzeptanzkriterien

- Kleine Config-/Cron-Änderung kann sicher nachgewiesen werden.
- Modellrouting bleibt vollständig blockiert.
- sudo bleibt vollständig blockiert.

### Rollback

Hermes Config-/Cron-Rechte deaktivieren; nur Vorschläge/Runbooks erlauben.

## 13. Slice 8 — MC-Ausfall: Hermes-Degraded-Mode

### Ziel

Hermes verhält sich bei MC-Ausfall korrekt: Analyse ja, operative Mutation nein.

### User Value

Keine Schattenwahrheit in Discord/Vault; MC bleibt SSOT.

### Erlaubt bei MC-Ausfall

- analysieren
- Vorschläge vorbereiten
- Runbooks erstellen
- Risiken benennen

### Verboten bei MC-Ausfall

- Tasks außerhalb MC erstellen
- Dispatch simulieren
- Tasks schließen
- Discord/Vault als operative Wahrheit behandeln

### Tests

Negative Integration:

- MC Health mock/down -> create task denied
- MC down -> dispatch denied
- MC down -> close task denied

Positive:

- MC down -> brief/runbook allowed
- MC restored -> Nachtrag oder Eskalation möglich

### Akzeptanzkriterien

- Hermes mutiert bei MC-Ausfall nichts.
- Degraded Mode ist klar sichtbar.
- Nach Wiederherstellung wird nicht blind nachgetragen, sondern verifiziert oder eskaliert.

### Rollback

Degraded Mode bleibt read-only; keine Zusatzrechte.

## 14. Slice 9 — Pilot-Review: GO / CHANGE / STOP

### Ziel

Nach einem Tag wird faktenbasiert entschieden, ob Hermes weiterläuft.

### Review-Fragen

- Hat Hermes mindestens einen Task sauber angelegt oder übernommen?
- Waren alle Agent-Beauftragungen vollständig spezifiziert?
- Hatte jedes `done` einen Receipt?
- Gab es Statuswahrheiten außerhalb von MC?
- Gab es Fanout-Überschreitungen?
- Wurde Restart/Deploy korrekt an Forge übergeben oder vermieden?
- Gab es sudo-/Modellrouting-Versuche?
- Waren Tests/Proofs ausreichend?

### Metriken

- Anzahl Hermes-Tasks
- Anzahl Agent-Beauftragungen
- Anzahl Deny-Events
- Anzahl Done-Closures mit Receipt
- Anzahl Plausicheck-Closures
- Anzahl Eskalationen an Atlas/Operator
- Durchlaufzeit pro Task
- manuelle Korrekturen durch Atlas

### Entscheidungsmöglichkeiten

GO:

- Pilot stabil, Guardrails halten.
- nächste Slice freigeben.

CHANGE:

- grundsätzlich sinnvoll, aber Regeln/Tests/Scope anpassen.

STOP:

- Autonomie zurücknehmen.
- Hermes nur noch als Analyse-/Briefing-Agent verwenden.

## 15. Empfohlene Reihenfolge

### Minimal sicherer Pfad

1. Phase 0: Baseline
2. Slice 1: Pilot-Task in MC
3. Slice 2: Task-Spec-Validator
4. Slice 3: Guarded MC Adapter
5. Slice 4A: Dispatch an 1 Agent
6. Slice 5: Done mit Receipt
7. Review nach 1 Tag

### Danach nur bei GO/CHANGE

8. Slice 4B: Dispatch an maximal 2 Agents
9. Slice 6: Forge-Handoff für Restart/Deploy
10. Slice 8: MC-Ausfall-Degraded-Mode formal testen
11. Slice 7: Config-/Cron-Rechte prüfen

Wichtig: Slice 7 sollte nicht früh kommen. Config/Cron ist operativ sensibler als reine Task-Orchestrierung.

## 16. Definition of Done für den gesamten Pilot

Der Pilot ist erfolgreich, wenn:

- mindestens ein ungefährlicher Task über Hermes sauber durchläuft
- MC die einzige operative Audit-Spur bleibt
- jede Beauftragung vollständige Spec enthält
- jeder Done-Status einen Receipt enthält
- Fanout-Limit eingehalten wird
- kein verbotener Restart/Deploy passiert
- kein sudo/Modellrouting passiert
- Tests/Proofs pro Slice dokumentiert sind
- Review GO/CHANGE/STOP mit Evidenz getroffen werden kann

## 17. Offene Entscheidungen für Lenard / gemeinsames Verständnis

Diese Punkte sollten wir vor Umsetzung gemeinsam klären:

1. Soll Hermes in Slice 1 nur bestehende Tasks übernehmen dürfen oder auch neue Tasks anlegen?
2. Soll der erste Pilot-Task bewusst rein dokumentations-/analysebasiert sein, oder darf er schon eine kleine MC-Operation enthalten?
3. Wie streng soll Plausicheck-Done sein?
   - Option A: nur low-risk Tasks
   - Option B: low + medium mit Begründung
   - Option C: vorerst gar nicht, nur Hard Gates
4. Soll der erste Agent im Controlled Dispatch Spark, Lens oder Forge sein?
   - Empfehlung: Spark oder Lens, nicht Forge, weil Restart/Runtime-Nähe vermieden wird.
5. Soll der Guarded Adapter direkt technisch erzwungen werden, oder reicht für Tag 1 ein operationaler Prozess mit Atlas-Review?
6. Wollen wir Config/Cron-Rechte im 1-Tages-Pilot komplett ausschließen und erst nach Review erlauben?
   - Empfehlung: ja, zuerst ausschließen.
7. Welche Testhärte erwartest du für den Pilot?
   - Minimal: API-Proof + Receipt-Prüfung
   - Sauber: Unit Guardrails + API-Integration + Worker-Lifecycle-Test
   - Streng: zusätzlich E2E/Smoke
8. Soll Atlas jede Hermes-Done-Closure im Pilot gegenprüfen, oder nur Stichproben?
   - Empfehlung: Tag 1 jede Closure gegenprüfen.

## 18. Meine Empfehlung

Für den ersten Tag würde ich Hermes nicht sofort die volle im Brief erlaubte Breite geben.

Empfohlener Pilot-Scope:

- Hermes darf einen MC-Pilot-Task anlegen oder übernehmen.
- Hermes darf genau einen low-risk Agent beauftragen.
- Hermes muss vollständige Task-Spec liefern.
- Hermes darf `done` nur mit Receipt setzen.
- Plausicheck-Done nur für low-risk und nur mit explizitem Text.
- Config/Cron bleiben für Tag 1 aus.
- Restart/Deploy bleibt vollständig Forge-Handoff, aber noch nicht aktiv testen.
- Atlas reviewed jeden Statuswechsel im Pilot.

Warum:

- echte operative Übung
- geringes Risiko
- Guardrails werden früh sichtbar
- Testaufwand bleibt beherrschbar
- wir bekommen schnell belastbare Evidenz

## 19. Nächster konkreter Umsetzungsschritt

Wenn Lenard zustimmt:

1. MC Health + Worker Proof prüfen.
2. Hermes-Pilot-Task in MC anlegen.
3. Task-Spec vollständig eintragen.
4. Einen low-risk Pilot-Task auswählen.
5. Hermes erstellt erste Agent-Spec.
6. Atlas prüft Spec einmal manuell.
7. Hermes dispatcht maximal einen Agent.
8. Ergebnis/Evidence abwarten.
9. Hermes schließt mit Receipt.
10. Review durchführen und GO/CHANGE/STOP entscheiden.

## 20. Entschiedene Pilot-Parameter — 2026-05-06

Lenard hat für den ersten Hermes-Pilot folgende Parameter gesetzt:

1. Hermes darf im Pilot auch neue MC-Tasks anlegen, nicht nur bestehende übernehmen.
2. Der erste Pilot soll eine echte, aber low-risk MC-Operation enthalten.
3. Plausicheck-Done ist für low-risk Tasks erlaubt.
4. Der erste Controlled-Dispatch-Agent ist Spark.

Konsequenz für Slice 1/4A:

- Pilot-Scope: echte MC-Task-Anlage oder -Pflege durch Hermes, aber ungefährlich und auditierbar.
- Dispatch-Limit: zuerst genau ein Agent, Spark.
- Done-Regel: low-risk darf per Plausicheck geschlossen werden, aber nur mit explizitem Receipt.
- Atlas prüft im Pilot weiterhin jeden Hermes-Statuswechsel.

Nächster Umsetzungskandidat:

- MC-Pilot-Task anlegen: `Hermes Pilot Slice 1/4A — low-risk MC operation with Spark dispatch`.
- Task-Spec enthält Guardrails, Anti-Scope, Verification-Gate und Eskalationspunkte.
- Vor Write: MC Health + Worker Proof prüfen.
- Nach Write: `GET /api/tasks/<id>` verifizieren.

## 21. Startentscheidung — nicht jetzt, Morgen-Start

Lenard hat entschieden: Der Hermes-Pilot wird **nicht sofort gestartet**.

Start ist auf den nächsten Arbeitstag verschoben. Bis dahin gilt:

- keine MC-Mutation für Hermes-Pilot heute
- kein Pilot-Task jetzt anlegen
- kein Spark-Dispatch jetzt auslösen
- keine Tests/Proofs jetzt starten
- Plan bleibt als vorbereiteter Draft für den Morgen-Start

Bestätigte Startparameter bleiben bestehen:

- Hermes darf neue MC-Tasks anlegen
- erster Pilot enthält eine echte low-risk MC-Operation
- Plausicheck-Done ist für low-risk erlaubt
- erster Dispatch-Agent ist Spark

Morgen-Startsequenz:

1. MC Health prüfen
2. Worker-/Pickup-Proofs prüfen
3. Pilot-Task in MC anlegen
4. `GET /api/tasks/<id>` verifizieren
5. Spark mit vollständiger Spec dispatchen
6. Receipt/Evidence abwarten
7. Hermes-Closure nur mit Receipt; Atlas prüft im Pilot jeden Statuswechsel

## 22. Hermes-Grundreview — Korrekturen und Härtungen — 2026-05-06

### Kurzurteil

Der Plan ist als vertikaler Pilot grundsätzlich richtig: Er startet klein, hält MC als Audit-SSOT fest und verzögert riskantere Rechte wie Config/Cron. Für eine belastbare Umsetzung fehlten aber noch harte technische Contracts, Gate-Definitionen, Stop-Regeln, Beobachtbarkeit und eine klare Trennung zwischen **operationalem Pilotprozess** und späterer **technischer Erzwingung**.

### Korrekturen gegenüber der bisherigen Fassung

1. **Slice 1/4A darf nicht nur „Task existiert“ prüfen.**
   - Korrigiert: Ein Pilot-Task ist erst startbereit, wenn er den vorhandenen MC Execution Contract erfüllt:
     - `Task ID:`
     - `Objective:`
     - `Definition of Done:`
     - `Return format:`
     - plus Hermes-spezifisch: `Anti-Scope`, `Risk-Level`, `Verification-Gate`, `Escalation-Point`, `Allowed Agents`, `Disallowed Actions`.

2. **Dispatch ist nicht gleich Assignment.**
   - Korrigiert: Erfolgreicher Dispatch bedeutet mindestens:
     - `status=pending-pickup`
     - `dispatchState=dispatched`
     - `executionState=queued`
     - nach Worker-Acceptance: Receipt-Sequenz beginnt mit `accepted|started|progress`.

3. **„Done mit Receipt“ muss gegen MC-Felder gemappt werden.**
   - Korrigiert: Done ist nur gültig, wenn der Task terminal normalisiert ist:
     - `status=done`
     - `dispatchState=completed`
     - `executionState=done`
     - `receiptStage=result`
     - `resultSummary` enthält spezifische Evidence oder ausdrücklich `Done per Plausicheck`.

4. **Config/Cron-Rechte bleiben für Tag 1 vollständig aus.**
   - Der Decision Brief erlaubt Config/Cron prinzipiell ohne sudo und ohne Modellrouting. Für den 1-Tages-Pilot wird diese Breite bewusst enger gezogen: Tag 1 testet ausschließlich Task-Orchestrierung, Spec-Qualität, Dispatch, Receipts und Closure.

5. **MC-Ausfall darf keinen Vault-/Discord-Ersatzbetrieb auslösen.**
   - Korrigiert: Bei MC-Ausfall darf Hermes zwar Analyse/Runbooks vorbereiten, aber keine nachträgliche „operative Wahrheit“ in Vault oder Discord erzeugen. Nach MC-Recovery wird erst verifiziert, dann ggf. mit Receipt nachgetragen oder eskaliert.

6. **Atlas-Review braucht einen expliziten Gatepunkt.**
   - Korrigiert: Im Pilot prüft Atlas jeden Hermes-Statuswechsel **vor** terminaler Closure. Wenn Atlas nicht verfügbar ist, bleibt der Task in `review` oder `blocked`, nicht `done`.

## 23. Verbindlicher Tag-1-Pilot-Contract

### Pilot-Task

Arbeitstitel:

`Hermes Pilot Slice 1/4A — low-risk MC operation with Spark dispatch`

### Risiko-Klasse

`low`

### Erlaubt

- MC Health und Worker-/Pickup-Proofs read-only prüfen.
- Einen MC-Pilot-Task anlegen oder einen eindeutig passenden bestehenden Pilot-Task übernehmen.
- Genau einen Worker beauftragen: `Spark`.
- Eine low-risk Task-Spec verbessern oder eine ungefährliche MC-Pflegeoperation durchführen.
- Task auf `review` setzen, wenn Spark-Output vorliegt.
- Task auf `done` setzen, aber nur nach Atlas-Gegenprüfung und mit Receipt.

### Verboten

- Restart/Deploy direkt durch Hermes.
- `sudo`.
- Modellrouting oder Provider-Konfiguration.
- Config-/Cron-Mutation.
- zweiter Worker ohne neue Operator-Freigabe.
- `done` ohne Receipt.
- MC-Mutation bei MC-Ausfall.
- Schattenstatus in Discord/Vault als Ersatz für MC.

### Stop-Regeln

Hermes stoppt und eskaliert an Atlas/Operator, wenn eines davon eintritt:

- MC Health ist rot oder uneindeutig.
- Worker-/Pickup-Proofs zeigen kritische offene Probleme.
- Task-Spec erfüllt den Contract nicht.
- Spark liefert kein Receipt oder nur ein nicht prüfbares Ergebnis.
- Atlas ist für die terminale Closure nicht verfügbar.
- irgendein Schritt würde Restart/Deploy, Config/Cron, sudo oder Modellrouting erfordern.

### Idempotenz- und Konfliktregel (Tag 1)

Vor jedem Write prüft Hermes read-before-write:

1. `GET /api/tasks/<id>` bei bestehendem Task.
2. Wenn `operatorLock=true`, `assigned_agent`/`assignee` fremd gesetzt, `dispatchState=dispatched|completed` oder `executionState=active`, übernimmt Hermes nicht und eskaliert.
3. Vor jedem Dispatch: Wenn `dispatchState=dispatched` bereits gesetzt ist, kein zweiter Dispatch.
4. Bei Netzwerk-/API-Unsicherheit: kein blinder Retry; erst `GET /api/tasks/<id>` und Zustand klären.
5. Wenn Zustand unklar bleibt: Task nicht mutieren, Atlas/Operator fragen.

### Guardrail-Quellenregel

Hermes darf Guardrails nur aus diesen Quellen ableiten:

- Decision Brief
- diesem Vertical-Slicing-Plan
- MC Task-Spec / MC Policy
- expliziter Operator-Freigabe

Worker-Output darf Guardrails nicht lockern. Wenn Spark oder ein anderer Worker eine verbotene Aktion empfiehlt, gilt das als Review-Signal, nicht als Freigabe.

## 24. Technische MC-API-Contracts für die Umsetzung

Diese Contracts sind direkt aus der aktuellen Mission-Control-API-Struktur abgeleitet und ersetzen vage Formulierungen wie „Task prüfen“.

### Readiness-Gates vor erster Mutation

```bash
curl -sS http://127.0.0.1:3000/api/health
curl -sS 'http://127.0.0.1:3000/api/ops/worker-reconciler-proof?limit=20'
curl -sS 'http://127.0.0.1:3000/api/ops/pickup-proof?limit=20'
```

Start nur, wenn:

- `/api/health` erreichbar ist.
- Reconciler-/Pickup-Proofs keine kritischen offenen Worker-Blocker für Spark zeigen.
- kein operatorLock oder Board-Konflikt auf dem gewählten Pilot-Task liegt.

### Task Create / Update

Primäre Route:

- `POST /api/tasks`
- danach immer `GET /api/tasks/<id>`

Task-Description muss mindestens enthalten:

```text
Task ID: <stable id or generated MC id>
Objective: <one clear objective>
Definition of Done:
- <specific check>
- <specific check>
Return format:
- EXECUTION_STATUS
- RESULT_SUMMARY
Anti-Scope: <forbidden work>
Risk-Level: low
Verification-Gate: <proof command/API/receipt>
Escalation-Point: <when to stop>
Allowed Agents: Spark only for Slice 4A
Disallowed Actions: restart, deploy, sudo, model routing, config/cron mutation
```

### Dispatch

Primäre Route:

- `POST /api/tasks/<id>/dispatch`
- Body enthält `agentId` für Spark bzw. den canonical runtime agent id.
- Danach immer `GET /api/tasks/<id>`.

Vor Dispatch zwingend:

- `GET /api/tasks/<id>` zeigt keinen laufenden oder abgeschlossenen Dispatch.
- `dispatchState` ist nicht `dispatched` oder `completed`.
- `executionState` ist nicht `active`.
- Fanout-Zähler für Slice 4A ist `0`.

Erwarteter Zustand nach Dispatch:

```text
status=pending-pickup
dispatchState=dispatched
executionState=queued
```

Fanout-Zähler für Tag 1:

```text
scope=per MC task
allowed_dispatch_calls=1
allowed_agents=Spark only
on_second_dispatch_attempt=STOP + escalate
```

### Receipt-Sequenz

Primäre Route:

- `POST /api/tasks/<id>/receipt`

Erlaubte Sequenz:

```text
accepted -> started/progress -> result|blocked|failed
```

Terminale Done-Normalisierung:

```text
status=done
dispatchState=completed
executionState=done
receiptStage=result
resultSummary=<specific receipt>
```

Hinweis zur Feldvalidierung:

- `receiptStage` ist in der aktuellen MC-Codebasis als WorkerReceiptStage-Feld sichtbar; der Pilot darf sich trotzdem nicht nur auf Code-Lesung verlassen.
- Akzeptanzbeweis ist der Live-Read nach einem echten Receipt: `GET /api/tasks/<id>` muss die terminale Feldkombination zeigen.
- Wenn `receiptStage` in der Live-Antwort fehlt oder abweicht, gilt der Task nicht als terminal bewiesen; Hermes eskaliert statt `done` zu behaupten.

## 25. Slice-Neuschnitt für Tag 1

Die bisherige Slice-Reihenfolge bleibt als Roadmap erhalten, aber Tag 1 wird enger und messbarer geschnitten.

### Slice A — Baseline Snapshot (read-only)

**Objective:** Sicherstellen, dass MC und Worker-Pfad gesund genug für den Pilot sind.

**Proof:** Health + Worker-Reconciler + Pickup-Proof gespeichert/verlinkt im MC-Task.

**Stop:** irgendein kritischer Health-/Worker-Blocker.

### Slice B — Pilot-Task anlegen oder übernehmen

**Objective:** Einen auditierbaren MC-Pilot-Task mit vollständigem Execution Contract erzeugen.

**Proof:** `GET /api/tasks/<id>` zeigt vollständige Spec.

**Stop:** Contract-Marker fehlen oder Task landet nicht eindeutig im erwarteten Status.

### Slice C — Spark-Dispatch mit genau einem Worker

**Objective:** Controlled Dispatch ohne Fanout testen.

**Proof:** `status=pending-pickup`, `dispatchState=dispatched`, Spark erhält vollständige Spec.

**Stop:** Dispatch noop/rejected, falscher Agent, mehr als ein Agent, fehlende Spec.

### Slice D — Worker Receipt und Hermes Review

**Objective:** Spark-Output prüfen, ohne blind zu schließen.

**Proof:** Receipt enthält Ergebnis, Evidence und offene Punkte; Hermes setzt höchstens `review`, wenn Atlas noch nicht geprüft hat.

**Stop:** Receipt fehlt, ist generisch, widerspricht DoD oder braucht verbotene Aktionen.

### Slice E — Atlas-Gegenprüfung und Closure

**Objective:** Terminale Closure nur mit Governance-Gate.

**Proof:** Atlas bestätigt Closure; MC zeigt terminale Done-Normalisierung und `resultSummary`.

**Stop:** Atlas nicht verfügbar, Evidence nicht ausreichend, oder Plausicheck unzulässig.

## 26. Qualitätsmetriken für den 1-Tages-Pilot

Diese Metriken entscheiden GO / CHANGE / STOP, nicht nur subjektiver Eindruck.

| Metrik | Zielwert Tag 1 | Stop-/Change-Signal |
|---|---:|---|
| Hermes-created/owned Pilot-Tasks | 1 | 0 oder mehrere ohne Freigabe |
| Worker pro Task | 1 | >1 ohne Freigabe |
| Fehlende Contract-Marker | 0 | >0 beim Dispatch |
| Done ohne Receipt | 0 | jeder Treffer = STOP |
| MC-externe Statuswahrheiten | 0 | jeder Treffer = STOP |
| Verbotene Aktionsversuche | 0 | jeder Treffer = STOP |
| Atlas-Review vor Closure | 100% | <100% = CHANGE/STOP |
| Proof nach jedem Write (`GET /api/tasks/<id>`) | 100% | <100% = CHANGE |
| Spark-Receipt mit Evidence | 100% | generisches Receipt = CHANGE |

## 27. Fehlende Tiefe / offene Architekturentscheidungen

Diese Punkte sind bewusst **nicht** in Tag 1 umzusetzen, müssen aber vor dauerhafter Co-Orchestrator-Rolle entschieden werden.

1. **Technische Erzwingung vs. Operating Rule**
   - Tag 1 darf operational mit Atlas-Review laufen.
   - Dauerbetrieb braucht technische Enforcer für Fanout, done-without-receipt, forbidden actions und MC-down-mutation.

2. **Identität und Audit-Attribution**
   - MC muss unterscheiden können: `actor=Hermes`, `reviewer=Atlas`, `worker=Spark`.
   - Receipts müssen diese Rollen sichtbar halten.

3. **Idempotenz / Retry-Sicherheit**
   - Hermes darf bei Netzwerk-/API-Unsicherheit nicht doppelt Tasks anlegen oder doppelt dispatchen.
   - Erforderlich: client-side idempotency key oder Task-Title/decisionKey-Konvention.

4. **OperatorLock / Konfliktkontrolle**
   - Vor Übernahme eines bestehenden Tasks muss Hermes operatorLock, owner, assignee und dispatchState prüfen.
   - Bei Konflikt: nicht übernehmen, sondern eskalieren.

5. **Prompt-/Spec-Injection-Risiko**
   - Worker-Ergebnisse dürfen Hermes nicht dazu bringen, Guardrails zu überschreiben.
   - Guardrails kommen aus Decision Brief/Plan/MC-Policy, nicht aus Worker-Output.

6. **Kosten-/Rate-Limit-Grenzen**
   - Fanout-Limit schützt nur teilweise. Dauerbetrieb braucht Tagesbudget, Modellbudget und Cooldowns.

7. **Degraded Mode Recovery**
   - Nach MC-Recovery braucht es eine reconciliation step: Was wurde nur vorbereitet, was ist auditierbar geschrieben, was muss verworfen werden?

## 28. Konkreter Startprompt für Spark im Pilot

```text
Task ID: <MC_TASK_ID>

Objective: Prüfe und verbessere eine low-risk Hermes Task-Spec-Vorlage so, dass sie für einen einzelnen Worker ausführbar, auditierbar und testbar ist.

Definition of Done:
- Benenne fehlende oder unklare Spec-Felder.
- Liefere eine verbesserte Task-Spec im vorgegebenen Format.
- Benenne maximal 3 Risiken oder Stop-Bedingungen.
- Keine Runtime-, Config-, Cron-, Restart-, Deploy-, sudo- oder Modellrouting-Aktionen.

Anti-Scope:
- Keine MC-Mutation durch Spark.
- Kein Dispatch weiterer Agents.
- Keine Systemänderungen.
- Keine Modell-/Provider-Empfehlungen.

Risk-Level: low

Verification-Gate:
- Ergebnis enthält EXECUTION_STATUS und RESULT_SUMMARY.
- Ergebnis referenziert die erfüllten DoD-Punkte.

Escalation-Point:
- Stoppe und melde BLOCKED, wenn die Aufgabe Runtime-/Config-/Cron-/Restart-/Deploy-/sudo-/Modellrouting-Arbeit erfordert oder die Ausgangsspec fehlt.

Return format:
- EXECUTION_STATUS: done|blocked|failed
- RESULT_SUMMARY: <kurz, evidence-orientiert>
- IMPROVED_SPEC: <copy-pasteable spec>
- RISKS: <max 3>
```

## 29. Revidierte Morgen-Startsequenz

1. MC Health read-only prüfen.
2. Worker-Reconciler-/Pickup-Proofs read-only prüfen.
3. Falls grün: MC-Pilot-Task mit vollständigem Contract anlegen oder vorhandenen eindeutigen Pilot-Task übernehmen.
4. Vor Anlage/Übernahme read-before-write prüfen: kein operatorLock-Konflikt, kein fremder Assignee, kein aktiver/abgeschlossener Dispatch, kein uneindeutiger Boardzustand.
5. Sofort `GET /api/tasks/<id>` ausführen und Contract-Felder prüfen.
6. Vor Spark-Dispatch erneut `GET /api/tasks/<id>` ausführen; wenn `dispatchState=dispatched|completed` oder `executionState=active`, kein Dispatch.
7. Spark-Dispatch auslösen: genau ein Worker, kein Fanout.
8. Sofort `GET /api/tasks/<id>` ausführen und `pending-pickup/dispatched/queued` prüfen.
9. Spark-Receipt abwarten und gegen DoD prüfen.
10. Hermes setzt nur dann `review`/`done`, wenn Receipt und Evidence passen; terminales `done` erst nach Atlas-Gegenprüfung.
11. Wenn Atlas nach 30 Minuten nicht reviewt: Task bleibt `review`/`blocked`, Operator-Eskalation; kein eigenmächtiges `done`.
12. Nach jedem Write: `GET /api/tasks/<id>` Proof.
13. Abschlussreview mit Metriken aus Abschnitt 26: GO / CHANGE / STOP.

## 30. MiniMax-M2.7-Verifikation — 2026-05-06

Ein unabhängiger Verifier-Lauf mit MiniMax M2.7 wurde nach dem Hermes-Review ausgeführt.

### Ausführungsevidence

- Aufruf: OpenClaw `agent --agent spark --model minimax/MiniMax-M2.7` mit read-only Prompt.
- Ergebnis-Metadaten: `winnerProvider=minimax`, `winnerModel=MiniMax-M2.7-highspeed`, `fallbackUsed=false`, `toolSummary.failures=0`.
- Verifier-Verdict: `CHANGE`, nicht `STOP`.

### Vom Verifier bestätigte Stärken

- Slice-Sequenz ist grundsätzlich schlüssig.
- MC-Ausfall-Regel ist sauber read-only/degraded getrennt.
- Tag-1-Scope ist sinnvoll eng: keine Config/Cron/Restart/Deploy/sudo/Modellrouting-Mutation.
- Metriken in Abschnitt 26 machen GO/CHANGE/STOP überprüfbar.
- Decision-Brief-Leitplanken wurden im Plan konsistent übernommen.

### Vom Verifier identifizierte Patches und eingearbeitete Entscheidung

1. **Idempotenz / Retry-Sicherheit**
   - Befund akzeptiert und eingearbeitet in Abschnitt 23 und Abschnitt 29.
   - Regel: kein blinder Retry; vor Dispatch Zustand per `GET /api/tasks/<id>` klären.

2. **OperatorLock / Task-Konflikte vor Übernahme**
   - Befund akzeptiert und eingearbeitet in Abschnitt 23 und Abschnitt 29.
   - Regel: bei operatorLock, fremdem Assignee oder aktivem Dispatch keine Übernahme.

3. **Receipt-/Done-Feldvalidierung**
   - Befund teilweise akzeptiert und präzisiert in Abschnitt 24.
   - Korrektur: `receiptStage` ist in der aktuellen MC-Codebasis sichtbar; trotzdem zählt nur Live-Proof per `GET /api/tasks/<id>` nach Receipt.

4. **Fanout-Zähler**
   - Befund akzeptiert und eingearbeitet in Abschnitt 24.
   - Tag 1: `scope=per MC task`, `allowed_dispatch_calls=1`, `allowed_agents=Spark only`.

5. **Degraded-Mode-Recovery und Atlas-Review-Timeout**
   - Befund akzeptiert und teilweise eingearbeitet in Abschnitt 29.
   - Tag 1: Wenn Atlas nach 30 Minuten nicht reviewt, bleibt der Task `review`/`blocked` und wird an Operator eskaliert; Hermes setzt nicht eigenmächtig `done`.

6. **Prompt-/Spec-Injection gegen Guardrails**
   - Befund akzeptiert und eingearbeitet in Abschnitt 23.
   - Worker-Output darf Guardrails nicht lockern; Guardrails kommen nur aus Decision Brief, Plan, MC Policy oder expliziter Operator-Freigabe.

### Schlussfolgerung nach Verifikation

Tag-1 bleibt **CHANGE → startfähig nach den eingearbeiteten Härtungen**. Der Plan ist nicht mehr nur ein Ablaufplan, sondern enthält jetzt die minimal nötigen Read-before-write-, Idempotenz-, Fanout-, Receipt- und Review-Gates für einen kontrollierten Hermes-Co-Orchestrator-Pilot.

