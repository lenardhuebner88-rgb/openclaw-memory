---
title: Hermes Playbook - Mission Control Build Failed
status: active
created: 2026-05-02
owner: Piet
scope: break-glass-debug
---

# Hermes Playbook - Mission Control Build Failed

Use this when Mission Control is down after a code/config change, Next.js build fails, `/api/health` is not HTTP 200, or `mission-control.service` enters restart-loop/degraded state.

## Ground Truth

- Workspace: `/home/piet/.openclaw/workspace/mission-control`
- Service: `mission-control.service`
- Health route: `http://127.0.0.1:3000/api/health`
- Build guard may require `ALLOW_BUILD_WHILE_RUNNING=1 npm run build` when the service is live.
- If code changed, use validation order: typecheck/build -> restart -> route checks.

## Allowed Without Approval

Read-only evidence:

```bash
systemctl --user status mission-control.service --no-pager --lines=60
curl -s -o /dev/null -w "mc=%{http_code}\n" http://127.0.0.1:3000/api/health
journalctl --user -u mission-control.service --since "30 minutes ago" --no-pager | tail -160
cd /home/piet/.openclaw/workspace/mission-control && git status --short
```

Non-mutating code gates:

```bash
cd /home/piet/.openclaw/workspace/mission-control
npm run typecheck
```

## Build/Edit Gate

Before edits, builds that may affect live service, or restarts:

1. Identify the failing route, build step, or service state.
2. State the exact command and why it is needed.
3. Backup the exact files to edit.
4. Wait for Piet approval unless Piet already approved this recovery slice.

## Approved Recovery Sequence

After approval:

```bash
cd /home/piet/.openclaw/workspace/mission-control
npm run typecheck
ALLOW_BUILD_WHILE_RUNNING=1 npm run build
systemctl --user restart mission-control.service
sleep 5
curl -s -o /dev/null -w "health=%{http_code}\n" http://127.0.0.1:3000/api/health
curl -s -o /dev/null -w "dashboard=%{http_code}\n" http://127.0.0.1:3000/dashboard
curl -s -o /dev/null -w "alerts=%{http_code}\n" http://127.0.0.1:3000/alerts
curl -s -o /dev/null -w "board=%{http_code}\n" http://127.0.0.1:3000/api/board-consistency
```

Expected:

- Typecheck passes.
- Build passes.
- `mission-control.service` active.
- Health and key routes return HTTP 200.

## If Build Fails

Report:

1. First failing command.
2. First meaningful compiler/build error.
3. Files implicated.
4. Whether service is still serving the previous build.
5. Exact smallest next action.

Do not keep retrying builds blindly.

## Stop Conditions

- Build failure is unrelated to the current incident and requires broad refactor.
- Restart would stop a still-working previous build without a successful replacement build.
- Disk/memory pressure appears in logs.
- Any route check returns non-200 after restart.

