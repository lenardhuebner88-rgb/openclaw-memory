---
status: active
owner: codex
created: 2026-04-25T05:59:49Z
scope:
  - worker-hardening
  - meeting-review-hardening
  - phase-c-codex-path
  - 2h-active-monitoring
---

# 2h Meeting/Worker Hardening + Phase C Plan

## Ziel
Die naechsten zwei Stunden werden aktiv begleitet:
- Worker-System ruhig halten.
- Meeting-/Debate-/Review-Pfad praktisch pruefen.
- Phase C als sicherer Codex-Beitragspfad vorbereiten.
- Alle 15 Minuten Status in Discord `1495737862522405088`.

## Ausgangslage
- `mission-control.service`: active.
- `openclaw-discord-bot.service`: active.
- Worker-Proof Baseline: `ok`, `criticalIssues=0`, `openRuns=0`.
- Keine running Meetings.
- Zwei queued Debates:
  - `2026-04-25_0451_debate_meeting-council-safe-mode`
  - `2026-04-25_0452_debate_phase4-readiness-gates`

## Phase C Scope
Phase C bedeutet: Codex-Beitragspfad auf dem Homeserver vorbereiten.

Erlaubt in diesem Lauf:
- `spawn-codex-meeting.sh` als dry-run-first Helper.
- Konkreter Prompt/Command-Vorschlag fuer Codex-Beitrag.
- Lock-, Timeout-, Budget- und Statuschecks.
- Integration in Statusposter als naechste Aktion.

Nicht erlaubt in diesem Lauf:
- Kein Cron.
- Kein dauerhafter Codex-Daemon.
- Kein automatischer rekursiver Codex-Spawn aus dem Runner.
- Kein Force-Execute ohne separates explizites Enable-Flag.

## Umsetzungsschritte
1. Live-Monitor Baseline posten.
2. `spawn-codex-meeting.sh` bauen:
   - Default `--dry-run`.
   - `--meeting-id <id>` Pflicht.
   - Erkennt Meeting-Datei, Modus, Status, Budget, fehlende Signaturen.
   - Gibt Codex-Prompt und optionalen `codex exec` Vorschlag aus.
   - `--execute` nur mit `CODEX_MEETING_PHASE_C_ENABLED=1`; sonst verweigern.
3. Statusposter erweitern:
   - Bei fehlendem Codex-Beitrag Phase-C Helper nennen.
   - Weiterhin read-only.
4. Runner-Text aktualisieren:
   - Codex-Pfad = Phase C helper/manual until explicit execute enable.
5. Gates:
   - `bash -n` fuer alle Meeting-Scripts.
   - `meeting-status-post.sh` auf queued und done Meeting.
   - `spawn-codex-meeting.sh --dry-run` auf queued/running/done Meeting.
   - Worker-Proof bleibt ohne Criticals.
6. 15-Minuten-Reports:
   - Services.
   - Worker-Proof.
   - Meeting-Queue/running.
   - Offene Blocker.
   - Minimal-Fixes falls angewandt.

## Go/No-Go
Go:
- Services active.
- Worker-Proof `criticalIssues=0`.
- Kein running Meeting vor Start eines neuen Laufs.

No-Go:
- `criticalIssues>0`.
- Mehr als ein running Meeting.
- Offener Run ohne Heartbeat, der nicht innerhalb eines normalen Pickup-Zyklus erklaerbar ist.
- Discord-Bot nicht active.

## Erwarteter Endzustand
Nach zwei Stunden liegt ein klarer Prozess vor:
1. `/meeting-debate`, `/meeting-review`, `/meeting-council` legen Dateien an.
2. `/meeting-run-once` startet genau einen Lauf.
3. `/meeting-status` erklaert Fortschritt und naechste Aktion.
4. Phase C Helper erzeugt oder spaeter ausfuehrt den Codex-Beitrag.
5. `meeting-finalize.sh --dry-run` prueft Abschluss.
6. Finalize `--execute` nur nach bestandenen Gates.

## Umsetzung 2026-04-25
- Phase C Helper gebaut: `/home/piet/.openclaw/scripts/spawn-codex-meeting.sh`.
- Statusposter nennt Phase-C Helper bei fehlendem Codex-Beitrag.
- Runner-Spawn-Plan nennt Phase-C statt nur manuell/plugin-driven.
- Real-Test 1:
  - `2026-04-25_0451_debate_meeting-council-safe-mode`
  - Claude Bot done, Lens done, Phase C Codex execute rc=0, Finalize done.
- Real-Test 2:
  - `2026-04-25_0452_debate_phase4-readiness-gates`
  - Claude Bot done, Lens done, Phase C Codex execute rc=0, Finalize done.
- Worker-Proof nach beiden Laeufen:
  - `status=ok`
  - `criticalIssues=0`
  - `openRuns=0`
  - `issues=0`

## Beobachtung
- Kurzzeitiges `degraded` direkt nach Dispatch ist normal, solange im naechsten Pickup-Zyklus `CLAIM_CONFIRMED` und Heartbeat folgen.
- Vorherige Spark-Folgeaufgabe hatte Claim-Timeouts; das war getrennt vom Meeting-Pfad. Waehrend der kontrollierten Meeting-Laeufe wurden Main und Lens jeweils sauber claimed.
- Phase C verursacht keine Worker-Runs, sondern laeuft als separater `codex exec` unter explizitem Enable-Flag.
