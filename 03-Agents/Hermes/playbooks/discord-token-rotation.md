---
title: Hermes Playbook - Discord Token Rotation
status: active
created: 2026-05-02
owner: Piet
scope: discord-ops
---

# Hermes Playbook - Discord Token Rotation

Use this when rotating the Piet/OpenClaw Discord bot token or when deleting an old Discord application such as Claudebridge.

## Bot Separation

- Piet/OpenClaw agents bot: app/user ID `1486895358725460069`, local service `openclaw-discord-bot.service`.
- OpenClaw Gateway Discord provider also uses the Piet/OpenClaw token via `channels.discord.token` and `gateway.systemd.env`.
- Mission Control uses `DISCORD_BOT_TOKEN` for `/api/discord/send` and execution reports.
- Hermes Agent bot is separate: app/user ID `1500199614706483210`, local service `hermes-gateway.service`, token in `/home/piet/.hermes/.env`.

Never replace the Hermes token with the Piet token.

## Files To Check

Runtime-relevant Piet/OpenClaw token locations:

```text
/home/piet/.openclaw/config/openclaw-discord-bot.env
/home/piet/.openclaw/gateway.systemd.env
/home/piet/.openclaw/.env
/home/piet/.openclaw/openclaw.json
/home/piet/.openclaw/workspace/mission-control/.env
/home/piet/.openclaw/workspace/mission-control/.env.local
```

Schema rule for `/home/piet/.openclaw/openclaw.json`:

- Valid: `channels.discord.token`
- Invalid: `channels.discord.botToken`
- Invalid: `plugins.entries.discord.token`
- Do not touch `gateway.auth.token`; it is not a Discord bot token.

## Safe Rotation Procedure

1. Decode the new token prefix to confirm the app/user ID.

```bash
python3 - <<'PY'
import base64
token = 'PASTE_TOKEN_HERE'
first = token.split('.', 1)[0]
print(base64.b64decode(first + '=' * ((4 - len(first) % 4) % 4)).decode())
PY
```

2. Backup every runtime-relevant file before editing.

```bash
backup_dir="/home/piet/backups/discord-token-rotation-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$backup_dir"
for f in \
  /home/piet/.openclaw/config/openclaw-discord-bot.env \
  /home/piet/.openclaw/gateway.systemd.env \
  /home/piet/.openclaw/.env \
  /home/piet/.openclaw/openclaw.json \
  /home/piet/.openclaw/workspace/mission-control/.env \
  /home/piet/.openclaw/workspace/mission-control/.env.local; do
  [ -f "$f" ] || continue
  mkdir -p "$backup_dir$(dirname "$f")"
  cp -a "$f" "$backup_dir$f"
done
chmod 700 "$backup_dir"
```

3. Update only the Piet/OpenClaw locations.

- In env files, set `DISCORD_BOT_TOKEN=<new-token>`.
- In `/home/piet/.openclaw/config/openclaw-discord-bot.env`, also set `DISCORD_APPLICATION_ID=<decoded-app-id>`.
- In `/home/piet/.openclaw/openclaw.json`, set `channels.discord.token` only.
- Leave `/home/piet/.hermes/.env` unchanged.

4. Validate before restart.

```bash
python3 -m json.tool /home/piet/.openclaw/openclaw.json >/dev/null
openclaw config validate
```

5. Restart only token-loading services.

```bash
systemctl --user restart openclaw-gateway.service mission-control.service openclaw-discord-bot.service
```

6. Post-verify.

```bash
systemctl --user is-active openclaw-gateway.service mission-control.service openclaw-discord-bot.service hermes-gateway.service
curl -s -o /dev/null -w "openclaw_http=%{http_code}\n" http://127.0.0.1:18789/health
curl -s -o /dev/null -w "mc_http=%{http_code}\n" http://127.0.0.1:3000/api/health
tail -80 /home/piet/.openclaw/workspace/logs/openclaw-discord-bot.log
journalctl --user -u openclaw-gateway.service --since "10 minutes ago" --no-pager | grep -E "discord.*(Piet|logged in|initialized)"
```

Expected:

- OpenClaw Gateway logs identify Discord as Piet with app/user ID `1486895358725460069`.
- OpenClaw Discord bot logs identify as Piet with app/user ID `1486895358725460069`.
- Mission Control health returns HTTP 200.
- Hermes remains active and unchanged.

## Stop Conditions

- `openclaw config validate` fails.
- The new token prefix decodes to the Hermes app ID or an unknown app ID.
- Discord API returns 401 after restart.
- Any legacy Claudebridge service becomes unmasked or active.

