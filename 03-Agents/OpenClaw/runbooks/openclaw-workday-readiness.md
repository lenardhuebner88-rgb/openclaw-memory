# OpenClaw Workday Readiness / Morning Launchpad

## Zweck

Der Morning Launchpad Report beantwortet morgens eine einfache Frage:

> Kann ich heute direkt produktiv mit Atlas, Forge, Spark, Lens, Pixel und James arbeiten?

Er ist read-only gegen OpenClaw und Mission Control. Er repariert nichts, rotiert keine Sessions, startet keine Services neu und ändert keine Config.

## Manuell ausführen

Nur lokal anzeigen:

```bash
python3 /home/piet/.openclaw/scripts/openclaw-morning-launchpad.py
```

Vault-Report schreiben und Discord senden:

```bash
python3 /home/piet/.openclaw/scripts/openclaw-morning-launchpad.py --write-vault --send
```

JSON für Debugging:

```bash
python3 /home/piet/.openclaw/scripts/openclaw-morning-launchpad.py --json
```

## Automatischer Lauf

Systemd-Timer:

```bash
systemctl --user status openclaw-morning-launchpad.timer
```

Zeitplan:

- Montag bis Freitag
- `07:45 Europe/Berlin`
- plus bis zu `120s` RandomizedDelay

## Report-Ziele

Vault:

```text
/home/piet/vault/03-Projects/reports/daily/YYYY-MM-DD_openclaw-morning-launchpad.md
```

Discord:

```text
1495737862522405088
```

## Bewertete Bereiche

- Gateway Health
- Mission Control Health
- Board Consistency
- Worker Lifecycle
- Cronjobs
- systemd Timer / failed units
- Gateway-Logs der letzten 12h
- Agent-Sessions:
  - Atlas
  - Forge
  - Spark
  - Lens
  - Pixel
  - James
  - System Bot

## Ampel

GREEN:

- produktiv starten
- keine Rotation nötig
- kein Restart nötig

YELLOW:

- produktiv mit Einschränkung
- erst genannten Bereich prüfen
- keine langen Agent-Turns starten, wenn Atlas/Forge betroffen sind

RED:

- erst stabilisieren
- keine langen Atlas-Turns
- keine neuen Orchestrierungsjobs

## Rollback

```bash
systemctl --user disable --now openclaw-morning-launchpad.timer
rm -f /home/piet/.config/systemd/user/openclaw-morning-launchpad.service
rm -f /home/piet/.config/systemd/user/openclaw-morning-launchpad.timer
systemctl --user daemon-reload
```
