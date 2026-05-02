# Mission Control API Read-only

Use this when Hermes needs current Mission Control context without changing system state.

## Scope

Read-only only:

- GET endpoints.
- service status.
- recent logs.

Do not call POST, PUT, PATCH, or DELETE routes from this playbook.

## Primary Endpoints

```bash
curl -s http://127.0.0.1:3000/api/health | jq '{status, severity, timestamp, service}'
curl -s http://127.0.0.1:3000/api/board-consistency | jq '{status, issueCount: ((.raw.issues // .normalized.issues // []) | length)}'
curl -s http://127.0.0.1:3000/api/tasks/snapshot | jq '{sampledAt, totals}'
curl -s http://127.0.0.1:3000/api/analytics/alerts | jq '{activeCount, generatedAt, alertCount: ((.alerts // []) | length)}'
curl -s http://127.0.0.1:3000/api/ops/skill-plugin-inventory | jq '{mode, generatedAt, riskSummary}'
curl -s http://127.0.0.1:3000/api/monitoring | jq 'keys'
```

HTTP-only status sweep:

```bash
for path in /api/health /api/board-consistency /api/tasks/snapshot /api/alerts /api/analytics/alerts /api/ops/skill-plugin-inventory /api/monitoring; do
  printf '%s ' "$path"
  curl -s -o /dev/null -w '%{http_code}\n' "http://127.0.0.1:3000$path" 2>/dev/null || echo conn_fail
done
```

## Service Context

```bash
systemctl --user status mission-control.service --no-pager --lines=30
journalctl --user -u mission-control.service --since "30 minutes ago" --no-pager --priority=warning
```

## Interpretation

- HTTP 200 with `status: ok`: Mission Control route is reachable and healthy.
- HTTP 200 with `status: degraded`: route is reachable but needs separate diagnosis before recovery action.
- `conn_fail`, 5xx, or service inactive: switch to `mission-control-down-atlas-unavailable.md`.
- Board consistency `status: ok`: no board consistency blocker visible from this route.

## Report Format

```text
Problem:
Evidence:
Risk:
Next Action:
```

Next Action must be one of:

- continue read-only diagnosis;
- ask Piet for approval before restart/config change;
- switch to a more specific runbook.
