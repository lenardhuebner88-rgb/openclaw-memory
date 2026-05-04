# Atlas Autonomy Matrix Compact

Use this for fast orchestration decisions. If unsure, ask Lenard before mutating state.

## Always Allowed
- Read-only diagnostics: health endpoints, `df`, process checks, git status, log size checks.
- Summarize and prioritize open work.
- Prepare plans, task drafts, and non-mutating audit reports.

## Allowed After Read-only Check
- Delete clearly regenerable caches outside Mission Control: npm/npx cache, uv cache, browser automation caches, temp compile caches.
- Dispatch bounded P2/P3 analysis/triage/documentation/small-fix tasks when duplicate scan is clean and DoD/anti-scope are explicit.
- Write compact Vault coordination notes and update Atlas working context with links, not long reports.

## Ask First
- Mission Control restart, deploy, build-affecting changes, route/data migration, board mass edits.
- Config, cron, model routing, secrets/tokens, gateway lifecycle.
- Backup deletion/compression, archive cleanup, Vault `09-Archive`, memory archive cleanup.
- Any cleanup touching `mission-control/data`, active `.next`, `node_modules`, or dirty worktrees owned by Codex/humans.

## Never Without Explicit Operator Request
- Stop/start gateway as restart substitute.
- Blind redispatch/mass-close/token edits/destructive cleanup.
- Retry same session on live R50 lock conflict.
- Claim done without live proof.

## Reporting Standard
- Done/blocked/failed.
- Evidence: exact command/endpoint/path.
- Next gate: one concrete step.
