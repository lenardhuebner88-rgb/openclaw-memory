# Forge Scoped Timeout Pin Rotation - 2026-05-04

Time: `2026-05-04T12:04Z`

Scope:
- Target sessionKey: `agent:sre-expert:discord:channel:1486480146524410028`
- Target agent: `sre-expert`
- Operation: scoped session-store rotation via `/home/piet/.openclaw/scripts/openclaw-discord-session-stability-guard.py`

Reason:
- Post-restart Forge/sre-expert timeout/fallback chain at `2026-05-04 13:28:22 CEST`.
- Fallback succeeded at `2026-05-04 13:30:25 CEST`, but the Discord session remained `running` with an auto model/provider override pin.
- Scoped guard dry-run reported exactly this key with:
  - `stale-running>30m`
  - `modelOverrideSource=auto`
  - `modelOverride-set`
  - `providerOverride-set`
  - `recentActive=false`
  - no load errors

Removed:
- sessionId: `339d5615-ed69-4624-8f9d-5c85199e8a92`
- sessionKey: `agent:sre-expert:discord:channel:1486480146524410028`

Backup:
- `/home/piet/.openclaw/agents/sre-expert/sessions/sessions.json.bak-20260504T120437Z-openclaw-discord-session-stability-guard`

Safety:
- No Gateway restart.
- No Mission Control restart.
- No `.jsonl` history deletion.
- No `openclaw.json`, `jobs.json`, cron, script, or Mission Control data mutation.
- JSONL history still present: `/home/piet/.openclaw/agents/sre-expert/sessions/339d5615-ed69-4624-8f9d-5c85199e8a92.jsonl`

Postcheck:
- Forge `sessions.json`: JSON valid.
- Target Forge sessionKey: absent.
- Atlas sessionKey `agent:main:discord:channel:1486480128576983070`: still present.
- Atlas overrides: none.
- Atlas cacheRead/totalTokens at postcheck: `77696 / 78540`.
- Gateway health: `{"ok":true,"status":"live"}`
- Gateway ActiveEnterTimestamp: `Mon 2026-05-04 12:09:24 CEST`
- Gateway NRestarts: `0`
- All-agent guard dry-run:
  - `ok=true`
  - `rotationNeeded=0`
  - `staleRunning=0`
  - `loadErrors=0`
  - `wouldRotateSessionKeys=[]`

Rollback:
- Restore the backup to `/home/piet/.openclaw/agents/sre-expert/sessions/sessions.json` if the rotated Forge session must be reattached.
- Do not restore while another live Forge Discord session is active without a fresh scoped precheck.
