---
title: Hermes Co-Orchestrator — Decision Brief
created: 2026-05-05
status: decision-brief
owner: Lenard
agents:
  - Hermes
  - Atlas
  - Security Guard
  - QA
  - Forge
  - Pixel
  - Spark
  - James
---

# Hermes Co-Orchestrator — Decision Brief

## Zielbild

Hermes soll zunächst als **Co-Orchestrator** im bestehenden OpenClaw-System eingeführt werden.

OpenClaw bleibt die operative Runtime für:
- Sessions
- Tools
- Mission Control
- Task Dispatch
- Receipts
- Gates
- Worker-Ausführung

Hermes übernimmt schrittweise:
- Orchestrierung
- Sprint-Planung
- Agent-Routing
- Learning aus Task-Ergebnissen
- Verbesserung von DoDs, Prompts und Entscheidungslogik

Atlas bleibt parallel als:
- Operator-Interface
- Governance-/Fallback-Agent
- Eskalations- und Kontrollinstanz

## Beschlossene Entscheidungen

### 1. Startrolle Hermes

**Entscheidung:** Hermes startet als **Co-Orchestrator**.

Nicht direkt als kompletter Ersatz für Atlas, sondern als lernender Orchestrator im bestehenden OpenClaw-System.

### 2. Anfangsautonomie

**Entscheidung:** Hermes darf **Low-Risk selbst ausführen**.

Erlaubt:
- P2/P3 Analyse
- Dokumentation
- Cleanup
- kleine nicht-kritische Fixes
- Board-Hygiene
- Routing kleiner Tasks

Nicht erlaubt ohne zusätzliche Freigabe:
- Config-Änderungen
- Cron-Änderungen
- Secrets/Tokens
- Restart/Service-Lifecycle
- Model-Routing
- Löschaktionen
- Mass-Dispatch
- Memory-Invariants
- externe Writes außerhalb erlaubter Kanäle

### 3. Stopprecht

**Entscheidung:** Der **Security Guard darf Hermes hard-stoppen**.

Der Guard ist keine zweite Orchestrierungsschicht, sondern ein Sicherheits- und Policy-Sentinel.

Er bewertet Aktionen als:
- allow
- warn
- require approval
- hard stop

### 4. Atlas-Rolle

**Entscheidung:** Es gibt zunächst ein **Doppel-Interface**.

- **Atlas:** Ops, Governance, Fallback, direkte Operator-Koordination
- **Hermes:** Planung, Lernen, Sprint-Orchestrierung, Agent-Routing

Die Grenze muss in der Implementierung sauber definiert werden, damit keine konkurrierenden Orchestratoren entstehen.

### 5. Konfliktentscheidung

**Entscheidung:** Bei Risiko entscheidet der Security Guard; sonst hat Hermes im Low-Risk-Bereich finale Entscheidung.

Prinzip:
- Risiko erkannt → Security Guard kann stoppen
- Low-Risk → Hermes darf entscheiden und ausführen
- Unklarheit → Hermes eskaliert

### 6. Learning / Memory

**Entscheidung:** Hermes darf **Learning Candidates** schreiben.

Hermes darf:
- Muster erkennen
- Agent-Performance auswerten
- Vorschläge für neue Regeln formulieren
- Learning Candidates dokumentieren

Hermes darf nicht eigenständig:
- dauerhafte Invariants setzen
- Governance-Regeln überschreiben
- falsche Learnings automatisch operationalisieren

Promotion in feste Regeln nur durch:
- Atlas
- User
- später ggf. definierter Review-Prozess

### 7. QA-Komponente

**Entscheidung:** QA startet als **nachgelagerter Prüfer**.

QA prüft:
- Done-Claims
- Evidence
- Tests/Build/Health
- Task-Ziel vs Ergebnis
- ob ein Learning Candidate valide ist

QA blockiert am Anfang noch nicht automatisch.

### 8. Security-Guard-Strenge

**Entscheidung:** Security Guard macht Hard-stop nur bei kritischen Aktionen.

Hard-stop-Klassen:
- Config
- Cron
- Secrets/Tokens
- Restart/Service-Lifecycle
- Model-Routing
- Löschaktionen
- Mass-Dispatch
- Memory-Invariants
- externe Writes außerhalb erlaubter Kanäle

### 9. Dispatch-Modus

**Entscheidung:** Hermes darf kleine Batches dispatchen.

Startbremse:
- Pilot zuerst mit 1 einzelner Low-Risk Task
- danach maximal 2–3 parallele Low-Risk Tasks
- kein Sprint-Fanout ohne separate Freigabe

