# Mission Control Next.js Build Hang — Problem Description

**Date:** 2026-05-05 23:24 CEST  
**Owner/operator:** Piet  
**Assistant:** Hermes  
**Scope:** Mission Control workspace only: `/home/piet/.openclaw/workspace/mission-control`  
**Mode:** Keep MC online; no deploy/restart until build root cause is understood.

---

## Problem

Mission Control is live and responding, but the current workspace cannot produce a fresh Next.js production build. Multiple isolated `next build` attempts hang indefinitely at:

```text
Creating an optimized production build ...
```

Next diagnostics consistently report the build stage as:

```json
{
  "buildStage": "compile",
  "buildOptions": {
    "useBuildWorker": "false"
  }
}
```

The original goal was to deploy Fix 1 of the OpenClaw observability work: make MC `/api/ops/openclaw/model-runtime-failures` detect OpenClaw runtime/fallback events instead of returning false-green empty counts.

---

## Current Live State

As of 2026-05-05 23:21–23:24 CEST:

- `mission-control.service` is **active**.
- `http://127.0.0.1:3000/api/health` returns HTTP `200`.
- MC health body reports `status=degraded`, `severity=warning` because of taskboard/execution state, not because MC is offline.
- Existing production build remains intact:
  - `.next/BUILD_ID`: `j7LD336O1PHS76Wph9yIq`
- No deploy or Mission Control restart was performed during the build-hang investigation.
- A stale `.openclaw/build.lock` was found and removed after backup:
  - stale PID: `2268333`, `/proc/2268333` absent
  - backup: `/home/piet/.openclaw/workspace/mission-control/backups/mc-online-recovery-20260505T205939Z/build.lock.bak`

---

## Changed Workspace Files

Current working tree changes in `/home/piet/.openclaw/workspace/mission-control`:

```text
M  src/lib/openclaw-readonly-diagnostics.ts
M  src/app/api/admin/tasks/[id]/sprint-outcome-backfill/route.ts
?? tests/openclaw-model-runtime-failures-regression.test.ts
?? backups/
?? reports/visual-diff/
```

### Intended Observability Fix

`src/lib/openclaw-readonly-diagnostics.ts` was changed to:

- classify additional runtime/fallback event types:
  - `embedded_run_timeout`
  - `embedded_run_failover_decision`
  - `model_fallback_candidate_failed`
  - `model_fallback_candidate_succeeded`
- parse `journalctl --output=json`
- increase journal command timeout/buffer
- parse all records first and apply `limit` after filtering relevant events, avoiding false-green from noisy recent logs
- expose extracted fields such as `requestedModel`, `candidateModel`, `nextModel`, `runId`

### TypeScript Fix Needed For Existing Build Blocker

`src/app/api/admin/tasks/[id]/sprint-outcome-backfill/route.ts` was minimally changed:

```diff
- lastExecutionEvent: 'admin-sprint-outcome-backfill'
+ lastExecutionEvent: 'update'
```

Reason: `npm run typecheck` failed with TS2322 because `'admin-sprint-outcome-backfill'` is not an allowed `lastExecutionEvent` literal. Audit context remains preserved in the update metadata:

```ts
{ source: 'admin-backfill', actor, action: 'sprint-outcome-backfill' }
```

### Regression Test Added

`tests/openclaw-model-runtime-failures-regression.test.ts` verifies:

- the four new runtime/fallback classes are recognized
- journal parsing applies filter-before-limit

---

## Backups / Snapshots

Created before or during investigation:

```text
backups/hermes-observability-fix-20260505T194836Z/openclaw-readonly-diagnostics.ts.bak
backups/hermes-observability-fix-20260505T200106Z/sprint-outcome-backfill-route.ts.bak
backups/mc-online-recovery-20260505T205939Z/build.lock.bak
backups/mc-online-recovery-20260505T210256Z/current.patch
backups/mc-online-recovery-20260505T210256Z/openclaw-readonly-diagnostics.current.ts.bak
backups/mc-online-recovery-20260505T210256Z/sprint-outcome-backfill-route.current.ts.bak
backups/mc-online-recovery-20260505T210256Z/openclaw-model-runtime-failures-regression.test.ts.bak
```

Note: `.ts` snapshots in `backups/mc-online-recovery-20260505T210256Z/` were renamed to `.ts.bak` because raw `.ts` files under `backups/` were picked up by `tsconfig` and polluted typecheck.

---

## Verification Already Passing

Before build attempts:

```text
npm run typecheck → OK
npx vitest run tests/openclaw-model-runtime-failures-regression.test.ts --reporter=dot → 2 tests passed
```

After restoring the current intended patch from snapshot:

```text
npm run typecheck → OK
```

---

## Build Attempts / Evidence

All builds used isolated dist directories and did **not** replace productive `.next`.

### Attempt 1 — Current Observability Patch

Command shape:

```bash
FORCE_BUILD=1 NEXT_DIST_DIR=.next-hermes-observability-build BUILD_WAIT_FOR_ACTIVE_LOCK=1 npm run build
```

Result:

- timed out after ~600s
- no `BUILD_ID`
- build dir about `960K`
- trace shows many module compilation events but no static generation

### Attempt 2 — Raw Next Build

Command shape:

