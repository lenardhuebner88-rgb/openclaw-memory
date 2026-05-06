# OpenClaw Post-Update Findings — Atlas Handoff 2026-05-06

> Purpose: hand this document to Atlas so Atlas can independently verify, ask Forge/Lens where useful, and create Mission Control tasks if warranted.

```yaml
for_atlas:
  status: actionable
  affected_agents: [main, sre-expert, efficiency-auditor, system-bot]
  affected_files:
    - /home/piet/vault/OPENCLAW_UPDATE_AUDIT_2026-05-06.md
    - /home/piet/vault/03-Agents/Hermes/plans/openclaw-disk-cleanup-execution-receipt-2026-05-06.md
    - /home/piet/.openclaw/openclaw.json
    - /home/piet/.config/systemd/user/openclaw-gateway.service.d/description-version.conf
    - /home/piet/.openclaw/npm/node_modules/@openclaw/discord/package.json
    - /home/piet/.openclaw/npm/node_modules/@openclaw/codex/package.json
  recommended_next_action: "Atlas should independently verify the P1 findings, then create bounded Mission Control tasks for plugin coherence and routing-intent verification if confirmed. Do not mutate config or restart from this handoff alone."
  risk: "Operational drift after real 2026.5.4 core update: external Discord plugin remains 2026.5.3, systemd description stale, PI/openai-codex routing should be confirmed intentional, QMD restart debt remains."
  evidence_files:
    - /home/piet/vault/OPENCLAW_UPDATE_AUDIT_2026-05-06.md
    - /home/piet/vault/03-Agents/Hermes/plans/openclaw-post-update-atlas-handoff-2026-05-06.md
```

## Executive summary

OpenClaw core update is real and live, not a shine update. But several post-update findings remain and should be independently verified by Atlas/Forge before remediation tasks are created.

Current state at Hermes recheck 2026-05-06 08:50 CEST:

- Gateway: live, `openclaw-gateway.service active/running`, `NRestarts=0`, PID `2613846`.
- Core: `/home/piet/bin/openclaw --version` → `OpenClaw 2026.5.4 (325df3e)`.
- Mission Control: `/api/health status=ok severity=ok`; previous degraded finding resolved.
- Disk: root improved to `81%` after cleanup (`98G total / 75G used / 19G free`).
- Sessions: 120m session health has `suspectedStuck=0`, `withErrors=0`.
- QMD: CLI status OK, index `460 MB`, `2276` docs, `16` pending; service restart count remains high (`NRestarts=4204`).

## Findings requiring Atlas/Forge verification

### P1 — External Discord plugin remains version-drifted

**Finding:** Core/Gateway is `2026.5.4`, but loaded external Discord plugin remains `@openclaw/discord@2026.5.3` from `/home/piet/.openclaw/npm`.

**Evidence:**

```text
/home/piet/bin/openclaw --version -> OpenClaw 2026.5.4 (325df3e)
node -p require('/home/piet/.npm-global/lib/node_modules/openclaw/package.json').version -> 2026.5.4
node -p require('/home/piet/.openclaw/npm/node_modules/@openclaw/discord/package.json').version -> 2026.5.3
openclaw plugins list --json -> discord 2026.5.3 loaded global true
```

**Risk:** Discord fixes/compatibility changes from `2026.5.4` may not be active. This is the main remaining post-update coherence issue.

**Suggested Atlas action:**

1. Verify whether `@openclaw/discord@2026.5.4` exists and is expected for OpenClaw `2026.5.4`.
2. If yes, create a Forge task for controlled external plugin sync:
   - backup npm plugin root / package lock;
   - install exact plugin versions;
   - validate plugin inventory;
   - restart gateway only in approved maintenance window;
   - post-check gateway health, Discord channel resolution, plugin inventory, and session health.
3. If no, document why `2026.5.3` is expected under `2026.5.4` core.

### P1/P2 — Routing intent verification: PI/openai-codex + MiniMax fallbacks

**Finding:** Current config differs from older native Codex-runtime guidance. Defaults and Atlas/main now use `agentRuntime.id=pi`, primary `openai-codex/gpt-5.5`, and MiniMax fallbacks.

**Evidence:**

```text
agents.defaults.agentRuntime = {"id":"pi"}
agents.defaults.model.primary = openai-codex/gpt-5.5
main.agentRuntime = {"id":"pi"}
main.primary = openai-codex/gpt-5.5
fallbacks include minimax/MiniMax-M2.7-highspeed and minimax/MiniMax-M2.7
```

**Risk:** This may be intentional from the update/migration, but it changes the old known-good ChatGPT Pro native-Codex route assumptions. Fallback behavior should be tested explicitly, especially MiniMax under PI route.

**Suggested Atlas action:**

1. Confirm with recent change notes whether PI route is intentional SSoT.
2. Ask Forge/Lens to run isolated, non-production model/fallback checks for:
   - `openai-codex/gpt-5.5` on main path;
   - `openai-codex/gpt-5.3-codex` fallback;
   - `minimax/MiniMax-M2.7-highspeed` as fallback/primary on a non-hot agent.
3. Do not change routing until tests prove the intended path.

### P2 — Stale systemd description remains

**Finding:** Base unit says `v2026.5.4`, but drop-in still overrides Description to `v2026.5.3-1`.

**Evidence:**

