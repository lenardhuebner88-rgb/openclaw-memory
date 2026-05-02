# Hermes API/MCP Integration Plan

Date: 2026-05-02
Owner: Piet
Scope: Hermes as shadow-debug assistant for OpenClaw/Homeserver.

## Goal

Hermes can inspect the local system through stable read-only APIs and MCP search before recommending action.

Default posture remains:

- MiniMax primary model.
- OpenAI Codex `gpt-5.5` fallback.
- OpenRouter optional manual route only.
- No tasks, crons, agents, deploys, restarts, or config edits without explicit Piet approval.

## Quality Gates

Gate 0 - Backup before mutation:

- Any Hermes config change requires a timestamped backup of `/home/piet/.hermes/config.yaml`.

Gate 1 - Read-only live evidence:

- Prove service state before any recommendation.
- Use HTTP status, service status, and recent logs.
- Do not infer current state from memory alone.

Gate 2 - Tool boundary:

- Mission Control API use starts with GET-only endpoints.
- OpenClaw status use starts with `openclaw-readonly` MCP.
- QMD MCP use starts with read-only search/retrieval tools only.
- Mutation routes stay out of the default flow.

Gate 3 - Break-glass:

- Restart/config edits require live evidence, exact command/file/key, timestamped backup when config changes, and explicit approval in the current Discord thread.

Gate 4 - Verification:

- After a config/service change, run the smallest relevant post-check.
- Document result in the E2E or playbook receipt.

## Phase 1 - Mission Control API Read-only

Stable read-only probes:

- `GET /api/health`
- `GET /api/board-consistency`
- `GET /api/tasks/snapshot`
- `GET /api/alerts`
- `GET /api/analytics/alerts`
- `GET /api/ops/skill-plugin-inventory`
- `GET /api/monitoring`

Live evidence on 2026-05-02:

- `mission-control.service`: active.
- `/api/health`: HTTP 200, JSON status currently `degraded`.
- `/api/board-consistency`: HTTP 200, JSON status `ok`.
- `/api/tasks/snapshot`: HTTP 200.
- `/api/alerts`: HTTP 200.
- `/api/analytics/alerts`: HTTP 200, `activeCount`/`alerts` shape.
- `/api/ops/skill-plugin-inventory`: HTTP 200.
- `/api/monitoring`: HTTP 200.

## Phase 2 - QMD MCP Read-only

Configured MCP server:

```yaml
mcp_servers:
  qmd-vault:
    command: /home/piet/.local/bin/qmd
    args:
    - mcp
    timeout: 120
    connect_timeout: 30
```

Live evidence on 2026-05-02:

- `qmd-mcp-http.service`: active.
- Direct HTTP probe to `/mcp` returns MCP protocol response.
- HTTP MCP test was unstable after initialize because QMD requires `Mcp-Session-Id` on follow-up requests.
- Hermes therefore uses QMD stdio MCP for `qmd-vault`.
- `hermes mcp test qmd-vault`: connected, 6 tools discovered.
- Tools discovered: `search`, `vector_search`, `deep_search`, `get`, `multi_get`, `status`.
- QMD source marks these tools with `readOnlyHint: true`.

## Phase 3 - Incident Packages

Hermes should first select the relevant runbook, then gather evidence.

## Phase 2b - OpenClaw MCP Read-only

Configured MCP server:

```yaml
mcp_servers:
  openclaw-readonly:
    command: /home/piet/.hermes/hermes-agent/venv/bin/python
    args:
    - /home/piet/.hermes/mcp/openclaw_readonly_server.py
    timeout: 30
    connect_timeout: 15
```

Live evidence on 2026-05-02:

- `hermes mcp test openclaw-readonly`: connected, 6 tools discovered.
- Tools discovered: `openclaw_gateway_health`, `openclaw_services_status`, `openclaw_recent_logs`, `openclaw_model_status`, `openclaw_recent_sessions`, `openclaw_status_summary`.
- E2E OpenClaw Lagebild: PASS, Gateway `ok=true/status=live`, Gateway and Discord bot services active.

Core incident packages:

- Mission Control API read-only: `/home/piet/vault/03-Agents/Hermes/playbooks/mission-control-api-readonly.md`
- OpenClaw read-only MCP: `/home/piet/vault/03-Agents/Hermes/playbooks/openclaw-readonly-mcp.md`
- QMD MCP read-only: `/home/piet/vault/03-Agents/Hermes/playbooks/qmd-mcp-readonly.md`
- Mission Control down and Atlas unavailable: `/home/piet/vault/03-Agents/Hermes/playbooks/mission-control-down-atlas-unavailable.md`
- OpenClaw Gateway down: `/home/piet/vault/03-Agents/Hermes/playbooks/openclaw-gateway-down.md`
- Discord 401/429: `/home/piet/vault/03-Agents/Hermes/playbooks/gateway-discord-provider-401-429.md`
- Model routing/fallback: `/home/piet/vault/03-Agents/Hermes/playbooks/hermes-model-routing.md`

## Phase 4 - Break-glass Actions

Allowed only after explicit approval:

- targeted service restart;
- small config edit with timestamped backup;
- focused post-check.

Still forbidden unless Piet explicitly requests the broader operation:

- creating tasks;
- creating crons;
- creating agents;
- deploys;
- broad scans;
- YOLO/always-allow command mode.

## Acceptance

This block is done when:

- The plan exists in the Hermes vault folder.
- Mission Control read-only runbook exists.
- OpenClaw read-only runbook exists.
- QMD MCP read-only runbook exists.
- Hermes config contains `qmd-vault`.
- Hermes config contains `openclaw-readonly`.
- `hermes mcp test qmd-vault` passes.
- `hermes mcp test openclaw-readonly` passes.
- Hermes gateway is restarted after config change and active.
- E2E notes record the result and any residual issue.
