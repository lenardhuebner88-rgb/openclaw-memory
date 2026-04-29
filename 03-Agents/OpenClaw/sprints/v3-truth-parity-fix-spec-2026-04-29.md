# V3 Truth Parity Fix Spec

Date: 2026-04-29
Author: Codex App
Scope: Specification only. No code changes performed.

## Problem

The V3 preview and the live Mission Control health surfaces currently risk telling different stories.

Observed live pattern:

- `/api/health` reports OK.
- `/api/board/snapshot` returns the current live task set used by the preview.
- `/api/board/v3-health` reports high incident counts, for example `blocked: 74`, `incidentCount: 74`, `hasIncident: true`.

The likely cause is that V3 health aggregation is counting historical, archived, or non-live tasks as active operational incidents. This can make the V3 Taskboard look dangerous even when the current board is stable.

## Goal

Make V3 truth signals derive from one consistent live task universe.

For the operator, these surfaces must agree:

- top chrome health
- incident strip
- lane counts
- task cards
- drawer status
- `/api/board/v3-health`
- `/api/board/snapshot`
- Mission Control global health summary

Historical incidents may still be visible, but they must be clearly labelled as historical and must not drive the live incident count.

## Canonical Definitions

### Live Task

A task is live if it is currently actionable or currently relevant for operation:

- draft
- ready
- queued
- assigned
- dispatched
- accepted
- in-progress
- review-needed
- blocked
- failed requiring operator attention

### Closed Task

A task is closed if it is done, cancelled, superseded, archived, or terminal without required action.

Closed tasks may appear in history or closed footer, but they must not inflate active incident counts.

### Active Incident

A task should count as an active incident only if:

1. It is in the live task set.
2. Its canonical V3 status is blocked, failed, stale, overdue, or review-needed with operator action required.
3. It is not archived, historical-only, completed, cancelled, or superseded.

## Required Alignment

The V3 health route should not independently invent its own task universe. It should reuse the same source and filtering logic as the preview board where practical.

Preferred alignment:

1. Load the same raw board task source used by `/api/board/snapshot`.
2. Convert through the same V3 adapter.
3. Classify through the same V3 status and lane mapping.
4. Aggregate incidents from the resulting live V3 tasks.

Relevant files:

- `/home/piet/.openclaw/workspace/mission-control/src/app/api/board/snapshot/route.ts`
- `/home/piet/.openclaw/workspace/mission-control/src/app/api/board/v3-health/route.ts`
- `/home/piet/.openclaw/workspace/mission-control/src/lib/v3/task-adapter.ts`
- `/home/piet/.openclaw/workspace/mission-control/src/lib/v3/status-derivation.ts`
- `/home/piet/.openclaw/workspace/mission-control/src/lib/v3/lane-mapping.ts`
- `/home/piet/.openclaw/workspace/mission-control/src/lib/v3/health-aggregation.ts`

## Proposed Implementation Shape

No implementation was done by Codex App. This is the recommended shape for Forge/Pixel:

1. Add a shared V3 live-task filter.
   - Input: raw task or adapted V3 task.
   - Output: include/exclude plus reason.
   - Exclude archived, done, cancelled, superseded and historical-only records from live incident counts.

2. Make `/api/board/v3-health` aggregate from the same adapted live task list as the preview route.
   - If direct reuse is too coupled, extract a small helper used by both routes.

3. Split response fields:
   - `liveIncidentCount`
   - `historicalIncidentCount`
   - `blockedLive`
   - `blockedHistorical`
   - `hasLiveIncident`

4. Keep backward-compatible fields only if needed:
   - `incidentCount` should mean live incidents.
   - If old total is still needed, call it `totalHistoricalIncidents` or similar.

5. Add fixture tests.
   - Active blocked task counts.
   - Archived blocked task does not count as live.
   - Completed failed task does not count as live unless it requires review.
   - Draft and ready tasks do not count as incidents unless explicitly stale/blocked.
   - `/api/board/snapshot` task count and `/api/board/v3-health` live universe match.

## Acceptance Criteria

Pass only if all are true:

1. `/api/board/v3-health` no longer reports historical blocked tasks as live incidents.
2. IncidentStrip and health API agree on current live incident count.
3. Board lane counts and V3 health are derived from the same status/lane logic.
4. Historical blocked/failed tasks remain accessible in history but do not drive live danger UI.
5. A regression test covers archived blocked tasks.
6. A browser validation screenshot shows the V3 preview without false incident overload.
7. No task state mutation is required to validate the fix.

## Stop Conditions

Stop and report if:

- Fix requires changing task lifecycle semantics.
- Fix would hide genuinely active blocked or failed tasks.
- The current data source cannot distinguish archived from live tasks.
- Any migration of `tasks.json` or event history appears necessary.

## Recommended Owner

Primary: Forge / SRE-expert

Reason: This is not a visual-only issue. It is a data truth and API aggregation issue. Pixel should only consume the corrected contract after Forge defines it.

Pixel follow-up:

- Rename visual labels only after the health contract is stable.
- Do not compensate in the UI by locally hiding counts from the API.

