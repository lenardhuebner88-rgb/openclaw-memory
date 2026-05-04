# OpenClaw All-Agent Discord Session Stability Guard Receipt

Date: 2026-05-04
Mode used on live system: dry-run only
Script: `/home/piet/.openclaw/scripts/openclaw-discord-session-stability-guard.py`

## Scope

Implemented an all-agent Discord session stability guard that scans:

`/home/piet/.openclaw/agents/*/sessions/sessions.json`

It checks only session keys matching:

`agent:<agentId>:discord:*`

The existing Atlas-specific guard was not modified:

`/home/piet/.openclaw/scripts/atlas-discord-stability-guard.py`

## Guard Behavior

Default mode is dry-run. Live mutation requires explicit `--live`.

Live mode, if explicitly run later, removes only affected Discord session keys from `sessions.json`. Before each changed file is written, the script creates a sibling backup:

`sessions.json.bak-<UTC>-openclaw-discord-session-stability-guard`

Writes are atomic and JSON-validated. The script does not restart the gateway and does not delete `.jsonl` session history.

If a rotation candidate is an active session younger than 10 minutes, live mode aborts with:

`abortReason=active-or-recent-session`

## Report Fields

Each checked session reports:

- `agentId`
- `sessionKey`
- `sessionId`
- `status`
- `updatedAt`
- `updatedAtIso`
- `ageSeconds`
- `model`
- `modelOverride`
- `modelOverrideSource`
- `providerOverride`
- `providerOverrideSource`
- `cacheRead`
- `totalTokens`
- `rotationNeeded`
- `reasons`

The report avoids dumping arbitrary session payload fields.

## Rotation Reasons

Implemented rotation reasons:

- `modelOverrideSource=auto`
- `modelOverride-set`
- `providerOverride-set`
- `stale-running><threshold>m`
- `stale-running-before-gateway-restart`
- `status=timeout-with-overrides`
- `status=failed-with-overrides`
- `cacheRead>120000`
- `totalTokens>140000`
- malformed/non-object entry
- session key/store agent mismatch

## Validation

Validation commands run:

- `python3 -m py_compile /home/piet/.openclaw/scripts/openclaw-discord-session-stability-guard.py /home/piet/.openclaw/scripts/tests/test_openclaw_discord_session_stability_guard.py`
- `python3 /home/piet/.openclaw/scripts/tests/test_openclaw_discord_session_stability_guard.py`
- `/home/piet/.openclaw/scripts/openclaw-discord-session-stability-guard.py`

Fixture coverage:

- Atlas auto override is detected and removed in temp live fixture.
- `sre-expert` stale running without override is detected.
- Young running session is not live-removed; live aborts with `active-or-recent-session`.
- Non-Discord session keys remain untouched.
- Cache and total-token thresholds are rotation reasons.

Test result: 4 tests passed.

## Live Dry-Run Result

Dry-run exit code: 2

No productive session mutation was performed.

Gateway restart was not attempted.

`.jsonl` history deleted: false

Gateway active since: 2026-05-04T10:09:24Z

Scanned session stores: 10

Discord sessions found: 2

Rotation-needed sessions: 2

Affected sessions:

- `main` / `agent:main:discord:channel:1486480128576983070`
  - status: `running`
  - updatedAt: 2026-05-04T10:24:05Z
  - model: `gpt-5.5`
  - reasons: `cacheRead>120000`
  - note: active/recent; explicit live mode would abort because it is younger than 10 minutes.

- `sre-expert` / `agent:sre-expert:discord:channel:1486480146524410028`
  - status: `running`
  - updatedAt: 2026-05-04T06:55:53Z
  - model: `gpt-5.3-codex`
  - reasons: `stale-running>30m`, `stale-running-before-gateway-restart`

Only stale-running:

- `sre-expert` / `agent:sre-expert:discord:channel:1486480146524410028`

Auto-fallback pins:

- none detected in live dry-run

## Mutation Statement

No live mode was run. No `sessions.json` file was changed on the live system. No `.jsonl` file was deleted. The only persistent write for this task is this receipt file.
