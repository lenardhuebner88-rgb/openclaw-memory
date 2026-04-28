---
title: Claude Design Brief - Mission Control Taskboard
date: 2026-04-28
status: ready-for-claude-design
scope: design-only
sources:
  - live-browser-analysis
  - read-only-code-structure
  - vault-sprint-task-lifecycle-context
code_changes: none
ui_state_changed: false
---

# Claude Design Brief - Mission Control Taskboard

## Source Summary

This brief is based on three inputs:

1. Live Mission Control browser analysis at `http://192.168.178.61:3000`.
2. Read-only inspection of Mission Control taskboard/kanban component structure.
3. Existing Vault and sprint context around OpenClaw task lifecycle, Atlas coordination, dispatch receipts, worker sessions, stale/blocked/review signals, and prior Claude Design prep.

No production code was changed. No tasks were dispatched, moved, finalized, retried, approved, or deleted. The browser was used read-only for navigation, screenshots, and inspection.

## Live Browser Evidence

Browser reachable: YES  
Used URL: `http://192.168.178.61:3000`

Checked screens:

- Dashboard: `/dashboard`
- Taskboard: `/taskboard`
- Task detail panel: `/taskboard?task=82c4076f-878e-4bf9-89e4-b36e168f57fa`
- Kanban/Pipeline: `/kanban`
- Alerts: `/alerts`

Screenshot references:

- `/home/piet/vault/03-Agents/OpenClaw/design/screenshots/2026-04-28-taskboard-brief/dashboard-desktop.png`
- `/home/piet/vault/03-Agents/OpenClaw/design/screenshots/2026-04-28-taskboard-brief/taskboard-desktop.png`
- `/home/piet/vault/03-Agents/OpenClaw/design/screenshots/2026-04-28-taskboard-brief/taskboard-detail-desktop.png`
- `/home/piet/vault/03-Agents/OpenClaw/design/screenshots/2026-04-28-taskboard-brief/taskboard-mobile.png`
- `/home/piet/vault/03-Agents/OpenClaw/design/screenshots/2026-04-28-taskboard-brief/kanban-desktop.png`
- `/home/piet/vault/03-Agents/OpenClaw/design/screenshots/2026-04-28-taskboard-brief/alerts-desktop.png`

Task sample data:

- `/home/piet/vault/03-Agents/OpenClaw/design/screenshots/2026-04-28-taskboard-brief/task-sample.json`

## Observed UI Problems

The current Taskboard is operationally rich but too noisy for fast command decisions. It shows many technically correct signals, yet the visual order does not consistently answer: what needs action, who owns it, what state is true, and what Atlas should do next.

Key live observations:

- Dashboard can show zero active/at-risk values while Taskboard still has active/ready work, which weakens trust in cross-page status.
- Taskboard starts with multiple high-density sections before the actual cards: header, health strip, operator suggestion, morning status, pulse, lane chips, and summary panels.
- Task cards show too much at once: title, agent, priority, status, age, project, next action, description text, buttons, and mobile swipe hints. The useful signal is there, but scan speed is low.
- The detail panel is comprehensive but front-loads long prompt/summary text. Lifecycle, receipt truth, dispatch token, worker session, events, blockers, and result history need stronger grouping.
- Kanban/Pipeline mixes loading text, KPI chips, incidents, stage steppers, and task cards at the same visual weight. Failed/incident/review meanings are easy to confuse.
- Alerts proves the system has massive signal volume. Taskboard should summarize alert/health influence, not repeat alert-feed density.
- Stale, blocked, failed, review-needed, accepted-but-no-progress, and terminal states need a stricter visual taxonomy.

## Relevant Read-Only Code Structure

Taskboard files:

- `src/app/taskboard/page.tsx`
- `src/app/taskboard/layout.tsx`
- `src/app/taskboard/loading.tsx`
- `src/components/taskboard/taskboard-client.tsx`
- `src/components/taskboard/task-card.tsx`
- `src/components/taskboard/task-detail-modal.tsx`
- `src/components/taskboard/agent-load-panel.tsx`
- `src/components/taskboard/MorningStatusHero.tsx`
- `src/components/taskboard/system-pulse.tsx`
- `src/components/taskboard/activity-feed.tsx`
- `src/components/board-filters.tsx`

Kanban/Pipeline files:

- `src/app/kanban/page.tsx`
- `src/app/kanban/PipelineClient.tsx`
- `src/app/kanban/components/TaskPipelineCard.tsx`
- `src/app/kanban/components/StageStepper.tsx`
- `src/app/kanban/components/NextUpPreview.tsx`
- `src/app/kanban/components/ViewToggle.tsx`
- `src/app/kanban/components/WaitingReasonBadge.tsx`

