# OpenClaw Legacy Commander Bot Deactivation Plan

> Scope: approved by Piet in Discord thread on 2026-05-03. Execute as a reversible service deactivation, not code deletion.

**Goal:** Remove the legacy `openclaw-discord-bot.service` as a second Discord application-command consumer for the shared OpenClaw/Piet Discord application, while keeping OpenClaw Gateway, Mission Control, and Hermes active.

**Root cause addressed:** The legacy Commander Bot and OpenClaw Gateway use the same Discord application ID (`1486895358725460069`). The Commander Bot has a `discord.py` `CommandTree`, so it receives/handles slash interactions even when guild commands are cleared, causing `CommandNotFound` and off-channel warnings for Gateway-owned commands.

## Decision

Prefer reversible deactivation over code refactor:

- Stop and disable `openclaw-discord-bot.service`.
- Do not delete scripts, env files, audit logs, or meeting artifacts.
- Preserve rollback by backing up the user unit, env file, and current script.
- Let `openclaw-gateway.service` own the shared Discord slash-command surface.

## Known Commander Functions Being Retired

- Read-only shortcuts: `/health`, `/status`, `/agents`, `/receipts`, `/logs`, `/help`
- Meeting controls: `/meeting-debate`, `/meeting-council`, `/meeting-review`, `/meeting-run-once`, `/meeting-status`, `/meeting-turn-next`
- Sprint preview: `/sprint-plan`
- Session reset: `/new`
- 15-minute heartbeat log: `heartbeat mc=active bot=alive`

Replacement paths:

- OpenClaw Gateway native commands: `/status`, `/tasks`, `/agents`, `/diagnostics`, `/help`, `/new`, `/reset`, etc.
- Mission Control read-only APIs for board/health.
- Meeting workflow should be migrated to Atlas/OpenClaw chat triggers or a namespaced OpenClaw plugin, not the shared legacy Commander Bot.

## Execution Steps

1. Capture pre-state:
   - `systemctl --user show openclaw-discord-bot.service ...`
   - Gateway health and Mission Control health.
   - Recent Commander collision logs.
2. Create timestamped backup:
   - service unit
   - drop-ins if any
   - env file
   - Commander script
3. Stop and disable service:
   - `systemctl --user stop openclaw-discord-bot.service`
   - `systemctl --user disable openclaw-discord-bot.service`
   - `systemctl --user daemon-reload`
4. Verify:
   - Commander inactive/disabled
   - Gateway live
   - Mission Control ok
   - Hermes active
   - OpenClaw Discord global commands remain present and guild commands remain zero
   - No fresh Commander logs after deactivation
5. Audit:
   - service dependency check
   - process check
   - journal scan
   - REST command registry count
   - list retired functions and replacement paths
6. Document receipt under Hermes notes.

## Rollback

```bash
systemctl --user enable --now openclaw-discord-bot.service
systemctl --user show openclaw-discord-bot.service -p ActiveState -p SubState -p NRestarts -p Result --no-pager
journalctl --user -u openclaw-discord-bot.service --since '2 minutes ago' --no-pager
```

Rollback restores the legacy bot but also restores the original slash-command collision risk unless the CommandTree is disabled first.
