# OpenClaw Read-only API/MCP Activation Plan

> **For Hermes:** Execute only after Piet explicitly approves the relevant gate in the current Discord thread. No restarts/deploys without live evidence and exact command disclosure.

**Goal:** Activate and verify the already implemented read-only Mission Control API endpoints and Hermes MCP tools without disturbing OpenClaw runtime state.

**Architecture:** Mission Control serves three GET-only diagnostic endpoints. Hermes `mc-readonly` MCP wraps those endpoints with bounded read-only tools. Activation requires Mission Control deploy/restart first, then Hermes MCP reload/restart only if tool discovery does not update automatically.

**Tech Stack:** Next.js Mission Control, TypeScript route handlers, Python FastMCP, user systemd services, local curl post-checks.

---

## Current Completed State

Implemented and locally verified:

```text
/home/piet/.openclaw/workspace/mission-control/src/lib/openclaw-readonly-diagnostics.ts
/home/piet/.openclaw/workspace/mission-control/src/app/api/ops/openclaw/effective-config-redacted/route.ts
/home/piet/.openclaw/workspace/mission-control/src/app/api/ops/openclaw/model-runtime-failures/route.ts
/home/piet/.openclaw/workspace/mission-control/src/app/api/ops/openclaw/session-health/route.ts
/home/piet/.openclaw/workspace/mission-control/tests/openclaw-readonly-diagnostics.test.ts
/home/piet/.hermes/mcp/mc_readonly_server.py
```

MCP backup:

```text
/home/piet/.hermes/mcp/mc_readonly_server.py.bak-20260503T183433Z
```

Last verified before this activation plan:

```text
npx vitest run tests/openclaw-readonly-diagnostics.test.ts  # 7 passed
npm run typecheck                                          # exit 0
python3 -m py_compile /home/piet/.hermes/mcp/mc_readonly_server.py  # exit 0
FORCE_BUILD=1 NEXT_DIST_DIR=.next-hermes-readonly-build BUILD_WAIT_FOR_ACTIVE_LOCK=1 npm run build  # exit 0, BUILD_ID present
```

No Mission Control deploy/restart done yet. No Hermes restart done yet. No OpenClaw config changes done.

---

## Gate A: Preflight Before Activation

**Objective:** Confirm nothing drifted since implementation.

**Files:**
- Read: `/home/piet/.openclaw/workspace/mission-control`
- Read: `/home/piet/.hermes/mcp/mc_readonly_server.py`
- Write: none

**Steps:**

1. Check current time and service state:
   ```bash
   date -u +%Y-%m-%dT%H:%MZ
   systemctl --user show mission-control.service --property=Id,ActiveState,SubState,MainPID,NRestarts,ExecMainStatus,Result
   systemctl --user show openclaw-gateway.service --property=Id,ActiveState,SubState,MainPID,NRestarts,ExecMainStatus,Result
   ```

2. Check dirty tree and own files:
   ```bash
   cd /home/piet/.openclaw/workspace/mission-control
   git status --short
   git status --short -- \
     src/lib/openclaw-readonly-diagnostics.ts \
     src/app/api/ops/openclaw/effective-config-redacted/route.ts \
     src/app/api/ops/openclaw/model-runtime-failures/route.ts \
     src/app/api/ops/openclaw/session-health/route.ts \
     tests/openclaw-readonly-diagnostics.test.ts
   ```

3. Re-run focused verification:
   ```bash
   cd /home/piet/.openclaw/workspace/mission-control
   npx vitest run tests/openclaw-readonly-diagnostics.test.ts
   npm run typecheck
   python3 -m py_compile /home/piet/.hermes/mcp/mc_readonly_server.py
   ```

**Expected:** tests/typecheck/py_compile pass. If not, stop and report.

---

## Gate B: Mission Control Build/Deploy Approval

**Objective:** Make new API routes live on port 3000.

**Requires Piet approval phrase:**

```text
Freigabe für Mission-Control Deploy/Restart Gate B
```

**Before executing, state exact command selected from live evidence.** Preferred candidates, depending on repo/runbook reality:

```bash
cd /home/piet/.openclaw/workspace/mission-control
./deploy.sh
```

or, if deploy script/runbook indicates systemd restart is canonical:

```bash
systemctl --user restart mission-control.service
```

**Important:** Do not guess. Inspect `deploy.sh`, `ecosystem.config.js`, service status, and existing runbook/context before selecting final command.

