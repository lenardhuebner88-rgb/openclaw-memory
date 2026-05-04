# Mission Control Discord Reporting E2E

Datum: 2026-05-04
Kanal: `1488976473942392932`
Marker: `MC-REPORT-E2E-20260504T122756Z`

## Verdict

YELLOW.

Die produktive Discord-Sendstrecke funktioniert: Direktnachricht, Dispatch-/Pending-Pickup-Report und Terminal-/Done-Report wurden von Discord angenommen und Mission Control persistiert die entsprechenden IDs.

Die Reporting-Kette ist aber nicht voll konsistent: `accepted` wird im realen Claim-Pfad nur als Board-Receipt geschrieben und nicht als Discord-Lifecycle-Report gesendet. Das passt zum beobachteten Symptom nach Abschalten des separaten Discord-Bots.

## E2E Canary

- Task: `84fb5510-bc04-4fab-a2e2-25baba8c589f`
- Run: `6a1260d7-d5e3-4c3c-b299-27d4cbc59bb2`
- Worker Session: `worker:mc-report-e2e-20260504`
- Statusfolge:
  - `draft`
  - `assigned`
  - `pending-pickup`
  - `in-progress` / `receiptStage=accepted`
  - `done` / `receiptStage=result`

## Backups

- `/home/piet/.openclaw/state/mission-control/data/tasks.json.bak-20260504T122756Z-discord-reporting-e2e`
- `/home/piet/.openclaw/state/mission-control/data/worker-runs.json.bak-20260504T122756Z-discord-reporting-e2e`
- `/home/piet/.openclaw/state/mission-control/data/board-events.json.bak-20260504T122756Z-discord-reporting-e2e`
- `/home/piet/.openclaw/state/mission-control/data/board-events.jsonl.bak-20260504T122756Z-discord-reporting-e2e`

## Discord Evidence

- Direct route smoke via `/api/discord/send`:
  - HTTP 200
  - messageId `1500836379750301728`
- Dispatch / pending-pickup report:
  - Mission Control log: `[dispatch-auto-report] {"taskId":"84fb5510-bc04-4fab-a2e2-25baba8c589f","reached":true,"messageId":"1500836385286918168"}`
  - persisted on task: `dispatchNotificationMessageId=1500836385286918168`
  - `dispatchNotificationSentAt=2026-05-04T12:27:58.650Z`
- Terminal result / done report:
  - persisted on task: `finalReportSentAt=2026-05-04T12:28:43.866Z`
  - persisted thread: `threadId=1500836577822249000`
  - `lastReportedStatus=result`
  - `lastReportedAt=2026-05-04T12:28:43.866Z`

Channel-readback via Discord GET returned `403 Forbidden`. Therefore arrival is proven by Discord POST success IDs and created thread ID, not by read-history retrieval.

## Board Evidence

Board events for the canary:

- `task-created`: to `draft`
- `move`: `draft -> assigned`
- `task-status-change`: `draft -> assigned`
- `task-dispatched`: `assigned -> pending-pickup`
- `receipt`: `accepted`
- `receipt`: `result`
- `admin-cleanup`: `lifecycle-receipt-result`
- `task-status-change`: `in-progress -> done`
- `materializer-ok`

Post-check:

- `/api/health`: OK
- `/api/board-consistency`: OK
- open tasks: `0`
- pending-pickup: `0`
- in-progress: `0`
- open worker-runs: `0`

## Code Path Evidence

`pending-pickup`:

- `src/lib/task-dispatch.ts`
- Dispatch calls `executionReportDispatch(activeTask)`.
- Result is persisted as `dispatchNotificationMessageId`, `dispatchNotificationSentAt`, or `dispatchNotificationError`.

`accepted`:

- `src/app/api/tasks/[id]/claim/route.ts`
- Claim sets:
  - `status='in-progress'`
  - `executionState='active'`
  - `receiptStage='accepted'`
  - `lastExecutionEvent='accepted'`
- Claim appends a Board `receipt` event.
- Claim does not call `emitTaskLifecycleReport`.
- Result: no Discord accepted report in the real Claim path.

`done/result`:

- `src/app/api/tasks/[id]/receipt/route.ts`
- Terminal result calls `emitTaskLifecycleReport(id, stage, ...)`.
- `src/lib/task-reports.ts` posts to Discord, creates a result thread for `result`, and persists final report metadata.

## Root Cause

The separate Discord bot likely used to cover or mirror lifecycle notifications that Mission Control core did not send directly.

After the Hermes integration / bot shutdown, the direct Mission Control path remains sufficient for:

