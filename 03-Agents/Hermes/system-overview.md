---
title: Hermes System Overview
status: active
created: 2026-05-02
owner: Piet
scope: hermes-debug-context
---

# Hermes System Overview

This is Hermes' first-read system map for Piet's local OpenClaw/Homeserver environment.

## Role Split

- OpenClaw / Atlas is the primary operating system for agents, dispatch, Mission Control, cron/system jobs, and the main Discord agent channels.
- Piet/OpenClaw Discord bot is the dedicated Discord command surface for OpenClaw agents.
- Hermes Agent is a shadow debug and backup assistant. Hermes reads context, applies runbooks, summarizes incidents, and may perform bounded break-glass recovery only after live evidence and Piet approval.

## Active Bot Surfaces

- Piet/OpenClaw bot:
  - service: `openclaw-discord-bot.service`
  - script: `/home/piet/.openclaw/scripts/openclaw-discord-bot.py`
  - env: `/home/piet/.openclaw/config/openclaw-discord-bot.env`
  - expected Discord identity: `Piet (1486895358725460069)`
- OpenClaw Gateway Discord provider:
  - service: `openclaw-gateway.service`
  - config: `/home/piet/.openclaw/openclaw.json`
  - expected Discord identity: `Piet (1486895358725460069)`
- Hermes bot:
  - service: `hermes-gateway.service`
  - config: `/home/piet/.hermes/config.yaml`
  - env: `/home/piet/.hermes/.env`
  - expected Discord app/user ID: `1500199614706483210`

## Canonical Paths

- Active vault: `/home/piet/vault`
- Agent planning SSoT: `/home/piet/vault/03-Agents/`
- Hermes context: `/home/piet/vault/03-Agents/Hermes/working-context.md`
- Hermes playbooks: `/home/piet/vault/03-Agents/Hermes/playbooks/`
- Sprint index: `/home/piet/vault/04-Sprints/INDEX.md`
- KB compiler output: `/home/piet/vault/10-KB/`
- OpenClaw config: `/home/piet/.openclaw/openclaw.json`
- OpenClaw Gateway env: `/home/piet/.openclaw/gateway.systemd.env`
- Mission Control workspace: `/home/piet/.openclaw/workspace/mission-control`
- Mission Control data: `/home/piet/.openclaw/state/mission-control/data`
- OpenClaw memory bulk: `/home/piet/.openclaw/workspace/memory/`
- Wrong-vault trap: `/home/piet/Vault`

## Services And Ports

- `openclaw-gateway.service`: OpenClaw Gateway on `http://127.0.0.1:18789/health`
- `mission-control.service`: Mission Control on `http://127.0.0.1:3000/api/health`
- `openclaw-discord-bot.service`: Piet/OpenClaw slash-command bot
- `hermes-gateway.service`: Hermes Discord gateway
- `qmd-mcp-http.service`: QMD MCP HTTP bridge on `127.0.0.1:8181`

## Hermes Read-only MCP Surface

- `mc-readonly`: Mission Control health, board, alerts, task snapshot, monitoring, skill/plugin inventory.
- `openclaw-readonly`: OpenClaw Gateway health, OpenClaw/Discord service status, recent warning logs, model status, recent sessions.
- `qmd-vault`: Vault/KB search and retrieval through QMD stdio MCP.

Use these before shell checks in normal Discord operation.

## Default Read-Only Checks

```bash
systemctl --user status openclaw-gateway.service mission-control.service openclaw-discord-bot.service hermes-gateway.service --no-pager --lines=30
curl -s -o /dev/null -w "openclaw=%{http_code}\n" http://127.0.0.1:18789/health
curl -s -o /dev/null -w "mc=%{http_code}\n" http://127.0.0.1:3000/api/health
journalctl --user -u openclaw-gateway.service -u mission-control.service -u openclaw-discord-bot.service -u hermes-gateway.service --since "15 minutes ago" --no-pager
```

## Hard Boundaries

- Do not create tasks, crons, agents, deploys, or broad scans unless Piet explicitly asks.
- Do not change configs without a timestamped backup.
- Do not restart services without live evidence and Piet approval, except when Piet has already approved the current break-glass task.
- Do not replace the Hermes Discord token with the Piet/OpenClaw token.
- Do not treat `/home/piet/.openclaw/workspace/vault` or `/home/piet/Vault` as the active planning vault.

## Preferred Hermes Response Shape

1. Problem
2. Evidence
3. Risk
4. Next Action
