---
title: OpenClaw model hotpath migration receipt
date: 2026-05-03
mutation_level: config_change_with_gateway_restart
for_atlas:
  status: info_only
  affected_agents:
    - main
    - sre-expert
    - frontend-guru
    - efficiency-auditor
    - james
    - system-bot
    - spark
  affected_files:
    - /home/piet/.openclaw/openclaw.json
  recommended_next_action: "Use Mission Control/OpenClaw read-only diagnostics for follow-up; do not route Atlas monitoring through sessions_send. MiniMax remains configured but is not in active agent hotpaths."
  risk: "Old sessions may still show prior provider metadata; new direct smoke tests used openai provider successfully."
  evidence_files:
    - /home/piet/.openclaw/openclaw.json.bak-20260503T204532Z
---

# OpenClaw Model Hotpath Migration Receipt

## Scope

Piet approved implementing the model-routing cleanup after MiniMax M2.7 smoke testing showed:

- MiniMax Token Plan API route itself is healthy.
- OpenClaw Codex agent runtime cannot currently use `minimax/...` in active agent primary/fallback chains without `Model provider minimax not found`.

## Changed file

- `/home/piet/.openclaw/openclaw.json`

## Backup

- `/home/piet/.openclaw/openclaw.json.bak-20260503T204532Z`

## Intended and applied changes

- Migrated active default and per-agent chains from `openai-codex/gpt-*` to `openai/gpt-*`.
- Removed MiniMax from active agent primary/fallback hotpaths.
- Kept MiniMax provider/model definitions available in `agents.defaults.models` and `models.providers` for later isolated testing.
- Removed obsolete `openai-codex/gpt-*` model definitions from `agents.defaults.models` to avoid stale allowed refs.
- Ensured agent runtime shape remains `{ "id": "codex", "fallback": "pi" }`.

## Resulting active chains

| Agent | Primary | Fallbacks |
|---|---|---|
| defaults | `openai/gpt-5.4-mini` | `openai/gpt-5.5`, `openai/gpt-5.4`, `openai/gpt-5.3-codex` |
| Atlas (`main`) | `openai/gpt-5.5` | `openai/gpt-5.4-mini`, `openai/gpt-5.4`, `openai/gpt-5.3-codex` |
| Forge (`sre-expert`) | `openai/gpt-5.3-codex` | `openai/gpt-5.5`, `openai/gpt-5.4-mini`, `openai/gpt-5.4` |
| Pixel (`frontend-guru`) | `openai/gpt-5.5` | `openai/gpt-5.3-codex`, `openai/gpt-5.4`, `openai/gpt-5.4-mini` |
| Lens (`efficiency-auditor`) | `openai/gpt-5.4-mini` | `openai/gpt-5.5`, `openai/gpt-5.4`, `openai/gpt-5.3-codex` |
| James (`james`) | `openai/gpt-5.4-mini` | `openai/gpt-5.5`, `openai/gpt-5.4`, `openai/gpt-5.3-codex` |
| System Bot (`system-bot`) | `openai/gpt-5.4-mini` | `openai/gpt-5.4`, `openai/gpt-5.5`, `openai/gpt-5.3-codex` |
| Spark (`spark`) | `openai/gpt-5.5` | `openai/gpt-5.4-mini`, `openai/gpt-5.3-codex`, `openai/gpt-5.4` |

## Verification

Direct JSON parse after write:

- JSON parse: OK
- `openai-codex/gpt-`: 0
- `openai/gpt-`: 44
- `minimax/MiniMax`: 2
- MiniMax in active chains: false

Gateway restart:

- Command: `systemctl --user restart openclaw-gateway.service`
- New MainPID observed: `276837`
- `/health`: `{"ok":true,"status":"live"}` after ~9s
- Gateway journal: `http server listening`, then `[gateway] ready`

Effective config / model status:

- Mission Control effective config shows defaults and all 7 agents on `openai/gpt-*` active chains.
- OpenClaw model status shows default `openai/gpt-5.4-mini` and fallbacks `openai/gpt-5.5`, `openai/gpt-5.4`, `openai/gpt-5.3-codex`.
- Allowed refs still include MiniMax models for later isolated testing.

Agent smoke tests:

- Atlas direct smoke:
  - Reply: `OPENCLAW_MODEL_MIGRATION_OK`
  - Provider/model: `openai` / `gpt-5.5`
  - Fallback used: false
  - Aborted: false
- System Bot direct smoke:
  - Reply: `SYSTEM_BOT_MODEL_MIGRATION_OK`
  - Provider/model: `openai` / `gpt-5.4-mini`
  - Fallback used: false
  - Aborted: false

Known residuals:

- Recent model-runtime-failures endpoint still reports pre-change events inside its 30-minute window, including MiniMax provider-not-found from the earlier smoke test and Codex timeout events before the migration.
- One post-restart Discord `/users/@me` fetch timeout appeared during startup; recent OpenClaw read-only logs returned no warning/error entries afterward.
- Existing old sessions may retain old provider metadata until refreshed; new smoke sessions used `modelProvider=openai`.

## Rollback

Restore backup and restart gateway:

```bash
cp /home/piet/.openclaw/openclaw.json.bak-20260503T204532Z /home/piet/.openclaw/openclaw.json
systemctl --user restart openclaw-gateway.service
```
