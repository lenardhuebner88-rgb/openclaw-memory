---
status: active
owner: codex
created: 2026-04-25T04:46:15Z
scope:
  - meeting-debate
  - five-debate-soak
  - phase2-final-hardening
  - phase3-review-council-first-features
---

# Meeting Debate 5x Soak + Phase 3/4 Execution Plan

## Ziel
Meeting-Debate auf Phase-4-Readiness bringen, ohne Cron/Loop und ohne Agentenflut.

## Live-Baseline
- Pickup-Proof: ok, keine critical findings.
- Worker-Reconciler: degraded, aber `criticalIssues=0`.
- Aktuelles Meeting: `2026-04-25_0438_debate_was-w-re-der-n-chste-gr-te-hebel-zur-umsetzung`
  - Lens/MiniMax Task ist done.
  - Claude Bot Task ist in-progress.
  - Codex + Synthese + Token-Fortschreibung fehlen noch.

## Prinzipien
- Maximal 1 neues Debate-Meeting gleichzeitig aktiv dispatchen, solange das vorige noch `running` ist.
- Fuenf Meetings duerfen queued sein; Runner `--once` wird nur kontrolliert ausgefuehrt.
- Kein Cron, kein `--loop`, kein Council-Fanout.
- Review/Council bekommen zuerst Diagnose-/Readiness-Features, keine breite Automation.

## Fuenf Soak-Debates
1. `meeting-debate-phase3-state-machine`
   - Thema: Welche Completion-State-Machine braucht Meeting-Debate?
2. `meeting-debate-token-accounting`
   - Thema: Wie erzwingen wir Token-Tracking ohne Overhead?
3. `meeting-debate-review-mode`
   - Thema: Was muss `/meeting-review` minimal koennen?
4. `meeting-debate-council-mode`
   - Thema: Was muss `/meeting-council` sicher koennen, bevor Fanout erlaubt ist?
5. `meeting-debate-phase4-readiness`
   - Thema: Welche Gates braucht Phase 4 fuer Cron/Loop-Readiness?

## Phase 2 End-Hardening Gates
- Jedes aktive Debate-Meeting hat:
  - Claude-Bot-Beitrag oder klaren Pickup-Status.
  - Lens/MiniMax-Beitrag oder klaren Pickup-Status.
  - Codex-Beitrag.
  - Synthese.
  - `tracked-tokens > 0`.
- `meeting-runner.sh --dry-run` meldet klare Completion-Findings.
- Worker-Proof bleibt `criticalIssues=0`.

## Phase 3 Features
### F3.1 Review Diagnose
`meeting-runner.sh --dry-run` soll bei `mode=review` erkennen:
- `missing-author`
- `missing-codex`
- `missing-synthesis`
- `tracked-tokens-zero`

### F3.2 Council Diagnose
`meeting-runner.sh --dry-run` soll bei `mode=council` erkennen:
- `missing-atlas`
- `missing-claude-bot`
- `missing-lens`
- `missing-james`
- `missing-codex`
- `missing-synthesis`
- `tracked-tokens-zero`

### F3.3 No-Fanout Guard
`meeting-runner.sh --once` darf Council weiter nur staged setzen, nicht 5-7 Tasks erzeugen.

## Phase 4 Readiness
Erst wenn mindestens 3 von 5 Soak-Debates sauber finalisiert sind und keine Worker-Criticals entstehen:
- optional read-only Cron fuer `--dry-run` Diagnostics diskutieren.
- Execute-Cron weiter verboten bis zweites Operator-Go.

## Letztes Gate - Effektive Operator-Nutzung nur per Discord

### Zielbild
Der Operator soll am Ende **nur Discord benutzen**:

1. Operator schreibt in Discord:
   - `/meeting-debate <thema>`
   - `/meeting-review <target>`
   - `/meeting-council <topic>`