- dispatch / pending-pickup
- terminal result / done

But not for:

- accepted via `/api/tasks/:id/claim`

This is a code-path gap, not a Discord token/channel outage.

## Recommended Fix

Primary action: add canonical accepted lifecycle reporting to the Claim route.

Minimal change:

1. Import `emitTaskLifecycleReport` in `src/app/api/tasks/[id]/claim/route.ts`.
2. After appending the accepted Board receipt, call `await emitTaskLifecycleReport(id, 'accepted')`.
3. Preserve existing behavior if Discord reporting fails: `emitTaskLifecycleReport` already catches report-send failures and continues with best-effort writes.
4. Add/update tests so claim-path accepted emits a report once and remains idempotent.

Validation:

1. Unit/integration test for claim accepted report.
2. `npx tsc --noEmit --pretty false`.
3. `npm run build` or approved live-build gate.
4. Restart Mission Control only after build.
5. Repeat this E2E canary and require:
   - pending-pickup messageId present
   - accepted `startedReportSentAt` present
   - done `finalReportSentAt` and `threadId` present
   - board consistency OK

## Fix Implementation

Status: implemented and live-validated.

Changed files:

- `/home/piet/.openclaw/workspace/mission-control/src/app/api/tasks/[id]/claim/route.ts`
- `/home/piet/.openclaw/workspace/mission-control/tests/worker-lifecycle-integration.test.ts`

Production change:

- Claim route imports `emitTaskLifecycleReport`.
- After the canonical accepted Board receipt is appended, Claim route calls `await emitTaskLifecycleReport(id, 'accepted')`.
- No custom Discord logic was added.

Test change:

- Worker lifecycle integration test now asserts:
  - accepted claim calls `emitTaskLifecycleReport(taskId, 'accepted')` exactly once.
  - duplicate claim does not emit another accepted report.
  - terminal result still calls `emitTaskLifecycleReport(taskId, 'result')`.

Validation:

- `npm run test:worker-lifecycle`: passed, 3 files, 8 tests.
- `npx tsc --noEmit --pretty false`: passed.
- `ALLOW_BUILD_WHILE_RUNNING=1 npm run build`: passed.
- `systemctl --user restart mission-control.service`: done.
- Mission Control active since `Mon 2026-05-04 14:39:27 CEST`, PID `1014552`, `NRestarts=0`.
- `/api/health`: OK.
- `/api/board-consistency`: OK.

## Post-Fix E2E Canary

Marker: `MC-REPORT-FIX-E2E-20260504T124035Z`

- Task: `ce09d2b6-0ca0-48bf-a520-cbe124716808`
- Run: `6a98732c-69cb-45f0-8467-3b5a1edce096`
- Worker Session: `worker:mc-report-fix-e2e-20260504`
- Statusfolge:
  - `draft`
  - `assigned`
  - `pending-pickup`
  - `in-progress` / `receiptStage=accepted`
  - `done` / `receiptStage=result`

Backups:

- `/home/piet/.openclaw/state/mission-control/data/tasks.json.bak-20260504T124035Z-accepted-reporting-fix-e2e`
- `/home/piet/.openclaw/state/mission-control/data/worker-runs.json.bak-20260504T124035Z-accepted-reporting-fix-e2e`
- `/home/piet/.openclaw/state/mission-control/data/board-events.json.bak-20260504T124035Z-accepted-reporting-fix-e2e`
- `/home/piet/.openclaw/state/mission-control/data/board-events.jsonl.bak-20260504T124035Z-accepted-reporting-fix-e2e`

Post-fix reporting proof:

- Direct route smoke:
  - messageId `1500839564707631155`
- Dispatch / pending-pickup:
  - messageId `1500839572550975499`
  - persisted as `dispatchNotificationMessageId`
  - `dispatchNotificationSentAt=2026-05-04T12:40:38.531Z`
- Accepted:
  - persisted as `startedReportSentAt=2026-05-04T12:40:39.160Z`
- Done / result:
  - `finalReportSentAt=2026-05-04T12:40:40.459Z`
  - `threadId=1500839581900083241`
  - `lastReportedStatus=result`

Post-fix board proof:

- Board events include `task-dispatched`, `receipt accepted`, `receipt result`, and `task-status-change in-progress -> done`.
- Worker run ended as `succeeded`.
- `/api/health`: OK, `openTasks=0`, `pendingPickup=0`, `inProgress=0`.
- `/api/board-consistency`: OK, `issueCount=0`.

Final verdict after fix: GREEN for the Mission Control lifecycle reporting chain.
