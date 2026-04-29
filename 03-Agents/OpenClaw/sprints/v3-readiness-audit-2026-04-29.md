# Mission Control V3 Readiness Audit

Date: 2026-04-29
Author: Codex App
Scope: Read-only audit for Claude Design V3 Taskboard implementation status.

## Verdict

Status: NOT READY FOR PRODUCTION PROMOTION YET.

V3 is implemented far beyond design-only status and exists as a live additive preview at `/kanban-v3-preview`. The slice train appears complete in the task hierarchy and the Gate 1 evidence pack reports PASS. However, promotion to the primary Taskboard should wait until three gaps are closed:

1. Truth parity: `/api/board/v3-health` currently reports high incident counts that do not match the live board snapshot or `/api/health`.
2. ControlBar behavior: state persists and URL-syncs, but density/mode/truth controls are not yet fully consumed by the layout.
3. Drawer depth: the drawer exists, but it is still a simplified inspect surface rather than the full operational detail model from the Claude Design brief.

No UI code was changed by this audit.

## Evidence Checked

- Vault design directory: `/home/piet/vault/03-Agents/OpenClaw/design/claude-design-v3-2026-04-28/`
- Canonical source export: `/home/piet/vault/03-Agents/OpenClaw/design/claude-design-v3-2026-04-28/source-export-final-2026-04-28-2213/`
- Sprint handoff: `/home/piet/vault/03-Agents/OpenClaw/sprints/mc-taskboard-v3-implementation-handoff.md`
- Gate 1 evidence pack: `/home/piet/vault/03-Agents/OpenClaw/sprints/v3-gate1-production-readiness-evidence-pack.md`
- Gate 2 result: `/home/piet/vault/03-Agents/OpenClaw/sprints/v3-gate2-pixel-implementation-result.md`
- V3 handover state: `/home/piet/.openclaw/state/v3-atlas-handover.json`
- Live routes checked:
  - `/api/health`
  - `/api/board-consistency`
  - `/api/board/snapshot`
  - `/api/board/v3-health`
  - `/kanban-v3-preview`
  - `/taskboard`

## Current Implementation State

V3 is present as an additive preview route:

- `/kanban-v3-preview` returns HTTP 200.
- `/taskboard` returns HTTP 200 but still represents the current production Taskboard path.
- Navigation still points to `/taskboard`, not to `/kanban-v3-preview`.
- The preview route uses `/api/board/snapshot` and maps live tasks through the V3 adapter.

Relevant files present in the Mission Control repo:

- `/home/piet/.openclaw/workspace/mission-control/src/app/kanban-v3-preview/page.tsx`
- `/home/piet/.openclaw/workspace/mission-control/src/app/api/board/snapshot/route.ts`
- `/home/piet/.openclaw/workspace/mission-control/src/app/api/board/v3-health/route.ts`
- `/home/piet/.openclaw/workspace/mission-control/src/lib/v3/status-derivation.ts`
- `/home/piet/.openclaw/workspace/mission-control/src/lib/v3/lane-mapping.ts`
- `/home/piet/.openclaw/workspace/mission-control/src/lib/v3/task-adapter.ts`
- `/home/piet/.openclaw/workspace/mission-control/src/lib/v3/health-aggregation.ts`
- `/home/piet/.openclaw/workspace/mission-control/src/components/v3/V3FinalDesktop.tsx`
- `/home/piet/.openclaw/workspace/mission-control/src/components/v3/V3DetailsDrawer.tsx`
- `/home/piet/.openclaw/workspace/mission-control/src/components/v3/V3ActionBar.tsx`

## Slice Status

The V3 master handover reports all 20 child slices done. The implemented commits include foundations, primitives, card, lanes, preview shell, health API, incident strip, next-action derive, details drawer, mock state actions, mobile, ControlBar and hardening.

Operational interpretation:

- Design assets: READY.
- Typed V3 domain model: READY.
- Additive preview route: READY.
- Live task snapshot wiring: PARTIAL READY.
- Status derivation: READY but needs parity validation against current live data.
- Incident/health aggregation: BLOCKED by truth-parity issue.
- Task card shell: READY.
- Lane states: READY.
- Details drawer: PARTIAL READY.
- State actions: SAFE MOCK ONLY, not live mutation-ready.
- Mobile surface: IMPLEMENTED, needs current screenshot validation before promotion.
- Primary route promotion: NOT READY.

## Key Blockers

### 1. Truth Parity

Observed mismatch:

- `/api/health` is OK.
- `/api/board/snapshot` shows the current live task surface.
- `/api/board/v3-health` reports a large blocked/incident count, for example `blocked: 74`, `incidentCount: 74`, `hasIncident: true`.

This looks like historical or archived blocked tasks leaking into the V3 health rollup. A market-ready operations UI must not show stale historical incidents as live current danger.

### 2. ControlBar Drift

The ControlBar state is implemented and persists via localStorage/URL, but the shell does not yet consume the controls deeply enough:

- Density does not fully reshape downstream card/lane density.
- Mode does not fully switch board vs triage layout.
- Truth rail visibility is not fully applied as a layout decision.
- Naming drift exists versus the Claude Design output:
  - implemented: `compact|comfortable`
  - design: `comfy|dense`
  - implemented: `board|list`
  - design: `board|triage`

This is not a blocker for preview, but it is a blocker for declaring V3 feature-complete.

### 3. Drawer Depth

The drawer exists and is safe to inspect, but it is still simplified. The Claude Design target asks for a richer operational drawer:

- lifecycle
- receipts
- dispatch token
- worker session
- acceptance criteria
- events
- logs/history
- parent/follow-up relations
- raw metadata optional

Current drawer sections are useful, but not yet the full operator-grade task evidence surface.

## Worktree Caution

The Mission Control worktree is dirty and contains many unrelated live changes, including data files and non-V3 code. This audit intentionally did not modify any repo code. Any implementation follow-up should start with a clean owner handoff and should not mix V3 promotion with unrelated operational fixes.

## Recommendation

Continue with a controlled hardening pass before promotion:

1. Fix truth parity first.
2. Wire ControlBar state into actual layout behavior.
3. Expand drawer data only where the current APIs can support it safely.
4. Re-run browser validation on desktop and mobile.
5. Promote via feature flag or route switch only after a final parity gate.

The safest role for Codex App here is planning, review, spec writing, parity analysis, and validation handoff. Pixel/Forge should own implementation inside OpenClaw because they have local runtime context, agent coordination, and existing ownership of the V3 slice train.

