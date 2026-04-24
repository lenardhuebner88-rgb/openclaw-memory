---
created: 2026-04-24T18:14:46Z
agent: codex
scope: mission-control worker structure hardening gate
status: worker-gate-green
confidence: 9/10
---

# Worker Structure Hardening Gate

## Executive Summary
- Worker gate is green: `worker-reconciler-proof=ok`, `pickup-proof=ok`, `openRuns=0`, `pendingPickup=0`.
- Production build completed and `mission-control.service` plus `openclaw-gateway.service` are active.
- Five useful live tasks were brought through to terminal green output after replacing two lost first-attempt gates with smaller retry gates.
- `/api/health` remains `degraded`, but the current blocker is not live worker execution. It is recovery/attention bookkeeping from failed/superseded tasks and recovery-ledger drift.
- Confidence for worker process stability after this run: 9/10. Not 10/10 because health/recovery semantics still need cleanup and the first Atlas/Forge large gates demonstrated `end_turn/no-result` and zero-byte-run failure modes.

## Live Gate Snapshot
- `GET /api/ops/worker-reconciler-proof?limit=50`: `status=ok`, `openRuns=0`, `issues=0`, `criticalIssues=0`, `proposedActions=[]`.
- `GET /api/ops/pickup-proof`: `status=ok`, `pendingPickup=0`, `claimTimeouts=0`, `activeSpawnLocks=0`, `activeSessionLocks=0`, `findings=0`.
- `GET /api/tasks`: no tasks in `pending-pickup` or `in-progress`.
- `systemctl --user is-active mission-control.service openclaw-gateway.service m7-auto-pickup.timer m7-worker-monitor.timer`: all `active`.
- `GET /api/board/snapshot?view=live`: 7,404 bytes, below 100 KB target.
- `GET /api/health`: `degraded` because `execution.recoveryLoad=5`, `attentionCount=5`; board and dispatch checks are `ok`.
- `GET /api/ops/reconcile-proof`: `degraded` with one warning `recovery-ledger-drift`.

## Code Changes
- `src/app/api/tasks/[id]/claim/route.ts`
  - Claim now requires a concrete `workerSessionId` for `pending-pickup`.
  - Claim writes `lastHeartbeatAt`.
  - Claim rebinds the worker-run placeholder through `syncWorkerRunBinding`.
- `src/app/api/tasks/[id]/receipt/route.ts`
  - Non-terminal receipts require a session binding if the task has none.
  - Non-terminal receipts refresh heartbeat and worker-run binding.
  - Retry pickup resets progress/stall baseline.
- `src/lib/worker-terminal-callback.ts`
  - Worker run records now support `lastHeartbeatAt`.
  - `syncWorkerRunBinding()` can update session, label, and heartbeat.
- `src/lib/taskboard-store.ts`
  - Preserves `lastHeartbeatAt`.
  - Keeps `pending-pickup` worker metadata instead of clearing it as queued reset state.
- `src/lib/worker-run-reconciler.ts`
  - Adds proposed action for `fail-active-task-without-open-run`.
- `scripts/worker-reconciler.mjs`
  - Supports executing `fail-active-task-without-open-run`.
- Tests updated:
  - `tests/pickup-claim-route.test.ts`
  - `tests/worker-run-reconciler.test.ts`

## Validation
- `npx vitest run tests/pickup-claim-route.test.ts tests/receipt-run-binding-regression.test.ts tests/worker-run-reconciler.test.ts tests/worker-flow-e2e.test.ts`
  - 4 files passed, 25 tests passed.
- `npm run typecheck`
  - passed.
- `npm run build`
  - passed after stopping Mission Control; production bundle rebuilt and service restarted.

## Worker Gate Tasks
Original stale/lost tasks were closed and replaced where needed:
- Original stale task `56fc8f1b-1c6d-4a98-b1ee-c9a3319e31f8` was failed as stale/no-process; useful work was carried through by Atlas retry `faef7ded-a53a-4c9c-b4d8-c60928b828a3`, `done/result`.
- Original stale task `53bce56b-e2aa-43fa-a354-1606922f553a` was carried through by Pixel gate `54316ed6-7037-4878-8a7e-bfeb2b178669`, `done/result`.
- Original stale task `44d8037a-ea0c-4358-a631-0563fdb33b18` was carried through by Lens gate `934acabf-43e2-4b57-8efb-eab1fdcd4fa7`, `done/result`.
- Forge first gate `d8deb3b3-a382-47c3-bb4b-dfe46cbf29bb` produced a zero-byte run log/no terminal receipt; useful work was carried through by Forge retry `d02cb065-0201-4c69-8889-9809c475160d`, `done/result`.
- Spark gate `546a107a-6c45-4c7f-b0ee-54b210923330`, `done/result`.

