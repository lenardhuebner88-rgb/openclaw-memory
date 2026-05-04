# Mission Control Live Worker Lifecycle Canary - Blocked Pre-Claim Gate

Date: 2026-05-04

Mode:
- Phase 0 read-only preflight completed.
- Phase 1 backups completed.
- Phase 2 live canary not started.
- No Task was created.
- No dispatch, claim, receipt, or terminal update was executed.
- No Gateway restart.
- No Mission Control restart.
- No productive agent sessions touched.

## Preflight

Mission Control:
- `GET /api/health`: OK
- `GET /api/board-consistency`: OK
- Open tasks before canary: `0`
- In-progress tasks before canary: `0`
- Open worker-runs before canary: `0`
- `data/tasks.json`, `data/worker-runs.json`, `data/board-events.json`, and `data/board-events.jsonl` parsed/read successfully.

Available lifecycle endpoints confirmed from source:
- `POST /api/tasks`
- `POST /api/tasks/:id/dispatch`
- `GET /api/worker-pickups`
- `POST /api/tasks/:id/claim`
- `POST /api/tasks/:id/receipt`
- `GET /api/tasks/:id/events`
- `GET /api/board/snapshot`
- `GET /api/board-events`

## Backups

- `/home/piet/.openclaw/state/mission-control/data/tasks.json.bak-20260504T105616Z-mc-canary-worker-lifecycle`
- `/home/piet/.openclaw/state/mission-control/data/worker-runs.json.bak-20260504T105616Z-mc-canary-worker-lifecycle`
- `/home/piet/.openclaw/state/mission-control/data/board-events.json.bak-20260504T105616Z-mc-canary-worker-lifecycle`
- `/home/piet/.openclaw/state/mission-control/data/board-events.jsonl.bak-20260504T105616Z-mc-canary-worker-lifecycle`

## Blocker

Requested canary convention:
- `workerSessionId: mc-canary-worker-20260504`

Live API validation found before mutation:
- `src/lib/worker-session-id.ts` allows only these prefixes:
  - `gateway:`
  - `monitor:`
  - `worker:`
  - `agent:`
  - `cron:`

Therefore the requested exact `workerSessionId` would be rejected by `POST /api/tasks/:id/claim` with `invalid workerSessionId prefix`.

## Verdict

YELLOW / BLOCKED

The board lifecycle API path appears available, but the requested workerSessionId convention is incompatible with the live claim route validation. Canary was not executed because changing the workerSessionId to `worker:mc-canary-worker-20260504` would be an operator-visible convention change not explicitly authorized.

## Proposed Next Step

Approve one of:
- Use `worker:mc-canary-worker-20260504` as the canary workerSessionId.
- Temporarily broaden the claim validator for this explicit canary ID after a code review and test.

## Live Canary Executed After Worker Prefix Approval

Executed at: `2026-05-04T11:01Z`

Approved workerSessionId:
- `worker:mc-canary-worker-20260504`

Canary:
- Title: `MC-CANARY worker lifecycle post-beta4 stability check`
- TaskId: `c7dcb8b2-def2-4ed3-841d-ca9c9defb92b`
- RunId: `72fd1cb6-bd78-4fe1-9f6f-ae5985c6d9b1`
- WorkerSessionId: `worker:mc-canary-worker-20260504`
- WorkerLabel: `MC Canary Worker`
- Result: `MC_CANARY_OK`

Fresh backups before live mutation:
- `/home/piet/.openclaw/state/mission-control/data/tasks.json.bak-20260504T110005Z-mc-canary-worker-lifecycle-live`
- `/home/piet/.openclaw/state/mission-control/data/worker-runs.json.bak-20260504T110005Z-mc-canary-worker-lifecycle-live`
- `/home/piet/.openclaw/state/mission-control/data/board-events.json.bak-20260504T110005Z-mc-canary-worker-lifecycle-live`
- `/home/piet/.openclaw/state/mission-control/data/board-events.jsonl.bak-20260504T110005Z-mc-canary-worker-lifecycle-live`

API endpoints used:
- `GET /api/health`
- `GET /api/board-consistency`
- `POST /api/tasks`
- `POST /api/tasks/:id/dispatch`
- `GET /api/worker-pickups`
- `POST /api/tasks/:id/claim`
- `POST /api/tasks/:id/receipt`
- `GET /api/tasks/:id/events`
- `GET /api/board/snapshot?view=archive&mode=full`

Status sequence:
- `assigned`
- `pending-pickup`
- `in-progress`
- `done`

Lifecycle proof:
- Dispatch created exactly one open placeholder run.
- Placeholder workerSessionId was `gateway:c7dcb8b2-def2-4ed3-841d-ca9c9defb92b`.
- `/api/worker-pickups` showed the task exactly once as ready before claim.
- Claim bound the existing run to `worker:mc-canary-worker-20260504`.
- Claim set task `status=in-progress`, `executionState=active`, `receiptStage=accepted`.
- Board event `receipt/accepted` exists.
- Duplicate claim with a different workerSessionId returned `409`.
- Result receipt set `status=done`, `dispatchState=completed`, `executionState=done`, `receiptStage=result`, `resultSummary=MC_CANARY_OK`.
- Worker-run ended with `status=succeeded`, `outcome=succeeded`.
- Board event `receipt/result` exists.
- Board event `task-status-change in-progress -> done` exists.
- `/api/worker-pickups` showed no duplicate pickup after completion.
- `/api/board/snapshot?view=archive&mode=full` found the Canary task.

Postcheck:
- `GET /api/health`: OK
- `GET /api/board-consistency`: OK
- Open worker-runs after: `0`
- Open tasks after: `0`
- Orphaned dispatches after: `0`
- Gateway restart: no; `ActiveEnterTimestamp=Mon 2026-05-04 12:09:24 CEST`, `NRestarts=0`
- Mission Control restart: no; `ActiveEnterTimestamp=Mon 2026-05-04 11:09:43 CEST`, `NRestarts=0`

Data diff summary vs fresh backups:
- `tasks.json`: `+1` task, the Canary task.
- `worker-runs.json`: `+1` run, the Canary run.
- `board-events.json`: `+8` events total.
- Canary board events: `task-created`, `task-dispatched`, `receipt/accepted`, `receipt/result`, `admin-cleanup`, `task-status-change`, `materializer-ok`.
- One unrelated concurrent board event occurred during the window: `task-updated` by `atlas-receipt-stream` for task `e40a90c9-238f-4b68-aba3-a5123f54f913`.
- `board-events.jsonl`: `+8` lines; `8` lines contained the Canary taskId.

Final verdict:
- GREEN for Mission Control worker lifecycle.
- YELLOW for data-diff purity because one unrelated concurrent board event landed during the same window.
