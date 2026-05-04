# OpenClaw Beta4 Stabilization Plan

Stand: 2026-05-04 09:00 CEST
Owner: Codex
Scope: Atlas/Forge timeout stabilization after OpenClaw 2026.5.3-beta.4

## Live Verdict

The Claude analysis is mostly valid for the snapshot around 08:41 CEST, but parts are stale after the completed beta4 migration and config cleanup.

Current live facts:

- OpenClaw runtime is `2026.5.3-beta.4 (c6c64e2)`.
- Gateway is active and `/health` returns `{"ok":true,"status":"live"}`.
- `agents.defaults.agentRuntime` is now `{ "id": "codex" }`.
- `agentRuntime.fallback = "pi"` is not present anymore.
- `agents.list[main].heartbeat` is not present anymore.
- `plugins.allow` does not include `schedule`.
- Atlas/main model routing is `openai/gpt-5.4 -> openai/gpt-5.4-mini -> openai/gpt-5.3-codex`.
- Forge/sre-expert model routing is `openai/gpt-5.3-codex -> openai/gpt-5.5 -> openai/gpt-5.4-mini -> openai/gpt-5.4`.
- A fresh real-use Atlas Discord turn did reproduce `codex app-server attempt timed out` after the final beta4 restart.
- The first fallback `openai/gpt-5.4-mini` also reproduced the same 300s timeout.
- A separate Minimax config/provider failure appeared: `Model provider minimax not found`.
- The old 08:49 heartbeat expectation did not produce an automatic `HEARTBEAT` LLM wake in the current live config.

## Claude Analysis Assessment

Accepted:

- Beta4 is installed and active.
- The systemd description drop-in is stale and still references v2026.5.2.
- `apply-openclaw-response-hardening.py` now hard-fails on the store-lock subpatch because the old store-lock symbols are gone.
- The embedded-run timeout patch must stay disabled. Re-enabling it would modify upstream beta4 behavior and likely fight the beta3/beta4 abort-drain strategy.
- Local patch drift is real: PR68846 cleanup marker is not present in the current attempt-execution bundle; the old S-reliability target file is absent.
- The original timeout class matches OpenClaw provider stream/embedded runtime behavior, not a Mission-Control or Discord outage.

Corrected:

- Current live config no longer contains `agentRuntime.fallback = "pi"`.
- Current live config no longer contains `heartbeat: {}` for Atlas/main.
- The heartbeat subsystem starts, but current live evidence does not show a scheduled Atlas LLM heartbeat after 08:40.
- A dedicated pre-beta4 backup exists under `/home/piet/.openclaw/backups/openclaw-beta4-upgrade-20260504T062526Z`.
- The relevant bundle filenames changed again after the final beta4/package alignment; current verification must use the live files under `/home/piet/.npm-global/lib/node_modules/openclaw/dist`.

## Stabilization Plan

### P0 - Observe Real Use Case

Goal: prove whether beta4 actually fixes the live Atlas/Forge timeout mode.

Current live canary:

- Session: `agent:main:discord:channel:1486480128576983070`
- File: `/home/piet/.openclaw/agents/main/sessions/8669821b-48d0-4fa1-9193-cb4ffd9c0b9d.trajectory.jsonl`
- Run: `9c32aaa4-46a1-453d-be59-ffe0419e0e26`
- Prompt submitted: `2026-05-04T06:50:05Z`
- Model: `openai/gpt-5.4`
- Real task: Minimax M2.7 integration analysis and smoke test request.
- Result: failed at `2026-05-04T06:55:05Z` after roughly 300s.
- Error: `codex app-server attempt timed out`.
- Usage at abort: `input=522`, `output=119`, `cacheRead=85376`, `total=86017`.
- Partial assistant text existed before abort.
- Fallback started at `2026-05-04T06:55:07Z` on `openai/gpt-5.4-mini`.
- First fallback result: failed at `2026-05-04T07:00:07Z` after roughly 300s.
- Fallback error: `codex app-server attempt timed out`.
- Fallback usage at abort: `input=2520`, `output=413`, `cacheRead=89472`, `total=92405`.
- Second fallback started at `2026-05-04T07:00:08Z` on `openai/gpt-5.3-codex`.
- Separate provider check failure in gateway log: `requested=minimax/MiniMax-M2.7-highspeed ... Model provider minimax not found`.

