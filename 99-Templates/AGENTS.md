# 99-Templates — Obsidian Template Store

**Purpose:** Templater / QuickAdd / Periodic-Notes templates.
**Writers:** Human (lenard) only.
**Readers:** Obsidian Templater plugin on demand.

## Rules
- One file per template, flat (no nesting) — Templater picks them up faster.
- Templates follow naming: `<use-case>.md` (e.g., `daily-note.md`, `sprint-plan.md`, `incident-rca.md`).

## Never touch
- Templates used by active crons (e.g., `daily-reflection-template.md`). Breaking them breaks the nightly pipeline.
