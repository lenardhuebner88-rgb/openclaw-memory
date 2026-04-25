---
status: draft-active
owner: codex
created: 2026-04-25T06:21:00Z
scope:
  - meeting
  - debate
  - review
  - phase-c
---

# Meeting / Debate / Review Operating Process

## Kurzfassung
Der Operator soll alles aus Discord anstossen koennen. Der Homeserver fuehrt nur kontrollierte Einzelschritte aus:
1. Meeting-Datei anlegen.
2. Genau einen Lauf starten.
3. Status lesen.
4. Codex-Beitrag ueber Phase C oder Claude-Main Plugin ergaenzen.
5. Dry-run-first finalisieren.

Kein Cron, kein Loop, kein automatischer Fanout ohne separates Go.

## Rollen
- `claude-bot`: Claude-Seite, kommt ueber Taskboard/Main.
- `lens`: MiniMax/Cost-/Risk-Observer, kommt ueber Taskboard `efficiency-auditor`.
- `codex`: OpenAI-Gegenstimme; Phase C Helper kann controlled `codex exec` ausfuehren.
- `atlas`: Chairman/Orchestrator; leitet Folgeaktionen aus finalisierten Ergebnissen ab.

## Discord-Bedienung

### Debate
1. `/meeting-debate <thema>`
2. `/meeting-run-once`
3. `/meeting-status <meeting-id>`
4. Warten bis Claude Bot und Lens `done/result` sind.
5. Wenn Status `append-codex-rebuttal` zeigt:
   - Phase C Helper vom Homeserver nutzen, oder
   - Codex-Beitrag ueber Claude Main/codex-plugin-cc einbringen.
6. `meeting-finalize.sh --dry-run`
7. Nur wenn dry-run ok: `meeting-finalize.sh --execute`

### Review
1. `/meeting-review <target>`
2. `/meeting-run-once`
3. `/meeting-status <meeting-id>`
4. Pflicht-Gates:
   - Target/Author-Kontext vorhanden.
   - `[codex ...]` vorhanden.
   - Synthese vorhanden.
   - CoVe-Verify-Log bei konkreten Claims nicht leer.
   - `tracked-tokens > 0`.
5. Finalize nur dry-run-first.

### Council
1. `/meeting-council <topic>`
2. Aktueller Stand: staged-only.
3. Kein 5-7-Agenten-Fanout ohne separates Operator-Go.
4. Safe-Mode-Gates vor Fanout:
   - harte Participant-Cap,
   - No-Fanout-Guard,
   - Synthese-/Completion-Gate,
   - Worker-Proof `criticalIssues=0`,
   - Rollback/Stop klar dokumentiert.

## Phase C: Codex-Beitragspfad

Helper:
`/home/piet/.openclaw/scripts/spawn-codex-meeting.sh`

Standard:
```bash
/home/piet/.openclaw/scripts/spawn-codex-meeting.sh --meeting-id <id> --dry-run
/home/piet/.openclaw/scripts/spawn-codex-meeting.sh --meeting-id <id> --print-prompt
```

Execute nur explizit:
```bash
CODEX_MEETING_PHASE_C_ENABLED=1 /home/piet/.openclaw/scripts/spawn-codex-meeting.sh --meeting-id <id> --execute
```

Sicherungen:
- Default ist dry-run.
- Execute ist per Env-Flag gesperrt.
- Lock pro Meeting unter `/tmp/openclaw-codex-meeting-<id>.lock`.
- Timeout default 900s.
- Arbeitsverzeichnis fuer Codex: `/home/piet/vault`.
- Kein Cron/Loop.
- Prompt verbietet Service-Restart und fremde Datei-Edits.

## Finalize-Prozess

Dry-run:
```bash
/home/piet/.openclaw/scripts/meeting-finalize.sh --meeting-id <id> --dry-run
```

Execute:
```bash
/home/piet/.openclaw/scripts/meeting-finalize.sh --meeting-id <id> --execute
```

Finalize blockiert bei:
- fehlender Claude-Bot-Signatur,
- fehlender Lens-Signatur, falls Lens Teilnehmer ist,
- fehlender Codex-Signatur,
- fehlender Synthese.

## Monitoring-Regeln
- Vor jedem neuen Lauf: `meeting-runner.sh --dry-run`.
- Wenn ein Meeting `running` ist: kein weiterer `/meeting-run-once`.
- Worker-Proof muss `criticalIssues=0` zeigen.
- Kurzzeitiges `degraded` direkt nach Dispatch ist ok, wenn Pickup/Heartbeat im naechsten Zyklus folgt.
- Wiederholte `claim-timeout` oder `open-run-without-heartbeat` nach normaler Pickup-Zeit = stoppen und analysieren.

## Aktueller validierter Stand 2026-04-25
- `2026-04-25_0451_debate_meeting-council-safe-mode`: done, Phase C success.
- `2026-04-25_0452_debate_phase4-readiness-gates`: done, Phase C success.
- Worker-Proof nach beiden Laeufen: ok, `criticalIssues=0`, `openRuns=0`.
