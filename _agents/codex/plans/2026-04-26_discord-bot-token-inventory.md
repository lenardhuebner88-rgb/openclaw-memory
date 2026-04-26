# Discord Bot Token Inventory

Stand: 2026-04-26T20:12Z

## Ergebnis

Die Vermutung `atlas-autonomy-discord` und `commander-bot` nutzen denselben Token ist nach Hash-Vergleich falsch.

Der echte Konflikt ist:

- `openclaw-discord-bot.service` und `commander-bot.service` nutzen denselben `DISCORD_BOT_TOKEN`.
- Beide nutzen außerdem dieselbe `DISCORD_APPLICATION_ID=1495736716227510402`.
- Beide Services sind laut Host-Systemd `active`.

Das kann Discord-Gateway-/Command-Konflikte erzeugen, weil zwei laufende Prozesse mit derselben Bot-Identität arbeiten.

## Bot-Gruppen

### Gruppe A: OpenClaw Commander / Personal Commander

Token-Fingerprint: `sha256_12=aecddbc05893`

Betroffene Dateien:

- `/home/piet/.openclaw/config/openclaw-discord-bot.env`
  - Service: `openclaw-discord-bot.service`
  - Status: `active`, `disabled`
  - Script: `/home/piet/.openclaw/scripts/openclaw-discord-bot.py`
  - Zweck: OpenClaw Discord Commander, Slash Commands, Meeting Commands, MC-Anbindung.
- `/home/piet/bots/commander/.env`
  - Service: `commander-bot.service`
  - Status: `active`, `enabled`
  - Script: `/home/piet/bots/commander/bot.py`
  - Zweck: Personal Claude via Discord standalone.

Bewertung:

- Das sind aktuell keine zwei unabhängigen Bots, sondern zwei aktive Prozesse mit derselben Bot-Identität.
- Rotation eines Tokens aus Gruppe A muss beide Dateien gleichzeitig ändern, falls diese Bot-Identität bewusst geteilt bleibt.
- Besser wäre langfristig: entweder nur einen der beiden Services aktiv lassen oder Commander/OpenClaw in zwei echte Discord Apps mit getrennten Tokens aufteilen.

### Gruppe B: Atlas Autonomy / OpenClaw Gateway

Token-Fingerprint: `sha256_12=b3157d3b6f20`

Betroffene Dateien:

- `/home/piet/.openclaw/config/atlas-autonomy-discord.env`
  - Service: `atlas-autonomy-discord.service`
  - Status: `inactive`, `enabled`
  - Script: `/home/piet/.openclaw/workspace/discord-bridge/autonomy-bot.js`
  - Zweck: Atlas Autonomy Approval Bot.
- `/home/piet/.openclaw/.env`
  - Wird von Scripts/MC-Kontext als generischer Bot-Token gelesen.
- `/home/piet/.openclaw/gateway.systemd.env`
  - Service: `openclaw-gateway.service`
  - Status: `active`, `enabled`
  - Zweck: OpenClaw Gateway env-managed `DISCORD_BOT_TOKEN`.

Bewertung:

- Diese Gruppe ist nicht identisch mit Commander.
- Bei Rotation dieser Bot-Identität müssen alle drei Dateien gemeinsam geändert werden.
- Gateway-Neustart wird nötig, wenn `gateway.systemd.env` geändert wird.

### Gruppe C: Legacy Discord Bridge

Token-Fingerprint: `sha256_12=72837fac6442`

Betroffene Datei:

- `/home/piet/.openclaw/workspace/discord-secrets.env`
  - Service: `discord-bridge.service`
  - Status: `inactive`, `disabled`
  - Script: `/home/piet/.openclaw/workspace/discord-bridge/bot.js`

Bewertung:

- Aktuell nicht aktiv.
- Datei ist mit `664` zu offen; wenn dieser Token weiter existiert, sollte `chmod 600` gesetzt oder der alte Token widerrufen werden.
- Rotation nur nötig, wenn der Legacy-Bridge-Bot weiter genutzt werden soll.

## Webhooks

Neben Bot-Tokens gibt es Webhook-Secrets, z. B.:

- `HEARTBEAT_WEBHOOK_URL` in:
  - `/home/piet/.openclaw/config/openclaw-discord-bot.env`
  - `/home/piet/bots/commander/.env`
- weitere Alert-Webhooks in Scripts wie `memory-budget-meter.sh`, `alert-dispatcher.sh`, `mc-critical-alert.py`, `session-size-alert.sh`.

Diese Webhooks sind nicht dasselbe wie Bot-Tokens. Wenn der Discord-Key im Sinne von Bot-Token rotiert wird, müssen Webhooks nicht zwingend geändert werden. Wenn ein Webhook geleakt ist, muss der jeweilige Webhook separat neu erzeugt werden.

## Rotationsplan

### Wenn nur der aktive Commander/OpenClaw-Bot rotiert wird

1. Neuen Token fuer die Discord-App `1495736716227510402` im Developer Portal erzeugen.
2. Token lokal in beide Dateien schreiben:
   - `/home/piet/.openclaw/config/openclaw-discord-bot.env`
   - `/home/piet/bots/commander/.env`
3. Danach kontrolliert neu starten:
   - `openclaw-discord-bot.service`
   - `commander-bot.service`
4. Smoke:
   - `/health` oder `/status` im Commander-Channel.
   - Log auf `LoginFailure`/`401 Unauthorized` prüfen.

### Wenn Atlas Autonomy/Gateway rotiert wird

1. Neuen Token fuer die zweite Discord-App erzeugen.
2. Token lokal in drei Dateien schreiben:
   - `/home/piet/.openclaw/config/atlas-autonomy-discord.env`
   - `/home/piet/.openclaw/.env`
   - `/home/piet/.openclaw/gateway.systemd.env`
3. Danach kontrolliert neu starten:
   - `openclaw-gateway.service`
   - `atlas-autonomy-discord.service`, falls der Bot wieder aktiv genutzt werden soll.
4. Smoke:
   - Mission-Control Discord send API.
   - Gateway Discord route, falls aktiv.

### Wenn Legacy Bridge rotiert wird

1. Prüfen, ob `discord-bridge.service` wieder genutzt werden soll.
2. Falls nein: Token im Discord Developer Portal widerrufen und Datei entfernen/archivieren.
3. Falls ja: `/home/piet/.openclaw/workspace/discord-secrets.env` aktualisieren und `chmod 600` setzen.

## Empfehlung

Kurzfristig:

- Token-Gruppe A rotieren, weil dort zwei aktive Services dieselbe Bot-Identität nutzen.
- Danach entscheiden, ob `openclaw-discord-bot.service` und `commander-bot.service` wirklich parallel laufen sollen.

Mittelfristig:

- Genau eine Bot-Identität pro Prozessfamilie:
  - OpenClaw Commander / Meeting Commands
  - Personal Claude Commander
  - Atlas Autonomy Approval
- Legacy `discord-bridge.service` entweder abschalten und Token widerrufen oder sauber als eigene App dokumentieren.
