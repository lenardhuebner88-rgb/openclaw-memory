# OpenClaw Read-only API/MCP Activation Receipt — 2026-05-03

for_atlas:
  status: info_only
  affected_agents: ["Hermes", "Atlas", "Mission Control"]
  affected_files:
    - "/home/piet/vault/03-Agents/Hermes/receipts/2026-05-03_openclaw-readonly-api-mcp-activation-receipt.md"
    - "/home/piet/.hermes/mcp/mc_readonly_server.py"
    - "/home/piet/.openclaw/workspace/mission-control/src/app/api/ops/openclaw/**/route.ts"
    - "/home/piet/.openclaw/workspace/mission-control/src/lib/openclaw-readonly-diagnostics.ts"
  recommended_next_action: "Use mc-readonly OpenClaw diagnostic tools as the first read-only evidence layer for config/model/session status."
  risk: "Read-only diagnostics only; no runtime mutation surface was added."
  evidence_files:
    - "/home/piet/vault/03-Agents/Hermes/playbooks/mission-control-api-readonly.md"
    - "/home/piet/vault/03-Agents/Hermes/playbooks/openclaw-readonly-mcp.md"

## Scope

Activate the Mission Control read-only OpenClaw diagnostics API routes and verify the Hermes MCP bridge state.

Mutation class approved by Piet in Discord thread on 2026-05-03: document final activation state and update Hermes' `openclaw-operator` skill so future diagnostics prefer the new MCP/API tools.

## Gate A — Preflight

- Timestamp: 2026-05-03T19:09:27Z
- Mission Control before deploy: active/running, MainPID=3493276, Result=success, NRestarts=0
- `/api/health`: HTTP 200
- Git status for owned files: new/untracked only
  - `src/app/api/ops/openclaw/`
  - `src/lib/openclaw-readonly-diagnostics.ts`
  - `tests/openclaw-readonly-diagnostics.test.ts`
- Tests:
  - `npm run typecheck`: exit 0
  - `npx vitest run tests/openclaw-readonly-diagnostics.test.ts`: 7/7 passed
  - `python3 -m py_compile /home/piet/.hermes/mcp/mc_readonly_server.py`: exit 0

## Build/Deploy

- First in-place build attempt was interrupted earlier, leaving `.next/BUILD_ID` missing while the old live `next-server` continued to serve traffic.
- Second in-place build attempt with `ALLOW_BUILD_WHILE_RUNNING=1 npm run build` exceeded 600s and timed out during `Creating an optimized production build ...`.
- Recovery path used the already-validated isolated build artifact:
  - Verified `.next-hermes-readonly-build/BUILD_ID`
  - Verified `.next-hermes-readonly-build/prerender-manifest.json`
  - Verified `.next-hermes-readonly-build/server/app-paths-manifest.json`
  - Confirmed all new routes were present in the isolated build manifest.
- Previous `.next` backup: `.next.bak-hermes-20260503T192025Z`
- Activated build: copied `.next-hermes-readonly-build` to `.next`
- Activated BUILD_ID: `1wokDcB2BlHIo7w1gl_cj`
- Restart command executed: `systemctl --user restart mission-control.service`

## Gate B/C — Mission Control Post-check

- Mission Control health became ready after 2s.
- Service after restart:
  - ActiveState=active
  - SubState=running
  - MainPID=208685
  - Result=success
  - NRestarts=0
  - ExecMainStatus=0
- Baseline endpoints:
  - `/api/health`: HTTP 200
  - `/api/board-consistency`: HTTP 200
  - `/dashboard`: HTTP 200
  - `/alerts`: HTTP 200
- New read-only endpoints:
  - `/api/ops/openclaw/effective-config-redacted`: HTTP 200; returned redacted config keys including agents/channels/models/plugins/redaction/source
  - `/api/ops/openclaw/model-runtime-failures?window=10m&limit=20`: HTTP 200; returned empty events/counts in current window
  - `/api/ops/openclaw/session-health?active=30m`: HTTP 200; returned activeMinutes=30, suspectedStuck=0

## Gate D — Hermes MCP Reload / Activation

Earlier state before Hermes reload:

- `/home/piet/.hermes/mcp/mc_readonly_server.py` on disk included the new tools and new endpoint status entries.
- Running Hermes gateway still had the old MCP child process:
  - Hermes gateway PID=4174467
  - mc_readonly_server.py child PID=4174473, uptime about 5h
- Evidence: `mc_endpoint_status` still reported only the old 6 endpoints, so the running MCP process had not reloaded the patched file yet.
- Required action was a restart/reload of `hermes-gateway.service`.

Final verified state after Hermes gateway restart/reload:

- Verification timestamp: 2026-05-03T22:14:42+02:00
- `hermes-gateway.service`:
  - ActiveState=active
  - SubState=running
  - MainPID=222477
  - Result=success
  - NRestarts=0
  - ExecMainStartTimestamp=Sun 2026-05-03 21:39:45 CEST
- Running MCP bridge process:
  - `/home/piet/.hermes/mcp/mc_readonly_server.py` child PID=222482
- Process evidence was redacted for tokens; command line showed:
  - `/home/piet/.hermes/hermes-agent/venv/bin/python -m hermes_cli.main gateway run --replace`
  - `/home/piet/.hermes/hermes-agent/venv/bin/python /home/piet/.hermes/mcp/mc_readonly_server.py`

## Gate E — MCP Tool Registry / Functional Verification

`mc_endpoint_status` from inside Hermes now reports 9 endpoints, all HTTP 200:

- `/api/health`: HTTP 200
- `/api/board-consistency`: HTTP 200
- `/api/tasks/snapshot`: HTTP 200
- `/api/analytics/alerts`: HTTP 200
- `/api/ops/skill-plugin-inventory`: HTTP 200
- `/api/monitoring`: HTTP 200
- `/api/ops/openclaw/effective-config-redacted`: HTTP 200
- `/api/ops/openclaw/model-runtime-failures?window=10m&limit=20`: HTTP 200
- `/api/ops/openclaw/session-health?active=30m`: HTTP 200

Direct new MCP tool calls verified from Hermes:

- `mc_openclaw_effective_config_redacted`
  - HTTP 200
  - returned redacted effective OpenClaw config
  - sensitive fields redacted; usable for model/channel/plugin/config routing analysis
- `mc_openclaw_model_runtime_failures(window=10m, limit=20)`
  - HTTP 200
  - `counts: {}`
  - `events: []`
  - `commandExitCode: 0`
- `mc_openclaw_session_health(active_minutes=30)`
  - HTTP 200
  - `total: 4`
  - `suspectedStuck: 0`
  - `withErrors: 0`
  - sessions covered `main`, `sre-expert`, and `system-bot`

Mission Control health at final verification:

- `/api/health`: HTTP 200
- `status: ok`
- `severity: ok`
- `totalTasks: 960`
- `openTasks: 1`
- `inProgress: 1`
- `staleOpenTasks: 0`
- `orphanedDispatches: 0`
- `criticalCostAnomalies: 0`

OpenClaw direct read-only cross-checks:

- OpenClaw Gateway `/health`: HTTP 200, body `{"ok": true, "status": "live"}`
- Recent OpenClaw logs, last 10 minutes: no warning/error entries from readonly log tool

## Operator Skill Update

Updated Hermes native skill `openclaw-operator` after Gate E verification:

- Skill path: `/home/piet/.hermes/skills/devops/openclaw-operator/SKILL.md`
- Updated section: `## Tool Preference`
- New preference:
  1. Use `mc-readonly` MCP first for Mission Control state and Mission-Control-hosted OpenClaw diagnostics.
  2. Prefer these new tools for current config/model/session evidence:
     - `mc_openclaw_effective_config_redacted`
     - `mc_openclaw_model_runtime_failures`
     - `mc_openclaw_session_health`
  3. Continue using `openclaw-readonly` MCP for direct Gateway/Discord/service/log evidence.
  4. Use shell only when no MCP/API route exists or process/service-level proof is required.

Rationale: the new Mission-Control-hosted tools are bounded, redacted, GET/read-only, HTTP-status checked, and safer/faster than ad-hoc shell inspection for routine diagnostics.

## Rollback

- If Mission Control regressions appear, restore `.next` from `.next.bak-hermes-20260503T192025Z` and restart `mission-control.service`.
- If MCP reload causes issues, restore `/home/piet/.hermes/mcp/mc_readonly_server.py.bak-20260503T183433Z` and restart `hermes-gateway.service`.
- Receipt backup before final documentation update:
  - `/home/piet/vault/03-Agents/Hermes/receipts/2026-05-03_openclaw-readonly-api-mcp-activation-receipt.md.bak-20260503T2214CEST`

## Final Status

Status: **complete / verified**

The read-only OpenClaw diagnostics surface is active end-to-end:

1. Mission Control routes are deployed and return HTTP 200.
2. Hermes MCP bridge has reloaded and exposes the new tools.
3. Direct calls to the new tools succeed from Hermes.
4. Current health signals are green: MC OK, OpenClaw Gateway live, no model runtime failures in the checked 10-minute window, no suspected stuck sessions in the checked 30-minute window.
5. `openclaw-operator` skill now documents the new tool preference so future diagnostics use the safer MCP/API path first.
