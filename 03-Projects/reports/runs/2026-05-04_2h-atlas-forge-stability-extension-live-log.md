

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

## Corrected sample 3 2026-05-04T17:11:59.047253+00:00

```text
UTC 2026-05-04T17:11:59.047253+00:00
MC {"status":"ok","openTasks":null,"inProgress":null,"pendingPickup":null,"staleOpenTasks":null,"orphanedDispatches":0}
Gateway {"ok":true,"status":"live"}
Guard {"ok": true, "rotationNeeded": 0, "staleRunning": 0, "loadErrors": 0, "wouldRotateSessionKeys": []}
GatewaySignalsSinceFix=0 MCSignalsSinceFix=2
Tasks:
- main 53895866 in-progress/active/progress runs=running:agent:main report=False atlasPingedAt=False result=-
- sre-expert 716dd0d3 done/done/result runs=succeeded:gateway:716dd0d3-4160-4efd-a116-460d3301a32d report=True atlasPingedAt=True result=Forge 2h stability RCA: Claim/Progress/Result-Pfad funktioniert; Hauptsignal bleibt reproduzierbarer 401-Auth-Fail im nested local embedded/API-key Fallback, nicht produktive Disco
WorkerServices:
mc-worker-main-53895866-c9f-1777913341.service loaded active running Mission Control worker main 53895866
GatewayTail:
-
MCTail:
26:May 04 18:52:30 huebners node[1262382]: [task-reports] atlas-ping-skipped {
38:May 04 19:07:24 huebners node[1262382]: [task-reports] atlas-ping-skipped {
```

## Corrected sample 4 2026-05-04T17:17:01.873720+00:00

```text
UTC 2026-05-04T17:17:01.873720+00:00
MC {"status":"ok","openTasks":null,"inProgress":null,"pendingPickup":null,"staleOpenTasks":null,"orphanedDispatches":0}
Gateway {"ok":true,"status":"live"}
Guard {"ok": true, "rotationNeeded": 0, "staleRunning": 0, "loadErrors": 0, "wouldRotateSessionKeys": []}
GatewaySignalsSinceFix=5 MCSignalsSinceFix=3
Tasks:
- main 53895866 failed/failed/failed runs=failed:agent:main report=True atlasPingedAt=True result=-
- sre-expert 716dd0d3 done/done/result runs=succeeded:gateway:716dd0d3-4160-4efd-a116-460d3301a32d report=True atlasPingedAt=True result=Forge 2h stability RCA: Claim/Progress/Result-Pfad funktioniert; Hauptsignal bleibt reproduzierbarer 401-Auth-Fail im nested local embedded/API-key Fallback, nicht produktive Disco
WorkerServices:
mc-worker-main-53895866-c9f-1777913341.service loaded active running Mission Control worker main 53895866
GatewayTail:
43:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.460+02:00 [agent/embedded] embedded run failover decision: runId=25b5d110-3b19-4d51-aff9-6ffe7e0255fe stage=assistant decision=fallback_model reason=timeout from=openai/gpt-5.5 profile=sha256:195d21b1dd7f rawError=codex app-server attempt timed out
44:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.462+02:00 [diagnostic] lane task error: lane=main durationMs=1500875 error="FailoverError: LLM request timed out."
45:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.463+02:00 [diagnostic] lane task error: lane=session:agent:main:main durationMs=1500876 error="FailoverError: LLM request timed out."
46:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.466+02:00 [model-fallback/decision] model fallback decision: decision=candidate_failed requested=openai/gpt-5.5 candidate=openai/gpt-5.5 reason=timeout next=openai/gpt-5.3-codex detail=codex app-server attempt timed out
48:May 04 19:15:40 huebners node[1210995]: 2026-05-04T19:15:40.789+02:00 [model-fallback/decision] model fallback decision: decision=candidate_succeeded requested=openai/gpt-5.5 candidate=openai/gpt-5.3-codex reason=unknown next=none
MCTail:
26:May 04 18:52:30 huebners node[1262382]: [task-reports] atlas-ping-skipped {
38:May 04 19:07:24 huebners node[1262382]: [task-reports] atlas-ping-skipped {
43:May 04 19:15:20 huebners node[1262382]: [task-reports] atlas-ping-skipped {
```

## Corrected sample 5 2026-05-04T17:22:03.812681+00:00

```text
UTC 2026-05-04T17:22:03.812681+00:00
MC {"status":"ok","openTasks":null,"inProgress":null,"pendingPickup":null,"staleOpenTasks":null,"orphanedDispatches":0}
Gateway {"ok":true,"status":"live"}
Guard {"ok": true, "rotationNeeded": 0, "staleRunning": 0, "loadErrors": 0, "wouldRotateSessionKeys": []}
GatewaySignalsSinceFix=5 MCSignalsSinceFix=3
Tasks:
- main 53895866 failed/failed/failed runs=failed:agent:main report=True atlasPingedAt=True result=-
- sre-expert 716dd0d3 done/done/result runs=succeeded:gateway:716dd0d3-4160-4efd-a116-460d3301a32d report=True atlasPingedAt=True result=Forge 2h stability RCA: Claim/Progress/Result-Pfad funktioniert; Hauptsignal bleibt reproduzierbarer 401-Auth-Fail im nested local embedded/API-key Fallback, nicht produktive Disco
WorkerServices:
mc-worker-main-43603d8c-234-1777915278.service loaded active running Mission Control worker main 43603d8c
GatewayTail:
43:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.460+02:00 [agent/embedded] embedded run failover decision: runId=25b5d110-3b19-4d51-aff9-6ffe7e0255fe stage=assistant decision=fallback_model reason=timeout from=openai/gpt-5.5 profile=sha256:195d21b1dd7f rawError=codex app-server attempt timed out
44:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.462+02:00 [diagnostic] lane task error: lane=main durationMs=1500875 error="FailoverError: LLM request timed out."
45:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.463+02:00 [diagnostic] lane task error: lane=session:agent:main:main durationMs=1500876 error="FailoverError: LLM request timed out."
46:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.466+02:00 [model-fallback/decision] model fallback decision: decision=candidate_failed requested=openai/gpt-5.5 candidate=openai/gpt-5.5 reason=timeout next=openai/gpt-5.3-codex detail=codex app-server attempt timed out
48:May 04 19:15:40 huebners node[1210995]: 2026-05-04T19:15:40.789+02:00 [model-fallback/decision] model fallback decision: decision=candidate_succeeded requested=openai/gpt-5.5 candidate=openai/gpt-5.3-codex reason=unknown next=none
MCTail:
26:May 04 18:52:30 huebners node[1262382]: [task-reports] atlas-ping-skipped {
38:May 04 19:07:24 huebners node[1262382]: [task-reports] atlas-ping-skipped {
43:May 04 19:15:20 huebners node[1262382]: [task-reports] atlas-ping-skipped {
```