Task truth and lane logic:

- `src/lib/task-board-lane.ts`
- `src/lib/taskboard-control-view.ts`
- `src/lib/taskboard-data.ts`
- `src/lib/taskboard-intelligence.ts`
- `src/lib/taskboard-now-view.ts`
- `src/lib/taskboard-projection.ts`
- `src/lib/taskboard-types.ts`
- `src/lib/task-status-presentation.ts`
- `src/lib/task-operator-state.ts`
- `src/lib/task-runtime-truth.ts`
- `src/lib/task-dispatch.ts`
- `src/lib/task-dispatch-gate.ts`
- `src/lib/task-drilldown.ts`
- `src/lib/projections/task-lane.ts`

Current implementation handoff constraint:

- Do not ask Claude Design to rewrite the codebase.
- Ask for a visual/interaction concept and a practical component handoff.
- Codex/Frontend-Guru should later map the output into small Next.js/Tailwind slices.

## Existing Vault Context

Relevant existing context:

- `/home/piet/vault/04-Sprints/planned/2026-04-27_mc-ui-audit-claude-design-prep.md`
- `/home/piet/vault/07-Research/design-handoffs/2026-04-20-taskboard/design-canvas.jsx`
- `/home/piet/vault/07-Research/design-handoffs/2026-04-20-taskboard/Taskboard v2 - Mobile Redesign.html`
- `/home/piet/vault/02-Docs/Design-Packs/claude-design-packs/mc-design-pack-taskboard-2026-04-20-0742.zip`

Existing direction from the Vault:

- Use Claude Design as a manual design/prototype surface, not as a live repo editor.
- Provide screenshots, reduced sample data, product goals, constraints, and non-goals.
- Avoid complete codebase dumps, long logs, server details, or vague goals.
- Stop design iteration after one or two useful passes, then hand off to Codex/Frontend-Guru.

## Copy-Paste Prompt For Claude Design

