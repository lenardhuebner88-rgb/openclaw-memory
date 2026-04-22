# Sprint-M P1 Pixel Delta Report — 2026-04-20

## Scope
Port Claude Design Taskboard v2 into live Mission Control `/taskboard` with mobile-first hero, single-lane focus, modal affordances, and responsive desktop scale-up.

## Changed files
- `/home/piet/.openclaw/workspace/mission-control/src/components/taskboard/MorningStatusHero.tsx` (new)
- `/home/piet/.openclaw/workspace/mission-control/src/components/taskboard/AdminConfirmDialog.tsx` (new)
- `/home/piet/.openclaw/workspace/mission-control/src/components/taskboard/RetryConfirmDialog.tsx` (new)
- `/home/piet/.openclaw/workspace/mission-control/src/components/taskboard/taskboard-client.tsx`
- `/home/piet/.openclaw/workspace/mission-control/src/components/taskboard/task-card.tsx`
- `/home/piet/.openclaw/workspace/mission-control/src/components/taskboard/task-detail-modal.tsx`
- `/home/piet/.openclaw/workspace/mission-control/src/components/command-palette.tsx`
- `/home/piet/.openclaw/workspace/mission-control/src/app/globals.css`

## What changed
### Hero and layout
- Added `MorningStatusHero` with:
  - big stalled count
  - procedural heartbeat strip
  - urgent card / quiet-lane fallback
  - lane chip row with mobile-friendly hit targets
- Integrated hero at top of taskboard.
- Added mobile single-lane focus state in `taskboard-client.tsx`.
- Preserved multi-lane desktop board on large screens.

### Task card interactions
- Added swipe hint ghosts.
- Right swipe now opens retry for failed/blocked tasks or dispatches when dispatchable.
- Left swipe now routes to admin cleanup confirmation.
- Added long-press menu entries for retry/admin actions.

### Modal/state coverage
- Added `AdminConfirmDialog`.
- Added `RetryConfirmDialog`.
- Updated task detail panel to behave like a bottom sheet on smaller screens and centered/sticky panel on larger screens.
- Extended command palette with direct taskboard navigation shortcuts and create-task trigger.
- Added quiet-lane empty state.

### Token merge
- Added panel, accent, spacing, shadow, and ghost-breathe tokens/animation into `globals.css`.
- Kept dark-only palette with violet brand and amber reserved for stalled/warning surfaces.

## Verification
### Build
- `npm run build` → success
- `npm run typecheck` → success

### Restart and health
- `mc-restart-safe 120 pixel-sprint-m-p1-deploy` → success
- `GET http://127.0.0.1:3000/api/health` → `200`
- `GET http://127.0.0.1:3000/taskboard` → `200`

### Viewport screenshots
Saved under:
- `/home/piet/.openclaw/workspace/mission-control/tmp-taskboard-v2/taskboard-mobile.png`
- `/home/piet/.openclaw/workspace/mission-control/tmp-taskboard-v2/taskboard-tablet.png`
- `/home/piet/.openclaw/workspace/mission-control/tmp-taskboard-v2/taskboard-desktop.png`

Viewport capture results:
- Mobile `390x844` → hero present, single-lane focus active
- Tablet `768x1024` → hero present, responsive scale-up active
- Desktop `1440x900` → hero present, multi-lane board active

## Prototype deltas
- Reused existing production board/state plumbing instead of cloning prototype structure.
- Command palette kept existing search/result model, only visual shell + quick actions were added.
- Task detail interaction re-used existing sheet/panel logic rather than replacing with a fully separate desktop modal tree.

## Notes
- The board task had auto-failed during the run because of the no-progress monitor and was recovered via retry before final verification.
- Verification screenshots were produced from the live local app after restart.