## Corrected sample 6 2026-05-04T17:27:05.554433+00:00

```text
UTC 2026-05-04T17:27:05.554433+00:00
MC {"status":"ok","openTasks":null,"inProgress":null,"pendingPickup":null,"staleOpenTasks":null,"orphanedDispatches":0}
Gateway {"ok":true,"status":"live"}
Guard {"ok": true, "rotationNeeded": 0, "staleRunning": 0, "loadErrors": 0, "wouldRotateSessionKeys": []}
GatewaySignalsSinceFix=5 MCSignalsSinceFix=3
Tasks:
- main 53895866 failed/failed/failed runs=failed:agent:main report=True atlasPingedAt=True result=-
- sre-expert 716dd0d3 done/done/result runs=succeeded:gateway:716dd0d3-4160-4efd-a116-460d3301a32d report=True atlasPingedAt=True result=Forge 2h stability RCA: Claim/Progress/Result-Pfad funktioniert; Hauptsignal bleibt reproduzierbarer 401-Auth-Fail im nested local embedded/API-key Fallback, nicht produktive Disco
WorkerServices:
mc-worker-main-43603d8c-234-1777915278.service loaded active running Mission Control worker main 43603d8c
GatewayTail:
43:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.460+02:00 [agent/embedded] embedded run failover decision: runId=25b5d110-3b19-4d51-aff9-6ffe7e0255fe stage=assistant decision=fallback_model reason=timeout from=openai/gpt-5.5 profile=sha256:195d21b1dd7f rawError=codex app-server attempt timed out
44:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.462+02:00 [diagnostic] lane task error: lane=main durationMs=1500875 error="FailoverError: LLM request timed out."
45:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.463+02:00 [diagnostic] lane task error: lane=session:agent:main:main durationMs=1500876 error="FailoverError: LLM request timed out."
46:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.466+02:00 [model-fallback/decision] model fallback decision: decision=candidate_failed requested=openai/gpt-5.5 candidate=openai/gpt-5.5 reason=timeout next=openai/gpt-5.3-codex detail=codex app-server attempt timed out
48:May 04 19:15:40 huebners node[1210995]: 2026-05-04T19:15:40.789+02:00 [model-fallback/decision] model fallback decision: decision=candidate_succeeded requested=openai/gpt-5.5 candidate=openai/gpt-5.3-codex reason=unknown next=none
MCTail:
26:May 04 18:52:30 huebners node[1262382]: [task-reports] atlas-ping-skipped {
38:May 04 19:07:24 huebners node[1262382]: [task-reports] atlas-ping-skipped {
43:May 04 19:15:20 huebners node[1262382]: [task-reports] atlas-ping-skipped {
```

## Corrected sample 7 2026-05-04T17:32:06.656155+00:00

```text
UTC 2026-05-04T17:32:06.656155+00:00
MC {"status":"ok","openTasks":null,"inProgress":null,"pendingPickup":null,"staleOpenTasks":null,"orphanedDispatches":0}
Gateway {"ok":true,"status":"live"}
Guard {"ok": true, "rotationNeeded": 0, "staleRunning": 0, "loadErrors": 0, "wouldRotateSessionKeys": []}
GatewaySignalsSinceFix=5 MCSignalsSinceFix=3
Tasks:
- main 53895866 failed/failed/failed runs=failed:agent:main report=True atlasPingedAt=True result=-
- sre-expert 716dd0d3 done/done/result runs=succeeded:gateway:716dd0d3-4160-4efd-a116-460d3301a32d report=True atlasPingedAt=True result=Forge 2h stability RCA: Claim/Progress/Result-Pfad funktioniert; Hauptsignal bleibt reproduzierbarer 401-Auth-Fail im nested local embedded/API-key Fallback, nicht produktive Disco
WorkerServices:
mc-worker-main-43603d8c-234-1777915278.service loaded active running Mission Control worker main 43603d8c
GatewayTail:
43:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.460+02:00 [agent/embedded] embedded run failover decision: runId=25b5d110-3b19-4d51-aff9-6ffe7e0255fe stage=assistant decision=fallback_model reason=timeout from=openai/gpt-5.5 profile=sha256:195d21b1dd7f rawError=codex app-server attempt timed out
44:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.462+02:00 [diagnostic] lane task error: lane=main durationMs=1500875 error="FailoverError: LLM request timed out."
45:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.463+02:00 [diagnostic] lane task error: lane=session:agent:main:main durationMs=1500876 error="FailoverError: LLM request timed out."
46:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.466+02:00 [model-fallback/decision] model fallback decision: decision=candidate_failed requested=openai/gpt-5.5 candidate=openai/gpt-5.5 reason=timeout next=openai/gpt-5.3-codex detail=codex app-server attempt timed out
48:May 04 19:15:40 huebners node[1210995]: 2026-05-04T19:15:40.789+02:00 [model-fallback/decision] model fallback decision: decision=candidate_succeeded requested=openai/gpt-5.5 candidate=openai/gpt-5.3-codex reason=unknown next=none
MCTail:
26:May 04 18:52:30 huebners node[1262382]: [task-reports] atlas-ping-skipped {
38:May 04 19:07:24 huebners node[1262382]: [task-reports] atlas-ping-skipped {
43:May 04 19:15:20 huebners node[1262382]: [task-reports] atlas-ping-skipped {
```

## Corrected sample 8 2026-05-04T17:37:08.042552+00:00

