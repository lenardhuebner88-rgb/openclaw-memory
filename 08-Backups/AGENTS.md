# 08-Backups — Config & State Snapshots

**Purpose:** Automated daily snapshots of critical state (atlas session, openclaw config).
**Writers:** `.openclaw/scripts/config-snapshot-to-vault.sh` (cron 03:00) + `.openclaw/scripts/atlas-state-snapshot.sh`.
**Readers:** humans for audit, not agents.

## Structure
- `atlas-snapshots/atlas-snapshot-YYYYMMDD-HHMMSS.md`
- `openclaw-config-backups/YYYY-MM-DD/{openclaw.json, scripts/}`

## Rules
- Do NOT hand-edit anything here — it is machine state.
- Retention: 90 days; older snapshots prune into `09-Archive/backups-YYYY-MM.tar.zst`.

## Never touch
- Anything in here, period. Read-only for humans except in incident recovery.
