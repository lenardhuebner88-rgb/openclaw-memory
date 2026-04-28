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

# V3 Taskboard Status-Derivation Specification

## Purpose

Maps Claude Design V3's 11 canonical statuses and 7 lanes onto Mission Control's
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
has work").

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

## Status-Derivation Mapping (the contract)

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

**Evaluation order:** Top-to-bottom. First match wins.

**Server-derivation invariant:** UI never invents status. `noheartbeat` is computed
server-side from `lastActivityAt` + 30min threshold. UI just renders.

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
  ├── types.ts                 // V3CanonicalStatus, V3Lane, V3Task, ControlBarState
  ├── status-derivation.ts     // toV3Status(task, now): V3CanonicalStatus
  ├── lane-mapping.ts          // toV3Lane(status): V3Lane
  ├── task-adapter.ts          // toV3Task(task): V3Task (composes above)
  ├── health-aggregation.ts    // computeHealth(tasks): Health
  └── use-control-bar-state.ts // localStorage + URL sync hook for ControlBar
```

## Touched Files (JSDoc-only, NO logic change)

Add `@deprecated since v3 2026-04-28, prefer src/lib/v3/lane-mapping.ts` to:
- `src/lib/task-board-lane.ts` (function + type exports)
- `src/lib/projections/task-lane.ts` (function + type exports)

## Acceptance Criteria (Forge-side verifiable)

1. `toV3Status()` returns all 11 V3 statuses across the 6 sample tasks in
   `screenshots/task-sample.json` without ambiguity.
2. `toV3Status()` is pure: same `(task, now)` → same output.
3. Jest test: 100% branch coverage on derivation table, including all edge cases.
4. No mutation of `task-runtime-truth.ts`, `taskboard-types.ts`, or any
   non-`src/lib/v3/*` file.
5. Health aggregation `computeHealth(tasks)` returns parity with
   `/api/board/snapshot` openCount and consistencyIssues for current
   live data (Lens A/B-validation).
6. No mutation of `/kanban` or `/taskboard` routes.

## Edge Cases (must handle)

| Case                                                              | Existing Behavior            | V3 Mapping                                                |
|-------------------------------------------------------------------|------------------------------|-----------------------------------------------------------|
| `isHistoricalFailedArtifact(task) === true`                       | hidden (lane=archive)        | V3 Lane: `done` (archived). NOT `failed`.                 |
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
   `?density=…&mode=…&rail=…`.

## References

- Polish-Pass source: `source-export-final-2026-04-28-2213/`
- Original handoff: `mc-taskboard-v3-implementation-handoff.md`
- Sprint plan: `mc-taskboard-ui-simplification-sprint.md`
- Foundation atoms: `source-export-final-2026-04-28-2213/mc-v3-foundations.jsx`
- Final layout: `source-export-final-2026-04-28-2213/mc-v3-final.jsx`
- Drawer spec: `source-export-final-2026-04-28-2213/mc-v3-drawer.jsx`
