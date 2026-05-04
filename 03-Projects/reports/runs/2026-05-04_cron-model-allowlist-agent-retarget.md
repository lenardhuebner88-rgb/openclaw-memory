# OpenClaw Cron Model-Allowlist and Agent Retarget

Date: 2026-05-04
Owner: Codex
Source plan: `/home/piet/vault/03-Agents/Hermes/plans/openclaw-cron-model-allowlist-and-agent-retarget-plan-2026-05-04.md`

## Verdict

YELLOW overall.

The primary cron allowlist problem is fixed and active:

- `agents.defaults.models` now includes the explicit `openai-codex/*` model refs used by enabled cron jobs.
- Enabled cron jobs no longer have `payload.model` refs missing from `agents.defaults.models`.
- `memory-sqlite-vacuum-weekly` no longer targets the non-existent `worker` agent.
- OpenClaw Gateway restarted successfully and is live.

Remaining separate issue:

- `mc-pending-pickup-smoke-hourly` no longer fails the model allowlist gate, but the manual smoke ended with `Message failed` because the run produced `SMOKE_OK` and then attempted a message send without a target. Gateway log: `Action send requires a target`. This is a delivery/job-prompt issue, not the cron model allowlist issue.

## Changes

### `/home/piet/.openclaw/openclaw.json`

Added these keys under `agents.defaults.models`:

```json
{
  "openai-codex/gpt-5.4-mini": {},
  "openai-codex/gpt-5.4": {},
  "openai-codex/gpt-5.3-codex": {},
  "openai-codex/gpt-5.5": {}
}
```

### `/home/piet/.openclaw/cron/jobs.json`

Retargeted only:

```json
{
  "id": "af681204-978f-46cf-b793-a50376580291",
  "name": "memory-sqlite-vacuum-weekly",
  "agentId": "system-bot",
  "sessionKey": "agent:system-bot:cron:memory-sqlite-vacuum-weekly:run"
}
```

Role-specific jobs were intentionally left on their existing agents.

## Backups

- `/home/piet/.openclaw/openclaw.json.bak-20260504T192023Z-cron-model-allowlist`
- `/home/piet/.openclaw/cron/jobs.json.bak-20260504T192023Z-worker-retarget`
- `/home/piet/.openclaw/cron/jobs.json.bak-20260504T192553Z-worker-retarget-correction`

## Validation

### Config and JSON

- `python3 -m json.tool /home/piet/.openclaw/openclaw.json` passed.
- `python3 -m json.tool /home/piet/.openclaw/cron/jobs.json` passed.
- `/home/piet/bin/openclaw config validate` passed: `Config valid: ~/.openclaw/openclaw.json`.
- Enabled cron jobs with `payload.model` missing from `agents.defaults.models`: `0`.
- Enabled cron jobs targeting `agentId=worker`: `0`.

### Gateway

Restarted `openclaw-gateway.service`.

Post-check:

- Active since: `Mon 2026-05-04 21:26:16 CEST`
- `NRestarts=0`
- `/health`: `{"ok":true,"status":"live"}`
- ExecStartPre hooks all exited `status=0/SUCCESS`.
- Startup log reached `[gateway] ready`.

Observed non-blocking startup noise:

- Discord `/users/@me` fetch timeout during startup.
- One unresolved Discord channel id.
- These are not the cron model allowlist failure.

### Focused Cron Smokes

#### `learnings-to-tasks-001`

Manual run:

- Run timestamp: `2026-05-04T19:24:09.730Z`
- Status: `ok`
- Session key: `agent:system-bot:cron:learnings-to-tasks-001:run:36b43a77-2cef-41cf-ad45-897196ba5bf9`
- Model/provider: `gpt-5.4-mini` / `openai-codex`
- Duration: `51622ms`
- Result summary: `STOPPED.`

Conclusion: allowlist failure cleared.

#### `mc-pending-pickup-smoke-hourly`

Manual run:

- Run timestamp: `2026-05-04T19:24:49.103Z`
- Status: `error`
- Error: `Message failed`
- Summary: `SMOKE_OK`
- Session key: `agent:system-bot:cron:0f9d0f2e-9839-4a14-ad18-cb75ff7f49c7:run:f92f6e84-a89f-43e7-b666-2caab415f7ca`
- Model/provider: `gpt-5.4-mini` / `openai-codex`
- Duration: `15749ms`
- Delivery: `mode=none` job, but run attempted a send without target.
- Gateway evidence: `[tools] message failed: Action send requires a target. raw_params={"action":"send","message":"SMOKE_OK"}`

