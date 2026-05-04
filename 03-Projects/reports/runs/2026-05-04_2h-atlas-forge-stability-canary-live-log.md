# 2h Atlas/Forge Stability Canary Live Log

Start: 2026-05-04T17:19:54+02:00

```json
{
  "ts": "2026-05-04T17:19:54+02:00",
  "healthOk": true,
  "boardOk": true,
  "service": "NRestarts=0\nActiveState=active\nSubState=running\nActiveEnterTimestamp=Mon 2026-05-04 16:58:20 CEST",
  "guardOk": true,
  "rotationNeeded": 0,
  "staleRunning": 0,
  "loadErrors": 0,
  "rotated": [],
  "events": []
}
```

## Manual incident intervention during canary

- Forge runtime-soak canary created/dispatched: task `3bc88655-53d9-4b1f-b007-7317d6d363b1`, run `14a78b47-2e88-41c6-b228-cad6832d741f`.
- Initial pickup blocked because old transient worker service `mc-worker-sre-expert-bf9d9ae2-7c2-1777903337.service` was still running although task `bf9d9ae2-7c20-41af-bd21-77115f7bec8f` was already `done` and worker-run `succeeded`.
- Stopped only that orphaned transient worker service.
- Manually started `m7-auto-pickup.service` once.
- Post-check: canary task moved to `in-progress`, `executionState=active`, fresh heartbeat, worker service `mc-worker-sre-expert-3bc88655-53d-1777908177.service` running.

```json
{
  "ts": "2026-05-04T17:24:56+02:00",
  "healthOk": true,
  "boardOk": true,
  "service": "NRestarts=0\nActiveState=active\nSubState=running\nActiveEnterTimestamp=Mon 2026-05-04 16:58:20 CEST",
  "guardOk": true,
  "rotationNeeded": 0,
  "staleRunning": 0,
  "loadErrors": 0,
  "rotated": [],
  "events": []
}
```

## Worker-service reaper hardening

- Root cause extension: transient `mc-worker-*` services can stay `active/running` after their Mission Control task is terminal.
- Added `/home/piet/.openclaw/scripts/mc-worker-service-reaper.py`.
- Default mode is dry-run; systemd service uses `--live`.
- Safety rule: stop only `mc-worker-*.service` units whose task ID resolves uniquely and whose task status is `done|failed|canceled`.
- Added and enabled user timer: `mc-worker-service-reaper.timer`, every 2 minutes.
- Validation: `py_compile` OK, dry-run OK, service run OK, timer active.

```json
{
  "ts": "2026-05-04T17:29:56+02:00",
  "healthOk": true,
  "boardOk": true,
  "service": "NRestarts=0\nActiveState=active\nSubState=running\nActiveEnterTimestamp=Mon 2026-05-04 16:58:20 CEST",
  "guardOk": true,
  "rotationNeeded": 0,
  "staleRunning": 0,
  "loadErrors": 0,
  "rotated": [],
  "events": []
}
```

## P1.4 Forge intensive matrix task

- Existing open task dispatched: `4c1a5a73-6b8b-49a5-ba7f-4b9990c3f154` `[P1.4][Forge] Controlled Atlas gpt-5.5 E2E Matrix`.
- Dispatch notification: `1500881512827195533`.
- Auto-pickup behavior:
  - First attempt: claim timeout, empty worker log, service stopped by auto-pickup.
  - Second retry: claim timeout, fresh session attempted.
  - Third attempt: `CLAIM_CONFIRMED`, task moved to `in-progress`, `receiptStage=accepted`, workerSessionId `gateway:4c1a5a73-6b8b-49a5-ba7f-4b9990c3f154`.
- RCA note: Forge larger-task startup path is fragile for first attempts; auto-pickup fresh-session retry recovers.

```json
{
  "ts": "2026-05-04T17:34:57+02:00",
  "healthOk": true,
  "boardOk": true,
  "service": "NRestarts=0\nActiveState=active\nSubState=running\nActiveEnterTimestamp=Mon 2026-05-04 16:58:20 CEST",
  "guardOk": true,
  "rotationNeeded": 0,
  "staleRunning": 0,
  "loadErrors": 0,
  "rotated": [],
  "events": []
}
```

## Atlas runtime-soak canary

- Initial Atlas dry-run blocked by cooldown at ~9m active age.
- Second dry-run after cooldown: selectedAgentCanExecute=true.
- Created/dispatched Atlas canary task: `11cf305b-bece-452b-a564-7f0153db0cd8`.
- Dispatch notification: `1500883710797549740`.

```json
{
  "ts": "2026-05-04T17:39:58+02:00",
  "healthOk": true,
  "boardOk": true,
  "service": "NRestarts=0\nActiveState=active\nSubState=running\nActiveEnterTimestamp=Mon 2026-05-04 16:58:20 CEST",
  "guardOk": true,
  "rotationNeeded": 0,
  "staleRunning": 0,
  "loadErrors": 0,
  "rotated": [],
  "events": []
}
```

