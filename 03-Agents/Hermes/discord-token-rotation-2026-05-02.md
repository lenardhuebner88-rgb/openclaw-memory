---
title: Discord Token Rotation - 2026-05-02
status: done
created: 2026-05-02
owner: Piet
scope: discord-hygiene
---

# Discord Token Rotation - 2026-05-02

## Outcome

Piet/OpenClaw Discord now uses app/user ID `1486895358725460069` consistently.

Hermes remains separate on app/user ID `1500199614706483210`.

## Updated Runtime Locations

- `/home/piet/.openclaw/config/openclaw-discord-bot.env`
- `/home/piet/.openclaw/gateway.systemd.env`
- `/home/piet/.openclaw/.env`
- `/home/piet/.openclaw/openclaw.json`
- `/home/piet/.openclaw/workspace/mission-control/.env`
- `/home/piet/.openclaw/workspace/mission-control/.env.local`

Schema correction:

- `channels.discord.token` is valid and was updated.
- `channels.discord.botToken` is invalid and is absent.
- `plugins.entries.discord.token` is invalid and is absent.
- `gateway.auth.token` was not touched.

## Validation

- `openclaw config validate` passed.
- `openclaw-gateway.service` active and `/health` returned HTTP 200.
- `mission-control.service` active and `/api/health` returned HTTP 200.
- `openclaw-discord-bot.service` active and logged in as `Piet (1486895358725460069)`.
- Mission Control `/api/discord/send` smoke succeeded with message ID `1500222107198685285`.
- `hermes-gateway.service` active and Discord connected.

## Hygiene

- Removed unused `CLAUDE_BIN` from the Piet/OpenClaw Discord bot config and script.
- Reworded misleading Claude bridge text in the Piet/OpenClaw Discord bot help/docstring.
- Fixed invalid systemd `Documentation=` entry.
- Switched Piet/OpenClaw Discord bot systemd stdout/stderr to journal to stop duplicate file-log writes.
- Updated Hermes Discord playbook and working context with the token-rotation runbook.
- Removed the Discord privileged message-content warning by switching the Piet/OpenClaw bot from `commands.Bot(command_prefix='!')` to a plain `discord.Client` plus `app_commands.CommandTree`. Slash commands remain active, and `message_content` stays disabled.

## Backups

- `/home/piet/backups/piet-discord-token-20260502-213710`
- `/home/piet/backups/piet-discord-token-comprehensive-20260502-214024`
- `/home/piet/backups/discord-hygiene-20260502-214439`
- `/home/piet/backups/hermes-runbook-link-20260502-214608`

## Runbook

- `/home/piet/vault/03-Agents/Hermes/playbooks/discord-token-rotation.md`
