# Nightly Builds Log

---

## 2026-04-06

### Model-ID Validator False Positive Fix

- **title:** Fix model-id-validator false positives — add missing VALID_PREFIXES
- **source:** errors
- **description:** validate-models.py had a hardcoded VALID_PREFIXES list missing prefixes used in openclaw.json: minimax/, ollama/, moonshotai/, claude-cli/, openrouter/x-ai/, openrouter/meta-llama/, openrouter/xiaomi/, openrouter/stepfun/, openrouter/z-ai/. Result: 16 model IDs flagged as invalid despite being correct.
- **status:** deployed
- **files changed:** /home/piet/.openclaw/scripts/validate-models.py
- **why selected:** model-id-validator cron produces false positive errors daily, masking real issues; fix is 1-file, no config changes
- **validation:** python3 validate-models.py → "✅ All 62 model IDs valid."; npm run build → exit 0 (from earlier)
- **impact:** model-id-validator cron will no longer spam #status-reports with false positives; 16 models now correctly recognized

---

## 2026-04-05

### Message-Delivery-Loop Bug

- **title:** Message-Delivery-Loop Bug Fix
- **description:** Lenard sendete einzelne Nachrichten die massiv dupliziert im Kontext ankamen (50-80+ Kopien). Ursache: wahrscheinlich Discord-Gateway- oder OpenClaw-Message-Delivery-Loop.
- **status:** blocked
- **date:** 2026-04-05
- **project/track:** infra / message-delivery
- **files changed:** none
- **why this was selected:** Bug wurde während des Tages (2026-04-04) gemeldet - Priorität 1 im Skill
- **validation result:** N/A - Blocked vor Implementation
- **blocker reason:** Task ist ambiguous - Ursache unklar ob Discord-Plugin, Gateway-Retry-Mechanismus oder Session-Zustellung. Skill verbietet ambiguous Items.

---

*Erster Nightly Build Run - keine vorherigen Logs vorhanden*
## 2026-04-06

### TypeScript Retry/Silencing Bugs in Task Lifecycle Routes

- **title:** Fix TypeScript bugs in retry logic and state transitions
- **source:** errors
- **description:** Three TypeScript errors silently prevented the task lifecycle system from working correctly: (1) retryCount and maxRetriesReached were not in the updateTask Pick type, so retry logic silently failed to write these fields; (2) receipt route set invalid dispatchState='assigned' and passed null to string fields; (3) complete-route and fail-route were not registered as valid MutationSource values.
- **status:** deployed
- **files changed:** src/lib/taskboard-store.ts, src/app/api/tasks/[id]/receipt/route.ts
- **why selected:** Top priority: errors that occurred today (retry failures on self-optimization-intelligence cron)
- **validation:** npm run build passed with exit code 0
- **impact:** Task retry logic now correctly persists retryCount/maxRetriesReached; dispatchState transitions are valid; MutationSource is complete for all lifecycle routes

---

## 2026-04-07

### Auto-Fix-Trigger v2: Escalation Caps + Systemic Error Detection

- **title:** Improve auto-fix-trigger.py with timeout escalation caps and systemic error detection
- **source:** errors
- **description:** auto-fix-trigger.py had two critical gaps: (1) no cap on timeout escalation — self-optimization-intelligence was auto-incremented from 45s to 405s+ without ever stopping; (2) LiveSessionModelSwitchError with no model override in payload was not detected — stability-test-3h-check has model=none yet still fails because the agent's default model is unavailable in isolated session context. Fix: two-pass algorithm (collect all fixes then write once to avoid mutation-during-iteration), escalation cap at 5 attempts then manual review flag, smarter timeout increments (+60s below 180s, +120s above), systemic error detection for model-switch errors without payload model override.
- **status:** deployed
- **files changed:** /home/piet/.openclaw/scripts/auto-fix-trigger.py
- **why selected:** LiveSessionModelSwitchError and timeout escalation are the top recurring error patterns (29 cron errors in learnings); fix is isolated to one script, no config changes
- **validation:** python3 auto-fix-trigger.py → correctly flags stability-test-3h-check as SYSTEMIC, self-optimization-intelligence at 600s cap with manual review flag; npm run build → exit 0
- **impact:** Timeout escalation spiral is now capped — jobs that can't be auto-fixed after 5 attempts are flagged for manual review instead of infinite auto-increment; systemic LiveSessionModelSwitchError (agent default incompatible with isolated session) is now recognized and not silently re-triggered

---

## 2026-04-08

### Fix Invalid ExecutionState 'pending' in Receipt Route

- **title:** Fix task retry logic — replace invalid ExecutionState 'pending' with 'queued'
- **source:** errors
- **description:** In src/app/api/tasks/[id]/receipt/route.ts, the retry-reset path set executionState to 'pending' which is not a valid ExecutionState value (valid: 'queued' | 'active' | 'started' | 'review' | 'done' | 'blocked' | 'failed'). This broke the task retry mechanism — failed tasks would get a TypeScript error and an invalid state after retry reset.
- **status:** deployed
- **files changed:** src/app/api/tasks/[id]/receipt/route.ts
- **why selected:** Top priority: active error in the task lifecycle system; retry-reset path was producing invalid ExecutionState, preventing failed tasks from being correctly requeued
- **validation:** npm run build passed with exit code 0
- **impact:** Task retry logic now correctly resets executionState to 'queued' (valid) instead of 'pending' (invalid), ensuring failed tasks can be properly retried without type errors


## 2026-04-09

### Core Task API Error-Handling Guardrails

- **title:** Add explicit error handling to the core task API routes
- **source:** autonomy
- **description:** Scanned all 6 nightly sources. The highest safe stability candidate was missing error handling in the two most critical board endpoints: `src/app/api/tasks/route.ts` and `src/app/api/tasks/[id]/route.ts`. Added try/catch wrappers so task store read/write failures now return structured JSON errors instead of unhandled route crashes.
- **status:** failed
- **files changed:** src/app/api/tasks/route.ts, src/app/api/tasks/[id]/route.ts
- **why selected:** Source 1 had recurring cron history but no single new safe one-file fix, source 2 had no stale board items, source 3 showed `ignoreBuildErrors: true` but that is not a safe nightly-sized fix, source 4 required config changes which are forbidden, source 5 showed no higher-impact safe cost fix, and source 6 exposed missing guardrails on the core task API.
- **validation:** Manual endpoint check passed: `GET /api/tasks` returned 200 and `GET /api/tasks/not-a-real-id` returned 404. Required `npm run build` failed before `next build` because the existing `clean` script exits with code 1 when Mission Control is already running (`MC running, skipping .next delete`). Therefore this run cannot be marked deployed.
- **impact:** Core board routes now fail more predictably with structured JSON error responses, but the nightly run remains failed until the build script itself is made runnable while Mission Control is live.
