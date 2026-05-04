# Discord Token Restore

Timestamp: 2026-05-04 20:14 CEST

## Verdict

GREEN. Discord token rotation was applied and validated without exposing the token in this report.

## Changed

- Updated active OpenClaw Discord token source in `/home/piet/.openclaw/openclaw.json`.
- Updated environment token sources used by Gateway / Mission Control / Discord helper tooling:
  - `/home/piet/.openclaw/gateway.systemd.env`
  - `/home/piet/.openclaw/.env`
  - `/home/piet/.openclaw/workspace/mission-control/.env`
  - `/home/piet/.openclaw/workspace/mission-control/.env.local`
  - `/home/piet/.openclaw/workspace/discord-secrets.env`
  - `/home/piet/.openclaw/config/openclaw-discord-bot.env`

## Backup

- `/home/piet/backups/2026-05-04-discord-token-restore-20260504T181256Z`

## Restarts

- `openclaw-gateway.service` restarted.
- `mission-control.service` restarted.
- Separate legacy `openclaw-discord-bot.service` remains inactive/disabled.

## Validation

- `openclaw config validate`: valid.
- Gateway: active, `/health` live.
- Mission Control: active, `/api/health` ok.
- `openclaw health`: Discord configured; Gateway event loop ok.
- Discord send test to channel `1495737862522405088`: success, messageId `1500923395846701171`.
- Post-restart log check: no new `401`, `Unauthorized`, `gateway/bot failed`, `channel exited`, `fatal gateway`, or `4004` events after the new token was loaded.

## Notes

- No token value is stored in this report.
- Previous 401 loop was caused by Discord invalidating the old bot token.
