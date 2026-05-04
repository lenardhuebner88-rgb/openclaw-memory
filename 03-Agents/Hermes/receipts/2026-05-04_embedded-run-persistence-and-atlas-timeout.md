---
title: Embedded-run timeout patch persistence + Atlas timeout analysis
created: 2026-05-04T00:05:00+02:00
status: verified
mutation_level: local_script_and_systemd_dropin_no_gateway_restart
for_atlas:
  status: info_only
  affected_agents: [main]
  affected_files:
    - /home/piet/.openclaw/scripts/apply-embedded-run-timeout-patch.py
    - /home/piet/.config/systemd/user/openclaw-gateway.service.d/embedded-run-timeout-patch.conf
    - /home/piet/.openclaw/agents/main/sessions/c398bead-a362-46ca-a764-6502d305ff61.trajectory.jsonl
  recommended_next_action: "Monitor primary-model 300s timeouts; keep fallback chain gpt-5.4-mini -> gpt-5.4 until latency pattern is understood."
  risk: "Dist hotfix is now restart-persistent, but OpenClaw upstream update can still change anchors and require checker review."
  evidence_files:
    - /home/piet/.openclaw/scripts/check-embedded-run-lane-timeout-patch.py
---

# Summary

Piet approved making the embedded-run timeout fix persistent and asked why Atlas timed out.

Implemented persistence without restarting the live gateway:

- Created `/home/piet/.openclaw/scripts/apply-embedded-run-timeout-patch.py`.
- Created systemd user drop-in `/home/piet/.config/systemd/user/openclaw-gateway.service.d/embedded-run-timeout-patch.conf`.
- Drop-in runs:
  - `ExecStartPre=-/usr/bin/python3 /home/piet/.openclaw/scripts/apply-embedded-run-timeout-patch.py`
- Ran:
  - `python3 -m py_compile /home/piet/.openclaw/scripts/apply-embedded-run-timeout-patch.py`
  - `/usr/bin/python3 /home/piet/.openclaw/scripts/apply-embedded-run-timeout-patch.py`
  - `/home/piet/.openclaw/scripts/check-embedded-run-lane-timeout-patch.py`
  - `systemctl --user daemon-reload`
- Gateway was not restarted; health remained `{"ok":true,"status":"live"}`.

# Persistence verification

Apply script result on current bundles:

- `already-patched embedded-grace /home/piet/.npm-global/lib/node_modules/openclaw/dist/pi-embedded-rWtLEwl7.js`
- `already-patched active-abort-drain /home/piet/.npm-global/lib/node_modules/openclaw/dist/diagnostic-oEUVZa4J.js`

Regression checker:

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

# Atlas timeout finding

Atlas Discord session:

- Session: `c398bead-a362-46ca-a764-6502d305ff61`
- Run: `a362c84a-6f6d-4279-b3ef-80b44553a1bb`
- Channel: `agent:main:discord:channel:1486480128576983070`
- User prompt: `Ja mach genau das`
- Intended action from assistant partial text: cancel four duplicate draft tasks, then verify task states.

Timeline:

```text
23:56:25.641  session.started openai/gpt-5.4-mini
23:56:25.642  prompt.submitted
23:59:28.795  stuck session warn at age=141s; recovery=checking
23:59:28.798  recovery skipped active_embedded_run action=observe_only
00:01:25.643  model.completed timedOut=true aborted=true; promptError="codex app-server attempt timed out"
00:01:25.657  embedded run failover decision: timeout from openai/gpt-5.4-mini
00:01:25.665  fallback next=openai/gpt-5.4
00:01:27.814  fallback session.started openai/gpt-5.4
00:01:56.314  fallback model.completed timedOut=false aborted=false
00:01:56.314  fallback session.ended status=success
```

Usage on timed-out attempt:

```json
{"input":3354,"output":893,"cacheRead":73088,"total":77335}
```

Usage on successful fallback:

```json
{"input":1279,"output":233,"cacheRead":84352,"total":85864}
```

# Interpretation

This Atlas timeout was not the old 330s lane-budget bug.

Facts:

- The timed-out model was `openai/gpt-5.4-mini`, not `gpt-5.5`.
- It hit the inner Codex app-server attempt timeout at ~300s:
  - journal: `rawError=codex app-server attempt timed out`
  - lane errors: `durationMs=300745/300746`
- The patched outer lane budget did not kill the recovery path.
- Fallback to `openai/gpt-5.4` started ~2s later and completed in ~29s.
- Session ended successfully.
- After `00:01:56`, journal scan showed zero fresh:
  - `CommandLaneTaskTimeout`
  - `Command lane "main" task timed out after 330000ms`
  - `codex app-server attempt timed out`
  - `stuck session`
  - `recovery skipped`
  - `active_embedded_run`
  - `FailoverError`

Likely exact problem:

- The Codex native app-server path for `openai/gpt-5.4-mini` stalled until the configured 300s per-attempt timeout.
- It had already produced a partial assistant text but did not complete the turn.
- This appears to be model/runtime latency or a stuck Codex app-server attempt, not a task-board mutation problem and not the fixed outer-lane timeout bug.
- Fallback behavior is now correct: `gpt-5.4-mini` timed out, `gpt-5.4` succeeded.

# Current state after verification

- Gateway PID: `343560`
- Gateway active/running
- Gateway health: `{"ok":true,"status":"live"}`
- Session health active 5m:
  - total `2`
  - suspectedStuck `0`
  - withErrors `0`
  - main now on `openai/gpt-5.4`, outputTokens `233`

# Risk / follow-up

- The persistence script handles current bundle anchors. If an OpenClaw update changes bundle code shape, the checker must be run after update.
- Atlas has now shown 300s timeouts on both `gpt-5.5` and `gpt-5.4-mini`; `gpt-5.4` completed the same task quickly. If this repeats, prefer making `gpt-5.4` a hotter fallback or temporarily primary for Atlas Discord operations.

# Canonical Final Report

- [[../../../03-Projects/plans/2026-05-04_openclaw-mission-control-stabilization-final-report|OpenClaw/Mission-Control Stabilization Final Report]]
- This receipt remains the Hermes timeout/persistence evidence source; the linked project report is the cross-agent/operator SSOT.
