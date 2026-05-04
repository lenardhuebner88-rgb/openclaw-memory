# 2026-05-04 PI Route All Agents + MiniMax Fallbacks

## Verdict

GREEN for config and gateway health.

OpenClaw text-agent configuration is now on PI route with `openai-codex/*` and explicit alternating MiniMax fallbacks. The native Codex app-server plugin is disabled in config.

## Backup

Primary backup:
- `/home/piet/backups/2026-05-04-pi-route-all-agents-20260504T184051Z`

Contains:
- `openclaw.json`
- `jobs.json`
- `agents-sessions-snapshot`

Script backup:
- `/home/piet/.openclaw/scripts/openclaw-longterm-stability-smoketest.py.bak-20260504T184646Z-pi-route-no-codex-plugin`

## Config Changes

Changed:
- `/home/piet/.openclaw/openclaw.json`
- `/home/piet/.openclaw/scripts/openclaw-longterm-stability-smoketest.py`

### Runtime

`agents.defaults.agentRuntime.id`:
- before: `codex`
- after: `pi`

All `agents.list[*].agentRuntime.id`:
- after: `pi`

`plugins.allow`:
- removed `codex`

`plugins.entries.codex`:
- removed

### Effective Agent Models

| Agent | Primary | Fallbacks |
| --- | --- | --- |
| Atlas/main | `openai-codex/gpt-5.5` | `minimax/MiniMax-M2.7-highspeed`, `openai-codex/gpt-5.3-codex`, `minimax/MiniMax-M2.7`, `openai-codex/gpt-5.4`, `openai-codex/gpt-5.4-mini` |
| Forge/sre-expert | `openai-codex/gpt-5.3-codex` | `minimax/MiniMax-M2.7-highspeed`, `openai-codex/gpt-5.5`, `minimax/MiniMax-M2.7`, `openai-codex/gpt-5.4`, `openai-codex/gpt-5.4-mini` |
| Pixel/frontend-guru | `openai-codex/gpt-5.5` | `minimax/MiniMax-M2.7-highspeed`, `openai-codex/gpt-5.3-codex`, `minimax/MiniMax-M2.7`, `openai-codex/gpt-5.4`, `openai-codex/gpt-5.4-mini` |
| Lens/efficiency-auditor | `minimax/MiniMax-M2.7-highspeed` | `openai-codex/gpt-5.5`, `minimax/MiniMax-M2.7`, `openai-codex/gpt-5.3-codex`, `openai-codex/gpt-5.4`, `openai-codex/gpt-5.4-mini` |
| James | `openai-codex/gpt-5.5` | `minimax/MiniMax-M2.7-highspeed`, `openai-codex/gpt-5.3-codex`, `minimax/MiniMax-M2.7`, `openai-codex/gpt-5.4`, `openai-codex/gpt-5.4-mini` |
| System Bot | `openai-codex/gpt-5.5` | `minimax/MiniMax-M2.7-highspeed`, `openai-codex/gpt-5.4`, `minimax/MiniMax-M2.7`, `openai-codex/gpt-5.4-mini`, `openai-codex/gpt-5.3-codex` |
| Spark | `openai-codex/gpt-5.3-codex` | `minimax/MiniMax-M2.7-highspeed`, `openai-codex/gpt-5.5`, `minimax/MiniMax-M2.7`, `openai-codex/gpt-5.4`, `openai-codex/gpt-5.4-mini` |

## Explicit Deviation

Requested Spark model:
- `openai-codex/gpt-5.3-codex-spark`

OpenClaw 2026.5.3-1 rejected this model during `openclaw config validate`:
- `Unknown model: openai-codex/gpt-5.3-codex-spark`
- validator says the Spark model is no longer exposed by OpenAI/Codex catalogs.

To keep production config valid, Spark was set to:
- `openai-codex/gpt-5.3-codex`

## Validation

Passed:
- `python3 -m json.tool /home/piet/.openclaw/openclaw.json`
- `openclaw config validate`
- `openclaw models status`
- `openclaw agents list --json`
- `openclaw plugins list --json`
- `python3 -m py_compile /home/piet/.openclaw/scripts/openclaw-longterm-stability-smoketest.py`
- `curl http://127.0.0.1:18789/health`

Gateway:
- restarted at `Mon 2026-05-04 20:46:04 CEST`
- health: `{"ok":true,"status":"live"}`

Plugin status after config:
- `discord`: loaded
- `openai`: loaded, includes provider `openai-codex`
- `minimax`: loaded, includes provider `minimax`
- `codex`: disabled

Guard:
- `rotationNeeded=0`
- `staleRunning=0`
- `loadErrors=0`

## Notes

`openclaw sessions --all-agents --active 180 --json` still shows older explicit/subagent session records with `modelProvider=openai`. Those are session-store history entries, not the new effective config. New sessions use the configured PI route. Use `/new`, `/reset`, or scoped session rotation if you want all old session bindings removed.

Post-restart journal had one Discord `/users/@me` fetch-timeout likely related to startup/event-loop delay, but no `codex app-server attempt timed out`, `unknown model`, or provider-not-found lines in the checked window.

## Rollback

```bash
cp /home/piet/backups/2026-05-04-pi-route-all-agents-20260504T184051Z/openclaw.json /home/piet/.openclaw/openclaw.json
cp /home/piet/backups/2026-05-04-pi-route-all-agents-20260504T184051Z/jobs.json /home/piet/.openclaw/cron/jobs.json
systemctl --user restart openclaw-gateway.service
curl -fsS http://127.0.0.1:18789/health
```

## Next Step

Run one bounded canary per active agent only when that agent is idle:
1. Atlas/main
2. Forge/sre-expert
3. Lens/efficiency-auditor
4. Pixel/frontend-guru
5. Spark

Do not run Atlas canary while the operator is actively working with Atlas.
