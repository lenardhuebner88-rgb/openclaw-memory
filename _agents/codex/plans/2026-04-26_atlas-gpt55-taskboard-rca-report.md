---
status: done
created: 2026-04-26T18:51:09Z
agent: codex
scope: atlas-gpt55-taskboard-rca
---

# Atlas GPT-5.5 + Taskboard RCA

## Kurzfazit

Atlas konnte nicht sauber ueber Taskboard-MCP arbeiten, obwohl Mission Control HTTP gesund war. Parallel wurde `openai-codex/gpt-5.5` als `Unknown model` behandelt.

Rootcause war zweigeteilt:
- OpenClaw 2026.4.22 kannte im `openai-codex` Provider nur Forward-Compat bis `gpt-5.4`; `gpt-5.5` war in den Agent-Model-Dateien unter `codex`, aber nicht wirksam unter `openai-codex`.
- Die Default-Session `agent:main:main` war auf `gpt-5.4-mini` persistiert und stellte diesen Wert nach einfacher Feldkorrektur wieder her.

## Live-Evidence

- `openclaw models --agent main list` vor Fix: `openai-codex/gpt-5.5` = `configured,missing`.
- Gateway-Log vor Fix: `FailoverError: Unknown model: openai-codex/gpt-5.5`.
- Gateway-Log vor Fix: `taskboard__taskboard_* failed: Not connected`.
- Mission Control HTTP war gesund: `/api/health` = `ok`, `/api/tasks` lieferte Tasks.
- Isolierter Taskboard-MCP-HTTP-Test war gesund: `/health` = `ok`.

## Fixes

- Provider Runtime gepatcht:
  - `/home/piet/.npm-global/lib/node_modules/openclaw/dist/openai-codex-provider-CqWyH5Qs.js`
  - `gpt-5.5` als OpenAI-Codex Forward-Compat-Modell, Modern-Modell und xhigh-faehiges Modell eingetragen.
- Agent Model Stores gepatcht:
  - `/home/piet/.openclaw/agents/main/agent/models.json`
  - `/home/piet/.openclaw/agents/frontend-guru/agent/models.json`
  - `/home/piet/.openclaw/agents/efficiency-auditor/agent/models.json`
  - `/home/piet/.openclaw/agents/sre-expert/agent/models.json`
  - `/home/piet/.openclaw/agents/spark/agent/models.json`
  - `/home/piet/.openclaw/agents/james/agent/models.json`
- Persistierten alten Default-Session-Binding rotiert:
  - `agent:main:main` aus `/home/piet/.openclaw/agents/main/sessions/sessions.json` entfernt.
  - Alter Transcript blieb erhalten; nur das Mapping wurde neu aufgebaut.
- `openclaw-gateway.service` kontrolliert neu gestartet, damit Provider-Patch und Session-Rotation wirksam werden.

## Backups

- `/home/piet/.openclaw/backup/atlas-gpt55-provider-rca-20260426/`
- zusaetzlich automatische OpenClaw-Config-Backups:
  - `/home/piet/.openclaw/openclaw.json.bak`

## Verification

- `openclaw models --agent main list`: `openai-codex/gpt-5.5` = `text+image`, `auth=yes`, `default,configured`.
- `openclaw models --agent frontend-guru list`: `gpt-5.5` = `default,configured`.
- `openclaw models --agent efficiency-auditor list`: `gpt-5.5` = `default,configured`.
- Gateway Restart-Log: `agent model: openai-codex/gpt-5.5`.
- Main default smoke:
  - Antwort: `MAIN_DEFAULT_GPT55_OK`
  - Modell: `gpt-5.5`
  - Session-Key: `agent:main:main`
- Taskboard smoke:
  - Antwort: `EXECUTION_STATUS: done; MODEL: openai-codex/gpt-5.5; TASKBOARD_TOOL: ok`
  - Ergebnis: `total=671, draft=8, done=564, failed=48, canceled=51`
- Seit dem finalen Restart keine neuen `Unknown model`, `model-fallback`, `Not connected` oder `taskboard__* failed` Logs im geprueften Gateway-Fenster.

## Rest-Risiken

- Der Patch liegt in installierter OpenClaw-Dist. Bei einem OpenClaw-Update kann er ueberschrieben werden. Empfehlung: Upstream-Fix oder lokaler Patch-Guard.
- `/home/piet/.openclaw/lib/node_modules/...` ist root-owned und wurde nicht gepatcht; aktuell nutzt Gateway `/home/piet/.npm-global/...`, daher ist das fuer den Live-Fix nicht relevant.
- Alte, spezifische Sessions koennen weiter eigene Modellhistorie haben. Neue/default Board-Arbeit laeuft jetzt aber ueber `gpt-5.5`.
