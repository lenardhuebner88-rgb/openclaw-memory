---
title: OpenClaw Read-only API/MCP Implementation Plan
created: 2026-05-03T18:23Z
agent: Hermes
for: Piet, Atlas, Forge
status: proposed_plan
scope: openclaw-readonly-api-mcp-improvements
mutation_level: plan_only_no_runtime_changes
---

# OpenClaw Read-only API/MCP Implementation Plan

> **For Atlas/Forge:** This is a feasibility verdict and implementation plan only. It does not record a Mission Control deploy, OpenClaw config change, Hermes config change, or service restart.

**Goal:** Add structured read-only OpenClaw/Mission-Control evidence surfaces so Hermes can diagnose model/runtime/session/config issues faster and safer.

**Architecture:** Implement new GET-only Mission Control API routes under `src/app/api/ops/openclaw/*`, then expose them through the existing Hermes `mc-readonly` MCP server. Keep all tools read-only, redacted, local-only, and explicitly allowlisted.

**Tech Stack:** Next.js 15 route handlers, TypeScript, Mission Control ingress enforcement, Hermes Python FastMCP servers, local HTTP to `127.0.0.1:3000`, systemd-gated deploy/restart after approval.

---

## Feasibility Verdict

**Yes — we can implement this ourselves with explicit approval.** The codebase already has the right building blocks:

1. Mission Control is a Next.js app with many existing GET route handlers under:
   ```text
   /home/piet/.openclaw/workspace/mission-control/src/app/api/**/route.ts
   ```
2. Existing routes use a consistent read gate:
   ```ts
   validateIngress(..., { actorKinds: [...], requestClasses: ['read'] })
   ```
3. Existing `ops/skill-plugin-inventory` already reads OpenClaw files and redacts secret-shaped keys.
4. Hermes already has native MCP configured in:
   ```text
   /home/piet/.hermes/config.yaml
   ```
   with existing servers:
   ```text
   mc-readonly -> /home/piet/.hermes/mcp/mc_readonly_server.py
   openclaw-readonly -> /home/piet/.hermes/mcp/openclaw_readonly_server.py
   ```
5. `mc-readonly` is deliberately GET-only and easy to extend with new allowlisted tools.

## Important Current Evidence

Inspected files:

```text
/home/piet/.openclaw/workspace/mission-control/package.json
/home/piet/.openclaw/workspace/mission-control/src/app/api/health/route.ts
/home/piet/.openclaw/workspace/mission-control/src/app/api/ops/skill-plugin-inventory/route.ts
/home/piet/.openclaw/workspace/mission-control/src/lib/ingress-enforcement.ts
/home/piet/.hermes/mcp/mc_readonly_server.py
/home/piet/.hermes/mcp/openclaw_readonly_server.py
/home/piet/.openclaw/mcp-servers/taskboard/server.js
```

Observed constraints:

```text
Mission Control repo has existing uncommitted changes from other work.
Do not overwrite unrelated files.
Need coordination lock before writes.
Need build/typecheck before restart/deploy.
Need Hermes gateway reset/restart only if MCP tool config changes must be loaded.
```

## Non-goals

- No write/admin MCP tools.
- No config editing endpoint.
- No restart endpoint.
- No task/cron/agent creation endpoint.
- No token exposure.
- No broad raw journal dump endpoint.
- No route that returns full `openclaw.json`.

---

## Target API Surface

### Endpoint 1: Effective redacted OpenClaw config

```text
GET /api/ops/openclaw/effective-config-redacted
```

**Purpose:** Answer routing/config questions without shell-reading full `openclaw.json`.

**Reads:**

```text
/home/piet/.openclaw/openclaw.json
```

**Returns only:**

```ts
type EffectiveConfigRedacted = {
  generatedAt: string;
  mode: 'read-only-redacted';
  source: { configPath: string };
  openclaw?: { version?: string | null };
  agents: {
    defaults?: { agentRuntime?: unknown; model?: unknown; models?: unknown };
    list: Array<{
      id?: string;
      name?: string;
      model?: unknown;
      agentRuntime?: unknown;
      enabled?: boolean;
    }>;
  };
  models: {
    providers: Array<{
      id: string;
      baseUrlHost?: string | null;
      api?: unknown;
      auth?: unknown;
      authHeader?: unknown;
      modelIds?: string[];
    }>;
  };
  plugins: {
    entries?: unknown;
    allow?: unknown;
  };
  channels: {
    discord?: {
      enabled?: unknown;
      streaming?: unknown;
      commands?: unknown;
      channelIds?: unknown;
    };
  };
  redaction: string;
};
```

