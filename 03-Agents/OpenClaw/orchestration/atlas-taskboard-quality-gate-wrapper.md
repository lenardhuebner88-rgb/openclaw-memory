# Atlas Taskboard Quality-Gate Wrapper

Purpose: one controlled command for clean sprint board flow.

## Script
`/home/piet/.openclaw/workspace/scripts/atlas-taskboard-quality-gate.py`

## Flow
1. Create master sprint task
2. Verify master with `GET /api/tasks/<id>`
3. Create child tasks
4. Verify each child after write
5. Optional dispatch children
6. Verify `pending-pickup`/`dispatchState=dispatched` after dispatch
7. Optional monitor via `atlas-sprint-monitor.py`
8. Finalize remains manual/gated until receipt semantics are fully integrated

## Default Safety
- Default mode is dry-run: no writes.
- `--execute` required for board writes.
- `--dispatch` required for dispatch.
- No restart/config/cron/secrets/backups/destructive cleanup.
- Finalize is not automatic in v1; Atlas must collect receipts and run monitor before done claim.

## Spec Format
```json
{
  "title": "UI Verbesserungen Mission Control Board",
  "goal": "Make the MC board visibly clearer and easier to operate.",
  "scope": "UI board improvements only.",
  "antiScope": "No restart/config/cron/backups/destructive cleanup.",
  "priority": "medium",
  "children": [
    {
      "title": "[P1][Pixel] Board UI improvement slice",
      "agent": "frontend-guru",
      "objective": "Implement/audit a bounded UI improvement.",
      "gates": ["typecheck/build as applicable", "UI proof or screenshot", "receipt with evidence"]
    }
  ]
}
```

## Usage
```bash
# Preview only
/home/piet/.openclaw/workspace/scripts/atlas-taskboard-quality-gate.py --spec sprint.json

# Create + verify master/children
/home/piet/.openclaw/workspace/scripts/atlas-taskboard-quality-gate.py --spec sprint.json --execute

# Create + verify + dispatch + monitor
/home/piet/.openclaw/workspace/scripts/atlas-taskboard-quality-gate.py --spec sprint.json --execute --dispatch --monitor
```

## v1 Gap
This is a CLI wrapper, not yet a Mission Control API/MCP primitive. Next hardening step:
- add persistent run record
- add receipt collection summary
- add controlled finalize once monitor + receipts + build/live gates pass
- expose as Taskboard MCP tool after CLI proves stable
