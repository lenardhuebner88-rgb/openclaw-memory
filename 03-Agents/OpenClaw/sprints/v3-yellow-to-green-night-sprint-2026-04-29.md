# V3 Yellow-to-Green Night Sprint — 2026-04-29

Owner: Atlas orchestration  
Primary workers: Pixel/frontend-guru, Forge/sre-expert only where explicitly needed  
Mode: Autonomous night sprint with bounded gates  
Master context: V3 Taskboard Sprint `e40a90c9-238f-4b68-aba3-a5123f54f913` ended YELLOW, not GREEN.

## Sprint Goal

Bring the V3 Taskboard preview from YELLOW to promotion-ready GREEN by closing the remaining acceptance gaps without expanding scope:

1. ControlBar behavior matches the V3 spec.
2. Mobile/compact behavior is validated and fixed where needed.
3. TruthRail does not create broken mobile/compact UX.
4. V3 health signal is trustworthy or clearly diagnosed.
5. Slice G live-task actions are validated only behind an Operator gate.

Non-goal: shipping a broad redesign, changing backend orchestration, changing worker routing, or enabling real state mutations without Operator acknowledgement.

## Current Baseline

Verified live before sprint planning:

- `/kanban-v3-preview` returns HTTP 200.
- `/api/board/v3-health` returns HTTP 200.
- Current health signal reported `incidentCount=78` and `blocked=78`.
- Final V3 report exists at `/home/piet/.openclaw/workspace/memory/05-learnings/v3-sprint-2026-04-29-final.md`.
- Verdict there is YELLOW because ControlBar/mobile behavior and Slice G live-task validation are incomplete.

## Night Sprint Rules

- No production promotion tonight unless all GREEN gates pass.
- No direct `tasks.json` mutation.
- No real dispatch/cancel/retry/approve state mutation without explicit Operator Ack.
- No service restart unless a task explicitly declares why and gets Operator Ack.
- UI files may be edited only by the assigned Pixel task.
- Forge may only touch backend/health/contracts if Atlas creates a separate bounded task.
- Each task must produce a result receipt with changed files, tests/checks, and remaining risks.
- If any worker sees route health degrade, STOP and report.

## Sprint Structure

### Phase 0 — Baseline + Lock Awareness

Owner: Atlas  
Type: read-only  
Expected time: 10-20 min

Actions:

- Read final report and V3 contracts.
- Capture current `/kanban-v3-preview` and `/api/board/v3-health` responses.
- Check active workers/tasks touching V3 UI files.
- Declare safe edit set for Pixel.
- Declare taboo files for the sprint.

Acceptance:

- Baseline report posted to Discord/status channel.
- Safe edit set is explicit.
- If another worker is touching same UI files, Atlas waits or reschedules.

Stop condition:

- Active conflicting UI worker found.
- Preview route not HTTP 200.
- Health route not HTTP 200.

### Phase 1 — Pixel: ControlBar + Mobile Fix

Owner: Pixel/frontend-guru  
Type: implementation  
Expected time: 2-4 h

Scope:

- ControlBar state must drive the preview layout.
- URL/search params must reflect selected mode/density/truthRail.
- localStorage persistence must match spec.
- Mobile/compact must hide or replace TruthRail safely.
- Keyboard shortcuts only if already present/spec-backed; otherwise do not invent extra behavior.

Likely files:

- `src/components/v3/V3FinalDesktop.tsx`
- related V3 ControlBar/mobile components if already split out
- focused tests only if existing patterns exist

Anti-scope:

- No backend route changes.
- No real task mutation actions.
- No unrelated CSS/theme refactor.
- No dashboard-wide redesign.

Acceptance:

- Desktop comfy/dense modes visibly change density.
- Board/triage mode visibly changes layout arrangement.
- TruthRail can be toggled on desktop.
- TruthRail is not shown as a broken side rail on mobile/compact.
- URL and localStorage round-trip without contradictory values.
- Preview route remains HTTP 200.

Stop condition:

- Required behavior cannot be implemented without broader component refactor.
- Existing V3 route breaks.
- Hydration/runtime errors appear.

### Phase 2 — Validation: Browser + Route Checks

Owner: Atlas or Lens  
Type: validation  
Expected time: 30-60 min

Actions:

- Validate `/kanban-v3-preview` desktop.
- Validate mobile/small viewport.
- Verify task titles/cards still render from live snapshot.
- Verify no obvious overlap, clipped buttons, or broken drawer layout.
- Verify `/api/board/v3-health` still returns HTTP 200.

Acceptance:

- Desktop and mobile screenshots or precise visual notes are saved.
- ControlBar behavior is proven, not assumed.
- Any remaining UI issue is classified as blocker/non-blocker.

Stop condition:

- Route 500/404.
- Hydration error.
- Mobile unusable.

### Phase 3 — Forge: V3 Health Incident Count Triage

Owner: Forge/sre-expert  
Type: read-only first; patch only if low-risk and bounded  
Expected time: 1-2 h

Question:

Why does `/api/board/v3-health` report `incidentCount=78` and `blocked=78`?

Required distinction:

- Real active blocked tasks.
- Archived/done tasks incorrectly counted.
- Follow-up drafts that should not count as active incidents.
- Failed/blocked lane projection issue.

Acceptance:

- Forge produces exact root cause with API/file references.
- If patch is needed, Forge creates a separate bounded fix task; it does not silently patch broad logic.
- Atlas decides whether this blocks GREEN.

Stop condition:

- Counting logic touches broad board lifecycle behavior.
- Data requires manual human cleanup.

### Phase 4 — Slice G Live-Task Validation Gate

Owner: Atlas, optionally Forge/Pixel  
Type: gated validation  
Expected time: 30-60 min

Purpose:

Validate state-action UI/flow without causing accidental production state changes.

Rules:

- No live state mutation without Operator Ack.
- If validation needs a test task, Atlas must ask for Operator Ack and create a safe dummy or use a clearly disposable test task.
- If only read-only validation is possible, mark Slice G as `YELLOW_ACCEPTABLE_WITH_OPERATOR_GATE`, not GREEN.

Acceptance:

- Atlas reports exactly which actions are mock-only, gated, or live.
- No false impression that mutation actions are fully production-approved.
- Promotion recommendation includes this caveat if not fully validated.

Stop condition:

- Any action would mutate a real task without confirmation.
- Human-review guard blocks validation path.

### Phase 5 — Final Aggregation

Owner: Atlas  
Type: report  
Expected time: 20-40 min

Output:

- `GREEN`, `YELLOW_WITH_KNOWN_GATES`, or `BLOCKED` verdict.
- Changed files and commits.
- Route health evidence.
- Browser validation evidence.
- Remaining operator actions.
- Clear next single action.

GREEN requires:

- ControlBar/mobile acceptance fixed and validated.
- Preview and health routes HTTP 200.
- No new critical incidents created.
- V3 health incident count is explained or corrected.
- Slice G validation is either completed safely or explicitly kept behind Operator gate with no misleading UI.

## Recommended Atlas Dispatch Prompt

```text
Atlas, run the V3 Yellow-to-Green Night Sprint using this plan:
/home/piet/vault/03-Agents/OpenClaw/sprints/v3-yellow-to-green-night-sprint-2026-04-29.md

Start with Phase 0 read-only baseline. Then dispatch only the bounded Pixel ControlBar/Mobile task if no conflicting UI worker is active.

Hard rules:
- No direct tasks.json mutation.
- No service restart without Operator Ack.
- No real task state mutation without Operator Ack.
- No broad redesign.
- Keep edits limited to V3 preview/controlbar/mobile files unless a separate task is created.

After Pixel result, validate desktop/mobile preview and route health. Then triage `/api/board/v3-health` incidentCount=78/blocked=78 as a separate read-only Forge task. Treat Slice G live actions as gated: validate read-only first, ask Operator before any live mutation.

Final output tonight: GREEN / YELLOW_WITH_KNOWN_GATES / BLOCKED, with evidence, changed files, route checks, browser validation, and next single action.
```

