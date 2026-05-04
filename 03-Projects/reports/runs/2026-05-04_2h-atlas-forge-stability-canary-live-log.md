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
