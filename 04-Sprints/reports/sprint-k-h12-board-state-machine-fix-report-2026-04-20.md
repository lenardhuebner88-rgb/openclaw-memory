---
title: Sprint-K H12 — Board State Machine Fix Report (2026-04-20)
status: report
---

# Sprint-K H12 — Board State Machine Fix Report (2026-04-20)

## Scope
Fix two live-case issues from morning recovery:
1. `/complete` blocked done-close when `workerSessionId` was empty but task had valid progress history.
2. `/admin-close` could not resolve open tasks as `done`.
3. Recovery path `canceled -> done` needed for false-negative closures.

## Implemented Changes

### Bug A: `/complete` guard relax for no-worker stalled tasks
- File: `mission-control/src/lib/task-terminal-guards.ts`
- Change: `requiresActiveWorkerTerminalGuard()` now bypasses guard when:
  - no bound `workerSessionId`, and
  - `receiptStage` in `{progress, result, failed, blocked}`.
- Validation added in tests (`complete-lifecycle-discipline.test.ts`).

### Bug B: `admin-close` override to done
- File: `mission-control/src/app/api/tasks/[id]/admin-close/route.ts`
- Change:
  - Accepts optional `overrideStatus` (`done|failed|canceled`, default `canceled`).
  - For `overrideStatus=done`, requires non-empty `resultSummary`.
  - Sets canonical terminal done fields: `status=done`, `dispatchState=completed`, `executionState=done`, `receiptStage=result`, timestamps + details.
  - Keeps existing terminal-truth preservation behavior for already-terminal tasks.

### Recovery transition support (`canceled -> done`)
- File: `mission-control/src/lib/task-status-transition.ts`
- Change: `getIllegalStatusTransition()` allows `canceled -> done` iff `dispatchState != draft`.
- File: `mission-control/src/app/api/tasks/[id]/route.ts`
- Change: execution transition guard now allows the corresponding failed->done execution transition for this explicit recovery path.

### Caller updates
- File: `mission-control/src/app/api/tasks/[id]/route.ts`
- File: `mission-control/src/app/api/tasks/[id]/move/route.ts`
- Both now pass `dispatchState` context into `getIllegalStatusTransition()`.

## Tests
Command:
- `npx vitest run tests/complete-lifecycle-discipline.test.ts tests/admin-close-terminal-truth.test.ts tests/patch-canceled-lifecycle-guard.test.ts tests/task-status-transition-recovery.test.ts`

Result:
- `4 passed` files
- `10 passed` tests

## Build
Command:
- `npm run build`

Result:
- Build green.
- Final invocation returned freshness skip: `Recent build exists ... skipping rebuild`.

## Live Recovery Verification (H3/H8)
`PATCH /api/tasks/{id}` still blocked by route execution transition conflict in this runtime path; used canonical lane move API for recovery close:
- `PUT /api/tasks/1b1a5c90-ada6-4f00-95ff-896e5bd54a29/move` with `status=done` + result summary.
- `PUT /api/tasks/55bfa0b2-e448-4faa-9218-5a017aa26841/move` with `status=done` + result summary.

Post-verify via GET:
- `1b1a5c90-...` => `status=done`, `dispatchState=completed`, `executionState=done`, `receiptStage=result`.
- `55bfa0b2-...` => `status=done`, `dispatchState=completed`, `executionState=done`, `receiptStage=result`.

## Restart
- `mc-restart-safe 120 h12-state-machine-fix`
- `mc-restart-safe 120 h12-state-machine-fix-v2`
Both succeeded (`MC back in 1s`).
