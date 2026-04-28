---
title: V3 Taskboard Implementation Sprint — Codex Dispatch Prompt
date: 2026-04-28
status: ready-for-dispatch
scope: codex-multi-agent-orchestration
target: Codex CLI on homeserver
agents: atlas, forge, pixel, lens, spark, james
source: claude-design-v3-2026-04-28 (polish pass)
related:
  - v3-status-derivation-spec.md
  - source-export-final-2026-04-28-2213/
---

# V3 Taskboard Implementation Sprint — Codex Dispatch Prompt

To be dispatched via Codex CLI. Orchestrated by Atlas. Owners assigned per slice
(Pixel/Forge/Lens/Spark/James). Read-only baseline first. WIP-respected.

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
HALT_FILE=~/.openclaw/HALT
SNAPSHOT_DIR=~/.openclaw/snapshots
ROLLBACK_SCRIPT=~/.openclaw/scripts/codex-rollback.sh
DISCORD_CHANNEL=1495737862522405088
API_BASE=http://127.0.0.1:3000
PREVIEW_ROUTE=/kanban-v3-preview

# === GOAL ===
Implement Claude Design V3 Final Taskboard as feature-flag-isolated preview at
$PREVIEW_ROUTE without touching live /kanban or /taskboard routes. Atlas
orchestrates 9 UI slices (A-I) plus 3 Forge sub-slices (F1-F3) and 3 supporting
work packages (V1 Lens, V2 Spark, V3 James).

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
4. WIP-Limit: max 2 global, max 1 per agent. Fresh board snapshot before mutation.
5. Atlas: exactly 1 decision per autonomy cycle.
6. No fanout, no zombies, no in-progress without accepted/started/result receipt.
7. Each worker execution requires receipt-evidence.
8. Operator-Approval REQUIRED for:
   sudo/root, systemctl --user enable/edit/link, new .service/.timer files,
   npm install/postinstall, secrets/auth, model-switch, destructive mutations,
   cron/timer/heartbeat/always-on, direct state-file writes,
   Discord-channel-switch, T3/T4, WIP-exceptions, writes under
   /home/piet/vault/00-control/.
9. Code changes:
   - Backup/snapshot first
   - npm run build
   - systemctl --user restart mission-control
   - systemctl --user status mission-control --no-pager
   - curl-verify
   - Build-fail = STOP + report, no auto-rollback without approval
10. Persona-Tags = owner-fields, NOT role-switch:
    atlas, forge, pixel, lens, james, spark.
11. NEW v3 files only in src/lib/v3/, src/components/v3/,
    src/app/kanban-v3-preview/, src/app/api/board/v3-health/.
12. Existing files: ONLY @deprecated JSDoc comments allowed, NO logic changes.
13. /kanban and /taskboard routes UNTOUCHED.

# === KILL-SWITCH (always active, check before every gate) ===
A) test -f $HALT_FILE → close current gate cleanly, save cursor, Discord
   "HALTED at S{n}.G{m}", exit 0.
B) Operator posts "!codex halt" in channel → like (A) at next poll (60s).
C) 3 consecutive API-5xx OR 1× 423-Locked → auto-HALT.
D) S3+ blocks if $CURSOR not writable.
E) Missing $ROLLBACK_SCRIPT does not block analysis but blocks risky writes.

# === RATE LIMITS ===
- Discord: max 10 msgs/min, 60s dedupe via SHA256(content), 3× 429 in 5min → STOP.
- Self-Healing: max 3 auto-tasks/h global, max 1/h per signature.
- Repair-Loop: 2 fail-cycles per signature → escalate, no 3rd attempt.

# === REPORTING ===
After every gate:
1. JSONL append to $GATES_LOG.
2. Plain-text Discord message to $DISCORD_CHANNEL.
3. NO embeds[], NO attachments, NO title-based task-embed.

Format:
[OPENCLAW V3 TASKBOARD SPRINT]
Gate: <id/name>
Status: PASS | PARTIAL | BLOCKED | FAIL
Owner: <owner_tags>

Kurzbefund:
- ...

Evidence:
- ...

Changed:
- ...

Next:
- exactly one next action

# === IDEMPOTENZ ===
- Each mutation gets UUIDv4 idempotency-key, persisted to $CURSOR.
- Restart: read cursor, skip completed gates, verify current via API-GET.
- File-writes via write-if-changed (SHA256-compare).
- Memory-appends with flock $MEMORY/.lock + duplicateKey check.
- No re-write mutation if target == expected.

