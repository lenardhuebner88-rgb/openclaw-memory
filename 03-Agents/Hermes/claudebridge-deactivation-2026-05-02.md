---
title: Claudebridge Deactivation
status: done
created: 2026-05-02
owner: Codex
scope: discord-bot-cleanup
---

# Claudebridge Deactivation

Goal: keep only Piet/OpenClaw Discord for agents and Hermes Agent for Hermes.

## Kept Active

- `openclaw-discord-bot.service` - OpenClaw Discord Commander Bot
- `hermes-gateway.service` - Hermes Agent Gateway

## Disabled And Masked

- `commander-bot.service` - Personal Claude via Discord
- `claude-telegram-bridge.service` - Claude Code Telegram Bridge
- `discord-bridge.service` - old Claudebridge/OpenClaw Discord Bridge
- `atlas-autonomy-discord.service` - old Atlas Autonomy Discord Approval Bot
- `tmux-claude.service` - persistent Claude CLI tmux session manager

## Quarantine

Backup and quarantine root:

```text
/home/piet/backups/claudebridge-deactivation-20260502-212729
```

Quarantined live paths include:

- `/home/piet/bots/commander`
- `/home/piet/.openclaw/config/claude-telegram-bridge.env`
- `/home/piet/.openclaw/config/atlas-autonomy-discord.env`
- `/home/piet/.openclaw/scripts/claude-telegram-bridge.py`
- `/home/piet/.openclaw/workspace/discord-bridge`

## Verification

After cleanup:

- `openclaw-discord-bot.service`: active
- `hermes-gateway.service`: active
- legacy bridge units: masked or not loaded
- legacy bridge processes: absent
- default target wants only includes `openclaw-discord-bot.service` and `hermes-gateway.service` for this bot surface

## Notes

The Claude CLI installation and `~/.claude` data were not deleted. This cleanup removed the persistent bridge/bot surfaces, not the standalone CLI tool.
