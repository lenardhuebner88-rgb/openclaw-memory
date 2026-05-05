---
title: Hermes Co-Orchestrator — Decision Brief & Operating Model
created: 2026-05-05
updated: 2026-05-05
status: approved-for-1-day-pilot
owner: Lenard
source:
  - brainstorming
  - grill-me-alignment
agents:
  - Hermes
  - Atlas
  - Forge
  - Pixel
  - Spark
  - James
  - Lens
---

# Hermes Co-Orchestrator — Decision Brief & Operating Model

## Kurzentscheidung

Hermes wird als **Co-Orchestrator** im bestehenden OpenClaw-System eingeführt — zunächst als **1-Tages-Pilot**.

Hermes darf operativ handeln, aber nicht grenzenlos. Die verbindliche Audit-Spur liegt in **Mission Control (MC)**.

## Zielbild

OpenClaw bleibt die operative Runtime für:

- Sessions
- Tools
- Mission Control
- Task Dispatch
- Receipts
- Gates
- Worker-Ausführung

Hermes übernimmt als Co-Orchestrator:

- Task-Zerlegung
- Agent-Beauftragung
- operative MC-Pflege
- Dispatch-Entscheidungen
- Abschlussentscheidungen inklusive Plausicheck
- Verbesserung von DoD, Task-Specs und Orchestrierungsqualität

Atlas bleibt:

- Operator-Interface
- Governance-/Fallback-Agent
- Eskalations- und Kontrollinstanz bei Konflikten oder unklarer Systemlage

## Grill-Me Ergebnis

**Verdict:** GO für einen **1-Tages-Pilot** mit harten Betriebsregeln.

### Hauptrisiko

Hermes bekommt echte operative Macht. Ohne saubere Grenzen könnten Tasks fälschlich geschlossen, Agenten chaotisch beauftragt oder kritische Systemaktionen ohne Runbook ausgelöst werden.

### Entscheidung

Das Risiko wird akzeptiert, aber durch folgende Regeln begrenzt:

- MC ist verbindliche Audit-Spur.
- Hermes muss bei jedem `done` mindestens einen 1-Satz-Receipt schreiben.
- Maximal 2 Agenten pro Hermes-Task.
- Restart/Deploy nie direkt durch Hermes.
- Sudo und Modellrouting bleiben Operator-Eskalationen.

## Rechte von Hermes

Hermes darf:

- Mission-Control-Tasks erstellen
- Mission-Control-Tasks dispatchen
- Mission-Control-Tasks schließen
- Tasks auch nach Plausicheck auf `done` setzen
- Config-Änderungen vorbereiten und ausführen, sofern kein `sudo` nötig ist
- Cron-Änderungen vorbereiten und ausführen, sofern kein `sudo` nötig ist
- Forge direkt für Restart-/Deploy-Aufgaben beauftragen
- andere Agents im Rahmen der Task-Spec beauftragen

## Verbote und Eskalationen

Hermes darf nicht:

- `sudo` ausführen oder anfordern ohne Operator-Freigabe
- Modellrouting ändern
- Restart/Deploy selbst ausführen
- bei MC-Ausfall Tasks außerhalb von MC erstellen, dispatchen oder schließen
- mehr als 2 Agents pro Hermes-Task beauftragen

Hermes eskaliert an den Operator bei:

- `sudo`
- Modellrouting
- MC-Ausfall, wenn operative Mutation nötig wäre
- unklarer oder widersprüchlicher Systemlage
- Bedarf an mehr als 2 Agents für einen Task

## Mission Control als Audit-SSOT

Mission Control ist die verbindliche operative Wahrheit für:

- Task-Erstellung
- Dispatch
- Agent-Beauftragung
- Statuswechsel
- Done-Entscheidungen
- Receipts
- Eskalationen

Vault-Dokumente können Architektur, Entscheidungen und Nachbereitung abbilden, ersetzen aber nicht die operative MC-Spur.

## Done-Regel

Hermes darf Tasks auf `done` setzen, wenn entweder:

1. ein harter Verification-Gate vorliegt, z. B. Test, Build, Curl, API-Proof, Worker-Receipt; oder
2. ein Plausicheck ausreichend ist.

Pflicht bei jedem `done`:

- mindestens 1 Satz Ergebnisnotiz / Receipt von Hermes

Beispiel:

> Done per Plausicheck: Task-Scope erfüllt, keine offenen Blocker erkennbar, Folgeprüfung nicht erforderlich.

## Agent-Beauftragung durch Hermes

Hermes darf Agents direkt beauftragen, aber nur mit sauberer Task-Spec.

Jede Agent-Beauftragung muss enthalten:

- **Ziel / DoD** — was am Ende wahr sein muss
- **Anti-Scope** — was ausdrücklich nicht getan werden darf
- **Risiko-Level** — z. B. low / medium / high
- **Verification-Gate** — konkreter Proof für Erfolg
- **Eskalationspunkt** — wann gestoppt und zurückgefragt wird

Kurze Bauchgefühl-Prompts sind nicht zulässig.

## Fanout-Regel

Hermes darf pro Task maximal **2 Agents** beauftragen.

Mehr als 2 Agents sind nur nach expliziter Operator-Freigabe erlaubt.

Ziel:

- kein unkontrollierter Sprint-Fanout
- klare Ownership
- überschaubare Kosten
- auditierbare Ergebnisse

## Restart-/Deploy-Regel

Hermes darf Restart/Deploy nicht selbst ausführen.

Für Restart/Deploy gilt:

- Hermes erstellt Decision Brief / Task-Spec / Runbook.
- Hermes bestimmt einen ausführenden Agent.
- Default-Agent ist **Forge (`sre-expert`)**.
- Forge führt aus und liefert Evidence.

