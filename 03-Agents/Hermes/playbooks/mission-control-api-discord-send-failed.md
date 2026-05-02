---
title: Hermes Playbook - Mission Control API Discord Send Failed
status: active
created: 2026-05-02
owner: Piet
scope: break-glass-debug
---

# Hermes Playbook - Mission Control API Discord Send Failed

Use this when Mission Control `/api/discord/send` fails, alerts do not arrive, execution reports are missing, or a script reports Discord delivery failure through Mission Control.

## Ground Truth

- Mission Control route: `POST http://127.0.0.1:3000/api/discord/send`
- Mission Control service: `mission-control.service`
- Token env files:
  - `/home/piet/.openclaw/workspace/mission-control/.env`
  - `/home/piet/.openclaw/workspace/mission-control/.env.local`
- Expected Piet/OpenClaw token app ID: `1486895358725460069`
- Default report channel fallback: `1488976473942392932`

## Allowed Without Approval

Read-only checks:

```bash
curl -s -o /dev/null -w "mc=%{http_code}\n" http://127.0.0.1:3000/api/health
systemctl --user status mission-control.service --no-pager --lines=50
journalctl --user -u mission-control.service --since "30 minutes ago" --no-pager | grep -Ei "discord|api/discord/send|401|403|404|429|500|token|webhook|report" | tail -160
```

Secret-safe token inventory:

```bash
python3 - <<'PY'
from pathlib import Path
import base64, hashlib
for path in ['/home/piet/.openclaw/workspace/mission-control/.env','/home/piet/.openclaw/workspace/mission-control/.env.local']:
    print('---', path)
    p = Path(path)
    if not p.exists():
        print('missing')
        continue
    for line in p.read_text(errors='replace').splitlines():
        if line.startswith('DISCORD_BOT_TOKEN='):
            token = line.split('=', 1)[1].strip().strip('"').strip("'")
            first = token.split('.', 1)[0]
            app_id = base64.b64decode(first + '=' * ((4 - len(first) % 4) % 4)).decode()
            print('DISCORD_BOT_TOKEN app_id=%s sha8=%s' % (app_id, hashlib.sha256(token.encode()).hexdigest()[:8]))
PY
```

Non-mutating route shape check:

```bash
sed -n '1,140p' /home/piet/.openclaw/workspace/mission-control/src/app/api/discord/send/route.ts
```

## Controlled Smoke

Only run a real send if Piet approves or explicitly asks for a smoke test. It will post a message to Discord.

```bash
curl -sS -X POST http://127.0.0.1:3000/api/discord/send \
  -H 'Content-Type: application/json' \
  -H 'x-actor-kind: system' \
  -H 'x-request-class: admin' \
  -d '{"channelId":"1495737862522405088","message":"[Hermes] Mission Control Discord send smoke."}'
```

Expected:

```json
{"ok":true,"kind":"direct","messageId":"...","channelId":"1495737862522405088"}
```

## Fix Gate

Before edits or restart:

1. Confirm Mission Control health and route failure mode.
2. Confirm token app ID in `.env` and `.env.local`.
3. State exact file/service action.
4. Backup files.
5. Ask Piet for approval.

## Approved Fix Pattern

- If token app ID is wrong, use `/home/piet/vault/03-Agents/Hermes/playbooks/discord-token-rotation.md`.
- If route code is broken, use `/home/piet/vault/03-Agents/Hermes/playbooks/mission-control-build-failed.md` validation order after patching.
- If Discord returns `429`, stop repeated smoke tests and wait.

## Stop Conditions

- Health route is non-200.
- Discord returns `401 Unauthorized` after token rotation.
- Discord returns `403 Forbidden`, indicating channel permission/invite issue.
- Repeated `429` appears.
- Any fix requires broad Mission Control rewrite.