```text
UTC 2026-05-04T17:37:08.042552+00:00
MC {"status":"ok","openTasks":null,"inProgress":null,"pendingPickup":null,"staleOpenTasks":null,"orphanedDispatches":0}
Gateway {"ok":true,"status":"live"}
Guard {"ok": false, "rotationNeeded": 1, "staleRunning": 1, "loadErrors": 0, "wouldRotateSessionKeys": ["agent:james:discord:channel:1487930174384247005"]}
GatewaySignalsSinceFix=5 MCSignalsSinceFix=4
Tasks:
- main 53895866 failed/failed/failed runs=failed:agent:main report=True atlasPingedAt=True result=-
- sre-expert 716dd0d3 done/done/result runs=succeeded:gateway:716dd0d3-4160-4efd-a116-460d3301a32d report=True atlasPingedAt=True result=Forge 2h stability RCA: Claim/Progress/Result-Pfad funktioniert; Hauptsignal bleibt reproduzierbarer 401-Auth-Fail im nested local embedded/API-key Fallback, nicht produktive Disco
WorkerServices:
-
GatewayTail:
43:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.460+02:00 [agent/embedded] embedded run failover decision: runId=25b5d110-3b19-4d51-aff9-6ffe7e0255fe stage=assistant decision=fallback_model reason=timeout from=openai/gpt-5.5 profile=sha256:195d21b1dd7f rawError=codex app-server attempt timed out
44:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.462+02:00 [diagnostic] lane task error: lane=main durationMs=1500875 error="FailoverError: LLM request timed out."
45:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.463+02:00 [diagnostic] lane task error: lane=session:agent:main:main durationMs=1500876 error="FailoverError: LLM request timed out."
46:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.466+02:00 [model-fallback/decision] model fallback decision: decision=candidate_failed requested=openai/gpt-5.5 candidate=openai/gpt-5.5 reason=timeout next=openai/gpt-5.3-codex detail=codex app-server attempt timed out
48:May 04 19:15:40 huebners node[1210995]: 2026-05-04T19:15:40.789+02:00 [model-fallback/decision] model fallback decision: decision=candidate_succeeded requested=openai/gpt-5.5 candidate=openai/gpt-5.3-codex reason=unknown next=none
MCTail:
26:May 04 18:52:30 huebners node[1262382]: [task-reports] atlas-ping-skipped {
38:May 04 19:07:24 huebners node[1262382]: [task-reports] atlas-ping-skipped {
43:May 04 19:15:20 huebners node[1262382]: [task-reports] atlas-ping-skipped {
70:May 04 19:33:58 huebners node[1262382]: [task-reports] atlas-ping-skipped {
```

## Corrected sample 9 2026-05-04T17:42:09.223348+00:00

```text
UTC 2026-05-04T17:42:09.223348+00:00
MC {"status":"ok","openTasks":null,"inProgress":null,"pendingPickup":null,"staleOpenTasks":null,"orphanedDispatches":0}
Gateway {"ok":true,"status":"live"}
Guard {"ok": false, "rotationNeeded": 1, "staleRunning": 1, "loadErrors": 0, "wouldRotateSessionKeys": ["agent:james:discord:channel:1487930174384247005"]}
GatewaySignalsSinceFix=5 MCSignalsSinceFix=4
Tasks:
- main 53895866 failed/failed/failed runs=failed:agent:main report=True atlasPingedAt=True result=-
- sre-expert 716dd0d3 done/done/result runs=succeeded:gateway:716dd0d3-4160-4efd-a116-460d3301a32d report=True atlasPingedAt=True result=Forge 2h stability RCA: Claim/Progress/Result-Pfad funktioniert; Hauptsignal bleibt reproduzierbarer 401-Auth-Fail im nested local embedded/API-key Fallback, nicht produktive Disco
WorkerServices:
mc-worker-main-ed95322d-2ca-1777916478.service       loaded active running Mission Control worker main ed95322d
  mc-worker-sre-expert-4b74db72-852-1777916521.service loaded active running Mission Control worker sre-expert 4b74db72
GatewayTail:
43:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.460+02:00 [agent/embedded] embedded run failover decision: runId=25b5d110-3b19-4d51-aff9-6ffe7e0255fe stage=assistant decision=fallback_model reason=timeout from=openai/gpt-5.5 profile=sha256:195d21b1dd7f rawError=codex app-server attempt timed out
44:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.462+02:00 [diagnostic] lane task error: lane=main durationMs=1500875 error="FailoverError: LLM request timed out."
45:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.463+02:00 [diagnostic] lane task error: lane=session:agent:main:main durationMs=1500876 error="FailoverError: LLM request timed out."
46:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.466+02:00 [model-fallback/decision] model fallback decision: decision=candidate_failed requested=openai/gpt-5.5 candidate=openai/gpt-5.5 reason=timeout next=openai/gpt-5.3-codex detail=codex app-server attempt timed out
48:May 04 19:15:40 huebners node[1210995]: 2026-05-04T19:15:40.789+02:00 [model-fallback/decision] model fallback decision: decision=candidate_succeeded requested=openai/gpt-5.5 candidate=openai/gpt-5.3-codex reason=unknown next=none
MCTail:
26:May 04 18:52:30 huebners node[1262382]: [task-reports] atlas-ping-skipped {
38:May 04 19:07:24 huebners node[1262382]: [task-reports] atlas-ping-skipped {
43:May 04 19:15:20 huebners node[1262382]: [task-reports] atlas-ping-skipped {
70:May 04 19:33:58 huebners node[1262382]: [task-reports] atlas-ping-skipped {
```

## Corrected sample 10 2026-05-04T17:47:10.530222+00:00

```text
UTC 2026-05-04T17:47:10.530222+00:00
MC {"status":"ok","openTasks":null,"inProgress":null,"pendingPickup":null,"staleOpenTasks":null,"orphanedDispatches":0}
Gateway {"ok":true,"status":"live"}
Guard {"ok": false, "rotationNeeded": 1, "staleRunning": 1, "loadErrors": 0, "wouldRotateSessionKeys": ["agent:james:discord:channel:1487930174384247005"]}
GatewaySignalsSinceFix=5 MCSignalsSinceFix=6
Tasks:
- main 53895866 failed/failed/failed runs=failed:agent:main report=True atlasPingedAt=True result=-
- sre-expert 716dd0d3 done/done/result runs=succeeded:gateway:716dd0d3-4160-4efd-a116-460d3301a32d report=True atlasPingedAt=True result=Forge 2h stability RCA: Claim/Progress/Result-Pfad funktioniert; Hauptsignal bleibt reproduzierbarer 401-Auth-Fail im nested local embedded/API-key Fallback, nicht produktive Disco
WorkerServices:
-
GatewayTail:
43:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.460+02:00 [agent/embedded] embedded run failover decision: runId=25b5d110-3b19-4d51-aff9-6ffe7e0255fe stage=assistant decision=fallback_model reason=timeout from=openai/gpt-5.5 profile=sha256:195d21b1dd7f rawError=codex app-server attempt timed out
44:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.462+02:00 [diagnostic] lane task error: lane=main durationMs=1500875 error="FailoverError: LLM request timed out."
45:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.463+02:00 [diagnostic] lane task error: lane=session:agent:main:main durationMs=1500876 error="FailoverError: LLM request timed out."
46:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.466+02:00 [model-fallback/decision] model fallback decision: decision=candidate_failed requested=openai/gpt-5.5 candidate=openai/gpt-5.5 reason=timeout next=openai/gpt-5.3-codex detail=codex app-server attempt timed out
48:May 04 19:15:40 huebners node[1210995]: 2026-05-04T19:15:40.789+02:00 [model-fallback/decision] model fallback decision: decision=candidate_succeeded requested=openai/gpt-5.5 candidate=openai/gpt-5.3-codex reason=unknown next=none
MCTail:
26:May 04 18:52:30 huebners node[1262382]: [task-reports] atlas-ping-skipped {
38:May 04 19:07:24 huebners node[1262382]: [task-reports] atlas-ping-skipped {
43:May 04 19:15:20 huebners node[1262382]: [task-reports] atlas-ping-skipped {
70:May 04 19:33:58 huebners node[1262382]: [task-reports] atlas-ping-skipped {
88:May 04 19:42:55 huebners node[1262382]: [task-reports] atlas-ping-skipped {
93:May 04 19:46:10 huebners node[1262382]: [task-reports] atlas-ping-skipped {
```

