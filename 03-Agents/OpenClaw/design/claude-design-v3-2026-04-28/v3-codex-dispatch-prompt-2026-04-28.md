---
title: V3 Taskboard Implementation Sprint — Codex Dispatch Prompt
date: 2026-04-28
status: ready-for-dispatch
scope: codex-init + atlas-autonomous-execution
target: Codex CLI (init+close) + Atlas Daemon (autonomous overnight execution)
agents: atlas, forge, pixel, lens, spark, james
source: claude-design-v3-2026-04-28 (polish pass)
related:
  - v3-status-derivation-spec.md
  - source-export-final-2026-04-28-2213/
---

> ## ⚡ UPDATED AFTER CODEX LIVE CHECK — 2026-04-28T22:35Z
> ## ⚡ UPDATED FOR AUTONOMOUS-NIGHT-RUN — 2026-04-28T23:15Z
> ## ⚡ UPDATED FOR FULL-ATLAS-AUTONOMY — 2026-04-28T23:45Z (Codex removed entirely; Atlas bootstraps via single morning POST)
> ## ⚡ Operator trigger now lives in `v3-morning-trigger.md` + `v3-atlas-bootstrap-task.json`. Atlas mission in `v3-atlas-mission.md`. This file remains as REFERENCE for slice details (Phase 1 description copy-source).
>
> - **verifiedAt:** 2026-04-28T22:35Z (live-check by Codex App)
> - **/api/health:** ok (status=ok, severity=ok, board.openCount=0, inProgress=0, review=0, blocked=0, failed=0, staleOpenTasks=0)
> - **/api/board/snapshot schema:** `{ generatedAt, view, tasks, summary }` — NO `openCount`/`consistencyIssues` at top level. Use `.summary.laneCounts`, `.summary.statusCounts`, `(.tasks | length)`.
> - **source-export-final hash:** identical to local v2 export (Codex App verified)
> - **mission-control worktree:** DIRTY incl. UI files. V3 sprint stays additive; existing dirty files OFF-LIMITS.
> - **/kanban-v3-preview:** 404 today (expected before Slice D — must NOT block P0)
> - **~/.openclaw/HALT:** does not exist
> - **changed decisions vs prior version:**
>   - 11 → **12** canonical statuses
>   - Phase-0 jq verification: use `summary.laneCounts/statusCounts`, NOT `openCount/consistencyIssues`
>   - Slice A split into A0 (visual primitives, parallel to F1) + A1 (typed integration, after F1)
>   - Slice E (IncidentStrip) acceptance: filter MUST include `stale`
>   - Slice I ControlBar: localStorage + URL-sync + keyboard (D/M/T) are real implementation requirements with tests
>   - Slice H Mobile: ControlBar compact-mode MUST hide Truth-rail toggle entirely
>   - Slice G Approval: REMOVED runtime operator-ack gate per operator request 2026-04-28T22:55Z. UI-Confirmation dialog is the safety layer
>   - Phase 0: document `git status --short` and dirty-file collision check
>   - **Execution model: codex-initiator + atlas-autonomous-overnight + codex-morning-close** (was: codex-sequential single-process). Sprint runs over night via existing Atlas auto-pickup pipeline. Single Codex trigger; no operator restart needed.
>   - **NEW Slice V0:** Atlas-Autonomy-Audit (Lens, parallel throughout). Tracks Atlas decisions, WIP-respect, dispatch latency, completion-rate. Doubles as Atlas-autonomy-phase test.
>   - **Slice G autonomous-mode constraint:** during overnight run, NO live task mutations. Build + unit-test + integration-test against mock data only. Live task validation deferred to operator morning review.
> - **remaining blockers:** none — sprint can start, Atlas takes over after Phase 2

# V3 Taskboard Implementation Sprint — Codex Dispatch Prompt

Atlas-orchestrated overnight execution. Codex performs Phase 0 (baseline read),
Phase 1 (sprint-task creation in Board), Phase 2 (handover to Atlas), then exits.
Atlas + Workers execute Phase 3 autonomously over night via existing auto-pickup
pipeline. Codex resumes for Phase 4 (morning review + sprint close).

Doubles as Atlas-Autonomy-Phase test (V0 audit slice).

============================================================
EXECUTION MODEL
============================================================

| Phase | Owner | When | Duration | Description |
|-------|-------|------|----------|-------------|
| 0 | Codex | Trigger evening | ~30min | Live-baseline + design-read + sprintplan write |
| 1 | Codex | Trigger evening | ~30min | Create 18 sprint-tasks in Board (1 master + 17 slices) |
| 2 | Codex | Trigger evening | ~5min  | Discord handover + cursor save + Codex exit |
| 3 | Atlas + Workers | Overnight | ~12h | Atlas auto-picks master, dispatches slices to workers via WIP-respected pipeline. Workers execute. Defense-crons monitor. |
| 4 | Codex | Next morning | ~30min | Resume, read gates.jsonl + Atlas-decisions, write summary, close sprint |

**No operator interaction overnight** unless Hard Rule #8 approval needed (Atlas
escalates via Discord and waits — does not block other slices).

============================================================
CODEX V3 TASKBOARD SPRINT — OPENCLAW MISSION CONTROL
============================================================

