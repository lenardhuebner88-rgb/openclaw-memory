# Forge Scoped Stale Session Rotation - 2026-05-04

Scope: `agent:sre-expert:discord:channel:1486480146524410028`

Actions:
- Ran scoped dry-run first and verified it reported exactly the Forge session key.
- Ran scoped live cleanup with `--only-session-key`.
- No Gateway restart was attempted by the guard.
- No `.jsonl` history was deleted.
- No `openclaw.json` change was made.

Result:
- Live rotated: yes
- Removed sessionId: `d62fb49b-74ec-49f7-a8a5-64db96bee16e`
- Removed sessionKey: `agent:sre-expert:discord:channel:1486480146524410028`
- Backup path: `/home/piet/.openclaw/agents/sre-expert/sessions/sessions.json.bak-20260504T103538Z-openclaw-discord-session-stability-guard`

Postcheck:
- `sre-expert/sessions.json` is JSON valid.
- Target Forge session key is removed from `sre-expert/sessions.json`.
- Atlas Discord session key remains present in `main/sessions.json`.
- Atlas session has no `modelOverride` or `providerOverride`.
- Gateway health returned OK.
- Gateway `ActiveEnterTimestamp` remained `Mon 2026-05-04 12:09:24 CEST`.

