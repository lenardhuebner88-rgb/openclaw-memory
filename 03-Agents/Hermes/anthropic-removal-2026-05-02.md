# Anthropic/Claude Removal

Datum: 2026-05-02T23:05:57+02:00

## Ziel

Anthropic/Claude soll nicht mehr als aktiver Provider, OAuth-Profil, API-Key-Profil, Alias oder Runtime in OpenClaw/Hermes auftauchen.

## Nicht Entfernt

Diese Strings bleiben absichtlich:

- MiniMax `baseUrl` mit `/anthropic`.
- MiniMax `api: anthropic-messages`.
- Hermes MiniMax `base_url: https://api.minimax.io/anthropic`.

Grund: Das ist Anthropic-kompatibles Protokoll, nicht Anthropic/Claude als Anbieter.

## Backup

Backup vor Mutation:

```text
/home/piet/backups/anthropic-removal-20260502-230335
```

Gesichert wurden:

- `/home/piet/.openclaw/openclaw.json`
- `/home/piet/.openclaw/agents/*/agent/auth-profiles.json`
- `/home/piet/.openclaw/agents/*/agent/models.json`
- `/home/piet/.hermes/.env`
- `/home/piet/.hermes/config.yaml`

## Entfernt

- `auth.profiles` mit `anthropic:*` und `claude-cli`.
- Agent-Auth-Profile `anthropic:claude-code`, `anthropic:claude-code-refresh`, `anthropic:claude-cli`.
- Provider `models.providers.anthropic`.
- OpenRouter Claude model entries (`anthropic/claude-*`).
- OpenClaw aliases `opus` und `sonnet`.
- OpenClaw allowed model entries `anthropic/claude-*`.
- `plugins.allow` Eintrag `anthropic`.
- `plugins.entries.anthropic`.
- `agents.defaults.agentRuntime.id=claude-cli` wurde auf `codex` gesetzt.
- Stale Hermes `.env` Kommentar `# LLM_MODEL=anthropic/claude-opus-4.6`.

## Validierung

- JSON-Syntax aller betroffenen JSON-Dateien: PASS.
- `openclaw config validate`: PASS.
- `openclaw models status --json`: PASS.
- `providersWithOAuth`: nur noch `openai-codex (2)`.
- OAuth Provider Summary: `google=static`, `openai-codex=ok`, `openrouter=static`.
- OpenClaw aliases: nur noch `OpenRouter -> openrouter/auto`.
- Allowed models: OpenAI Codex, MiniMax highspeed, OpenRouter auto, GPT image only.
- Agent `auth-profiles.json`: 0 Anthropic/Claude Profile.
- Agent `models.json`: 0 `providers.anthropic`.
- Hermes E2E via `openclaw-readonly`: PASS.
- OpenClaw health: HTTP 200.
- Services: `openclaw-gateway.service`, `openclaw-discord-bot.service`, `hermes-gateway.service` active.

## Kein Restart

OpenClaw Gateway wurde initial nicht neu gestartet. Danach gab Piet am 2026-05-02 um ca. 23:09 CEST die Freigabe, weil das System ruhig war.

Apply-Restart:

```bash
systemctl --user restart openclaw-gateway.service
curl -s -o /dev/null -w "openclaw=%{http_code}\n" http://127.0.0.1:18789/health
```

## Post-Restart Validation

- Pre-check Mission Control: `status=ok`, `severity=ok`, `openTasks=0`, `staleOpenTasks=0`, `recoveryLoad=0`, `attentionCount=0`.
- Pre-check Board: `All clear`, `action=none`.
- `systemctl --user restart openclaw-gateway.service`: PASS.
- `openclaw-gateway.service`: active, Node `v22.22.0`, PID `3549834`.
- OpenClaw Health: HTTP 200, `ok=true`, `status=live`.
- Mission Control Health after restart: `status=ok`, `severity=ok`, `openTasks=0`, `staleOpenTasks=0`.
- `openclaw models status --json`: PASS.
- Default model: `minimax/MiniMax-M2.7`.
- Fallbacks: `minimax/MiniMax-M2.7-highspeed`, `openai-codex/gpt-5.5`, `openrouter/auto`.
- OAuth providers: only `openai-codex (2)`; no Anthropic/Claude OAuth left.
- OpenClaw aliases: only `OpenRouter -> openrouter/auto`.
- `openclaw-discord-bot.service`: active, last heartbeat `mc=active bot=alive`.
- `hermes-gateway.service`: active.
- `hermes mcp test openclaw-readonly`: PASS.
- `hermes mcp test mc-readonly`: PASS.
- `hermes mcp test qmd-vault`: PASS.
- QMD HTTP `/health`: HTTP 200.
- OpenClaw Gateway warnings/errors after restart: none.

## Residual Observations

- Hermes Discord slash-command sync still showed Discord HTTP 429 rate-limit warnings before/around the check window. Gateway stayed active.
- One Hermes QMD search error appeared around 23:07, but direct `qmd-vault` MCP test and QMD HTTP health passed afterward.