```json
{
  "ts": "2026-05-04T17:44:59+02:00",
  "healthOk": true,
  "boardOk": true,
  "service": "NRestarts=0\nActiveState=active\nSubState=running\nActiveEnterTimestamp=Mon 2026-05-04 16:58:20 CEST",
  "guardOk": true,
  "rotationNeeded": 0,
  "staleRunning": 0,
  "loadErrors": 0,
  "rotated": [],
  "events": []
}
```

```json
{
  "ts": "2026-05-04T17:49:59+02:00",
  "healthOk": true,
  "boardOk": true,
  "service": "NRestarts=0\nActiveState=active\nSubState=running\nActiveEnterTimestamp=Mon 2026-05-04 16:58:20 CEST",
  "guardOk": true,
  "rotationNeeded": 0,
  "staleRunning": 0,
  "loadErrors": 0,
  "rotated": [],
  "events": [
    "May 04 17:48:04 huebners node[1157347]: 2026-05-04T17:48:04.402+02:00 [agent/embedded] embedded run failover decision: runId=b9420f5e-da6d-47e5-8a22-b4493e5d9572 stage=assistant decision=fallback_model reason=timeout from=openai/gpt-5.3-codex profile=sha256:195d21b1dd7f rawError=codex app-server attempt timed out",
    "May 04 17:48:04 huebners node[1157347]: 2026-05-04T17:48:04.404+02:00 [diagnostic] lane task error: lane=main durationMs=1503394 error=\"FailoverError: LLM request timed out.\"",
    "May 04 17:48:04 huebners node[1157347]: 2026-05-04T17:48:04.407+02:00 [diagnostic] lane wait exceeded: lane=main waitedMs=1011131 queueAhead=5",
    "May 04 17:48:04 huebners node[1157347]: 2026-05-04T17:48:04.447+02:00 [diagnostic] lane task error: lane=session:agent:sre-expert:main durationMs=1503438 error=\"FailoverError: LLM request timed out.\"",
    "May 04 17:48:04 huebners node[1157347]: 2026-05-04T17:48:04.449+02:00 [diagnostic] lane wait exceeded: lane=session:agent:sre-expert:main waitedMs=1169383 queueAhead=0",
    "May 04 17:48:04 huebners node[1157347]: 2026-05-04T17:48:04.457+02:00 [model-fallback/decision] model fallback decision: decision=candidate_failed requested=openai/gpt-5.3-codex candidate=openai/gpt-5.3-codex reason=timeout next=openai/gpt-5.5 detail=codex app-server attempt timed out"
  ]
}
```

## Forge P1.4 matrix terminal result

- Task `4c1a5a73-6b8b-49a5-ba7f-4b9990c3f154` ended `done` / `receiptStage=result` with `EXECUTION_STATUS partial`.
- Run 1 hard-stopped after a 1500s timeout and full fallback-chain failure.
- Evidence from resultSummary: model path `openai/gpt-5.5 > openai/gpt-5.3-codex > openai/gpt-5.4 > openai/gpt-5.4-mini`, `timeout_count=1`, `fallback_count=4`, `candidate_failed_count=4`, latency 330s reported in task summary while gateway lane shows long run budget around 1500s for the worker run.
- Evidence from trajectory: nested worker OpenClaw home under `/home/piet/.openclaw/agents/sre-expert/agent/codex-home/...` used direct `api.openai.com/v1/responses` and failed with `401 Unauthorized: Missing bearer or basic <redacted>` for `openai/gpt-*` fallback attempts.
- Interpretation: production Discord health and Mission Control health are not the failing surface in this case; the failing surface is embedded/nested worker routing/auth and too-long run-timeout propagation.

