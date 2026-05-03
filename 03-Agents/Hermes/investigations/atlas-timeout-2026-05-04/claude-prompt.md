You are a read-only Claude Code investigation subagent for Piet's OpenClaw huebners setup.

Goal: Independently assess whether Atlas timeouts in OpenClaw 2026.5.2 indicate a new OpenClaw bug/regression, and whether reverting/trying the old `openai-codex/gpt-5.5` route would likely be more stable than current `openai/gpt-*` + `agentRuntime.id=codex`.

Evidence directory: /home/piet/vault/03-Agents/Hermes/investigations/atlas-timeout-2026-05-04
Files:
- trajectory-relevant.json
- gateway-journal-window.log
- gateway-journal-timeout-subset.log
- config-main-redacted.json
- pi-embedded-rWtLEwl7.js
- diagnostic-oEUVZa4J.js

Context facts from prior live evidence:
- OpenClaw Gateway runs v2026.5.2 with external Discord/Codex plugins.
- Main/Atlas config currently: primary openai/gpt-5.5, fallbacks openai/gpt-5.4-mini, openai/gpt-5.4, openai/gpt-5.3-codex, agentRuntime {id: codex, fallback: pi}.
- Previous migration away from `openai-codex/gpt-*` fixed old model-resolution stall/outputTokens=9 abort pattern in this setup.
- Current incident: `openai/gpt-5.4-mini` timed out after ~300s, then fallback `openai/gpt-5.4` succeeded after ~29s.

Questions:
1. Is this more consistent with a new OpenClaw 2026.5.2 bug/regression, a Codex app-server runtime timeout, or model/backend latency?
2. Does evidence suggest `openai-codex/gpt-5.5` would be more stable? Compare likely code paths/providers and known pitfalls. Be skeptical: do not recommend old route just because current route timed out.
3. What source-code areas should be inspected next to prove/deny a bug? Include filenames/search strings.
4. What read-only experiment would safely compare `openai/gpt-*` Codex runtime vs `openai-codex/gpt-*` without risking Atlas production Discord?
5. Give a verdict and confidence level.

Constraints:
- Do NOT mutate any runtime/config/service files.
- You may write final report to /home/piet/vault/03-Agents/Hermes/investigations/atlas-timeout-2026-05-04/claude-openclaw-regression-report.md
- German final report preferred, evidence-first.
