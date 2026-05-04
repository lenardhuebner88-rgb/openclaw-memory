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
