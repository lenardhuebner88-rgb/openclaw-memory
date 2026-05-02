---
title: Hermes Playbook - Discord Bot Unresponsive
status: active
created: 2026-05-02
owner: Piet
scope: break-glass-debug
---

# Hermes Playbook - Discord Bot Unresponsive

Use this playbook when a Discord bot does not respond, responds in the wrong channel, or the operator is unsure whether the issue is Piet/OpenClaw Discord or Hermes Agent.

## Ground Truth

Active Discord bot surfaces after Claudebridge cleanup:

- Piet/OpenClaw agents bot: `openclaw-discord-bot.service`
- Hermes bot: `hermes-gateway.service`

Legacy bridge surfaces should stay disabled/masked:

- `commander-bot.service`
- `claude-telegram-bridge.service`
- `discord-bridge.service`
- `atlas-autonomy-discord.service`
- `tmux-claude.service`

Relevant paths:

```text
/home/piet/.openclaw/scripts/openclaw-discord-bot.py
/home/piet/.openclaw/config/openclaw-discord-bot.env
/home/piet/.openclaw/workspace/logs/openclaw-discord-bot.log
/home/piet/.hermes/config.yaml
/home/piet/.hermes/.env
/home/piet/.hermes/gateway_state.json
/home/piet/.hermes/logs/gateway.log
```

Known identity baseline:

- The OpenClaw Discord bot should log in as `Piet (1486895358725460069)`.
- Hermes should log in with app/user ID `1500199614706483210`.
- A live `Claudebridge` login after 2026-05-02 is drift and should be treated as a token/config regression.
- Do not rename Discord applications locally. Bot display/application names are a Discord-side/operator action unless a verified local config path controls them.

## Allowed Without Approval

Read-only evidence gathering:

```bash
systemctl --user status openclaw-discord-bot.service hermes-gateway.service --no-pager --lines=30
systemctl --user is-enabled commander-bot.service claude-telegram-bridge.service discord-bridge.service atlas-autonomy-discord.service tmux-claude.service openclaw-discord-bot.service hermes-gateway.service 2>&1 || true
pgrep -af 'openclaw-discord-bot.py|hermes.*gateway|commander/bot.py|claude-telegram-bridge.py|discord-bridge/bot.js|autonomy-bot.js|tmux.*claude' | sed -n '1,120p'
tail -120 /home/piet/.openclaw/workspace/logs/openclaw-discord-bot.log 2>/dev/null
journalctl --user -u openclaw-discord-bot.service --since "15 minutes ago" --no-pager
tail -120 /home/piet/.hermes/logs/gateway.log 2>/dev/null
sed -n '1,160p' /home/piet/.hermes/gateway_state.json 2>/dev/null || true
```

Secret-safe config inventory:

```bash
python3 - <<'PY'
from pathlib import Path
for path in ['/home/piet/.openclaw/config/openclaw-discord-bot.env','/home/piet/.hermes/.env']:
    p=Path(path)
    print('---', path)
    if not p.exists():
        print('missing')
        continue
    for line in p.read_text(errors='replace').splitlines():
        s=line.strip()
        if not s or s.startswith('#') or '=' not in s:
            continue
        k=s.split('=',1)[0]
        if 'TOKEN' in k.upper() or 'SECRET' in k.upper() or 'KEY' in k.upper():
            print(k+'=<redacted>')
        elif k.startswith('DISCORD') or k.startswith('OPENCLAW') or k.startswith('HERMES'):
            print(k+'=<set>')
PY
```

## Interpret Results

- `openclaw-discord-bot.service active` and recent `heartbeat mc=active bot=alive`: Piet/OpenClaw bot is alive.
- `hermes-gateway.service active` and `gateway_state=running` with `discord.state=connected`: Hermes Discord is alive.
- Discord HTTP `429` in Hermes logs during command sync: degraded slash-command reconciliation, not necessarily message delivery failure.
- `Privileged message content intent is missing` in OpenClaw bot logs may affect command handling; do not change it locally without Piet's approval.
- Legacy services `masked` is expected after Claudebridge cleanup.

## Restart Gate

Restart only the affected bot, and only after live evidence plus Piet's explicit approval in the current Discord thread.

OpenClaw/Piet bot restart:

```bash
systemctl --user restart openclaw-discord-bot.service
```

Hermes bot restart:

```bash
systemctl --user restart hermes-gateway.service
```

Before restart, report:

1. Which bot is affected.
2. Exact evidence: service status, process, logs, or gateway state.
3. Exact restart command.
4. Expected post-check.
5. Wait for Piet's approval.

Post-check:

```bash
systemctl --user status openclaw-discord-bot.service hermes-gateway.service --no-pager --lines=20
pgrep -af 'openclaw-discord-bot.py|hermes.*gateway' | sed -n '1,40p'
tail -60 /home/piet/.openclaw/workspace/logs/openclaw-discord-bot.log 2>/dev/null
tail -60 /home/piet/.hermes/logs/gateway.log 2>/dev/null
sed -n '1,160p' /home/piet/.hermes/gateway_state.json 2>/dev/null || true
```

## Config Edit Gate

Do not edit bot env/config unless Piet explicitly asks.

Before any edit:

1. Identify exact file and key.
2. Create a timestamped backup.
3. State intended diff.
4. Wait for approval.
5. Apply the smallest edit.
6. Restart only the affected bot if needed.
7. Run focused post-verify.

## Stop Conditions

Stop and ask Piet if any of these happen:

- Discord token/auth appears invalid.
- The issue requires Discord Developer Portal changes.
- Both bot services are active but Discord does not deliver messages.
- The affected bot is unclear.
- A command would unmask legacy Claudebridge services.
- A command would create tasks, crons, agents, deployments, permanent allowlist entries, or YOLO mode.

## Report Format

Use:

1. Problem
2. Evidence
3. Risk
4. Next Action

Keep it short and cite exact command results.
