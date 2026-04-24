---
title: Sprint-M Session Closeout + Forge Verification (2026-04-21)
status: report
---

# Sprint-M Session Closeout + Forge Verification (2026-04-21)

## Scope
- Non-QMD operative Stabilisierung
- Auto-pickup / worker / board path hardening
- OpenClaw session-routing root cause isolation
- Forge claim verification for `efficiency-auditor` / Lens on the live auto-pickup path

## Out of Scope
- Keine QMD-Arbeit
- Keine Änderungen an QMD-cron, QMD-registry oder QMD-Pfaden

## Implemented

### 1. Auto-pickup / board hardening
- Changed: `/home/piet/.openclaw/scripts/auto-pickup.py`
- Changed: `/home/piet/.openclaw/scripts/tests/test_auto_pickup.py`
- Changed: `/home/piet/.openclaw/scripts/healthcheck-watchdog.sh`
- Changed: `/home/piet/.openclaw/workspace/mission-control/src/lib/worker-terminal-callback.ts`
- Changed: `/home/piet/.openclaw/workspace/mission-control/tests/worker-terminal-callback.test.ts`
- Changed: `/home/piet/.openclaw/workspace/mission-control/tests/fail-pending-pickup-regression.test.ts`

Key results:
- stale redispatch behavior in auto-pickup reduced by live re-read before trigger
- session-lock handling aligned against the real session store
- pre-claim `pending-pickup` tasks can now be terminalized cleanly instead of poisoning the board forever
- watchdog detects lane-jam patterns more conservatively on the existing healthcheck path

### 2. OpenClaw routing hotfix for real fresh retry sessions
- Changed: `/home/piet/.npm-global/lib/node_modules/openclaw/dist/register.agent-COPfBHma.js`

Key result:
- `auto-pickup.py` already used explicit retry session keys, but the Gateway CLI path dropped `opts.sessionKey`
- patched `agentViaGatewayCommand()` to forward `sessionKey: opts.sessionKey` into `resolveSessionKeyForRequest(...)`
- this converted the retry path from fake-fresh to truly isolated session routing

### 3. Auto-fail alert path fix
- Changed: `/home/piet/.openclaw/scripts/auto-pickup.py`
- Changed: `/home/piet/.openclaw/workspace/mission-control/src/app/api/discord/send/route.ts`

Key result:
- `auto-pickup.py` was using the MC fallback alert path with a stale ingress class (`write`)
- the route also did not accept the existing `channelId + message` payload shape used by auto-pickup
- fixed caller header to `x-request-class: admin`
- added a direct-message branch in `/api/discord/send` for `channelId + message`
- after restart of `mission-control.service`, live probe succeeded and `auto-pickup.py` logged `ALERT_SENT`

### 4. systemd unit hardening for the active production path
- Changed: `/home/piet/.config/systemd/user/m7-auto-pickup.service`

Key result:
- added `KillMode=process`
- reloaded systemd and restarted `m7-auto-pickup.timer`
- validated that `m7-auto-pickup.service` can now finish while leaving its spawned worker process alive

## Root Cause Confirmed

### A. `sre-expert` retry path
The main hard root cause for the earlier `sre-expert` incident was not simply "a stuck lane" but incorrect retry routing semantics:
- `openclaw agent --agent <id> --session-id <custom>` pinned to `agent:<id>:main`
- our retry path therefore did not create a real fresh worker session
- retries kept colliding with the main session bucket

Primary-source upstream match:
- Issue `#26058`: `--agent` + `--session-id` routes to agent main bucket
- Issue `#36401`: `--session-key` requested as the smallest CLI fix
- PR `#36448`: proposed CLI wiring for `--session-key`, not merged

References:
- https://github.com/openclaw/openclaw/issues/26058
- https://github.com/openclaw/openclaw/issues/36401
- https://github.com/openclaw/openclaw/pull/36448

### B. Gateway / transport residual risk
Separate from the retry-routing bug, local Gateway websocket instability still exists:
- repeated `closed before connect code=1006`
- known issue family includes handshake / challenge timeout and lane backlog under gateway load

References:
- https://github.com/openclaw/openclaw/issues/49726
- https://github.com/openclaw/openclaw/issues/45419
- https://github.com/openclaw/openclaw/issues/51987
- https://github.com/openclaw/openclaw/issues/42097
- https://github.com/openclaw/openclaw/issues/57425