```json
{
  "ts": "2026-05-04T17:55:01+02:00",
  "healthOk": true,
  "boardOk": true,
  "service": "NRestarts=0\nActiveState=active\nSubState=running\nActiveEnterTimestamp=Mon 2026-05-04 17:54:26 CEST",
  "guardOk": true,
  "rotationNeeded": 0,
  "staleRunning": 0,
  "loadErrors": 0,
  "rotated": [],
  "events": [
    "May 04 17:51:49 huebners node[1157347]: 2026-05-04T17:51:49.560+02:00 [agent/embedded] embedded run failover decision: runId=a4f4d3f5-f10e-4328-84a1-4fdc7d31dc7f stage=assistant decision=fallback_model reason=timeout from=openai/gpt-5.3-codex profile=sha256:195d21b1dd7f rawError=codex app-server attempt timed out",
    "May 04 17:51:49 huebners node[1157347]: 2026-05-04T17:51:49.562+02:00 [diagnostic] lane task error: lane=main durationMs=225153 error=\"FailoverError: LLM request timed out.\"",
    "May 04 17:51:49 huebners node[1157347]: 2026-05-04T17:51:49.563+02:00 [diagnostic] lane wait exceeded: lane=main waitedMs=1180756 queueAhead=6",
    "May 04 17:51:49 huebners node[1157347]: 2026-05-04T17:51:49.565+02:00 [diagnostic] lane task error: lane=session:agent:sre-expert:explicit:sre-expert-be948b8c-4b34-4787-8f0d-a545d92c8812 durationMs=1236290 error=\"FailoverError: LLM request timed out.\"",
    "May 04 17:51:49 huebners node[1157347]: 2026-05-04T17:51:49.569+02:00 [diagnostic] lane wait exceeded: lane=main waitedMs=769305 queueAhead=5",
    "May 04 17:51:49 huebners node[1157347]: 2026-05-04T17:51:49.625+02:00 [model-fallback/decision] model fallback decision: decision=candidate_failed requested=openai/gpt-5.3-codex candidate=openai/gpt-5.3-codex reason=timeout next=openai/gpt-5.5 detail=codex app-server attempt timed out",
    "May 04 17:51:49 huebners node[1157347]: 2026-05-04T17:51:49.632+02:00 [diagnostic] lane wait exceeded: lane=session:agent:main:main waitedMs=868656 queueAhead=2",
    "May 04 17:51:49 huebners node[1157347]: 2026-05-04T17:51:49.898+02:00 [model-fallback/decision] model fallback decision: decision=candidate_failed requested=openai/gpt-5.5 candidate=openai/gpt-5.5 reason=timeout next=openai/gpt-5.3-codex detail=This operation was aborted",
    "May 04 17:51:50 huebners node[1157347]: 2026-05-04T17:51:50.151+02:00 [model-fallback/decision] model fallback decision: decision=candidate_failed requested=openai/gpt-5.5 candidate=openai/gpt-5.3-codex reason=timeout next=openai/gpt-5.4 detail=This operation was aborted",
    "May 04 17:51:50 huebners node[1157347]: 2026-05-04T17:51:50.393+02:00 [model-fallback/decision] model fallback decision: decision=candidate_failed requested=openai/gpt-5.5 candidate=openai/gpt-5.4 reason=timeout next=openai/gpt-5.4-mini detail=This operation was aborted",
    "May 04 17:51:50 huebners node[1157347]: 2026-05-04T17:51:50.635+02:00 [model-fallback/decision] model fallback decision: decision=candidate_failed requested=openai/gpt-5.5 candidate=openai/gpt-5.4-mini reason=timeout next=none detail=This operation was aborted",
    "May 04 17:53:42 huebners node[1157347]: 2026-05-04T17:53:42.385+02:00 [diagnostic] lane wait exceeded: lane=main waitedMs=783010 queueAhead=6"
  ]
}
```

## Recovery action after lane abort chain

- After the visible Atlas Discord smoke exposed abort-poisoned `main` lanes and no Mission Control worker tasks were active, Gateway was restarted intentionally.
- Pre-gate: Mission Control health showed `openCount=0`, `orphanedDispatches=0`, `staleOpenTasks=0`; no active `mc-worker-main` or `mc-worker-sre-expert` services were present.
- Restart time: `Mon 2026-05-04 17:54:26 CEST`.
- Post-gate: `openclaw-gateway.service active/running`, ExecStartPre scripts successful, HTTP health `http://127.0.0.1:18789/health` returned `{"ok":true,"status":"live"}`.
- Discord plugin restarted and resolved channels; Telegram has separate duplicate polling conflict noise, not part of Atlas/Forge Discord failure.

```json
{
  "ts": "2026-05-04T18:00:05+02:00",
  "healthOk": true,
  "boardOk": true,
  "service": "NRestarts=0\nActiveState=active\nSubState=running\nActiveEnterTimestamp=Mon 2026-05-04 17:54:26 CEST",
  "guardOk": true,
  "rotationNeeded": 0,
  "staleRunning": 0,
  "loadErrors": 0,
  "rotated": [],
  "events": []
}
```

## 18:00 Atlas ping/reporting fallback finding

- Forge post-restart canary `75638bd4-90e6-4e85-a4e7-80dbcff02fa4` completed `done` with accepted/progress/result receipts.
- The terminal receipt triggered Mission Control's canonical Atlas ping path (`src/lib/task-reports.ts`, `postAtlasPing()`), which POSTs to OpenClaw Gateway `/v1/chat/completions` with model `openclaw/main`.
- That created `agent:main:openai:*` sessions, not `agent:main:discord:*`.
- One ping session failed fast with four fallback steps at `2026-05-04T16:00:13Z`:
  - `openai/gpt-5.5 -> openai/gpt-5.3-codex`
  - `openai/gpt-5.3-codex -> openai/gpt-5.4`
  - `openai/gpt-5.4 -> openai/gpt-5.4-mini`
  - chain exhausted
- Failure detail: `This operation was aborted`.
- A second Atlas ping session immediately succeeded at `2026-05-04T16:00:21Z`, assistant text: `Received. Forge canary validation is done...`.
- Interpretation: productive Discord lane remains clean, but terminal task reporting can still invoke Atlas through the OpenClaw Gateway model path and create fallback noise/load.
- Candidate next fix after the 2h test: make `atlas_pinged` non-blocking and/or queue-limited, or route it to a cheaper/light isolated reporting lane instead of `openclaw/main`.