Conclusion: allowlist failure cleared; remaining failure is separate delivery/prompt behavior.

## Current Follow-Up

Primary next step:

Fix `mc-pending-pickup-smoke-hourly` so the agent does not call the message send tool when `delivery.mode` is `none`. The narrowest likely change is to adjust the cron payload prompt from "reply with exactly: SMOKE_OK" to a no-send terminal-result wording, or set an explicit delivery target if the job is intended to report externally.

Do not retarget broader cron ownership unless a separate live failure proves it necessary.

## Rollback

Rollback both config surfaces:

```bash
cp /home/piet/.openclaw/openclaw.json.bak-20260504T192023Z-cron-model-allowlist /home/piet/.openclaw/openclaw.json
cp /home/piet/.openclaw/cron/jobs.json.bak-20260504T192553Z-worker-retarget-correction /home/piet/.openclaw/cron/jobs.json
python3 -m json.tool /home/piet/.openclaw/openclaw.json >/dev/null
python3 -m json.tool /home/piet/.openclaw/cron/jobs.json >/dev/null
/home/piet/bin/openclaw config validate
systemctl --user restart openclaw-gateway.service
curl -fsS --max-time 5 http://127.0.0.1:18789/health; echo
```

Note: this rollback would reintroduce the cron allowlist failure and the `worker` retarget drift.

## Follow-up: `mc-pending-pickup-smoke-hourly` no-send fix

Date: 2026-05-04

### Problem

After the model allowlist fix, `mc-pending-pickup-smoke-hourly` reached the model/runtime path but failed with:

```text
Message failed
Action send requires a target
```

The job had `delivery.mode=none`, but its payload said `reply with exactly: SMOKE_OK`. In one run the agent interpreted that as a message/send tool action even though the job had no target.

### Change

Modified only `/home/piet/.openclaw/cron/jobs.json` for job `0f9d0f2e-9839-4a14-ad18-cb75ff7f49c7` / `mc-pending-pickup-smoke-hourly`:

- Removed `delivery.channel: "last"`; final delivery block is now only:

```json
{
  "mode": "none"
}
```

- Reworded payload message from `reply with exactly: SMOKE_OK` to final-text-only wording:

```text
RUN: /home/piet/.openclaw/scripts/mc-pending-pickup-smoke.sh
After the command completes:
- If stdout contains SMOKE_OK, return final assistant text exactly: SMOKE_OK
- Do not call Discord, message, send, reply, notify, report, or any delivery tool. This cron has delivery.mode=none; the final assistant text is stored only in cron run history.
- If stdout/stderr contains ERROR or the command fails, return a short final assistant text with the relevant stdout/stderr summary.
STOP.
```

### Backup

- `/home/piet/.openclaw/cron/jobs.json.bak-20260504T192938Z-mc-pending-pickup-no-send`

### Validation

- `python3 -m json.tool /home/piet/.openclaw/cron/jobs.json` passed.
- `/home/piet/bin/openclaw config validate` passed.
- Enabled cron jobs with `payload.model` missing from `agents.defaults.models`: `0`.
- Enabled cron jobs targeting `agentId=worker`: `0`.
- Gateway restarted and is live:
  - Active since: `Mon 2026-05-04 21:30:08 CEST`
  - `/health`: `{"ok":true,"status":"live"}`

### Smoke Result

Manual run:

- Run id: `manual:0f9d0f2e-9839-4a14-ad18-cb75ff7f49c7:1777923037737:1`
- Cron run timestamp: `2026-05-04T19:31:30.868Z`
- Status: `ok`
- Summary: `SMOKE_OK`
- Delivery status: `not-requested`
- Session key: `agent:system-bot:cron:0f9d0f2e-9839-4a14-ad18-cb75ff7f49c7:run:db668fea-ccd1-4126-a6b1-5a9a4d56731b`
- Model/provider: `gpt-5.4-mini` / `openai-codex`
- Duration: `53124ms`

Gateway log check after the fix showed no new matches for:

- `Action send requires a target`
- `message failed`
- `payload.model`
- `allowlist`
- provider-not-found
- Failover/timeout signatures

### Verdict

GREEN for this follow-up. The remaining `mc-pending-pickup-smoke-hourly` issue is fixed and validated.