### C. systemd migration interaction on the active path
Claude's architecture claim was tested directly on this host and is materially correct:
- `Type=oneshot` + default `KillMode=control-group` kills a background child when the service exits
- `Type=oneshot` + `KillMode=process` leaves the child alive after the service ends

This was verified with transient systemd units:
- `codex-oneshot-killtest.service`:
  - service finished
  - child PID was gone immediately
- `codex-oneshot-processtest.service`:
  - service finished
  - child `sleep 45` remained alive

So the Claude analysis is confirmed on the core mechanism, with one important nuance:
- `0`-byte run logs are not by themselves proof of a dead process
- a later `frontend-guru` live test showed a worker process alive, task already on `accepted/progress`, and the run log still `0` bytes until the process exited and flushed

## Verification Evidence

### 1. `sre-expert` live probe after hotfix
- Before fix: routing landed on `agent:sre-expert:main`
- After fix: routing landed on `agent:sre-expert:explicit:...`
- explicit key present in session store separately from main

### 2. `sre-expert` real board E2E
- Real task: `6a385845-baef-480d-9494-9b73eb4f3e49`
- Lifecycle:
  - `assigned`
  - `pending-pickup`
  - `accepted`
  - `progress`
  - `result`
  - `done`
- Final:
  - `status=done`
  - `dispatchState=completed`
  - `executionState=done`

### 3. Tests
- `python3 /home/piet/.openclaw/scripts/tests/test_auto_pickup.py`
- Result: `9 tests, OK`

### 4. Alert-path live probes
- Before fix:
  - `POST /api/discord/send` with `x-request-class: write` returned `403`
  - with `admin` but old payload shape handling, request reached business logic and returned `400`
- After route/caller fix + full `mission-control.service` restart:
  - `POST /api/discord/send` with `channelId + message` returned `200`
  - `auto-pickup.py alert()` probe logged:
    - `ALERT_SENT kind=live-probe-direct-postrestart transport=mc-api`

### 5. Four live agent E2E checks
- Forge / `sre-expert`
  - task: `3b45d061-d844-4225-88dd-590787d8bf0c`
  - result: `done`
- Lens / `efficiency-auditor`
  - task: `e0bb49ed-7bd0-4329-90a0-9b6e05306fe9`
  - result: `done`
- James / `james`
  - task: `96b66234-ddcc-410d-98d6-0cd98a79cf8b`
  - result: `done`
- Pixel / `frontend-guru`
  - task: `564b78ad-f814-45a1-ba0f-b7d8706fb3df`
  - result: `done`

All four agents completed a real read-only board task via the active worker path.

### 6. Real systemd-path verification after `KillMode=process`
- task: `67e87769-6635-4ef2-b212-aea2f8096e3e`
- trigger path:
  - `systemctl --user start m7-auto-pickup.service`
  - `m7-auto-pickup.service` exited as `inactive (dead)`
  - child processes remained alive in the unit after stop
  - task progressed to `accepted` and then `done`
- final summary:
  - `E2E systemd m7 path PASSED: hostname=huebners, date=2026-04-21T17:56:00UTC, systemd->auto-pickup->worker lifecycle completed.`

## Forge Verification

### Claim from Forge
Forge reported that the active production path for the Lens incident was:
- `m7-auto-pickup.timer`
- `m7-auto-pickup.service`
- `/home/piet/.openclaw/scripts/auto-pickup-runner.sh`
- `/home/piet/.openclaw/scripts/auto-pickup.py`

and that task `50998199-9c48-4640-b0bb-bd1f9464812c` failed due to repeated empty worker spawns for `efficiency-auditor`.

### What is confirmed
Forge was correct on these points:
- the active path is the systemd timer/service path above
- the old task `50998199-9c48-4640-b0bb-bd1f9464812c` was seen by `auto-pickup.py`
- it was triggered three times for `efficiency-auditor`
- all three spawn logs were `0` bytes:
  - `50998199-...__1776792418.log`
  - `50998199-...__1776792487.log`
  - `50998199-...__1776792557.log`
- the task was then auto-failed:
  - `AUTO_FAIL_UNCLAIMED task=50998199 agent=efficiency-auditor attempts=3 reason=dead-unclaimed-spawn`

### What is NOT confirmed
Forge was not correct on these points:
- `m7-auto-pickup.service` does **not** crash before each trigger
  - `journalctl --user -u m7-auto-pickup.service` shows repeated `Finished`, not service failure
