---
title: S-HERMES-OPENCLAW-INTEGRATION-PILOT
created: 2026-05-05
owner: Atlas
status: planned
scope: Hermes read-only review lane integration into OpenClaw/Mission Control
risk: low-to-medium
---

# S-HERMES-OPENCLAW-INTEGRATION-PILOT

## Ziel

Hermes soll zuverlässig als read-only Review-/Audit-Agent für Atlas und Mission Control nutzbar werden, ohne sofort als vollwertiger mutierender Worker in den Dispatch-Pfad zu gehen.

Primärziel:
- MC Task → Hermes Review → strukturiertes Result → `sprintOutcome v1.1` im Board.

Sekundärziel:
- Entscheidungsvorlage, ob Hermes später als echter OpenClaw-Agent `hermes` registriert werden soll.

## Ausgangslage / Evidence

- `openclaw agents list` enthält aktuell keinen Agent `hermes`.
- Frühere MC-Dispatches mit `dispatchTarget=hermes` scheiterten an `Unknown agent id "hermes"`.
- Lokales Runbook empfiehlt aktuell Hermes zunächst als CLI/Adapter-Pilot, nicht als Auto-Pickup-Worker.
- Hermes-Rolle laut Vault: Shadow-Debug/Review-Agent, read-only, PERN/Review-Format, keine stillen Mutationen.
- OpenClaw Multi-Agent-Doku unterstützt grundsätzlich isolierte Agents via `agents.list`, AgentDir, Workspace und Bindings.
- Adapter-Guardrails sind derzeit sehr grob und blocken riskante Wörter unabhängig vom Handlungskontext.

## Prinzipien

- Atlas bleibt Lead/Orchestrator.
- Forge verantwortet technische Integration, Adapter, Tests, Receipts.
- Spark entlastet Forge bei klar abgegrenzten, risikoarmen Vorarbeiten: Prompt-Templates, Runbook-Struktur, Testmatrix, Beispiel-Tasks, Review der UX/Lesbarkeit.
- Hermes bleibt in diesem Sprint read-only.
- Keine Config-/Gateway-/Restart-/Token-/Secret-Änderungen ohne explizite Operator-Freigabe.
- Kein Auto-Pickup als produktiver Hermes-Worker vor erfolgreichem Pilot.
- Long-Run-Regel: nach 2–3 schweren Toolphasen Checkpoint statt 600s-Turn riskieren.

## Anti-Scope

- Keine Secrets/Tokens ändern.
- Kein Gateway-/Config-Restart ohne Approval.
- Kein Hermes mit Sudo/Config/Restart/Delete-Rechten.
- Kein produktiver Auto-Pickup für Hermes.
- Kein Backfill alter Tasks.
- Kein Ersatz von Atlas/Forge durch Hermes.

## Sprint-Aufteilung

### T1 — Discovery & Evidence

Owner: Forge  
Support: Spark für Checklisten-/Evidence-Format

DoD:
- Hermes CLI Pfad verifiziert: `/home/piet/.hermes/hermes-agent/venv/bin/python -m hermes_cli.main`.
- `hermes-gateway.service` read-only Status geprüft.
- OpenClaw Multi-Agent-Optionen lokal dokumentiert.
- Aktueller Zustand `openclaw agents list` dokumentiert.

Quality Gate:
- Nur read-only Checks.
- Evidence mit konkreten Pfaden/Versionen/Exitcodes.

### T2 — Adapter Guardrail Fix / Design

Owner: Forge  
Support: Spark für Testmatrix und sichere Formulierungen

Problem:
- Der Adapter blockt aktuell Wörter wie `config`, auch wenn der Task nur read-only Review meint.

DoD:
- Guardrail-Konzept unterscheidet zwischen verbotener Handlung und bloßer Erwähnung.
- Pflichtmarker für erlaubte Hermes-Reviews: `TASK_TYPE: hermes-review`, `MODE: read-only only`.
- Tests für erlaubte und blockierte Fälle.

