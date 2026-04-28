---
title: MC Taskboard UI Simplification Sprint
date: 2026-04-28
status: planned
scope: design-handoff-to-implementation
code_changes: none
---

# MC Taskboard UI Simplification Sprint

## Goal

Turn the Claude Design output for Mission Control Taskboard/Kanban into small, safe implementation slices. The sprint should improve scanability, reduce card noise, clarify worker/task truth, and move technical depth into a details drawer/modal.

## Preconditions

- Claude Design produces three variants and one recommended direction.
- Terminal-Codex/Pixel active work is checked before any code edits.
- No implementation starts while another worker owns the same Taskboard/Kanban UI files.
- Task lifecycle truth must be preserved; visual simplification must not create false state.

## Slice 1 - Taskboard Layout Shell

Goal: Reduce top-level visual clutter before task cards and establish a clearer operational board hierarchy.

Files:

- `src/components/taskboard/taskboard-client.tsx`
- `src/components/taskboard/MorningStatusHero.tsx`
- `src/components/taskboard/system-pulse.tsx`
- `src/components/taskboard/agent-load-panel.tsx`

Risk: Useful operator context may become hidden or feel disconnected.

Acceptance criteria:

- First viewport makes active/waiting/blocked/review work visible faster than current UI.
- Header and health signals do not compete with the board.
- No state-changing behavior changes.

Stop condition:

- If lifecycle or operator truth becomes ambiguous, stop and re-map the hierarchy before continuing.

Owner:

- Frontend-Guru / Pixel, coordinated by Atlas.

## Slice 2 - Kanban Lane Mapping

Goal: Map task runtime truth into clear lanes: Draft, Ready/Waiting, Assigned, Active, Review Needed, Done, Failed/Blocked.

Files:

- `src/lib/task-board-lane.ts`
- `src/lib/taskboard-projection.ts`
- `src/lib/task-status-presentation.ts`
- `src/lib/task-runtime-truth.ts`
- `src/lib/projections/task-lane.ts`

Risk: Accepted-but-stalled, queued, failed, blocked, and review-needed tasks can be misclassified.

Acceptance criteria:

- Accepted without progress does not look like healthy active work.
- Failed and blocked are visually related but semantically distinct.
- Review Needed has its own unambiguous lane/state.

Stop condition:

- If real task data produces contradictory lane assignments, stop and add mapping tests before UI polish.

Owner:

- Forge or Codex for logic review; Frontend-Guru for presentation integration.

## Slice 3 - Slim Task Card

Goal: Keep only high-signal information on cards.

Visible card fields:

- Title
- Agent/worker label
- Canonical status
- Priority/risk
- Age/staleness
- Receipt stage
- One short blocker/result/next-action line

Files:

- `src/components/taskboard/task-card.tsx`
- `src/lib/task-status-presentation.ts`
- `src/lib/taskboard-types.ts`

Risk: Removing data that operators use for quick decisions.

Acceptance criteria:

- Cards are compact and scannable.
- Raw metadata and long summaries are not visible on cards.
- The first line answers what the task is; the second signal answers what needs attention.

Stop condition:

- If operators need to open details for every normal decision, restore one missing high-signal field.

Owner:

- Frontend-Guru / Pixel.

## Slice 4 - Details Drawer / Modal

Goal: Move technical depth into a structured details surface.

Content:

- Current truth and suggested next safe action
- Lifecycle
- Receipt chain
- Dispatch token
- Worker session ID
- Acceptance criteria
- Events
- Logs/history
- Parent/follow-up relation
- Result summary/details
- Blocker/risk detail
- Raw metadata in optional advanced section

Files:

- `src/components/taskboard/task-detail-modal.tsx`
- `src/lib/task-drilldown.ts`
- `src/lib/taskboard-data.ts`

Risk: The drawer becomes a raw-data dump again.

Acceptance criteria:

- First drawer section gives current truth and next safe action.
- Lifecycle/receipts are grouped and readable.
- Raw metadata is available but not primary.

Stop condition:

- If long prompt text dominates the drawer top, pause and redesign the section order.

Owner:

- Frontend-Guru / Pixel with Atlas review.

## Slice 5 - Loading / Empty / Error States

Goal: Make transient and failure states honest and visually distinct.

Files:

- `src/app/taskboard/loading.tsx`
- `src/app/taskboard/page.tsx`
- `src/app/kanban/page.tsx`
- `src/app/kanban/PipelineClient.tsx`

Risk: Mixed loading and live-data states can imply stale or false confidence.

Acceptance criteria:

- Loading never appears beside apparently final KPI truth unless clearly labeled.
- Empty lane state is calm and useful.
- Error state explains what is unavailable without suggesting task mutation.

Stop condition:

- If live and loading states overlap visually, fix before moving to polish.

Owner:

- Frontend-Guru / Pixel.

## Slice 6 - Stale / Blocked / Review Visual Cues

Goal: Create a consistent visual language for stale, blocked, failed, review-needed, active, and done states.

Files:

- `src/lib/task-status-presentation.ts`
- `src/components/taskboard/task-card.tsx`
- `src/app/kanban/components/TaskPipelineCard.tsx`
- `src/app/kanban/components/WaitingReasonBadge.tsx`

Risk: Color overload and alarm fatigue.

Acceptance criteria:

- State meaning is readable without relying only on color.
- Review Needed is not confused with Failed.
- Blocked is not confused with Done terminal state.

Stop condition:

- If two critical states share the same visual treatment, stop and revise taxonomy.

Owner:

- Frontend-Guru / Pixel; Codex review for truth mapping.

## Slice 7 - Responsive Layout

Goal: Preserve task truth and action clarity on mobile.

Files:

- Taskboard and Kanban components touched in prior slices.

Risk: Mobile layout hides lane state or creates oversized controls.

Acceptance criteria:

- Mobile view shows lane/status and next action clearly.
- Details drawer can become a full-screen sheet.
- Text does not overlap or overflow.

Stop condition:

- If mobile scanability becomes worse than the current UI, stop and simplify controls.

Owner:

- Frontend-Guru / Pixel.

## Slice 8 - Build / Test / Visual Validation

Goal: Verify the result with build, state examples, and screenshots.

Files:

- Relevant tests for lane/status mapping.
- Screenshot artifacts for desktop and mobile.

Risk: UI looks correct but state mapping regresses.

Acceptance criteria:

- Build passes.
- Task examples render in expected lanes.
- Desktop and mobile screenshots match chosen Claude Design direction.
- No dispatch/finalize/retry/delete behavior changed unless explicitly scoped later.

Stop condition:

- Any state mapping regression blocks release.

Owner:

- Terminal-Codex for build/deploy gate; Codex App for design-review audit if requested.

