---
title: OpenClaw Atlas/Forge Codex Runtime Incident Plan
status: active
created: 2026-05-03
owner: Hermes
scope: stabilize-first-readonly-rca-after
---

# OpenClaw Atlas/Forge Codex Runtime Incident Plan

## Situation
Atlas/main and Forge/sre-expert are not responding in Discord while OpenClaw Gateway health remains live.

## Initial Evidence
- `openclaw-gateway.service` active/running, NRestarts=0.
- `openclaw-discord-bot.service` inactive/dead.
- Mission Control ok.
- Gateway logs show repeated embedded Codex app-server timeouts:
  - `codex app-server attempt timed out`
  - `FailoverError: LLM request timed out`
  - `Command lane "main" task timed out after 330000ms`
- Forge/SRE stuck-session diagnostics:
  - `queued_work_without_active_run`
  - recovery skipped because `active_embedded_run`.

## Phase 0 — Guardrails
- No token edits.
- No OpenClaw config edits unless later explicitly needed.
- No Commander bot reactivation.
- Stabilization mutation allowed by Piet in Discord thread.

## Phase 1 — Stabilize
1. Capture pre-restart state and focused logs.
2. Restart only `openclaw-gateway.service` to clear embedded Codex app-server children and lane state.
3. Verify:
   - service active/running
   - `/health` live
   - Discord/gateway logs reconnect cleanly
   - no immediate crash loop

## Phase 2 — Functional Verification
1. Confirm recent logs after restart.
2. Ask Piet to test Atlas and Forge short command/message.
3. Watch 5 minutes for:
   - `codex app-server attempt timed out`
   - `FailoverError`
   - `stuck session`
   - `lane wait exceeded`

## Phase 3 — Dedicated RCA
1. Timeline: config reload, lane waits, app-server spawn/timeout, fallback chain, stuck sessions.
2. Separate confirmed cause vs contributing factors.
3. Identify whether failure is:
   - stale embedded Codex child process / lane state
   - upstream OpenAI-Codex timeout
   - config hot-reload side effect
   - model/provider routing issue
4. Produce final incident note with evidence and prevention recommendations.

## Phase 4 — Optional Follow-up Scope
Only after stabilization and RCA:
- harness/monitoring detection for embedded app-server stall
- more aggressive stale lane recovery
- route specific agents away from fragile model/runtime if confirmed