```bash
NEXT_TELEMETRY_DISABLED=1 NEXT_DIST_DIR=.next-hermes-raw-diagnostic NEXT_BUILD_CPUS=1 NODE_OPTIONS='--max-old-space-size=4096' timeout 300s node_modules/.bin/next build
```

Result:

- timeout
- no `BUILD_ID`
- diagnostics: `buildStage=compile`

### Attempt 3 — Cache-Copied Build

Command shape:

```bash
rm -rf .next-hermes-cache-diagnostic
mkdir -p .next-hermes-cache-diagnostic
cp -a .next/cache .next-hermes-cache-diagnostic/cache
NEXT_TELEMETRY_DISABLED=1 NEXT_DIST_DIR=.next-hermes-cache-diagnostic NEXT_BUILD_CPUS=2 NODE_OPTIONS='--max-old-space-size=4096' timeout 540s node_modules/.bin/next build
```

Result:

- reached about `457M`, mostly copied webpack cache
- no `BUILD_ID`
- no final manifests (`app-build-manifest.json`, `build-manifest.json`, `routes-manifest.json`, `required-server-files.json` absent)
- diagnostics: `buildStage=compile`

### Attempt 4 — A/B: Diagnostics Rollback, Sprint Fix Retained

`src/lib/openclaw-readonly-diagnostics.ts` restored from backup while keeping sprint TS fix.

Result:

- `npm run typecheck → OK`
- isolated build still timed out
- no `BUILD_ID`
- diagnostics: `buildStage=compile`

Interpretation: build hang is not uniquely caused by the new diagnostics code.

### Attempt 5 — A/B: Diagnostics Rollback + Sprint Rollback

Both touched source files restored from backups.

Result:

- typecheck fails again with known TS2322 in sprint route
- build still hangs in `compile`
- no `BUILD_ID`

Interpretation: build hang is not explained solely by the current patch. The old sprint route also contains a real type error, but Next build is configured with `typescript.ignoreBuildErrors=true`, so the compile hang persists independently.

### Attempt 6 — Full `.next` Copy To Isolated Dist

Existing `.next` copied to `.next-hermes-fullcopy-current`, then `next build` run against that isolated dist.

Result:

- interrupted by session/context cut before normal timeout handling
- residual build process was later detected and stopped
- no `BUILD_ID` in isolated dir after build start
- diagnostics: `buildStage=compile`

---

## Current Root-Cause Assessment

Strongest current conclusion:

> The fresh Next.js production build hangs in the Webpack/Next compile phase before static generation and before final manifests/BUILD_ID are written. This appears broader than the new OpenClaw diagnostics patch, because rollback variants still hang.

Evidence against other causes:

- Not a TypeScript-check-only issue: `npm run typecheck` passes for intended current patch.
- Not a test failure: targeted vitest regression passed.
- Not MC offline: MC service and health endpoint are live.
- Not OOM observed during earlier checks: memory was available and no kernel OOM/killed evidence was found.
- Not just cold cache: copying `.next/cache` let the directory reach ~457M but still did not finish compile.

Likely investigation areas:

1. Next.js 15.5.15 / Webpack compile hang in this workspace.
2. Interaction of `NEXT_DIST_DIR` isolated builds with existing cache/output state.
3. `next.config.ts` experimental setting:
   ```ts
   experimental: { cpus: Number(process.env.NEXT_BUILD_CPUS) || 2 }
   ```
4. Build wrapper / lock / dist-dir behavior, especially when MC is already running.
5. A route or entry in `src/app` causing Webpack compile to stall, independent of the recent diagnostics patch.

---

## Recommended Next Safe Plan

Keep MC online and do not restart/deploy until build completes.

1. Verify no background build processes and no stale build lock:
   ```bash
   pgrep -af 'node_modules/.bin/next build|next build|NEXT_DIST_DIR=.next-hermes' || true
   [ -f .openclaw/build.lock ] && cat .openclaw/build.lock || echo no-lock
   ```

2. Reconfirm MC health:
   ```bash
   systemctl --user is-active mission-control.service
   curl -sS --max-time 5 http://127.0.0.1:3000/api/health
   ```

3. Stop doing full repeated build attempts until narrower instrumentation exists.

4. Add temporary build instrumentation only in isolated diagnostics path, or run Next with debug/env tracing if available, to identify the exact compiler/entrypoint stall.

5. Once build root cause is fixed:
   ```bash
   npm run typecheck
   npx vitest run tests/openclaw-model-runtime-failures-regression.test.ts --reporter=dot
   NEXT_DIST_DIR=<isolated-final-dir> npm run build
   ```

6. Only after successful build with `BUILD_ID`, plan a controlled MC restart/deploy with explicit Piet approval.

7. Live smoke after deployment:
   ```bash
   curl -sS --max-time 10 'http://127.0.0.1:3000/api/ops/openclaw/model-runtime-failures?window=6h&limit=200'
   ```

Expected post-deploy outcome: false-green `counts={}` is replaced by visible runtime/fallback event classes where present.

---

## Short Operator Summary

MC is online. The observability fix is coded and typechecked, but not deployed because fresh Next production builds hang in `compile`. A/B rollback tests show the hang is broader than the diagnostics patch. Productive `.next` remains intact. Next work should focus on the Next/Webpack compile hang, not on restarting MC.