**Redaction rule:** Never return values for keys matching:

```text
key|token|secret|password|credential|authorization|bearer|apiKey|clientSecret|refresh|access
```

For URLs, return host only where possible.

### Endpoint 2: Model/runtime failures summary

```text
GET /api/ops/openclaw/model-runtime-failures?window=30m&limit=100
```

**Purpose:** Structured journal classification for model/runtime problems.

**Reads:**

```text
journalctl --user -u openclaw-gateway.service --since <safe-window> --no-pager -n <safe-limit>
```

**Accepted windows:**

```text
10m, 30m, 2h, 6h
```

**Classes:**

```text
provider_not_found
fetch_timeout
codex_app_server_timeout
failover_error
lane_task_error
command_lane_timeout
tool_call_format_error
discord_send_failed
native_hook_relay_not_found
```

**Output:**

```ts
type ModelRuntimeFailures = {
  generatedAt: string;
  window: string;
  limit: number;
  counts: Record<string, number>;
  events: Array<{
    timestamp?: string;
    class: string;
    service: 'openclaw-gateway.service';
    agentId?: string;
    lane?: string;
    provider?: string;
    model?: string;
    sessionId?: string;
    message: string; // truncated + secret-redacted
  }>;
};
```

**Safety:** truncate messages to ~500 chars and redact secret-shaped substrings.

### Endpoint 3: Session health summary

```text
GET /api/ops/openclaw/session-health?active=180m
```

**Purpose:** Distinguish gateway liveness from stuck agent/session/lane state.

**Implementation choice:** Prefer reading OpenClaw CLI JSON via the Node v22 wrapper:

```text
/home/piet/bin/openclaw sessions --all-agents --active <safe-minutes> --json
```

**Accepted active range:** 5–1440 minutes.

**Output:**

```ts
type SessionHealthSummary = {
  generatedAt: string;
  activeMinutes: number;
  commandExitCode: number;
  summary: {
    total: number;
    byStatus: Record<string, number>;
    suspectedStuck: number;
    withErrors: number;
  };
  sessions: Array<{
    agentId?: string;
    sessionId?: string;
    status?: string;
    updatedAt?: string;
    modelProvider?: string;
    model?: string;
    inputTokens?: number;
    outputTokens?: number;
    lastErrorClass?: string | null;
    suspectedStuck?: boolean;
  }>;
};
```

**Stuck heuristics:** conservative only:

```text
status=running with old updatedAt
outputTokens small/unchanged where field exists
error text includes active_embedded_run / queued_work_without_active_run / timed out
```

---

## Target MCP Surface

Patch only:

```text
/home/piet/.hermes/mcp/mc_readonly_server.py
```

Add read-only tools:

```python
mc_openclaw_effective_config_redacted()
mc_openclaw_model_runtime_failures(window='30m', limit=100)
mc_openclaw_session_health(active_minutes=180)
```

Also update `mc_endpoint_status()` allowlist to include:

```text
/api/ops/openclaw/effective-config-redacted
/api/ops/openclaw/model-runtime-failures?window=10m&limit=20
/api/ops/openclaw/session-health?active=30m
```

**Do not add MCP write tools.**

---

## Implementation Plan

### Task 0: Preflight and coordination

**Objective:** Avoid colliding with active Atlas/Forge work.

**Files:**
- Create/update coordination note in `/home/piet/vault/_agents/_coordination/`.
- Read git status in `/home/piet/.openclaw/workspace/mission-control`.

**Steps:**
1. Check for active coordination locks touching Mission Control or Hermes MCP files.
2. Run:
   ```bash
   cd /home/piet/.openclaw/workspace/mission-control && git status --short
   ```
3. If unrelated files are dirty, avoid touching them and mention dirty working tree in receipt.

**Expected:** safe to touch only new route files + MCP server file.

### Task 1: Add shared OpenClaw diagnostics library

**Objective:** Keep route files small and testable.

**Create:**

```text
/home/piet/.openclaw/workspace/mission-control/src/lib/openclaw-readonly-diagnostics.ts
```

