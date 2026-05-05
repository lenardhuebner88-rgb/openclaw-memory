# REM Backfill systemJob PATH Fix Plan — 2026-05-05

## Scope

Exactly one approved fix: repair `/home/piet/.openclaw/scripts/rem-backfill-safe.sh` so the `memory-rem-backfill` systemd systemJob can find the OpenClaw CLI in the systemd user environment.

## Live evidence

- Mission Control health: `status=ok`, `openTasks=0`, `staleOpenTasks=0`, `recoveryLoad=0` at `2026-05-05T12:14:55Z`.
- Board consistency: `status=ok`, `issueCount=0`.
- Gateway health: HTTP 200, body `{ ok: true, status: live }`.
- Gateway service: `openclaw-gateway.service` active/running, `NRestarts=0`.
- OpenClaw recent warning/error logs for 120 minutes: no entries.
- Session health last 180 minutes: `suspectedStuck=0`, `withErrors=0`.
- `memory-rem-backfill` cron registry: OpenClaw cron disabled because migrated to systemd systemJob; systemJob enabled on `openclaw-systemjob-memory-rem-backfill.timer`; last registry status `error`.
- systemd journal for `openclaw-systemjob@c49eb440-6a6d-49fb-9809-225d6ccfa463.service` at `2026-05-05 02:45`: `/home/piet/.openclaw/scripts/rem-backfill-safe.sh: line 17: openclaw: command not found`.
- CLI exists at `/home/piet/bin/openclaw`; version: `OpenClaw 2026.5.3-1 (2eae30e)`.

## Intended diff

File: `/home/piet/.openclaw/scripts/rem-backfill-safe.sh`

Replace:

```bash
openclaw memory index --force
openclaw memory rem-harness --json > "$TMP"
```

With:

```bash
/home/piet/bin/openclaw memory index --force
/home/piet/bin/openclaw memory rem-harness --json > "$TMP"
```

## Backup

Create a timestamped backup before editing:

```text
/home/piet/.openclaw/scripts/rem-backfill-safe.sh.bak-20260505T121732Z
```

## Restart needed

No Gateway restart. No Mission Control restart. No timer restart expected for script-path-only change.

## Verification

1. Confirm script syntax: `bash -n /home/piet/.openclaw/scripts/rem-backfill-safe.sh`.
2. Run the script once directly: `/home/piet/.openclaw/scripts/rem-backfill-safe.sh`.
3. Confirm output contains `REM_BACKFILL_OK`.
4. Confirm generated JSON exists and parses: `/home/piet/.openclaw/workspace/memory/.dreams/rem-backfill-last.json`.
5. Confirm timer still exists: `systemctl --user list-timers 'openclaw-systemjob-memory-rem-backfill.timer' --all --no-pager`.

## Rollback

Restore the backup file if syntax or focused run fails:

```bash
cp /home/piet/.openclaw/scripts/rem-backfill-safe.sh.bak-20260505T121732Z /home/piet/.openclaw/scripts/rem-backfill-safe.sh
```
