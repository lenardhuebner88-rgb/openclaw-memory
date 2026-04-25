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

## Rollback
- Bot/Runner-Code kann per Git-Diff zurueckgesetzt werden.
- Meeting-Dateien sind Coordination-Artefakte; falsche Soak-Datei kann auf `status: aborted` gesetzt werden.
- Kein Cron wurde hinzugefuegt.
