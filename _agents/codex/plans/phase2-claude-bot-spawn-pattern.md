---
status: implemented-helper
owner: codex
created: 2026-04-24T21:43:00Z
helper: /home/piet/.openclaw/scripts/spawn-claude-bot-meeting.sh
---

# Phase 2D: Claude-Bot-Spawn-Pattern

## Kontext

Claude Bot ist der serverseitige Claude-Gegenpart fuer Discord-getriggerte Meetings. Laut Operator ist die relevante Discord-Bridge im Channel `1495737862522405088`, User-ID `1495736716227510402`, mit Commands `/opus` und `/quality`.

## Varianten

### Variante A: Session-Resume `7c136829`

Vorteil:
- Kein neuer Taskboard-/Worker-Overhead.
- Potenziell direkter Zugriff auf die bestehende Discord-Listener-Session.

Risiko:
- R50-Konflikt: aktive Main-/Discord-Session kann blockiert oder uebernommen werden.
- Schwerer nachweisbar im Worker-/Receipt-Proof.
- Kann eingehende Discord-Nachrichten stoeren.

### Variante B: Taskboard-Task fuer `main`

Vorteil:
- Nutzt vorhandene Dispatch-/Pickup-/Receipt-Pipeline.
- R50-konform, weil kein direkter Eingriff in eine aktive Session.
- Sichtbarer Task, Run, Heartbeat und terminaler Output.

Risiko:
- Race mit anderen Main-Tasks, wenn Main gerade gesperrt oder ausgelastet ist.
- Etwas mehr Overhead und moeglicher Claim-Timeout.

## Entscheidung

**Variante B ist implementiert.**

Begruendung:
- Amendments A2/A5 und HANDSHAKE §6 priorisieren R50 und sichtbaren Proof.
- Der fruehere Systemzustand hatte wiederholt Main-Session-Locks als echte Blocker; Session-Resume waere die riskantere Loesung.
- Taskboard-Task kann vom bestehenden Pickup-/Worker-Proof ueberwacht werden.

## Implementierung

Helper:

```bash
/home/piet/.openclaw/scripts/spawn-claude-bot-meeting.sh <meeting-id>
```

Verhalten:
- Sucht das Meeting-File unter `/home/piet/vault/03-Agents/_coordination/meetings/`.
- Erstellt eine `assigned` Task fuer `assigned_agent=main`.
- Beschreibung enthaelt alle Pflichtmarker fuer Handoff/Execution-Contract.
- Dispatcht die Task an `main` mit `runTimeoutSeconds=900`.
- Verbietet im Task selbst direkten Session-Resume auf `7c136829`.

## Test-Hinweis

Der Helper ist aktivierbar, aber in dieser Session nicht automatisch als Cron geschaltet. Fuer einen manuellen Test:

```bash
/home/piet/.openclaw/scripts/meeting-runner.sh --dry-run
/home/piet/.openclaw/scripts/meeting-runner.sh --once
```

Go/No-Go vor echtem Debate:
- `/api/ops/pickup-proof` critical=0.
- `/api/ops/worker-reconciler-proof` critical=0.
- Kein aktiver Main-Session-Lock.
