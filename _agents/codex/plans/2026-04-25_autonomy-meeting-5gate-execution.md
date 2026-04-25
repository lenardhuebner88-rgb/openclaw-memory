# Autonomie + Meeting 5-Gate Execution 2026-04-25

## Ziel
Alle offenen Hebel aus der 3h-Live-Analyse aktiv uebernehmen und danach 5 kontrollierte Debate-/Meeting-Laeufe als Abschlussgate durchziehen.

## Baseline 2026-04-25T17:26Z
- `/api/health`: `ok`
- Worker-Proof: `ok`, `openRuns=0`, `issues=0`, `criticalIssues=0`
- `meeting-runner.sh --dry-run`: keine queued/running Meetings
- Phase-D-Meeting `2026-04-25_1658_debate_phase-d-next-single-run-candidate`: `done`, `tracked-tokens=4333/30000`, alle Signaturen ok.

## Offene Hebel
1. Planrunner-Noise:
   - `test-mini-plan-d` skippt dauerhaft mit `status=paused pause_reason=failed_child`.
   - Keine direkte Mutation ohne Beleg; erst nach 5-Gate erneut entscheiden.
2. Draft-Hygiene:
   - `7f8a3949` Phase-D-Vorbereitungsmeeting
   - `b29802c7` Alert-Routing vereinheitlichen
   - Beide bleiben bis nach Gate-Lauf sichtbar, werden dann priorisiert/superseded empfohlen.
3. Meeting-Autonomie:
   - Aktuell funktioniert Single-Run, aber Codex-Beitragspfad bleibt Phase-C/manual.
   - Abschlussgate prueft, ob 5 Meetings nacheinander ohne offene Runs und ohne Runner-Parallelismus terminal werden.

## 5 Abschlussgate-Meetings
Regeln:
- Immer genau ein Meeting zur Zeit.
- Vor jedem Start: `meeting-runner.sh --dry-run`, Worker-Proof `criticalIssues=0`.
- Danach: `meeting-runner.sh --once`.
- Warten bis Claude-Bot + Lens done.
- Codex-Beitrag automatisch per CLI/Phase-C Helper:
  `CODEX_MEETING_PHASE_C_ENABLED=1 /home/piet/.openclaw/scripts/spawn-codex-meeting.sh --meeting-id <id> --execute`
- `meeting-finalize.sh --dry-run`, danach `--execute` nur wenn dry-run gruen.
- Nach jedem Meeting Discord-Statusbericht.

Themen:
1. `atlas-latency-context-problem`: Optimierung langsame Antworten Atlas / Kontextproblem. **Done 2026-04-25T17:40Z.**
   - Meeting: `2026-04-25_1730_debate_atlas-latency-context-problem`
   - Ergebnis: `done`, `tracked-tokens=1900/30000`, Signaturen `claude-bot=ok`, `lens=ok`, `codex=ok`, `codex-interim=ok`.
   - Codex-Integration: automatisch via `CODEX_MEETING_PHASE_C_ENABLED=1 .../spawn-codex-meeting.sh --execute`.
   - Befund: Kontext ist als Hauptursache nicht belegt; staerkerer Hebel ist Mess-/Orchestrierungswahrheit.
   - Fix: Claude-Bot hatte Beitrag geschrieben, aber wegen `NO_REPLY` keinen terminalen Result-Receipt geliefert. Einzeltask `1e1b93cf-75f5-4a08-8dd7-63b2e21d368c` wurde nach Backup via kanonischem `/api/tasks/:id/receipt` terminal geschlossen.
   - Backup: `/home/piet/.openclaw/backup/codex-5gate-2026-04-25/gate1-terminal-receipt/`.
   - Gate: Worker-Proof danach `ok`, `openRuns=0`, `issues=0`, `criticalIssues=0`.
2. `lens-cost-report-fix`: Lens Analyse-Report und Kosten-/Tokenplan-Thema fixen. **Done 2026-04-25T17:49Z.**
   - Meeting: `2026-04-25_1742_debate_lens-cost-report-fix`
   - Ergebnis: `done`, `tracked-tokens=2400/30000`, Signaturen `claude-bot=ok`, `lens=ok`, `codex=ok`, `codex-interim=ok`.
   - Befund: MiniMax/Lens-Reporting muss Tokenplan-/Kontingent-Nutzung von echtem API-Billing-Alarm trennen.
   - Härtungsfund: multiline `participants:` wurde von Runner/Statuspfad nicht sauber erkannt; fuer diesen Lauf auf Inline-Format korrigiert und Lens gezielt nachgespawnt.
   - Follow-up: Runner/Status-Parser soll YAML-Listen korrekt erkennen oder Meeting-Template muss Inline-Participants erzwingen.
   - Gate: Worker-Proof danach `ok`, `openRuns=0`, `issues=0`, `criticalIssues=0`.
3. `meeting-debate-hardening-next`: Meeting/Debate weiter haerten und stabilisieren. **Done 2026-04-25T17:53Z.**
   - Meeting: `2026-04-25_1750_debate_meeting-debate-hardening-next`
   - Ergebnis: `done`, `tracked-tokens=4300/30000`, Signaturen `claude-bot=ok`, `lens=ok`, `codex=ok`, `codex-interim=ok`.
   - Befund: Die groessten Meeting-Hebel sind Participants-Parser/Template, Terminal-Receipt-Absicherung und Finalize als explizites Gate statt Cron-Automatik.
   - Stop-Kriterium bestaetigt: keine weitere Automatisierung bei `openRuns>0`, `criticalIssues>0`, fehlenden Signaturen oder `tracked-tokens=0` nach Fremdbeitraegen.
   - Gate: Worker-Proof danach `ok`, `openRuns=0`, `issues=0`, `criticalIssues=0`.
4. `next-concrete-features`: Naechste konkrete moegliche Features.
5. `autonomy-followup-tasks-next-level`: Empfehlung fuer Autonomie und automatische Follow-Tasks.

## Gate
Gruen nur wenn:
- 5/5 Meetings terminal `done` oder bewusst `aborted` sind.
- Worker-Proof danach `criticalIssues=0`.
- Keine queued/running Meetings uebrig.
- Discord hat nach jedem Schritt Bericht erhalten.