## Root Cause
- Primary issue: claim/receipt lifecycle did not consistently update worker-run truth and heartbeat truth. A task could be accepted while `worker-runs.json` still looked like a gateway placeholder or had no heartbeat proof.
- Secondary issue: active tasks whose worker process had already ended could stay open until a later reconciliation pass. The proof did not have a direct executable action for `active-task-without-open-run`; this is now covered.
- Operational issue: larger Atlas/Forge gates can still terminate without terminal receipts (`end_turn` without result, zero-byte run log). Smaller replacement gates completed cleanly, which isolates this as a runner/result-contract failure mode rather than a general pickup failure.

## Applied Runtime Cleanup
- Backups written before state mutation:
  - `/home/piet/.openclaw/backup/worker-state-2026-04-24-1739/tasks.before-reconcile.json`
  - `/home/piet/.openclaw/backup/worker-state-2026-04-24-1739/worker-runs.before-reconcile.json`
  - additional `tasks.before-atlas-forge-fail-retry.*.json` and `worker-runs.before-atlas-forge-fail-retry.*.json`
- Stale/lost worker runs were closed sequentially. Note: an early parallel cleanup attempt exposed JSON race risk; future state repair writes must be strictly sequential or guarded by file lock.

## Internet Research Notes
- systemd service restarts are subject to `StartLimitIntervalSec` / `StartLimitBurst`; this matches observed `start-limit-hit` risk for repeated pickup launcher failures. Source: https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html
- systemd handles leftover processes after service command completion according to `KillMode`; current `KillMode=process` explains why child worker processes can remain in the unit cgroup. Source: https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html
- systemd timers can combine `OnBootSec` and `OnUnitActiveSec` for regular activation; the current `m7-auto-pickup.timer` pattern is valid, but service isolation needs hardening. Source: https://www.freedesktop.org/software/systemd/man/systemd.timer.html
- Next.js production guidance supports building and testing a production build before serving; this validates the stop-build-start gate used here. Source: https://nextjs.org/docs/app/guides/production-checklist

## Next 5 Stabilization Points
1. Split pickup launcher and worker runtime into separate systemd scopes/units.
   - Why: `m7-auto-pickup.service` currently reports leftover child processes in its cgroup; this creates start-limit/noise risk.
   - Gate: timer run exits with no leftover child process warnings; spawned worker is tracked by its own unit/scope.

2. Add runner-exit-to-terminal watchdog.
   - Why: Atlas first gate ended with `end_turn` but no terminal receipt; Forge first gate created a zero-byte run log.
   - Gate: if runner exits and task is still active after grace, system posts a bounded `failed` or `blocked` receipt with run log pointer.

3. Persist explicit `claimState=claimed` and `claimedAt` in `worker-runs.json`.
   - Why: heartbeat now works, but run records still lack a first-class claimed marker in some paths.
   - Gate: every accepted task has `workerSessionId`, `lastHeartbeatAt`, `claimState=claimed`, and `claimedAt`.

4. Separate unresolved failures from superseded/replaced gate failures in health.
   - Why: `/api/health` is degraded although worker runtime is clean; recovery ledger needs a `supersededByTaskId` / `resolvedAt` semantics.
   - Gate: historical superseded failures do not keep health degraded; `/api/ops/reconcile-proof` explains remaining drift read-only.

5. Add a 5-agent soak suite with small tasks first, large tasks second.
   - Why: small replacement gates succeeded; large first gates exposed output/terminal-contract failure. The suite should detect both.
   - Gate: five small tasks and two larger orchestration tasks finish with terminal receipts; proof stays `ok` for 10 minutes after completion.

## Residual Risks
- Recovery/attention backlog is still visible in `/api/health`.
- `worker-monitor` still logs historical 409s on unrelated assigned-stall cleanup.
- Existing worktree contains many unrelated changes from prior/live work; this run did not normalize unrelated files.
- The first Atlas/Forge gate failures show a real runner/result-contract weakness even though replacement gates passed.
