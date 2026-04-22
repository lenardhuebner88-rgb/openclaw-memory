# 09-Archive — Cold Storage

**Purpose:** Historical content retained for reference / audit. Rarely read, never edited.
**Writers:** nightly archive cron + hand-archival during migrations.
**Readers:** occasional historical lookups.

## Structure
- `YYYY-MM/` — month-grouped archive
- `decommissioned/<thing>/` — explicitly retired projects or sub-vaults (e.g., `Openclaw-peter-nested-vault/`)

## Rules
- Append-only. Nothing leaves except to `/dev/null` during quarterly pruning.
- Archive entries keep their original filenames — no rename.

## Never touch
- Anything here, unless doing incident recovery or historical audit.
