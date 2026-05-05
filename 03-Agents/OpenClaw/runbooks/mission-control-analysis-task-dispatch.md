# Mission Control Runbook — Analysis Task Dispatch Without Pickup Deadlock

Purpose: prevent read-only/review tasks from getting stuck in `pending-pickup` because they were created as operator-locked drafts.

## Rule

For worker-executable analysis/review tasks that should be picked up automatically:

- create them as `status=assigned`, not `draft`
- do **not** set `operatorLock=true`
- use `approvalClass=safe-read-only`
- set `assigned_agent` to the display owner, then dispatch with the concrete agent id
- verify after write with `GET /api/tasks/<id>`

Only use `operatorLock=true` when the task is intentionally waiting for operator approval and should **not** be auto-picked up.

## Symptom

Task remains:

- `status=pending-pickup`
- `dispatchState=dispatched`
- `executionState=queued`
- no accepted receipt / no promotion to `in-progress`

Pickup proof or auto-pickup log shows:

- `SKIP_OPERATOR_LOCK task=<prefix> locked_until=?`

## Fix

Preferred safe fix:

1. Admin-close the wrongly locked task with a clear reason.
2. Create a replacement task as unlocked `status=assigned` with `approvalClass=safe-read-only`.
3. Dispatch the replacement.
4. Verify:
   - wrong task is terminal/canceled
   - replacement is `pending-pickup` or later `in-progress`
   - pickup proof no longer shows `SKIP_OPERATOR_LOCK` for the replacement

Avoid patching `operatorLock=false` on an already-dispatched task when a worker run may already exist; closing and replacing is cleaner.

## 2026-05-05 Incident Note

Atlas created Forge review task `02f82b7a-7444-468b-885d-561560a1210f` as a locked draft. Auto-pickup skipped it with `SKIP_OPERATOR_LOCK`. The task was admin-closed and replaced by unlocked analysis task `29d14526-aecc-49cd-bf37-7e4680bbacd3`.
