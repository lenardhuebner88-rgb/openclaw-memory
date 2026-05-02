# Atlas Orchestrator Audit - 2026-05-02

## Scope

Audit target: Atlas as operator-facing orchestrator, including context management, session management, tools, memory, Mission Control dependency behavior, model routing, and timeout behavior.

Live evidence was collected on 2026-05-02 between 19:28 and 19:43 CEST from:

- `/home/piet/.openclaw/openclaw.json`
- `journalctl --user -u openclaw-gateway --since '2026-05-02 00:00'`
- `openclaw sessions --all-agents --active 1440 --json`
- `qmd status` and QMD search smoke
- Mission Control `/api/health`, `/api/tasks`, `/api/ops/pickup-proof`, `/api/ops/worker-reconciler-proof`
- Gateway `/v1/chat/completions` model gates for `openclaw/main` and `openclaw/sre-expert`

## Executive Finding

Atlas was operational but not acceptable as an orchestrator because multiple latency and context-fidelity risks stacked:

1. Gateway startup/prep overhead was consistently high before the model even answered.
2. QMD memory was previously denied for Discord channel sessions, causing context retrieval gaps exactly where the operator talks to Atlas.
3. Large long-lived sessions and context-overflow paths caused compaction and lock contention.
4. The old model path mixed OpenAI Codex and MiniMax fallbacks, so timeouts could move through slow provider lanes.
5. Mission Control runtime data lived inside the Git worktree, making recovery and repo hygiene fragile.
6. Atlas had no explicit offline/degraded Mission Control operating contract; if MC was down, the operator experience degraded instead of switching to a clear fallback procedure.

## Root Cause Analysis

### 1. Context Loss After 6-7 Messages

Observed causes:

- QMD scope denied Discord channel searches before the fix:
  - `qmd search denied by scope (channel=discord, chatType=channel, session=agent:main:discord:channel:1486480128576983070)`
  - Same denial was observed for James.
- Active Atlas sessions carry large context windows:
  - Recent Atlas Discord/main sessions report `contextTokens=272000`.
- Historical logs show context overflow and auto-compaction in worker lanes:
  - `context-overflow-diag`
  - `auto-compaction succeeded`
- Session resource loading repeatedly appears in the 0.5s-2.7s range, sometimes higher. When combined with large prompts and tool payloads, Atlas starts each answer with a heavy context tax.

Fixed now:

- `memory.qmd.scope` now explicitly allows Discord channel sessions.
- Atlas `tools.allow` no longer contains stale `qmd__*` and `taskboard__*` aliases that did not match any enabled plugin.

Remaining risk:

- Existing large sessions remain large. New turns work, but long-lived sessions still need a rotation/compaction policy tied to operator conversations.

### 2. Slow Answers

Typical pre-model overhead from logs:

- `core-plugin-tools`: about 5.0s-5.8s per turn.
- `system-prompt`: about 2.2s-3.2s per turn.
- `stream-setup`: about 2.5s-3.1s per turn.
- Total prep often lands at 11s-14s before user-visible answer generation.

Model gate after cleanup:

- Atlas `openclaw/main`, configured `openai-codex/gpt-5.5`: `MODEL_GATE_OK Atlas`, 49.6s, no fallback logged.
- Forge `openclaw/sre-expert`, configured `openai-codex/gpt-5.3-codex`: `MODEL_GATE_OK - sre-expert`, 24.5s, no fallback logged.

Conclusion:

- GPT-5.5 is usable but not fast enough for every operator turn.
- The current 49.6s Atlas gate is acceptable for deep orchestration only if Atlas has a clear "quick acknowledgment then deep work" pattern. It is not acceptable as the only conversational mode.

### 3. Timeout History

Observed timeout classes:

- GPT-5.5 surface errors around 12:13, 12:36, 12:54:
  - `surface_error reason=timeout from=openai-codex/gpt-5.5`
  - These occurred before the QMD-scope/tool cleanup and while Gateway prep remained heavy.
- MiniMax timeouts:
  - `MiniMax-M2.7` and `MiniMax-M2.7-highspeed` timed out in James/Lens lanes.
  - One MiniMax path timed out after about 300s and then fell back to GPT-5.5.
- Fetch timeouts around provider/channel startup also appeared, especially during Gateway starts.

Conclusion:

- OpenAI Codex was not globally broken. GPT-5.5 timed out under older orchestration conditions and long prompt/session load.
- MiniMax is a material timeout risk for critical operator lanes and should not be in Atlas/Forge first-line fallback.

### 4. Mission Control Down Handling

Mission Control now starts and serves from external state:

- Effective env: `MISSION_CONTROL_DATA_DIR=/home/piet/.openclaw/state/mission-control/data`
- `/api/tasks` reads 946 live tasks from State.
- `worker-reconciler-proof`: ok, 946 tasks, 850 runs, 0 critical.

Remaining gap:

- Atlas still relies operationally on MC for board truth and Discord reporting.
- There is no operator-facing degraded-mode protocol that says:
  - what Atlas can do if MC is down,
  - which files are fallback truth,
  - when to restart MC,
  - when to stop and report manual recovery,
  - how to avoid writing divergent board state.

## Target State

### Atlas

- Primary model: `openai-codex/gpt-5.5`.
- Fallbacks: `openai-codex/gpt-5.3-codex`, `openai-codex/gpt-5.4-mini`, `openrouter/auto`.
- No MiniMax in Atlas critical fallback path.
- Conversation mode:
  - fast acknowledgement within one short turn,
  - explicit context refresh before long work,
  - compact evidence bullets,
  - no silent deep runs without progress report.

### Forge

- Primary model: `openai-codex/gpt-5.3-codex`.
- Fallbacks: `openai-codex/gpt-5.5`, `openai-codex/gpt-5.4-mini`, `openrouter/auto`.
- No MiniMax in Forge critical fallback path.

### Memory

- QMD allowed for Discord channel sessions.
- QMD backlog target: less than 20 pending embeddings and trending down.
- Atlas must use explicit collection prefixes for important vault/doc retrieval when possible.
- Context refresh rule: before multi-step operator work, Atlas should retrieve:
  - current MC health,
  - current board summary,
  - current relevant vault sprint/plan,
  - latest session state if continuing old context.

### Session Management

- Add an Atlas operator-session rotation rule:
  - rotate or summarize after 6-8 substantial operator turns,
  - rotate immediately after context-overflow or repeated correction by operator,
  - preserve a short handoff note in vault before rotation.
- Treat context overflow and session lock timeout as degradation events, not normal noise.

### Mission Control Down Mode

If MC is down:

1. Atlas must not claim board truth from stale UI/API.
2. Atlas should read fallback files only:
   - `/home/piet/.openclaw/state/mission-control/data/tasks.json`
   - `/home/piet/.openclaw/state/mission-control/data/worker-runs.json`
   - `/home/piet/.openclaw/state/mission-control/data/board-events.jsonl`
3. Atlas may restart MC only through the documented safe gate:
   - typecheck/build when code changed,
   - `systemctl --user restart mission-control`,
   - curl health and board proof.
4. If data validation fails, Atlas stops and reports manual recovery instead of mutating.

## Implemented During This Run

- Migrated Mission Control runtime data out of the Git worktree:
  - new path: `/home/piet/.openclaw/state/mission-control/data`
  - backup: `/home/piet/.openclaw/backups/mission-control-data-pre-migration-20260502-193218`
- Patched Mission Control resolver default to `~/.openclaw/state/mission-control/data`.
- Patched reconciliation and dispatch scripts to use the new default data dir.
- Patched live OpenClaw scripts:
  - `auto-pickup.py`
  - `stale-lock-cleaner.sh`
  - `atlas-receipt-stream-subscribe.sh`
  - `atlas-orphan-detect.sh`
  - `openclaw-discord-bot.py`
  - `backfill-outcomes.py`
  - `s-health-bulk-close.py`
  - `workspace-backup.py`
- Added systemd environment drop-ins for M7 services, Discord bot, and system jobs.
- Restored repo-tracked `data/*` after migration; Git status no longer shows live `data/*` mutations.
- Set model routing:
  - Atlas primary GPT-5.5.
  - Forge primary GPT-5.3-Codex.
  - OpenAI-first fallbacks for both.

## Gates Already Passed

- Script syntax gates:
  - Node script checks passed.
  - Python compile checks passed.
  - Shell `bash -n` checks passed.
- Mission Control:
  - `npm run typecheck`: pass.
  - `npm run build`: pass.
  - service active after restart.
  - `/api/tasks`: 946 live tasks from State path.
  - `/api/ops/worker-reconciler-proof`: ok, 0 critical.
