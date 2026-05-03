---
title: MiniMax M2.7-highspeed Research Summary
created: 2026-05-03T17:58Z
agent: Hermes
for: Atlas
status: read_only_research_summary
source: Discord incident thread / Hermes read-only investigation
---

# MiniMax M2.7-highspeed — Kurzrecherche für Atlas

## Kurzfazit

MiniMax M2.7-highspeed ist für Piet grundsätzlich passend, weil Piet auf huebners einen **MiniMax Token Plan API Key** nutzt. Der korrekte technische Pfad ist daher der **Anthropic-compatible Token-Plan Endpoint**:

```text
https://api.minimax.io/anthropic
```

Das beobachtete lokale Problem war nicht primär ein fehlender MiniMax-Account oder fehlender Provider, sondern Runtime-Routing: Agenten mit `agentRuntime.id: "codex"` versuchen MiniMax-Fallbacks über den Codex app-server zu laden. Dort ist `minimax` nicht verfügbar, was zu folgendem Fehler führt:

```text
Model provider `minimax` not found
```

## Relevante Erkenntnisse

1. **Token Plan Semantik**
   - Piet nutzt einen Token Plan API Key, nicht OAuth/Coding-Plan als Primärannahme.
   - Für diesen Key ist `https://api.minimax.io/anthropic` der richtige Base-URL-Pfad.
   - OpenClaw sollte dafür den Provider `minimax` mit `api: anthropic-messages` nutzen.

2. **Empfohlener Provider-Pfad**
   - Bevorzugt:
     ```text
     minimax/MiniMax-M2.7-highspeed
     baseUrl=https://api.minimax.io/anthropic
     api=anthropic-messages
     ```
   - Nicht als erste Annahme für Piet:
     ```text
     minimax-portal/...
     ```
     weil das eher zum OAuth/Portal-Pfad passt.

3. **MiniMax M2.7-highspeed Parameter**
   - Offizielle Eckdaten: ca. 204,800 Kontext, hohe Ausgaberate, Streaming unterstützt.
   - Unterstützt u.a. `model`, `messages`, `max_tokens`, `stream`, `system`, `temperature`, `tools`, `tool_choice`.
   - MiniMax empfiehlt `temperature: 1`.
   - Für Agent-Stabilität lieber konservativ starten: `maxTokens` etwa `8192` oder `16384`, nicht direkt extreme Output-Limits.

4. **Bekannte Risiken aus GitHub/Community-Signalen**
   - MiniMax 2.7 kann bei langen agentischen TODO-/Continuation-Flows unerwartet stoppen.
   - Es gibt Berichte über Tool-/Subagent-Probleme, u.a. HTTP 400 / error 2013 und duplicate `tool_call` IDs bei Anthropic-/Relay-Pfaden.
   - Für lange Multi-Agent- oder Tool-heavy Workflows ist M2.7-highspeed daher besser zuerst als Fallback statt als alleiniger Primary zu testen.

5. **Lokaler OpenClaw-Routing-Fix**
   - Wenn Atlas primary OpenAI/Codex bleiben soll, MiniMax aber als Fallback nutzbar sein soll, braucht Atlas/runtime-seitig einen Provider-Runtime-Fallback, z.B. konzeptionell:
     ```json
     "agentRuntime": {
       "id": "codex",
       "fallback": "pi"
     }
     ```
   - Ohne diesen Fallback landet MiniMax weiterhin im Codex app-server und schlägt mit `Model provider minimax not found` fehl.

## Empfohlene Zielstrategie für Atlas

Konservativer Start:

```text
Primary:   openai/gpt-5.5
Fallback1: minimax/MiniMax-M2.7-highspeed
Fallback2: minimax/MiniMax-M2.7
Fallback3: openai/gpt-5.4-mini oder openai/gpt-5.4
Runtime:   codex mit PI/provider fallback für nicht-Codex Provider
```

MiniMax nicht sofort als alleiniger Primary für Atlas setzen, sondern erst isoliert testen:

1. kurzer Direktturn
2. mittlerer Textturn
3. einfacher Tool-/Plan-Turn
4. danach produktiver Atlas-Fallback-Test

## Offene Punkte für Atlas

- Prüfen, ob aktuelle Atlas-Session Runtime-/Model-State cached; ggf. nach Config-Änderung neue Session oder Reset nötig.
- Nach jeder Änderung Gateway-Health und OpenClaw Logs prüfen.
- Bei MiniMax-Timeouts zwischen echtem Upstream-Timeout und lokalem Runtime-Routing-Fehler unterscheiden.

## Wichtig

Diese Notiz ist eine **read-only Recherche-Zusammenfassung**. Sie dokumentiert keine durchgeführte Config-Änderung.
