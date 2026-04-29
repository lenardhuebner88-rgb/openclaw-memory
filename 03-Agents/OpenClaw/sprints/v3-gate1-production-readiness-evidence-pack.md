---
title: V3 Gate 1 Production-Readiness Evidence Pack
date: 2026-04-29
status: pass
scope: v3-gate1-evidence
---

# V3 Gate 1 Production-Readiness Evidence Pack

## Goal

Certify that the Mission Control V3 preview is production-ready for Gate 1 browser parity without relying on mock/sample data and without hidden asset-pipeline failures.

Gate 1 covers:
- Mission Control runtime health.
- Current build/assets served by the live runtime.
- V3 preview route hydration.
- Live board snapshot parity.
- Drawer/live-route behavior.
- Absence of sample/fallback data.
- Browser telemetry classification.

## Non-Scope

- No UI or feature changes.
- No legacy `/kanban`, `/taskboard`, or `/dashboard` rewrite.
- No Gateway, model-routing, cron/config changes.
- No build/restart unless explicitly approved for runtime stabilization.
- No worker dispatch as part of this evidence pack.

## Tested Endpoints

Base URL: `http://127.0.0.1:3000`

Required read-only checks:

```bash
curl -fsS http://127.0.0.1:3000/api/health | jq '{status,severity,recoveryLoad:.metrics.recoveryLoad,attentionCount:.metrics.attentionCount,issueCount:.checks.board.issueCount,consistencyIssues:.checks.dispatch.consistencyIssues}'
curl -fsS http://127.0.0.1:3000/api/board/snapshot | jq '{view,returnedTasks:(.tasks|length),summary}'
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:3000/kanban-v3-preview
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:3000/kanban-v3-preview/<live-task-id>
curl -sSI http://127.0.0.1:3000/sw.js | head
```

Expected:
- `/api/health`: `status=ok`, `severity=ok`, `recoveryLoad=0`, `attentionCount=0`, `issueCount=0`, `consistencyIssues=0`.
- `/api/board/snapshot`: HTTP 200 and non-empty live task subset.
- `/kanban-v3-preview`: HTTP 200.
- `/kanban-v3-preview/<live-task-id>`: HTTP 200.
- `/sw.js`: HTTP 200.

## Playwright Rerun Script

Canonical final rerun artifact used for Gate 1:

- Script: `/tmp/v3-gate1-classified.cjs`
- Latest PASS output: `/tmp/v3-gate1-classified-20260429-134445.json`

If the temp script is gone, recreate equivalent logic with Playwright/Chromium:

```bash
node /tmp/v3-gate1-classified.cjs | tee /tmp/v3-gate1-classified-$(date +%Y%m%d-%H%M%S).json
```

The script must:
1. Fetch `/api/health` and `/api/board/snapshot`.
2. Open `/kanban-v3-preview` in Chromium.
3. Wait for hydration/network idle.
4. Confirm snapshot task titles are visible.
5. Confirm sample IDs `v3-1..v3-6` and sample text `Alerts collapse UI` are absent.
6. Open a live task drawer and verify live title/id are shown.
7. Navigate to `/kanban-v3-preview/<live-task-id>` and verify live data.
8. Navigate to `/kanban-v3-preview/v3-1` and verify no sample task renders.
9. Collect console errors, failed requests, >=400 responses, and classify benign aborts.

## PASS Criteria

Gate 1 passes only if all are true:

- Build/runtime state is clean when checked.
- System health OK:
  - `recoveryLoad=0`
  - `attentionCount=0`
  - `issueCount=0`
  - `consistencyIssues=0`
- `/kanban-v3-preview` returns HTTP 200.
- V3 preview hydrates.
- `live_cards_visible > 0`.
- Visible live cards match `/api/board/snapshot` or a documented V3 subset.
- `sample_ids_present=[]` for `v3-1..v3-6`.
- `sample_text_present=false` for `Alerts collapse UI`.
- Drawer uses live task data.
- `/kanban-v3-preview/<live-task-id>` renders the live task.
- `/kanban-v3-preview/v3-1` renders no sample task.
- Counts match snapshot/subset.
- `consoleErrors=[]`.
- No blocking 400/404/500 responses.
- No blocking network failures.

## Telemetry Classification

Blocking failures:
- Any current-build `/_next/static/...` JS/CSS request with 400/404/500.
- Any `/sw.js` 404.
- Any console error indicating failed resource load, hydration failure, uncaught exception, or app crash.
- Any V3 route returning >=400.
- Any snapshot/health endpoint failure.

Known non-blocking telemetry, if all UI and endpoint checks pass:
- Navigation-time `_rsc` `net::ERR_ABORTED` during Playwright route changes.
- Navigation-time `/sw.js` `HEAD net::ERR_ABORTED` caused by component unmount/route transition, **only if** direct `HEAD /sw.js` returns 200 and no console error is emitted.

Rule: classify aborts as non-blocking only when there are no associated 4xx/5xx responses and no UI impact.

## Last Known PASS Evidence

Date/time: 2026-04-29 13:44 CEST final classified rerun.

Result:
- Playwright/Chromium completed.
- `/kanban-v3-preview`: 200.
- Hydrated: yes.
- Live cards visible: 3.
- Live task IDs:
  - `e40a90c9-238f-4b68-aba3-a5123f54f913`
  - `82c4076f-878e-4bf9-89e4-b36e168f57fa`
  - `c92fb95f-9d6c-491f-aebc-c59557f74e1d`
- Sample IDs present: none.
- Sample text present: no.
- Drawer live data: yes.
- Live route OK: yes.
- Sample route behavior: no sample task rendered.
- Counts match: yes.
- Console errors: none.
- Bad responses: none.
- Blocking failures: none.
- System health: OK.

Supporting files:
- Working log: `/home/piet/.openclaw/workspace/memory/working/2026-04-29.md`
- Sprint closure: `/home/piet/vault/03-Agents/OpenClaw/sprints/mc-taskboard-v3-implementation-handoff.md`
- Build log: `/tmp/mission-control-v3-gate1-build-20260429-133041.log`
- Final rerun JSON: `/tmp/v3-gate1-classified-20260429-134445.json`

## Rerun Procedure

1. Quiet-state check: ensure no active build/Playwright process is already running.
2. Read-only health and endpoint checks.
3. Confirm `/sw.js` and current static assets return 200.
4. Run the Playwright classified rerun once.
5. Inspect output:
   - `result` must be `PASS`.
   - `consoleErrors`, `badResponses`, `blockingFailures` must be empty.
   - Benign aborts may exist only as classified above.
6. Record result in working memory and sprint doc if Gate status changes.

## Troubleshooting / Rollback Notes

If `/sw.js` returns 404:
- Confirm `mission-control/public/sw.js` exists.
- Confirm Mission Control runtime started after the build that includes `public/sw.js`.
- Do not claim Gate PASS until live `/sw.js` is 200.

If current chunks return 400/404:
- Treat as asset-pipeline failure.
- Do not accept browser parity PASS.
- Stabilize build/runtime first.

If build is required:
- Use canonical `npm run build` only.
- Avoid build while Mission Control is serving old live chunks unless explicitly approved.
- Restart only via established safe wrapper (`mc-restart-safe`) after build PASS.

Rollback for SW placeholder:
- Revert mission-control commit `b6775a4` only if SW registration is intentionally removed or replaced by a better PWA strategy.
