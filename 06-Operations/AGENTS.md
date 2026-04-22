# 06-Operations — Live Operations Data

**Purpose:** Ops tables, backups, validations, runtime data snapshots.
**Writers:** operators + ops cron scripts.
**Readers:** agents (read-only for most).

## Rules
- `backups/` — snapshot outputs; NOT where `08-Backups/` lives (that is vault-level config).
- `Validations/` — manual test runs + smoke-test reports.
- Anything auto-generated (JSON dumps, CSV reports) must land here, not in `02-Docs/`.

## Never touch
- Live `tasks.json` or `events.jsonl` (authoritative source is `.openclaw/workspace/mission-control/data/`).
