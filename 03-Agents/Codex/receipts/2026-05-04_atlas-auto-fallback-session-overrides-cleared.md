# Atlas Auto Fallback Session Overrides Cleared

Timestamp: 2026-05-04 09:45 CEST
Owner: Codex

## Scope

User requested:

- Cleanly set up and execute the fix for embedded fallback/session override masking.
- Parallel check of the claim that `openclaw.json` had been changed to runtime `auto` / codex+pi and later reverted.

## Preflight

Gateway before change:

- `/health`: `{"ok":true,"status":"live"}`
- Service: active/running
- PID before stop: `737681`

Runtime config check:

- `/home/piet/.openclaw/openclaw.json`
  - `agents.defaults.agentRuntime`: `{ "id": "codex" }`
  - Agent overrides for `main`, `sre-expert`, `frontend-guru`, `efficiency-auditor`, `james`, `system-bot`, `spark`: each still `{ "id": "codex" }`
- Conclusion: the reported temporary `agentRuntime.id="auto"` change is not currently active. The live state is codex, not auto.

Session-store issue before fix:

- `/home/piet/.openclaw/agents/main/sessions/sessions.json`
- `agent:main:main`
  - `modelProvider=openai`
  - `model=gpt-5.4-mini`
  - `providerOverride=openai`
  - `modelOverride=gpt-5.4-mini`
  - `modelOverrideSource=auto`
- `agent:main:discord:channel:1486480128576983070`
  - `modelProvider=openai`
  - `model=gpt-5.3-codex`
  - `providerOverride=openai`
  - `modelOverride=gpt-5.3-codex`
  - `modelOverrideSource=auto`

No recent active Atlas turn was visible in the last 10 minutes of gateway journal before mutation.

## Backup

- `/home/piet/.openclaw/agents/main/sessions/sessions.json.bak-20260504T074202Z-clear-auto-model-overrides`

## Change

Gateway was stopped before editing the session store to avoid concurrent store writes.

Removed only auto fallback selection fields from the two active Atlas session entries:

- `providerOverride`
- `modelOverride`
- `modelOverrideSource`
- `modelProvider`
- `model`
- `authProfileOverride`
- `authProfileOverrideSource`
- `authProfileOverrideCompactionCount`

Affected entries:

- `agent:main:main`
- `agent:main:discord:channel:1486480128576983070`

No `modelOverrideSource=user` entry was touched.

## Validation

Session store:

- `python3 -m json.tool /home/piet/.openclaw/agents/main/sessions/sessions.json` passed.
- Both affected entries now have no model/provider override fields.

Gateway after change:

- Restarted at `2026-05-04 09:42:29 CEST`
- PID after restart: `751323`
- `/health`: `{"ok":true,"status":"live"}`

Effective Atlas model:

- `openclaw agents list --json` reports `main` / Atlas model `openai/gpt-5.5`.
- `openclaw sessions --agent main --json` now reports both active Atlas sessions effective as:
  - model: `gpt-5.5`
  - modelProvider: `openai`
  - providerOverride: null
  - modelOverride: null
  - agentRuntime: `{ "id": "codex", "source": "agent" }`

Journal after restart:

- No fresh `FailoverError`
- No fresh `codex app-server attempt timed out`
- No fresh `No API key found`
- No fresh `ERR_MODULE_NOT_FOUND`
- No fresh `model fallback decision`

## Next Proof Needed

The next real Discord Atlas turn should be checked for:

- `session.started` with `modelId=gpt-5.5`
- no immediate auto fallback
- no `codex app-server attempt timed out`

If it falls back, that is now a fresh runtime event, not stale session-state masking.

