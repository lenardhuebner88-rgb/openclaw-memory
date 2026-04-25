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
4. `next-concrete-features`: Naechste konkrete moegliche Features. **Done 2026-04-25T18:00Z.**
   - Meeting: `2026-04-25_1754_debate_next-concrete-features`
   - Ergebnis: `done`, `tracked-tokens=2500/30000`, Signaturen `claude-bot=ok`, `lens=ok`, `codex=ok`, `codex-interim=ok`.
   - Empfohlene Feature-Reihenfolge: `/meeting-status <meeting-id>`, `/meeting-run-once <meeting-id>`, danach Follow-Task-Erzeugung nur mit Dry-run/Preview.
   - Begruendung: hoechster Operator-Nutzen bei geringem Autonomie-Risiko und passend zu Discord-only Bedienung.
   - Gate: Worker-Proof danach `ok`, `openRuns=0`, `issues=0`, `criticalIssues=0`.
5. `autonomy-followup-tasks-next-level`: Empfehlung fuer Autonomie und automatische Follow-Tasks. **Done 2026-04-25T18:08Z.**
   - Meeting: `2026-04-25_1801_debate_autonomy-followup-tasks-next-level`
   - Ergebnis: `done`, `tracked-tokens=4500/30000`, Signaturen `claude-bot=ok`, `lens=ok`, `codex=ok`, `codex-interim=ok`.
   - Befund: Follow-Task-Automation ist als Preview-/Approval-Flow produktionsreif, nicht als Vollautopilot.
   - Harte Regeln: max. 3 Follow-Tasks pro Meeting, kein Auto-Dispatch, Deduping gegen offene Tasks, Worker-Proof `ok`, Meeting `done`, alle Signaturen ok, Tokenstand >0 und unter Budget.
   - Fix: Claude-Bot hatte Beitrag geschrieben, blieb aber ohne terminalen Receipt bei `accepted`; Einzeltask `2323ce19-b8a4-4ccd-9e69-63f55c7da003` wurde nach Backup via kanonischem `/api/tasks/:id/receipt` terminal geschlossen. Client-Call lief in Timeout, Servermutation war erfolgreich.
   - Backup: `/home/piet/.openclaw/backup/codex-5gate-2026-04-25/gate5-terminal-receipt/`.
   - Gate: Worker-Proof danach `ok`, `openRuns=0`, `issues=0`, `criticalIssues=0`.

## Gate
Gruen nur wenn:
- 5/5 Meetings terminal `done` oder bewusst `aborted` sind. **Erfuellt: 5/5 `done`.**
- Worker-Proof danach `criticalIssues=0`. **Erfuellt: `criticalIssues=0`, `openRuns=0`, `issues=0`.**
- Keine queued/running Meetings uebrig. **Erfuellt: `meeting-runner.sh --dry-run` meldet keine queued/running Meetings.**
- Discord hat nach jedem Schritt Bericht erhalten. **Erfuellt: Gate-Reports 1-5 gesendet.**

## Abschlussbefund 2026-04-25T18:10Z
- 5 kontrollierte Debates liefen nacheinander, nicht parallel.
- Codex wurde in allen 5 Meetings automatisch per CLI/Phase-C-Helper eingebunden.
- Wiederholbare Härtungsfunde:
  1. Claude-Bot kann einen Beitrag schreiben, aber terminalen Receipt auslassen (`NO_REPLY`/accepted-only). Das braucht einen kleinen Recovery-/Guard-Helper oder eine strengere Task-Prompt-Quittung.
  2. Multiline `participants:` wird vom aktuellen Shell-Parser nicht robust erkannt. Entweder Template auf Inline fixieren oder Parser YAML-listenfest machen.
  3. Finalize darf vorerst explizites Gate bleiben; kein Cron-Autopilot, bis Parser und terminale Receipts abgesichert sind.
- Naechste produktionsreife Feature-Reihenfolge:
  1. `/meeting-status <meeting-id>`
  2. `/meeting-run-once <meeting-id>`
  3. Follow-Task-Preview mit Deduping und Approval, max. 3 Tasks pro Meeting, kein Auto-Dispatch.