- the live data does **not** support the broad statement "Lens session boot is broken"
  - manual `openclaw agent --agent efficiency-auditor ...` returned successfully with JSON
  - current real auto-pickup E2E for Lens also completed successfully
- the older `0`-byte observation is not sufficient by itself to prove immediate worker death
  - later `frontend-guru` run stayed `0` bytes while the worker was already `accepted/progress`, then flushed on completion

### Narrowed conclusion
The historical `50998199` failure was real, but the broader interpretation was too wide.

Best-supported reading from IST data:
- a transient spawn/transport failure happened on the live Lens task at that time
- this aligned with Gateway `code=1006` closes in the same window
- it is **not** currently reproducible as a general `efficiency-auditor` boot failure
- therefore the old incident should be treated as a real but isolated runtime failure, not as proof that the Lens path is generally broken

## Live Countercheck Against Forge

### Manual `efficiency-auditor` run
- Replayed the same style of message outside the board path
- Result: success, clean JSON response
- This disproved the stronger claim "Lens dies before any useful output on every spawn"

### Fresh real Lens E2E on active auto-pickup path
- Created and dispatched real task: `e0bb49ed-7bd0-4329-90a0-9b6e05306fe9`
- Triggered through the same active production path:
  - `m7-auto-pickup.service`
  - `auto-pickup-runner.sh`
  - `auto-pickup.py`
- Observed lifecycle:
  - `pending-pickup`
  - `accepted`
  - `result`
  - `done`
- Final state:
  - `status=done`
  - `dispatchState=completed`
  - `executionState=done`
  - `receiptStage=result`
  - `resultSummary="E2E Lens path verification PASSED: hostname=huebners, date=2026-04-21T17:42:05UTC, board lifecycle completed."`
- Run log for this task was non-empty and completed successfully:
  - `/home/piet/.openclaw/workspace/logs/auto-pickup-runs/e0bb49ed-7bd0-4329-90a0-9b6e05306fe9__efficiency-auditor__1776793282.log`

## Side Findings
- `AUTO_FAIL_UNCLAIMED` alert path currently logs:
  - `ALERT_FAIL kind=unclaimed-terminalized transport=mc-api err=HTTP Error 403: Forbidden`
- This is not the root cause of the worker failure, but it is a real secondary operational gap on the alerting path

## Current Assessment
- The concrete `sre-expert` retry-routing bug is fixed locally and live-verified
- The Lens incident `50998199` was real, but it does not prove a persistent Lens boot defect
- Forge's ingress analysis for the `403` was correct but incomplete:
  - first defect: wrong ingress class
  - second defect: fallback payload shape drift
- Claude's systemd mechanism diagnosis was materially correct and is now live-patched with `KillMode=process`
- The active Lens auto-pickup path is currently functional end-to-end
- Remaining risk is the broader Gateway transport instability (`code=1006`) and the fact that the OpenClaw hotfix currently lives in `node_modules`

## Smallest Next Steps
1. Preserve the `sessionKey` Gateway CLI hotfix as a reproducible patch so it survives package updates.
2. Keep `KillMode=process` and watch whether the historical `dead-unclaimed` rate drops on the real timer path.
3. Investigate the `code=1006` Gateway transport issue separately from worker routing.

## Claude Prompt Verification Addendum

### (1) KillMode effect on the real path
- Change timestamp for `m7-auto-pickup.service`: `2026-04-21T17:53:09.759287Z`
- Pre-window: `2026-04-21T15:53:09.759287Z` to `2026-04-21T17:53:09.759287Z`
- Post-window: `2026-04-21T17:53:09.759287Z` to `2026-04-21T18:13:40.517841Z`

Artifact table from `auto-pickup-runs/` plus `LOCK_REAP` correlation:

| Window | Agent Group | empty-live | empty-dead | non-empty |
| --- | --- | ---: | ---: | ---: |
| Pre | sre-expert | 2 | 44 | 4 |
| Pre | rest | 0 | 3 | 3 |
| Post | sre-expert | 0 | 0 | 0 |
| Post | rest | 0 | 0 | 3 |

Verdict:
- `empty-dead` on the real timer path disappeared in the measured post-fix window.
- The cgroup-kill class is therefore considered eliminated on the patched `m7-auto-pickup.service` path.
- The still-existing second `0`-byte class is not visible as final `0`-byte artifacts here because those logs flush on process completion.

