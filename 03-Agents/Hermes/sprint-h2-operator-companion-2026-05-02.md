---
title: Hermes Sprint H-2 Operator Companion
status: completed
created: 2026-05-02
owner: Piet
scope: hermes-operator-companion
---

# Sprint H-2: Hermes Operator Companion

Date: 2026-05-02
Owner: Piet
System: Hermes + OpenClaw + Mission Control + QMD

## Goal

Make Hermes useful as an OpenClaw operator companion without making it a second lead system.

Hermes should:

- inspect OpenClaw/Mission Control/QMD state read-only first;
- search Vault/KB context through QMD;
- select the correct runbook;
- summarize incidents in `Problem / Evidence / Risk / Next Action`;
- prepare break-glass actions only after live evidence and Piet approval.

Hermes must not:

- create OpenClaw tasks;
- create crons;
- add agents;
- deploy;
- silently restart services;
- silently edit config;
- use YOLO or permanent command allowlists.

## Research Inputs

- Hermes MCP supports stdio and HTTP servers, automatic tool discovery, per-server filtering, and runtime MCP toolsets.
- Hermes toolsets can be configured per platform, so Discord does not need the same surface as CLI.
- Hermes Gateway approval flow waits for user confirmation on messaging platforms for dangerous commands.
- Hermes skills are on-demand procedural memory and are appropriate for durable operator workflows.

## Deliverables

1. `openclaw-operator` Hermes skill.
2. `mc-readonly` Mission Control MCP server.
3. `mc-readonly` wired into `/home/piet/.hermes/config.yaml`.
4. Security redaction enabled in Hermes config.
5. Discord tool-surface audit documented.
6. E2E tests recorded.

## Quality Gates

Gate 0 - Backup:

- Before Hermes config mutation, create `/home/piet/.hermes/config.yaml.bak-<timestamp>`.

Gate 1 - Skill:

- `hermes skills list` shows `openclaw-operator` enabled.
- A Hermes oneshot with the skill selects the correct runbook for an incident prompt.

Gate 2 - MCP:

- `hermes mcp test mc-readonly` passes.
- Tool discovery shows only read-only Mission Control tools.
- MCP tools perform GET-only calls.

Gate 3 - Tool Boundary:

- Discord tool surface is explicitly reviewed.
- Terminal/file access remains approval-gated by policy and runbooks.
- No cron/delegation/code execution enabled for Discord.

Gate 4 - E2E:

- Mission Control degraded/health test passes.
- QMD/Vault status test passes.
- Model routing/fallback test passes.
- Runbook selection test passes.
- No unauthorized mutation occurs.

## Stop Conditions

Stop and report if:

- Hermes config backup fails;
- `hermes mcp test mc-readonly` fails after one fix attempt;
- Hermes Gateway restart fails;
- a test response proposes mutation before read-only evidence;
- Discord starts producing model 400s again.