# === VARS ===
WORKDIR=~/.openclaw/workspace/mission-control
MEMORY=~/.openclaw/workspace/memory
DESIGN=~/vault/03-Agents/OpenClaw/design/claude-design-v3-2026-04-28
SOURCE=$DESIGN/source-export-final-2026-04-28-2213
SPEC_FILE=$DESIGN/v3-status-derivation-spec.md
SPRINT_FILE=$MEMORY/sprints/openclaw-v3-taskboard-sprint-2026-04-28.md
GATES_LOG=$MEMORY/sprints/v3-gates.jsonl
CURSOR=~/.openclaw/state/codex-v3-cursor.json
HANDOVER_FILE=~/.openclaw/state/v3-atlas-handover.json
HALT_FILE=~/.openclaw/HALT
SNAPSHOT_DIR=~/.openclaw/snapshots
ROLLBACK_SCRIPT=~/.openclaw/scripts/codex-rollback.sh
DISCORD_CHANNEL=1495737862522405088
API_BASE=http://127.0.0.1:3000
PREVIEW_ROUTE=/kanban-v3-preview
SPRINT_ID=v3-taskboard-2026-04-28

# === GOAL ===
Implement Claude Design V3 Final Taskboard (12 canonical statuses, 7 lanes) as
feature-flag-isolated preview at $PREVIEW_ROUTE without touching live /kanban,
/taskboard, or /dashboard routes. Codex initiates + hands off to Atlas. Atlas
orchestrates overnight via existing auto-pickup pipeline, dispatching to
Forge/Pixel/Lens/Spark/James workers. Codex closes sprint next morning.

Test outcome (Slice V0): Atlas autonomy phase quality — decisions, WIP-respect,
dispatch latency, completion-rate, defense-cron coordination.

# === VERBINDLICHE DEFINITIONEN ===
- destruktive Mutation: irreversible (DELETE, status→closed/cancelled, file-delete,
  schema-change). PATCH on reversible fields = NOT destructive.
- RiskTier: T1=read-only, T2=reversible-write, T3=irreversible-mit-recovery,
  T4=irreversible-ohne-recovery.
