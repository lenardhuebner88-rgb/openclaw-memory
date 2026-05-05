# Gateway Runtime Root-Cause + Timer Stagger Plan — 2026-05-05

## Scope

Approved next lever: reduce observer timer herd / thundering-herd pressure around the Gateway without restarting Gateway or changing model/session config.

## Live evidence

Current system state at analysis time:

- Mission Control `/api/health`: `status=ok`, `openTasks=0`, `staleOpenTasks=0`, `recoveryLoad=0`.
- OpenClaw session-health 480m: `suspectedStuck=0`, `withErrors=0`.
- Gateway stayed live; previous post-check had `/health={"ok":true,"status":"live"}`, `NRestarts=0`.

Runtime warning cluster:

- `2026-05-05 11:55:15 CEST`: Discord `Gateway heartbeat ACK timeout`.
- `2026-05-05 11:59:53 CEST`: Discord REST `fetch timeout after 10000ms ... /users/@me`.
- `2026-05-05 12:22:30 CEST`: Discord `Gateway heartbeat ACK timeout`.
- `2026-05-05 12:23:00 CEST`: Gateway diagnostic `event_loop_delay`, `eventLoopDelayP99Ms=2594.2`, `eventLoopDelayMaxMs=4508.9`, `eventLoopUtilization=0.738`, `cpuCoreRatio=0.815`, `active=1 waiting=0 queued=1`.

Correlated local timer evidence:

- At `11:55:01`: `m7-auto-pickup`, `m7-plan-runner`, `openclaw-systemjob@m7-atlas-master-heartbeat`, and `openclaw-systemjob@atlas-receipt-stream-subscribe` started together; heartbeat ACK timeout followed at `11:55:15`.
- At `11:59:47`: five observer services started together: `canary-atlas-discord-fallback-chain-watch`, `canary-atlas-discord-stability-guard`, `canary-openclaw-discord-fallback-chain-watch`, `gateway-memory-monitor`, `mc-worker-service-reaper`; Discord REST fetch timeout occurred while `gateway-memory-monitor` was still running.
- At `12:20:01`: four systemJobs started together; `mc-task-parity-check` ran until `12:21:50`, `atlas-receipt-stream-subscribe` until `12:21:58`; heartbeat ACK timeout followed at `12:22:30`, event-loop warning at `12:23:00`.
- Multiple observer timers share `OnBootSec=2min` / `OnUnitActiveSec=2min`, which causes same-second batches after timer alignment.

## Working root cause

Not a single Gateway crash, not a stale task, not memory exhaustion.

Most likely root is a combination of:

1. **Gateway is doing real work** (`active=1 queued=1`, high event-loop utilization), and
2. **observer/systemJob timer bursts** run in same-second clusters, adding CPU/IO/journal/HTTP pressure exactly in the windows where Discord heartbeat and REST calls are latency-sensitive.

This does not prove the timers are the only cause. It does prove that local deterministic timer collisions are a controllable contributor and the best next low-risk lever.

## Change plan

Add bounded random jitter to the five same-second 2-minute observer timers:

- `canary-atlas-discord-fallback-chain-watch.timer`
- `canary-atlas-discord-stability-guard.timer`
- `canary-openclaw-discord-fallback-chain-watch.timer`
- `gateway-memory-monitor.timer`
- `mc-worker-service-reaper.timer`

Intended timer additions:

```ini
RandomizedDelaySec=45s
AccuracySec=30s
```

For `mc-worker-service-reaper.timer`, keep existing `AccuracySec=15s` and add only `RandomizedDelaySec=45s`.

## Safety

- No Gateway restart.
- No service restart except timer-unit reload/restart so systemd picks up timer metadata.
- No OpenClaw config/model/session mutation.
- Back up each timer file before editing.

## Verification

1. `systemd-analyze --user verify` on changed timer files if available.
2. `systemctl --user daemon-reload`.
3. Restart only the five timer units.
4. `systemctl --user cat ...timer` confirms jitter lines.
5. `systemctl --user list-timers ...` confirms timers loaded and scheduled.
6. Gateway health remains live and `NRestarts=0`.
