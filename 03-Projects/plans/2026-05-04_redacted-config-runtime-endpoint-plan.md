# Redacted Config/Runtime Endpoint Plan

Status: planned after live research
Owner: Atlas/Forge candidate
Scope: Mission Control read-only diagnostics for OpenClaw runtime/config, no secrets, less shell/config reading.

## Research Findings
- Mission Control already contains a read-only endpoint:
  - `GET /api/ops/openclaw/effective-config-redacted`
  - route: `src/app/api/ops/openclaw/effective-config-redacted/route.ts`
  - logic: `src/lib/openclaw-readonly-diagnostics.ts`
- Related existing endpoints:
  - `GET /api/ops/openclaw/model-runtime-failures?window=30m&limit=100`
  - `GET /api/ops/openclaw/session-health?active=180m`
- Existing test coverage:
  - `tests/openclaw-readonly-diagnostics.test.ts`
- Live curl proof on 2026-05-04:
  - endpoint returns JSON
  - includes agents, models/providers, Discord channel slice
  - secret scan passed for common patterns (`sk-*`, Bearer, apiKey/token/secret leaks)

## Gap
The capability mostly exists, but needs productization/hardening:
1. Add stable alias matching the intended public contract:
   - `GET /api/config/effective-redacted`
   - keep existing `/api/ops/openclaw/effective-config-redacted` as canonical/legacy or internal ops path.
2. Include more runtime/tool visibility:
   - active agent ids/names/models/runtimes
   - agent defaults
   - configured tools policy summary
   - MCP server ids/commands redacted to basename/intent, no args containing secrets
   - channels summary for Discord/Telegram without tokens
   - OpenClaw version/config source
3. Add stronger redaction guard:
   - recursive key redaction already exists
   - add response-level denylist scan test for token-like values and local secret paths
   - no raw config path, no env, no prompt/user content
4. Add compact consumer output option:
   - `?compact=1` for Atlas/Hermes startup use
   - default full diagnostic JSON remains read-only

## Proposed Response Shape
```json
{
  "generatedAt": "...",
  "mode": "read-only-redacted",
  "openclaw": { "version": "..." },
  "agents": { "defaults": {}, "list": [] },
  "models": { "providers": [] },
  "runtimes": { "defaults": {}, "configured": [] },
  "tools": { "exec": {}, "sessions": {}, "agentToAgent": {}, "mcp": [] },
  "channels": { "discord": {}, "telegram": {} },
  "redaction": "..."
}
```

## Implementation Plan
1. Preflight
   - Ensure Codex/build status; avoid collision if active in Mission Control.
   - Read current endpoint/test files.
2. Alias route
   - Add `src/app/api/config/effective-redacted/route.ts` delegating to same library function.
3. Library hardening
   - Extend `EffectiveConfigRedacted` with `runtimes`, `tools`, `mcp`, and non-secret channel summary.
   - Keep output compact and explicit; do not dump whole config tree.
4. Tests
   - Extend unit tests for tools/MCP/channels redaction.
   - Add serialized denylist assertions.
5. Gates
   - `npm test -- tests/openclaw-readonly-diagnostics.test.ts`
   - `npm run typecheck`
   - route curl proof for both endpoints
   - response secret scan
6. Deployment
   - Build/restart only after explicit approval or sprint allowance.
   - Use `mc-restart-safe`; no direct restart.
7. Documentation
   - Link endpoint in Atlas orchestrator index and Hermes playbook.

## Stop Conditions
- Codex/build active in Mission Control and touching same files.
- Any test reveals possible secret leakage.
- Need for config/gateway changes.
- Build red.

## Recommended Next Action
Create a Forge implementation task or run as an Atlas/Forge bounded sprint slice once Mission Control worktree is clear.

## Implementation Update 2026-05-04 23:00 CEST
Implemented in Mission Control repo commit `27ad9cc`:
- Added alias route `src/app/api/config/effective-redacted/route.ts`.
- Extended redacted diagnostics with runtime/tool/MCP/Telegram summaries.
- Hardened tests to assert MCP command basename only, no args/secret path leakage, and no channel/tool/runtime secret leakage.

Gates run:
- `./node_modules/.bin/vitest run tests/openclaw-readonly-diagnostics.test.ts` — passed, 8 tests.
- `npm run typecheck` — passed.

Blocked/postponed gate:
- Production build/live curl proof not run by Atlas because Codex already had `mc-restart-safe --refresh-build 600 codex-board-quality-final-network-clean` / `next build` active. Do not collide with active Codex build. Next gate after Codex finishes: build if needed, safe restart if approved, curl `/api/config/effective-redacted` + secret scan.