```text
systemctl --user show openclaw-gateway.service --property=Description
-> OpenClaw Gateway (v2026.5.3-1)

systemctl --user cat openclaw-gateway.service
-> base unit Description=OpenClaw Gateway (v2026.5.4)
-> drop-in /home/piet/.config/systemd/user/openclaw-gateway.service.d/description-version.conf:
   Description=OpenClaw Gateway (v2026.5.3-1)
```

**Risk:** Not runtime-critical, but it misleads operators and audit tools.

**Suggested Atlas action:** low-risk Forge task after backup: remove/update stale drop-in, `systemctl --user daemon-reload`, verify Description. No gateway restart should be needed solely for description correction.

### P2 — Gateway restart/settle warning cluster

**Finding:** Gateway currently recovered, but recent logs show a restart timeout and post-start event-loop/Discord fetch timeout.

**Evidence:**

```text
08:41:18 systemd: State 'stop-sigterm' timed out. Killing.
08:41:19 openclaw-gateway.service: Failed with result 'timeout'.
08:41:24 gateway http server listening
08:41:25 gateway ready
08:41:29 fetch timeout url=https://discord.com/api/v10/users/@me, timer delayed 1760ms
08:42:38 liveness warning: event_loop_delay ... eventLoopDelayMaxMs=16936.6
```

**Counter-evidence / not emergency:** Gateway health is live, service active/running, `NRestarts=0`, sessions not stuck.

**Suggested Atlas action:** create hardening/RCA task if not already covered: classify whether restart timeout is known/benign or indicates Gateway stop-path cleanup debt.

### P2 — QMD restart-count debt remains

**Finding:** QMD works, but service restart count is very high.

**Evidence:**

```text
qmd status -> returncode 0
Index: /home/piet/.cache/qmd/index.sqlite, Size 460.0 MB
Documents: 2276 files indexed, 89261 vectors, Pending 16
qmd-mcp-http.service ActiveState=active SubState=running NRestarts=4204
```

**Risk:** Current function OK, but restart history indicates lifecycle instability or historical crash loop. Could affect retrieval reliability.

**Suggested Atlas action:** Forge/Lens RCA task: inspect qmd-mcp-http journal over 24h/7d; classify historical vs ongoing; propose timer/service fixes only if evidence shows recurrence.

### P2/P3 — Alerts and monitoring semantics

**Finding:** Mission Control health is OK now, but alerts endpoint reports one active alert; task snapshot still reports a broad backlog count that differs from health open-task semantics.

**Evidence:**

```text
/api/health -> status=ok, staleOpenTasks=0, recoveryLoad=0
/api/tasks/snapshot -> total=1067, open=237, done=830, staleInProgress=0
/api/analytics/alerts -> activeCount=1, alertCount=1
```

**Suggested Atlas action:** inspect the single active alert. Do not treat broad `open=237` as the same as health `openTasks=3`; they are different views/definitions.

## Findings resolved or reduced

### Disk pressure reduced

Cleanup already executed by Hermes with Piet approval:

- Deleted stale non-live Mission Control `.next*` artefacts, keeping live `.next` and one rollback build.
- Cleaned regenerable npm/pip/pnpm/node-gyp/Playwright caches.
- Result: root changed from `87%` to `81%`, approx `6G` reclaimed.

Receipt: `/home/piet/vault/03-Agents/Hermes/plans/openclaw-disk-cleanup-execution-receipt-2026-05-06.md`

Remaining disk candidates are not emergency:

- `/home/piet/backups/2026-05-04-pi-route-all-agents-20260504T184051Z` ~`3.9G` — needs retention/offload decision.
- OpenClaw update backups: newest `629M`; older preupdate backups `339M` + `426M`.
- Journals/apt cache require root/sudo and are smaller.

### Mission Control degraded resolved

Original audit saw MC degraded. Current recheck: `status=ok`, `severity=ok`, `staleOpenTasks=0`, `recoveryLoad=0`.

## Anti-scope / guardrails for Atlas

- Do not restart Gateway from this handoff alone. Current service is live.
- Do not edit `/home/piet/.openclaw/openclaw.json` before proving routing intent and fallback behavior.
- Do not delete QMD cache/models, OpenClaw memory DBs, agent sessions, or update backups as part of plugin/routing verification.
- Do not treat stale systemd Description as proof the core update failed; live core is `2026.5.4`.
- Do not conflate Mission Control broad backlog `open=237` with degraded health; current health is OK.

## Suggested Mission Control task set if Atlas confirms

1. **Forge P1:** Verify and plan OpenClaw external plugin coherence for Discord/Codex under core `2026.5.4`.
2. **Forge/Lens P1/P2:** Verify current PI/openai-codex + MiniMax fallback routing is deliberate and functionally tested.
3. **Forge P2:** RCA Gateway stop timeout / post-restart event-loop settle warning cluster.
4. **Forge P2:** QMD MCP HTTP restart-count RCA (`NRestarts=4204`).
5. **Spark/Forge P2-low:** Correct stale Gateway systemd Description drop-in after backup and daemon-reload.
6. **Lens P3:** Classify single active Mission Control alert and clarify task snapshot vs health metric semantics.

## Source audit

The root audit was updated with a new `Live Recheck Update — 2026-05-06 08:50 CEST` section:

`/home/piet/vault/OPENCLAW_UPDATE_AUDIT_2026-05-06.md`