## Corrected sample 11 2026-05-04T17:52:11.859405+00:00

```text
UTC 2026-05-04T17:52:11.859405+00:00
MC {"status":"ok","openTasks":null,"inProgress":null,"pendingPickup":null,"staleOpenTasks":null,"orphanedDispatches":0}
Gateway {"ok":true,"status":"live"}
Guard {"ok": true, "rotationNeeded": 0, "staleRunning": 0, "loadErrors": 0, "wouldRotateSessionKeys": []}
GatewaySignalsSinceFix=5 MCSignalsSinceFix=6
Tasks:
- main 53895866 failed/failed/failed runs=failed:agent:main report=True atlasPingedAt=True result=-
- sre-expert 716dd0d3 done/done/result runs=succeeded:gateway:716dd0d3-4160-4efd-a116-460d3301a32d report=True atlasPingedAt=True result=Forge 2h stability RCA: Claim/Progress/Result-Pfad funktioniert; Hauptsignal bleibt reproduzierbarer 401-Auth-Fail im nested local embedded/API-key Fallback, nicht produktive Disco
WorkerServices:
-
GatewayTail:
43:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.460+02:00 [agent/embedded] embedded run failover decision: runId=25b5d110-3b19-4d51-aff9-6ffe7e0255fe stage=assistant decision=fallback_model reason=timeout from=openai/gpt-5.5 profile=sha256:195d21b1dd7f rawError=codex app-server attempt timed out
44:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.462+02:00 [diagnostic] lane task error: lane=main durationMs=1500875 error="FailoverError: LLM request timed out."
45:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.463+02:00 [diagnostic] lane task error: lane=session:agent:main:main durationMs=1500876 error="FailoverError: LLM request timed out."
46:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.466+02:00 [model-fallback/decision] model fallback decision: decision=candidate_failed requested=openai/gpt-5.5 candidate=openai/gpt-5.5 reason=timeout next=openai/gpt-5.3-codex detail=codex app-server attempt timed out
48:May 04 19:15:40 huebners node[1210995]: 2026-05-04T19:15:40.789+02:00 [model-fallback/decision] model fallback decision: decision=candidate_succeeded requested=openai/gpt-5.5 candidate=openai/gpt-5.3-codex reason=unknown next=none
MCTail:
26:May 04 18:52:30 huebners node[1262382]: [task-reports] atlas-ping-skipped {
38:May 04 19:07:24 huebners node[1262382]: [task-reports] atlas-ping-skipped {
43:May 04 19:15:20 huebners node[1262382]: [task-reports] atlas-ping-skipped {
70:May 04 19:33:58 huebners node[1262382]: [task-reports] atlas-ping-skipped {
88:May 04 19:42:55 huebners node[1262382]: [task-reports] atlas-ping-skipped {
93:May 04 19:46:10 huebners node[1262382]: [task-reports] atlas-ping-skipped {
```

## Corrected sample 12 2026-05-04T17:57:13.068890+00:00

```text
UTC 2026-05-04T17:57:13.068890+00:00
MC {"status":"ok","openTasks":null,"inProgress":null,"pendingPickup":null,"staleOpenTasks":null,"orphanedDispatches":0}
Gateway {"ok":true,"status":"live"}
Guard {"ok": true, "rotationNeeded": 0, "staleRunning": 0, "loadErrors": 0, "wouldRotateSessionKeys": []}
GatewaySignalsSinceFix=5 MCSignalsSinceFix=7
Tasks:
- main 53895866 failed/failed/failed runs=failed:agent:main report=True atlasPingedAt=True result=-
- sre-expert 716dd0d3 done/done/result runs=succeeded:gateway:716dd0d3-4160-4efd-a116-460d3301a32d report=True atlasPingedAt=True result=Forge 2h stability RCA: Claim/Progress/Result-Pfad funktioniert; Hauptsignal bleibt reproduzierbarer 401-Auth-Fail im nested local embedded/API-key Fallback, nicht produktive Disco
WorkerServices:
-
GatewayTail:
43:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.460+02:00 [agent/embedded] embedded run failover decision: runId=25b5d110-3b19-4d51-aff9-6ffe7e0255fe stage=assistant decision=fallback_model reason=timeout from=openai/gpt-5.5 profile=sha256:195d21b1dd7f rawError=codex app-server attempt timed out
44:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.462+02:00 [diagnostic] lane task error: lane=main durationMs=1500875 error="FailoverError: LLM request timed out."
45:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.463+02:00 [diagnostic] lane task error: lane=session:agent:main:main durationMs=1500876 error="FailoverError: LLM request timed out."
46:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.466+02:00 [model-fallback/decision] model fallback decision: decision=candidate_failed requested=openai/gpt-5.5 candidate=openai/gpt-5.5 reason=timeout next=openai/gpt-5.3-codex detail=codex app-server attempt timed out
48:May 04 19:15:40 huebners node[1210995]: 2026-05-04T19:15:40.789+02:00 [model-fallback/decision] model fallback decision: decision=candidate_succeeded requested=openai/gpt-5.5 candidate=openai/gpt-5.3-codex reason=unknown next=none
MCTail:
26:May 04 18:52:30 huebners node[1262382]: [task-reports] atlas-ping-skipped {
38:May 04 19:07:24 huebners node[1262382]: [task-reports] atlas-ping-skipped {
43:May 04 19:15:20 huebners node[1262382]: [task-reports] atlas-ping-skipped {
70:May 04 19:33:58 huebners node[1262382]: [task-reports] atlas-ping-skipped {
88:May 04 19:42:55 huebners node[1262382]: [task-reports] atlas-ping-skipped {
93:May 04 19:46:10 huebners node[1262382]: [task-reports] atlas-ping-skipped {
107:May 04 19:55:18 huebners node[1262382]: [task-reports] atlas-ping-skipped {
```

