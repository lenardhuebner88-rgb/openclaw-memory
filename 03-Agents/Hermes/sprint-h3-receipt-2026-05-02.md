---
title: Hermes Sprint H-3 Receipt
status: passed
created: 2026-05-02
owner: Piet
scope: hermes-openclaw-readonly
---

# Hermes Sprint H-3 Receipt

Datum: 2026-05-02

## Ergebnis

H-3 ist umgesetzt: Hermes hat jetzt einen dedizierten `openclaw-readonly` MCP und kann OpenClaw-Lagebilder im Discord MCP-first bearbeiten.

## Geaenderte Artefakte

- `/home/piet/.hermes/mcp/openclaw_readonly_server.py`
- `/home/piet/.hermes/config.yaml`
- `/home/piet/.hermes/skills/devops/openclaw-operator/SKILL.md`
- `/home/piet/vault/03-Agents/Hermes/sprint-h3-discord-live-openclaw-readonly-2026-05-02.md`
- `/home/piet/vault/03-Agents/Hermes/playbooks/openclaw-readonly-mcp.md`
- `/home/piet/vault/03-Agents/Hermes/playbooks/openclaw-gateway-down.md`
- `/home/piet/vault/03-Agents/Hermes/break-glass-mode-split-2026-05-02.md`
- `/home/piet/vault/03-Agents/Hermes/mission-control-degraded-rca-2026-05-02.md`
- `/home/piet/vault/03-Agents/Hermes/discord-live-testpack-h3-2026-05-02.md`
- `/home/piet/vault/03-Agents/Hermes/system-overview.md`
- `/home/piet/vault/03-Agents/Hermes/hermes-api-mcp-integration-plan-2026-05-02.md`

## Backup

- Hermes config backup: `/home/piet/.hermes/config.yaml.bak-20260502-224524`

## Validation

- `py_compile /home/piet/.hermes/mcp/openclaw_readonly_server.py`: PASS.
- `hermes mcp test openclaw-readonly`: PASS, 6 tools discovered.
- `hermes mcp list`: PASS, `qmd-vault`, `mc-readonly`, `openclaw-readonly` enabled.
- `systemctl --user restart hermes-gateway.service`: PASS.
- `systemctl --user status hermes-gateway.service`: active, MCP subprocesses for `mc-readonly` and `openclaw-readonly`.
- E2E OpenClaw Lagebild: PASS, used `openclaw-readonly`, Gateway HTTP 200 `ok=true/status=live`, Gateway and Discord bot active.
- E2E Mission Control degraded: PASS, used `mc-readonly`, live state currently OK, no mutation.
- E2E Break-Glass simulation: PASS after runbook sharpening, named `openclaw-gateway-down.md`, required approval, no command executed.
- `hermes fallback list`: PASS, primary `MiniMax-M2.7` via MiniMax, fallback `gpt-5.5` via `openai-codex`.
- `hermes -z "Welches Modell bist du?"`: PASS, `MiniMax-M2.7, MiniMax Provider`.
- `hermes mcp test qmd-vault`: PASS, 6 tools discovered.

## Observations

- Discord slash-command sync hit Discord HTTP 429 after Hermes Gateway restart. Hermes Gateway stayed active and Discord should retry automatically. Treat this as rate-limit noise unless commands remain missing after the retry window.
- One QMD E2E prompt failed transiently with MCP connection retries, but direct `hermes mcp test qmd-vault` passed immediately after.
- One model-config E2E with `file` tool timed out; direct fallback/model checks passed.
- Discord live test exposed a Node/PATH issue in `openclaw_model_status`: Hermes Gateway did not include `/home/piet/bin`, so OpenClaw resolved through npm-global Node 20 instead of the local Node 22 wrapper.
- Fixed in `openclaw_readonly_server.py` by calling `/home/piet/bin/openclaw` directly.
- `openclaw_model_status` now returns a redacted summary only; credential values, labels, and synthetic credentials are omitted.

## Follow-up Validation 23:00

- `py_compile /home/piet/.hermes/mcp/openclaw_readonly_server.py`: PASS.
- `hermes mcp test openclaw-readonly`: PASS, 6 tools discovered.
- `systemctl --user restart hermes-gateway.service`: PASS.
- Hermes E2E model status: PASS.
- Reported model state: default `minimax/MiniMax-M2.7`; fallbacks `minimax/MiniMax-M2.7-highspeed`, `openai-codex/gpt-5.5`, `openrouter/auto`.
- Reported OAuth summary: `openai-codex=ok`, `openrouter=static`, `anthropic=expired`, `claude-cli=expiring`.

## Follow-up Anthropic Removal 23:05

