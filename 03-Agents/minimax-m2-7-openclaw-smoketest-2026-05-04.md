# MiniMax M2.7 in OpenClaw — Analyse + Smoketest

Datum: 2026-05-04  
Kontext: #atlas-main (Operator-Anfrage)  
Modus: Nur Analyse, keine Konfigurationsaenderungen

## Ziel

Pruefen, wie `MiniMax M2.7` im aktuellen OpenClaw-System hinterlegt ist, ob ein Live-Smoketest erfolgreich ist, und ob die Einbindung sauber/nutzbar ist.

## Gepruefte Bereiche

1. Konfiguration in `~/.openclaw/openclaw.json`
2. Modellregistrierung ueber OpenClaw-CLI
3. Live-Inferenztest ueber Gateway (`model.run`)
4. Plugin-/Provider-Metadaten fuer MiniMax

## Konfigurationsbefund

- Auth-Profile vorhanden:
  - `minimax-portal:default` (api key)
  - `minimax:global` (api key)
- Provider vorhanden:
  - `minimax-portal` mit Endpoint `https://api.minimax.io/v1` (`openai-completions`)
  - `minimax` mit Endpoint `https://api.minimax.io/anthropic` (`anthropic-messages`)
- Modelle vorhanden:
  - `MiniMax-M2.7`
  - `MiniMax-M2.7-highspeed`
- Plugin-Eintrag aktiv:
  - `plugins.entries.minimax.enabled = true`

## Smoketests (live)

Getestet via `openclaw infer model run --gateway ... --json`.

### Test A

Command:

```bash
openclaw infer model run --gateway --model minimax/MiniMax-M2.7 --prompt "Reply with exactly: pong" --json
```

Ergebnis:

- `ok: true`
- Antworttext: `pong`
- gemeldetes Laufzeitmodell: `MiniMax-M2.7-highspeed`

### Test B

Command:

```bash
openclaw infer model run --gateway --model minimax/MiniMax-M2.7-highspeed --prompt "Reply with exactly: pong" --json
```

Ergebnis:

- `ok: true`
- Antworttext: `pong`
- gemeldetes Laufzeitmodell: `MiniMax-M2.7-highspeed`

### Test C

Command:

```bash
openclaw infer model run --gateway --model minimax-portal/MiniMax-M2.7 --prompt "Reply with exactly: pong" --json
```

Ergebnis:

- Fehler: `Model override "minimax-portal/MiniMax-M2.7" is not allowed for agent "main".`

Analog fuer `minimax-portal/MiniMax-M2.7-highspeed` ebenfalls blocked.

## Bewertung

1. `minimax/*` ist im Live-System funktional und fuer Inferenz nutzbar.
2. `minimax/MiniMax-M2.7` wird im getesteten Pfad effektiv auf `MiniMax-M2.7-highspeed` aufgeloest.
3. `minimax-portal/*` ist als Provider registriert, aber fuer Agent `main` aktuell nicht als Model-Override zulaessig.
4. Fuer das vorhandene MiniMax-Token-Abo ist unmittelbare Nutzung ueber den `minimax/*`-Pfad gegeben.

## Ergaenzender Hinweis aus Plugin-Metadaten

Die MiniMax-Plugin-Metadaten deklarieren beide Provider (`minimax`, `minimax-portal`) und kennzeichnen M2.7 als empfohlenen Pfad (`groupHint: "M2.7 (recommended)"`).

## Offene technische Frage (fuer Folgeanalyse)

Warum `minimax/MiniMax-M2.7` im Runtime-Ergebnis als `...highspeed` erscheint (Alias/Normalisierung/Fallback), sollte im Codepfad der Modellaufloesung verifiziert werden.

---

## Folgeanalyse: Root Cause `M2.7 -> highspeed`

Status: geklaert (Codepfad verifiziert)

### Beobachtung

Bei Run mit `minimax/MiniMax-M2.7` meldet die Runtime als effektives Modell `MiniMax-M2.7-highspeed`.

