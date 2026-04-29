# V3 Taskboard Promotion Plan

Date: 2026-04-29
Author: Codex App
Scope: Promotion plan only. No code changes performed.

## Goal

Promote the Claude Design V3 Taskboard from additive preview to the primary Mission Control Taskboard only after truth, safety, and operator usability are verified.

Current state:

- Preview route: `/kanban-v3-preview`
- Production route: `/taskboard`
- V3 slices: implemented and child tasks report done
- Promotion: not yet safe

## Promotion Strategy

Use a gated rollout, not a direct replacement.

Recommended path:

1. Keep `/taskboard` as stable production route.
2. Keep `/kanban-v3-preview` as preview route during hardening.
3. Fix truth parity and ControlBar behavior.
4. Run desktop and mobile visual validation.
5. Promote via one small route/navigation change behind a clear rollback path.

## Gate 0: Freeze And Baseline

Owner: Atlas

Actions:

- Confirm no active Pixel/Forge worker is currently editing the same V3 UI files.
- Capture current `/taskboard` and `/kanban-v3-preview` screenshots.
- Record `/api/health`, `/api/board/snapshot`, `/api/board/v3-health`, and `/api/board-consistency`.
- Record git status before implementation resumes.

Acceptance:

- Baseline is in Vault.
- Dirty worktree is acknowledged and ownership is clear.

Stop condition:

- Active worker is editing V3 files.
- Gateway unstable or OOM loop returns.

## Gate 1: Truth Parity

Owner: Forge / SRE-expert

Goal:

Make V3 health, board snapshot, lane counts, and incident strip agree on current live truth.

Required:

- Implement the truth-parity fix spec.
- Add regression tests for archived blocked tasks.
- Prove `/api/board/v3-health` does not count historical blockers as live incidents.

Acceptance:

- Health API and preview board show the same live incident universe.
- No historical blocker flood appears in top chrome or incident strip.

Stop condition:

- Fix requires data migration or lifecycle rewrite.

## Gate 2: ControlBar Wiring

Owner: Pixel / Frontend-Guru

Goal:

Make V3 ControlBar real, not only persisted state.

Required:

- Density changes card/lane spacing and compactness.
- Mode changes board vs triage arrangement.
- Truth rail toggle changes layout behavior.
- URL and localStorage stay in sync.
- Mobile behavior follows spec: no confusing truth rail control if rail is hidden.

Acceptance:

- Operator can switch density, mode, and truth rail and see meaningful layout changes.
- Keyboard shortcuts do not trigger while typing in inputs.
- Naming matches the final chosen spec.

Stop condition:

- ControlBar change causes task data refetch loops or state mutation.

## Gate 3: Drawer Evidence Depth

Owner: Pixel with Forge support

Goal:

Make the details drawer useful for operator decisions without making cards heavy.

Required drawer sections:

- lifecycle
- receipts
- dispatch token
- worker session
- acceptance criteria
- events
- logs/history
- parent/follow-up relationships
- result/blocker
- raw metadata optional

Acceptance:

- Cards remain slim.
- Drawer contains enough evidence to understand a task without opening raw data files.
- Missing optional data renders gracefully.

Stop condition:

- Drawer requires direct mutation actions before action safety is ready.

## Gate 4: Visual QA

Owner: Lens / Spark / Atlas

Goal:

Validate that the board is market-ready on desktop and mobile.

Required:

- Desktop screenshot.
- Mobile screenshot.
- Loading state.
- Empty lane state.
- Error state.
- Blocked/stale/review visual cues.
- Long titles and agent labels.
- Drawer open/close.

Acceptance:

- No overlapping text.
- No false danger emphasis.
- No SaaS marketing look.
- Scan order is clear within 5 seconds.
- Important worker/blocker/review signals are visible without card overload.

Stop condition:

- UI hides active risk or suggests actions that are not wired.

## Gate 5: Safe Promotion

Owner: Atlas with Pixel support

Goal:

Make V3 the operator-facing Taskboard with a small rollback.

Recommended implementation:

- Switch navigation from `/taskboard` to V3 only after Gate 1-4 pass.
- Prefer a feature flag or alias-style route transition.
- Keep old route available for rollback until a full soak passes.

Acceptance:

- Operator can reach V3 as primary Taskboard.
- Old board remains available during rollback window.
- Health, board, and incident truth still match after promotion.

Stop condition:

- Any live state mutation bug.
- Any false incident count after promotion.
- Gateway instability or new OOMs.

## Rollback

Rollback should be simple:

1. Restore navigation to `/taskboard`.
2. Keep `/kanban-v3-preview` available for debugging.
3. Do not delete V3 components during rollback.
4. Record reason and screenshots in Vault.

## What Codex App Can Safely Support

Codex App can support safely and sustainably by doing:

- read-only live audits
- Vault specs and handoff docs
- parity checks
- browser screenshot review
- task note updates
- acceptance criteria refinement
- implementation review after Pixel/Forge patches

Codex App should not be the primary implementer for this rollout while Terminal-Codex, Pixel and Forge are already coordinating inside OpenClaw. The better quality path is to let the OpenClaw agents implement with full runtime context, while Codex App acts as independent reviewer, spec writer and validation layer.

