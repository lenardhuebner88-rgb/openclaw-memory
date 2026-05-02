---
title: Hermes Playbook - OpenClaw Gateway Down
status: active
created: 2026-05-02
owner: Piet
scope: break-glass-debug
---

# Hermes Playbook - OpenClaw Gateway Down

Use this playbook when OpenClaw Gateway appears crashed, unreachable, or severely degraded.

## Allowed Without Approval

Prefer `openclaw-readonly` MCP first:

- `openclaw_gateway_health`
- `openclaw_services_status`
- `openclaw_recent_logs`
- `openclaw_status_summary`

Use shell checks only when the MCP path is unavailable or Piet explicitly asks for host-level break-glass diagnosis.

Read-only evidence gathering:

```bash
systemctl --user status openclaw-gateway.service --no-pager --lines=20
pgrep -af 'openclaw.*gateway|openclaw-gateway' | sed -n '1,20p'
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:18789/health 2>/dev/null || echo conn_fail
journalctl --user -u openclaw-gateway.service --no-pager -n 80
journalctl --user -u openclaw-gateway.service --no-pager -n 80 --priority=warning
df -h /home/piet
free -h
```

## Restart Gate

Before recommending or running a restart, report:

1. **Live Evidence** - exact status, HTTP result, and relevant log lines.
2. **Action** - exact restart command:

```bash
systemctl --user restart openclaw-gateway.service
```

3. **Expected Post-Check**:

```bash
systemctl --user status openclaw-gateway.service --no-pager --lines=20
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:18789/health 2>/dev/null || echo conn_fail
```

4. **Approval** - wait for Piet's explicit approval in the current Discord thread.

## Config Edit Gate

Before editing any config:

1. Identify the exact file and key/path.
2. Create a timestamped backup.
3. State the intended diff in plain language.
4. Wait for Piet's explicit approval.
5. Apply the smallest edit.
6. Run focused post-verify.

Relevant config path:

```text
/home/piet/.openclaw/openclaw.json
```

## Stop Conditions

Stop and ask Piet if any of these happen:

- service ownership is unclear
- backup creation fails
- live evidence contradicts the suspected failure
- restart does not restore `/health=200`
- new unrelated failure appears during verification
- a command would create tasks, crons, agents, deployments, permanent allowlist entries, or YOLO mode

## Report Format

Use:

1. Problem
2. Evidence
3. Risk
4. Next Action

Keep the report short and cite exact command results.
