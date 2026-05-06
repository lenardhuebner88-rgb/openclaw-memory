# OpenClaw 2026.5.4 Update Execution Report

Status: completed with live gates passed
Date: 2026-05-06
Owner: Atlas
Scope: Controlled OpenClaw stable update from `2026.5.3-1` to `2026.5.4`

## Summary

OpenClaw was updated from `2026.5.3-1` to stable `2026.5.4` using the official updater. The update had to be launched from a transient systemd user unit because running it directly from the Discord/Gateway tool context is blocked by OpenClaw safety logic: the updater detected it was running inside the Gateway process tree and refused to stop/restart its parent Gateway.

The package update, package swap, doctor step, and plugin sync completed successfully. The updater then reported a final restart/health-wait problem because the restarted Gateway was already running on port `18789`. Live post-update verification passed, so no rollback was performed.

## Backup

Backup directory:

```text
/home/piet/.openclaw/backups/openclaw-update-2026-5-4-20260506T052705Z
```

Backup contents include:

- `openclaw.json`
- Gateway systemd unit dump
- Gateway systemd drop-ins
- Mission Control live data snapshot
- previous OpenClaw package tree `openclaw-package-2026.5.3-1`
- pre-update `openclaw status`
- pre-update Gateway health
- pre-update MC health
- pre-update worker/pickup proofs
- pre-update Gateway journal excerpt

## Preflight

Initial preflight issue:

- Manual execution of `/home/piet/.openclaw/scripts/gateway-port-guard.sh` was found to be unsafe as a passive preflight because it killed the live Gateway process on port `18789`.
- Gateway restarted successfully afterward.
- Plan was corrected: do not manually run `gateway-port-guard.sh` before update; it is suitable as an `ExecStartPre` guard during Gateway start, not as a harmless live preflight check.

Corrected passive preflight used:

- `openclaw update --tag 2026.5.4 --dry-run --json`
- config guard / validator
- `systemctl --user status openclaw-gateway`
- passive port check via `ss`
- Gateway `/health`
- MC `/api/health`
- worker reconciler proof
- pickup proof

Expected preflight state:

- Gateway live
- MC degraded only due to known blocked/stale T15 task
- Board issue count `0`
- Dispatch consistency issues `0`
- Worker/Pickup proofs ok

## Update Execution

Direct updater attempt from the live Gateway tool context was refused safely:

```text
openclaw update detected it is running inside the gateway process tree.
Gateway PID ... is an ancestor of this process, so this updater cannot safely stop or restart the gateway that owns it.
```

Update was then launched via transient systemd user unit:

```text
openclaw-update-2026-5-4-20260506T054538Z.service
```

Updater result before final restart check:

```text
Update Result: OK
Before: 2026.5.3-1
After: 2026.5.4
Steps:
  ✓ global update
  ✓ global install swap
  ✓ openclaw doctor
Plugins: 0 updated, 1 unchanged, 1 skipped
```

Final updater nuance:

- The updater reported that Gateway did not become healthy after restart and that port `18789` was already in use.
- Live inspection showed the port was occupied by the restarted OpenClaw Gateway itself.
- Gateway was active and healthy after the updater run.

## Post-Update Verification

Live post-gates passed:

- OpenClaw package: `2026.5.4`
- `openclaw status`: up to date, npm latest `2026.5.4`
- Gateway app: `2026.5.4`
- Gateway service: active/running, PID `2572457`
- Gateway `/health`: `ok/live`
- Telegram channel: OK
- Discord channel: OK
- MC health:
  - board status: ok
  - board issueCount: `0`
  - dispatch status: ok
  - dispatch consistencyIssues: `0`
  - execution: degraded due to known `staleOpenTasks=1`, `recoveryLoad=1`
- Worker proof: ok, no issues
- Pickup proof: ok, no findings
- Model validation:
  - 57 cross-provider model references valid
  - 11 enabled cron jobs passed model/agent validation
  - 1 pre-existing warning: `nightly-self-improvement` timeout budget >600s

## Workspace / Commit

The validation run wrote a workspace validator log:

```text
memory/validators/2026-05-06.md
```

Committed:

```text
43aef9b4 docs: add 2026-05-06 model validation log
```

Other pre-existing workspace dirty files remained untouched.

## Current Remaining Issue

Mission Control is still not fully green because of the known T15 blocked/stale task, not because of the update.

Known T15 context:

- T15 concerns controlled shadow telemetry smoke for large tool-result handling.
- Previous blocker: active Gateway runtime package lacked required shadow/tool-result components.
- After update: active OpenClaw package is now `2026.5.4`; tool-result summary/persistence components are present.
- Literal grep for `tool-result-shadow` marker in the active package did not return a direct match, so T15 still needs a focused smoke/proof run before it can be unblocked or closed.

## Rollback Decision

Rollback was not performed because live post-update gates passed.

Rollback path remains available if a delayed issue appears:

```bash
openclaw update --tag 2026.5.3-1 --yes
```

Backup directory remains available for config/systemd/state/package restore if package rollback is insufficient.

## Follow-Up Recommendation

Next step:

1. Run focused T15 shadow/tool-result smoke with synthetic non-secret large output.
2. Verify whether expected telemetry/summary behavior is observable on `2026.5.4`.
3. If successful: close/unblock T15 and re-check MC health for full green.
4. If not successful: keep MC degraded as known blocker and create a narrow follow-up with exact missing marker/behavior evidence.

## Lessons Learned

- Do not run `gateway-port-guard.sh` manually as a live preflight; it can kill the active Gateway.
- When executing `openclaw update` from an OpenClaw-driven chat/tool context, use an external shell or transient systemd user unit because the updater refuses to restart its own Gateway ancestor process.
- Treat updater final health-wait failures carefully: verify live Gateway status before rollback. In this run, the updater’s final failure was not an actual service failure.
