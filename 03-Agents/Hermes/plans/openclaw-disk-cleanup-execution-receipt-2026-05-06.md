# Disk Cleanup Execution Receipt — 2026-05-06

Scope: Approved execution of disk cleanup plan Step 1 and Step 2 only.

## Pre-checks

- Time: 2026-05-06T08:29:45+02:00
- Root FS before: `98G total / 81G used / 13G free / 87%`
- Mission Control: `active/running`, `NEXT_DIST_DIR=.next`, `WorkingDirectory=/home/piet/.openclaw/workspace/mission-control`
- Active build/install/test/browser processes: none found via process scan.
- Mission Control open file descriptors into old `.next*`: `0`
- Mission Control health before: `degraded warning` due existing `staleOpenTasks=1`, `recoveryLoad=1`.

## Step 1 executed — Mission Control non-live `.next*` cleanup

Kept:

- `/home/piet/.openclaw/workspace/mission-control/.next` — live runtime dir.
- `/home/piet/.openclaw/workspace/mission-control/.next-hermes-precommit-verify-20260506T001338` — retained verified rollback build.

Deleted non-live `.next*` candidates totaling about `4537.2 MB` dry-run estimate, including old Hermes diagnostics, rollback copies, verify builds, proof/debug builds, and `.next.bak-hermes-20260503T192025Z`.

Post Step 1:

- Root FS: `98G total / 77G used / 17G free / 83%`
- Mission Control health: still reachable; same existing `degraded warning` class.

## Step 2 executed — regenerable cache cleanup

Pre-cache sizes:

```text
654M /home/piet/.npm/_cacache
205M /home/piet/.cache/pip
123M /home/piet/.cache/pnpm
122M /home/piet/.cache/node-gyp
631M /home/piet/.cache/ms-playwright
279M /var/cache/apt
```

Actions:

- Ran `npm cache clean --force`.
- Ran `pip3 cache purge` — removed 488 files / 209.3 MB.
- Ran `pnpm store prune` — metadata cleared, no packages removed.
- Removed `/home/piet/.cache/node-gyp`.
- Removed `/home/piet/.cache/ms-playwright`.
- Attempted passwordless `apt-get clean`; skipped because sudo unavailable in this environment (`no new privileges`; `/etc/sudo.conf` ownership warning). `/var/cache/apt` remains ~279M.

Post Step 2:

```text
/home/piet/.npm/_cacache absent
/home/piet/.cache/pip 3.6M
/home/piet/.cache/pnpm 4.0K
/home/piet/.cache/node-gyp absent
/home/piet/.cache/ms-playwright absent
/var/cache/apt ~279M remains
```

Final root FS:

```text
98G total / 75G used / 19G free / 81%
```

## Post-checks

- OpenClaw Gateway `/health`: `{"ok":true,"status":"live"}`
- `openclaw-gateway.service`: `active/running`, `NRestarts=0`, `MainPID=2572457`
- Mission Control `/api/health`: HTTP 200, still `degraded warning` for pre-existing `staleOpenTasks=1`, `recoveryLoad=1`; not caused by cleanup.
- Remaining Mission Control build dirs:
  - `.next` = `474M`
  - `.next-hermes-precommit-verify-20260506T001338` = `407M`

## Result

Cleanup reclaimed roughly `6G` according to `df` (`81G used` → `75G used`) and moved root usage from `87%` to `81%` without restart or config change.

## Remaining low/medium-risk candidates

- `/var/cache/apt` ~279M — needs real sudo/root shell if desired.
- Backup retention/offload:
  - `/home/piet/backups/2026-05-04-pi-route-all-agents-20260504T184051Z` ~3.76G
  - older OpenClaw preupdate backups ~0.7G+
- Journals ~523M — can be vacuumed after incident evidence retention decision.