### (2) Live split of the two `0`-byte mechanisms
- Fresh live probe: direct `openclaw agent --agent frontend-guru ... --json > /tmp/openclaw-fdproof-frontend.log`
- While process `3508904` was alive, the log file stayed at `0` bytes.

Verbatim evidence:

```text
LOG_SIZE_DURING=0
ERR_SIZE_DURING=0
FD_LS_BEGIN
l-wx------ 1 piet piet 64 Apr 21 20:12 /proc/3508904/fd/1 -> /tmp/openclaw-fdproof-frontend.log
l-wx------ 1 piet piet 64 Apr 21 20:12 /proc/3508904/fd/2 -> /tmp/openclaw-fdproof-frontend.err
FD_LS_END
FD1_READLINK_BEGIN
/tmp/openclaw-fdproof-frontend.log
FD1_READLINK_END
STACK_BEGIN
cat: /proc/3508904/stack: Permission denied
STACK_END
LSOF_BEGIN
openclaw 3508904 piet    1w      REG  252,0         0  3593451 /tmp/openclaw-fdproof-frontend.log
openclaw 3508904 piet    5r     FIFO   0,15       0t0 27254201 pipe
openclaw 3508904 piet    6w     FIFO   0,15       0t0 27254201 pipe
openclaw 3508904 piet    7r     FIFO   0,15       0t0 27254202 pipe
openclaw 3508904 piet    8w     FIFO   0,15       0t0 27254202 pipe
openclaw 3508904 piet   12r     FIFO   0,15       0t0 27261956 pipe
openclaw 3508904 piet   13w     FIFO   0,15       0t0 27261956 pipe
openclaw 3508904 piet   17r     FIFO   0,15       0t0 27254204 pipe
openclaw 3508904 piet   18w     FIFO   0,15       0t0 27254204 pipe
LSOF_END
WAIT_STATUS=0
LOG_SIZE_FINAL=13710
ERR_SIZE_FINAL=0
```

Verdict:
- `fd/1` pointed to the final log file while the process was alive and the file was still `0` bytes.
- This confirms a real buffered-output / write-at-end class independent of the old cgroup-kill failure mode.

### (3) `mission-control.service` ExecReload trap fixed
- `ExecReload` no longer does build-only.
- New path: `/home/piet/.openclaw/scripts/mission-control-reload.sh`
- Mechanism: build, then enqueue restart via transient systemd unit with `--on-active=1s`, so `reload` returns cleanly and the real process restart follows.

Proof cycle:
- `systemctl --user reload mission-control.service`
- Journal:

```text
2026-04-21T20:11:21+02:00 ... Reloading mission-control.service ...
2026-04-21T20:11:22+02:00 ... Recent build exists (99s old), skipping rebuild
2026-04-21T20:11:22+02:00 ... MISSION_CONTROL_RELOAD build_ok restart_enqueued_via_transient_unit
2026-04-21T20:11:22+02:00 ... Reloaded mission-control.service - Mission Control (Next.js Production).
2026-04-21T20:11:23+02:00 ... Stopping mission-control.service ...
2026-04-21T20:11:25+02:00 ... Started mission-control.service ...
2026-04-21T20:11:26+02:00 ... [reload-proof] api/health RELOAD_PROOF_20260421T181121Z_V3
```

This is the missing proof that a route code change becomes live after `reload`, not only after manual `restart`.

### (4) `sessionKey` patch persisted
- Patch file: `/home/piet/.openclaw/patches/openclaw-sessionkey.patch`
- Reapply script: `/home/piet/.openclaw/scripts/openclaw-sessionkey-patch-check.sh`
- Trigger: `openclaw-sessionkey-patch.path`
- Service: `openclaw-sessionkey-patch.service`

Verification:
- Touch trigger on package metadata:
  - `touch /home/piet/.npm-global/lib/node_modules/openclaw/package.json`
- Journal:

```text
2026-04-21T20:11:54+02:00 ... Starting openclaw-sessionkey-patch.service ...
2026-04-21T20:11:54+02:00 ... OPENCLAW_SESSIONKEY_PATCH already_present
2026-04-21T20:11:54+02:00 ... Finished openclaw-sessionkey-patch.service ...
```

- Patch file also validates against a fresh `openclaw@2026.4.15` tarball and applies cleanly in a temp root.

### New Defect found during verification
- The first version of the reapply helper used `rg`, but `/usr/local/bin/rg` on this host is not executable (`Exec format error`).
- The helper was hardened to use `grep -Fq` instead.
