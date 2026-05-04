

# 2h Atlas/Forge stability extension

Start UTC: 2026-05-04T16:48:08.565848+00:00
End UTC: 2026-05-04T18:48:08.565848+00:00
Tasks: 53895866-c9f5-482b-a336-a92c31485141, 716dd0d3-4160-4efd-a116-460d3301a32d


## Sample 0 2026-05-04T16:48:09.803644+00:00

```text
UTC 2026-05-04T16:48:09.803644+00:00
MC: {"status":"ok","openTasks":null,"inProgress":null,"pendingPickup":null,"staleOpenTasks":null,"orphanedDispatches":0}
Gateway: {"ok":true,"status":"live"}
Guard: 
GatewaySignalsSinceFix=0 MCSignalsSinceFix=0
Tasks:
- main 53895866 status=pending-pickup/queued/None runs=running:main:53895866-c9f5-482b-a336-a92c31485141 result=-
- sre-expert 716dd0d3 status=pending-pickup/queued/None runs=running:gateway:716dd0d3-4160-4efd-a116-460d3301a32d result=-
WorkerServices:
-
GatewayTail:
-
MCTail:
-
```

## Sample 1 2026-05-04T16:53:10.904583+00:00

```text
UTC 2026-05-04T16:53:10.904583+00:00
MC: {"status":"ok","openTasks":null,"inProgress":null,"pendingPickup":null,"staleOpenTasks":null,"orphanedDispatches":0}
Gateway: {"ok":true,"status":"live"}
Guard: 
GatewaySignalsSinceFix=0 MCSignalsSinceFix=1
Tasks:
- main 53895866 status=in-progress/active/accepted runs=running:agent:main result=-
- sre-expert 716dd0d3 status=done/done/result runs=succeeded:gateway:716dd0d3-4160-4efd-a116-460d3301a32d result=Forge 2h stability RCA: Claim/Progress/Result-Pfad funktioniert; Hauptsignal bleibt reproduzierbarer 401-Auth-Fail im nested local embedded/API-key Fallback, ni
WorkerServices:
mc-worker-main-53895866-c9f-1777913341.service loaded active running Mission Control worker main 53895866
GatewayTail:
-
MCTail:
26:May 04 18:52:30 huebners node[1262382]: [task-reports] atlas-ping-skipped {
```


# Corrected 2h monitor restart
Start UTC: 2026-05-04T16:56:55.428950+00:00
End UTC: 2026-05-04T18:56:55.428950+00:00
Reason: previous extension monitor used obsolete guard flags; corrected to parse real guard output.


## Corrected sample 0 2026-05-04T16:56:56.631613+00:00

```text
UTC 2026-05-04T16:56:56.631613+00:00
MC {"status":"ok","openTasks":null,"inProgress":null,"pendingPickup":null,"staleOpenTasks":null,"orphanedDispatches":0}
Gateway {"ok":true,"status":"live"}
Guard {"ok": true, "rotationNeeded": 0, "staleRunning": 0, "loadErrors": 0, "wouldRotateSessionKeys": []}
GatewaySignalsSinceFix=0 MCSignalsSinceFix=1
Tasks:
- main 53895866 in-progress/active/accepted runs=running:agent:main report=False atlasPingedAt=False result=-
- sre-expert 716dd0d3 done/done/result runs=succeeded:gateway:716dd0d3-4160-4efd-a116-460d3301a32d report=True atlasPingedAt=True result=Forge 2h stability RCA: Claim/Progress/Result-Pfad funktioniert; Hauptsignal bleibt reproduzierbarer 401-Auth-Fail im nested local embedded/API-key Fallback, nicht produktive Disco
WorkerServices:
mc-worker-main-53895866-c9f-1777913341.service loaded active running Mission Control worker main 53895866
GatewayTail:
-
MCTail:
26:May 04 18:52:30 huebners node[1262382]: [task-reports] atlas-ping-skipped {
```

## Corrected sample 1 2026-05-04T17:01:57.572015+00:00

```text
UTC 2026-05-04T17:01:57.572015+00:00
MC {"status":"ok","openTasks":null,"inProgress":null,"pendingPickup":null,"staleOpenTasks":null,"orphanedDispatches":0}
Gateway {"ok":true,"status":"live"}
Guard {"ok": true, "rotationNeeded": 0, "staleRunning": 0, "loadErrors": 0, "wouldRotateSessionKeys": []}
GatewaySignalsSinceFix=0 MCSignalsSinceFix=1
Tasks:
- main 53895866 in-progress/active/accepted runs=running:agent:main report=False atlasPingedAt=False result=-
- sre-expert 716dd0d3 done/done/result runs=succeeded:gateway:716dd0d3-4160-4efd-a116-460d3301a32d report=True atlasPingedAt=True result=Forge 2h stability RCA: Claim/Progress/Result-Pfad funktioniert; Hauptsignal bleibt reproduzierbarer 401-Auth-Fail im nested local embedded/API-key Fallback, nicht produktive Disco
WorkerServices:
mc-worker-main-53895866-c9f-1777913341.service loaded active running Mission Control worker main 53895866
GatewayTail:
-
MCTail:
26:May 04 18:52:30 huebners node[1262382]: [task-reports] atlas-ping-skipped {
```

## Corrected sample 2 2026-05-04T17:06:58.340742+00:00

```text
UTC 2026-05-04T17:06:58.340742+00:00
MC {"status":"ok","openTasks":null,"inProgress":null,"pendingPickup":null,"staleOpenTasks":null,"orphanedDispatches":0}
Gateway {"ok":true,"status":"live"}
Guard {"ok": true, "rotationNeeded": 0, "staleRunning": 0, "loadErrors": 0, "wouldRotateSessionKeys": []}
GatewaySignalsSinceFix=0 MCSignalsSinceFix=1
Tasks:
- main 53895866 in-progress/active/progress runs=running:agent:main report=False atlasPingedAt=False result=-
- sre-expert 716dd0d3 done/done/result runs=succeeded:gateway:716dd0d3-4160-4efd-a116-460d3301a32d report=True atlasPingedAt=True result=Forge 2h stability RCA: Claim/Progress/Result-Pfad funktioniert; Hauptsignal bleibt reproduzierbarer 401-Auth-Fail im nested local embedded/API-key Fallback, nicht produktive Disco
WorkerServices:
mc-worker-main-53895866-c9f-1777913341.service       loaded active running Mission Control worker main 53895866
  mc-worker-sre-expert-99bd3b9e-fb8-1777914377.service loaded active running Mission Control worker sre-expert 99bd3b9e
GatewayTail:
-
MCTail:
26:May 04 18:52:30 huebners node[1262382]: [task-reports] atlas-ping-skipped {
```