Quality Gate:
- Unit Tests grün.
- Beispiele:
  - erlaubt: „review config risk read-only“
  - blockiert: „change config“, „restart service“, „delete file", „sudo ...“

### T3 — Spark Entlastung: Prompt-/Runbook-Pack

Owner: Spark  
Reviewer: Atlas

DoD:
- Standard Hermes Review Prompt in finaler Fassung.
- MC Task Template für `hermes-review`.
- Return-Format:
  - `status`
  - `summary`
  - `evidence`
  - `risk`
  - `next_action`
- Mini-Runbook: wann Hermes nutzen / wann nicht.
- 5 Beispiel-Review-Aufgaben mit erwarteter Klassifikation.

Anti-Scope:
- Keine Codeänderung.
- Keine Config-/Service-/Task-Mutation außer eigener Task-Receipt.

Quality Gate:
- Atlas prüft auf Guardrail-Kompatibilität und Verständlichkeit.

### T4 — Manual Hermes Review Pilot

Owner: Atlas/Forge  
Support: Spark bei Prompt-Feinschliff falls nötig

DoD:
- Ein echter MC Task `hermes-review` wird erstellt.
- Hermes wird via CLI ausgeführt.
- Atlas übernimmt Hermes-Antwort als Board-Result.
- `task.sprintOutcome.schema_version = v1.1` strukturiert vorhanden.

Quality Gate:
- MC Health ok.
- Task terminal `done` oder sauber `blocked`.
- Worker-/Pickup-Proof ohne Issues.

### T5 — Adapter Real-Run Pilot

Owner: Forge

DoD:
- `HERMES_DISPATCH_DRY_RUN=0` gegen einen Testtask ausgeführt.
- Adapter ruft Hermes CLI auf.
- Result wird strukturiert in Receipt übersetzt.

Quality Gate:
- Keine Mutation außerhalb Task Receipt.
- `openRuns=0`, `issues=0` nach Abschluss.
- `sprintOutcome v1.1` persistiert.

### T6 — Decision Gate: Hermes als OpenClaw-Agent?

Owner: Atlas  
Inputs: Forge + Spark

DoD:
- Entscheidungsvorlage mit Optionen:
  - A: CLI/Adapter bleibt Standard.
  - B: Hermes als echter OpenClaw-Agent `hermes` registrieren.
  - C: Nur manuelle Review-Lane.
- Empfehlung mit Risiken, Aufwand, Rollback.

Quality Gate:
- Keine Config-Änderung in diesem Task.
- Operator-Entscheidung erforderlich für Option B.

## Gesamt-Quality-Gates

- MC Health vor/nach jeder Board-Mutation.
- Nach jeder Task-Erstellung/Dispatch: `GET /api/tasks/<id>` verifizieren.
- Jeder terminale Task mit `resultSummary` + strukturiertem `sprintOutcome v1.1`.
- Keine offenen Runs/Dispatch-Issues am Sprintende.
- Runbook und Prompt-Templates im Vault/Docs abgelegt.
- Mindestens 1 erfolgreicher manueller Hermes Review.
- Optional erst danach: Adapter Real-Run.

## Rollen

### Atlas
- Sprint-Orchestration.
- Board-Hygiene.
- Operator-Entscheidungen einholen.
- Finales Go/No-Go.

### Forge
- Technische Discovery.
- Adapter/Receipt/Tests.
- CLI-/Service-Proof.
- Quality Gates.

### Spark
- Entlastung für Forge:
  - Prompt-Pack.
  - Runbook-Text.
  - Testmatrix.
  - Beispiel-Hermes-Tasks.
  - Lesbarkeit/UX der Review-Lane.

### Hermes
- Read-only Review-Agent.
- Keine Mutationen.
- Liefert Evidenz/Risiko/Nächsten Schritt.

## Next Action

1. Atlas erstellt T1 Forge Discovery Task.
2. Atlas erstellt T3 Spark Prompt-/Runbook-Pack Task parallel.
3. Nach T1+T3: T2 Adapter Guardrail Fix entscheiden/dispatchen.