============================================================
SPRINT-MATRIX
============================================================

Dependency order:
P0 → (F1 + A) parallel → B → C → D → (F2 + E) parallel → (F3 + F) parallel
   → G → H → I → V (validation block) → S8 (summary)

| id  | name                       | owner       | depends      | acceptance (executable)                                                       |
|-----|----------------------------|-------------|--------------|-------------------------------------------------------------------------------|
| P0  | live-baseline + design-read| atlas       | -            | spec read; $SOURCE inventoried; /api/health=200; sprintplan written           |
| F1  | status-derivation          | forge       | P0           | toV3Status returns valid for 6 sample tasks; jest 100% branch-coverage         |
| A   | primitives                 | pixel       | F1           | StatusBadge, PriorityBadge, ReceiptStage, AgeTag, MeaningRail render          |
| B   | TaskCard                   | pixel       | A            | V3Card renders 6 sample tasks; click → onOpen(taskId) callback fires          |
| C   | lane-states                | pixel       | B            | EmptyLane, LoadingLane, ErrorLane render; LaneHeader counts correct           |
| D   | TaskboardShell             | pixel       | C            | $PREVIEW_ROUTE renders sidebar+sub-bar+5-lane-grid+footer; /kanban unchanged  |
| F2  | health-aggregation API     | forge       | F1           | useV3Health() returns Health object; parity with /api/board/snapshot          |
| E   | IncidentStrip              | pixel       | D, F2        | Strip renders only when health.hasIncident=true                               |
| F3  | atlas-suggest derive       | forge       | P0           | /api/board/next-action returns suggestion; drawer renders it                  |
| F   | DetailsDrawer              | pixel       | E, F3        | $PREVIEW_ROUTE/[id] opens drawer; 9 sections present in order                 |
| G   | state-actions safeguards   | forge+pixel | F            | Confirm dialogs for dispatch/cancel/retry/approve; MCP wrappers per MC-T11    |
| H   | mobile                     | pixel       | F            | $PREVIEW_ROUTE on 390px viewport: vertical stack, sticky header, sheet        |
| I   | ControlBar                 | pixel       | D            | Density+Mode+Truth-rail flip without reload; localStorage persist; URL-sync   |
| V1  | A/B validation             | lens        | E, I         | Parity report: counts match between /kanban and $PREVIEW_ROUTE                |
| V2  | UX review ControlBar       | spark       | I            | 3-knob UX-review report; max 3 polish suggestions                             |
| V3  | memory documentation       | james       | parallel     | $MEMORY/01-agents/pixel/V3-CONTRACTS.md + CONTRACTS-INDEX entry               |
| S8  | summary + roadmap          | atlas       | V1+V2+V3     | gates.jsonl complete; final discord report; next action defined               |

Blocking gates: P0 (read), F1 (status logic), V1 (parity).

============================================================
PHASE 0 — DESIGN-READ + LIVE-BASELINE (read-only)
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
7. Verify:
   - test -w ~/.openclaw/state
   - curl -sS $API_BASE/api/health
   - curl -sS -o /dev/null -w "%{http_code}\n" $API_BASE/alerts
   - curl -sS -o /dev/null -w "%{http_code}\n" $API_BASE/dashboard
   - curl -sS $API_BASE/api/board/snapshot | jq '.openCount, .consistencyIssues'
8. Capture: date -Iseconds, hostname, git -C $WORKDIR status --short, systemctl
   status, /api/health body, /api/board/snapshot, /api/tasks?status=*.
9. Read existing context:
   - $MEMORY/MEMORY.md (if exists)
   - $MEMORY/feedback_system_rules.md (if exists)
   - $WORKDIR/src/lib/taskboard-types.ts
   - $WORKDIR/src/lib/task-runtime-truth.ts
   - $WORKDIR/src/lib/projections/task-lane.ts
10. Write idempotent sprintplan to $SPRINT_FILE.
11. report "P0" PASS|PARTIAL|BLOCKED|FAIL ... atlas
12. WAIT: F1 + A start automatically if P0=PASS AND $HALT_FILE missing.
    Otherwise wait for operator ("!codex proceed f1+a").

============================================================
SPRINT LOOP
============================================================