## Corrected sample 13 2026-05-04T18:02:14.132583+00:00

```text
UTC 2026-05-04T18:02:14.132583+00:00
MC {"status":"ok","openTasks":null,"inProgress":null,"pendingPickup":null,"staleOpenTasks":null,"orphanedDispatches":0}
Gateway {"ok":true,"status":"live"}
Guard {"ok": true, "rotationNeeded": 0, "staleRunning": 0, "loadErrors": 0, "wouldRotateSessionKeys": []}
GatewaySignalsSinceFix=5 MCSignalsSinceFix=7
Tasks:
- main 53895866 failed/failed/failed runs=failed:agent:main report=True atlasPingedAt=True result=-
- sre-expert 716dd0d3 done/done/result runs=succeeded:gateway:716dd0d3-4160-4efd-a116-460d3301a32d report=True atlasPingedAt=True result=Forge 2h stability RCA: Claim/Progress/Result-Pfad funktioniert; Hauptsignal bleibt reproduzierbarer 401-Auth-Fail im nested local embedded/API-key Fallback, nicht produktive Disco
WorkerServices:
-
GatewayTail:
43:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.460+02:00 [agent/embedded] embedded run failover decision: runId=25b5d110-3b19-4d51-aff9-6ffe7e0255fe stage=assistant decision=fallback_model reason=timeout from=openai/gpt-5.5 profile=sha256:195d21b1dd7f rawError=codex app-server attempt timed out
44:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.462+02:00 [diagnostic] lane task error: lane=main durationMs=1500875 error="FailoverError: LLM request timed out."
45:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.463+02:00 [diagnostic] lane task error: lane=session:agent:main:main durationMs=1500876 error="FailoverError: LLM request timed out."
46:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.466+02:00 [model-fallback/decision] model fallback decision: decision=candidate_failed requested=openai/gpt-5.5 candidate=openai/gpt-5.5 reason=timeout next=openai/gpt-5.3-codex detail=codex app-server attempt timed out
48:May 04 19:15:40 huebners node[1210995]: 2026-05-04T19:15:40.789+02:00 [model-fallback/decision] model fallback decision: decision=candidate_succeeded requested=openai/gpt-5.5 candidate=openai/gpt-5.3-codex reason=unknown next=none
MCTail:
26:May 04 18:52:30 huebners node[1262382]: [task-reports] atlas-ping-skipped {
38:May 04 19:07:24 huebners node[1262382]: [task-reports] atlas-ping-skipped {
43:May 04 19:15:20 huebners node[1262382]: [task-reports] atlas-ping-skipped {
70:May 04 19:33:58 huebners node[1262382]: [task-reports] atlas-ping-skipped {
88:May 04 19:42:55 huebners node[1262382]: [task-reports] atlas-ping-skipped {
93:May 04 19:46:10 huebners node[1262382]: [task-reports] atlas-ping-skipped {
107:May 04 19:55:18 huebners node[1262382]: [task-reports] atlas-ping-skipped {
```

## Corrected sample 14 2026-05-04T18:07:15.370366+00:00

```text
UTC 2026-05-04T18:07:15.370366+00:00
MC {"status":"ok","openTasks":null,"inProgress":null,"pendingPickup":null,"staleOpenTasks":null,"orphanedDispatches":0}
Gateway {"ok":true,"status":"live"}
Guard {"ok": true, "rotationNeeded": 0, "staleRunning": 0, "loadErrors": 0, "wouldRotateSessionKeys": []}
GatewaySignalsSinceFix=5 MCSignalsSinceFix=8
Tasks:
- main 53895866 failed/failed/failed runs=failed:agent:main report=True atlasPingedAt=True result=-
- sre-expert 716dd0d3 done/done/result runs=succeeded:gateway:716dd0d3-4160-4efd-a116-460d3301a32d report=True atlasPingedAt=True result=Forge 2h stability RCA: Claim/Progress/Result-Pfad funktioniert; Hauptsignal bleibt reproduzierbarer 401-Auth-Fail im nested local embedded/API-key Fallback, nicht produktive Disco
WorkerServices:
-
GatewayTail:
43:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.460+02:00 [agent/embedded] embedded run failover decision: runId=25b5d110-3b19-4d51-aff9-6ffe7e0255fe stage=assistant decision=fallback_model reason=timeout from=openai/gpt-5.5 profile=sha256:195d21b1dd7f rawError=codex app-server attempt timed out
44:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.462+02:00 [diagnostic] lane task error: lane=main durationMs=1500875 error="FailoverError: LLM request timed out."
45:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.463+02:00 [diagnostic] lane task error: lane=session:agent:main:main durationMs=1500876 error="FailoverError: LLM request timed out."
46:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.466+02:00 [model-fallback/decision] model fallback decision: decision=candidate_failed requested=openai/gpt-5.5 candidate=openai/gpt-5.5 reason=timeout next=openai/gpt-5.3-codex detail=codex app-server attempt timed out
48:May 04 19:15:40 huebners node[1210995]: 2026-05-04T19:15:40.789+02:00 [model-fallback/decision] model fallback decision: decision=candidate_succeeded requested=openai/gpt-5.5 candidate=openai/gpt-5.3-codex reason=unknown next=none
MCTail:
26:May 04 18:52:30 huebners node[1262382]: [task-reports] atlas-ping-skipped {
38:May 04 19:07:24 huebners node[1262382]: [task-reports] atlas-ping-skipped {
43:May 04 19:15:20 huebners node[1262382]: [task-reports] atlas-ping-skipped {
70:May 04 19:33:58 huebners node[1262382]: [task-reports] atlas-ping-skipped {
88:May 04 19:42:55 huebners node[1262382]: [task-reports] atlas-ping-skipped {
93:May 04 19:46:10 huebners node[1262382]: [task-reports] atlas-ping-skipped {
107:May 04 19:55:18 huebners node[1262382]: [task-reports] atlas-ping-skipped {
122:May 04 20:04:44 huebners node[1262382]: [task-reports] atlas-ping-skipped {
```

