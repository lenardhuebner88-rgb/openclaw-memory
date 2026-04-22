# Memory Governance

## Source of Truth by Tier

### Tier 0 — Working Memory
- Scope: current session, active task, recent tool outputs
- Storage: prompt/context window only
- Lifetime: session-bound
- Rule: keep small and task-local, never treat as durable truth

### Tier 1 — Episodic Memory
- Source of truth: `memory/YYYY-MM-DD.md`
- Purpose: append-only daily events, decisions, status changes, noteworthy context
- Lifetime: 14 days in active memory, then archive
- Writers: agents, debrief flows, targeted append operations

### Tier 2 — Semantic Memory
- Source of truth: `MEMORY.md`, `memory/GOVERNANCE.md`, other curated durable docs
- Purpose: stable facts, preferences, decisions, durable procedures, long-lived system knowledge
- Lifetime: permanent until explicitly revised
- Rule: no operational TODO piles here

### Tier 3 — Archive
- Source of truth: `memory/archive-YYYY-MM-DD.md`
- Purpose: older daily history after active retention expires
- Lifetime: 90 days from archive cutoff unless kept intentionally elsewhere
- Rule: reference-only, not part of normal startup context

### Tier 4 — Learnings
- Source of truth: `memory/learnings.md`
- Purpose: repeated failures, patterns, lessons, candidate improvements
- Lifetime: rolling permanent log, deduped and curated
- Rule: promote durable truths to Tier 2, convert actionables into board tasks

## Secondary / Reference Files
- `memory/readme.md`
  - format and usage rules for daily memory
- `memory/template-daily.md`
  - template for new daily files
- `memory/nightly-builds.md`
  - build/change log, not canonical long-term truth
- `memory/evening-debrief-*.md`
  - structured reflection artifacts, input to learnings and task extraction
- `memory/.dreams/short-term-recall.json`
  - retrieval cache, bounded derived data, not a source of truth

## Memory Loading Chain

### Main Session
1. `SOUL.md`
2. `USER.md`
3. `memory/YYYY-MM-DD.md` for today and yesterday only
4. `MEMORY.md` only in the direct main session
5. targeted retrieval via `memory_search` when needed

### Heartbeat Chain
1. `SOUL.md`
2. `USER.md`
3. `HEARTBEAT.md`
4. targeted retrieval only if the heartbeat task needs it

### Subagent Chain
1. `SOUL.md`
2. `USER.md`
3. parent task brief
4. task-specific files only
5. avoid loading `MEMORY.md` unless explicitly required

## Consolidation Rules
1. Extract, do not dump. Store only salient events, facts, decisions, and patterns.
2. Promote from Tier 1 or Tier 4 into Tier 2 only when information is durable or repeatedly useful.
3. Keep operational work in the task board, not in `MEMORY.md`.
4. Deduplicate learnings by identity, date, and normalized text.
5. Merge repeated patterns into a single clearer learning instead of appending noise.
6. Archive old daily files after 14 days.
7. Delete old archives after 90 days unless intentionally preserved elsewhere.
8. Keep `short-term-recall.json` under 100 KB and trim entries older than 7 days.

## Retrieval Order
When answering or resuming work, prefer this order:
1. matching Tier 0 task context
2. relevant Tier 1 daily files for today or yesterday
3. Tier 2 curated memory
4. Tier 4 learnings if the question is about patterns or prior failures
5. Tier 3 archives only when recent memory does not cover it

## Guardrails
- Do not treat backup or derived files as canonical truth.
- Do not create parallel learnings stores.
- Do not keep stale open loops outside the board.
- Do not load large memory histories by default when selective retrieval will do.
