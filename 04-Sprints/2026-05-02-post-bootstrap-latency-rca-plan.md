# 2026-05-02 Post-Bootstrap Latency RCA Plan

## Scope

Atlas bootstrap is now stable around 11-13s, but user-visible response time still exceeds the 25s operator target.

## Evidence Before Mutation

- `existing-pong`: 27638ms end-to-end, model duration 22253ms, model `gpt-5.5`.
- `fresh-pong`: 30645ms end-to-end, model duration 25338ms, model `gpt-5.5`.
- `existing-board-status`: 37508ms end-to-end, model duration 32474ms.
- Prep trace remains dominated by `core-plugin-tools` around 5.1s and `stream-setup` around 2.5s.
- System prompt report exposes 40 tools and 30290 schema chars, including media tools not required for the measured operator flows.

## Planned Change

Conservatively restrict Atlas tools to the operational core needed for Discord, taskboard, sessions, memory/QMD, and shell/file work. Also set Atlas `thinkingDefault` to `off` to avoid extra reasoning latency for normal operator turns.

## Safety

- Backup `/home/piet/.openclaw/openclaw.json` before edit.
- Run `openclaw doctor` after edit.
- Restart only `openclaw-gateway`.
- Verify `/health`, MC `/api/health`, prep traces, and controlled Atlas pings.

## Rollback

Restore the timestamped `openclaw.json` backup and restart `openclaw-gateway`.