Updated interpretation:

- Beta4 reduced some install/runtime packaging failures but did not eliminate the embedded Codex app-server 300s timeout in the real Atlas Discord hotpath.
- The issue is model-route-wide inside the native Codex embedded runtime; `gpt-5.4` and `gpt-5.4-mini` both failed in the same real run.
- The remaining failure is not a heartbeat issue; it occurred on a direct user Discord request.
- The remaining failure is not obviously a broken tool execution; the abort happened during assistant/model turn completion after partial text.
- `gpt-5.4` and `gpt-5.4-mini` should no longer be considered proven-stable for Atlas primary in high-cache Discord sessions.
- Minimax integration must be treated as a separate provider-config problem and not mixed with the Codex timeout RCA.

Pass criteria for the remaining fallback:

- `openai/gpt-5.3-codex` completes the same run with `timedOut=false`.
- `session.ended` has `status=success`.
- Gateway stays healthy.

Fail criteria:

- Any `codex app-server attempt timed out`.
- Any `FailoverError: LLM request timed out`.
- Any fallback from `openai/gpt-5.4` during the run.
- Any new `ERR_MODULE_NOT_FOUND`.
- Gateway restart loop or `/health` failure.

### P1 - Patch Hygiene

Goal: remove unstable local patch drift without changing behavior blindly.

Actions:

1. Keep `embedded-run-timeout-patch.conf.disabled-20260504T062526Z` disabled.
2. Replace `response-hardening.conf` with a beta4-safe checker or split patch:
   - keep only the verified typing TTL and 1s watchdog checks if still needed,
   - remove or bypass the dead store-lock subpatch.
3. Re-anchor or retire PR68846 patch logic against beta4 `attempt-execution-*` files.
4. Mark old bundle-hash checkers as obsolete and replace them with pattern-based beta4 checks.
5. Document which local patches remain intentional after beta4.

Validation:

- `systemctl --user restart openclaw-gateway.service`
- `/health` returns live.
- No ExecStartPre hard failure except explicitly accepted no-op checks.
- Same Atlas/Forge canary set must be repeated after any patch cleanup.

### P2 - Heartbeat And Context Control

Goal: avoid accidental long-context automatic wakes.

Actions:

1. Verify whether any heartbeat source still schedules LLM turns outside `openclaw.json`.
2. If no automatic LLM heartbeat occurs for a full 30m cycle, classify Claude's `heartbeat:{}` finding as historical.
3. If automatic LLM heartbeat still appears, identify source and either disable it or move it to a low-cost/low-context route.
4. Add a lightweight monitor for `cacheRead` and `totalTokens` on Atlas/Forge turns.

Suggested alert thresholds:

- Warn at `cacheRead >= 80000`.
- Investigate at `cacheRead >= 120000`.
- Rotate or compact session if repeated turns exceed `150000` cached tokens and start approaching timeout behavior.

Validation:

- At least one 30m cycle after restart with no unexpected HEARTBEAT LLM turn.
- At least one manual Atlas Discord turn succeeds after the cycle.

### P3 - Config And Systemd Metadata Cleanup

Goal: remove misleading state that can cause wrong operator decisions.

Actions:

1. Update stale `description-version.conf` from v2026.5.2 to v2026.5.3-beta.4.
2. Update stale `meta.lastTouchedVersion` only if OpenClaw accepts this field as metadata-only.
3. Keep `agentRuntime.fallback` absent unless upstream beta4 docs require a new equivalent key.
4. Record managed plugin-root peer package requirement: `/home/piet/.openclaw/npm` must include `openclaw@2026.5.3-beta.4` while managed plugins import it.