2. Homeserver erzeugt Meeting-Datei.
3. Homeserver startet die erlaubten Teilnehmer kontrolliert.
4. Homeserver prueft Completion-Findings.
5. Homeserver postet Statusberichte zurueck in Discord.
6. Operator bekommt Ergebnis + naechste Aktion, ohne Terminal und ohne Desktop.

### Was heute schon automatisch laeuft
- Discord-Bot nimmt `/meeting-debate`, `/meeting-review`, `/meeting-council` an.
- `/meeting-debate` erzeugt eine Meeting-Datei mit `claude-bot`, `codex`, `lens`.
- `meeting-runner.sh --once` dispatcht:
  - Claude Bot an `main`
  - Lens/MiniMax an `efficiency-auditor`
- `meeting-runner.sh --dry-run` erkennt:
  - fehlende Claude-/Lens-/Codex-Beitraege
  - fehlende Synthese
  - `tracked-tokens-zero`
  - `spawned-task-done-but-meeting-running`
  - `next-action:` fuer den naechsten sinnvollen Schritt
- `meeting-tokens-log.sh` schreibt Meeting-Budget-/Token-Zeilen.

### Was heute noch manuell ist
- Runner wird manuell gestartet, nicht per Cron.
- Codex-Beitrag wird manuell/extern ergaenzt, bis `codex-plugin-cc` oder ein expliziter Codex-Workerpfad produktiv ist.
- Synthese wird manuell als `codex-interim` oder spaeter durch Atlas geschrieben.
- Abschlussstatus `done` und `tracked-tokens` werden aktuell noch bewusst kontrolliert gesetzt.
- Statusberichte nach jeder Debate werden aktuell durch Codex/Operator-Lauf gepostet, nicht automatisch vom Runner.

### Braucht der Operator den Desktop-PC?
Nein, fuer den Zielbetrieb nicht.

Der Desktop-PC wird nur benoetigt fuer:
- interaktive Claude-Main-Arbeit,
- manuelle Plugin-Installation in Claude Code,
- Desktop-spezifische Obsidian-/Syncthing-Pruefung.

Fuer normale Meeting-Nutzung reicht der Homeserver, solange dort laufen:
- `mission-control.service`
- `openclaw-discord-bot.service`
- Worker-/Auto-Pickup-System
- Vault unter `/home/piet/vault`
- Discord Bot Token / Channel-Konfiguration

### Was auf dem Homeserver noch fehlt

#### H1 - Discord-Only Runner Command
Ein sicherer Discord-Befehl:

`/meeting-run-once`

Funktion:
- prueft queued Meetings,
- startet genau ein Meeting,
- postet sofort Meeting-ID + gestartete Task-IDs.

Guardrails:
- kein Cron,
- kein Loop,
- nur Operator-User,
- maximal ein running Meeting gleichzeitig.

#### H2 - Discord Completion Check
Ein Discord-Befehl:

`/meeting-status <meeting-id>`

Funktion:
- ruft Runner-Diagnose auf,
- postet `completion-finding` + `next-action`,
- zeigt Task-Status fuer Claude/Lens.

#### H3 - Auto Status Reporter nach Debate
Kleines Script:

`meeting-status-post.sh <meeting-id>`

Funktion:
- liest Meeting-Status,
- postet Kurzbericht in Discord,
- keine Mutation.

#### H4 - Finalize Helper
Ein bewusst manueller Helper:

`meeting-finalize.sh <meeting-id> --execute`

Funktion:
- nur wenn Claude/Lens/Codex/Synthese vorhanden sind,
- setzt `tracked-tokens`,
- setzt `status: done`,
- postet Abschlussbericht.

Default:
- `--dry-run`

#### H5 - Codex Beitragspfad
Option A:
- Codex bleibt manuell, Operator/Codex schreibt Rebuttal.

Option B:
- `codex-plugin-cc` in Claude Main installieren und `/codex:adversarial-review` nutzen.

Option C:
- eigener Codex-Workerpfad auf Homeserver, erst nach separatem Sicherheitsreview.

