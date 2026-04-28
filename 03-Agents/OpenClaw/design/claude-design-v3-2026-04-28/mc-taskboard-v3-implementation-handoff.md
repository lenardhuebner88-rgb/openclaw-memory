---
title: Mission Control Taskboard V3 Implementation Handoff
date: 2026-04-28
status: ready-for-planning
source: Claude Design V3
scope: design-to-implementation
---

# Mission Control Taskboard V3 Implementation Handoff

## Source

Claude Design project:

- Project: `Taskboard v2 - Mobile-First Glance-State`
- New tab/result: `V3 Operational Taskboard`
- Target output: `Mission Control Taskboard V3 - Market Ready Operations UI`

Local/export folder:

- `/home/piet/vault/03-Agents/OpenClaw/design/claude-design-v3-2026-04-28/`

## What Claude Produced

New V3 project files observed in Claude Design:

- `mc-v3-foundations.jsx`
- `mc-v3a-cockpit.jsx`
- `mc-v3b-balanced.jsx`
- `mc-v3c-triage.jsx`
- `mc-v3-drawer.jsx`
- `mc-v3-mobile-states.jsx`
- `mc-v3-canvas.jsx`

## Recommended Direction

Use the Claude-recommended hybrid:

- `V3B` as the calm main Taskboard/Kanban chrome.
- `V3C` incident strip only when something is broken or needs immediate review.
- `V3A` right rail as an optional operator/power-user mode.

## Product Rules To Preserve

- 7 canonical lanes: Draft, Ready, Assigned, Active, Review, Done, Failed.
- Slim cards only: title, agent, status, priority/risk, age/staleness, receipt stage, one signal line.
- No raw metadata on cards.
- Details move to drawer/modal/sheet.
- Accepted-without-progress/no-heartbeat must not look like healthy active work.
- Status color must mean something; avoid decorative color.
- Mobile and Desktop must both be production-ready.
- No broad rewrite before mapping existing components and data contracts.

## Implementation Approach

Start with read-only mapping:

1. Compare Claude V3 files to existing Mission Control components.
2. Map V3 concepts to current files:
   - Taskboard shell
   - Lane mapping
   - Task card
   - Task detail modal/drawer
   - Status presentation
   - Runtime truth
   - Responsive layout
3. Identify minimal code slices.
4. Do not edit until active workers and current git status are checked.

## Suggested Slices

1. Lane/status taxonomy audit
2. Slim Task Card prototype behind feature flag or isolated branch
3. Details Drawer content ordering
4. Stale/blocked/review/failed visual taxonomy
5. Desktop board shell and optional right rail
6. Mobile sheet/detail behavior
7. Loading/empty/error states
8. Visual validation and build gate

## Stop Conditions

- Stop if lane mapping creates false state.
- Stop if accepted-without-progress appears as active healthy work.
- Stop if another worker is editing the same Taskboard/Kanban UI files.
- Stop if implementation requires service/data mutation outside UI scope.

## First Task For Terminal-Codex / Frontend-Guru

Read-only planning task:

```text
Read /home/piet/vault/03-Agents/OpenClaw/design/claude-design-v3-2026-04-28/ and this handoff.

Do not implement yet.
Produce a mapping from Claude V3 concepts to existing Mission Control files, with proposed implementation slices, risk, acceptance criteria, and files touched.

Explicitly preserve the no-false-progress rule and the 7-lane taxonomy.
```

