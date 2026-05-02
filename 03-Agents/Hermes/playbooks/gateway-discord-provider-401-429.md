---
title: Hermes Playbook - Gateway Discord Provider 401 429
status: active
created: 2026-05-02
owner: Piet
scope: break-glass-debug
---

# Hermes Playbook - Gateway Discord Provider 401/429

Use this when OpenClaw Gateway logs show Discord API `401 Unauthorized`, `429 rate limited`, failed channel resolve, failed gateway information, or Discord provider restart loops.

## Meaning

- `401 Unauthorized` usually means the token loaded by OpenClaw Gateway is invalid, stale, or belongs to the wrong Discord application.
- `429` usually means Discord rate limiting. Do not repeatedly restart services during 429 windows unless there is a stronger outage signal.
- The expected Piet/OpenClaw Discord app/user ID is `1486895358725460069`.
- Hermes has a separate token/app ID and must not be used for OpenClaw Gateway.

## Allowed Without Approval

Read-only evidence:

```bash
systemctl --user status openclaw-gateway.service --no-pager --lines=40
curl -s -o /dev/null -w "openclaw=%{http_code}\n" http://127.0.0.1:18789/health
journalctl --user -u openclaw-gateway.service --since "30 minutes ago" --no-pager | grep -Ei "discord|401|429|Unauthorized|rate limit|gateway/bot|logged in|initialized|channel resolve" | tail -120
openclaw config validate
```

Secret-safe token inventory:

```bash
python3 - <<'PY'
from pathlib import Path
import base64, hashlib, json
def app_id(token):
    try:
        first = token.split('.', 1)[0]
        return base64.b64decode(first + '=' * ((4 - len(first) % 4) % 4)).decode()
    except Exception:
        return '?'
paths = [
    '/home/piet/.openclaw/gateway.systemd.env',
    '/home/piet/.openclaw/.env',
    '/home/piet/.openclaw/openclaw.json',
]
for path in paths:
    print('---', path)
    p = Path(path)
    if not p.exists():
        print('missing')
        continue
    if path.endswith('.json'):
        data = json.loads(p.read_text())
        token = data.get('channels', {}).get('discord', {}).get('token', '')
        print('channels.discord.token app_id=%s sha8=%s' % (app_id(token), hashlib.sha256(token.encode()).hexdigest()[:8] if token else 'missing'))
        print('invalid botToken present=%s' % ('botToken' in data.get('channels', {}).get('discord', {})))
        print('invalid plugin token present=%s' % ('token' in data.get('plugins', {}).get('entries', {}).get('discord', {})))
    else:
        for line in p.read_text(errors='replace').splitlines():
            if line.startswith('DISCORD_BOT_TOKEN='):
                token = line.split('=', 1)[1].strip().strip('"').strip("'")
                print('DISCORD_BOT_TOKEN app_id=%s sha8=%s' % (app_id(token), hashlib.sha256(token.encode()).hexdigest()[:8]))
PY
```

## Fix Gate

Before any edit or restart:

1. Confirm live evidence: `401`, persistent failed Discord provider, or confirmed wrong app ID.
2. State exact file and service to change.
3. Backup all token-bearing files.
4. Ask Piet for approval in the current Discord thread.

## Approved Fix Pattern

Follow the token-rotation runbook:

```text
/home/piet/vault/03-Agents/Hermes/playbooks/discord-token-rotation.md
```

Minimum post-verify:

```bash
openclaw config validate
systemctl --user restart openclaw-gateway.service
sleep 8
systemctl --user is-active openclaw-gateway.service
curl -s -o /dev/null -w "openclaw=%{http_code}\n" http://127.0.0.1:18789/health
journalctl --user -u openclaw-gateway.service --since "5 minutes ago" --no-pager | grep -Ei "discord.*(Piet|initialized|logged in)|401|429|Unauthorized|rate limit" | tail -80
```

Expected:

- Config validates.
- Gateway health returns HTTP 200.
- Discord provider identifies Piet / app ID `1486895358725460069`.
- No fresh `401 Unauthorized`.

## Stop Conditions

- `openclaw config validate` fails.
- New token prefix decodes to Hermes app ID `1500199614706483210`.
- Discord returns fresh `401` after token update and restart.
- Rate limits worsen after repeated restarts.