## Corrected sample 15 2026-05-04T18:12:16.775639+00:00

```text
UTC 2026-05-04T18:12:16.775639+00:00
MC {"status":"ok","openTasks":null,"inProgress":null,"pendingPickup":null,"staleOpenTasks":null,"orphanedDispatches":0}
Gateway {"ok":true,"status":"live"}
Guard {"ok": true, "rotationNeeded": 0, "staleRunning": 0, "loadErrors": 0, "wouldRotateSessionKeys": []}
GatewaySignalsSinceFix=5 MCSignalsSinceFix=12
Tasks:
- main 53895866 failed/failed/failed runs=failed:agent:main report=True atlasPingedAt=True result=-
- sre-expert 716dd0d3 done/done/result runs=succeeded:gateway:716dd0d3-4160-4efd-a116-460d3301a32d report=True atlasPingedAt=True result=Forge 2h stability RCA: Claim/Progress/Result-Pfad funktioniert; Hauptsignal bleibt reproduzierbarer 401-Auth-Fail im nested local embedded/API-key Fallback, nicht produktive Disco
WorkerServices:
-
GatewayTail:
43:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.460+02:00 [agent/embedded] embedded run failover decision: runId=25b5d110-3b19-4d51-aff9-6ffe7e0255fe stage=assistant decision=fallback_model reason=timeout from=openai/gpt-5.5 profile=sha256:195d21b1dd7f rawError=codex app-server attempt timed out
44:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.462+02:00 [diagnostic] lane task error: lane=main durationMs=1500875 error="FailoverError: LLM request timed out."
45:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.463+02:00 [diagnostic] lane task error: lane=session:agent:main:main durationMs=1500876 error="FailoverError: LLM request timed out."
46:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.466+02:00 [model-fallback/decision] model fallback decision: decision=candidate_failed requested=openai/gpt-5.5 candidate=openai/gpt-5.5 reason=timeout next=openai/gpt-5.3-codex detail=codex app-server attempt timed out
48:May 04 19:15:40 huebners node[1210995]: 2026-05-04T19:15:40.789+02:00 [model-fallback/decision] model fallback decision: decision=candidate_succeeded requested=openai/gpt-5.5 candidate=openai/gpt-5.3-codex reason=unknown next=none
MCTail:
88:May 04 19:42:55 huebners node[1262382]: [task-reports] atlas-ping-skipped {
93:May 04 19:46:10 huebners node[1262382]: [task-reports] atlas-ping-skipped {
107:May 04 19:55:18 huebners node[1262382]: [task-reports] atlas-ping-skipped {
122:May 04 20:04:44 huebners node[1262382]: [task-reports] atlas-ping-skipped {
131:May 04 20:10:25 huebners node[1262382]: [task-reports] lifecycle report failed, continuing with best-effort vault writes {
134:May 04 20:10:25 huebners node[1262382]:   error: 'Failed to send report: {"message":"401: Unauthorized","code":0}'
136:May 04 20:10:36 huebners node[1262382]: [task-reports] lifecycle report failed, continuing with best-effort vault writes {
139:May 04 20:10:36 huebners node[1262382]:   error: 'Failed to send report: {"message":"401: Unauthorized","code":0}'
```

## Corrected sample 16 2026-05-04T18:17:18.023595+00:00

```text
UTC 2026-05-04T18:17:18.023595+00:00
MC {"status":"ok","openTasks":null,"inProgress":null,"pendingPickup":null,"staleOpenTasks":null,"orphanedDispatches":0}
Gateway {"ok":true,"status":"live"}
Guard {"ok": true, "rotationNeeded": 0, "staleRunning": 0, "loadErrors": 0, "wouldRotateSessionKeys": []}
GatewaySignalsSinceFix=5 MCSignalsSinceFix=12
Tasks:
- main 53895866 failed/failed/failed runs=failed:agent:main report=True atlasPingedAt=True result=-
- sre-expert 716dd0d3 done/done/result runs=succeeded:gateway:716dd0d3-4160-4efd-a116-460d3301a32d report=True atlasPingedAt=True result=Forge 2h stability RCA: Claim/Progress/Result-Pfad funktioniert; Hauptsignal bleibt reproduzierbarer 401-Auth-Fail im nested local embedded/API-key Fallback, nicht produktive Disco
WorkerServices:
mc-worker-sre-expert-33e741f7-4d0-1777918609.service loaded active running Mission Control worker sre-expert 33e741f7
GatewayTail:
43:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.460+02:00 [agent/embedded] embedded run failover decision: runId=25b5d110-3b19-4d51-aff9-6ffe7e0255fe stage=assistant decision=fallback_model reason=timeout from=openai/gpt-5.5 profile=sha256:195d21b1dd7f rawError=codex app-server attempt timed out
44:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.462+02:00 [diagnostic] lane task error: lane=main durationMs=1500875 error="FailoverError: LLM request timed out."
45:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.463+02:00 [diagnostic] lane task error: lane=session:agent:main:main durationMs=1500876 error="FailoverError: LLM request timed out."
46:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.466+02:00 [model-fallback/decision] model fallback decision: decision=candidate_failed requested=openai/gpt-5.5 candidate=openai/gpt-5.5 reason=timeout next=openai/gpt-5.3-codex detail=codex app-server attempt timed out
48:May 04 19:15:40 huebners node[1210995]: 2026-05-04T19:15:40.789+02:00 [model-fallback/decision] model fallback decision: decision=candidate_succeeded requested=openai/gpt-5.5 candidate=openai/gpt-5.3-codex reason=unknown next=none
MCTail:
88:May 04 19:42:55 huebners node[1262382]: [task-reports] atlas-ping-skipped {
93:May 04 19:46:10 huebners node[1262382]: [task-reports] atlas-ping-skipped {
107:May 04 19:55:18 huebners node[1262382]: [task-reports] atlas-ping-skipped {
122:May 04 20:04:44 huebners node[1262382]: [task-reports] atlas-ping-skipped {
131:May 04 20:10:25 huebners node[1262382]: [task-reports] lifecycle report failed, continuing with best-effort vault writes {
134:May 04 20:10:25 huebners node[1262382]:   error: 'Failed to send report: {"message":"401: Unauthorized","code":0}'
136:May 04 20:10:36 huebners node[1262382]: [task-reports] lifecycle report failed, continuing with best-effort vault writes {
139:May 04 20:10:36 huebners node[1262382]:   error: 'Failed to send report: {"message":"401: Unauthorized","code":0}'
```

