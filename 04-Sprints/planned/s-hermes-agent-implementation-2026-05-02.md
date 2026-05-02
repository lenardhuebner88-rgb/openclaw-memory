# HERMES-AGENT Implementation Plan
**Version:** 1.1-draft  
**Datum:** 2026-05-02  
**Status:** DRAFT → Atlas + Lens Review DONE → NEEDS OPERATOR DECISION  
**Owner:** James (Piet's research assistant)  
**Supersedes:** none

---

## 1. Kontext & Motivation

### 1.1 Problem Statement
Das OpenClaw-System läuft mit aktuell 10+ aktiven Agenten, 50+ Defense-Crons, Mission Control V3, und komplexen Dispatch-Mechanismen. Bei Problemen (Session-Störungen, Task-Blockaden, Cron-Ausfälle, Build-Fehler) fehlt ein **dedizierter Debug/Support-Agent**, der:

- Erste Diagnose leisten kann, bevor ein humanoider Operator eingreift
- Wiederkehrende Muster erkennen und Eskalation steuern
- Den Operator bei der Fehlersuche unterstützt (Log-Analyse, Config-Debugging, Health-Checks)

### 1.2 Ziel
Ein neuer Agent namens **Hermes** (griechischer Götterbote — der Vermittler/Debugger) wird als **Support/Debug-Bot** in das OpenClaw-System integriert. Er agiert als erster Ansprechpartner für systemische Probleme und kann eigenständig Diagnose-Scripts ausführen, Logs lesen, Configs prüfen und Resultate rapportieren.

### 1.3 Einbettung ins bestehende Agent-Ökosystem
```
Bestehende Agenten:
- main        → primärer Operator-Assistent
- james       → Research + spezielle Aufgaben
- atlas       → autonome Sprint-Planung und Koordination
- forge       → Infrastruktur + Build + Deployments
- pixel       → Frontend-Entwicklung
- lens        → Efficiency-Auditor (Follow-up Autonomie)
- spark       → Atlas-Hilfe + Webchat
- sre-expert  → SRE-spezifische Aufgabe (Deploy /memory V3, gerade blocked)
- codex       → Coding-Aufgaben (GPT-5.5)
- worker      → Dispatch-Worker
- system-bot  → System-Bot
- test-lock   → Test-Automation

NEU:
- hermes      → Support/Debug-Bot (dieser Plan)
```

**Differenzierung:**
- `sre-expert` ist dediziert auf SRE/Deployment fokussiert
- `hermes` ist der **allgemeine Support-Bot** für alle Agenten/Probleme
- `lens` ist Auditor, `hermes` ist Debugger/Diagnostiker

---

## 2. Agent-Definition

### 2.1 Name & Persona
- **Agent-ID:** `hermes`
- **Name:** Hermes
- **Emoji:** 🔧
- **Persona:** Resourcely, direkt, diagnose-fokussiert. Kein Füllwort. Kommt schnell auf den Punkt. Hat alle System-Zugriffe die nötig sind um zu helfen.
- **Vibe:** "Der freundliche Techniker, der immer weiß wo das Problem liegt"

### 2.2 Primäre Rolle
**Support/Debug-Bot** — First-Line-Diagnose für das OpenClaw-System

### 2.3 Fähigkeiten (Capability Scope)

```
DIAGNOSE (primär)
├── Log-Analyse: Session-Logs, Cron-Logs, Build-Logs lesen + filtern
├── Config-Validation: Gateway-Config, Agent-Config prüfen
├── Health-Checks: Cron-Status, Agent-Last-Activity, Session-Size
├── Connectivity-Tests: Mission-Control /health, Board-API, QMD-Index
└── Traces lesen: recent session transcripts, task receipts, dispatch history

SKRIPTE AUSFÜHREN (bounded one-shot)
├── Vordefinierte Debug-Scripts (hermes-debug/ Library)
├── openclaw status / doctor für Health-Reports
├── One-Shot exec für gezielte Diagnose-Kommandos
└── Ergebnis-Rapportierung in strukturierten Receipts

ESKALATION
├── Bei klarer Ursache: Fix-Vorschlag mit Begründung
├── Bei unbekannter Ursache: Evidence-Bündelung + Eskalationsempfehlung
├── Bei kritischen Findings: Sofort-Alert an Operator (Discord/Telegram)
└── Verweis an spezialisierte Agenten (Forge bei Infra, Atlas bei komplexen Mustern)

RAPPORTE
├── Strukturierte Diagnose-Rapporte (Problem → Evidence → Risks → Next Action)
├── Konsistente Ausgabe über alle Kanäle (Discord DM, Telegram, MC-Board-Update)
└── Follow-up-Task-Erstellung bei nachhaltigen Problemen (nur mit expliziter Freigabe)
```

### 2.4 WAS NICHT (Anti-Scope)
- Keine Build/Deploy-Ausführung (Forge's Domäne)
- Keine Agent-Prompt-Änderungen ohne explizite Freigabe
- Keine destruktiven Aktionen (rm, kill, chmod ohne Bestätigung)
- Keine Cron-Job-Erstellung ohne Operator-Approval
- Keine Änderungen an Mission-Control-Code ohne Pixel/Forge-Authorisierung
- Keine automatische Eskalation ohne klare Evidence (verhindert Alert-Stürme)

### 2.5 Trigger-Logik
```
HERMES AKTIVIERUNG (Reihenfolge):
1. MANUELL: DM an Hermes oder @hermes in #james-research
2. ALERT-BASIERT: Bei kritischen Defense-Cron-Failures (T1/T2)
3. HEARTBEAT: Optionaler 15min-Health-Check im Hintergrund

KEINE AUTOMATISCHE ESKALATION ohne klare Evidence
→ Keine Alert-Stürme durch Hermes selbst
→ Keine Doppelarbeit mit Forge/Atlas
```

### 2.6 Session/Lock-Handling
```
BEI KONFLIKT (R50 Session Locks):
- backoff: 60s + jitter, dann Retry
- max_retries: 2
- Danach: blocked receipt + Eskalation an Operator/Atlas
- Hermes annotiert jeden Run mit session-id + task-id für Traceability
```

### 2.6b Dedup/Cooldown
```
INCIDENT-KEY = <type>:<primary-resource>:<error-signature>
TTL: 15 Minuten pro Incident-Key
RATE-LIMIT: max 3 Alerts pro Stunde pro Incident-Type
BEHAVIOR: Duplicate innerhalb TTL wird zusammengeführt, nicht neu eskaliert
```

### 2.6c Board-first Enforcement
```
REGEL: No Task-ID, no diagnostic run — außer read-only quick health ping.
VOR JEDEM RUN:
1. Board-State lesen
2. Task-ID/Incident-ID annotieren
3. Keine Mutation ohne Board-Receipt + Operator/Atlas Double-Check
```

### 2.7 Diagnose-Standardpfad
```
DIAGNOSE FLOW (immer in dieser Reihenfolge):
1. health     → openclaw status / gateway /health
2. proof      → kritische Routes checken
3. logs       → tail + filter ERROR/WARN
4. hypothesis → max 2 Hypothesen, nie mehr
5. claim      → "No evidence, no claim" Regel

OUTPUT PRO BEVORRUCHENEM INCIDENT:
- Problem:     Was ist kaputt?
- Evidence:    Was wurde gefunden (exakte Log-Zeilen, Return-Codes)
- Risks:      Was könnte schiefgehen bei der Diagnose
- Next Action: Konkrete nächste Handlung (eskaliert oder behoben)
```

### 2.8 Budget & Kostenkontrolle
```
MODELL:            minimax/MiniMax-M2.7-highspeed (default)
MAX OUTPUT TOKENS: 4096 pro Incident
TIMEOUT PRO RUN:   60s
BUDGET GUARDRAIL:  Warnung bei 80%, Graceful-Decline bei 100%
```

---

## 3. Technische Architektur

### 3.1 Agent-Setup
```yaml
agent_id: hermes
model: minimax/MiniMax-M2.7-highspeed
model_fallbacks:
  - minimax/MiniMax-M2.7
  - openrouter/deepseek/deepseek-v3.2

# Zugriff auf Tools (read-only + bounded exec)
tools:
  - read                    # Log-Files, Configs
  - exec                    # Health-Checks, Scripts (one-shot, non-destructive)
  - sessions_history       # Transcript-Diagnose
  - taskboard_list_tasks   # Board-Diagnose
  - taskboard_get_task     # Einzelne Task-Details
  - memory_search          # Memory-Queries
  - memory_get             # Memory-Reads
  - gateway (config.get only)  # Config-Inspection
  - message (send only)    # Rapport-Kanal

# Keine mutierenden Tools standardmäßig
# → Eskalation immer an Operator
```

### 3.2 Debug-Script-Library (hermes-debug/)
```
/home/piet/.openclaw/scripts/hermes-debug/
├── hermes-mc-down.sh            # MC-DOWN Playbook
├── hermes-worker-stuck.sh       # WORKER-STUCK Playbook
├── hermes-session-stuck.sh      # SESSION-STUCK Playbook
├── hermes-health-check.sh      # Master Health Overview (nach MVP)
├── hermes-log-analyzer.sh       # Tail + Filter by Severity (nach MVP)
├── hermes-session-diagnose.sh  # Session Size/Activity (nach MVP)
├── hermes-cron-audit.sh         # Cron Status + Last Run (nach MVP)
├── hermes-board-diagnose.sh     # Task State Overview (nach MVP)
└── hermes-config-validator.sh  # Config Consistency Check (nach MVP)
```

### 3.3 Integration Points
- **Mission Control:** Nicht als separater Tab/Route — primär DM/Channel-Interaktion
- **Discord:** DM an Hermes (oder @hermes-Erwähnung) startet Diagnose
- **Memory:** nutzt bestehende QMD-Index + memory-Files
- **Taskboard:** liest Tasks für Board-Diagnose, erstellt keine neuen Tasks

---

## 4. Implementierung — Phasen (MVP-first)

### Phase 1: MVP Grundlagen (Tag 1)
**Verantwortlich:** James → Forge (Implementierung)  
**Exit-Kriterium:** Hermes antwortet auf DM, Health-Script gibt strukturierte Ausgabe

```
1.1 Agent-Config anlegen
    - agent_id: hermes
    - model: minimax/MiniMax-M2.7-highspeed
    - tools: read, exec (one-shot only, non-destructive),
             sessions_history, taskboard_list_tasks,
             taskboard_get_task, memory_search, memory_get,
             gateway (config.get only), message (send only)
    - workspace: /home/piet/.openclaw/workspace/hermes/

1.2 SOUL.md + IDENTITY.md für Hermes
    - Persona: "Der freundliche Techniker, der immer weiß wo das Problem liegt"
    - Resourcely, direkt, diagnose-fokussiert. Kein Füllwort.

1.3 Arbeitskontext anlegen
    - vault/03-Agents/Hermes/working-context.md
    - vault/03-Agents/Hermes/system-access.md (nur lesbare Pfade)
```

### Phase 2: MVP Debug-Script-Library (Tag 1-2)
**Verantwortlich:** Forge  
**Exit-Kriterium:** Alle 3 Playbook-Scripts lauffähig + Output validiert

```
2.1 MC-DOWN Playbook (hermes-mc-down.sh)
    - Prüft: /health, /api/health, Prozess-Status auf Port 3000
    - Output: "UP/DEGRADED/DOWN" + Evidence + Risks + Next Action

2.2 WORKER-STUCK Playbook (hermes-worker-stuck.sh)
    - Prüft: offene Tasks >2h, Worker-Sessions mit stale activity
    - Output: Task-Liste + betroffene Worker + Empfehlung

2.3 SESSION-STUCK Playbook (hermes-session-stuck.sh)
    - Prüft: aktive Sessions ohne Fortschritt, Timeouts, repeated tool failures
    - Liest: session transcripts + session status + recent process/session errors
    - Output: betroffene Session, Symptom, Evidence, Risiko, Next Action
```

### Phase 3: Discord-Integration (Tag 2)
**Verantwortlich:** Forge

```
3.1 Discord-Bot-Konfiguration
    - Hermes als Discord-User/App registrieren
    - DM-Channel für Hermes aktivieren
    - @hermes mention detection in #james-research

3.2 Rapport-Templates
    - !diagnose <topic>   → Startet Diagnose
    - !health              → Quick Health-Overview (MC-DOWN Playbook)
    - !worker-stuck        → Worker-Stuck Playbook
```

### Phase 4: Test & Validation (Tag 2-3)
**Verantwortlich:** James + Forge

```
4.1 Smoke-Tests (MVP)
    - Hermes startet, antwortet auf DM
    - MC-DOWN Playbook: korrektes UP/DEGRADED/DOWN
    - WORKER-STUCK Playbook: findet bewusst stale Task
    - SESSION-STUCK Playbook: findet absichtlich blockierte/stale Session

4.2 Security-Audit
    - Hermes kann keine destruktiven Aktionen
    - Config-Änderungen nur als Vorschlag
    - Keine Cron-Erstellung ohne Approval
```

### Phase 5: Live-Deploy + Monitoring (Tag 3)
**Verantwortlich:** Forge + Piet (Operator-Approval)

```
5.1 Hermes zu openclaw agents hinzufügen
    - openclaw agents add hermes

5.2 Health-Cron für Hermes selbst
    - Monitor dass Hermes selbst healthy ist
    - Alert bei Hermes-Down

5.3 Dokumentation
    - KB-Artikel: "Wie man Hermes nutzt"
    - Discord: How-To in #james-research pinned
```

### Phase 6: Vollversion (nach MVP approval)
**Verantwortlich:** Forge

```
6.1 Erweiterte Debug-Scripts (hermes-debug/)
    - hermes-log-analyzer.sh
    - hermes-session-diagnose.sh
    - hermes-cron-audit.sh
    - hermes-board-diagnose.sh
    - hermes-config-validator.sh

6.2 Alert-Integration
    - T1/T2 Cron-Failure → Hermes automatisch
    - Config-Watch für kritische Änderungen
```

---

## 5. Akzeptanzkriterien

### MVP Akzeptanzkriterien (Phase 1+2)

| # | Kriterium | Prüfmethode |
|---|-----------|-------------|
| AC-1 | Hermes antwortet auf DM/Erwähnung innerhalb 30s | Manual Discord-Test |
| AC-2 | MC-DOWN Playbook gibt "UP/DEGRADED/DOWN" + korrekte Evidence | absichtlicher MC-Stop |
| AC-3 | WORKER-STUCK Playbook zeigt Tasks >2h + Worker | bewusste stale Task |
| AC-4 | SESSION-STUCK Playbook zeigt stale/blockierte Session + Evidence | absichtliche stale Session |
| AC-5 | Keine destruktiven Aktionen ohne explizite Bestätigung | Security-Review + exec-log |
| AC-6 | Receipt pro Run: Problem/Evidence/Risks/Next Action | Manual Review |
| AC-7 | Budget: max 4096 output tokens pro Incident | Token-Meter |
| AC-8 | Operator kann Hermes jederzeit stoppen/deaktivieren | Operator-Befehl |

### Hermes KPI-Ziele (14-Tage Review-Fenster)

| KPI | Zielwert | Messung |
|---|---:|---|
| MTTR für häufige Incidents | -20% ggü. Baseline | Zeit von Alert → klare Next Action |
| False-positive Eskalationen | <15% | Operator/Atlas markiert unnötig |
| Blocked wegen fehlender Evidence | -25% | Receipts mit blockerReason evidence-missing |
| Duplicate Alerts | <2 pro Incident-Key / 15min | Dedup-Log |

### Vollversion Akzeptanzkriterien (Phase 3+)

| # | Kriterium | Prüfmethode |
|---|-----------|-------------|
| AC-9 | Cron-Alert-Integration funktioniert | absichtlicher T1/T2 Failure |
| AC-10 | Log-Analyse findet ERROR der letzten Stunde | bewusster ERROR in Test-Log |
| AC-11 | Board-Diagnose zeigt alle Tasks mit korrektem Status | Stichprobe 10 Tasks |
| AC-12 | Config-Validator identifiziert absichtliche Fehlkonfiguration | Eingriff in test config |
| AC-13 | Rapport ist menschenlesbar + enthält klare Handlungsempfehlung | Manual Review |

---

## 6. Offene Fragen / Operator-Entscheidungen

| # | Frage | Empfehlung | Status |
|---|-------|-----------|--------|
| O1 | Read-only oder bounded exec? | Bounded one-shot exec (kein rm, chmod, kill) | **ENTSCHEIDUNG NÖTIG** |
| O2 | Naming: "Hermes" oder anderer Name? | Hermes ist ok | **ENTSCHEIDUNG NÖTIG** |
| O3 | Kanal: Primary DM oder auch Channel-Ping? | Primär DM, Channel-@hermes als second-class | **ENTSCHEIDUNG NÖTIG** |
| O4 | Alert-Kanal: Discord oder Telegram? | Discord + Telegram als Backup | **ENTSCHEIDUNG NÖTIG** |
| O5 | Budget-Guardrail: harte Grenze oder Warnung? | Erst Warnung, dann Graceful-Decline | **ENTSCHEIDUNG NÖTIG** |
| O6 | Rollout-Phasen: wann von Shadow → Gated → Limited Autonomy? | MVP-Exit-Kriterien als Gate | OFFEN |
| O7 | Sekundär-Check vor irreversiblen Aktionen: wer? | Atlas oder Operator | **ENTSCHEIDUNG NÖTIG** |

---

## 7. Abhängigkeiten

| Dep | Beschreibung | Status |
|-----|-------------|--------|
| D1 | Discord-Bot-Setup für Hermes | Pending |
| D2 | Debug-Script-Library (Phase 2) | Pending |
| D3 | openclaw agents add permission | Operator-Approval |
| D4 | Arbeitskontext + Identity-Files | Pending |

---

## 8. Zeitplan (Geschätzt)

```
MVP (Phase 1-2):    Tag 1   (~4h Work, 1h Review)
Discord (Phase 3):  Tag 2   (~2h Work)
Test (Phase 4):     Tag 2-3 (~2h Work)
Deploy (Phase 5):   Tag 3   (Operator-Approval nötig)
Vollversion:        nach MVP Approval

Total MVP:          ~3 Tage inkrementell
Total Vollversion:   ~5 Tage total
```

---

## 9. Nächste Schritte

```
1. [Piet] Review + Approve + O1-O5 Entscheidungen
2. [Lens] Efficiency + Redundanz-Review — DONE: approve-with-changes
3. [Atlas] Operational Plausibility Check — DONE: approve-with-changes
4. [Forge] Implementierung starten nach Approval + Atlas/Lens Feedback
5. [James] Hermes-Identity + working-context vorbereiten
```

---

*Plan erstellt: 2026-05-02 von James*  
*Review-History:*  
*- Atlas (2026-05-02): 12 kritische Fragen gestellt, MVP empfohlen, Key-Gaps identifiziert (Trigger-Logik, Lock-Handling, Playbooks, Budget)*  
*- Lens (2026-05-02): approve-with-changes; P0: SESSION-STUCK statt PROOF-MISMATCH, Dedup/Cooldown, Board-first Enforcement, robustere Lock-Policy*