## 18:14 Atlas main canary recovery proof

- Atlas/main dry-run gate became eligible after 10 minute cooldown.
- Created/dispatched real Atlas runtime-soak canary: task `9a882666-8eec-4620-b300-ebde4148f3a4`, dispatch notification `1500892554877472809`.
- Initial auto-pickup run was intentionally held as `young=1`; second pickup after age gate claimed successfully.
- Accepted receipt: `2026-05-04T16:13:30Z`, workerSessionId `agent:main`.
- Terminal result: `2026-05-04T16:13:59Z`, resultSummary `canary-ok`.
- Task state: `done`, dispatchState `completed`, executionState `done`, receiptStage `result`.
- Reaper post-check: no lingering `mc-worker-main-*` service.
- Gateway log since `18:10 CEST`: no `codex app-server`, `FailoverError`, `candidate_failed`, `lane wait exceeded`, `status:408`, or `AbortError` matches.
- Session guard after Atlas canary: `rotationNeeded=0`, `staleRunning=0`, `loadErrors=0`.
- Interpretation: the Atlas Mission Control worker path is recovered after stale `agent:main:main` rotation plus Gateway restart. Productive proof is still bounded; broader real Atlas work should now be observed, not assumed.

## 18:17 Real RCA workload dispatched

- Atlas RCA task dispatched: `24987336-4cfa-4913-ab7c-518e951bc788`, title `[P5][Atlas] atlas_pinged reporting path RCA`, dispatch notification `1500894176148062503`.
- Forge RCA task dispatched: `85607987-3593-43e3-8da4-12d52e278f10`, title `[P5][Forge] nested worker auth/fallback RCA`, dispatch notification `1500894182514884882`.
- Purpose: move beyond canaries into real read-only RCA work while the monitor tracks claim/receipt/worker-service/gateway fallback behavior.
- No config/runtime/session mutation included in either task.

## 18:23 Real workload status

- Atlas RCA task `24987336-4cfa-4913-ab7c-518e951bc788` claimed successfully:
  - Accepted receipt: `2026-05-04T16:19:45Z`
  - Progress receipt: `2026-05-04T16:21:20Z`
  - Current state: `in-progress`, executionState `active`, receiptStage `progress`, workerSessionId `agent:main`
  - Progress summary: `Read-only RCA evidence gathered: task-reports.ts posts atlas_pinged synchronously through Gateway openclaw/main after terminal reports...`
- Forge RCA task `85607987-3593-43e3-8da4-12d52e278f10` failed before first claim:
  - Four worker logs were created with zero bytes.
  - Auto-pickup attempted normal session plus three fresh-session retries.
  - Final failure: `Auto-pickup unclaimed after 3 attempts: unclaimed-retry-limit-before-trigger`.
  - systemd worker services exited with status 1 after 3-6 seconds CPU and around 300 MB peak memory.
- Gateway log since `18:17 CEST`: no model timeout/fallback/lane-wait matches. The Forge failure is pre-claim worker startup, not model inference.
- Mission Control health: `openCount=1` (Atlas active), `orphanedDispatches=0`, `staleOpenTasks=0`.
- Session guard: `rotationNeeded=0`, `staleRunning=0`, `loadErrors=0`.

## 18:26 SRE claim-budget fix and Forge retest

- Live cause for Forge RCA failure: pre-claim timeout, not model inference. Four `sre-expert` worker attempts wrote 0-byte logs and were stopped before first accepted receipt.
- `auto-pickup.py` previously gave `sre-expert` only the base 45s sync-claim budget; Atlas/main already had 90s.
- Patched `/home/piet/.openclaw/scripts/auto-pickup.py`:
  - Added `AUTO_PICKUP_SRE_SYNC_CLAIM_TIMEOUT_SEC`, default `120`.
  - `claim_timeout_for_agent("sre-expert")` now returns at least 120s.
- Validation:
  - `python3 -m py_compile /home/piet/.openclaw/scripts/auto-pickup.py` OK.
  - `/home/piet/.openclaw/scripts/tests/test_auto_pickup.py` OK, 15 tests.
  - Live function check: `main=90`, `sre-expert=120`, `efficiency-auditor=90`.
- Also rotated failed high-cache `agent:sre-expert:main` session:
  - removed sessionId `22af7dcb-4992-446a-a85c-f1d0a03b3ab1`
  - status `failed`, cacheRead `163200`, totalTokens `174723`
  - backup `/home/piet/.openclaw/agents/sre-expert/sessions/sessions.json.bak-20260504T162536Z-rotate-sre-main-timeout`
- Forge retest task dispatched: `7a4e6d3a-9066-4d15-81fc-b1c67b39d7dd`, dispatch notification `1500896392820953280`.

## 18:33 Forge retest accepted

