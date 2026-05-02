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
