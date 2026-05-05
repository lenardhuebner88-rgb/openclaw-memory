# Gateway Runtime Root-Cause + Timer Stagger Receipt — 2026-05-05

## Result

Applied the approved next stability lever: deterministic staggering for the five high-frequency observer timers that previously started in same-second bursts around Gateway/Discord runtime warnings.

## Root-cause finding

This was not a Gateway crash, Mission-Control board failure, stale task, or memory exhaustion.

Live evidence points to **latency pressure on the Gateway event loop / Discord heartbeat path** caused by the combination of:

1. Gateway doing real work (`active=1 waiting=0 queued=1`) with high runtime utilization, and
2. local timer bursts from observer/systemJob jobs starting in same-second clusters.

Key live signals:

- `2026-05-05 11:55:15 CEST`: Discord `Gateway heartbeat ACK timeout`.
- `2026-05-05 11:59:53 CEST`: Discord REST `fetch timeout after 10000ms ... /users/@me`.
- `2026-05-05 12:22:30 CEST`: Discord `Gateway heartbeat ACK timeout`.
- `2026-05-05 12:23:00 CEST`: diagnostic `event_loop_delay`, `eventLoopDelayP99Ms=2594.2`, `eventLoopDelayMaxMs=4508.9`, `eventLoopUtilization=0.738`, `cpuCoreRatio=0.815`, `active=1 waiting=0 queued=1`.

Correlated timer evidence:

- `11:55:01`: `m7-auto-pickup`, `m7-plan-runner`, `m7-atlas-master-heartbeat`, `atlas-receipt-stream-subscribe` started together; heartbeat ACK timeout followed at `11:55:15`.
- `11:59:47`: five observer timers started together; Discord REST fetch timeout occurred while `gateway-memory-monitor` was still running.
- `12:20:01`: four systemJobs started together; `mc-task-parity-check` ran until `12:21:50`, `atlas-receipt-stream-subscribe` until `12:21:58`; heartbeat ACK timeout followed at `12:22:30`, event-loop warning at `12:23:00`.

Conclusion: timer herding is a controllable contributor. It may not be the only root cause, but it is the best low-risk next lever.

## Changed timer units

Backups created with suffix:

```text
.bak-20260505T123305Z
```

Changed files:

```text
/home/piet/.config/systemd/user/canary-atlas-discord-stability-guard.timer
/home/piet/.config/systemd/user/mc-worker-service-reaper.timer
/home/piet/.config/systemd/user/gateway-memory-monitor.timer
/home/piet/.config/systemd/user/canary-atlas-discord-fallback-chain-watch.timer
/home/piet/.config/systemd/user/canary-openclaw-discord-fallback-chain-watch.timer
```

Final deterministic schedule:

```ini
canary-atlas-discord-stability-guard.timer:         OnCalendar=*:00/2:10
mc-worker-service-reaper.timer:                     OnCalendar=*:00/2:25
gateway-memory-monitor.timer:                       OnCalendar=*:00/2:40
canary-atlas-discord-fallback-chain-watch.timer:    OnCalendar=*:01/2:10
canary-openclaw-discord-fallback-chain-watch.timer: OnCalendar=*:01/2:25
```

All five use:

```ini
AccuracySec=1s
Persistent=true
```

Note: I first tested bounded `RandomizedDelaySec=45s`, but the post-check still showed a partial cluster. I promoted the fix to deterministic `OnCalendar` offsets and verified actual staggered firings.

## Verification

- `systemd-analyze --user verify` completed for changed timers. It emitted an unrelated existing `vault-sync.service` warning, not related to these timer files.
- `systemctl --user daemon-reload` completed.
- Restarted only the five timer units; no Gateway restart.
- Actual starts after deterministic schedule:

```text
14:37:10 canary-atlas-discord-fallback-chain-watch
14:37:25 canary-openclaw-discord-fallback-chain-watch
14:38:10 canary-atlas-discord-stability-guard
14:38:25 mc-worker-service-reaper
14:38:40 gateway-memory-monitor
```

- Gateway monitor after stagger:

```text
gateway_runtime_signal=ok lookback_min=10 count=0
```

- Gateway post-check:

```text
{"ok":true,"status":"live"}
NRestarts=0
ActiveState=active
SubState=running
```

- Failed user units:

```text
0 loaded units listed.
```

## Residual risk

This reduces observer-timer burst pressure. It does not eliminate all event-loop risk because Gateway can still be loaded by:

- large active Atlas/Forge turns,
- long `mc-task-parity-check` systemJob windows,
- Discord/API-side latency,
- active embedded runs with queued follow-up work.

## Next recommended probe

If another `gateway_runtime_signal=warning` appears, correlate it against:

1. active OpenClaw session/run at that timestamp,
2. systemJobs running in the previous 120s,
3. `mc-task-parity-check` duration,
4. Discord REST/heartbeat signals.

If the next warning follows `mc-task-parity-check`, the next lever is to stagger or optimize the 10-minute systemJob cluster.