## Corrected sample 17 2026-05-04T18:22:20.208394+00:00

```text
UTC 2026-05-04T18:22:20.208394+00:00
MC {"status":"ok","openTasks":null,"inProgress":null,"pendingPickup":null,"staleOpenTasks":null,"orphanedDispatches":0}
Gateway {"ok":true,"status":"live"}
Guard {"ok": true, "rotationNeeded": 0, "staleRunning": 0, "loadErrors": 0, "wouldRotateSessionKeys": []}
GatewaySignalsSinceFix=5 MCSignalsSinceFix=13
Tasks:
- main 53895866 failed/failed/failed runs=failed:agent:main report=True atlasPingedAt=True result=-
- sre-expert 716dd0d3 done/done/result runs=succeeded:gateway:716dd0d3-4160-4efd-a116-460d3301a32d report=True atlasPingedAt=True result=Forge 2h stability RCA: Claim/Progress/Result-Pfad funktioniert; Hauptsignal bleibt reproduzierbarer 401-Auth-Fail im nested local embedded/API-key Fallback, nicht produktive Disco
WorkerServices:
-
GatewayTail:
43:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.460+02:00 [agent/embedded] embedded run failover decision: runId=25b5d110-3b19-4d51-aff9-6ffe7e0255fe stage=assistant decision=fallback_model reason=timeout from=openai/gpt-5.5 profile=sha256:195d21b1dd7f rawError=codex app-server attempt timed out
44:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.462+02:00 [diagnostic] lane task error: lane=main durationMs=1500875 error="FailoverError: LLM request timed out."
45:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.463+02:00 [diagnostic] lane task error: lane=session:agent:main:main durationMs=1500876 error="FailoverError: LLM request timed out."
46:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.466+02:00 [model-fallback/decision] model fallback decision: decision=candidate_failed requested=openai/gpt-5.5 candidate=openai/gpt-5.5 reason=timeout next=openai/gpt-5.3-codex detail=codex app-server attempt timed out
48:May 04 19:15:40 huebners node[1210995]: 2026-05-04T19:15:40.789+02:00 [model-fallback/decision] model fallback decision: decision=candidate_succeeded requested=openai/gpt-5.5 candidate=openai/gpt-5.3-codex reason=unknown next=none
MCTail:
93:May 04 19:46:10 huebners node[1262382]: [task-reports] atlas-ping-skipped {
107:May 04 19:55:18 huebners node[1262382]: [task-reports] atlas-ping-skipped {
122:May 04 20:04:44 huebners node[1262382]: [task-reports] atlas-ping-skipped {
131:May 04 20:10:25 huebners node[1262382]: [task-reports] lifecycle report failed, continuing with best-effort vault writes {
134:May 04 20:10:25 huebners node[1262382]:   error: 'Failed to send report: {"message":"401: Unauthorized","code":0}'
136:May 04 20:10:36 huebners node[1262382]: [task-reports] lifecycle report failed, continuing with best-effort vault writes {
139:May 04 20:10:36 huebners node[1262382]:   error: 'Failed to send report: {"message":"401: Unauthorized","code":0}'
162:May 04 20:17:43 huebners node[1345689]: [task-reports] atlas-ping-skipped {
```

## Corrected sample 18 2026-05-04T18:27:21.443266+00:00

```text
UTC 2026-05-04T18:27:21.443266+00:00
MC {"status":"ok","openTasks":null,"inProgress":null,"pendingPickup":null,"staleOpenTasks":null,"orphanedDispatches":0}
Gateway {"ok":true,"status":"live"}
Guard {"ok": true, "rotationNeeded": 0, "staleRunning": 0, "loadErrors": 0, "wouldRotateSessionKeys": []}
GatewaySignalsSinceFix=5 MCSignalsSinceFix=13
Tasks:
- main 53895866 failed/failed/failed runs=failed:agent:main report=True atlasPingedAt=True result=-
- sre-expert 716dd0d3 done/done/result runs=succeeded:gateway:716dd0d3-4160-4efd-a116-460d3301a32d report=True atlasPingedAt=True result=Forge 2h stability RCA: Claim/Progress/Result-Pfad funktioniert; Hauptsignal bleibt reproduzierbarer 401-Auth-Fail im nested local embedded/API-key Fallback, nicht produktive Disco
WorkerServices:
mc-worker-sre-expert-15d09468-729-1777919238.service loaded active running Mission Control worker sre-expert 15d09468
GatewayTail:
43:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.460+02:00 [agent/embedded] embedded run failover decision: runId=25b5d110-3b19-4d51-aff9-6ffe7e0255fe stage=assistant decision=fallback_model reason=timeout from=openai/gpt-5.5 profile=sha256:195d21b1dd7f rawError=codex app-server attempt timed out
44:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.462+02:00 [diagnostic] lane task error: lane=main durationMs=1500875 error="FailoverError: LLM request timed out."
45:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.463+02:00 [diagnostic] lane task error: lane=session:agent:main:main durationMs=1500876 error="FailoverError: LLM request timed out."
46:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.466+02:00 [model-fallback/decision] model fallback decision: decision=candidate_failed requested=openai/gpt-5.5 candidate=openai/gpt-5.5 reason=timeout next=openai/gpt-5.3-codex detail=codex app-server attempt timed out
48:May 04 19:15:40 huebners node[1210995]: 2026-05-04T19:15:40.789+02:00 [model-fallback/decision] model fallback decision: decision=candidate_succeeded requested=openai/gpt-5.5 candidate=openai/gpt-5.3-codex reason=unknown next=none
MCTail:
93:May 04 19:46:10 huebners node[1262382]: [task-reports] atlas-ping-skipped {
107:May 04 19:55:18 huebners node[1262382]: [task-reports] atlas-ping-skipped {
122:May 04 20:04:44 huebners node[1262382]: [task-reports] atlas-ping-skipped {
131:May 04 20:10:25 huebners node[1262382]: [task-reports] lifecycle report failed, continuing with best-effort vault writes {
134:May 04 20:10:25 huebners node[1262382]:   error: 'Failed to send report: {"message":"401: Unauthorized","code":0}'
136:May 04 20:10:36 huebners node[1262382]: [task-reports] lifecycle report failed, continuing with best-effort vault writes {
139:May 04 20:10:36 huebners node[1262382]:   error: 'Failed to send report: {"message":"401: Unauthorized","code":0}'
162:May 04 20:17:43 huebners node[1345689]: [task-reports] atlas-ping-skipped {
```

