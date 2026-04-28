---
title: V3 Taskboard — Status-Derivation Specification
date: 2026-04-28
status: ready-for-implementation
scope: forge-pixel-implementation-contract
source: claude-design-v3-2026-04-28 (polish pass)
related:
  - mc-taskboard-ui-simplification-sprint.md
  - mc-taskboard-v3-implementation-handoff.md
  - source-export-final-2026-04-28-2213/mc-v3-foundations.jsx
  - source-export-final-2026-04-28-2213/mc-v3-final.jsx
---

> ## ⚡ UPDATED AFTER CODEX LIVE CHECK — 2026-04-28T22:35Z
>
> - **verifiedAt:** 2026-04-28T22:35Z
> - **/api/health:** ok (status=ok, severity=ok, board.openCount=0, inProgress=0, review=0, blocked=0, failed=0, staleOpenTasks=0)
> - **/api/board/snapshot:** 200, schema confirmed — top-level fields are `generatedAt`, `view`, `tasks`, `summary` (NOT `openCount`/`consistencyIssues`). Live values: returnedTasks=2, laneCounts.waiting=2, laneCounts.archive=703, statusCounts.done=589, statusCounts.canceled=64, statusCounts.failed=50, statusCounts.draft=2.
> - **/api/tasks:** 705 tasks total — do NOT poll for UI; prefer snapshot/health.
> - **source-export-final hash:** identical to local v2 export (Codex App verified)
> - **mission-control worktree:** dirty, including UI files (dashboard/page.tsx, overview-dashboard.tsx). V3 sprint MUST stay additive; no edits to dirty existing files.
> - **changed decisions vs prior version:**
>   - 11 → **12** canonical statuses (accepted stays separate; not merged into active)
>   - **historical failed artifacts** (`statusCounts.failed=50` from /api/tasks) MUST NOT count as V3 active incidents — derivation explicitly filters via `isHistoricalFailedArtifact()`
>   - Triage incident filter must include stale (was: failed+blocked+noheartbeat only)
>   - ControlBar persistence/URL-sync/keyboard moved from spec to **implementation requirement** with tests
>   - Mobile ControlBar must hide Truth-rail toggle entirely (not just default-off)
> - **remaining blockers:** none for P0 — sprint can start

# V3 Taskboard Status-Derivation Specification

## Purpose

Maps Claude Design V3's **12 canonical statuses** and 7 lanes onto Mission Control's
existing field schema (`status`, `executionState`, `dispatchState`, `receiptStage`,
timestamps). NO new server fields required. This spec is the contract between
Forge (server-side derivation) and Pixel (UI consumption).

## Architecture Decisions (resolved 2026-04-28)

### Decision 1 — Draft Visibility = SHOW

V3Final shows drafts as a first-class lane (`primary = ["draft", "ready", "assigned",
"active", "review"]`). Existing `projections/task-lane.ts:30` hides drafts.

**Resolution:** V3 follows V3-Design spec — drafts visible.