### Ursache im Runtime-Code

1. `fastMode` wird pro Run aufgeloest aus Session > Agent-Default > Model-Config > Fallback:
   - Datei: `dist/fast-mode-DhnUJLZf.js`
   - Funktion: `resolveFastModeState(...)`
2. Wenn `fastMode=true`, wird bei MiniMax im Stream-Wrapper aktiv umgeschrieben:
   - `MiniMax-M2.7` -> `MiniMax-M2.7-highspeed`
   - Datei: `dist/proxy-stream-wrappers-ByIMwzl_.js`
   - `MINIMAX_FAST_MODEL_IDS = new Map([["MiniMax-M2.7", "MiniMax-M2.7-highspeed"]])`

### Relevanz fuer dieses System

`fastModeDefault: true` ist fuer mehrere Agenten gesetzt, inklusive `main`. Dadurch ist das Umschreiben auf Highspeed erwartetes Verhalten.

## Folgeanalyse: Warum `minimax-portal/*` fuer `main` blocked ist

Status: geklaert (Policypfad verifiziert)

### Ursache

Model-Overrides werden strikt gegen die Agent-Allowlist validiert.

- Datei: `dist/agent-command-6SSRbWDZ.js`
- Fehlerstelle: `Model override ".../..." is not allowed for agent "..."`
- Gleiches Prinzip im HTTP-Kompatibilitaetspfad:
  - Datei: `dist/http-utils-DvOnAXvn.js`

In der aktuellen Agent-Model-Allowlist stehen `minimax/*`-Eintraege, aber keine `minimax-portal/*`-Eintraege. Daher ist `minimax-portal/MiniMax-M2.7` als Override fuer `main` nicht zugelassen.

---

## Runtime-Analyse Codex vs PI (Ist + Soll-Schema)

### Ist-Zustand (2026-05-04)

- Global/default Runtime:
  - `agents.defaults.agentRuntime.id = "codex"`
- Agent-spezifisch:
  - `main`, `sre-expert`, `frontend-guru`, `efficiency-auditor`, `james`, `spark`, `system-bot` jeweils mit `agentRuntime.id = "codex"`
- Modelle sind ueberwiegend `openai/*` gesetzt (nicht `openai-codex/*`).

### Einordnung

Das entspricht der nativen Codex-Runtime-Variante (OpenAI-Modellref + Codex-Harness).

### Soll-Schema (saubere Trennung)

1. **Codex-native Runtime (empfohlen fuer ChatGPT/Codex-Subscription)**
   - Modellrefs: `openai/gpt-*`
   - Runtime: `agentRuntime.id: "codex"`
   - Auth: `openai-codex`-Loginprofil fuer Subscription-Auth

2. **PI-Route ueber Codex-OAuth (bewusst, nicht Default)**
   - Modellrefs: `openai-codex/gpt-*`
   - Runtime: `pi` (bzw. kein `codex`-Runtime-Force fuer diesen Agent)
   - Zweck: nur wenn explizit PI-Verhalten statt nativer Codex-Harness gewollt ist

3. **MiniMax sauber neben Codex**
   - Wenn MiniMax ohne implizite Highspeed-Umschaltung gewollt:
     - `fastModeDefault` fuer den betroffenen Agent aus
     - optional per-Model `params.fastMode` explizit setzen
   - Wenn Highspeed gewollt:
     - `fastModeDefault: true` beibehalten

### Praktische Architektur-Empfehlung

- Dedizierter Codex-Agent:
  - `openai/gpt-*` + `agentRuntime.id: "codex"`
- Dedizierter PI/Non-Codex-Agent:
  - `agentRuntime.id: "pi"` (oder `auto`, falls bewusst)
  - fuer Provider wie MiniMax/OpenRouter
- Keine Mischintention pro Agent (Codex-Harness und PI-Routing gleichzeitig erzwingen)  
  Das reduziert Debug-Aufwand bei Model-Override, Fast-Mode und Auth-Pfad.
