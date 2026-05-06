# T15 Runtime Package Sync + Smoke Plan

Status: planned / gated
Date: 2026-05-06
Owner: Atlas
Execution owner: Forge
Trigger: Post-update audit found T15 still blocked by runtime binary mismatch.

## Objective

Resolve the T15 blocker sustainably by proving and, only after explicit go, correcting the mismatch between the installed OpenClaw package version and the active runtime binary/code path, then rerunning the T15 shadow/tool-result smoke.

## Current Evidence

- OpenClaw update to `2026.5.4` completed and live gates passed.
- Worker/pickup proofs are clean.
- Lock/pickup warning context is historical, not current.
- T15 remains blocked because active global runtime/dist lacks expected shadow telemetry symbols.
- MC remains degraded only due the known blocked/stale T15 item.

## Sustainable Fix Strategy

1. Diagnose exact mismatch before mutation:
   - active process path and PID
   - global npm package path/version
   - package/dist tree that Gateway actually imports
   - expected symbol/file presence for shadow telemetry
   - systemd unit/drop-in ExecStart and environment
   - plugin sync state

2. Prepare rollback:
   - capture current package path/version
   - capture Gateway unit/drop-ins
   - capture `openclaw status`, Gateway health, MC health, worker/pickup proofs
   - confirm previous backup from update exists

3. Controlled sync proposal:
   - prefer official OpenClaw package/update/sync path
   - avoid manual symlink/file surgery unless separately approved
   - no data edits
   - no config/model/cron changes unless separately approved

4. Stop gate:
   - Forge must stop and ask for explicit Atlas/operator go before any runtime mutation or restart.

5. Execution after go:
   - perform bounded runtime package sync
   - use official Gateway restart path
   - verify Gateway health, MC health, worker/pickup proofs
   - rerun T15 smoke for `[tool-result-shadow]`

6. Completion:
   - if smoke passes: recommend unblocking/closing T15 via normal task lifecycle
   - if smoke fails: report exact missing symbol/path/runtime evidence and rollback recommendation

## Hard Anti-Scope

- No direct live data edits.
- No blind symlink swaps.
- No manual deletion of package trees/backups.
- No config, cron, model routing, or secret changes.
- No restart before explicit go.
- No closing/unblocking T15 without smoke proof.

## Acceptance Criteria

- Active runtime path and package version are consistent.
- Expected shadow telemetry/tool-result symbol is present in active runtime path.
- Gateway and MC health verified after sync/restart.
- Worker and pickup proofs clean after sync/restart.
- T15 smoke produces proof for `[tool-result-shadow]` or a precise blocker.
