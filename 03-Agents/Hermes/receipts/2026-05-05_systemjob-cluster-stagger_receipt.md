# Receipt — SystemJob Cluster Stagger

Date: 2026-05-05
Operator: Hermes
Scope: Entzerrung von 4 OpenClaw systemd user Timern für systemJobs. Keine OpenClaw/Gateway/Mission-Control Service-Restarts.

## Problem

Vier OpenClaw systemJob Timer feuerten zur vollen 5-/10-Minute gleichzeitig. Bei 14:50 wurde der Burst live toleriert, aber die Kopplung blieb ein vermeidbarer Latenz-/Event-Loop-Risikofaktor.

## Approval

Piet erteilte im Discord-Thread Freigabe: "Ok setze das genauso schritt für Schritt um und sauber dokumentieren."

## Live evidence before change

Aktuelle Timer vor Änderung:

```ini
openclaw-systemjob-mc-task-parity-check.timer
OnCalendar=*-*-* *:0/10:00

openclaw-systemjob-mcp-zombie-killer-10min.timer
OnCalendar=*-*-* *:0/10:00

openclaw-systemjob-m7-atlas-master-heartbeat.timer
OnCalendar=*-*-* *:0/5:00

openclaw-systemjob-atlas-receipt-stream-subscribe.timer
OnCalendar=*-*-* *:0/5:00
```

14:50 Beobachtung vor Änderung:

```text
14:50:01 4 systemJobs gestartet
14:50:01 mcp-zombie-killer fertig
14:50:02 m7-heartbeat fertig
14:50:11 receipt-stream fertig
14:52:17 mc-task-parity-check fertig
```

## Files changed

- `/home/piet/.config/systemd/user/openclaw-systemjob-mc-task-parity-check.timer`
- `/home/piet/.config/systemd/user/openclaw-systemjob-mcp-zombie-killer-10min.timer`
- `/home/piet/.config/systemd/user/openclaw-systemjob-m7-atlas-master-heartbeat.timer`
- `/home/piet/.config/systemd/user/openclaw-systemjob-atlas-receipt-stream-subscribe.timer`

## Backups

Timestamp: `20260505T132410Z`

- `/home/piet/.config/systemd/user/openclaw-systemjob-mc-task-parity-check.timer.bak-20260505T132410Z`
- `/home/piet/.config/systemd/user/openclaw-systemjob-mcp-zombie-killer-10min.timer.bak-20260505T132410Z`
- `/home/piet/.config/systemd/user/openclaw-systemjob-m7-atlas-master-heartbeat.timer.bak-20260505T132410Z`
- `/home/piet/.config/systemd/user/openclaw-systemjob-atlas-receipt-stream-subscribe.timer.bak-20260505T132410Z`

Backup command succeeded and backup files were non-empty.

## Diff summary

```diff
openclaw-systemjob-mcp-zombie-killer-10min.timer
- OnCalendar=*-*-* *:0/10:00
+ OnCalendar=*-*-* *:0/10:05

openclaw-systemjob-m7-atlas-master-heartbeat.timer
- OnCalendar=*-*-* *:0/5:00
+ OnCalendar=*-*-* *:0/5:15

openclaw-systemjob-atlas-receipt-stream-subscribe.timer
- OnCalendar=*-*-* *:0/5:00
+ OnCalendar=*-*-* *:0/5:45

openclaw-systemjob-mc-task-parity-check.timer
- OnCalendar=*-*-* *:0/10:00
+ OnCalendar=*-*-* *:2/10:20
```

## Validation

`systemd-analyze --user verify` exited `0` for all 4 edited timers.

Note: verify printed an unrelated pre-existing warning for `/home/piet/.config/systemd/user/vault-sync.service` about ignored escape sequences. It was not one of the edited units.

## Activation

Executed:

```bash
systemctl --user daemon-reload
systemctl --user restart \
  openclaw-systemjob-mc-task-parity-check.timer \
  openclaw-systemjob-mcp-zombie-killer-10min.timer \
  openclaw-systemjob-m7-atlas-master-heartbeat.timer \
  openclaw-systemjob-atlas-receipt-stream-subscribe.timer
```