```text
You are Claude Design. Create a production-grade UI concept for the Mission Control Taskboard in OpenClaw.

MISSION CONTROL SUMMARY
Mission Control is the operator cockpit for OpenClaw, a multi-agent autonomy system. It helps Atlas and human operators see task truth, worker ownership, lifecycle receipts, blockers, stale work, review needs, and follow-up actions. It is not a marketing dashboard. It is an operational control surface for repeated daily use.

ROLE OF THE TASKBOARD
The Taskboard is where Atlas decides what is draft, ready, assigned, active, blocked, stale, review-needed, done, or failed. It must make the next safe action obvious without hiding lifecycle truth. The UI must support fast scanning, clean prioritization, worker coordination, and details on demand.

CURRENT PAIN FROM LIVE BROWSER REVIEW
I reviewed the live Mission Control UI. The current Taskboard is information-rich but visually noisy.

Observed issues:
- Too many top-level panels compete before the actual tasks are visible.
- Task cards expose too many technical fields at once.
- Key action signals are buried among project labels, descriptions, buttons, and repeated status text.
- Details panel is thorough but long prompt/summary text dominates before lifecycle and receipt truth.
- Kanban/Pipeline stage indicators are useful but crowded; failed, blocked, review, stale, and terminal states can be confused.
- Dashboard, Taskboard, Kanban, and Alerts do not always feel like one shared status language.
- Health and alert signals are high volume; Taskboard needs a summarized operational signal, not an alert-feed clone.

SCREENSHOT REFERENCES
Use these screenshots as the current-state visual reference:
- dashboard-desktop.png
- taskboard-desktop.png
- taskboard-detail-desktop.png
- taskboard-mobile.png
- kanban-desktop.png
- alerts-desktop.png

If screenshots are attached in this Claude conversation, treat them as the primary source of current visual truth.

TARGET OUTCOME
Design a slimmer, faster, operational Taskboard/Kanban experience.

The target UI should:
- Be easier to scan in under 10 seconds.
- Put task state truth ahead of decoration.
- Keep task cards compact and high-signal.
- Move lifecycle depth, receipts, dispatch tokens, worker sessions, event logs, acceptance criteria, and raw metadata into a details drawer/modal.
- Clearly separate active work, waiting work, review work, blocked work, failed work, and completed work.
- Make stale/blocked/review/failed states impossible to miss without making the page visually alarming.
- Support Atlas steering and follow-up task creation.
- Avoid suggesting false states. For example, accepted-without-progress must not look the same as actively progressing work.

TARGET LANES
Design for these lanes:
1. Draft
2. Ready / Waiting
3. Assigned
4. Active
5. Review Needed
6. Done
7. Failed / Blocked

TASK CARD DATA THAT SHOULD STAY VISIBLE
Each card should show only high-signal data:
- Title
- Agent / worker label
- Canonical status
- Priority or risk
- Age / staleness
- Receipt stage
- One short blocker/result/next-action line

TASK DATA THAT SHOULD MOVE INTO DETAILS DRAWER/MODAL
The details drawer/modal should contain:
- Full lifecycle
- Receipt chain
- Dispatch token
- Worker session ID
- Acceptance criteria
- Events
- Logs/history
- Parent/follow-up relationship
- Full result summary/details
- Blocker/risk detail
- Raw metadata as optional advanced section

STATES TO DESIGN
Include visual treatment for:
- Loading
- Empty lane
- Error state
- Stale task
- Blocked task
- Failed task
- Review-needed task
- Accepted but no heartbeat/progress
- Active with healthy heartbeat
- Done with result summary
- Draft waiting for dispatch
- Assigned/queued but not accepted

DESIGN CONSTRAINTS
- This is an operational SaaS/internal tool, not a landing page.
- No hero marketing layout.
- No decorative gradient blobs/orbs.
- Avoid a one-note dark-blue/purple dashboard look.
- No nested cards inside cards.
- Keep cards compact, with strong hierarchy and predictable scan paths.
- Use restrained color: status color should mean something and be consistent.
- Prefer familiar controls: tabs for views, segmented controls for modes, icons for simple tools, buttons only for clear commands.
- Preserve accurate state truth over visual polish.
- Design should be implementable in Next.js + Tailwind with existing components.
- Do not require a total rewrite. Think in small implementation slices.
- Do not include production code unless asked. Provide a component-level design and handoff spec.

SAMPLE TASK DATA
Use these sample tasks to design realistic cards and lanes:

[
  {
    "id": "efb571d6",
    "title": "[P2][Pixel] MC-T03 Alerts - Group-Collapse UI for cost-spam fatigue",
    "agent": "frontend-guru / Pixel",
    "status": "done",
    "executionState": "done",
    "dispatchState": "completed",
    "receiptStage": "result",
    "priority": "P2",
    "age": "today",
    "line": "Result available; UI grouped alert noise into collapsible categories."
  },
  {
    "id": "65d93c82",
    "title": "MC-T02 Foundations - Dashboard signal cleanup",
    "agent": "frontend-guru / Pixel",
    "status": "done",
    "executionState": "done",
    "dispatchState": "completed",
    "receiptStage": "result",
    "priority": "P2",
    "age": "today",
    "line": "Completed after accepted receipt and build verification."
  },
  {
    "id": "82c4076f",
    "title": "[P1][Forge] Add Taskboard MCP wrappers for receipt/finalize/move",
    "agent": "sre-expert / Forge",
    "status": "draft",
    "executionState": "queued",
    "dispatchState": "draft",
    "receiptStage": "none",
    "priority": "P1",
    "age": "new",
    "line": "Draft waiting for safe dispatch decision."
  },
  {
    "id": "42df1ec1",
    "title": "[P2][Forge] mc-pending-pickup-smoke.sh - operatorLock missing in payload",
    "agent": "sre-expert / Forge",
    "status": "failed",
    "executionState": "failed",
    "dispatchState": "completed",
    "receiptStage": "failed",
    "priority": "P2",
    "age": "older",
    "line": "Failed; needs blocker/root-cause review before retry."
  },
  {
    "id": "e31ff00a",
    "title": "[P2][Forge] mc-pending-pickup-smoke.sh - operatorLock missing in payload",
    "agent": "sre-expert / Forge",
    "status": "assigned",
    "executionState": "queued",
    "dispatchState": "queued",
    "receiptStage": "queued",
    "priority": "P2",
    "age": "older",
    "line": "Queued/assigned but no accepted receipt yet."
  },
  {
    "id": "7f4cdd21",
    "title": "[P1][Forge] 403 Auto-Pickup Bug - Ingress/Receipt Validation",
    "agent": "sre-expert / Forge",
    "status": "failed",
    "executionState": "failed",
    "dispatchState": "completed",
    "receiptStage": "failed",
    "priority": "P1",
    "age": "stale",
    "line": "High-risk failed autonomy path; needs explicit review."
  },
  {
    "id": "916d45c6",
    "title": "[MC-T01] T4 Retry: Cost Source-of-Truth Consolidation",
    "agent": "backend / Atlas",
    "status": "done",
    "executionState": "done",
    "dispatchState": "completed",
    "receiptStage": "result",
    "priority": "P1",
    "age": "recent",
    "line": "Completed retry with source-of-truth consolidation."
  }
]

NON-GOALS
- Do not design a landing page.
- Do not redesign the whole OpenClaw product.
- Do not expose every technical field on cards.
- Do not create a decorative SaaS marketing dashboard.
- Do not hide lifecycle truth behind vague labels.
- Do not assume all failed tasks are blockers; distinguish failed, blocked, review-needed, and stale.
- Do not propose state-changing actions without confirmation patterns.
- Do not require a total rewrite of Mission Control.

DESIRED OUTPUT
Please produce:

1. Three distinct Taskboard/Kanban UI variants.
   - Variant A: dense operator cockpit, fastest scanning.
   - Variant B: balanced board with clear lane structure and details drawer.
   - Variant C: incident-first board optimized for stale/blocked/review triage.

2. A recommendation:
   - Pick one direction or a hybrid.
   - Explain why it fits Mission Control and Atlas.

3. Component structure:
   - Taskboard shell
   - Lane header
   - Slim task card
   - Status/receipt badge system
   - Stale/blocked/review visual cue system
   - Details drawer/modal
   - Empty/loading/error states
   - Mobile layout

4. Handoff spec for Codex/Frontend-Guru:
   - Small implementation slices.
   - What data each component needs.
   - Which behavior stays read-only.
   - Which controls are state-changing and need safeguards.
   - Suggested Next.js/Tailwind implementation notes.

5. Acceptance criteria:
   - A user can identify active, blocked, stale, failed, and review-needed tasks within 10 seconds.
   - Task cards are compact and do not expose raw metadata.
   - Details drawer contains lifecycle, receipts, dispatch token, worker session, events, logs/history, acceptance criteria, parent/follow-up links, and raw metadata.
   - Visual states do not suggest false progress.
   - Mobile view remains readable and actionable.
   - The output is implementable without a full rewrite.
```

