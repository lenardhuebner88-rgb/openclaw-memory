---
title: Atlas Long-Run Timeout Analysis — Mission Control Workblock
created: 2026-05-05T13:15:12+02:00
source: Hermes Discord analysis
agent: Hermes
related:
  - Atlas
  - OpenClaw
  - Mission Control
  - session-stability
  - long-running-task-management
status: active-reference
---

# Atlas Long-Run Timeout Analysis — Mission Control Workblock

## Problem

Atlas wurde während eines wichtigen Mission-Control-Arbeitsblocks im Discord-Chat nach ca. 10 Minuten abgebrochen/failovered. Der direkte Auslöser war **nicht** eine Tool-Anzahlbegrenzung und **nicht** ein einzelner hängender Shell-Befehl, sondern der OpenClaw **Embedded-Run-Wallclock-Timer**.

Kurzfassung:

> OpenClaw hat den laufenden Atlas-Turn nach `600000ms` aktiv abgebrochen, weil `agents.defaults.timeoutSeconds = 600` erreicht wurde.

## Evidence

### Config

Aktive OpenClaw-Konfiguration:

```json
"agents": {
  "defaults": {
    "timeoutSeconds": 600
  }
}
```

Das Schema erlaubt aktuell für `agents.defaults.timeoutSeconds` maximal `600` Sekunden.

### Journal

Relevanter Logauszug:

```text
07:36:55 [agent/embedded] embedded run timeout: runId=ab14b56a-af87-4706-9611-ed8a325ee500 sessionId=a0e09bc2-f90f-441f-840d-9c4f45f9a196 timeoutMs=600000
07:36:55 [agent/embedded] Profile openai-codex:... timed out. Trying next account...
07:36:55 [agent/embedded] embedded run failover decision ... reason=timeout from=openai-codex/gpt-5.5
07:36:55 [model-fallback/decision] candidate_failed openai-codex/gpt-5.5 reason=timeout next=minimax/MiniMax-M2.7-highspeed
07:38:01 [model-fallback/decision] candidate_succeeded minimax/MiniMax-M2.7-highspeed
```

### Trajectory

Primary-Run:

```text
session.started: 2026-05-05T05:26:55.577Z
model.completed: 2026-05-05T05:36:55.604Z
```

Delta: ca. `600s`.

Trajectory-Fakten:

```json
{
  "timedOut": true,
  "idleTimedOut": false,
  "timedOutDuringToolExecution": false,
  "promptError": "request timed out | request timed out"
}
```

Interpretation:

- Kein Idle-Timeout.
- Kein einzelner Tool-Prozess war beim finalen Kill der direkte Grund.
- Der gesamte Atlas-Turn überschritt das globale 600s Run-Budget.

### Arbeitslast im Run

Der Atlas-Turn war produktiv und tool-heavy:

- ca. 19 Tool-Metas
- ca. 38 lifecycle items completed
- mehrere sichtbare Zwischenstatus-Texte
- große Kontext-/Cache-Last (`cacheRead` im hohen sechsstelligen Bereich)
- Arbeit an Mission-Control-Artefakten, `.gitignore`, ESLint/Lint-Gate, Typecheck/Test-Gates

## Root Cause

Direkter Root Cause:

> Ein wichtiger Mission-Control-Arbeitsblock wurde als einzelner Atlas-Discord-Turn ausgeführt und lief länger als das konfigurierte OpenClaw Embedded-Run-Budget von 600 Sekunden.

Das ist **keine Toolbegrenzung nach Anzahl**, sondern eine **Wallclock-Begrenzung pro Run**.

Provider-/Modellgeschwindigkeit war vermutlich ein Faktor, aber nicht der direkte Killmechanismus. Der direkte Killmechanismus war der OpenClaw-Timer.

## Risk

Wenn Atlas lange Mission-Control-Arbeiten in einem einzigen Discord-Turn ausführt:

- kann der Turn nach 600s abgebrochen werden,
- Fallback kann übernehmen, aber mit Delay und möglichem Kontext-/Arbeitsflussbruch,
- wichtige Build-/Start-/Health-Schritte können mitten in einer Sequenz unterbrochen werden,
- der User sieht ggf. scheinbar plötzliches Vergessen oder eine inkonsistente Fortsetzung.

Einfaches Hochsetzen des Timeouts ist aktuell nicht der sauberste Erstschritt, weil:

- das Schema für `agents.defaults.timeoutSeconds` maximal `600` erlaubt,
- längere globale Runs Hänger später erkennen,
- Discord-/Session-Lanes länger blockiert bleiben können.

## Recommended Policy

### 1. Lange Atlas-Arbeiten in Checkpoint-Turns schneiden

Atlas sollte bei Mission-Control-/Build-/Restart-/Test-Arbeiten nach 2–3 schweren Toolphasen einen sichtbaren Checkpoint senden:

- Was wurde erledigt?
- Welche Evidence gibt es?
- Was bleibt offen?
- Was ist der nächste sichere Schritt?

Ziel: kein einzelner Discord-Turn soll in Richtung 600s laufen.

### 2. Heavy Work an Subagents/Tasks delegieren

Wenn ein Schritt voraussichtlich lange dauert, z.B.:

- `npm install`
- `npm run build`
- Typecheck/Lint full-suite
- Playwright/Vitest breite Gates
- Mission-Control Restart/Healthcheck-Sequenzen
- größere Git-Cleanup-Arbeit

soll Atlas bevorzugt einen spezialisierten Worker/Task nutzen und selbst Kontextanker/Koordinator bleiben.

### 3. Long-run Guardrail für Atlas

Atlas sollte intern die Regel übernehmen:

> Wenn ein Schritt wahrscheinlich >5 Minuten oder >10 Toolcalls braucht: nicht weiter im Main-Discord-Turn durcharbeiten. Checkpoint senden, Subagent nutzen oder gezielt eine Continuation vorbereiten.

### 4. Timeout-Architektur nur gezielt erweitern

Falls später echte approved Long-Runs nötig sind, sollte das nicht global passieren, sondern als expliziter Modus, z.B.:

- `approved mission-control maintenance run`
- sichtbare Fortschrittsmeldungen alle paar Minuten
- begrenzte Obergrenze, z.B. 20–30 Minuten
- klare Abort-/Recovery-Regeln

Das wäre eine OpenClaw-Feature-/Schema-Änderung, nicht nur eine einfache Config-Anpassung.

## Atlas Handoff Prompt

```text
Atlas, bitte berücksichtige die Hermes-Analyse zum Mission-Control-Timeout: Der letzte lange Mission-Control-Arbeitsblock wurde nicht wegen Tool-Anzahl gekillt, sondern weil ein einzelner Discord-Turn das OpenClaw Embedded-Run-Budget von 600s überschritten hat. Bitte plane die nächsten Schritte so, dass lange Build/Test/Restart-Arbeiten in Checkpoint-Turns oder Worker-Tasks zerlegt werden: nach 2–3 schweren Toolphasen kurz Zwischenstand + Evidence + nächster Schritt senden; heavy Gates an Forge/SRE delegieren, statt alles im Main-Turn zu halten. Ziel: Kontext stabil halten und keinen wichtigen Schritt durch den 600s Run-Timer verlieren.
```

## Link

Obsidian-Link: [[atlas-long-run-timeout-analysis-2026-05-05]]

Pfad: `03-Agents/Hermes/atlas-long-run-timeout-analysis-2026-05-05.md`