**Functions:**

```ts
readOpenClawConfigRedacted(): EffectiveConfigRedacted
getOpenClawModelRuntimeFailures(opts): Promise<ModelRuntimeFailures>
getOpenClawSessionHealth(opts): Promise<SessionHealthSummary>
redactSecrets(value: unknown): unknown
redactText(text: string): string
safeWindow(input: string | null): '10m' | '30m' | '2h' | '6h'
safeLimit(input: string | null): number
```

**Notes:**
- Use `node:fs`, `node:path`, `node:child_process`.
- Use `/home/piet/bin/openclaw` for CLI calls.
- Use bounded `execFile`, not shell string.
- Add command timeout.

### Task 2: Add effective config route

**Create:**

```text
src/app/api/ops/openclaw/effective-config-redacted/route.ts
```

**Pattern:**

```ts
import { NextResponse } from 'next/server';
import { withApiMetrics } from '@/lib/api-metrics';
import { validateIngress } from '@/lib/ingress-enforcement';
import { readOpenClawConfigRedacted } from '@/lib/openclaw-readonly-diagnostics';

function handler(request: Request) {
  const ingress = validateIngress({
    route: 'ops/openclaw/effective-config-redacted',
    actorKind: request.headers.get('x-actor-kind') ?? 'human',
    requestClass: request.headers.get('x-request-class') ?? 'read',
  }, { actorKinds: ['human', 'service', 'system'], requestClasses: ['read'] });
  if (!ingress.ok) return NextResponse.json({ error: ingress.error }, { status: ingress.status });
  return NextResponse.json(readOpenClawConfigRedacted(), { headers: { 'Cache-Control': 'no-store, max-age=0' } });
}

export const GET = withApiMetrics({ route: '/api/ops/openclaw/effective-config-redacted', method: 'GET' }, handler);
```

### Task 3: Add model/runtime failures route

**Create:**

```text
src/app/api/ops/openclaw/model-runtime-failures/route.ts
```

**Behavior:**
- Validate read ingress.
- Parse query params `window`, `limit`.
- Return classified journal events.
- No raw unbounded logs.

### Task 4: Add session health route

**Create:**

```text
src/app/api/ops/openclaw/session-health/route.ts
```

**Behavior:**
- Validate read ingress.
- Parse query param `active` supporting `30m`, `180m`, or number minutes.
- Return compact sessions only.
- Include command exit code/stderr summary if CLI fails.

### Task 5: Add tests for redaction and classifiers

**Create:**

```text
tests/openclaw-readonly-diagnostics.test.ts
```

**Test cases:**

```text
redactSecrets removes apiKey/token/secret/password values
URL redaction returns host only
classify provider-not-found lines
classify fetch-timeout lines
safeWindow rejects arbitrary shell input
safeLimit clamps large values
session summary marks obvious running+old session as suspectedStuck
```

**Run:**

```bash
cd /home/piet/.openclaw/workspace/mission-control
npm run typecheck
npx vitest run tests/openclaw-readonly-diagnostics.test.ts
```

If `typecheck` is noisy due existing repo state, still run the targeted test and report exact failure separately.

### Task 6: Patch Hermes `mc-readonly` MCP server

**Modify:**

```text
/home/piet/.hermes/mcp/mc_readonly_server.py
```

**Add:**

```python
@mcp.tool(description="Read redacted OpenClaw effective config via Mission Control.", annotations=READ_ONLY)
def mc_openclaw_effective_config_redacted() -> dict[str, Any]:
    return _get('/api/ops/openclaw/effective-config-redacted')

@mcp.tool(description="Read structured OpenClaw model/runtime failures via Mission Control.", annotations=READ_ONLY)
def mc_openclaw_model_runtime_failures(window: str = '30m', limit: int = 100) -> dict[str, Any]:
    ...

@mcp.tool(description="Read OpenClaw session health summary via Mission Control.", annotations=READ_ONLY)
def mc_openclaw_session_health(active_minutes: int = 180) -> dict[str, Any]:
    ...
```

**Safety:** build query with local allowlist/clamps. Do not expose arbitrary path fetch.

### Task 7: Local verification before restart/deploy

**Run:**

```bash
cd /home/piet/.openclaw/workspace/mission-control
npm run typecheck
npx vitest run tests/openclaw-readonly-diagnostics.test.ts
npm run build
```

