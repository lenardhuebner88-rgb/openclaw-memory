---
title: Hermes Playbook - OpenClaw Discord Commands Broken
status: active
created: 2026-05-02
owner: Piet
scope: break-glass-debug
---

# Hermes Playbook - OpenClaw Discord Commands Broken

Use this when Piet/OpenClaw slash commands do not appear, do not respond, respond in the wrong channel, or Discord interactions fail.

## Ground Truth

- Piet/OpenClaw bot service: `openclaw-discord-bot.service`
- Expected identity: `Piet (1486895358725460069)`
- Script: `/home/piet/.openclaw/scripts/openclaw-discord-bot.py`
- Env: `/home/piet/.openclaw/config/openclaw-discord-bot.env`
- Commander channel: `1495737862522405088`
- Hermes is separate and should not be used to fix Piet/OpenClaw commands unless the runbook says so.

## Allowed Without Approval

Read-only checks:

```bash
systemctl --user status openclaw-discord-bot.service --no-pager --lines=50
journalctl --user -u openclaw-discord-bot.service --since "30 minutes ago" --no-pager | tail -160
python3 -m py_compile /home/piet/.openclaw/scripts/openclaw-discord-bot.py
awk -F= '/^DISCORD_APPLICATION_ID=|^DISCORD_GUILD_ID=|^DISCORD_COMMANDER_CHANNEL_ID=|^OPERATOR_USER_ID=|^ALLOWED_USER_IDS=/ {print}' /home/piet/.openclaw/config/openclaw-discord-bot.env
```

Secret-safe token/app check:

```bash
python3 - <<'PY'
from pathlib import Path
import base64, hashlib
p = Path('/home/piet/.openclaw/config/openclaw-discord-bot.env')
for line in p.read_text(errors='replace').splitlines():
    if line.startswith('DISCORD_BOT_TOKEN='):
        token = line.split('=', 1)[1].strip().strip('"').strip("'")
        first = token.split('.', 1)[0]
        app_id = base64.b64decode(first + '=' * ((4 - len(first) % 4) % 4)).decode()
        print('token_app_id=%s sha8=%s' % (app_id, hashlib.sha256(token.encode()).hexdigest()[:8]))
PY
```

## Common Signals

- `logged in as Piet (1486895358725460069)`: identity is correct.
- `synced 14 slash commands`: slash-command registration succeeded.
- `Unknown interaction` / `10062`: interaction expired or defer race.
- `401 Unauthorized`: use `gateway-discord-provider-401-429.md` or `discord-token-rotation.md`.
- `Privileged message content intent is missing`: should not appear after the 2026-05-02 switch to `discord.Client` plus `app_commands.CommandTree`.

## Fix Gate

Before restart or edits:

1. Identify whether the issue is service down, token/identity, slash-command sync, channel restriction, or code syntax.
2. State exact action and expected post-check.
3. Backup script/env/unit before editing.
4. Wait for Piet approval in the current Discord thread.

## Approved Post-Verify

```bash
systemctl --user restart openclaw-discord-bot.service
sleep 5
systemctl --user is-active openclaw-discord-bot.service
journalctl --user -u openclaw-discord-bot.service --since "2 minutes ago" --no-pager | grep -E "logged in as|synced|ERROR|WARNING|401|10062|Privileged"
```

Expected:

- service active
- `logged in as Piet (1486895358725460069)`
- slash commands synced
- no fresh `401`
- no fresh privileged message-content warning

## Stop Conditions

- Token app ID is not `1486895358725460069`.
- Service logs show repeated `401 Unauthorized`.
- Slash-command sync returns repeated Discord `429`; stop restarts and wait.
- Fix would unmask legacy Claudebridge services.