- First Forge retest attempt still hit `claim_timeout_sec=120` before accepted receipt.
- A fresh-session retry then succeeded:
  - task `7a4e6d3a-9066-4d15-81fc-b1c67b39d7dd`
  - accepted at `2026-05-04T16:32:52Z`
  - state `in-progress`, executionState `active`, receiptStage `accepted`
  - workerSessionId `gateway:7a4e6d3a-9066-4d15-81fc-b1c67b39d7dd`
- Interpretation: the SRE claim-budget fix is materially better than 45s; Forge can now claim under the retest. It still needs follow-through to terminal result and may need a deeper first-attempt startup fix later.

```json
{
  "ts": "2026-05-04T18:05:08+02:00",
  "healthOk": true,
  "boardOk": true,
  "service": "NRestarts=0\nActiveState=active\nSubState=running\nActiveEnterTimestamp=Mon 2026-05-04 17:54:26 CEST",
  "guardOk": true,
  "rotationNeeded": 0,
  "staleRunning": 0,
  "loadErrors": 0,
  "rotated": [],
  "events": [
    "May 04 18:00:13 huebners node[1210995]: 2026-05-04T18:00:13.771+02:00 [model-fallback/decision] model fallback decision: decision=candidate_failed requested=openai/gpt-5.5 candidate=openai/gpt-5.5 reason=timeout next=openai/gpt-5.3-codex detail=This operation was aborted",
    "May 04 18:00:13 huebners node[1210995]: 2026-05-04T18:00:13.927+02:00 [model-fallback/decision] model fallback decision: decision=candidate_failed requested=openai/gpt-5.5 candidate=openai/gpt-5.3-codex reason=timeout next=openai/gpt-5.4 detail=This operation was aborted",
    "May 04 18:00:14 huebners node[1210995]: 2026-05-04T18:00:14.074+02:00 [model-fallback/decision] model fallback decision: decision=candidate_failed requested=openai/gpt-5.5 candidate=openai/gpt-5.4 reason=timeout next=openai/gpt-5.4-mini detail=This operation was aborted",
    "May 04 18:00:14 huebners node[1210995]: 2026-05-04T18:00:14.215+02:00 [model-fallback/decision] model fallback decision: decision=candidate_failed requested=openai/gpt-5.5 candidate=openai/gpt-5.4-mini reason=timeout next=none detail=This operation was aborted"
  ]
}
```

```json
{
  "ts": "2026-05-04T18:10:10+02:00",
  "healthOk": true,
  "boardOk": true,
  "service": "NRestarts=0\nActiveState=active\nSubState=running\nActiveEnterTimestamp=Mon 2026-05-04 17:54:26 CEST",
  "guardOk": true,
  "rotationNeeded": 0,
  "staleRunning": 0,
  "loadErrors": 0,
  "rotated": [],
  "events": []
}
```

```json
{
  "ts": "2026-05-04T18:15:11+02:00",
  "healthOk": true,
  "boardOk": true,
  "service": "NRestarts=0\nActiveState=active\nSubState=running\nActiveEnterTimestamp=Mon 2026-05-04 17:54:26 CEST",
  "guardOk": true,
  "rotationNeeded": 0,
  "staleRunning": 0,
  "loadErrors": 0,
  "rotated": [],
  "events": []
}
```

```json
{
  "ts": "2026-05-04T18:20:12+02:00",
  "healthOk": true,
  "boardOk": true,
  "service": "NRestarts=0\nActiveState=active\nSubState=running\nActiveEnterTimestamp=Mon 2026-05-04 17:54:26 CEST",
  "guardOk": true,
  "rotationNeeded": 0,
  "staleRunning": 0,
  "loadErrors": 0,
  "rotated": [],
  "events": [
    "May 04 18:15:26 huebners node[1210995]: 2026-05-04T18:15:26.829+02:00 [diagnostic] lane wait exceeded: lane=main waitedMs=84912 queueAhead=0",
    "May 04 18:15:26 huebners node[1210995]: 2026-05-04T18:15:26.843+02:00 [model-fallback/decision] model fallback decision: decision=candidate_failed requested=openai/gpt-5.5 candidate=openai/gpt-5.5 reason=timeout next=openai/gpt-5.3-codex detail=This operation was aborted",
    "May 04 18:15:27 huebners node[1210995]: 2026-05-04T18:15:27.060+02:00 [model-fallback/decision] model fallback decision: decision=candidate_failed requested=openai/gpt-5.5 candidate=openai/gpt-5.3-codex reason=timeout next=openai/gpt-5.4 detail=This operation was aborted",
    "May 04 18:15:27 huebners node[1210995]: 2026-05-04T18:15:27.204+02:00 [model-fallback/decision] model fallback decision: decision=candidate_failed requested=openai/gpt-5.5 candidate=openai/gpt-5.4 reason=timeout next=openai/gpt-5.4-mini detail=This operation was aborted",
    "May 04 18:15:27 huebners node[1210995]: 2026-05-04T18:15:27.348+02:00 [model-fallback/decision] model fallback decision: decision=candidate_failed requested=openai/gpt-5.5 candidate=openai/gpt-5.4-mini reason=timeout next=none detail=This operation was aborted"
  ]
}
```