- Resolver:
  - `tests/data-dir-resolver-unification.test.ts`: 2/2 pass.
- Gateway:
  - `/health`: live.
  - Atlas model gate: pass on GPT-5.5, 49.6s.
  - Forge model gate: pass on GPT-5.3-Codex, 24.5s.
  - No fallback log for the two gate calls.

## Remaining Implementation Plan

### P0 - Operator Usability Guard

Add an Atlas response contract for operator-facing channels:

- First response must acknowledge, state live gate status, and either answer or declare deep-work mode.
- If expected work exceeds 30s, Atlas posts progress rather than appearing silent.
- If MC is down, Atlas switches to MC-down mode and states fallback files.

Acceptance:

- A Discord/operator smoke test shows a sub-10s acknowledgement pattern.
- A forced MC-down read-only drill produces a correct fallback status without mutation.

### P1 - Session Rotation And Context Handoff

Add/activate a policy that rotates or summarizes Atlas operator sessions after 6-8 substantial turns or after context-overflow.

Acceptance:

- Session-size guard detects Atlas operator sessions before context loss.
- A generated handoff contains current objective, live gates, files touched, and next action.

### P1 - Tool Prep Latency Reduction

Investigate `core-plugin-tools` fixed cost around 5s per run.

Candidate fixes:

- reduce Atlas default tool bundle,
- lazy-load tools by mode,
- remove unused provider/plugin entries from the critical path,
- add a fast operator lane for acknowledgement.

Acceptance:

- Warm Atlas prep time below 8s total, or a documented reason why OpenClaw runtime cannot yet do this.

### P1 - Memory Freshness

Keep QMD pending embeddings below 20 and add a visible warning if backlog rises.

Acceptance:

- QMD status smoke in health report.
- No `qmd search denied by scope` for operator Discord sessions.

### P2 - Model Policy

Use GPT-5.5 for Atlas deep orchestration, not necessarily every fast acknowledgement.

Acceptance:

- Atlas GPT-5.5 deep gate succeeds twice without fallback.
- Forge GPT-5.3-Codex execution gate succeeds twice without fallback.
- Timeout/fallback logs stay clean for 24h observation.

## Stop Conditions

- Any new `qmd search denied by scope` for Atlas Discord channel.
- Any Atlas GPT-5.5 timeout in a simple gate prompt.
- Mission Control health unreachable after restart.
- State-path and repo-path task counts diverge because a live writer went back to repo `data`.
- Git status shows tracked `data/*` modified again.

## Final Update - 2026-05-02 20:02 CEST

Additional fixes completed after the initial audit write-up:

- P0 operator rules were promoted into active bootstrap docs:
  - `/home/piet/.openclaw/workspace/AGENTS.md`
  - `/home/piet/.openclaw/workspace/HEARTBEAT.md`
  - `/home/piet/.openclaw/workspace/CONTEXT_MAP.md`
  - `/home/piet/.openclaw/workspace/docs/operations/WORKSPACE-GROUND-TRUTH.md`
  - `/home/piet/.openclaw/workspace/README.md`
- Real Atlas bootstrap proof after Gateway restart:
  - model route: `openclaw/main` -> `openai-codex/gpt-5.5`
  - duration: 51.6s
  - Atlas returned the new operator ACK, MC-down fallback path, and context-rotation rule.
- Old Atlas session overrides were rotated:
  - `agent:main:discord:channel:1486480128576983070`
  - `agent:main:main`
  - backups are under `/home/piet/.openclaw/backups/session-rotation-*`.
- Mission Control `/agents` had a stale model display bug:
  - root cause: `openai-codex/gpt-5.5` matched the broad `codex` display rule and was shown as `GPT-5.3-Codex`.
  - fixed in `src/lib/live-agent-data.ts` and `src/lib/team-data.ts`.
  - `/api/agents/live` now reports Atlas `GPT-5.5` and Forge `GPT-5.3-Codex`.
- E2E V3 route proofs passed:
  - `/overview`
  - `/taskboard`
  - `/team`
  - `/agents`
  - final model proof: `/agents` contains `GPT-5.5` on desktop and mobile, with no horizontal overflow and valid touch targets.
- Discord final report sent:
  - channel `1495737862522405088`
  - message `1500195675361644625`