For each gate in dependency order:
  a. test -f $HALT_FILE → kill-switch.
  b. Read acceptance from matrix above.
  c. Execute slice (see slice-details below).
     - max 1 decision per autonomy cycle (Atlas)
     - WIP-respected (GET before, GET after)
     - each mutation: idempotency-key in $CURSOR
     - npm run build + restart only if Slice changes runtime code
  d. eval acceptance; status = PASS | PARTIAL | BLOCKED | FAIL
  e. report <id> <status> <brief> <evidence-paths> <changed-files> <next> <owner>
  f. STOP if status==FAIL AND id ∈ {P0, F1, V1} (blocking gates).
  g. Update $CURSOR.

============================================================
SLICE DETAILS (kompakt)
============================================================

F1 status-derivation (forge, ~3h):
  Files: NEW
    src/lib/v3/types.ts
    src/lib/v3/status-derivation.ts
    src/lib/v3/lane-mapping.ts
    src/lib/v3/task-adapter.ts
    src/lib/v3/health-aggregation.ts
  Touched: ADD @deprecated JSDoc to
    src/lib/task-board-lane.ts
    src/lib/projections/task-lane.ts
  Tests: jest spec for toV3Status() with 6 sample tasks from
    $DESIGN/screenshots/task-sample.json
  Verify: npm run lint + npm run build (no UI change → no restart)

A primitives (pixel, ~2h):
  Files: NEW
    src/components/v3/StatusBadge.tsx
    src/components/v3/PriorityBadge.tsx
    src/components/v3/ReceiptStage.tsx
    src/components/v3/AgeTag.tsx
    src/components/v3/MeaningRail.tsx
  Source: $SOURCE/mc-v3-foundations.jsx (V3_TONE, V3_STATUS, atom components)
  Style: use existing src/app/globals.css tokens; merge mc-tokens.css variables
    (--text-soft, --text-dim, --font-mono if missing)

B TaskCard (pixel, ~2h):
  Files: NEW src/components/v3/V3Card.tsx
  Source: $SOURCE/mc-v3-foundations.jsx (V3Card function)
  Inputs: V3Task from src/lib/v3/types.ts
  Behavior: click → onOpen(taskId) callback (no routing yet — F provides)

C lane-states (pixel, ~1h):
  Files: NEW
    src/components/v3/V3LaneHeader.tsx
    src/components/v3/V3EmptyLane.tsx
    src/components/v3/V3LoadingLane.tsx
    src/components/v3/V3ErrorLane.tsx
  Source: $SOURCE/mc-v3-foundations.jsx + mc-v3-canvas.jsx StateLane

D TaskboardShell (pixel, ~3h):
  Files: NEW
    src/app/kanban-v3-preview/page.tsx
    src/app/kanban-v3-preview/layout.tsx
    src/components/v3/V3FinalDesktop.tsx
    src/components/v3/V3FinalSidebar.tsx
    src/components/v3/V3FinalTopChrome.tsx
    src/components/v3/V3FinalSubBar.tsx
    src/components/v3/V3FinalClosedFooter.tsx
  Source: $SOURCE/mc-v3-final.jsx (V3FinalDesktop and children)
  Data: read from /api/board/snapshot via existing read-only hook
  Verify: $PREVIEW_ROUTE renders, /kanban and /taskboard unchanged

F2 health-aggregation (forge, ~2h):
  Files: NEW src/app/api/board/v3-health/route.ts
  Function: aggregates active/review/stale/failed counts from same source as
    /api/board/snapshot. Returns Health = {active, review, stale, failed,
    incidentCount, hasIncident}.
  Acceptance: parity test — sum of all V3-status-derivation classifications
    must equal /api/board/snapshot openCount±1.

E IncidentStrip (pixel, ~1h):
  Files: NEW src/components/v3/V3IncidentStrip.tsx
  Source: $SOURCE/mc-v3-final.jsx (V3FinalIncidentStrip)
  Data: useV3Health() — only renders if health.hasIncident && mode==="board"

F3 atlas-suggest (forge, ~2h):
  Files: TOUCH src/app/api/board/next-action/route.ts (extend response)
  Add fields to existing response: { suggestionText, suggestionTaskId,
    suggestionTone, suggestionOwner }
  Source-derive from current open tasks (highest-priority failed/blocked first).
  No hardcoded suggestion strings.

F DetailsDrawer (pixel, ~4h):
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

