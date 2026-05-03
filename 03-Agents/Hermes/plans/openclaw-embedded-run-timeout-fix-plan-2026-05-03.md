---
title: OpenClaw embedded-run lane-timeout sustainable fix
created: 2026-05-03
owner: Hermes
mutation_level: approved_runtime_patch_and_session_hygiene
for_atlas:
  status: actionable
  affected_agents: [main, sre-expert]
  affected_files:
    - /home/piet/.npm-global/lib/node_modules/openclaw/dist/pi-embedded-rWtLEwl7.js
    - /home/piet/.openclaw/agents/sre-expert/sessions/sessions.json
  recommended_next_action: "Patch embedded run lane timeout budget, rotate Forge/SRE Discord session, restart gateway, run direct + log verification."
  risk: "Direct dist patch is not update-persistent; must be reapplied or upstreamed after OpenClaw update."
  evidence_files:
    - /home/piet/.openclaw/agents/sre-expert/sessions/be1f1492-8276-4c48-8a02-33ec07c63d55.trajectory.jsonl
---

# Problem

OpenClaw Codex embedded runs time out internally at ~300s. When timeout-compaction succeeds and retry/fallback starts, the outer command-lane task is still capped at `timeoutMs + 30000` (=330s). This kills the recovery path shortly after compaction succeeds.

Observed evidence:
- `23:19:12 [timeout-compaction] compaction succeeded for openai/gpt-5.5; retrying prompt`
- `23:19:26 Command lane "main" task timed out after 330000ms`
- SRE trajectory: `codex app-server attempt timed out` at 300s, then fallback/retry begins.

# Fix plan

1. Back up production dist file and relevant SRE session store.
2. Patch `EMBEDDED_RUN_LANE_TIMEOUT_GRACE_MS` in `pi-embedded-rWtLEwl7.js` from 30s to 10min.
   - Result: outer lane timeout becomes ~900s for a 300s inner model attempt.
   - Rationale: preserves a hard cap, but gives timeout-compaction and one fallback/retry enough budget.
3. Add a local regression checker script under `/home/piet/.openclaw/scripts/` to verify the patched dist invariant.
4. Rotate only the Forge/SRE Discord session mapping to clear the bloated 185k-token historical session and stale modelOverride.
   - Preserve a timestamped backup first.
   - Leave direct SRE and Atlas sessions untouched unless post-check shows failures.
5. Restart `openclaw-gateway.service` so the dist patch and session-store change are loaded.
6. Verify:
   - Gateway PID changed and `/health` live.
   - Journal shows `[gateway] ready` and Discord channels resolved.
   - No fresh `CommandLaneTaskTimeout`, `codex app-server attempt timed out`, `stuck session`, `FailoverError` after ready.
   - Direct SRE and Atlas smoke tests complete.
   - Session health has `suspectedStuck=0`, `withErrors=0`.
7. Parallel Codex audit reviews whether this is sufficient or whether more changes are required.

# Rollback

Restore the timestamped JS backup and SRE `sessions.json` backup, restart gateway, and re-run the same post-checks.