- Anthropic/Claude provider, aliases, allowed models, OAuth/API profiles, and `agentRuntime.id=claude-cli` removed from active OpenClaw config stores.
- `agentRuntime.id` set to `codex`.
- Backup: `/home/piet/backups/anthropic-removal-20260502-230335`.
- Receipt: `/home/piet/vault/03-Agents/Hermes/anthropic-removal-2026-05-02.md`.
- Validation: JSON PASS, `openclaw config validate` PASS, Hermes `openclaw-readonly` model status PASS.
- Remaining provider OAuth summary: `openai-codex=ok`; `openrouter=static`; `google=static`.

## Follow-up Apply Restart 23:09

- Pre-check: Mission Control `ok`, Board `All clear`, `openTasks=0`, `staleOpenTasks=0`.
- Restarted `openclaw-gateway.service`.
- Post-check: OpenClaw Health HTTP 200, `ok=true`, `status=live`.
- `openclaw models status --json`: PASS, no Anthropic/Claude provider or OAuth entries.
- Services active: `openclaw-gateway.service`, `openclaw-discord-bot.service`, `mission-control.service`, `hermes-gateway.service`, `qmd-mcp-http.service`.
- Hermes MCP tests: `openclaw-readonly`, `mc-readonly`, `qmd-vault` PASS.
- OpenClaw Gateway warnings/errors after restart: none.

## Follow-up Hermes Hardening Gate 1/2 23:21

- Backup: `/home/piet/backups/hermes-hardening-20260502-231833`.
- Set `privacy.redact_pii=true` in `/home/piet/.hermes/config.yaml`.
- Added `/home/piet/.config/systemd/user/hermes-gateway.service.d/10-discord-sync-policy.conf` with `DISCORD_COMMAND_SYNC_POLICY=off`.
- Added `/home/piet/.config/systemd/user/hermes-gateway.service.d/20-hardening-stage1.conf`.
- Active stage-1 hardening: `NoNewPrivileges=yes`, `PrivateTmp=yes`, `MemoryHigh=1536M`, `MemoryMax=2G`.
- Not yet enabled: `ProtectSystem`, `ProtectHome`, `ReadWritePaths`.
- `systemd-analyze --user verify hermes-gateway.service`: PASS for Hermes; unrelated existing warning in `vault-sync.service`.
- `systemctl --user restart hermes-gateway.service`: PASS.
- Post-check: Hermes active, OpenClaw health HTTP 200, Mission Control `ok`, `openTasks=0`, `staleOpenTasks=0`.
- MCP tests: `openclaw-readonly`, `mc-readonly`, `qmd-vault` PASS.
- Vault stale-doc override boxes added to shared/OpenClaw/Forge/Roadmap files.

## Follow-up Discord Sync Throttle 23:24

- Backed up `/home/piet/.hermes/hermes-agent/gateway/platforms/discord.py` to `/home/piet/backups/hermes-hardening-20260502-231833/discord.py.pre-sync-throttle`.
- Added durable Discord slash-command sync state/hash logic in `gateway/platforms/discord.py`.
- Behavior when `DISCORD_COMMAND_SYNC_POLICY=safe`: skip Discord command sync if desired command hash is unchanged and last successful sync is fresher than `DISCORD_COMMAND_SYNC_MIN_INTERVAL_SECONDS` (default 3600s), unless `DISCORD_COMMAND_SYNC_FORCE=1`.
- Current active policy remains `DISCORD_COMMAND_SYNC_POLICY=off`, so no Discord command write calls are made on Hermes startup.
- Validation: `py_compile` PASS.
- Tests: `tests/gateway/test_discord_connect.py` and `tests/gateway/test_reload_skills_discord_resync.py` PASS, 17 passed.
- Restarted `hermes-gateway.service`: PASS.
- Post-check: Hermes active, OpenClaw HTTP 200, Mission Control `ok`, MCP tests `openclaw-readonly`, `mc-readonly`, `qmd-vault` PASS.

## Current Operating Recommendation

For Hermes in Discord:

1. Use `openclaw-operator` skill.
2. For MC questions use `mc-readonly`.
3. For OpenClaw/Gateway/Discord bot questions use `openclaw-readonly`.
4. For Vault/KB context use known runbook path first, then focused `qmd-vault`.
5. Restarts/config edits remain Break-Glass only with live evidence and Piet approval.

## Next Suggested Sprint

H-4 should focus on Discord command UX and reliability:

- verify slash-command sync after Discord 429 retry window;
- test `/model`, model fallback, and MCP prompts from real Discord;
- decide whether Hermes needs separate normal/break-glass profiles;
- add a compact "Hermes daily operator check" prompt that does not mutate anything.
