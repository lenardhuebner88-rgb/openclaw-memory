---
title: OpenClaw Embedded-Run Timeout / Lane-Budget RCA
created: 2026-05-03T21:52:30Z
agent: Hermes
status: final
scope: openclaw-incident
for_atlas:
  status: actionable
  affected_agents: [main, sre-expert]
  affected_files:
    - /home/piet/.npm-global/lib/node_modules/openclaw/dist/pi-embedded-rWtLEwl7.js
    - /home/piet/.npm-global/lib/node_modules/openclaw/dist/diagnostic-oEUVZa4J.js
    - /home/piet/.openclaw/scripts/check-embedded-run-lane-timeout-patch.py
    - /home/piet/.openclaw/agents/main/sessions/sessions.json
    - /home/piet/.openclaw/agents/sre-expert/sessions/sessions.json
  recommended_next_action: "Keep monitoring post-23:51 logs; upstream or persist the dist patch before the next OpenClaw update; treat future gpt-5.5 300s timeouts as model/runtime latency unless they again produce 330s lane aborts."
  risk: "The 330s lane-abort root cause is fixed in the installed dist, but primary gpt-5.5 attempts can still hit the 300s model timeout; fallback now survives. Dist patch is not update-persistent."
  evidence_files:
    - /home/piet/vault/03-Agents/Hermes/plans/openclaw-embedded-run-timeout-fix-plan-2026-05-03.md
    - /home/piet/vault/03-Agents/Hermes/receipts/codex-embedded-run-timeout-audit-2026-05-03.md
---

# OpenClaw Embedded-Run Timeout / Lane-Budget RCA

## Summary

User-visible symptom was that OpenClaw/Atlas/Forge Discord turns could look stuck or go silent after Codex app-server timeouts. The root cause for the **wedging / aborted recovery path** was a too-small outer command-lane budget: the inner Codex attempt was allowed ~300s, while the outer embedded command lane was capped at `timeoutMs + 30000` (=330s). That left only ~30s for timeout-compaction and fallback/retry, so recovery was killed after it had started.

The installed fix increases embedded lane grace to 10 minutes and adds a delayed active-run abort/drain safety valve at 15 minutes. Post-fix evidence confirms the original `Command lane "main" task timed out after 330000ms` failure mode no longer appears. A later real Atlas turn still hit the normal 300s `gpt-5.5` app-server timeout, but the fallback to `gpt-5.4-mini` completed successfully; this is important because it proves the lane-budget root cause was removed while also showing that model-level 300s timeouts remain possible.

## Timeline

| Time UTC | Local | Event | Evidence |
|---|---:|---|---|
| 21:19:12 | 23:19:12 | Timeout compaction succeeded after a `gpt-5.5` timeout and attempted retry. | Earlier journal evidence in plan: `timeout-compaction ... succeeded; retrying prompt`. |
| 21:19:26 | 23:19:26 | Outer lane killed recovery after 330s. | Earlier journal evidence: `Command lane "main" task timed out after 330000ms`. |
| 21:31:36 | 23:31:36 | Patch/backup sequence began. | Backups under `.bak-20260503T213136Z-*`. |
| 21:36:08 | 23:36:08 | Delayed active embedded recovery patch backed up and applied. | Backup `diagnostic-oEUVZa4J.js.bak-20260503T213608Z-active-embedded-recovery`. |
| 21:37:06 | 23:37:06 | Gateway restarted and became ready. | Journal: `[gateway] ready`; PID `343560`. |
| 21:37-21:41 | 23:37-23:41 | Direct and visible Discord smokes passed for SRE and Atlas. | Markers `HERMES_VISIBLE_SRE_20260503T214039Z`, `HERMES_VISIBLE_ATLAS_20260503T214039Z`; direct `*_FINAL_OK` replies. |
| 21:45:52 | 23:45:52 | Real Atlas Discord turn started on `gpt-5.5`. | Trajectory `c398bead...`: `session.started`, model `gpt-5.5`. |
| 21:48:28 | 23:48:28 | Stuck warning fired while active run was still real/active. | Journal: `stuck session ... age=138s`, `recovery skipped: reason=active_embedded_run action=observe_only`. |
| 21:50:52 | 23:50:52 | `gpt-5.5` inner attempt timed out at ~300s. | Journal: `codex app-server attempt timed out`; trajectory: `timedOut=True`, `promptError='codex app-server attempt timed out'`. |
| 21:50:54 | 23:50:54 | Fallback attempt began on `gpt-5.4-mini`. | Trajectory `c398bead...`: `session.started`, model `gpt-5.4-mini`. |
| 21:51:52 | 23:51:52 | Fallback succeeded. | Trajectory: `model.completed`, `timedOut=False`, output `1007`; journal: `candidate_succeeded ... candidate=openai/gpt-5.4-mini`. |
| 21:52:26 | 23:52:26 | Post-check clean after fallback completion. | Session-health: `suspectedStuck=0`, `withErrors=0`; post-23:51:52 journal counts all timeout/stuck patterns zero. |

