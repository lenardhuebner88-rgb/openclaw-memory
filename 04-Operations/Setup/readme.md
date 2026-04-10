# Daily Memory System

## Source of Truth
- Daily memory lives in `memory/YYYY-MM-DD.md`
- Long-term memory lives in `MEMORY.md`
- Open operational follow-ups that are not yet board tasks live in `memory/OPEN-LOOPS.md`
- Daily files are append-only and store only important blocks (Option A)

See also: `memory/GOVERNANCE.md`

## Structured Entry Format
```markdown
### YYYY-MM-DDTHH:MM:SS+01:00 | project:general | type:decision | importance:high | id:YYYYMMDD-HHMMSS-general-decision
- Summary: Important distilled memory block
- Why it matters: Why this should be remembered later
- Context:
  - Supporting point
  - Supporting point
- Tags: #memory #decision
- Source: telegram direct chat
```

## Allowed types
- `decision`
- `task`
- `fact`
- `preference`
- `status`
- `risk`
- `idea`

## Write Rule (Option A)
Only write an entry if at least one of these is true:
- a decision was made
- a real commitment/task/follow-up was agreed
- a blocker/risk/status change matters
- a durable preference/fact was clarified
- a reusable insight is worth revisiting

Do not write:
- greetings / filler / jokes
- trivial one-off asks
- transcript dumps
- repeated restatements of the same point

## Retrieval Rule
When Lenard asks about:
- a date
- a project
- a previous decision
- what happened on a given day

Check in this order:
1. `memory/YYYY-MM-DD.md`
2. `MEMORY.md`

## Mission Control
- `/memory` is the workspace UI for browsing daily memory
- The UI should surface project, type, importance, source, and why-it-matters