## Corrected sample 19 2026-05-04T18:32:22.806769+00:00

```text
UTC 2026-05-04T18:32:22.806769+00:00
MC {"status":"ok","openTasks":null,"inProgress":null,"pendingPickup":null,"staleOpenTasks":null,"orphanedDispatches":0}
Gateway {"ok":true,"status":"live"}
Guard {"ok": true, "rotationNeeded": 0, "staleRunning": 0, "loadErrors": 0, "wouldRotateSessionKeys": []}
GatewaySignalsSinceFix=5 MCSignalsSinceFix=14
Tasks:
- main 53895866 failed/failed/failed runs=failed:agent:main report=True atlasPingedAt=True result=-
- sre-expert 716dd0d3 done/done/result runs=succeeded:gateway:716dd0d3-4160-4efd-a116-460d3301a32d report=True atlasPingedAt=True result=Forge 2h stability RCA: Claim/Progress/Result-Pfad funktioniert; Hauptsignal bleibt reproduzierbarer 401-Auth-Fail im nested local embedded/API-key Fallback, nicht produktive Disco
WorkerServices:
-
GatewayTail:
43:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.460+02:00 [agent/embedded] embedded run failover decision: runId=25b5d110-3b19-4d51-aff9-6ffe7e0255fe stage=assistant decision=fallback_model reason=timeout from=openai/gpt-5.5 profile=sha256:195d21b1dd7f rawError=codex app-server attempt timed out
44:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.462+02:00 [diagnostic] lane task error: lane=main durationMs=1500875 error="FailoverError: LLM request timed out."
45:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.463+02:00 [diagnostic] lane task error: lane=session:agent:main:main durationMs=1500876 error="FailoverError: LLM request timed out."
46:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.466+02:00 [model-fallback/decision] model fallback decision: decision=candidate_failed requested=openai/gpt-5.5 candidate=openai/gpt-5.5 reason=timeout next=openai/gpt-5.3-codex detail=codex app-server attempt timed out
48:May 04 19:15:40 huebners node[1210995]: 2026-05-04T19:15:40.789+02:00 [model-fallback/decision] model fallback decision: decision=candidate_succeeded requested=openai/gpt-5.5 candidate=openai/gpt-5.3-codex reason=unknown next=none
MCTail:
107:May 04 19:55:18 huebners node[1262382]: [task-reports] atlas-ping-skipped {
122:May 04 20:04:44 huebners node[1262382]: [task-reports] atlas-ping-skipped {
131:May 04 20:10:25 huebners node[1262382]: [task-reports] lifecycle report failed, continuing with best-effort vault writes {
134:May 04 20:10:25 huebners node[1262382]:   error: 'Failed to send report: {"message":"401: Unauthorized","code":0}'
136:May 04 20:10:36 huebners node[1262382]: [task-reports] lifecycle report failed, continuing with best-effort vault writes {
139:May 04 20:10:36 huebners node[1262382]:   error: 'Failed to send report: {"message":"401: Unauthorized","code":0}'
162:May 04 20:17:43 huebners node[1345689]: [task-reports] atlas-ping-skipped {
179:May 04 20:28:41 huebners node[1345689]: [task-reports] atlas-ping-skipped {
```

## Corrected sample 20 2026-05-04T18:37:25.485289+00:00

```text
UTC 2026-05-04T18:37:25.485289+00:00
MC {"status":"ok","openTasks":null,"inProgress":null,"pendingPickup":null,"staleOpenTasks":null,"orphanedDispatches":0}
Gateway {"ok":true,"status":"live"}
Guard {"ok": true, "rotationNeeded": 0, "staleRunning": 0, "loadErrors": 0, "wouldRotateSessionKeys": []}
GatewaySignalsSinceFix=5 MCSignalsSinceFix=14
Tasks:
- main 53895866 failed/failed/failed runs=failed:agent:main report=True atlasPingedAt=True result=-
- sre-expert 716dd0d3 done/done/result runs=succeeded:gateway:716dd0d3-4160-4efd-a116-460d3301a32d report=True atlasPingedAt=True result=Forge 2h stability RCA: Claim/Progress/Result-Pfad funktioniert; Hauptsignal bleibt reproduzierbarer 401-Auth-Fail im nested local embedded/API-key Fallback, nicht produktive Disco
WorkerServices:
-
GatewayTail:
43:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.460+02:00 [agent/embedded] embedded run failover decision: runId=25b5d110-3b19-4d51-aff9-6ffe7e0255fe stage=assistant decision=fallback_model reason=timeout from=openai/gpt-5.5 profile=sha256:195d21b1dd7f rawError=codex app-server attempt timed out
44:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.462+02:00 [diagnostic] lane task error: lane=main durationMs=1500875 error="FailoverError: LLM request timed out."
45:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.463+02:00 [diagnostic] lane task error: lane=session:agent:main:main durationMs=1500876 error="FailoverError: LLM request timed out."
46:May 04 19:14:06 huebners node[1210995]: 2026-05-04T19:14:06.466+02:00 [model-fallback/decision] model fallback decision: decision=candidate_failed requested=openai/gpt-5.5 candidate=openai/gpt-5.5 reason=timeout next=openai/gpt-5.3-codex detail=codex app-server attempt timed out
48:May 04 19:15:40 huebners node[1210995]: 2026-05-04T19:15:40.789+02:00 [model-fallback/decision] model fallback decision: decision=candidate_succeeded requested=openai/gpt-5.5 candidate=openai/gpt-5.3-codex reason=unknown next=none
MCTail:
107:May 04 19:55:18 huebners node[1262382]: [task-reports] atlas-ping-skipped {
122:May 04 20:04:44 huebners node[1262382]: [task-reports] atlas-ping-skipped {
131:May 04 20:10:25 huebners node[1262382]: [task-reports] lifecycle report failed, continuing with best-effort vault writes {
134:May 04 20:10:25 huebners node[1262382]:   error: 'Failed to send report: {"message":"401: Unauthorized","code":0}'
136:May 04 20:10:36 huebners node[1262382]: [task-reports] lifecycle report failed, continuing with best-effort vault writes {
139:May 04 20:10:36 huebners node[1262382]:   error: 'Failed to send report: {"message":"401: Unauthorized","code":0}'
162:May 04 20:17:43 huebners node[1345689]: [task-reports] atlas-ping-skipped {
179:May 04 20:28:41 huebners node[1345689]: [task-reports] atlas-ping-skipped {
```