```json
{
  "ts": "2026-05-04T18:25:14+02:00",
  "healthOk": true,
  "boardOk": true,
  "service": "NRestarts=0\nActiveState=active\nSubState=running\nActiveEnterTimestamp=Mon 2026-05-04 17:54:26 CEST",
  "guardOk": true,
  "rotationNeeded": 0,
  "staleRunning": 0,
  "loadErrors": 0,
  "rotated": [],
  "events": [
    "May 04 18:24:24 huebners node[1210995]: 2026-05-04T18:24:24.961+02:00 [agent/embedded] embedded run failover decision: runId=117281b8-5527-44de-8fc9-e9c119d363ae stage=assistant decision=fallback_model reason=timeout from=openai/gpt-5.3-codex profile=sha256:195d21b1dd7f rawError=codex app-server attempt timed out",
    "May 04 18:24:24 huebners node[1210995]: 2026-05-04T18:24:24.963+02:00 [diagnostic] lane task error: lane=main durationMs=1503637 error=\"FailoverError: LLM request timed out.\"",
    "May 04 18:24:24 huebners node[1210995]: 2026-05-04T18:24:24.964+02:00 [diagnostic] lane wait exceeded: lane=main waitedMs=214055 queueAhead=3",
    "May 04 18:24:24 huebners node[1210995]: 2026-05-04T18:24:24.990+02:00 [diagnostic] lane task error: lane=session:agent:sre-expert:main durationMs=1503664 error=\"FailoverError: LLM request timed out.\"",
    "May 04 18:24:24 huebners node[1210995]: 2026-05-04T18:24:24.991+02:00 [diagnostic] lane wait exceeded: lane=session:agent:sre-expert:main waitedMs=274419 queueAhead=0",
    "May 04 18:24:24 huebners node[1210995]: 2026-05-04T18:24:24.995+02:00 [model-fallback/decision] model fallback decision: decision=candidate_failed requested=openai/gpt-5.3-codex candidate=openai/gpt-5.3-codex reason=timeout next=openai/gpt-5.5 detail=codex app-server attempt timed out"
  ]
}
```

```json
{
  "ts": "2026-05-04T18:30:15+02:00",
  "healthOk": true,
  "boardOk": true,
  "service": "NRestarts=0\nActiveState=active\nSubState=running\nActiveEnterTimestamp=Mon 2026-05-04 17:54:26 CEST",
  "guardOk": true,
  "rotationNeeded": 0,
  "staleRunning": 0,
  "loadErrors": 0,
  "rotated": [],
  "events": [
    "May 04 18:26:41 huebners node[1210995]: 2026-05-04T18:26:41.238+02:00 [diagnostic] lane wait exceeded: lane=main waitedMs=289701 queueAhead=3",
    "May 04 18:29:45 huebners node[1210995]: 2026-05-04T18:29:45.326+02:00 [diagnostic] lane wait exceeded: lane=main waitedMs=419842 queueAhead=2",
    "May 04 18:29:45 huebners node[1210995]: 2026-05-04T18:29:45.329+02:00 [diagnostic] lane wait exceeded: lane=main waitedMs=407524 queueAhead=1",
    "May 04 18:29:45 huebners node[1210995]: 2026-05-04T18:29:45.355+02:00 [model-fallback/decision] model fallback decision: decision=candidate_failed requested=openai/gpt-5.5 candidate=openai/gpt-5.5 reason=timeout next=openai/gpt-5.3-codex detail=This operation was aborted",
    "May 04 18:29:45 huebners node[1210995]: 2026-05-04T18:29:45.496+02:00 [model-fallback/decision] model fallback decision: decision=candidate_failed requested=openai/gpt-5.5 candidate=openai/gpt-5.3-codex reason=timeout next=openai/gpt-5.4 detail=This operation was aborted",
    "May 04 18:29:45 huebners node[1210995]: 2026-05-04T18:29:45.626+02:00 [model-fallback/decision] model fallback decision: decision=candidate_failed requested=openai/gpt-5.5 candidate=openai/gpt-5.4 reason=timeout next=openai/gpt-5.4-mini detail=This operation was aborted",
    "May 04 18:29:45 huebners node[1210995]: 2026-05-04T18:29:45.792+02:00 [model-fallback/decision] model fallback decision: decision=candidate_failed requested=openai/gpt-5.5 candidate=openai/gpt-5.4-mini reason=timeout next=none detail=This operation was aborted"
  ]
}
```