Validation:

- `openclaw --version` remains beta4.
- `openclaw doctor --dry-run` or equivalent config check does not propose reverting critical beta4 migration.
- Gateway health stays live after restart.

### P4 - Routing Decision After Evidence

Goal: decide model routing by observed stability, not by recommendation text alone.

Current recommendation:

- Do not keep treating `openai/gpt-5.4` as stable Atlas primary; the 08:50 real Discord use case timed out at 08:55.
- Do not promote `openai/gpt-5.4-mini`; it also timed out in the 09:00 CEST live-use fallback.
- Wait for the current `openai/gpt-5.3-codex` fallback result before changing routing.
- Do not move Atlas back to `openai/gpt-5.5` until beta4 has passed a longer real-use window on a lower-risk agent.
- Do not roll back to `openai-codex/gpt-*`; that path has a separate open timeout issue class.

Decision gates:

- If `gpt-5.3-codex` succeeds: consider making Atlas primary `openai/gpt-5.3-codex` for a short stabilization window, with `gpt-5.4-mini` only behind it or removed temporarily.
- If `gpt-5.3-codex` also times out: stop model churn and reduce active Atlas context pressure before more tests.
- If only one agent model fails repeatedly: isolate that model in its fallback order.

## Immediate Next Decision

If the current `gpt-5.3-codex` fallback succeeds:

1. Backup `/home/piet/.openclaw/openclaw.json`.
2. Change Atlas/main primary from `openai/gpt-5.4` to `openai/gpt-5.3-codex` for a short stabilization window.
3. Remove duplicate primary from Atlas fallbacks and avoid immediate retry through known-failing `gpt-5.4`/`gpt-5.4-mini` unless needed.
4. Restart `openclaw-gateway.service`.
5. Validate with a real Atlas Discord turn and a Forge canary.

If the current `gpt-5.3-codex` fallback also times out:

1. Do not change model routing yet.
2. Treat beta4 as insufficient for this hotpath.
3. Reduce active Atlas context pressure first.
4. Capture a maintainer-ready issue package with run IDs, trajectories, logs, package versions, and local patch inventory.
5. Keep Minimax provider setup as a separate task; do not use Minimax smoke tests as the Codex timeout validator until provider registration is fixed.

## Monitoring Commands

```bash
openclaw --version
curl -fsS http://127.0.0.1:18789/health
systemctl --user show openclaw-gateway.service -p ActiveState -p SubState -p ExecMainStartTimestamp -p ExecMainPID -p NRestarts -p MemoryCurrent -p TasksCurrent --value
journalctl --user -u openclaw-gateway.service --since '2026-05-04 08:40:00' --no-pager | rg 'codex app-server attempt timed out|FailoverError|fetch timeout reached|ERR_MODULE_NOT_FOUND|Invalid config|model fallback decision'
rg -n 'model.completed|session.ended|timedOut|promptError|fallback' /home/piet/.openclaw/agents/main/sessions/*.trajectory.jsonl
```

## Stop Conditions

Stop and re-RCA before further config changes if any of these appear:

- fresh `codex app-server attempt timed out`
- fresh `FailoverError`
- fallback during a real Atlas Discord turn
- `ERR_MODULE_NOT_FOUND`
- OpenClaw config guard rollback
- Gateway restart loop
- health endpoint not live

## Durable Artifacts

- Fix receipt: `/home/piet/vault/03-Agents/Codex/receipts/2026-05-04_openclaw-beta4-timeout-fix.md`
- Upgrade backup: `/home/piet/.openclaw/backups/openclaw-beta4-upgrade-20260504T062526Z`
- Current plan: `/home/piet/vault/03-Agents/Codex/plans/2026-05-04_openclaw-beta4-stabilization-plan.md`
