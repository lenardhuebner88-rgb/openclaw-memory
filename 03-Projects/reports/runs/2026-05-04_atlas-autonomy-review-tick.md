# Atlas Autonomy Review Tick — 2026-05-04

## Ziel

Atlas soll in Richtung Autonomie wachsen, ohne den produktiven Discord-Hotpath zu belasten.

Die wichtigste Architekturentscheidung: Der normale Atlas-Heartbeat bleibt ein reiner Liveness-Check. Autonomie läuft separat als read-only Review-Tick.

## Implementierung

Neue Dateien:

- `/home/piet/.openclaw/scripts/atlas-autonomy-review-tick.py`
- `/home/piet/.config/systemd/user/atlas-autonomy-review-tick.service`
- `/home/piet/.config/systemd/user/atlas-autonomy-review-tick.timer`

Der Tick läuft tagsüber alle 2 Stunden:

- `08:07`
- `10:07`
- `12:07`
- `14:07`
- `16:07`
- `18:07`
- `20:07`

Plus `RandomizedDelaySec=90s`, damit er nicht exakt mit anderen Cronjobs kollidiert.

## Sicherheitsmodell

Der Tick ist absichtlich kein OpenClaw `agentTurn`.

Er öffnet daher keine Atlas-Modelllane, erzeugt keinen Atlas-Cache, rotiert keine Session, startet keinen Service neu und verändert keine Mission-Control-Daten.

Er liest nur:

- Mission Control `/api/health`
- Mission Control `/api/board-consistency`
- Gateway `/health`
- `openclaw-gateway.service` Status
- `openclaw-discord-session-stability-guard.py` im Dry-run
- Atlas-/Team-Sessionstores read-only
- Gateway-Journal-Signale der letzten 2 Stunden

Optional sendet er einen kurzen Bericht über Mission Control `/api/discord/send` nach `1495737862522405088`.

## Atlas Heartbeat bleibt separat

Atlas `agents.list[id=main].heartbeat` bleibt minimal:

```json
{
  "every": "30m",
  "isolatedSession": true,
  "skipWhenBusy": true,
  "lightContext": true,
  "target": "none",
  "model": "openai-codex/gpt-5.4-mini",
  "timeoutSeconds": 120,
  "ackMaxChars": 80,
  "suppressToolErrorWarnings": true,
  "prompt": "Liveness check only. Do not read files, do not use tools, do not call APIs, do not inspect tasks, and do not continue previous work. Reply exactly HEARTBEAT_OK."
}
```

Das verhindert, dass der Heartbeat selbst Autonomie-Arbeit startet.

## Autonomie-Leiter

1. **Liveness**: Heartbeat antwortet nur `HEARTBEAT_OK`.
2. **Read-only Review**: dieser Tick prüft Lage und berichtet.
3. **Proposal Autonomy**: später maximal ein Draft-Task pro Tick.
4. **Safe Execution Lane**: später nur für freigegebene sichere Aufgabenklassen.

Aktuell ist nur Stufe 1 und 2 aktiv.

## Qualitätsgates

Vor Aktivierung:

- Python Syntaxcheck muss grün sein.
- Dry-run muss ohne Mutation laufen.
- Mission Control `/api/health` muss erreichbar sein.
- Timer muss aktiv sein.
- Kein Gateway-Restart.
- Kein Mission-Control-Restart.

Nach Aktivierung:

- `atlas-autonomy-review-tick.service` muss `0/SUCCESS` liefern.
- Der Discord-Bericht muss verständlich sein.
- `openclaw.json` bleibt unverändert.
- Atlas-Session behält keine Overrides.

## Rollback

```bash
systemctl --user disable --now atlas-autonomy-review-tick.timer
rm -f /home/piet/.config/systemd/user/atlas-autonomy-review-tick.timer
rm -f /home/piet/.config/systemd/user/atlas-autonomy-review-tick.service
systemctl --user daemon-reload
```

Das entfernt nur den Review-Tick. Atlas Heartbeat und OpenClaw-Runtime bleiben unberührt.

## Live-Validierung

Zeitpunkt: 2026-05-04 22:11 CEST.

Durchgeführt:

- `python3 -m py_compile /home/piet/.openclaw/scripts/atlas-autonomy-review-tick.py` passed.
- Dry-run via `atlas-autonomy-review-tick.py --json` passed.
- `systemd-analyze verify --user ...atlas-autonomy-review-tick.{service,timer}` ohne Fehler für diese Units.
- `systemctl --user enable --now atlas-autonomy-review-tick.timer` ausgeführt.
- Manueller Service-Lauf: `atlas-autonomy-review-tick.service` `0/SUCCESS`.
- Discord-Report gesendet nach `1495737862522405088`, messageId `1500952957670396205`.
- Gateway blieb aktiv, kein Restart: `openclaw-gateway.service` `NRestarts=0`, Startzeit `Mon 2026-05-04 21:57:05 CEST`.
- Mission Control blieb aktiv, kein Restart durch diesen Tick.
- `/home/piet/.openclaw/openclaw.json` blieb unverändert.

Erster Report:

```text
Atlas Autonomy Review Tick — GREEN
Atlas: model=openai-codex/gpt-5.5, runtime=pi, heartbeat=30m isolated=True skipBusy=True
Mission Control: status=ok open=0 inProgress=0 pendingPickup=0 stale=0
Board: status=ok issues=0
Guard: rotationNeeded=0 staleRunning=0 loadErrors=0
```

Hinweis: Während der Validierung änderte sich `/home/piet/.openclaw/cron/jobs.json` durch parallel laufende bestehende OpenClaw/systemJob-Aktivität um 22:10 CEST. Der neue Atlas Review Tick liest diese Datei nicht und schreibt sie nicht; er ist als systemd-Timer außerhalb von OpenClaw `jobs.json` implementiert.
