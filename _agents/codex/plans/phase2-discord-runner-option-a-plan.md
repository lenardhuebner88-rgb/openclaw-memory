---
status: option-a-prepared
owner: codex
created: 2026-04-24T21:29:00Z
---

# Phase 2 Discord/Runner Umsetzung unter Option A

## Entscheidung

Option A bleibt: **Phase 1 produktiv im Vault, Phase 2 vorbereitet, aber kein Cron-/Runner-/Bot-Restart als Blind-Deploy.**

Grund:
- `openclaw-discord-bot.service` ist aktuell inactive.
- Parallel laufen andere Discord-Services (`atlas-autonomy-discord.service`, `commander-bot.service`).
- Ein Bot-Restart oder Crontab-Erweiterung waere ein Live-Routing-Eingriff und braucht ein separates Operator-Go.

## Empfohlene Reihenfolge fuer den naechsten Go

1. Bot-Service-Ziel klaeren: Soll `openclaw-discord-bot.service` reaktiviert werden oder gehoeren Meeting-Commands in `commander-bot.service`?
2. Slash-Commands in genau dem aktiven Bot implementieren.
3. Erst danach `meeting-runner.sh` als dry-run pruefen.
4. Cron erst nach dry-run:

```cron
*/5 * * * * flock -n /tmp/meeting-tokens-log.lock /home/piet/.openclaw/scripts/meeting-tokens-log.sh >> /home/piet/.openclaw/workspace/logs/meeting-tokens-log.cron.log 2>&1
*/2 * * * * flock -n /tmp/meeting-runner.lock /home/piet/.openclaw/scripts/meeting-runner.sh --execute >> /home/piet/.openclaw/workspace/logs/meeting-runner.log 2>&1
```

## Claude-Bot-Spawn-Entscheidung

Empfehlung: **Taskboard-Task fuer `main`**, nicht `session-resume 7c136829`.

Begruendung:
- R50 verbietet das Umgehen aktiver Session-Locks.
- Taskboard-Task erzeugt sichtbaren Board-/Receipt-/Worker-Proof.
- Session-Resume in eine Discord-Listener-Session kann aktive Nachrichten blockieren.

## Go/No-Go Gate

Go nur wenn:
- aktiver Bot-Zielservice eindeutig ist,
- `/api/ops/pickup-proof` critical=0,
- `/api/ops/worker-reconciler-proof` critical=0,
- Test-Meeting-File queued -> running -> done ohne manuelle File-Korrektur funktioniert.