**Expected post-check:**

```bash
curl -sS --max-time 5 -H 'x-actor-kind: system' -H 'x-request-class: read' \
  http://127.0.0.1:3000/api/health
```

Expected: HTTP 200 JSON health.

---

## Gate C: API Endpoint Post-checks

**Objective:** Verify the three new GET-only endpoints are live and safe.

**Commands:**

```bash
curl -sS --max-time 5 -H 'x-actor-kind: system' -H 'x-request-class: read' \
  http://127.0.0.1:3000/api/ops/openclaw/effective-config-redacted

curl -sS --max-time 5 -H 'x-actor-kind: system' -H 'x-request-class: read' \
  'http://127.0.0.1:3000/api/ops/openclaw/model-runtime-failures?window=10m&limit=20'

curl -sS --max-time 10 -H 'x-actor-kind: system' -H 'x-request-class: read' \
  'http://127.0.0.1:3000/api/ops/openclaw/session-health?active=30m'
```

**Expected:**

- effective config returns `mode: read-only-redacted`
- no raw API keys/tokens/secrets in response
- model-runtime-failures returns bounded `counts` + `events`
- session-health returns compact `summary` + `sessions`

**Secret safety check:** Run a targeted local check that response does not include known secret-shaped field values. Do not print secrets.

---

## Gate D: Hermes MCP Discovery/Reload

**Objective:** Make new MCP tools available to Hermes.

**First try:** no service restart; check if current Hermes session can see/use new tools after Mission Control deploy. If tools are unavailable, use least invasive reload path.

**Requires Piet approval phrase if restart/reload needed:**

```text
Freigabe für Hermes MCP Reload/Restart Gate D
```

**Possible actions, in order:**

1. Try current session tool discovery / new conversation reset if enough.
2. If unavailable, identify exact Hermes service ownership and restart command from live evidence.
3. Only then restart the precise Hermes service, not OpenClaw.

**Never:** replace Hermes tokens with OpenClaw/Piet Discord tokens.

**MCP post-checks:**

Use the new tools once available:

```text
mc_openclaw_effective_config_redacted()
mc_openclaw_model_runtime_failures(window='10m', limit=20)
mc_openclaw_session_health(active_minutes=30)
mc_endpoint_status()
```

**Expected:** HTTP 200 for new endpoints in MCP body.

---

## Gate E: Receipt and Atlas Handoff

**Objective:** Persist activation evidence and tell Atlas/Forge what changed.

**Create receipt:**

```text
/home/piet/vault/03-Agents/Hermes/receipts/2026-05-03_openclaw-readonly-api-mcp-activation-receipt.md
```

**Include:**

```text
- approval phrase/time
- exact commands run
- service status before/after
- API post-check summary
- MCP post-check summary
- files changed
- backup path
- dirty working tree caveat
- rollback command/path
- no OpenClaw config changes confirmation
- no token changes confirmation
```

**Atlas handoff block:**

```yaml
for_atlas:
  status: activated | partial | failed
  new_api_endpoints:
    - /api/ops/openclaw/effective-config-redacted
    - /api/ops/openclaw/model-runtime-failures
    - /api/ops/openclaw/session-health
  new_mcp_tools:
    - mc_openclaw_effective_config_redacted
    - mc_openclaw_model_runtime_failures
    - mc_openclaw_session_health
  restrictions:
    - read_only
    - redacted
    - local_mission_control_only
  restart_deploy_performed: true | false
  hermes_reload_performed: true | false
```

---

## Rollback Plan

If Mission Control deploy fails or API post-checks fail:

1. Do not proceed to Hermes MCP reload.
2. Revert/remove new Mission Control files or restore from git/worktree state.
3. If `mc_readonly_server.py` caused issues, restore:
   ```bash
   cp /home/piet/.hermes/mcp/mc_readonly_server.py.bak-20260503T183433Z \
      /home/piet/.hermes/mcp/mc_readonly_server.py
   ```
4. Re-run:
   ```bash
   npm run typecheck
   python3 -m py_compile /home/piet/.hermes/mcp/mc_readonly_server.py
   ```
5. Restart only the service that was changed, and only with approval.
6. Write failed/rollback receipt.

---

## Recommended Next Step

Run **Gate A only** first. If still green, ask Piet for Gate B approval with the exact Mission Control deploy/restart command selected from live evidence.