## Operator Morning Review Checklist

- Did Atlas keep scope bounded?
- Did Pixel only touch V3 UI files?
- Are `/kanban-v3-preview` and `/api/board/v3-health` still HTTP 200?
- Was the `incidentCount=78` signal explained?
- Is Slice G still gated or safely validated?
- Is V3 ready for promotion, or only preview-hardening complete?
﻿
---

## Live Update — Atlas Started Follow-up

Timestamp: 2026-04-29 late evening  
Source: Atlas operator response

### Active Pixel Task

- Task: `4d30f81f-31bc-42fa-8a36-bed6fb248c30`
- Owner: Pixel / frontend-guru
- Dispatch: verified, `pending-pickup`, `dispatchState=dispatched`
- Documentation: `/home/piet/.openclaw/workspace/memory/working/2026-04-29-v3-yellow-to-green-followup.md`
- Commit referenced by Atlas: `0879ad34`

### Allowed Pixel Edit Scope

Pixel may touch only the bounded V3 preview/controlbar/mobile surface:

- `mission-control/src/app/kanban-v3-preview/page.tsx`
- `mission-control/src/app/kanban-v3-preview/[id]/page.tsx` only if needed
- `mission-control/src/components/v3/V3FinalDesktop.tsx`
- `mission-control/src/components/v3/V3FinalTopChrome.tsx`
- `mission-control/src/components/v3/V3FinalSubBar.tsx`
- `mission-control/src/components/v3/V3FinalSidebar.tsx`
- `mission-control/src/components/v3/MeaningRail.tsx`
- `mission-control/src/components/v3/V3DetailsDrawer.tsx` only if needed
- directly related tests/docs only

### Pixel Acceptance Criteria

- ControlBar state affects layout behavior.
- URL/SearchParams and localStorage follow V3 spec.
- TruthRail/MeaningRail is correctly hidden or replaced in compact/mobile.
- Desktop and mobile remain regression-free.
- Smallest meaningful frontend gate runs.

### Pixel Stop Conditions

- No backend/API/service/store changes.
- No restart, cron, gateway, or model-routing changes.
- No live task actions.
- No edits to legacy `/kanban`, `/taskboard`, or `/dashboard` routes.
- If scope must expand, Pixel must return BLOCKED instead of improvising.

### v3-health Finding

`/api/board/v3-health` previously reported `incidentCount=78` and `blocked=78`.

Atlas finding:

- These 78 are not active blockers.
- All 78 are terminal tasks:
  - `canceled=48`
  - `failed=27`
  - `done=3`
- Root cause: `toV3Status()` evaluates `blockerReason` before terminal status. Old terminal follow-ups with retained `blockerReason` are therefore counted as V3 blocked.
- Status: documented only, not fixed in this follow-up yet.

### Updated Night Sprint Interpretation

The health finding changes Phase 3 from open discovery to a known follow-up candidate:

- This is not an operations emergency.
- It is a V3 status-derivation/order-of-precedence bug.
- It should be fixed only as a separate bounded Forge task after Pixel finishes, unless Atlas decides it blocks GREEN.
- Suggested owner: Forge/sre-expert.
- Suggested scope: status derivation and tests for terminal tasks with retained blocker metadata.

### Updated Next Decision

After Pixel completes task `4d30f81f-31bc-42fa-8a36-bed6fb248c30`, Atlas should choose one of these:

1. If ControlBar/mobile passes and health bug is considered GREEN-blocking:
   - Create bounded Forge fix for `toV3Status()` terminal precedence.
2. If ControlBar/mobile passes and health bug is acceptable as documented follow-up:
   - Mark sprint `YELLOW_WITH_KNOWN_GATES` and defer health fix.
3. If ControlBar/mobile fails:
   - Keep sprint BLOCKED/YELLOW and do not start Slice-G validation.

### Operator Ack Reminder

No Operator Ack is needed until Slice-G live validation would perform real state mutations.
Until then, all checks remain read-only or preview-only.
