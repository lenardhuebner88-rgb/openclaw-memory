# 00-Inbox — Staging / Proposals Gate

**Purpose:** Raw landing zone before promotion to `10-KB/`, `02-Docs/`, or `07-Research/`.
**Writers:** Human (lenard) directly. Agents MUST write to `00-Inbox/_proposed/` only.
**Readers:** Human review + nightly librarian cron.

## Rules
- Agent proposals go to `_proposed/YYYY-MM-DD_<agent>_<slug>.md` with frontmatter `{source_agent, proposed_for, vetted: false}`.
- Human or librarian cron promotes vetted items out of this folder.
- Nothing stays >14 days — auto-archive to `09-Archive/inbox/YYYY-MM/`.

## Never touch
- `Home.md` without operator approval (vault home).