**Then, if Mission Control is already running old build:** do not restart until Piet approves exact restart/deploy command.

### Task 8: Approved deploy/restart gate

**Only after Piet approval.**

Use the existing Mission Control safe restart discipline, not ad-hoc restart. Exact command should be selected from the current MC runbook before execution.

**Post-check:**

```bash
curl -s --max-time 5 -H 'x-actor-kind: system' -H 'x-request-class: read' \
  http://127.0.0.1:3000/api/ops/openclaw/effective-config-redacted

curl -s --max-time 5 -H 'x-actor-kind: system' -H 'x-request-class: read' \
  'http://127.0.0.1:3000/api/ops/openclaw/model-runtime-failures?window=10m&limit=20'

curl -s --max-time 10 -H 'x-actor-kind: system' -H 'x-request-class: read' \
  'http://127.0.0.1:3000/api/ops/openclaw/session-health?active=30m'
```

### Task 9: Hermes MCP reload/restart gate

MCP discovery happens at Hermes startup. After patching `mc_readonly_server.py`, new tools may require Hermes `/reset` or gateway restart/reload depending on runtime behavior.

**Only after Piet approval**, use the least invasive option first:

```text
/reset in this Hermes thread if enough
or Hermes gateway restart if tools do not appear
```

**Verify:**

```text
new MCP tools appear and return data
existing mc-readonly tools still work
```

### Task 10: Receipt

**Create:**

```text
/home/piet/vault/03-Agents/Hermes/receipts/YYYY-MM-DD_openclaw-readonly-api-mcp_receipt.md
```

Include:

```text
files changed
preflight dirty git state
backup paths if any
commands run
test/build results
restart/deploy approval phrase/time if used
post-check outputs summarized
rollback notes
for_atlas block
```

---

## Risk Assessment

| Risk | Level | Mitigation |
|---|---:|---|
| Secret leakage from redacted config | High | strict key redaction, URL host-only, tests with fake secrets |
| Journal endpoint returns too much raw data | Medium | fixed classes, truncation, limit/window clamps |
| Mission Control dirty working tree collision | Medium | create only new files, inspect git status, coordination note |
| Build/deploy affects MC UI | Medium | typecheck/test/build before restart; safe restart only after approval |
| MCP tool not visible until Hermes restart | Low | document reload/restart gate |
| Endpoint becomes mutation path | Low if scoped | GET-only, read ingress, no write/admin classes |

## Rollback Plan

If implementation breaks build or post-check:

1. Revert new route/library/test files.
2. Restore previous `mc_readonly_server.py` from timestamped backup if patched.
3. Rebuild Mission Control.
4. Restart only with approval if service had been changed.
5. Write failed/rollback receipt.

## Recommended Execution Scope

Recommended first execution batch:

```text
Task 0-7 only: code + tests + build, no service restart.
```

Then report build/test result. If green, request/confirm deploy/restart gate for Task 8-9.

## for_atlas

```yaml
for_atlas:
  status: needs_piet_approval
  affected_agents:
    - Hermes
    - Atlas
    - Forge
  affected_files:
    - /home/piet/.openclaw/workspace/mission-control/src/lib/openclaw-readonly-diagnostics.ts
    - /home/piet/.openclaw/workspace/mission-control/src/app/api/ops/openclaw/effective-config-redacted/route.ts
    - /home/piet/.openclaw/workspace/mission-control/src/app/api/ops/openclaw/model-runtime-failures/route.ts
    - /home/piet/.openclaw/workspace/mission-control/src/app/api/ops/openclaw/session-health/route.ts
    - /home/piet/.openclaw/workspace/mission-control/tests/openclaw-readonly-diagnostics.test.ts
    - /home/piet/.hermes/mcp/mc_readonly_server.py
  recommended_next_action: "If Piet approves implementation, execute Tasks 0-7 first without service restart; then separately gate Mission Control deploy/restart and Hermes MCP reload."
  risk: "Medium overall because Mission Control code/build is touched; runtime risk stays low if execution stops before restart/deploy."
  evidence_files:
    - /home/piet/vault/03-Agents/Hermes/plans/hermes-openclaw-collaboration-improvement-plan-2026-05-03.md
    - /home/piet/vault/03-Agents/Hermes/INDEX.md
```
