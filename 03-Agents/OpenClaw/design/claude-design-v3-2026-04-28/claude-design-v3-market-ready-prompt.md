You are Claude Design working inside the existing Mission Control Taskboard project.

IMPORTANT CONTEXT
This project already contains a good older prototype:
- Taskboard v2 - Mobile Redesign.html
- V1 Mobile
- V2 Mobile
- V2 Tablet
- V2 Desktop
- Interaction states
- Components: mc-v2-states-canvas.jsx, mc-v2-states.jsx, mc-v2-responsive.jsx, mc-v2.jsx, mc-mobile-shared.jsx, mc-v1.jsx, design-canvas.jsx
- Styles/tokens: mc-tokens.css, tokens.js

Do not throw that work away. Treat it as the existing visual language and interaction reference.

NEW GOAL
Create a V3 market-ready operational UI direction for Mission Control Taskboard/Kanban.

Mission Control is the operator cockpit for OpenClaw, a multi-agent autonomy system. It helps Atlas and human operators see task truth, worker ownership, lifecycle receipts, blockers, stale work, review needs, and follow-up actions. This is not a marketing dashboard. It is an operational control surface for repeated daily use.

The UI must feel more polished, professional, and production-ready on both Mobile and Desktop, while staying fast, dense, and honest about system state.

LIVE CURRENT-STATE OBSERVATIONS
The live Mission Control UI was reviewed in browser. Current pain:
- Dashboard can show zero/healthy summaries while Taskboard still has active or ready work, reducing trust.
- Taskboard starts with too many high-density sections before the actual cards: header, health strip, operator suggestion, morning status, pulse, lane chips, summaries.
- Task cards show too much at once: title, agent, priority, status, age, project, next action, description snippet, and multiple buttons.
- Detail drawer/modal is rich but long prompt/summary text dominates before lifecycle, receipt truth, worker session, and next safe action.
- Kanban/Pipeline mixes loading text, KPI chips, incident states, stage steppers, and task cards at similar visual weight.
- Alerts has massive volume; Taskboard should summarize alert/health influence instead of becoming another alert feed.
- Stale, blocked, failed, review-needed, accepted-without-progress, and terminal states need a stricter visual taxonomy.

PRODUCT GOAL
Design a slimmer, faster, more beautiful operational Taskboard/Kanban experience that is scannable in under 10 seconds and suitable for a market-ready Mission Control product.

Target outcomes:
- Mobile-first but not mobile-only.
- Desktop must be excellent for real operators.
- Task state truth must be visually obvious.
- Active workers and blockers must stand out immediately.
- Cards must be compact and high-signal.
- Details must move into a drawer/modal/sheet.
- No false progress: accepted-without-heartbeat must not look like healthy active work.
- Atlas steering and follow-up task creation should feel first-class.

TARGET LANES
Use this canonical lane model:
1. Draft
2. Ready / Waiting
3. Assigned
4. Active
5. Review Needed
6. Done
7. Failed / Blocked

CARD CONTENT: ONLY HIGH SIGNAL
Task cards should show:
- Title
- Agent / worker label
- Canonical status
- Priority or risk
- Age / staleness
- Receipt stage
- One short blocker/result/next-action line

MOVE TO DETAILS DRAWER/MODAL
Details should contain:
- Current truth and suggested next safe action
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
Include:
- Loading
- Empty lane
- Error
- Stale
- Blocked
- Failed
- Review-needed
- Accepted but no heartbeat/progress
- Active with healthy heartbeat
- Done with result summary
- Draft waiting for dispatch
- Assigned/queued but not accepted

REALISTIC SAMPLE TASKS
Use these examples:
1. [P2][Pixel] MC-T03 Alerts - Group-Collapse UI for cost-spam fatigue
   Agent: frontend-guru / Pixel
   Status: done, execution done, dispatch completed, receipt result
   Line: Result available; UI grouped alert noise.

2. MC-T02 Foundations - Dashboard signal cleanup
   Agent: frontend-guru / Pixel
   Status: done, receipt result
   Line: Completed after accepted receipt and build verification.

3. [P1][Forge] Add Taskboard MCP wrappers for receipt/finalize/move
   Agent: sre-expert / Forge
   Status: draft, execution queued, dispatch draft, receipt none
   Line: Draft waiting for safe dispatch decision.

4. [P2][Forge] mc-pending-pickup-smoke.sh - operatorLock missing in payload
   Agent: sre-expert / Forge
   Status: failed, dispatch completed, receipt failed
   Line: Failed; needs blocker/root-cause review before retry.

5. [P2][Forge] mc-pending-pickup-smoke.sh - retry
   Agent: sre-expert / Forge
   Status: assigned, execution queued, dispatch queued
   Line: Queued/assigned but no accepted receipt yet.

6. [P1][Forge] 403 Auto-Pickup Bug - Ingress/Receipt Validation
   Agent: sre-expert / Forge
   Status: failed/stale, high risk
   Line: High-risk failed autonomy path; needs explicit review.

DESIGN CONSTRAINTS
- Operational SaaS/internal tool, not a landing page.
- No hero marketing treatment.
- No decorative gradient blobs/orbs.
- Avoid generic one-note dark blue/purple dashboard styling.
- Use restrained color where every status color means something.
- No nested cards inside cards.
- Compact cards, clear lane hierarchy, strong scan path.
- Preserve existing Mission Control brand/tokens where useful, but raise polish.
- Mobile and Desktop must both feel native and complete.
- Use familiar controls: tabs, segmented controls, status badges, drawers/sheets, command palette.
- Do not expose every technical field on cards.
- Do not hide lifecycle truth.
- Do not require a total rewrite.

YOUR OUTPUT
Create a new V3 design direction in this project.

Please produce:
1. Three V3 variants:
   - V3A Dense Operator Cockpit
   - V3B Balanced Kanban + Details Drawer
   - V3C Incident-first Triage Board
2. A recommendation/hybrid direction.
3. Mobile and Desktop artboards for the recommended direction.
4. Details drawer/modal/sheet states.
5. Loading/empty/error/stale/blocked/review state examples.
6. Component structure for handoff:
   - Taskboard shell
   - Lane header
   - Slim task card
   - Status/receipt badge system
   - Stale/blocked/review visual cues
   - Details drawer/modal
   - Empty/loading/error states
   - Mobile layout
   - Desktop layout/right rail
7. A Codex/Frontend-Guru handoff spec:
   - Small implementation slices
   - Data each component needs
   - Which controls are state-changing and need safeguards
   - Next.js/Tailwind implementation notes
8. Acceptance criteria:
   - Operator can identify active, blocked, stale, failed, and review-needed tasks within 10 seconds.
   - Cards are compact and do not expose raw metadata.
   - Details include lifecycle, receipts, dispatch token, worker session, events, history, acceptance criteria, parent/follow-up, result detail, and raw metadata.
   - Visual states do not suggest false progress.
   - Mobile and desktop are both production-ready.

Name the new output clearly as:
"Mission Control Taskboard V3 - Market Ready Operations UI"

