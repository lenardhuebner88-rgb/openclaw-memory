---
status: proposed
owner: codex
created: 2026-04-24T21:20:00Z
target-plan: /home/piet/vault/03-Agents/agent-team-meetings-plan-2026-04-24.md
---

# Amendments: Agent-Team-Meetings 2026-04-24

Dieses Dokument ist bewusst ein Amendment-Report. Das Claude-owned Plan-Doc wurde nicht veraendert.

## A1 - Empirie-Claims korrigieren

Ersetze im Plan:

> Cross-Provider-Debate ... empirisch Single-Agent mit Self-Consistency schlaegt (ICLR 2025 MAD-Eval)

durch:

> Aktuelle MAD-Frameworks schlagen CoT/Self-Consistency nicht konsistent. Heterogene Modellkombinationen zeigen in einzelnen Konfigurationen positive Signale und sind fuer adversarial review plausibel, aber kein robuster Default-Gewinn. Deshalb bleiben Meetings eng gescoped, budgetiert und CoVe-verifiziert.

Ersetze:

> CoVe +23% GPQA

durch:

> CorrectBench zeigt fuer CoVe auf GPQA +18.85 Punkte; Self-Refine erreicht +22.13 Punkte. CoVe bleibt als Verify-Log nuetzlich, aber der +23-Claim gehoert nicht zu CoVe.

Ersetze:

> MAST-Taxonomie (5 Failure-Kategorien)

durch:

> MAST: 14 Failure-Modes in 3 Hauptkategorien: System Design, Inter-Agent Misalignment, Task Verification.

## A2 - Teilnehmer-Matrix auf 6-7 Agents anpassen

| Modus | Teilnehmer | Pflicht | Optional | Nicht-Ziel |
|---|---:|---|---|---|
| Debate | 2 aktive Debater | Claude-Seite + Codex | Atlas als Chairman, andere nur Observer/Sub-Debate-Input | 5-Agent-Round-Robin |
| Council | 5-7 | Atlas Chairman, Forge, Pixel, Lens, James, Codex | Claude Bot als Main-Synthese | volle parallele File-Writes |
| Review | 2 | Autor + Reviewer | Atlas als Recorder | Council-artige Diskussion |

## A3 - Budget-Defaults

| Modus | Default | Warnung | Hard Stop | Begruendung |
|---|---:|---:|---:|---|
| Review | 20k | 16k | 20k | Diff-/Architekturreview soll klein bleiben. |
| Debate | 30k | 24k | 30k | 2 Debater + Rebuttal + Synthese + Verify. |
| Council | 80k | 64k | 80k | 5-7 Teilnehmer brauchen mehr Raum; 50k ist knapp. |

Operator-Default aus Plan-V1 `50k` bleibt als globaler Startwert okay, aber Council sollte begruendet auf 80k skalieren oder Teilnehmerzahl auf 5 begrenzen.

## A4 - Review-Output-Regel korrigieren

Review braucht zwei Klassen:

- **Lightweight Review:** inline im aktuellen live session file, kein Meeting-File.
- **Audit/Architecture Review:** eigenes Meeting-File in `_coordination/meetings/`, inklusive CoVe-Verify-Log.

Der Pilot "Memory-Level-3-Setup (L1-L6)" ist Audit/Architecture Review und braucht deshalb ein Meeting-File.

## A5 - Cron-Strategie entschärfen

Nicht sofort "Defense Layer 15" in die Crontab schreiben.

Empfohlene Reihenfolge:

1. `meeting-tokens-log.sh` read-only bauen.
2. Manuell mit `--dry-run` gegen Pilot-Meeting testen.
3. Erst nach Operator-Go entweder:
   - Cron `*/5` mit `flock` anlegen, oder
   - bestehende Memory-/Ops-Orchestrierung nutzen.

Grund: lokale Crontab ist bereits stark belegt; mehrere historische 14-Layer-Solljobs sind systemd-migriert oder superseded.

## A6 - HANDSHAKE §6 Zieltext

Empfohlene Kurzfassung fuer `03-Agents/_coordination/HANDSHAKE.md`:

```markdown
## 6. Meeting-Modi

Trigger:
- "Team-Meeting Debate zu <topic>"
- "Team-Meeting Council zu <topic>"
- "Team-Meeting Review fuer <target>"

Teilnehmer:
- Debate: 2 aktive Debater, Claude-Seite vs Codex; Atlas Chairman; andere Observer nur mit separatem Input.
- Council: 5-7 Agents, Atlas Chairman, Forge/Pixel/Lens/James/Codex plus optional Claude Bot.
- Review: Autor + Reviewer; Meeting-File nur bei Audit/Architecture Review.

Budgets:
- Review 20k, Debate 30k, Council 80k.
- Warnung bei 80%, Hard Stop bei 100%.

R49/R50:
- Jeder File-/SHA-/Session-ID-Claim muss im CoVe-Verify-Log belegt sein.
- Meeting darf keine aktiven Session-Locks umgehen und keine Live-Agent-Dateien parallel beschreiben.
```

## A7 - Phase-1-Pilot nach STOP-Freigabe

Wenn Operator "Proceed mit Amendments" bestaetigt:

1. Template schreiben.
2. Meetings-Ordner + README schreiben.
3. HANDSHAKE §6 anhaengen.
4. `meeting-tokens-log.sh` als read-only Script mit dry-run default bauen.
5. Pilot-Review "Memory-Level-3-Setup (L1-L6)" erstellen.
6. Kein Cron ohne explizites zweites Go.

## A8 - Phase-2-Prep nach STOP-Freigabe

Plugin-Install-Anleitung muss folgende Commands enthalten:

```text
/plugin marketplace add openai/codex-plugin-cc
/plugin install codex@openai-codex
/reload-plugins
/codex:setup
!codex login
/codex:review --background
/codex:status
/codex:result
```

Failure-Modes:
- Plugin nicht verfuegbar oder Claude-Code-Plugin-Controls deaktiviert.
- Codex nicht eingeloggt oder falsche Auth-Lane.
- ChatGPT-Pro Usage-Limit erreicht.
- Background-Job haengt in `Initializing`.
- Review-Gate erzeugt Schleife und verbraucht Limits.
- Workspace nicht trusted, Projekt-Config wird nicht geladen.

## A9 - Operator-Entscheidung Option A

Am 2026-04-24T21:27Z bestaetigt: **Option A bleibt**.

Umsetzung:
- Phase 1 wird gebaut.
- `meeting-tokens-log.sh` und `meeting-runner.sh` werden als sichere Scripts bereitgestellt und getestet.
- Kein Crontab-Eintrag.
- Kein Bot-Restart.
- Keine automatische Claude-Bot-Session-Uebernahme.

Begruendung:
- `openclaw-discord-bot.service` ist lokal inactive; parallel laufen andere Discord-Services.
- Ein Cron-/Runner-Live-Deploy waere ein eigener Runtime-Eingriff.
- R50 spricht gegen Session-Resume in `7c136829`; naechster Go sollte Taskboard-Task fuer `main` verwenden.