## Confirmed Facts

- Installed OpenClaw Gateway is live: PID `343560`, `ActiveState=active`, `/health` returns `{"ok":true,"status":"live"}` at `2026-05-03T21:50:47Z`.
- Patch invariant is present:
  - `pi-embedded-rWtLEwl7.js:1437` has `const EMBEDDED_RUN_LANE_TIMEOUT_GRACE_MS = 10 * 60 * 1e3;`.
  - `resolveEmbeddedRunLaneTimeoutMs()` still returns `timeoutMs + grace`.
  - checker output: `outer_ms=900000`, `outer_minutes=15.0`.
- Delayed active-run abort safety is present:
  - `diagnostic-oEUVZa4J.js:347` has `ACTIVE_EMBEDDED_RUN_ABORT_ELIGIBLE_MS = 15 * 60 * 1e3`.
  - `recoverStuckSession` receives `allowActiveAbort: ageMs >= ACTIVE_EMBEDDED_RUN_ABORT_ELIGIBLE_MS`.
- Current sessions are not stuck:
  - `mc_openclaw_session_health(active=20)`: `total=4`, `suspectedStuck=0`, `withErrors=0`.
- After the successful fallback at `23:51:52`, journal scan shows:
  - `CommandLaneTaskTimeout=0`
  - `Command lane "main" task timed out after 330000ms=0`
  - `codex app-server attempt timed out=0`
  - `stuck session=0`
  - `recovery skipped=0`
  - `active_embedded_run=0`
  - `FailoverError=0`
- The post-fix real Atlas turn proves fallback survival:
  - `gpt-5.5` timed out after ~300s.
  - Fallback `gpt-5.4-mini` started ~2s later.
  - Fallback completed successfully ~58s later.
  - Session store records `abortedLastRun=false`, `modelOverride=gpt-5.4-mini`, `outputTokens=1007`, `lastErrorClass=null`.

## Root Cause

### Primary root cause for the wedge / recovery cut-off

The embedded-run outer lane timeout was incorrectly budgeted as:

```text
outer lane timeout = inner attempt timeout + 30s
                   = 300s + 30s
                   = 330s
```

This was too close to the inner model-attempt timeout. When the inner Codex app-server attempt consumed ~300s, the system had only ~30s left for timeout-compaction, fallback selection, retry startup, cleanup, and reply delivery. Logs showed timeout-compaction succeeded, then the outer command-lane timeout killed the job shortly after.

### Secondary contributors

- High-context / long-running Discord turns can still make `gpt-5.5` hit the 300s Codex app-server timeout.
- `active_embedded_run` is a protective state while a real run is ongoing; it correctly prevents early hard reset, but without a delayed abort/drain threshold it can become a stale recovery blocker.
- Bloated/stale Discord sessions and persistent model overrides made failures more likely and harder to recover from.

## Rejected / Refined Hypotheses

- **"The problem is fully gone because `/health` is live."** Rejected. `/health` only proves gateway liveness, not embedded model path health.
- **"Any new `codex app-server attempt timed out` means the patch failed."** Refined. A 300s model timeout can still occur; the patch target was the 330s outer lane abort that prevented fallback/recovery. Post-fix evidence shows fallback completed successfully after a 300s timeout.
- **"`active_embedded_run` itself is the bug."** Rejected. During an active run it is protective. The bug was missing/delayed stale-handle recovery plus insufficient outer budget.
- **"The current system is error-free forever."** Not supported. Current state is clean after fallback completion, but `gpt-5.5` can still timeout on heavy turns; this is now a recoverable model/runtime event rather than a lane-wedging incident.

## Mitigation Taken