```json
{
  "ts": "2026-05-04T18:35:17+02:00",
  "healthOk": true,
  "boardOk": true,
  "service": "NRestarts=0\nActiveState=active\nSubState=running\nActiveEnterTimestamp=Mon 2026-05-04 17:54:26 CEST",
  "guardOk": true,
  "rotationNeeded": 0,
  "staleRunning": 0,
  "loadErrors": 0,
  "rotated": [],
  "events": [
    "May 04 18:31:17 huebners node[1210995]: 2026-05-04T18:31:17.860+02:00 [diagnostic] lane wait exceeded: lane=main waitedMs=412868 queueAhead=1",
    "May 04 18:31:40 huebners node[1210995]: 2026-05-04T18:31:40.914+02:00 [diagnostic] lane wait exceeded: lane=main waitedMs=69528 queueAhead=0",
    "May 04 18:31:40 huebners node[1210995]: 2026-05-04T18:31:40.938+02:00 [diagnostic] lane wait exceeded: lane=session:agent:sre-expert:main waitedMs=435809 queueAhead=1",
    "May 04 18:31:40 huebners node[1210995]: 2026-05-04T18:31:40.941+02:00 [diagnostic] lane wait exceeded: lane=session:agent:sre-expert:main waitedMs=199073 queueAhead=0",
    "May 04 18:31:40 huebners node[1210995]: 2026-05-04T18:31:40.945+02:00 [model-fallback/decision] model fallback decision: decision=candidate_failed requested=openai/gpt-5.3-codex candidate=openai/gpt-5.5 reason=timeout next=openai/gpt-5.4-mini detail=This operation was aborted",
    "May 04 18:31:41 huebners node[1210995]: 2026-05-04T18:31:41.083+02:00 [model-fallback/decision] model fallback decision: decision=candidate_failed requested=openai/gpt-5.3-codex candidate=openai/gpt-5.4-mini reason=timeout next=openai/gpt-5.4 detail=This operation was aborted",
    "May 04 18:31:41 huebners node[1210995]: 2026-05-04T18:31:41.226+02:00 [model-fallback/decision] model fallback decision: decision=candidate_failed requested=openai/gpt-5.3-codex candidate=openai/gpt-5.4 reason=timeout next=none detail=This operation was aborted",
    "May 04 18:31:41 huebners node[1210995]: 2026-05-04T18:31:41.908+02:00 [ws] ⇄ res ✗ agent errorCode=UNAVAILABLE errorMessage=FallbackSummaryError: All models failed (4): openai/gpt-5.3-codex: codex app-server attempt timed out (timeout) | openai/gpt-5.5: This operation was aborted (timeout) | openai/gpt-5.4-mini: This operation was aborted (timeout) | openai/gpt-... runId=117281b8-5527-44de-8fc9-e9c119d363ae error=FallbackSummaryError: All models failed (4): openai/gpt-5.3-codex: codex app-server attempt timed out (timeout) | openai/gpt-5.5: This operation was aborted (timeout) | openai/gpt-5.4-mini: This operation was aborted (timeout) | openai/gpt-... conn=4b4f613a…e45a id=15ea889f…7c5c"
  ]
}
```

```json
{
  "ts": "2026-05-04T18:40:18+02:00",
  "healthOk": true,
  "boardOk": true,
  "service": "NRestarts=0\nActiveState=active\nSubState=running\nActiveEnterTimestamp=Mon 2026-05-04 17:54:26 CEST",
  "guardOk": true,
  "rotationNeeded": 0,
  "staleRunning": 0,
  "loadErrors": 0,
  "rotated": [],
  "events": [
    "May 04 18:35:25 huebners node[1210995]: - `/home/piet/.openclaw/agents/sre-expert/sessions/sre-expert-be948b8c-4b34-4787-8f0d-a545d92c8812.trajectory.jsonl` enthält `turn.completion_idle_timeout` und `codex app-server attempt timed out` (Turn-Timeout nach Start, kein neuer Pending-Pickup-Claim-Abbruch).",
    "May 04 18:36:05 huebners node[1210995]: 2026-05-04T18:36:05.405+02:00 [diagnostic] lane wait exceeded: lane=main waitedMs=205069 queueAhead=2",
    "May 04 18:36:35 huebners node[1210995]: 2026-05-04T18:36:35.185+02:00 [diagnostic] lane wait exceeded: lane=main waitedMs=152944 queueAhead=1",
    "May 04 18:36:35 huebners node[1210995]: 2026-05-04T18:36:35.188+02:00 [diagnostic] lane wait exceeded: lane=main waitedMs=82823 queueAhead=0",
    "May 04 18:36:35 huebners node[1210995]: 2026-05-04T18:36:35.194+02:00 [model-fallback/decision] model fallback decision: decision=candidate_failed requested=openai/gpt-5.5 candidate=openai/gpt-5.5 reason=timeout next=openai/gpt-5.3-codex detail=This operation was aborted",
    "May 04 18:36:35 huebners node[1210995]: 2026-05-04T18:36:35.203+02:00 [model-fallback/decision] model fallback decision: decision=candidate_failed requested=openai/gpt-5.5 candidate=openai/gpt-5.5 reason=timeout next=openai/gpt-5.3-codex detail=This operation was aborted",
    "May 04 18:36:35 huebners node[1210995]: 2026-05-04T18:36:35.353+02:00 [model-fallback/decision] model fallback decision: decision=candidate_failed requested=openai/gpt-5.5 candidate=openai/gpt-5.3-codex reason=timeout next=openai/gpt-5.4 detail=This operation was aborted",
    "May 04 18:36:35 huebners node[1210995]: 2026-05-04T18:36:35.503+02:00 [model-fallback/decision] model fallback decision: decision=candidate_failed requested=openai/gpt-5.5 candidate=openai/gpt-5.3-codex reason=timeout next=openai/gpt-5.4 detail=This operation was aborted",
    "May 04 18:36:35 huebners node[1210995]: 2026-05-04T18:36:35.635+02:00 [model-fallback/decision] model fallback decision: decision=candidate_failed requested=openai/gpt-5.5 candidate=openai/gpt-5.4 reason=timeout next=openai/gpt-5.4-mini detail=This operation was aborted",
    "May 04 18:36:35 huebners node[1210995]: 2026-05-04T18:36:35.763+02:00 [model-fallback/decision] model fallback decision: decision=candidate_failed requested=openai/gpt-5.5 candidate=openai/gpt-5.4 reason=timeout next=openai/gpt-5.4-mini detail=This operation was aborted",
    "May 04 18:36:35 huebners node[1210995]: 2026-05-04T18:36:35.892+02:00 [model-fallback/decision] model fallback decision: decision=candidate_failed requested=openai/gpt-5.5 candidate=openai/gpt-5.4-mini reason=timeout next=none detail=This operation was aborted",
    "May 04 18:36:36 huebners node[1210995]: 2026-05-04T18:36:36.233+02:00 [model-fallback/decision] model fallback decision: decision=candidate_failed requested=openai/gpt-5.5 candidate=openai/gpt-5.4-mini reason=timeout next=none detail=This operation was aborted"
  ]
}
```