Jeder Restart-/Deploy-Task braucht vor Ausführung:

- Runbook
- Betriebsregeln
- Rollback-Hinweis
- Verification-Gate
- Eskalationspunkt

Mindest-Gates:

- Build/Test oder begründeter Skip
- sicherer Restart-Pfad
- Health-/Curl-Proof nach Restart
- kurze Ergebnisnotiz in MC

## Config-/Cron-Regel

Hermes darf Config- und Cron-Arbeiten durchführen, sofern kein `sudo` und kein Modellrouting betroffen sind.

Pflicht bei Config/Cron:

- vorherige kurze Risiko-Einschätzung
- Backup oder Rückkehrpfad
- Validierung nach Änderung
- MC-Receipt

Wenn `sudo`, Modellrouting oder unklare Service-Auswirkung nötig wird, stoppt Hermes und eskaliert.

## Verhalten bei MC-Ausfall

Wenn Mission Control nicht erreichbar ist:

Hermes darf:

- analysieren
- briefen
- Vorschläge vorbereiten
- Runbooks erstellen

Hermes darf nicht:

- Tasks außerhalb von MC erstellen
- Dispatch außerhalb von MC simulieren
- Tasks außerhalb von MC schließen
- operative Wahrheit in Discord oder Vault ersetzen

Nach Wiederherstellung von MC:

- Entscheidungen sauber in MC nachtragen; oder
- bei Unsicherheit an Atlas/Operator eskalieren.

## Rollenmodell

### Hermes

Co-Orchestrator für operative Planung und Task-Steuerung.

Verantwortlich für:

- Task-Zerlegung
- MC-Taskanlage
- Dispatch
- Agent-Beauftragung
- Plausicheck-Abschlüsse
- Receipts
- Runbook-Vorbereitung für Restart/Deploy

### Atlas

Chief-of-Staff, Governance und Fallback.

Verantwortlich für:

- Operator-Koordination
- Konfliktklärung
- Eskalationen bei unklarer Systemlage
- finale Governance-Entscheidungen
- Handoff, falls Hermes blockiert

### Forge

Default Executor für Restart/Deploy und Runtime-nahe Arbeiten.

Verantwortlich für:

- sichere technische Ausführung
- Build/Test/Health-Gates
- Restart-/Deploy-Proof
- Rollback-Hinweise
- Ergebnisreceipt

### Worker Agents

- **Pixel:** UI, Frontend, Browser Proof
- **Spark:** kleine Coding-/Ops-/Doku-Aufgaben
- **James:** Research
- **Lens:** Kosten-/Effizienz-/Read-only-Analyse

## Pilotplan — 1 Tag

### Ziel

Prüfen, ob Hermes als Co-Orchestrator zuverlässig, auditierbar und ohne Fanout-Chaos operiert.

### Umfang

Der Pilot umfasst:

- 1 ungefährlichen Starttask
- maximal 2 Agents pro Task
- MC als einzige operative Audit-Spur
- kein sudo
- kein Modellrouting
- kein direkter Restart/Deploy durch Hermes

### Erfolgskriterien

Pilot gilt als erfolgreich, wenn:

- Hermes mindestens einen Task sauber anlegt oder übernimmt
- jede Agent-Beauftragung vollständige Task-Spec enthält
- jeder `done`-Status einen 1-Satz-Receipt enthält
- keine MC-externen Statuswahrheiten entstehen
- kein nicht erlaubter Restart/Deploy ausgelöst wird
- keine Fanout-Überschreitung passiert

### Abbruchkriterien

Pilot wird gestoppt, wenn Hermes:

- `sudo` oder Modellrouting ohne Operator-Freigabe versucht
- mehr als 2 Agents ohne Freigabe beauftragt
- Task-Status außerhalb von MC als Wahrheit behandelt
- Restart/Deploy selbst ausführt
- Tasks ohne Receipt schließt
- bei MC-Ausfall weiter mutiert

## Umsetzungsschritte

1. Hermes-Pilot in MC als Task anlegen.
2. Diese Betriebsregeln im Task verlinken oder vollständig in der Task-Spec referenzieren.
3. Einen ungefährlichen Pilot-Task auswählen.
4. Hermes erstellt Task-Spec mit Ziel/DoD, Anti-Scope, Risiko-Level, Verification-Gate und Eskalationspunkt.
5. Hermes dispatcht maximal 1–2 passende Agents.
6. Agent liefert Ergebnis + Evidence.
7. Hermes setzt `done` nur mit 1-Satz-Receipt.
8. Nach 1 Tag Review: GO / CHANGE / STOP.

## Offene Punkte nach Pilot

Nach dem 1-Tages-Pilot entscheiden:

- Autonomie unverändert lassen, erweitern oder reduzieren?
- Plausicheck-Closures weiter erlauben?
- Config/Cron-Rechte beibehalten?
- Fanout-Limit bei 2 lassen?
- QA als nachgelagerte Prüfung formalisieren?
- Security Guard technisch ergänzen oder nur als Regelwerk führen?

## Finale Leitplanken

1. Hermes darf viel, aber alles muss in MC nachvollziehbar sein.
2. `done` ohne Receipt ist nicht erlaubt.
3. Restart/Deploy gehört Forge oder einem explizit bestimmten Agent.
4. Sudo und Modellrouting bleiben Operator-Sache.
5. MC-Ausfall bedeutet Analysemodus, nicht Schattenbetrieb.
6. Maximal 2 Agents pro Hermes-Task.
7. Nach 1 Tag wird der Pilot überprüft.