No Gateway/Mission-Control/OpenClaw service restart was performed.

## Timer proof after reload

Immediately after reload/restart, `systemctl --user list-timers` showed staggered next runs:

```text
15:25:15 openclaw-systemjob-m7-atlas-master-heartbeat.timer
15:25:45 openclaw-systemjob-atlas-receipt-stream-subscribe.timer
15:30:05 openclaw-systemjob-mcp-zombie-killer-10min.timer
15:32:20 openclaw-systemjob-mc-task-parity-check.timer
```

Later postcheck showed continuing schedule:

```text
15:35:45 openclaw-systemjob-atlas-receipt-stream-subscribe.timer
15:40:05 openclaw-systemjob-mcp-zombie-killer-10min.timer
15:40:15 openclaw-systemjob-m7-atlas-master-heartbeat.timer
15:42:20 openclaw-systemjob-mc-task-parity-check.timer
```

## Live observation after change

Observation window: `15:24:59–15:35:00 CEST`.

Important nuance: the first monitor warnings at 15:24/15:26/15:28 referenced an older Gateway event from `15:20:35`, before the change took effect:

```text
latest="...15:20:35.167+02:00 [diagnostic] liveness warning: reasons=event_loop_delay ..."
```

After the old event left the 10-minute lookback, monitor returned to OK:

```text
15:30:42 gateway_runtime_signal=ok lookback_min=10 count=0
15:32:42 gateway_runtime_signal=ok lookback_min=10 count=0
15:34:42 gateway_runtime_signal=ok lookback_min=10 count=0
```

The staggered systemJob starts occurred as intended:

```text
15:30:06 start/finish mcp-zombie-killer
15:30:21 start m7-atlas-master-heartbeat
15:30:22 finish m7-atlas-master-heartbeat
15:30:51 start atlas-receipt-stream-subscribe
15:30:59 finish atlas-receipt-stream-subscribe
15:32:21 start mc-task-parity-check
15:34:11 finish mc-task-parity-check
```

No Gateway signal lines were present in the final `Gateway signals:` section for the post-change observation window.

## Final post-check

Gateway health:

```json
{"ok":true,"status":"live"}
```

Mission Control `/api/health`:

```text
status=ok
openTasks=0
staleOpenTasks=0
orphanedDispatches=0
recoveryLoad=0
attentionCount=0
```

Systemd user failed units:

```text
0 loaded units listed.
```

## Rollback

If rollback is needed:

```bash
TS=20260505T132410Z
cp /home/piet/.config/systemd/user/openclaw-systemjob-mc-task-parity-check.timer.bak-$TS \
   /home/piet/.config/systemd/user/openclaw-systemjob-mc-task-parity-check.timer
cp /home/piet/.config/systemd/user/openclaw-systemjob-mcp-zombie-killer-10min.timer.bak-$TS \
   /home/piet/.config/systemd/user/openclaw-systemjob-mcp-zombie-killer-10min.timer
cp /home/piet/.config/systemd/user/openclaw-systemjob-m7-atlas-master-heartbeat.timer.bak-$TS \
   /home/piet/.config/systemd/user/openclaw-systemjob-m7-atlas-master-heartbeat.timer
cp /home/piet/.config/systemd/user/openclaw-systemjob-atlas-receipt-stream-subscribe.timer.bak-$TS \
   /home/piet/.config/systemd/user/openclaw-systemjob-atlas-receipt-stream-subscribe.timer
systemctl --user daemon-reload
systemctl --user restart \
  openclaw-systemjob-mc-task-parity-check.timer \
  openclaw-systemjob-mcp-zombie-killer-10min.timer \
  openclaw-systemjob-m7-atlas-master-heartbeat.timer \
  openclaw-systemjob-atlas-receipt-stream-subscribe.timer
```

## Result

SystemJob cluster was successfully staggered. Post-change observation showed intended separated starts and `gateway_runtime_signal=ok` after the older pre-change event left the monitor lookback window.
