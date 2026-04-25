---
status: active
owner: codex
created: 2026-04-25T05:24:35Z
scope:
  - meeting-debate
  - discord-only
  - codex-path-option-b
  - phase-c-foundation
---

# Meeting Discord-Only Runner Gate Plan

## Ziel
Der Operator soll Meeting-Debates vom Handy/Discord aus starten, pruefen und abschliessen koennen, ohne Desktop-PC und ohne Terminal.

## Ausgangslage
- `/meeting-debate`, `/meeting-review`, `/meeting-council` existieren.
- Debate nutzt `claude-bot`, `codex`, `lens`.
- `meeting-runner.sh --once` startet Claude Bot und Lens/MiniMax.
- Codex-Beitrag ist aktuell manuell.
- Drei Soak-Debates sind queued und sollen nicht parallel geflutet werden.

## Entscheidung: Codex-Beitragspfad

### Schritt B - bevorzugter Pfad
**Codex via Claude-Main/codex-plugin-cc.**

Warum:
- Kein neuer Homeserver-Codex-Daemon.
- Kein direkter rekursiver Codex-Spawn aus der laufenden Codex-Session.
- Passt zur bestehenden Claude/Codex-Bruecke.
- Operator kann weiterhin kontrollieren, wann Codex als Gegenstimme schreibt.

Was B liefern muss:
- Install-/Nutzungsanleitung fuer Claude Main bleibt im Vault.
- Discord-Status zeigt klar `next-action=append-codex-rebuttal`.
- Statuspost liefert einen copy/paste Prompt fuer Claude Main / Codex Plugin.

### Phase C - Grundlage, noch nicht aktiv
**Homeserver Codex Workerpfad vorbereiten, aber nicht aktivieren.**

Grundlagen:
- eigenes Script spaeter, z. B. `spawn-codex-meeting.sh`
- Default `--dry-run`
- Timeout, Lock, Budgetcap
- keine Session-Resume-Manipulation
- keine Ausfuehrung ohne separaten Operator-Go

Entscheidung fuer heute:
- C wird dokumentiert und durch Status-/Finalize-Schnittstellen vorbereitet.
- Kein Codex-CLI/API-Worker wird heute aktiviert.

## Implementierung in diesem Lauf

### 1. `/meeting-run-once`
Discord Command.

Verhalten:
- Operator-only.
- Readiness check:
  - keine running Meetings,
  - genau queued Meeting oder erstes queued Meeting kontrolliert starten.
- Ruft `meeting-runner.sh --once` auf.
- Postet Output gekuerzt in Discord.

### 2. `/meeting-status <meeting-id>`
Discord Command.

Verhalten:
- Operator-only.
- ruft read-only Statusposter auf.
- zeigt:
  - Meeting status,
  - participants,
  - task ids,
  - completion findings,
  - next-action,
  - Worker-Proof Kurzstatus,
  - Codex-Prompt falls Codex fehlt.

### 3. Read-only Statusposter
Script:
`/home/piet/.openclaw/scripts/meeting-status-post.sh`

Default:
- read-only,
- gibt Markdown/Plaintext fuer Discord aus,
- keine Datei-Mutation.

### 4. Dry-run-first Finalize Helper
Script:
`/home/piet/.openclaw/scripts/meeting-finalize.sh`

Default:
- `--dry-run`

Execute:
- nur mit `--execute`,
- nur wenn Claude/Lens/Codex/Synthese vorhanden,
- setzt `tracked-tokens`, wenn 0, ueber einfache Dateigroessen-Schaetzung,
- setzt `status: done`,
- schreibt Runner Note.

## Gates
- `python3 -m py_compile /home/piet/.openclaw/scripts/openclaw-discord-bot.py`
- `bash -n /home/piet/.openclaw/scripts/meeting-runner.sh`
- `bash -n /home/piet/.openclaw/scripts/meeting-status-post.sh`
- `bash -n /home/piet/.openclaw/scripts/meeting-finalize.sh`
- Statusposter auf queued und done Meeting.
- Finalize dry-run auf queued/running/done Meeting.
- Discord bot restart kontrolliert und active.
- Worker proof bleibt `criticalIssues=0`.

## Zusatz-Gate 2026-04-25: Outcome Channel + 3 Real Meetings
Operator hat `#debaten-outcome` (`1497468698263552021`) als dedizierten Ergebnis-Kanal angelegt.

Abnahme:
1. Drei Meeting-/Debate-Laeufe werden sequenziell gestartet, nicht parallel.
2. Nach jedem Lauf: Statusbericht in `#debaten-outcome`.
3. Jeder Bericht nennt:
   - Meeting-ID,
   - Task-IDs,
   - Signaturstand,
   - fehlende naechste Aktion,
   - Worker-Proof Kurzstatus.
4. Atlas-Folgeaktion:
   - Wenn Meeting vollstaendig ist: Atlas bekommt einen konkreten Follow-up-Prompt/Task aus dem Meeting-Ergebnis.
   - Wenn Codex/Synthese fehlt: Status nennt zuerst den Blocker, damit Atlas nicht aus halbfertigen Debatten falsche Actions ableitet.
5. Kein Cron, kein Loop, kein paralleler Fanout.

## Nutzung nach Umsetzung
Nur Discord:

1. `/meeting-debate <thema>`
2. `/meeting-run-once`
3. nach ein paar Minuten `/meeting-status <meeting-id>`
4. wenn `next-action=append-codex-rebuttal`, Codex/Claude-Main Plugin nutzen
5. wenn alles vollstaendig: `/meeting-status <meeting-id>` bestaetigt ready; Finalize bleibt vorerst Helper/Operator-Gate

## Blocker
- Codex-Plugin-Install in Claude Main muss fuer volle Option B erledigt sein.
- Phase C ist absichtlich nicht aktiv.
- Council-Fanout bleibt verboten.
- Cron/Loop bleibt verboten.

## Umsetzungsergebnis 2026-04-25
- `/meeting-run-once` im Discord-Bot implementiert und Bot neu gestartet.
- `/meeting-status <meeting-id>` im Discord-Bot implementiert.
- `meeting-status-post.sh` read-only implementiert.
- `meeting-finalize.sh` dry-run-first implementiert.
- `meeting-runner.sh --once` blockiert jetzt, wenn bereits ein Meeting `running` ist.
- Bot sync nach Restart: 13 Slash-Commands.
- Drei abgeschlossene Debate-Reports wurden nach `#debaten-outcome` gepostet:
  - `2026-04-25_0448_debate_meeting-debate-phase3-state-machine`
  - `2026-04-25_0449_debate_meeting-debate-token-accounting`
  - `2026-04-25_0450_debate_meeting-review-minimal-features`
- Atlas wurde im Outcome-Channel mit konkreten Folgeaktionen gepingt.

## Rest-Risiken
- Der vom Operator bereitgestellte Webhook fuer `#debaten-outcome` antwortete mit `403 Forbidden`; Reporting lief stattdessen ueber den bestehenden Mission-Control `/api/discord/send` Pfad mit Channel-ID.
- Worker-Proof war am Ende `degraded`, aber `criticalIssues=0`; Ursache waren parallel laufende P1/P2-Folgeaufgaben, nicht die abgeschlossenen Meetings.
- Spark-Folgeaufgabe war zuletzt noch `pending-pickup` mit Warning-Run ohne Heartbeat. Keine weiteren Meeting-Starts, bis dieser Worker-Pfad wieder ruhig ist.