## Recommended Claude Design Iteration

Iteration 1:

- Give Claude Design the screenshots and the prompt above.
- Ask for three variants and a recommendation.
- Do not attach the full codebase.

Iteration 2:

- Pick the best variant or hybrid.
- Ask Claude Design to reduce noise, sharpen scanability, and finalize the handoff spec.

Iteration 3 only if needed:

- Use it only to clarify component handoff details.
- After two useful design passes, Codex/Frontend-Guru should implement.

## Implementation Translation Notes

Translate the chosen Claude Design output into small slices:

1. Taskboard layout shell
   - Goal: simplify top-level hierarchy and reduce pre-card clutter.
   - Files: `taskboard-client.tsx`, related shell components.
   - Risk: hiding useful operator context.
   - Acceptance: first screen shows board truth and next action faster than today.

2. Kanban lane mapping
   - Goal: map task runtime truth into Draft, Ready/Waiting, Assigned, Active, Review Needed, Done, Failed/Blocked.
   - Files: `task-board-lane.ts`, taskboard projection/status presentation files.
   - Risk: false state mapping.
   - Acceptance: accepted-without-progress is not shown as healthy active progress.

3. Slim task card
   - Goal: keep only title, agent, status, priority/risk, age/staleness, receipt stage, one result/blocker line.
   - Files: `task-card.tsx`, task status presentation.
   - Risk: removing data operators still need immediately.
   - Acceptance: card is compact and scan-friendly.

4. Details drawer/modal
   - Goal: make lifecycle, receipts, events, worker session, acceptance criteria, result, blockers, and metadata accessible on demand.
   - Files: `task-detail-modal.tsx`, drilldown helpers.
   - Risk: details become a dumping ground.
   - Acceptance: first drawer section answers current truth and next safe action.

5. Loading/empty/error states
   - Goal: prevent mixed loading and live-data states.
   - Files: page loading components and Taskboard/Kanban clients.
   - Risk: showing stale UI as live.
   - Acceptance: loading/error/empty states are visually distinct and honest.

6. Stale/blocked/review cues
   - Goal: unified visual taxonomy.
   - Files: status presentation helpers and card/lane components.
   - Risk: color overload.
   - Acceptance: severity is clear without alarm fatigue.

7. Responsive layout
   - Goal: mobile board remains readable; details can become full-screen sheet.
   - Files: Taskboard/Kanban components.
   - Risk: mobile controls become too large or hide state truth.
   - Acceptance: mobile first screen still exposes lane/status and next action.

8. Build/test/visual validation
   - Goal: verify rendering and state mapping.
   - Files: tests plus screenshots.
   - Risk: visual drift from intended design.
   - Acceptance: build passes and desktop/mobile screenshots match agreed design direction.

## Coordination Status

Status: SAFE_TO_PLAN

Do not implement while Terminal-Codex/Pixel is actively editing related UI or deploying. Before coding, re-check current changed files and active worker sessions. At the time of this brief, planning and documentation are safe; UI implementation should be separately coordinated.

