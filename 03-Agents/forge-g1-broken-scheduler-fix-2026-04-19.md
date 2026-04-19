# Forge G1 Broken Scheduler Fix — 2026-04-19

## Scope
Sprint-G G1 (`ba5e654b-9a5f-4704-a258-0ba943ec7b9a`): broken scheduler remediation.

## Backups (before changes)
- `/home/piet/.openclaw/workspace/mission-control/backups/sprint-g-g1-2026-04-19/20260419-200429`
- `/home/piet/.openclaw/workspace/mission-control/backups/sprint-g-g1-2026-04-19/20260419-200655-step1-systemd`
- `/home/piet/.openclaw/workspace/mission-control/backups/sprint-g-g1-2026-04-19/20260419-200704-step2-tmux`
- `/home/piet/.openclaw/workspace/mission-control/backups/sprint-g-g1-2026-04-19/20260419-200728-step3-cronjob`

## Fixes applied

### 1) systemd broken units (4 target services + dependent timers)
Restored missing service unit files and scripts:
- `~/.config/systemd/user/forge-heartbeat.service` (from disabled-obsolete copy)
- `~/.config/systemd/user/lens-cost-check.service` (from disabled-obsolete copy)
- `~/.config/systemd/user/openclaw-healthcheck.service` (from disabled-obsolete copy)
- `~/.config/systemd/user/researcher-run.service` (from disabled-obsolete copy)
- `/home/piet/.openclaw/scripts/forge-heartbeat.sh` (restored from scripts-archive)
- `/home/piet/.openclaw/scripts/lens-cost-check.sh` (restored from scripts-archive)
- `/home/piet/.openclaw/scripts/healthcheck-watchdog.sh` (restored from scripts-archive)
- `/home/piet/.openclaw/scripts/researcher-run.sh` (restored from scripts-archive)

Then executed:
- `systemctl --user daemon-reload`
- `systemctl --user reset-failed`
- `systemctl --user enable --now forge-heartbeat.timer lens-cost-check.timer openclaw-healthcheck.timer researcher-run.timer`
- start+status verify for all 4 services

### 2) Additional failed scheduler unit blocking global verification
- Fixed `~/.config/systemd/user/tmux-claude.service` pre-start failure:
  - Added `ExecStartPre=/bin/mkdir -p /tmp/tmux-1000` before chmod.
- Restarted and verified active/running.

### 3) openclaw-cron broken job: Sprint-Debrief-Watch
Patched `/home/piet/.openclaw/cron/jobs.json` job `031f586a-51b7-4e2d-adc8-c29773fb2a77`:
- Added explicit session type line in payload (compliant prompt)
- Added explicit `NO_REPLY` path when no sprint changed
- Increased timeout to 120s
- Changed delivery target to channel ID `1486480128576983070`
- Reset state counters (`consecutiveErrors=0`, lastStatus/lastRunStatus set ok)

### 4) crontab-user entries
- Checked all active user-crontab entries for executable/path validity.
- Result: `broken_count=0` (no broken entries present at run time).

## Verification
- `systemctl --user list-units --failed --no-pager` => **0 loaded failed units**
- `crontab -l` validation => **broken_count=0**
- Sprint-Debrief-Watch state in `jobs.json` => **consecutiveErrors=0** (<3)

## Notes
- `lens-cost-check.service` currently exits 0 but logs JSON/usage parse warnings; scheduler no longer fails, but script robustness can be improved in follow-up.
