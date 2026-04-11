# Context Management Implementation Plan

_Date: 2026-04-09_

## Objectives
- Replace ad-hoc memory loading with a clear loading chain.
- Split memory into explicit tiers with retention and promotion rules.
- Eliminate stale and duplicate memory artifacts.
- Bound short-term retrieval growth.
- Repair the learnings-to-tasks pipeline and nightly validation flow.

## Deliverables
1. Update `memory/GOVERNANCE.md` with Tier 0-4 architecture.
2. Add `memory/memory-rotation.py` for 14-day daily-note rotation, 90-day archive cleanup, and short-term recall pruning.
3. Add `memory/learnings-cleanup.py` for deduping `memory/learnings.md`.
4. Remove obsolete memory files and archive `OPEN-LOOPS.md`.
5. Repair `/home/piet/.openclaw/scripts/learnings-to-tasks.py` fallback chain and Discord diagnostics.
6. Fix `skills/nightly-self-improvement/SKILL.md` validation so active Mission Control does not break the run.
7. Write rollout summary to `memory/CONTEXT-MANAGEMENT-RESULTS-2026-04-09.md`.

## Memory Loading Chain
### Main Session
1. `SOUL.md`
2. `USER.md`
3. `memory/YYYY-MM-DD.md` for today and yesterday only
4. `MEMORY.md` only in the main session
5. Task-specific retrieval via `memory_search`

### Heartbeat Session
1. `SOUL.md`
2. `USER.md`
3. `HEARTBEAT.md`
4. Minimal targeted retrieval only when needed

### Subagent Session
1. `SOUL.md`
2. `USER.md`
3. Parent task brief
4. Narrow task-specific files only
5. No `MEMORY.md` unless explicitly required by the parent

## Tiered Memory Architecture
### Tier 0, Working Memory
- Current turn, recent tool outputs, active task state
- Lives only in prompt/session context
- Never persisted automatically

### Tier 1, Episodic Memory
- `memory/YYYY-MM-DD.md`
- Append-only event log for the last 14 days
- Rotated to `memory/archive-YYYY-MM-DD.md` after 14 days

### Tier 2, Semantic Memory
- `MEMORY.md`, `memory/GOVERNANCE.md`, durable decisions and stable facts
- Human-editable source of truth
- Updated by explicit promotion, not raw transcript dumping

### Tier 3, Archive
- `memory/archive-YYYY-MM-DD.md`
- Historical reference only
- Old archives older than 90 days are deleted automatically

### Tier 4, Learnings
- `memory/learnings.md`
- Pattern-level lessons and repeated failures
- Deduped regularly and promoted to Tier 2 when durable

## Consolidation Rules
- Promote only stable facts, repeated patterns, or durable decisions.
- Do not keep operative TODOs in `MEMORY.md`.
- Convert actionable learnings into board tasks, not memory clutter.
- Merge duplicates by identity plus normalized content.
- Prefer short summaries over full transcript excerpts.

## Automation Plan
- Run `memory/memory-rotation.py` daily.
- Run `memory/learnings-cleanup.py` before or after nightly learning jobs.
- Keep `memory/.dreams/short-term-recall.json` under 100 KB and 7-day retention.
- Keep learnings pipeline fallback order: Ollama, MiniMax, then graceful failure with diagnostics.

## Validation
- Verify file creation and updates.
- Verify obsolete files are removed or archived.
- Verify learnings pipeline loads MiniMax key from `workspace/openclaw.json` and handles Discord 403 clearly.
- Verify nightly skill uses `npx tsc --noEmit` instead of `npm run build`.

## Follow-up Recommendations
- Migrate any remaining operative TODOs from `MEMORY.md` into the task board.
- Add a persistent result log for `validate-models` in a future pass.
- Consider a later episodic JSON schema plus embeddings only after this files-first redesign is stable.
