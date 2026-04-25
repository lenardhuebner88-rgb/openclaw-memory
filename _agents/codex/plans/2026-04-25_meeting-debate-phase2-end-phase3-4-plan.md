---
status: active
owner: codex
created: 2026-04-25T04:42:00Z
scope:
  - meeting-debate
  - minimax-observer
  - phase2-hardening
  - phase3-phase4-plan
sources:
  - https://iclr-blogposts.github.io/2025/blog/mad/
  - https://platform.minimax.io/docs/guides/text-generation
  - https://developer.nvidia.com/blog/minimax-m2-7-advances-scalable-agentic-workflows-on-nvidia-platforms-for-complex-ai-applications/
  - https://link.springer.com/article/10.1007/s44443-025-00353-3
---

# Meeting Debate - Phase 2 End-Hardening und Phase 3/4 Plan

## Ausgangslage live
- Discord-Command `/meeting-debate` erzeugt Meeting-Dateien.
- `meeting-runner.sh --once` dispatcht Claude Bot und, wenn `participants` `lens` enthaelt, Lens als MiniMax-Observer.
- Aktuelles Meeting: `2026-04-25_0438_debate_was-w-re-der-n-chste-gr-te-hebel-zur-umsetzung`
  - Status: `running`
  - Participants: `[claude-bot, codex, lens]`
  - Claude Task: `77ee2581-b64d-4edd-8b04-a96241e4537b`, aktuell `pending-pickup`
  - Lens/MiniMax Task: `4c117590-79c8-4d6e-9e93-cde3b92aa907`, aktuell `pending-pickup`
- `pickup-proof`: degraded, aber keine critical findings.
- `worker-reconciler-proof`: degraded wegen 2 offenen Runs / 4 Issues, aber `criticalIssues=0`.

## Recherche-Fazit
- MAD-Eval/ICLR 2025 warnt: Multi-Agent-Debate ist nicht automatisch besser als einfache Single-Agent-Test-Time-Strategien. Mehr Agenten nur mit klaren Rollen, Evidenzpflicht und Kostenkontrolle.
- Heterogene Debate-Ansätze zeigen Nutzen, wenn Rollen wirklich verschieden sind und ein kontrollierter Konsens-/Judge-Schritt existiert.
- MiniMax M2.7 Highspeed ist laut MiniMax-Dokumentation als schnelle Long-Context-Variante verfuegbar; NVIDIA beschreibt M2.7 als agentic/coding-orientiertes MoE-Modell mit grossem Kontext. Damit passt Lens als kurzer Reality-/Cost-/Long-Context-Observer.

## Phase 2 End-Hardening
Ziel: Debate-MVP sicher abschliessen, ohne Cron/Loop.

### P2-E1 - Dispatch-Contract stabilisieren
Status: umgesetzt.

Was gebaut wurde:
- `spawn-lens-meeting.sh` erstellt.
- Mandatory Handoff-Marker `Open:` und `Offen-Entschieden:` nachgezogen.
- Runner kann Lens/MiniMax observer dispatchen.

Gate:
- `bash -n meeting-runner.sh`
- `bash -n spawn-lens-meeting.sh`
- `python3 -m py_compile openclaw-discord-bot.py`
- Kein Cron.

### P2-E2 - Running-Meeting Drift erkennen
Status: umgesetzt.

Runner erkennt jetzt:
- `missing-claude-bot`
- `missing-codex`
- `missing-lens`, wenn Lens participant ist
- `missing-synthesis`
- `tracked-tokens-zero`
- `spawned-task-done-but-meeting-running`

Gate:
- `meeting-runner.sh --dry-run` zeigt keine Findings fuer abgeschlossene Meetings.
- Isolierter Smoke erkennt absichtlich fehlende Lens-/Token-Felder.

### P2-E3 - Aktuelles Live-Meeting fertigstellen
Status: offen.

Warten auf:
- Claude Bot Beitrag
- Lens/MiniMax Observer Beitrag
- Codex Rebuttal
- Synthese
- `tracked-tokens > 0`
- `status: done`

Gate:
- `meeting-runner.sh --dry-run` meldet `no running meetings` oder nur erklaerte Findings.
- Worker proof: `criticalIssues=0`.

## Phase 3 - Structured Debate Completion
Ziel: Atlas oder Runner kann aus einer laufenden Debate automatisch erkennen, was als naechstes fehlt.

### P3.1 - Completion-State Machine
Felder:
- `queued`
- `running:awaiting-claude`
- `running:awaiting-lens`
- `running:awaiting-codex`
- `running:awaiting-synthesis`
- `done`
- `blocked`

Umsetzung:
- Nicht sofort Frontmatter-Status erweitern, sondern zuerst Runner-Diagnose als read-only State ausgeben.
- Spaeter optional `meeting-state:` im Frontmatter.

Gate:
- Fuer jedes fehlende Element gibt es genau eine klare naechste Aktion.

### P3.2 - Atlas Action Prompt Generator
Runner gibt bei Findings einen copy-paste Prompt fuer Atlas aus:
- "Bitte schreibe Synthese fuer Meeting X."
- "Bitte warte auf Lens Task Y."
- "Bitte Codex-Rebuttal eintragen."

Gate:
- Keine automatischen Writes ausser explizit freigegeben.
- Keine rekursiven Codex-Spawns.

### P3.3 - Token Accounting Pflicht
Jeder Agent-Beitrag muss Token-Log-Zeile schreiben oder `tracked-tokens` erhoehen.

Gate:
- `tracked-tokens=0` blockiert `done`.

## Phase 4 - Controlled Automation
Ziel: Automatisierung erst nach mehreren gruenen manuellen Debates.

### P4.1 - Three-Debate Soak
Voraussetzung:
- 3 echte `/meeting-debate` Laeufe.
- Jeweils Claude + Lens + Codex + Synthese.
- Keine Criticals, keine haengenden Runs.

Gate:
- `completion-findings=0` am Ende jedes Laufs.

### P4.2 - Manual Queue Processor
Ein kleiner Befehl:
`meeting-runner.sh --complete-check`

Er liefert:
- naechster fehlender Beitrag
- verantwortlicher Agent
- Task-ID, falls vorhanden
- empfohlener Operator-/Atlas-Prompt

Kein Cron.

### P4.3 - Optional Cron erst mit zweitem Go
Wenn P4.1 und P4.2 gruen:
- Runner maximal alle 10 Minuten.
- Nur read-only Check by default.
- Execute nur fuer queued Meetings und nur mit Lock.

Rollback:
- Cron-Zeile auskommentieren.
- Bot-Service restart nur bei Command-Code-Aenderung.

## Empfehlung
Naechster konkreter Schritt:
1. Aktuelles Meeting laufen lassen, bis Claude und Lens entweder posten oder Pickup-Drift sichtbar wird.
2. Danach Meeting sauber finalisieren.
3. Dann P3.1 bauen: Completion-State Machine als read-only Runner-Ausgabe.

Nicht als naechstes tun:
- Kein Council-Fanout.
- Kein Cron.
- Kein weiterer Agent, bevor Lens/MiniMax als Observer stabil durchlaeuft.
