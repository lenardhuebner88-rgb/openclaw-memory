# Mission Control E2E Draft-to-Done Canary - 2026-05-04

Verdict: YELLOW overall, GREEN for core board-state lifecycle.

Yellow reasons:
- First `draft -> assigned` attempt with `x-actor-kind: system` failed as expected by ingress policy: `Review requests require a human actor`.
- The real move succeeded with the route-required `x-actor-kind: human`, `x-request-class: review`.
- Two unrelated board events landed during the diff window: one cost anomaly event and one `atlas-receipt-stream` task update.

No Gateway restart and no Mission Control restart occurred.

## Canary

- Title: `MC-E2E-CANARY draft-to-done board state check`
- taskId: `9c2cd146-e4e3-4f69-a562-125784a628cb`
- runId: `4f51fd44-9103-41b0-bc65-ad55e40fbdea`
- workerSessionId: `worker:mc-e2e-canary-20260504`
- workerLabel: `MC E2E Canary Worker`
- result: `MC_E2E_CANARY_OK`

## Backups

- `/home/piet/.openclaw/state/mission-control/data/tasks.json.bak-20260504T110757Z-mc-e2e-draft-to-done-canary`
- `/home/piet/.openclaw/state/mission-control/data/worker-runs.json.bak-20260504T110757Z-mc-e2e-draft-to-done-canary`
- `/home/piet/.openclaw/state/mission-control/data/board-events.json.bak-20260504T110757Z-mc-e2e-draft-to-done-canary`
- `/home/piet/.openclaw/state/mission-control/data/board-events.jsonl.bak-20260504T110757Z-mc-e2e-draft-to-done-canary`

## API Endpoints Used

- `GET /api/health`
- `GET /api/board-consistency`
- `GET /api/board/snapshot`
- `POST /api/tasks`
- `PUT /api/tasks/:id/move`
- `POST /api/tasks/:id/dispatch`
- `GET /api/worker-pickups`
- `POST /api/tasks/:id/claim`
- `POST /api/tasks/:id/receipt`
- `GET /api/tasks/:id`
- `GET /api/tasks/:id/events`

## State Table

| State | API action | tasks.json | worker-runs.json | board-events | board snapshot | Verdict |
|---|---|---|---|---|---|---|
| Draft | `POST /api/tasks` | `status=draft`, `dispatchState=draft`, `executionState=queued` | no Canary run | `task-created` to `draft` | live snapshot contained the draft task | GREEN |
| Assigned | `PUT /api/tasks/:id/move` with human/review ingress | `status=assigned`, `dispatchState=queued`, `executionState=queued` | no Canary run | `move`, `task-status-change draft -> assigned` | live snapshot contained assigned task | GREEN |
| Pending Pickup | `POST /api/tasks/:id/dispatch` | `status=pending-pickup`, `dispatchState=dispatched`, `executionState=queued` | exactly one open placeholder, `gateway:9c2cd146-e4e3-4f69-a562-125784a628cb` | `task-dispatched assigned -> pending-pickup` | live snapshot contained pending-pickup task | GREEN |
| Accepted / Active | `POST /api/tasks/:id/claim` | `status=in-progress`, `executionState=active`, `receiptStage=accepted` | same run bound to `worker:mc-e2e-canary-20260504`, `claimState=claimed` | `receipt accepted` | live snapshot contained in-progress task | GREEN |
| Duplicate Safety | second `POST /api/tasks/:id/claim` with different workerSessionId | unchanged | unchanged | ownership mismatch recorded by API path | no duplicate pickup | GREEN, returned `409` |
| Done / Result | `POST /api/tasks/:id/receipt` | `status=done`, `dispatchState=completed`, `executionState=done`, `receiptStage=result`, `resultSummary=MC_E2E_CANARY_OK` | run `status=succeeded`, `outcome=succeeded`, `endedAt` set | `receipt result`, `task-status-change in-progress -> done`, `materializer-ok` | archive snapshot contained done task | GREEN |

## Final State

Task:
- `status=done`
- `dispatchState=completed`
- `executionState=done`
- `receiptStage=result`
- `resultSummary=MC_E2E_CANARY_OK`
- `completedAt=2026-05-04T11:10:08.288Z`

Worker run:
- `status=succeeded`
- `outcome=succeeded`
- `workerSessionId=worker:mc-e2e-canary-20260504`
- `workerLabel=MC E2E Canary Worker`
- `endedAt=2026-05-04T11:10:08.345Z`

Final health:
- `/api/health`: OK
- `/api/board-consistency`: OK
- open worker-runs: `0`
- duplicate pickups: `0`
- orphaned dispatches: `0`
- Gateway restart: no, `ActiveEnterTimestamp=Mon 2026-05-04 12:09:24 CEST`, `NRestarts=0`
- Mission Control restart: no, `ActiveEnterTimestamp=Mon 2026-05-04 11:09:43 CEST`, `NRestarts=0`

## Diff Summary

Compared to fresh backups:
- `tasks.json`: `+1` task, the Canary task.
- `worker-runs.json`: `+1` run, the Canary run.
- `board-events.json`: `+11` events total.
- `board-events.jsonl`: `+11` lines total.
- Canary board-event lines: `10`.

Unrelated concurrent events in the same window:
- `cost-anomaly:cache_miss_above_90pct` by `cost-anomaly-detector`.
- `task-updated` by `atlas-receipt-stream` for task `e40a90c9-238f-4b68-aba3-a5123f54f913`.