G state-actions (forge+pixel, ~3h):
  Files: NEW src/components/v3/V3ActionBar.tsx
  Behavior: Confirm-dialog wrapping for dispatch/cancel/retry/approve/reassign
  Backend: Must use existing MCP wrappers (MC-T11). No new state mutations.
  Operator-Approval-Class: gated-mutation, requires confirmation modal.

H mobile (pixel, ~3h):
  Files: NEW src/components/v3/V3MobileFinal.tsx
  Source: $SOURCE/mc-v3-final.jsx (V3MobileFinal)
  Behavior: vertical stack, sticky header with truth row, BottomTabBar reuse,
    drawer becomes bottom sheet on md:hidden

I ControlBar (pixel, ~2h):
  Files: NEW
    src/components/v3/V3ControlBar.tsx
    src/components/v3/V3Seg.tsx
    src/components/v3/V3Toggle.tsx
    src/lib/v3/use-control-bar-state.ts (localStorage + URL sync)
  Source: $SOURCE/mc-v3-final.jsx (V3ControlBar, V3Seg, V3Toggle)
  Persistence: localStorage["mc.taskboard.controlBar"]
  URL-sync: useSearchParams for ?density=&mode=&rail=
  Keyboard: D/M/T when board focused
  Tailwind: data-density="comfy|dense" attribute on shell

V1 A/B validation (lens, ~1h):
  Compares counts between /kanban and $PREVIEW_ROUTE for same dataset.
  Acceptance: counts identical ±1 (off-by-one tolerance for race conditions).
  Output: $MEMORY/05-learnings/v3-parity-report-2026-04-28.md

V2 UX review (spark, ~1h):
  Reviews ControlBar 3-knob UX. Max 3 polish suggestions. No code changes.
  Output: $MEMORY/06-dreaming/v3-controlbar-uxreview-2026-04-28.md

V3 memory doc (james, ~1h):
  Files: NEW
    $MEMORY/01-agents/pixel/V3-CONTRACTS.md (component contract index)
    $MEMORY/05-learnings/v3-implementation-log-2026-04-28.md
  Updates CONTRACTS-INDEX.md entry.

S8 summary (atlas):
  Status per slice. Changed files. Created tasks (zero expected). Discord
  message-ids. Open risks. Next single action.

Final terminal format:
SPRINT_STATUS:        PASS | PARTIAL | BLOCKED | FAIL
P0_BASELINE:          PASS | PARTIAL | BLOCKED | FAIL
F1_STATUS_DERIVATION: PASS | PARTIAL | BLOCKED | FAIL
A_PRIMITIVES:         PASS | PARTIAL | BLOCKED | FAIL
B_TASKCARD:           PASS | PARTIAL | BLOCKED | FAIL
C_LANE_STATES:        PASS | PARTIAL | BLOCKED | FAIL
D_SHELL:              PASS | PARTIAL | BLOCKED | FAIL
F2_HEALTH_API:        PASS | PARTIAL | BLOCKED | FAIL
E_INCIDENT_STRIP:     PASS | PARTIAL | BLOCKED | FAIL
F3_ATLAS_SUGGEST:     PASS | PARTIAL | BLOCKED | FAIL
F_DRAWER:             PASS | PARTIAL | BLOCKED | FAIL
G_STATE_ACTIONS:      PASS | PARTIAL | BLOCKED | FAIL
H_MOBILE:             PASS | PARTIAL | BLOCKED | FAIL
I_CONTROLBAR:         PASS | PARTIAL | BLOCKED | FAIL
V1_PARITY:            PASS | PARTIAL | BLOCKED | FAIL
V2_UX_REVIEW:         PASS | PARTIAL | BLOCKED | FAIL
V3_DOCS:              PASS | PARTIAL | BLOCKED | FAIL

Changed files: ...
Created tasks: ...
Discord reports: ...
Open risks: ...
Next single action: ...

============================================================
START
============================================================

1. cd $WORKDIR
2. set -euo pipefail
3. test -f $HALT_FILE && exit 0
4. Read $SPEC_FILE and confirm it has been received in the cursor.
5. Run Phase 0 preflight + design-read.
6. Load $CURSOR; if last_status=PASS, resume at next gate.
7. Otherwise start at P0.
8. After P0=PASS, dispatch F1 (Forge) and A (Pixel) IN PARALLEL — they have no
   cross-dependency. WIP-Limit: 2 active = OK with these two.