- approvalClass: auto | operator-ack | operator-explicit | blocked.
- WIP-aktiv: status ∈ {dispatched, in_progress, awaiting_receipt, pending-pickup}.
- Always-on Worker: systemd-Service, Timer or Cron <5min.
- State-Files (canonical-API-only): tasks.json, receipts/, memory/graph.jsonl,
  retrieval-feedback.jsonl, $MEMORY/00-control/*.
- Polish-Source: $SOURCE (final V3 with ControlBar, V3Final, useV3Health).
- Spec-Truth: $SPEC_FILE (status-derivation contract).
- Active incidents (V3): tasks where toV3Status(task) ∈ {failed, blocked,
  noheartbeat, stale} AND NOT isHistoricalFailedArtifact(task).
- Autonomous-Run: phases 3+4 — Atlas + Workers execute without Codex; Codex
  resumes only for Phase 4 morning close.
- Agent-profile mapping (for Atlas dispatch):
  atlas → main · forge → sre-expert · pixel → frontend-guru
  lens → efficiency-auditor · james → james · spark → spark

# === HARTE REGELN ===
1. Board = Source of Truth, API access preferred.
2. Canonical APIs only:
   - POST /api/tasks
   - PATCH /api/tasks/[id]
   - POST /api/tasks/[id]/dispatch
   - POST /api/tasks/[id]/receipt
   - POST /api/tasks/[id]/finalize
   - PUT /api/tasks/[id]/move
3. Preflight:
   - GET $API_BASE/api/health must respond
   - GET $API_BASE/api/openapi.json optional (404 = use known routes, NOT abort)
   - Snapshot schema: top-level is `{ generatedAt, view, tasks, summary }`.
     Counts live in `.summary.laneCounts` and `.summary.statusCounts`.
4. WIP-Limit: max 2 global, max 1 per agent. Atlas enforces during dispatch.
5. Atlas: exactly 1 decision per autonomy cycle.
6. No fanout, no zombies, no in-progress without accepted/started/result receipt.
7. Each worker execution requires receipt-evidence.
8. Operator-Approval REQUIRED for:
   sudo/root, systemctl --user enable/edit/link, new .service/.timer files,
   npm install/postinstall, secrets/auth, model-switch, destructive mutations,
   cron/timer/heartbeat/always-on, direct state-file writes,
   Discord-channel-switch, T3/T4, WIP-exceptions, writes under
   /home/piet/vault/00-control/.
   Atlas escalates via Discord and continues with next independent slice;
   does NOT block whole sprint.
9. Code changes (per slice, by worker):
   - Backup/snapshot first
   - npm run build
   - systemctl --user restart mission-control (only if route changed)
   - systemctl --user status mission-control --no-pager
   - curl-verify
   - Build-fail = STOP that slice, report FAILED, Atlas continues with next
     independent slice
10. Persona-Tags = owner-fields, NOT role-switch:
    atlas, forge, pixel, lens, james, spark.
11. NEW v3 files only in:
    - src/lib/v3/
    - src/components/v3/
    - src/app/kanban-v3-preview/
    - src/app/api/board/v3-health/
12. Existing files: ONLY @deprecated JSDoc comments allowed, NO logic changes.
13. UNTOUCHED routes and components:
    - /kanban (route + components)
    - /taskboard (route + components)
    - /dashboard (route + components)
    - /api/board/* (existing endpoints, except additive v3-health)
    - Any file in `git status --short` at sprint start (collected in Phase 0)
14. Active incidents must EXCLUDE historical failed artifacts. Use
    `isHistoricalFailedArtifact()` filter.
15. **Autonomous-night constraint:** Slice G must NOT execute live task
    mutations during Phase 3. Build + tests against mocks only. Live mutation
    validation deferred to operator morning review.

# === KILL-SWITCH (always active) ===
A) test -f $HALT_FILE → Atlas + Workers close current slice cleanly, save
   per-slice state, finalize Discord report, exit.
B) Operator posts "!sprint halt" in Discord → Atlas reads at next
   defense-cron tick (every 5min via session-health-monitor) and triggers (A).
C) 3 consecutive API-5xx OR 1× 423-Locked per slice → that slice auto-HALT,
   Atlas continues with next independent slice.
D) F1 (status-derivation) FAIL = sprint-blocking; all dependent slices
   wait. Atlas escalates via Discord.
E) Defense-cron `session-health-monitor` failure 3× in 30min → Atlas
   auto-HALT entire sprint, save full state, await operator.

# === RATE LIMITS ===
- Discord: max 10 msgs/min, 60s dedupe via SHA256(content), 3× 429 in 5min → STOP.
- Self-Healing: max 3 auto-tasks/h global, max 1/h per signature.
- Repair-Loop: 2 fail-cycles per signature → escalate, no 3rd attempt.
- Atlas decision rate: max 1 dispatch / cycle (existing rule R5).

# === REPORTING ===

**Phase 0/1/2/4** (Codex): JSONL append to $GATES_LOG + plain Discord report.
**Phase 3** (Atlas + Workers, autonomous): every slice transition (dispatch,
receipt-accepted, receipt-result) emits Discord report via existing Mission
Control reporting pipeline (POST /api/discord/send). Atlas writes hourly
"autonomy heartbeat" report with sprint progress.

NO embeds[], NO attachments, NO title-based task-embed.

Format:
[OPENCLAW V3 TASKBOARD SPRINT]
Phase: 0|1|2|3|4
Slice: <id/name>  (or "AUTONOMY HEARTBEAT" for hourly summary)
Status: PASS | PARTIAL | BLOCKED | FAIL | DISPATCHED | ACCEPTED
Owner: <owner_tag> (atlas|forge|pixel|lens|spark|james)

Kurzbefund:
- ...

Evidence:
- ...

Changed:
- ...

Next:
- exactly one next action

# === IDEMPOTENZ ===
- Each task created in Phase 1 has `decisionKey: SHA1("v3-sprint-2026-04-28-<slice-id>")`.
  Codex restart in Phase 0/1: existing decisionKey = no duplicate task.
- Each mutation gets UUIDv4 idempotency-key, persisted to $CURSOR.
- Restart: read cursor, skip completed gates, verify current via API-GET.
- File-writes via write-if-changed (SHA256-compare).
- Memory-appends with flock $MEMORY/.lock + duplicateKey check.

============================================================
SPRINT-MATRIX
============================================================

Dependency order (Atlas dispatches in this order, respecting WIP):
P0 → (F1 + A0) parallel → A1 → B → C → D → (F2 + E) parallel → (F3 + F) parallel
   → G → H → I → V (V0 throughout, V1+V2+V3 after I) → S8 (summary)

| id  | name                       | owner   | profile          | depends      | acceptance (executable, by worker)                                                         |
|-----|----------------------------|---------|------------------|--------------|--------------------------------------------------------------------------------------------|
| P0  | live-baseline + design-read| atlas   | main             | -            | spec read; $SOURCE inventoried; /api/health=200; sprintplan written; dirty-list saved      |
| F1  | status-derivation          | forge   | sre-expert       | P0           | toV3Status returns valid for 6 sample tasks + live snapshot; jest 100% branch-coverage     |
| A0  | visual primitives          | pixel   | frontend-guru    | P0           | StatusBadge, PriorityBadge, ReceiptStage, AgeTag, MeaningRail render with raw status props |
| A1  | typed integration          | pixel   | frontend-guru    | A0, F1       | Atoms accept V3Task; type-safe imports from src/lib/v3/types.ts                            |
| B   | TaskCard                   | pixel   | frontend-guru    | A1           | V3Card renders 6 sample tasks; click → onOpen(taskId) callback fires                       |
| C   | lane-states                | pixel   | frontend-guru    | B            | EmptyLane, LoadingLane, ErrorLane render; LaneHeader counts correct                        |
| D   | TaskboardShell             | pixel   | frontend-guru    | C            | $PREVIEW_ROUTE renders sidebar+sub-bar+5-lane-grid+footer; /kanban unchanged               |
| F2  | health-aggregation API     | forge   | sre-expert       | F1           | useV3Health() returns Health; computeIncidentTasks parity with health.incidentCount        |
| E   | IncidentStrip              | pixel   | frontend-guru    | D, F2        | Strip renders only when health.hasIncident; filter includes failed+blocked+noheartbeat+stale |
| F3  | atlas-suggest derive       | forge   | sre-expert       | P0           | /api/board/next-action returns suggestion; drawer renders it; no hardcoded strings         |
| F   | DetailsDrawer              | pixel   | frontend-guru    | E, F3        | $PREVIEW_ROUTE/[id] opens drawer; 9 sections present in order                              |
| G   | state-actions              | pixel + forge | frontend-guru + sre-expert | F | Confirm dialogs + gated wrappers wired; UI-confirmation pattern enforced; **mock-only tests during Phase 3** |
| H   | mobile                     | pixel   | frontend-guru    | F            | $PREVIEW_ROUTE on 390px: vertical stack, sticky header, sheet, ControlBar compact          |
| I   | ControlBar                 | pixel   | frontend-guru    | D            | Density+Mode+Truth-rail flip without reload; localStorage persist; URL-sync; D/M/T keyboard|
| V0  | atlas-autonomy-audit       | lens    | efficiency-auditor| parallel    | Atlas decision-log captured; WIP-respect tracked; dispatch-latency measured per slice      |
| V1  | A/B validation             | lens    | efficiency-auditor| E, I        | Parity report: counts match between /kanban and $PREVIEW_ROUTE                             |
| V2  | UX review ControlBar       | spark   | spark            | I            | 3-knob UX-review report; max 3 polish suggestions                                          |
| V3  | memory documentation       | james   | james            | parallel     | $MEMORY/01-agents/pixel/V3-CONTRACTS.md + CONTRACTS-INDEX entry                            |
| S8  | summary + roadmap          | atlas   | main             | V0+V1+V2+V3  | gates.jsonl complete; final discord report; next action defined; autonomy-test verdict     |

Blocking gates: P0 (read), F1 (status logic), V1 (parity).

============================================================
PHASE 0 — LIVE-BASELINE + DESIGN-READ (Codex, ~30min)
============================================================

Allowed tools: journalctl, systemctl status, GET /api/*, sqlite3 -readonly, ls, cat,
git status, mkdir for sprint/log dirs, write to $SPRINT_FILE, $GATES_LOG, $CURSOR.

Steps:
1. set -euo pipefail; trap 'report "TRAP" "FAIL" "Trap caught at line $LINENO" - - - atlas' ERR
2. mkdir -p $MEMORY/sprints ~/.openclaw/state $SNAPSHOT_DIR
3. Initialize $CURSOR if missing.
4. Initialize $GATES_LOG if missing.
5. Read $SPEC_FILE in full.
6. Read $SOURCE/mc-v3-final.jsx + mc-v3-foundations.jsx + mc-v3-drawer.jsx.
7. Verify health & snapshot:
   - test -w ~/.openclaw/state
   - curl -sS $API_BASE/api/health | jq '{status, severity, openCount: .board.openCount, inProgress: .board.inProgress, review: .board.review, blocked: .board.blocked, failed: .board.failed, stale: .board.staleOpenTasks}'
   - curl -sS $API_BASE/api/board/snapshot | jq '{laneCounts: .summary.laneCounts, statusCounts: .summary.statusCounts, taskCount: (.tasks | length), totalTasks: .summary.totalTasks}'
8. Capture baseline state:
   - date -Iseconds
   - hostname
   - git -C $WORKDIR status --short → save full output to $SPRINT_FILE under
     "## Dirty files at sprint start"
   - systemctl --user status mission-control --no-pager
9. Read existing context (read-only):
   - $MEMORY/MEMORY.md (if exists)
   - $MEMORY/feedback_system_rules.md (if exists)
   - $WORKDIR/src/lib/taskboard-types.ts
   - $WORKDIR/src/lib/task-runtime-truth.ts
   - $WORKDIR/src/lib/projections/task-lane.ts
   - $WORKDIR/src/lib/historical-failure-artifacts.ts
10. Dirty-file collision check: for each planned slice output path, grep against
    the dirty list. If any collision, mark that slice BLOCKED in sprintplan.
11. Write idempotent sprintplan to $SPRINT_FILE including:
    - dirty-file list
    - planned output paths per slice
    - any flagged collisions
    - "Atlas-Handover: planned" status
12. report "P0" PASS|PARTIAL|BLOCKED|FAIL ... atlas
13. If P0=PASS: proceed to Phase 1. If FAIL: exit, await operator.

============================================================
PHASE 1 — SPRINT-TASK CREATION (Codex, ~30min)
============================================================

Codex creates 18 tasks in the Board via canonical API. Atlas auto-pickup picks
them up in Phase 3.

Steps:
1. Create master orchestrator task FIRST:
   ```
   POST $API_BASE/api/tasks
   {
     "title": "[V3 Sprint] Atlas Orchestrator — V3 Taskboard Implementation",
     "description": "Master orchestration task. Reads $SPRINT_FILE for execution plan. Spec: $SPEC_FILE. Dispatch: <this file>. Dispatches sub-slices to workers per dependency graph in SPRINT-MATRIX. Respects WIP=2 global, 1/agent. Writes hourly autonomy heartbeat. Final report at S8.",
     "assignee": "main",
     "priority": "high",
     "approvalClass": "safe-read-only",
     "riskLevel": "low",
     "decisionKey": "v3-sprint-2026-04-28-master",
     "labels": ["v3-sprint", "orchestrator", "autonomy-test"]
   }
   ```
   Save returned `id` as `$MASTER_TASK_ID`.

2. Create 17 slice tasks (one POST each) with `parentTaskId: $MASTER_TASK_ID`:

   For each row in SPRINT-MATRIX (F1, A0, A1, B, C, D, F2, E, F3, F, G, H, I,
   V0, V1, V2, V3, S8 — 18 total — but S8 is owned by atlas inside the master,
   so 17 child tasks):

   ```
   POST $API_BASE/api/tasks
   {
     "title": "[V3 Sprint] Slice <id> — <name>",
     "description": "Owner: <owner> (profile: <agent-profile>). Dependencies: <depends>. Acceptance: <acceptance-text>. Read full slice details: $DESIGN/v3-codex-dispatch-prompt-2026-04-28.md section 'SLICE DETAILS' under '<id>'. Spec: $SPEC_FILE.",
     "assignee": "<agent-profile>",
     "parentTaskId": "$MASTER_TASK_ID",
     "priority": "<high if id in {F1,V1} else medium>",
     "approvalClass": "<gated-mutation if id == G else safe-read-only>",
     "riskLevel": "<medium if id in {G,F2,F3} else low>",
     "decisionKey": "v3-sprint-2026-04-28-<id-lowercase>",
     "labels": ["v3-sprint", "slice-<id-lowercase>"]
   }
   ```

3. Each task creation:
   - Idempotency: if task with same `decisionKey` exists, PATCH instead of POST
     (existing system handles this via dispatch-gate logic)
   - Validate response 200/201 + valid task.id
   - Append to $HANDOVER_FILE registry

4. After all 18 tasks created, write $HANDOVER_FILE:
   ```
   {
     "sprintId": "$SPRINT_ID",
     "createdAt": "<iso>",
     "masterTaskId": "<id>",
     "slices": [
       {"id": "F1", "taskId": "<id>", "owner": "forge", "profile": "sre-expert", "depends": [], "status": "draft"},
       {"id": "A0", "taskId": "<id>", "owner": "pixel", "profile": "frontend-guru", "depends": [], "status": "draft"},
       ...
     ],
     "specFile": "$SPEC_FILE",
     "dispatchPrompt": "$DESIGN/v3-codex-dispatch-prompt-2026-04-28.md"
   }
   ```

5. report "Phase1" PASS|PARTIAL|FAIL with task-id list.

============================================================
PHASE 2 — ATLAS HANDOVER (Codex, ~5min)
============================================================

Codex's final action before exit. Hands sprint over to Atlas.

Steps:
1. Plain-text Discord-Report announcing handover:
   ```
   [OPENCLAW V3 TASKBOARD SPRINT]
   Phase: 2 — Atlas Handover
   Status: DISPATCHED
   Owner: codex → atlas

   Kurzbefund:
   - 1 master task + 17 slice tasks created in Board
   - Sprint will execute autonomously over night
   - Master Task ID: <master-id>
   - Spec: $SPEC_FILE
   - Dispatch Plan: $DESIGN/v3-codex-dispatch-prompt-2026-04-28.md
   - Handover registry: $HANDOVER_FILE

   Evidence:
   - All 18 tasks acknowledged by API (200/201)
   - Atlas auto-pickup will pick master at next cycle (~60s)
   - Defense-crons monitoring (session-health, stale-lock-cleaner, r49-validator)

   Changed:
   - $HANDOVER_FILE created
   - $SPRINT_FILE written
   - 18 board tasks created

   Next:
   - Atlas picks up master orchestrator → dispatches F1 + A0 (WIP=2)
   - Workers execute overnight per SPRINT-MATRIX dependency graph
   - Operator: Codex resumes Phase 4 next morning for sprint close
   ```

2. Cursor save:
   ```
   {
     "phase": "2-handover-complete",
     "lastStatus": "PASS",
     "completed": ["P0", "Phase1", "Phase2"],
     "masterTaskId": "<id>",
     "handoverFile": "$HANDOVER_FILE",
     "next": "atlas-autonomous-phase-3",
     "expectedResumeAt": "<next morning iso>",
     "updatedAt": "<iso>"
   }
   ```

3. Codex exit 0.

============================================================
PHASE 3 — ATLAS AUTONOMOUS EXECUTION (Atlas + Workers, ~12h overnight)
============================================================

NO Codex involvement. Atlas + Workers run via existing Mission-Control pipeline.

**Atlas-side loop** (every auto-pickup cycle, ~60s):

1. Read master task (`$MASTER_TASK_ID`).
2. Read $HANDOVER_FILE for slice registry + dependency graph.
3. Determine eligible slices (deps satisfied AND not yet completed AND not WIP-blocking).
4. Apply WIP-Limit: max 2 in-progress globally, max 1 per agent-profile.
5. Dispatch eligible slice via POST /api/tasks/<id>/dispatch with dispatchTarget=<profile>.
6. Workers (sre-expert, frontend-guru, etc.) auto-pickup their dispatched tasks.
7. Track receipts (accepted, started, progress, result).
8. On worker `result` receipt: validate acceptance per SPRINT-MATRIX. PATCH task
   status to done|failed accordingly.
9. Hourly Discord report: "AUTONOMY HEARTBEAT" with completed/in-progress/blocked
   slice counts, total elapsed, est. remaining.
10. On any slice FAIL with id ∈ {F1, V1}: mark master "PARTIAL", continue with
    independent slices, escalate via Discord.
11. On all slices done OR sprint-fatal error: prepare final state for Phase 4.

**Worker-side loop** (per slice, per worker):

1. Auto-pickup slice task from Board.
2. POST receipt: stage=accepted.
3. Read slice details from $DESIGN/v3-codex-dispatch-prompt-2026-04-28.md
   section "SLICE DETAILS" for own slice id.
4. Read $SPEC_FILE for V3 contracts (status-derivation, lanes, types).
5. Read referenced source files in $SOURCE.
6. Snapshot WORKDIR state (per Hard Rule 9).
7. Implement slice (write NEW files only in approved paths per Hard Rule 11).
8. Run `npm run lint` + `npm run build` in WORKDIR.
9. If build PASS: POST receipt: stage=progress with file-list.
10. Run jest tests for own slice (if applicable).
11. Run `systemctl --user restart mission-control` ONLY if route changed (D, F).
12. Verify acceptance criteria executable (curl, jq).
13. POST receipt: stage=result with PASS|PARTIAL|FAIL + evidence.
14. Mark task done|partial|failed via PATCH.

**Defense-crons** (existing, run throughout):
- `*/5 session-freeze-watcher` — detect stuck sessions
- `*/5 stale-lock-cleaner` — release abandoned locks
- `*/10 session-health-monitor` — overall health
- `*/15 r49-claim-validator` — validate worker claims
- `0 */1 r48-board-hygiene` — board consistency

**V0 Autonomy Audit** (Lens, runs throughout):
Lens is dispatched as soon as master task is picked up. Lens runs a low-WIP
audit-loop reading:
- Atlas decision log
- Worker dispatch latencies (dispatchedAt → acceptedAt)
- WIP-respect tracking
- Defense-cron firing
- Receipt-completion-rate per slice

Lens writes incremental observations to:
$MEMORY/05-learnings/v3-atlas-autonomy-audit-2026-04-28.md

============================================================
PHASE 4 — MORNING REVIEW + SPRINT CLOSE (Codex, ~30min)
============================================================

Operator triggers Codex with same trigger-prompt next morning. Codex:

1. Read $CURSOR — confirm phase=2-handover-complete.
2. Read $GATES_LOG — see all Atlas/worker reports overnight.
3. Read $HANDOVER_FILE — verify all slice tasks status.
4. Query: GET $API_BASE/api/tasks?parentTaskId=<master> for current state.
5. Read Lens autonomy-audit at $MEMORY/05-learnings/v3-atlas-autonomy-audit-2026-04-28.md.
6. Aggregate per-slice status into S8 final terminal format.
7. Operator-review prompt for Slice G live-task validation (NO autonomous
   live mutations were done; G has mock-only acceptance).
8. Final Discord report (S8 format, see SLICE DETAILS).
9. Update MEMORY.md with sprint outcome + Atlas-autonomy-test verdict.
10. Mark master task done|partial via PATCH.
11. Save final cursor.
12. Exit.

============================================================
SLICE DETAILS (kompakt — workers read this for their slice)
============================================================

F1 status-derivation (forge / sre-expert, ~3h):
  Files: NEW
    src/lib/v3/types.ts                  // 12 V3CanonicalStatus, V3Lane, V3Task, ControlBarState, Health
    src/lib/v3/status-derivation.ts      // toV3Status(task, now): one of 12 statuses
    src/lib/v3/lane-mapping.ts           // toV3Lane(status): one of 7 lanes
    src/lib/v3/task-adapter.ts
    src/lib/v3/health-aggregation.ts     // computeHealth + computeIncidentTasks
  Touched: ADD @deprecated JSDoc to
    src/lib/task-board-lane.ts
    src/lib/projections/task-lane.ts
  Tests: jest spec for toV3Status() with:
    - 6 sample tasks from $DESIGN/screenshots/task-sample.json
    - Live snapshot data via curl $API_BASE/api/board/snapshot
    - 100% branch coverage
    - Parity assertion: computeIncidentTasks(tasks).length === computeHealth(tasks).incidentCount
    - Historical-failed-artifact exclusion: assertEquals(activeFailedCount, /api/health.failed)
  Verify: npm run lint + npm run build (no UI change → no restart)

A0 visual primitives (pixel / frontend-guru, ~1.5h, parallel to F1):
  Files: NEW
    src/components/v3/StatusBadge.tsx    // accepts status: string + tone: ToneKey props
    src/components/v3/PriorityBadge.tsx
    src/components/v3/ReceiptStage.tsx
    src/components/v3/AgeTag.tsx
    src/components/v3/MeaningRail.tsx
  Source: $SOURCE/mc-v3-foundations.jsx (V3_TONE, atom components)
  Style: use existing src/app/globals.css tokens; merge mc-tokens.css variables
  Constraint: NO import from src/lib/v3/types.ts yet (F1 may not be done).
    Atoms accept raw string props. Type-safety comes in A1.

A1 typed integration (pixel / frontend-guru, ~0.5h, after A0+F1):
  Files: TOUCH src/components/v3/*.tsx (the 5 atoms from A0)
  Change: replace string props with V3CanonicalStatus / V3PriorityKey from
    src/lib/v3/types.ts
  Tests: TS compile passes; visual render unchanged.

B TaskCard (pixel / frontend-guru, ~2h):
  Files: NEW src/components/v3/V3Card.tsx
  Source: $SOURCE/mc-v3-foundations.jsx (V3Card function)
  Inputs: V3Task from src/lib/v3/types.ts
  Behavior: click → onOpen(taskId) callback (no routing yet — F provides)

C lane-states (pixel / frontend-guru, ~1h):
  Files: NEW
    src/components/v3/V3LaneHeader.tsx
    src/components/v3/V3EmptyLane.tsx
    src/components/v3/V3LoadingLane.tsx
    src/components/v3/V3ErrorLane.tsx
  Source: $SOURCE/mc-v3-foundations.jsx + mc-v3-canvas.jsx StateLane

D TaskboardShell (pixel / frontend-guru, ~3h):
  Files: NEW
    src/app/kanban-v3-preview/page.tsx
    src/app/kanban-v3-preview/layout.tsx
    src/components/v3/V3FinalDesktop.tsx
    src/components/v3/V3FinalSidebar.tsx
    src/components/v3/V3FinalTopChrome.tsx
    src/components/v3/V3FinalSubBar.tsx
    src/components/v3/V3FinalClosedFooter.tsx
  Source: $SOURCE/mc-v3-final.jsx (V3FinalDesktop and children)
  Data: read from /api/board/snapshot via existing read-only hook. Use
    `summary.laneCounts` for lane numbers, `tasks` array for cards.
  Verify: $PREVIEW_ROUTE renders, /kanban and /taskboard unchanged.

F2 health-aggregation (forge / sre-expert, ~2h):
  Files: NEW src/app/api/board/v3-health/route.ts
  Function: aggregates active/review/stale/failed counts using toV3Status() per
    task. Returns Health = {active, review, stale, failed, incidentCount,
    hasIncident}.
  Acceptance: parity tests
    - computeIncidentTasks(tasks).length === Health.incidentCount
    - active V3 failed count === /api/health.failed (currently 0)
    - active V3 stale count  === /api/health.staleOpenTasks (currently 0)
    - HISTORICAL failed (e.g. /api/tasks statusCounts.failed=50) NOT in V3 failed

E IncidentStrip (pixel / frontend-guru, ~1h):
  Files: NEW src/components/v3/V3IncidentStrip.tsx
  Source: $SOURCE/mc-v3-final.jsx (V3FinalIncidentStrip)
  Data: useV3Health() — only renders if health.hasIncident && mode==="board"
  Filter (CRITICAL): MUST include failed + blocked + noheartbeat + stale.
  Acceptance: computeIncidentTasks(tasks).length === health.incidentCount.

F3 atlas-suggest (forge / sre-expert, ~2h):
  Files: TOUCH src/app/api/board/next-action/route.ts (extend response)
  Add fields: { suggestionText, suggestionTaskId, suggestionTone, suggestionOwner }
  Source-derive from current open tasks (highest-priority failed/blocked first).
  No hardcoded suggestion strings.

F DetailsDrawer (pixel / frontend-guru, ~4h):
  Files: NEW
    src/app/kanban-v3-preview/[id]/page.tsx
    src/components/v3/V3Drawer.tsx
    src/components/v3/V3DrawerContent.tsx
    9 section components: V3SecTruth, V3SecLifecycle, V3SecReceipts,
      V3SecSession, V3SecAcceptance, V3SecEvents, V3SecRelations, V3SecResult,
      V3SecRaw
  Source: $SOURCE/mc-v3-drawer.jsx (V3DrawerContent and 9 sections in order)
  Routing: /kanban-v3-preview/[id] — Next.js parallel route or modal route
  Data: GET /api/tasks/[id] (existing) + receipts/events from existing endpoints

G state-actions (pixel + forge / frontend-guru + sre-expert, ~3h):
  Files: NEW src/components/v3/V3ActionBar.tsx
  Build:
    - Confirm-Dialog UI scaffolding for dispatch / cancel / retry / approve /
      reassign — every action requires UI-confirmation before firing
    - Gated wrappers per MC-T11 (MCP wrappers) — wire to canonical APIs
    - Visually render the action buttons inline in card actions and drawer
    - Unit-tests for confirm-dialog flow + gate logic
  **AUTONOMOUS-NIGHT CONSTRAINT (Phase 3):**
    - Build full implementation
    - Run unit-tests + integration-tests against MOCK DATA only
    - NO live task API mutations during Phase 3 (no real dispatch/cancel/retry
      against real tasks)
    - Acceptance for autonomous run: code committed, tests pass, mock-flow OK
    - Live-task validation deferred to Phase 4 morning operator review
  Receipt: every fired action MUST write a receipt entry per existing MC-T11
    contract. (Will fire only against mocks during Phase 3.)

H mobile (pixel / frontend-guru, ~3h):
  Files: NEW src/components/v3/V3MobileFinal.tsx
  Source: $SOURCE/mc-v3-final.jsx (V3MobileFinal)
  Behavior: vertical stack, sticky header with truth row, BottomTabBar reuse,
    drawer becomes bottom sheet on md:hidden
  ControlBar (compact mode): MUST hide Truth-rail toggle entirely.
  Acceptance: on 390px viewport, V3ControlBar renders only 2 controls
    (Density + Mode). No truthRail switch visible.

I ControlBar (pixel / frontend-guru, ~2h):
  Files: NEW
    src/components/v3/V3ControlBar.tsx
    src/components/v3/V3Seg.tsx
    src/components/v3/V3Toggle.tsx
    src/lib/v3/use-control-bar-state.ts
  Source: $SOURCE/mc-v3-final.jsx (V3ControlBar, V3Seg, V3Toggle)
  Implementation requirements (real impl, not just spec):
    1. localStorage["mc.taskboard.controlBar"] persistence — load on mount,
       save on change. Test: state survives reload.
    2. URL-sync via useSearchParams — read on mount, write on change.
       Test: ?density=dense&mode=triage&rail=on hydrates correctly.
    3. Keyboard: D toggles Density, M toggles Mode, T toggles Truth-rail,
       only when board has focus.
    4. Compact mode (mobile): hide Truth-rail toggle; ignore truthRail in
       persisted state when compact=true.
    5. Tailwind: shell gets data-density="comfy|dense" attribute.

V0 atlas-autonomy-audit (lens / efficiency-auditor, parallel throughout):
  Files: NEW $MEMORY/05-learnings/v3-atlas-autonomy-audit-2026-04-28.md
  Audit dimensions:
    - Atlas decision log per cycle (timestamps, dispatches made, WIP-state)
    - Dispatch latency per slice: dispatchedAt → acceptedAt diff
    - WIP-respect tracking: any cycle exceed 2 global / 1-per-agent? log violations
    - Defense-cron firing log (session-health, r49-validator, stale-lock-cleaner)
    - Receipt completion rate per slice (accepted → progress → result conversion)
    - Discord-report cadence: hourly heartbeats present?
    - Operator-escalation triggers (Hard Rule #8 hits)
  Update method: Lens auto-pickup runs every ~30min, appends incremental
    observations to audit file. Final summary at sprint close.
  Output: structured md with sections: timeline, dispatch-log, wip-violations,
    defense-cron-fires, autonomy-quality-score (1-10), recommendations.

V1 A/B validation (lens / efficiency-auditor, ~1h, after E + I):
  Compares counts between /kanban and $PREVIEW_ROUTE for same dataset.
  Acceptance: lane and status counts identical ±1.
  Output: $MEMORY/05-learnings/v3-parity-report-2026-04-28.md

V2 UX review (spark / spark, ~1h, after I):
  Reviews ControlBar 3-knob UX. Max 3 polish suggestions. No code changes.
  Output: $MEMORY/06-dreaming/v3-controlbar-uxreview-2026-04-28.md

V3 memory doc (james / james, parallel, ~1h):
  Files: NEW
    $MEMORY/01-agents/pixel/V3-CONTRACTS.md (component contract index)
    $MEMORY/05-learnings/v3-implementation-log-2026-04-28.md
  Updates CONTRACTS-INDEX.md entry.

S8 summary (atlas / main, ~30min Phase 4):
  Status per slice. Changed files. Created tasks. Discord message-ids.
  Open risks. Atlas-autonomy-test verdict (read from V0 audit).
  Next single action.

Final terminal format (Phase 4 by Codex):
SPRINT_STATUS:        PASS | PARTIAL | BLOCKED | FAIL
P0_BASELINE:          PASS | PARTIAL | BLOCKED | FAIL
F1_STATUS_DERIVATION: PASS | PARTIAL | BLOCKED | FAIL
A0_VISUAL_PRIMITIVES: PASS | PARTIAL | BLOCKED | FAIL
A1_TYPED_INTEGRATION: PASS | PARTIAL | BLOCKED | FAIL
B_TASKCARD:           PASS | PARTIAL | BLOCKED | FAIL
C_LANE_STATES:        PASS | PARTIAL | BLOCKED | FAIL
D_SHELL:              PASS | PARTIAL | BLOCKED | FAIL
F2_HEALTH_API:        PASS | PARTIAL | BLOCKED | FAIL
E_INCIDENT_STRIP:     PASS | PARTIAL | BLOCKED | FAIL
F3_ATLAS_SUGGEST:     PASS | PARTIAL | BLOCKED | FAIL
F_DRAWER:             PASS | PARTIAL | BLOCKED | FAIL
G_STATE_ACTIONS:      PASS | PARTIAL | BLOCKED | FAIL  (mock-only Phase 3)
H_MOBILE:             PASS | PARTIAL | BLOCKED | FAIL
I_CONTROLBAR:         PASS | PARTIAL | BLOCKED | FAIL
V0_AUTONOMY_AUDIT:    PASS | PARTIAL | BLOCKED | FAIL  (autonomy-quality-score N/10)
V1_PARITY:            PASS | PARTIAL | BLOCKED | FAIL
V2_UX_REVIEW:         PASS | PARTIAL | BLOCKED | FAIL
V3_DOCS:              PASS | PARTIAL | BLOCKED | FAIL

Atlas-Autonomy-Test verdict: GREEN | YELLOW | RED
Changed files: ...
Created tasks: <master + 17 slices>
Discord reports: ...
Open risks: ...
Operator-action-items (morning):
- Slice G live-task validation (manual UI walk-through)
- Review V0 audit findings
- ...
Next single action: ...

============================================================
START
============================================================

1. cd $WORKDIR
2. set -euo pipefail
3. test -f $HALT_FILE && exit 0
4. Read $SPEC_FILE.
5. Read $CURSOR. If phase=2-handover-complete: jump to PHASE 4 (morning resume).
   Otherwise start at PHASE 0.
6. Execute Phase 0 → Phase 1 → Phase 2 → exit (initial trigger).
   OR Execute Phase 4 (morning resume).
7. Phase 3 runs autonomously by Atlas + Workers between Phase 2 and Phase 4 —
   NO Codex involvement.