- Backed up installed dist and session stores:
  - `/home/piet/.npm-global/lib/node_modules/openclaw/dist/pi-embedded-rWtLEwl7.js.bak-20260503T213136Z-embedded-lane-timeout`
  - `/home/piet/.npm-global/lib/node_modules/openclaw/dist/diagnostic-oEUVZa4J.js.bak-20260503T213608Z-active-embedded-recovery`
  - `/home/piet/.openclaw/agents/sre-expert/sessions/sessions.json.bak-20260503T213136Z-embedded-lane-timeout`
  - `/home/piet/.openclaw/agents/main/sessions/sessions.json.bak-20260503T213304Z-atlas-discord-stale-reset`
- Increased `EMBEDDED_RUN_LANE_TIMEOUT_GRACE_MS` from 30s to 10min.
- Added delayed active embedded abort eligibility after 15min.
- Added regression checker: `/home/piet/.openclaw/scripts/check-embedded-run-lane-timeout-patch.py`.
- Rotated stale/bloated Forge/SRE and Atlas Discord sessions.
- Restarted `openclaw-gateway.service` and verified startup/readiness.
- Ran direct agent smokes and visible Discord delivery smokes.

## Verification

### Static patch verification

`/home/piet/.openclaw/scripts/check-embedded-run-lane-timeout-patch.py`:

```text
old_30s_constant_absent=True
new_10min_constant_present=True
resolver_still_adds_grace=True
lane_timeout_still_applied=True
active_abort_threshold_present=True
active_abort_passed_to_recovery=True
inner_ms=300000
outer_ms=900000
outer_minutes=15.0
active_abort_ms=900000
active_abort_minutes=15.0
```

### Direct model/agent verification

- `sre-expert` direct smoke: `status=ok`, model `gpt-5.3-codex`, `aborted=false`, `fallbackUsed=false`.
- `main` direct smoke: `status=ok`, model `gpt-5.5`, `aborted=false`, `fallbackUsed=false`.

### Visible Discord delivery verification

- Forge/SRE marker delivered/logged: `HERMES_VISIBLE_SRE_20260503T214039Z`.
- Atlas marker delivered/logged: `HERMES_VISIBLE_ATLAS_20260503T214039Z`.

### Real post-fix timeout/fallback verification

Post-fix real Atlas Discord turn:

```text
23:50:52 gpt-5.5 timed out: codex app-server attempt timed out
23:50:54 fallback gpt-5.4-mini started
23:51:52 fallback gpt-5.4-mini succeeded
23:51:52 model fallback decision: candidate_succeeded requested=openai/gpt-5.5 candidate=openai/gpt-5.4-mini
```

This is the strongest evidence that the 330s lane-budget root cause was fixed: the system had enough budget to continue after the 300s timeout and complete fallback.

### Current post-fallback health

At `2026-05-03T21:52:26Z`:

- Session health: `suspectedStuck=0`, `withErrors=0`.
- Since `23:51:52`, journal count for timeout/stuck patterns is zero except the expected final `candidate_succeeded` fallback decision.
- Gateway memory around `~579 MB`, service active/running.

## Risk / Remaining Issues

- The patch is in installed dist under `/home/piet/.npm-global/lib/node_modules/openclaw/dist`; OpenClaw update can overwrite it.
- `gpt-5.5` can still hit a normal 300s Codex app-server timeout on heavy Atlas Discord turns. That is not the same root cause; it is now recoverable via fallback.
- Main Discord session now has `modelOverride=gpt-5.4-mini` after successful fallback. That may be desired for stability or may need deliberate reset if Atlas should return to `gpt-5.5` primary in that channel.
- MCP model-runtime failure summaries classify intermediate `FailoverError` and `codex_app_server_timeout` events even when the overall fallback succeeded. Interpret with trajectory/session-health, not counts alone.

## Follow-ups

1. Persist/upstream the dist patch before the next OpenClaw update.
2. Consider whether Atlas Discord should keep `gpt-5.4-mini` after fallback or reset to `gpt-5.5` primary per session policy.
3. Improve monitoring classifier: distinguish "fallback succeeded after timeout" from "incident still unresolved".
4. Keep using trajectory + post-success journal window as the acceptance test, not `/health` alone.

## Verdict

- **Root cause identified for the wedging failure:** yes — outer embedded lane budget was too short (`300s + 30s`).
- **That root cause fixed in current installed runtime:** yes — outer cap now `900s`, and real fallback after a 300s timeout succeeded.
- **All future 300s model timeouts eliminated:** no — `gpt-5.5` can still timeout, but the system now recovers instead of being cut off by the 330s lane cap.
