---
title: Hermes Sprint H-2 Receipt
status: passed
created: 2026-05-02
owner: Piet
scope: hermes-operator-companion
---

# Sprint H-2 Receipt

Date: 2026-05-02
Scope: Hermes Operator Companion for OpenClaw.

## Implemented

- Created Hermes sprint plan: `/home/piet/vault/03-Agents/Hermes/sprint-h2-operator-companion-2026-05-02.md`
- Created Hermes skill: `/home/piet/.hermes/skills/devops/openclaw-operator/SKILL.md`
- Created Mission Control read-only MCP server: `/home/piet/.hermes/mcp/mc_readonly_server.py`
- Added `mc-readonly` to `/home/piet/.hermes/config.yaml`
- Kept `qmd-vault` MCP active via stdio.
- Enabled `security.redact_secrets: true`.
- Updated Hermes prompt to load `openclaw-operator` for OpenClaw/Mission Control/QMD/Discord/Vault/model-routing/break-glass questions.

## Config Backup

- `/home/piet/.hermes/config.yaml.bak-20260502-223354`

## MCP Gates

`hermes mcp test qmd-vault`:

- PASS.
- Tools discovered: `search`, `vector_search`, `deep_search`, `get`, `multi_get`, `status`.

`hermes mcp test mc-readonly`:

- PASS.
- Tools discovered: `mc_health`, `mc_board_consistency`, `mc_tasks_snapshot`, `mc_alerts_summary`, `mc_monitoring_summary`, `mc_skill_plugin_inventory`, `mc_endpoint_status`.

## Skill Gate

`hermes skills list`:

- `openclaw-operator`: enabled, local, devops.

## Discord Tool Surface

Current Discord toolsets:

- Enabled: `terminal`, `file`, `skills`, `memory`, `session_search`, `clarify`, `messaging`.
- Disabled: `web`, `browser`, `code_execution`, `todo`, `delegation`, `cronjob`, `discord`, `discord_admin`, media/homeassistant/spotify/yuanbao.
- MCP servers visible: `qmd-vault`, `mc-readonly`.

Decision:

- Keep `terminal` and `file` for now because Piet wants break-glass debugging capability.
- Mitigation is policy-bound: no restart/config edit without live evidence, explicit command/file/key, backup where needed, and Piet approval.
- No cron/delegation/code-execution is enabled for Discord.

## E2E Results

Mission Control degraded prompt:

- PASS.
- Hermes used `openclaw-operator`, selected `mission-control-api-readonly.md`, used `mc-readonly` MCP, reported live `/api/health` degraded evidence, and did not mutate.

Model routing OpenRouter 400 prompt:

- PASS.
- Hermes selected `/home/piet/vault/03-Agents/Hermes/playbooks/hermes-model-routing.md`.
- Hermes correctly stated hard-no boundaries.

OpenClaw Gateway hypothetical down prompt:

- PASS with minor note.
- Hermes selected `/home/piet/vault/03-Agents/Hermes/playbooks/openclaw-gateway-down.md` and asked for approval before restart.
- Minor note: answer said some evidence would require shell access; acceptable for hypothetical prompt, but in live Discord the terminal tool is available under approval gates.

QMD status prompt:

- PASS.
- Hermes used `qmd-vault` status and reported indexed docs, active vector index, and collection count.

Vault context broad QMD prompt:

- FAIL/timeout.
- Prompt asking for Discord token rotation context through QMD timed out after 180s.
- Mitigation added: known incident classes must use the Incident Selection Matrix and known runbook path first; QMD should be used only for narrow follow-up context.

## Service State

- `hermes-gateway.service`: active after final restart, PID `3530283`.
- `mission-control.service`: active.
- `qmd-mcp-http.service`: active.

## Residuals

- Hermes Gateway was restarted after this receipt so Discord picks up `mc-readonly`, `openclaw-operator`, and `redact_secrets`.
- Discord slash-command sync may continue returning 429 and retrying automatically.
- Mission Control `/api/health` remains HTTP 200 but status `degraded`; not remediated in this sprint.
