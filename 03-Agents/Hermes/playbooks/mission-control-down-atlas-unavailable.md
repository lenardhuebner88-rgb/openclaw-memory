---
title: Hermes Playbook - Mission Control Down and Atlas Unavailable
status: active
created: 2026-05-02
owner: Piet
scope: break-glass-debug
---

# Hermes Playbook - Mission Control Down and Atlas Unavailable

Use this playbook when Mission Control appears down, unreachable, or degraded and Atlas is not able to coordinate recovery.

## Ground Truth

- Mission Control workspace: `/home/piet/.openclaw/workspace/mission-control`
- Service: `mission-control.service`
- Port: `3000`
- Core routes:
  - `http://127.0.0.1:3000/api/health`
  - `http://127.0.0.1:3000/api/board-consistency`
  - `http://127.0.0.1:3000/dashboard`
  - `http://127.0.0.1:3000/alerts`
- Atlas-related services observed on this host:
  - `atlas-autonomy-discord.service`
  - `m7-plan-runner.service`

## Allowed Without Approval

Read-only evidence gathering:

```bash
systemctl --user status mission-control.service --no-pager --lines=30
pgrep -af 'mission-control|next.*3000|node.*3000' | sed -n '1,30p'
for path in /api/health /api/board-consistency /dashboard /alerts; do printf '%s ' "$path"; curl -s -o /dev/null -w '%{http_code}\n' "http://127.0.0.1:3000$path" 2>/dev/null || echo conn_fail; done
journalctl --user -u mission-control.service --no-pager -n 120
journalctl --user -u mission-control.service --no-pager -n 120 --priority=warning
systemctl --user status atlas-autonomy-discord.service m7-plan-runner.service --no-pager --lines=12
df -h /home/piet
free -h
```

Optional read-only repository checks:

```bash
cd /home/piet/.openclaw/workspace/mission-control
git status --short
node -e "const p=require('./package.json'); console.log(JSON.stringify(p.scripts,null,2))"
```

## Restart Gate

Restart is allowed only after live evidence and Piet's explicit approval in the current Discord thread.

Before recommending or running a restart, report:

1. **Live Evidence** - service status, route matrix, and relevant log lines.
2. **Atlas State** - whether Atlas services are inactive, failed, or irrelevant to the immediate outage.
3. **Action** - exact restart command:

```bash
systemctl --user restart mission-control.service
```

4. **Expected Post-Check**:

```bash
systemctl --user status mission-control.service --no-pager --lines=30
for path in /api/health /api/board-consistency /dashboard /alerts; do printf '%s ' "$path"; curl -s -o /dev/null -w '%{http_code}\n' "http://127.0.0.1:3000$path" 2>/dev/null || echo conn_fail; done
```

5. **Approval** - wait for Piet's explicit approval.

## Config Or Code Edit Gate

Do not edit Mission Control config or code unless Piet explicitly asks.

Before any edit:

1. Identify exact file and key/function/component.
2. Create a timestamped backup or confirm git-tracked diff scope.
3. State intended diff in plain language.
4. Wait for Piet's explicit approval.
5. Apply the smallest edit.
6. Validate in this order:

```bash
cd /home/piet/.openclaw/workspace/mission-control
npm run typecheck
ALLOW_BUILD_WHILE_RUNNING=1 npm run build
systemctl --user restart mission-control.service
for path in /api/health /api/board-consistency /dashboard /alerts; do printf '%s ' "$path"; curl -s -o /dev/null -w '%{http_code}\n' "http://127.0.0.1:3000$path" 2>/dev/null || echo conn_fail; done
```

If the build guard refuses a live build, stop and ask Piet rather than forcing a different path.

## Atlas Unavailable Rule

If Atlas is not handlungsfaehig:

- Do not wait for Atlas to recover before stabilizing Mission Control.
- Do not create Atlas tasks, agents, crons, or approvals.
- Report directly to Piet in the current Discord thread.
- Keep the action bounded to Mission Control recovery.
- If the issue is coordination-only and Mission Control is healthy, stop and ask Piet before touching Atlas services.

## Stop Conditions

Stop and ask Piet if any of these happen:

- service ownership is unclear
- route checks disagree with service status in a way you cannot explain
- backup creation fails
- build/typecheck fails
- restart does not restore core routes
- post-check reveals new board consistency or alerts failures
- action would create tasks, crons, agents, deployments, permanent allowlist entries, or YOLO mode

## Report Format

Use:

1. Problem
2. Evidence
3. Risk
4. Next Action

Keep it short and cite exact command results.
