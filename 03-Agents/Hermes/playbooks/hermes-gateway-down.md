---
title: Hermes Playbook - Hermes Gateway Down
status: active
created: 2026-05-02
owner: Piet
scope: break-glass-debug
---

# Hermes Playbook - Hermes Gateway Down

Use this playbook when Hermes is unreachable from Discord, the Hermes Gateway service appears down, or Discord delivery is degraded.

## Ground Truth

- Hermes home: `/home/piet/.hermes`
- Hermes config: `/home/piet/.hermes/config.yaml`
- Hermes env: `/home/piet/.hermes/.env`
- Hermes gateway service: `hermes-gateway.service`
- Gateway state file: `/home/piet/.hermes/gateway_state.json`
- Gateway log: `/home/piet/.hermes/logs/gateway.log`
- Discord bot ID: `1500199614706483210`
- Primary Discord channel: `1500203113867378789`

## Allowed Without Approval

Read-only evidence gathering:

```bash
systemctl --user status hermes-gateway.service --no-pager --lines=30
sed -n '1,160p' /home/piet/.hermes/gateway_state.json 2>/dev/null || true
tail -120 /home/piet/.hermes/logs/gateway.log 2>/dev/null
pgrep -af 'hermes.*gateway|hermes-gateway|hermes chat' | sed -n '1,40p'
python3 - <<'PY'
from pathlib import Path
p=Path('/home/piet/.hermes/.env')
for line in p.read_text(errors='replace').splitlines():
    s=line.strip()
    if s and not s.startswith('#') and '=' in s:
        k=s.split('=',1)[0]
        if k.startswith('DISCORD_') or k.startswith('HERMES_'):
            print(k+'=<redacted>')
PY
```

## Interpret Results

- `gateway_state=running` and `discord.state=connected`: Hermes Gateway is up.
- Discord HTTP `429` during slash-command sync: degraded command reconciliation, not necessarily message delivery failure.
- `active_agents > 0`: avoid restart unless stuck or Piet explicitly asks; a restart can interrupt active work.
- Missing or stale `gateway_state.json`: verify with `systemctl --user status` and logs before claiming failure.

## Restart Gate

Restart is allowed only after live evidence and Piet's explicit approval in the current Discord thread.

Before recommending or running a restart, report:

1. **Live Evidence** - service status, gateway_state, Discord state, and relevant log lines.
2. **Action** - exact restart command:

```bash
systemctl --user restart hermes-gateway.service
```

3. **Expected Post-Check**:

```bash
systemctl --user status hermes-gateway.service --no-pager --lines=30
sed -n '1,160p' /home/piet/.hermes/gateway_state.json 2>/dev/null || true
tail -60 /home/piet/.hermes/logs/gateway.log 2>/dev/null
```

4. **Approval** - wait for Piet's explicit approval.

## Config Edit Gate

Before editing Hermes config or env:

1. Identify the exact file and key/path.
2. Create a timestamped backup.
3. State the intended diff in plain language.
4. Wait for Piet's explicit approval.
5. Apply the smallest edit.
6. Restart `hermes-gateway.service` only if needed.
7. Run focused post-verify.

Relevant paths:

```text
/home/piet/.hermes/config.yaml
/home/piet/.hermes/.env
/home/piet/vault/03-Agents/Hermes/working-context.md
```

## Stop Conditions

Stop and ask Piet if any of these happen:

- service ownership is unclear
- Discord auth/token appears invalid
- backup creation fails
- `active_agents > 0` and no emergency is confirmed
- restart does not restore `discord.state=connected`
- logs show rate limiting but normal message flow still works
- action would create tasks, crons, agents, deployments, permanent allowlist entries, or YOLO mode

## Report Format

Use:

1. Problem
2. Evidence
3. Risk
4. Next Action

Keep it short and cite exact command results.