### Nutzungsablauf fuer den Operator

Heute, mit aktuellem Stand:

1. In Discord:
   `/meeting-debate Soll X oder Y umgesetzt werden?`
2. Danach einmalig durch Atlas/Codex/Operator:
   `/home/piet/.openclaw/scripts/meeting-runner.sh --once`
3. Nach einigen Minuten:
   `/home/piet/.openclaw/scripts/meeting-runner.sh --dry-run`
4. Wenn `next-action=append-codex-rebuttal`:
   Codex ergaenzt Rebuttal.
5. Wenn `next-action=write-chairman-or-interim-synthesis`:
   Atlas oder Codex-Interim schreibt Synthese.
6. Wenn keine Findings:
   Meeting auf `done`, Statusbericht in Discord.

Ziel nach H1-H4:

1. In Discord:
   `/meeting-debate Soll X oder Y umgesetzt werden?`
2. In Discord:
   `/meeting-run-once`
3. In Discord:
   `/meeting-status <meeting-id>`
4. In Discord:
   Ergebnis lesen und ggf. naechsten Prompt an Atlas geben.

### Letztes Gate fuer Phase 4
Phase 4 ist erst bereit, wenn folgende Bedingungen in drei echten Debates erfuellt sind:

- Operator nutzt nur Discord fuer Start und Status.
- Kein Desktop ist beteiligt.
- Homeserver bleibt health ok.
- Worker proof bleibt `criticalIssues=0`.
- Jede Debate liefert:
  - Claude-Beitrag,
  - Lens/MiniMax-Beitrag,
  - Codex-Rebuttal,
  - Synthese,
  - `tracked-tokens > 0`,
  - Discord-Statusbericht.
- `meeting-runner.sh --dry-run` endet ohne running Completion-Findings.

### Dedizierter Atlas-Prompt fuer den naechsten Schritt
```text
Atlas, bitte uebernimm als naechsten Sprint "Meeting Discord-Only Runner Gate".

Read first:
- /home/piet/vault/03-Agents/codex/plans/2026-04-25_meeting-debate-5x-soak-phase3-4-execution-plan.md
- /home/piet/vault/03-Agents/_coordination/HANDSHAKE.md
- /home/piet/.openclaw/scripts/meeting-runner.sh
- /home/piet/.openclaw/scripts/openclaw-discord-bot.py

Ziel:
Der Operator soll Meeting-Debates nur per Discord starten und pruefen koennen.

Scope:
1. Discord Command `/meeting-run-once` hinzufuegen.
2. Discord Command `/meeting-status <meeting-id>` hinzufuegen.
3. Beide Commands operator-only.
4. Keine Cron-/Loop-Aktivierung.
5. Maximal ein running Meeting gleichzeitig.
6. Status-Output muss `completion-finding`, `next-action`, Task-IDs und Worker-Proof-Kurzstatus enthalten.

Quality Gates:
- `python3 -m py_compile /home/piet/.openclaw/scripts/openclaw-discord-bot.py`
- `bash -n /home/piet/.openclaw/scripts/meeting-runner.sh`
- Dry-run zeigt bei einer laufenden Testdatei korrekte `next-action`.
- Echter Discord-Test mit einem queued Meeting.
- Worker proof bleibt `criticalIssues=0`.

Verbote:
- Kein Cron.
- Kein `--loop`.
- Kein Council-Fanout.
- Kein direkter Session-Resume.

Abschluss:
Poste in Discord:
- Was wurde gebaut?
- Wie nutzt der Operator es?
- Welche Gates sind gruen?
- Was ist noch Phase 4 offen?
```

## Rollback
- Bot/Runner-Code kann per Git-Diff zurueckgesetzt werden.
- Meeting-Dateien sind Coordination-Artefakte; falsche Soak-Datei kann auf `status: aborted` gesetzt werden.
- Kein Cron wurde hinzugefuegt.