### 10. Agent-Scope

**Entscheidung:** Hermes darf grundsätzlich alle Agents steuern.

Leitplanken:
- **Spark/James:** frei für Low-Risk Analyse, Recherche, Doku
- **Pixel:** UI/Frontend Low-Risk; kein Deploy ohne Gate
- **Forge:** Low-Risk Infra-/Codeanalyse/Fixes; kein Restart, Config, Cron, Secrets ohne Security Guard + Approval
- **Atlas:** nicht gesteuert, sondern Governance/Fallback

### 11. Kritische Eskalationen

**Entscheidung:** Hermes darf bei kritischen Eskalationen direkt den User fragen.

Form der Eskalation:
- eine konkrete Entscheidung
- Risiko kurz benennen
- Empfehlung nennen
- keine langen Agenten-Debatten

### 12. Sichtbarkeit

**Entscheidung:** Hermes arbeitet mit kurzen Checkpoints.

Sichtbar werden:
- Start/Plan
- Dispatch
- Blocker/Eskalation
- Done + Evidence

Kein Dauerlog.

### 13. Decision Ledger

**Entscheidung:** Decision Ledger lebt in **Mission Control + Vault**.

- **Mission Control:** operative Entscheidungen, Tasks, Receipts, Eskalationen
- **Vault:** dauerhafte Architekturentscheidungen, Learning Candidates, Promotions

### 14. Startreihenfolge

**Entscheidung:** Erst Architektur-Dokument, dann technische Umsetzung.

Kein technischer Umbau vor dokumentiertem Operating Model.

### 15. Dokumenttyp

**Entscheidung:** Das Architektur-Dokument wird eine **Implementierungs-Spezifikation**.

Es soll enthalten:
- Zielbild
- Rollen
- Rechte
- Verbote
- Eskalationsregeln
- Decision Ledger
- Learning Candidate Flow
- Pilotplan
- Rollback
- konkrete Umsetzungsschritte

## Empfohlene Zielarchitektur

### Rollen

#### Hermes

Primärer lernender Co-Orchestrator.

Verantwortlich für:
- Sprint-Planung
- Task-Zerlegung
- Agent-Routing
- Low-Risk Dispatch
- Learning Candidates
- Performance-Auswertung

#### Atlas

Chief-of-Staff, Governance und Fallback.

Verantwortlich für:
- Operator-facing Koordination
- kritische Entscheidungen bündeln
- finale Promotion dauerhafter Regeln
- Fallback bei Hermes-Fehlern
- Systemkohärenz

#### Security Guard

Policy- und Sicherheitsinstanz.

Verantwortlich für:
- Risk Classification
- Hard-stops bei kritischen Aktionen
- Approval-Anforderungen
- Schutz vor Secrets-/Config-/Cron-/Restart-Risiken

#### QA / Evaluator

Nachgelagerter Prüfer.

Verantwortlich für:
- Done-Claim-Prüfung
- Evidence-Prüfung
- Gate-Prüfung
- Learning-Qualität
- Agent-Performance-Signale

#### Worker Agents

Ausführungsschicht.

- Forge: Infra, Backend, Runtime, Config-Analyse
- Pixel: UI, Frontend, Browser Proof
- Spark: kleine Coding-/Ops-/Doku-Aufgaben
- James: Research
- Lens: Kosten-/Effizienz-/Read-only-Analyse

## Kernprinzipien

1. **Hermes darf orchestrieren, aber nicht unkontrolliert herrschen.**
2. **Security Guard hat Vetorecht bei Risiko.**
3. **QA prüft Ergebnisse, nicht Absichten.**
4. **Learning wird erst nach Evidence wertvoll.**
5. **Dauerhafte Regeln brauchen Promotion.**
6. **Mission Control ist Live-Spur; Vault ist Langzeitgedächtnis.**
7. **Low-Risk-Autonomie ja, kritische Systemmacht nein.**

## Nächster Schritt

Erstelle eine vollständige Implementierungs-Spezifikation auf Basis dieses Decision Briefs.

Die Spezifikation soll danach als Grundlage für einen kleinen Hermes-Pilot dienen:

1. Hermes-Agent real konfigurieren
2. Security-Guard-Rolle definieren
3. QA-Receipt-Prüfung definieren
4. Decision-Ledger-Pfade festlegen
5. einen einzelnen Low-Risk-Pilot-Task ausführen
6. Evidence + Review dokumentieren
7. danach Autonomie auf kleine Batches erweitern
