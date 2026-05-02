---
title: Hermes Learning Packet - 2026-05-02 - Discord Token Rotation
status: active
created: 2026-05-02
owner: Piet
scope: hermes-learning
---

# Hermes Learning Packet - 2026-05-02 - Discord Token Rotation

## Context

Piet replaced the old Claudebridge Discord application with a dedicated Piet/OpenClaw Discord bot and kept Hermes as a separate Discord bot.

The system needed a clean token rotation without mixing Piet/OpenClaw and Hermes credentials.

## Live Evidence

- Piet/OpenClaw bot logged in as `Piet (1486895358725460069)`.
- OpenClaw Gateway Discord provider identified Piet / app ID `1486895358725460069`.
- Hermes remained separate on app/user ID `1500199614706483210`.
- Mission Control `/api/discord/send` smoke succeeded with message ID `1500222107198685285`.
- `openclaw config validate` passed after removing invalid token locations.

## Decision

Piet/OpenClaw token rotation must update all runtime-relevant Piet/OpenClaw locations, but must not touch Hermes' token.

Hermes should treat Discord identity drift as a high-signal configuration issue and use the token-rotation runbook before suggesting restarts.

## Fix Or Outcome

Updated Piet/OpenClaw token locations:

- `/home/piet/.openclaw/config/openclaw-discord-bot.env`
- `/home/piet/.openclaw/gateway.systemd.env`
- `/home/piet/.openclaw/.env`
- `/home/piet/.openclaw/openclaw.json`
- `/home/piet/.openclaw/workspace/mission-control/.env`
- `/home/piet/.openclaw/workspace/mission-control/.env.local`

Valid OpenClaw config field:

- `channels.discord.token`

Invalid fields to avoid:

- `channels.discord.botToken`
- `plugins.entries.discord.token`

Hermes token location:

- `/home/piet/.hermes/.env`

## Reusable Rule

For Discord token rotation, first decode the token prefix to confirm the app/user ID, then update only the matching bot's runtime locations.

Never copy the Piet/OpenClaw token into Hermes or the Hermes token into OpenClaw.

Always run `openclaw config validate` before restarting OpenClaw Gateway after `openclaw.json` changes.

## Stop Conditions

- New token decodes to Hermes app ID when rotating Piet/OpenClaw.
- New token decodes to Piet/OpenClaw app ID when rotating Hermes.
- `openclaw config validate` fails.
- Discord returns fresh `401 Unauthorized` after the update.
- Legacy Claudebridge services become unmasked or active.

## Sources

- `/home/piet/vault/03-Agents/Hermes/playbooks/discord-token-rotation.md`
- `/home/piet/vault/03-Agents/Hermes/discord-token-rotation-2026-05-02.md`
- `/home/piet/vault/03-Agents/Hermes/playbooks/discord-bot-unresponsive.md`