```json
{
  "ts": "2026-05-04T18:45:19+02:00",
  "healthOk": true,
  "boardOk": true,
  "service": "NRestarts=0\nActiveState=active\nSubState=running\nActiveEnterTimestamp=Mon 2026-05-04 17:54:26 CEST",
  "guardOk": true,
  "rotationNeeded": 0,
  "staleRunning": 0,
  "loadErrors": 0,
  "rotated": [],
  "events": [
    "May 04 18:44:25 huebners node[1210995]: 2026-05-04T18:44:25.053+02:00 [agent/embedded] embedded run failover decision: runId=9d15a4c3-863f-4400-979b-d01ac0ef0fdc stage=assistant decision=fallback_model reason=timeout from=openai/gpt-5.5 profile=sha256:195d21b1dd7f rawError=codex app-server attempt timed out",
    "May 04 18:44:25 huebners node[1210995]: 2026-05-04T18:44:25.055+02:00 [diagnostic] lane task error: lane=main durationMs=1500905 error=\"FailoverError: LLM request timed out.\"",
    "May 04 18:44:25 huebners node[1210995]: 2026-05-04T18:44:25.056+02:00 [diagnostic] lane task error: lane=session:agent:main:main durationMs=1500906 error=\"FailoverError: LLM request timed out.\"",
    "May 04 18:44:25 huebners node[1210995]: 2026-05-04T18:44:25.060+02:00 [model-fallback/decision] model fallback decision: decision=candidate_failed requested=openai/gpt-5.5 candidate=openai/gpt-5.5 reason=timeout next=openai/gpt-5.3-codex detail=codex app-server attempt timed out"
  ]
}
```

```json
{
  "ts": "2026-05-04T18:50:21+02:00",
  "healthOk": true,
  "boardOk": true,
  "service": "NRestarts=0\nActiveState=active\nSubState=running\nActiveEnterTimestamp=Mon 2026-05-04 17:54:26 CEST",
  "guardOk": true,
  "rotationNeeded": 0,
  "staleRunning": 0,
  "loadErrors": 0,
  "rotated": [],
  "events": []
}
```

```json
{
  "ts": "2026-05-04T18:55:22+02:00",
  "healthOk": true,
  "boardOk": true,
  "service": "NRestarts=0\nActiveState=active\nSubState=running\nActiveEnterTimestamp=Mon 2026-05-04 17:54:26 CEST",
  "guardOk": true,
  "rotationNeeded": 0,
  "staleRunning": 0,
  "loadErrors": 0,
  "rotated": [],
  "events": []
}
```

```json
{
  "ts": "2026-05-04T19:00:23+02:00",
  "healthOk": true,
  "boardOk": true,
  "service": "NRestarts=0\nActiveState=active\nSubState=running\nActiveEnterTimestamp=Mon 2026-05-04 17:54:26 CEST",
  "guardOk": true,
  "rotationNeeded": 0,
  "staleRunning": 0,
  "loadErrors": 0,
  "rotated": [],
  "events": []
}
```

```json
{
  "ts": "2026-05-04T19:05:24+02:00",
  "healthOk": true,
  "boardOk": true,
  "service": "NRestarts=0\nActiveState=active\nSubState=running\nActiveEnterTimestamp=Mon 2026-05-04 17:54:26 CEST",
  "guardOk": true,
  "rotationNeeded": 0,
  "staleRunning": 0,
  "loadErrors": 0,
  "rotated": [],
  "events": []
}
```
