# OpenClaw/Discord Long-Term Stabilization Plan — 2026-05-03

## Objective
Make Piet's OpenClaw + Discord path resilient after 2026.5.2 by removing known drift, restoring real Discord transport monitoring, and adding repeatable use-case gates.

## Live baseline
- Gateway health: `{"ok":true,"status":"live"}`.
- `openclaw-gateway.service` and `openclaw-discord-bot.service`: active/running.
- OpenClaw core/plugin versions: `openclaw@2026.5.2`, `@openclaw/discord@2026.5.2`, `@openclaw/codex@2026.5.2`.
- Mission Control `/api/health`: ok.
- Risk signal: monitor uses `/home/piet/.npm-global/bin/openclaw`, which fails under Node v20; rich Discord health is therefore skipped.
- Risk signal: OpenClaw config still enables Hermes' private channel `1486480293153214515`; intended isolation says OpenClaw must not reach it.
- Cosmetic drift: systemd description drop-in still overrides service label to `v2026.4.27`.

## Changes
1. **Restore real Discord transport watchdog**
   - Patch `/home/piet/.openclaw/scripts/gateway-memory-monitor.py` default `OPENCLAW_BIN` to `/home/piet/bin/openclaw` (Node v22 wrapper).
   - Add/keep service env `OPENCLAW_BIN=/home/piet/bin/openclaw`.
   - Gate: one monitor run logs `discord_watchdog=ok connected=True transport_age_sec=<threshold`.

2. **Preserve Hermes/OpenClaw channel isolation**
   - Disable `channels.discord.guilds.1486464140246520068.channels.1486480293153214515.enabled` in active config and last-good copies.
   - Gate: config parser confirms value `false`; OpenClaw validator passes; gateway restart health green.

3. **Clean service metadata drift**
   - Update/remove stale drop-in `description-version.conf` so service label matches `2026.5.2`.
   - Gate: `systemctl --user status openclaw-gateway.service` displays v2026.5.2.

4. **Install repeatable long-term stability use-case test harness**
   - Create `/home/piet/.openclaw/scripts/openclaw-longterm-stability-smoketest.py`.
   - Use cases:
     1. Gateway HTTP health.
     2. Rich OpenClaw health includes Discord connected/running + plugins clean.
     3. Mission Control health ok.
     4. Plugin inventory includes Discord channel and Codex provider.
     5. Direct Atlas reply via `openclaw agent --agent main`.
     6. Direct system-bot reply via `openclaw agent --agent system-bot`.
     7. Recent journal scan for known error patterns.
     8. Optional short soak.
   - Gate: script exits 0 and writes JSON report under `/home/piet/.openclaw/workspace/logs/stability/`.

## Rollback
- Each touched file gets timestamped backup before mutation.
- Rollback config: restore backed-up `openclaw.json`, `openclaw.json.last-good`, and config-guard last-good; restart gateway; health check.
- Rollback monitor: restore backed-up monitor script/service; `systemctl --user daemon-reload && systemctl --user restart gateway-memory-monitor.timer`.

## Done criteria
- Config validator OK.
- Gateway + Discord bot active/running.
- `/health` live.
- `openclaw health --json` returns Discord `connected=true`.
- Monitor logs real `discord_watchdog=ok`, not `no_discord_health`.
- Long-term stability smoketest PASS.
- 5-minute soak: health OK, no known error patterns.
