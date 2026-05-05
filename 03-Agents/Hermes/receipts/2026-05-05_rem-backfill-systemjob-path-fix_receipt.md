# REM Backfill systemJob PATH Fix Receipt — 2026-05-05

## Result

Applied exactly one approved fix to make the `memory-rem-backfill` shell wrapper independent of the systemd user `PATH`.

## Live evidence before fix

- Mission Control `/api/health`: `status=ok`, `openTasks=0`, `staleOpenTasks=0`, `recoveryLoad=0` at `2026-05-05T12:14:55Z`.
- Mission Control board consistency: `status=ok`, `issueCount=0`.
- Gateway `/health`: HTTP 200, `{ ok: true, status: live }`.
- `openclaw-gateway.service`: `active/running`, `NRestarts=0`.
- OpenClaw recent warning/error logs for 120 minutes: no entries.
- OpenClaw session health last 180 minutes: `suspectedStuck=0`, `withErrors=0`.
- `memory-rem-backfill` registry state before fix: systemJob enabled, timer `openclaw-systemjob-memory-rem-backfill.timer`, last registry status `error`.
- systemd journal evidence: `/home/piet/.openclaw/scripts/rem-backfill-safe.sh: line 17: openclaw: command not found` during the `2026-05-05 02:45` run.
- OpenClaw CLI path verified: `/home/piet/bin/openclaw`, version `OpenClaw 2026.5.3-1 (2eae30e)`.

## Plan document

`/home/piet/vault/03-Agents/Hermes/rem-backfill-systemjob-path-fix-plan-2026-05-05.md`

## Backup

Created before editing:

`/home/piet/.openclaw/scripts/rem-backfill-safe.sh.bak-20260505T121732Z`

Backup and target were both present after backup creation:

- target: `757 bytes`, mode `775`
- backup: `757 bytes`, mode `775`

## Exact file changed

`/home/piet/.openclaw/scripts/rem-backfill-safe.sh`

## Exact diff summary

Changed only the two OpenClaw CLI invocations from PATH-dependent `openclaw` to absolute `/home/piet/bin/openclaw`:

```diff
-openclaw memory index --force
+/home/piet/bin/openclaw memory index --force

-openclaw memory rem-harness --json > "$TMP"
+/home/piet/bin/openclaw memory rem-harness --json > "$TMP"
```

No Gateway restart. No Mission Control restart. No timer/unit restart.

## Verification

1. Syntax check:
   - `bash -n /home/piet/.openclaw/scripts/rem-backfill-safe.sh` passed.

2. Direct focused script proof:
   - Command: `/home/piet/.openclaw/scripts/rem-backfill-safe.sh`
   - Result: success.
   - Terminal success line:

```text
REM_BACKFILL_OK out=/home/piet/.openclaw/workspace/memory/.dreams/rem-backfill-last.json bytes=12392201
```

3. Output JSON parse proof:

```text
json_ok /home/piet/.openclaw/workspace/memory/.dreams/rem-backfill-last.json bytes 12392201 type dict
keys workspaceDir,sourcePath,sourceFiles,historicalImport,remConfig,deepConfig,rem,grounded,deep
```

4. Timer existence proof:

```text
openclaw-systemjob-memory-rem-backfill.timer -> openclaw-systemjob@c49eb440-6a6d-49fb-9809-225d6ccfa463.service
NEXT Wed 2026-05-06 02:45:00 CEST
LAST Tue 2026-05-05 02:45:01 CEST
```

5. Failed systemd user units:

```text
0 loaded units listed.
```

## Residual note

The cron registry `systemJob.lastStatus` may still show the prior `error` until the next scheduled systemJob run updates registry metadata. The wrapper itself now runs successfully with the same command path that systemd will execute.

## Rollback

If needed:

```bash
cp /home/piet/.openclaw/scripts/rem-backfill-safe.sh.bak-20260505T121732Z /home/piet/.openclaw/scripts/rem-backfill-safe.sh
```
