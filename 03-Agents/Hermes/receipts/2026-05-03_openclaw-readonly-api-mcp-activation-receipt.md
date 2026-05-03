# OpenClaw Read-only API/MCP Activation Receipt — 2026-05-03

## Scope
Activate the Mission Control read-only OpenClaw diagnostics API routes and verify the Hermes MCP bridge state.

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

## Post-check
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
  - `/api/ops/openclaw/session-health?active=30m`: HTTP 200; returned activeMinutes=30, total=5, suspectedStuck=0

## MCP State
- `/home/piet/.hermes/mcp/mc_readonly_server.py` on disk includes the new tools and new endpoint status entries.
- Current Hermes gateway is still running the old MCP child process:
  - Hermes gateway PID=4174467
  - mc_readonly_server.py child PID=4174473, uptime about 5h
- Evidence: current `mc_endpoint_status` MCP tool still reports only the old 6 endpoints, so the running MCP process has not reloaded the patched file yet.
- Pending Gate D: restart/reload `hermes-gateway.service` to make Hermes discover the new MCP tool registry.

## Rollback
- If Mission Control regressions appear, restore `.next` from `.next.bak-hermes-20260503T192025Z` and restart `mission-control.service`.
- If MCP reload causes issues, restore `/home/piet/.hermes/mcp/mc_readonly_server.py.bak-20260503T183433Z` and restart `hermes-gateway.service`.