**Why:** Sprint-S2 Reporting-Contract treats drafts as visible operator state. Hiding
drafts re-creates the trust gap that motivated V3 ("Dashboard zero while Taskboard
has work"). Live snapshot confirms `statusCounts.draft=2` exists today.

**Apply:** New V3-derivation does not filter drafts. Legacy `/kanban` keeps existing
behavior (no regression for live route).

### Decision 2 — assigned/queued/dispatched = UI-only mapping

V3 has 3 separate statuses (queued / dispatched / assigned). Existing schema has
`status='assigned'` + `status='pending-pickup'` plus `dispatchState` substructure.

**Resolution:** UI-only mapping. NO server-state split. NO new state machine.

**Why:** Splitting touches state-machine logic, risks double-classification. The
information already exists in `dispatchState` and `dispatchedAt`.

**Apply:** Pure derivation function in `src/lib/v3/status-derivation.ts` (table below).

### Decision 3 — Lane Functions = New + Deprecate

Two competing lane functions exist: `task-board-lane.ts` (6 lanes) and
`projections/task-lane.ts` (8 lanes).

**Resolution:** New `src/lib/v3/lane-mapping.ts` introduces single canonical V3 lane
function. Both legacy functions get JSDoc `@deprecated` markers but stay wired to
existing routes.

**Why:** Polish-Pass ControlBar contract states "Mode=triage does not filter the
dataset; it re-arranges". Means: ONE lane function returns all lanes; UI rearranges
via mode-state. Forced consolidation now would touch live `/kanban` and `/taskboard`
— blocks active workers. 4-week soak window for migration.

**Apply:**
- Week 0: V3 file new, both old `@deprecated`
- Week 0–4: V3-preview uses new, legacy routes use old
- Week 4: Audit consumers, migrate, delete unused
- Week 5: Single canonical function

## Status-Derivation Mapping (the contract — 12 canonical)

| V3 Status     | V3 Lane                | Derivation from existing fields                                                                                  |
|---------------|------------------------|------------------------------------------------------------------------------------------------------------------|
| `draft`       | draft                  | `status === 'draft'`                                                                                             |
| `queued`      | ready                  | `status === 'assigned' AND dispatchState IN ('draft','queued')`                                                  |
| `dispatched`  | ready                  | `status === 'pending-pickup' AND dispatchState === 'dispatched' AND age(dispatchedAt) <= 15min`                  |
| `assigned`    | ready                  | `status === 'assigned' AND dispatchState === 'dispatched'`                                                       |
| `accepted`    | active                 | `status === 'pending-pickup' AND receiptStage === 'accepted'`                                                    |
| `active`      | active                 | `status === 'in-progress' AND getTaskRuntimeTruth() === 'active-live'`                                           |
| `noheartbeat` | active (striped rail)  | `status === 'in-progress' AND getTaskRuntimeTruth() === 'waiting-stale' AND hasAcceptedExecutionProof()`         |
| `stale`       | active (stale tag)     | `status === 'pending-pickup' AND age(dispatchedAt) > 15min`                                                      |
| `blocked`     | failed                 | `status === 'blocked' OR blockerReason OR blockedReason OR receiptStage === 'blocked'`                           |
| `failed`      | failed                 | `status === 'failed' AND NOT isHistoricalFailedArtifact(task)`                                                   |
| `review`      | review                 | `status === 'review'`                                                                                            |
| `done`        | done                   | `status IN ('done', 'canceled')`                                                                                 |

**Total: 12 statuses across 7 lanes** (`draft`, `ready`, `active`, `review`, `failed`, `done`, plus internal lane subdivision via status).

**Evaluation order:** Top-to-bottom. First match wins.

**Server-derivation invariant:** UI never invents status. `noheartbeat` is computed
server-side from `lastActivityAt` + 30min threshold. UI just renders.

## Health vs Snapshot Semantics (Codex Live-Check)

**Two truth sources, separated concerns:**

| Endpoint | What it tells you | When to use |
|---|---|---|
| `/api/health` | **Operative truth** — active incident state. Excludes archived/historical artifacts. `failed=0` here means zero ACTIVE failed work, even if `/api/tasks` has `statusCounts.failed=50` from history. | Top chrome health beats, IncidentStrip visibility, alerts |
| `/api/board/snapshot` | Board snapshot with full lane and status counts. Schema: `{ generatedAt, view, tasks, summary }` where `summary = { totalTasks, returnedTasks, laneCounts, statusCounts }`. | V3 lane rendering, A/B parity validation |
| `/api/tasks` | Full task inventory (705 tasks today). Includes archived. **Do NOT poll for UI.** | Backups, audits, one-off queries only |

**Invariant for V3 incident counting:** active V3 failed/incidents MUST exclude tasks
where `isHistoricalFailedArtifact(task) === true`. Live data shows
`statusCounts.failed=50` but `/api/health.failed=0` — the 50 are historical
artifacts. V3 derivation MUST follow `/api/health` semantics, not raw `statusCounts`.

## Triage Incident Filter (Codex correction)

V3 incident set MUST be: `failed + blocked + noheartbeat + stale` (4 statuses).

```ts
function computeIncidentTasks(tasks: V3Task[]): V3Task[] {
  return tasks.filter(t =>
    t.status === 'failed'      ||
    t.status === 'blocked'     ||
    t.status === 'noheartbeat' ||
    t.status === 'stale'
  );
}

// Invariant:
// computeIncidentTasks(tasks).length === computeHealth(tasks).incidentCount
```

The Polish source `mc-v3-final.jsx::V3FinalTriage` filter omits `stale` — that's a
source bug. V3 implementation must include all 4. `useV3Health()` already
aggregates `stale` and `noheartbeat` together as `health.stale`, and
`incidentCount = failed + stale`. Triage list MUST agree.

## Existing Reference Fields

From `src/lib/taskboard-types.ts`:

```ts
TASK_STATUSES = ['draft', 'assigned', 'pending-pickup', 'in-progress', 'blocked',
                 'review', 'done', 'failed', 'canceled']

ExecutionState = 'queued' | 'active' | 'started' | 'stalled' | 'stalled-warning' |
                 'review' | 'done' | 'blocked' | 'failed'

DispatchState = 'draft' | 'queued' | 'dispatched' | 'completed'

WorkerReceiptStage = 'accepted' | 'started' | 'progress' | 'result' | 'blocked' |
                     'failed' | 'no-receipt'
```

Existing helpers (reuse, do not modify):
- `getTaskRuntimeTruth(task, now)` from `src/lib/task-runtime-truth.ts`
- `LIVE_RUNTIME_FRESHNESS_MS = 30 * 60 * 1000`
- `hasAcceptedExecutionProof(task)`
- `isHistoricalFailedArtifact(task)` from `src/lib/historical-failure-artifacts.ts`

## New Files (additive, no mutation of legacy code)

```
src/lib/v3/
  ├── types.ts                  // V3CanonicalStatus, V3Lane, V3Task, ControlBarState, Health
  ├── status-derivation.ts      // toV3Status(task, now): V3CanonicalStatus
  ├── lane-mapping.ts           // toV3Lane(status): V3Lane
  ├── task-adapter.ts           // toV3Task(task): V3Task (composes above)
  ├── health-aggregation.ts     // computeHealth(tasks): Health, computeIncidentTasks(tasks)
  └── use-control-bar-state.ts  // localStorage + URL sync hook for ControlBar (NEW: real impl, with tests)
```

## Touched Files (JSDoc-only, NO logic change)

Add `@deprecated since v3 2026-04-28, prefer src/lib/v3/lane-mapping.ts` to:
- `src/lib/task-board-lane.ts` (function + type exports)
- `src/lib/projections/task-lane.ts` (function + type exports)

## Files MUST NOT be touched (Codex live-check: dirty worktree)

The mission-control worktree currently has uncommitted changes including UI files.
V3 sprint stays additive — these existing files are OFF-LIMITS regardless of dirty
state:

- `src/app/dashboard/page.tsx`
- `src/components/overview-dashboard.tsx`
- `src/app/kanban/**` (entire route)
- `src/app/taskboard/**` (entire route)
- `src/components/taskboard/**` (existing components, no V3 modifications)
- Any file currently appearing in `git status --short`

Phase 0 of the implementation sprint MUST run `git -C $WORKDIR status --short`,
document the dirty file list to `$SPRINT_FILE`, and abort if any planned V3-slice
output path collides with a dirty existing file.

## Acceptance Criteria (Forge-side verifiable)

1. `toV3Status()` returns one of the 12 V3 statuses without ambiguity for the 6
   sample tasks in `screenshots/task-sample.json` AND for live tasks from
   `/api/board/snapshot`.
2. `toV3Status()` is pure: same `(task, now)` → same output.
3. Jest test: 100% branch coverage on derivation table, including all edge cases.
4. **Active V3 failed/incident counting MUST exclude historical failed artifacts.**
   Verified by parity test: V3 incident-count matches `/api/health.failed +
   /api/health.staleOpenTasks` (currently both 0), NOT `/api/tasks
   statusCounts.failed` (currently 50).
5. `computeIncidentTasks(tasks).length === computeHealth(tasks).incidentCount` —
   filter parity.
6. Health aggregation `computeHealth(tasks)` returns parity with `/api/health` for
   active state.
7. No mutation of `task-runtime-truth.ts`, `taskboard-types.ts`, or any
   non-`src/lib/v3/*` file.
8. No mutation of `/kanban`, `/taskboard`, or `/dashboard` routes.
9. No mutation of any file appearing in `git status --short` at sprint start.

## Edge Cases (must handle)

| Case                                                              | Existing Behavior            | V3 Mapping                                                |
|-------------------------------------------------------------------|------------------------------|-----------------------------------------------------------|
| `isHistoricalFailedArtifact(task) === true`                       | hidden (lane=archive)        | V3 Lane: `done` (archived). NOT `failed`. NOT in incidents. |
| `securityStatus === 'critical'` on `in-progress`                  | → incident lane              | V3 Status: `failed`. Lane: `failed`.                      |
| `status === 'canceled'`                                           | hidden default               | V3 Status: `done`. Lane: `done`.                          |
| `executionState === 'stalled-warning'`                            | currently unused             | V3 Status: `noheartbeat` (treat as pre-failure)           |
| `receiptStage === 'no-receipt' AND status === 'pending-pickup'`   | dispatched but no receipt    | V3 Status: `stale` if age > 15min, else `dispatched`      |
| `receiptStage === 'progress' AND lastActivityAt < 30min`          | active healthy               | V3 Status: `active`                                       |
| `receiptStage === 'progress' AND lastActivityAt > 30min`          | stalled                      | V3 Status: `noheartbeat`                                  |

## Open Backend Items (NOT covered by this spec)

These belong to separate Forge slices, not blocking V3-Foundation port:

1. **`/api/mc/stream` SSE endpoint** — Polish spec mentions it; existing system has
   `/api/board/events`. Decision: re-use existing or build new. Forge call.
2. **Atlas-Suggest server-side derivation** — Polish hardcoded the suggestion in V3
   sample. Production must compute from `/api/board/next-action` (already exists).
3. **Tailwind `data-density` plugin** — Polish describes the convention; Pixel
   implements the Tailwind config extension.
4. **URL-sync hook for ControlBar** — `useSearchParams()` for
   `?density=…&mode=…&rail=…`. Now scoped as Slice I implementation requirement
   with tests, not just spec.

## References

- Polish-Pass source: `source-export-final-2026-04-28-2213/`
- Original handoff: `mc-taskboard-v3-implementation-handoff.md`
- Sprint plan: `mc-taskboard-ui-simplification-sprint.md`
- Foundation atoms: `source-export-final-2026-04-28-2213/mc-v3-foundations.jsx`
- Final layout: `source-export-final-2026-04-28-2213/mc-v3-final.jsx`
- Drawer spec: `source-export-final-2026-04-28-2213/mc-v3-drawer.jsx`
