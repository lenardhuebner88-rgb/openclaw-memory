# OpenClaw Embedded Fallback RCA

Timestamp: 2026-05-04 09:45 CEST
Owner: Codex
Scope: read-only RCA for the `openclaw agent` embedded fallback/auth failure and whether it is part of the Atlas/Forge timeout problem.

## Verdict

The `openclaw agent --agent main` smoke failure is not the original 300s Codex app-server timeout root cause.

It is, however, part of the current stabilization problem because OpenClaw persists successful fallback candidates as session-level `modelOverrideSource: auto`. Existing active Atlas sessions can therefore keep using old fallback models even after `openclaw.json` is changed to `openai/gpt-5.5`.

## Live Evidence

OpenClaw status:

- Runtime: `OpenClaw 2026.5.3-beta.4 (c6c64e2)`
- Gateway health: `{"ok":true,"status":"live"}`
- Agent list reports Atlas/main model: `openai/gpt-5.5`

Auth status:

- `openclaw models status` shows OpenAI API-key auth is missing for provider `openai`.
- The same status shows `openai-codex` OAuth is valid and has remaining quota.
- Main agent auth store contains `openai-codex:lenardhuebner88@gmail.com`.

CLI smoke failure:

- Command attempted: `openclaw agent --agent main --message 'SMOKE TEST after Atlas routing change. Reply exactly: ATLAS_GPT55_OK' --json --timeout 180`
- Result: gateway agent failed, then CLI/local embedded fallback failed on missing `openai` API-key auth.
- Gateway/journal error: `No API key found for provider "openai"`.
- Important: the request did not test the normal Discord OAuth hotpath.

Session-store evidence:

`/home/piet/.openclaw/agents/main/sessions/sessions.json`

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

Post-switch evidence:

- After Atlas config was changed to `openai/gpt-5.5`, `openclaw sessions --agent main --json` still reported:
  - Direct main session model: `gpt-5.4-mini`
  - Discord Atlas session model: `gpt-5.3-codex`
- The active Discord session completed fresh post-switch turns on `gpt-5.3-codex`, not `gpt-5.5`.

Bundle/code evidence:

- `agent-runner.runtime-BaC5oTwh.js` defines fallback selection state fields:
  - `providerOverride`
  - `modelOverride`
  - `modelOverrideSource`
  - auth override fields
- `buildFallbackSelectionState()` stores fallback selections with `modelOverrideSource: "auto"`.
- `persistFallbackCandidateSelection()` writes the fallback candidate to the active session entry unless the override source is user-owned.
- `session-By1K9w8H.js` shows fresh cron sessions preserve non-auto model overrides but should not preserve auto overrides.

## Root Cause

There are two separate but interacting mechanisms:

1. Native Codex app-server timeout/stall:
   - This is the original Atlas/Forge symptom: partial assistant text, no tool execution required, then `codex app-server attempt timed out` after about 300s.
   - This occurred on Discord and heartbeat lanes with high cached context and overlap.

2. Auto fallback persistence:
   - Once a fallback candidate succeeds, OpenClaw persists that candidate into `sessions.json` as `modelOverrideSource: auto`.
   - Existing sessions then continue using the fallback model instead of the newly configured agent primary.
   - This explains why Atlas can be configured as `openai/gpt-5.5` while active sessions still run `gpt-5.3-codex` or `gpt-5.4-mini`.

The CLI embedded fallback auth error is a third surface:

- It appears when `openclaw agent` uses a direct/main session path and falls into a local embedded/provider path that expects provider `openai` API-key auth.
- Your production OpenAI lane is ChatGPT/Codex OAuth through `openai-codex`, not raw OpenAI API key.
- Therefore CLI smoke tests using `openclaw agent` are currently unreliable for validating Atlas Discord OAuth routing unless the session/model/auth path is explicitly controlled.

## Is This Part Of Our Problem?

Yes, but not as the primary timeout root cause.

It is part of the operational problem in three ways:

1. It invalidates naive smoke tests.
   - `openclaw agent --agent main` can fail on local/openai API-key auth even while Discord/OAuth Gateway operation remains viable.

2. It masks routing changes.
   - Changing `openclaw.json` to `openai/gpt-5.5` does not force existing active sessions to use `gpt-5.5`.
   - Active Atlas Discord is currently pinned by auto override to `gpt-5.3-codex`.

3. It can preserve a recovery state as if it were the desired steady state.
   - Fallback success is useful for recovery, but persisting it means the system may never return to primary without session reset/override cleanup.

## Recommended Next Step

Do not run more `openclaw agent` CLI smokes as proof for Atlas primary.

Next safe remediation should target session state, not model config:

1. Backup `/home/piet/.openclaw/agents/main/sessions/sessions.json`.
2. Clear only auto fallback override fields for active Atlas sessions:
   - `providerOverride`
   - `modelOverride`
   - `modelOverrideSource`
   - `modelProvider`
   - `model`
3. Keep user-owned overrides untouched.
4. Restart Gateway.
5. Validate via real Discord turn:
   - next `session.started` for `agent:main:discord:channel:1486480128576983070` should show `modelId=gpt-5.5`.
   - If it falls back, fallback event should be explicit and measured.

Alternative lower-risk path:

- Force a new Atlas Discord session/rotation instead of editing session store fields.
- This avoids direct JSON mutation but may lose some immediate conversation continuity.

## Stop Conditions

Stop before mutation if:

- session store format changes,
- active session has `modelOverrideSource=user`,
- Gateway is not healthy,
- Atlas is mid-turn.

