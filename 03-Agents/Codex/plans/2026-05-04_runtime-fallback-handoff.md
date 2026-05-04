# Runtime Fallback Handoff

Stand: 2026-05-04 10:05 CEST
Owner: Atlas/Codex
Scope: Uebergabepunkt nach Analyse zu Codex Runtime, Pi/auto-Fallback und MiniMax M2.7 als Stabilitaets-Fallback.

## Kurzfazit

Die aktuelle OpenClaw-Config ist syntaktisch valide, aber fuer Stabilitaet weiterhin zu hart auf Codex gepinnt. Das Zielbild fuer den Alltagsbetrieb ist nicht `agentRuntime.id = "codex"`, sondern `agentRuntime.id = "auto"` mit MiniMax M2.7 als erstem Modell-Fallback. Codex-strikte Ausfuehrung sollte nur fuer dedizierte Test-/Lab-Agenten oder explizite Diagnose genutzt werden.

Wichtig: Ein Runtime-Fallback ist kein garantierter Mid-Turn-Replay. Wenn eine bestehende Session bereits auf Codex gepinnt ist oder ein Codex-Turn nach sichtbaren Side Effects ausfaellt, wird der laufende Turn nicht automatisch sauber auf Pi/MiniMax neu abgespielt. Stabilisierung greift vor allem fuer neue oder reset Sessions.

## Verifizierte Fakten aus der Session

- Aktive Version laut Status/CLI: `OpenClaw 2026.5.3-beta.4 (c6c64e2)`.
- Aktive Discord-Session `agent:main:discord:channel:1486480128576983070` laeuft als `openai/gpt-5.5` ueber `openai-codex` OAuth.
- Aktive Runtime der Session: `OpenAI Codex`.
- Aktive Session-Fallbacks: `openai/gpt-5.3-codex`, `openai/gpt-5.4`, `openai/gpt-5.4-mini`.
- Kontextstatus waehrend Analyse: ca. `199k/272k` (`73%`), Cache-Hit ca. `91%`, Compactions `0`.
- Toolcalls funktionieren: `session_status`, `openclaw config validate`, `openclaw models status --json` liefen erfolgreich.
- `openclaw config validate`: Config valid.
- `openclaw models status --json` meldete `openai` als missing provider in use, obwohl die aktuelle Session ueber `openai-codex` OAuth laeuft.
- `openclaw models status` warnte ueber stale Plugin-Config:
  - `plugins.entries.discord: plugin not found`
  - `plugins.entries.codex: plugin not found`
  - `plugins.allow: plugin not found: discord`
  - `plugins.allow: plugin not found: codex`
- Plugin-Registry meldete stale persisted registry metadata und empfahl `openclaw plugins registry --refresh`.
- Plugin-Liste zeigte `minimax`, `openai`, `openrouter`, `memory-core` als geladene bundled Plugins.
- `codex` und `discord` tauchten in der gefilterten Plugin-Liste nicht als geladene Plugin-IDs auf, obwohl sie in `plugins.allow`/`plugins.entries` stehen.
- Gateway/Service-Env wirkte nicht voll versiongleich: CLI meldete beta4, `OPENCLAW_SERVICE_VERSION` meldete `2026.5.2`.

## Ist-Zustand der Runtime-/Model-Config

- `agents.defaults.agentRuntime.id = "codex"`.
- Alle Alltagsagenten haben eigene `agentRuntime.id = "codex"` Overrides:
  - `main`
  - `sre-expert`
  - `frontend-guru`
  - `efficiency-auditor`
  - `james`
  - `system-bot`
  - `spark`
- Default-Modell ist `openai/gpt-5.4-mini`.
- Default-Fallbacks sind derzeit nur OpenAI/Codex-nahe Modelle:
  - `openai/gpt-5.5`
  - `openai/gpt-5.4`
  - `openai/gpt-5.3-codex`
- Per-Agent-Fallbacks enthalten aktuell kein MiniMax M2.7.
- MiniMax M2.7 und MiniMax M2.7 Highspeed sind im Modellkatalog vorhanden.
- MiniMax Provider ist in `models.providers.minimax` und `models.providers.minimax-portal` konfiguriert.
- MiniMax Auth ist laut Models-Status effektiv ueber `models.json` vorhanden.
- `embeddedHarness` ist nicht aktiv gesetzt; das ist gut, weil beta4 `agentRuntime` als kanonischen Key nutzt.

## Soll-Zustand

Ziel fuer Alltagsbetrieb:

```json
{
  "agents": {
    "defaults": {
      "agentRuntime": { "id": "auto" },
      "model": {
        "primary": "openai/gpt-5.5",
        "fallbacks": [
          "minimax/MiniMax-M2.7",
          "minimax/MiniMax-M2.7-highspeed",
          "openai/gpt-5.4-mini"
        ]
      }
    }
  }
}
```

Per-Agent `agentRuntime.id = "codex"` sollte fuer Atlas/Forge/Pixel/Lens/James/System-Bot/Spark nicht global gesetzt bleiben, wenn Stabilitaet und Fallback-Faehigkeit Prioritaet haben. Codex-strikt gehoert in einen dedizierten Test-Agenten oder in temporaere Diagnose.

## Schwachpunkte fuer den naechsten Handoff

1. Runtime ist zu hart auf Codex gepinnt.
   - Folge: `agentRuntime.id = "codex"` ist fail-closed und verhindert den stabilen Pi/MiniMax-Pfad.

2. Per-Agent Overrides hebeln jeden Default-Fix aus.
   - Selbst wenn `agents.defaults.agentRuntime.id` auf `auto` gesetzt wird, bleiben alle Agenten mit eigenem `codex` Override hart gepinnt.

3. MiniMax ist konfiguriert, aber nicht operativ als Fallback verdrahtet.
   - Modell vorhanden und Auth sichtbar, aber keine aktiven Agent-Fallback-Ketten nutzen `minimax/MiniMax-M2.7`.

4. Plugin-Registry/Plugin-Config ist nicht sauber.
   - `discord` und `codex` werden als stale Plugin-Eintraege gewarnt. Das muss vor einer Runtime-Umbauaktion geklaert werden, weil sonst unklar bleibt, welche Plugin-/Harness-Pfade wirklich geladen sind.

5. CLI/Gateway-Version wirkt driftend.
   - CLI beta4, Service-Env `2026.5.2`. Vor stabilisierenden Config-Aenderungen sollte die laufende Gateway-Umgebung versiongleich sein.

6. Bestehende Sessions behalten Runtime-Pins.
   - Die aktuelle `#atlas-main` Session bleibt `Runtime: OpenAI Codex`, auch wenn die Config danach auf `auto` geht. Nach Aenderungen braucht es Reset/neue Session fuer belastbare Tests.

7. Kontextdruck ist durch Bootstrap/Toolausgaben hoch.
   - Der hohe Kontextstatus kam nicht aus wenigen Chat-Nachrichten allein, sondern aus Bootstrap, Tool-Schemas, bisherigen Session-Daten und grossen Diagnoseausgaben. Fuer einen echten Umbau ist eine frische Session sinnvoll.

8. Auth-Sicht ist uneinheitlich.
   - `models status` meldet `openai` missing, waehrend die aktive Session ueber `openai-codex` OAuth funktioniert. Das ist nicht zwingend ein Blocker, aber ein Diagnosepunkt fuer OpenAI-vs-Codex-Routing.

## Empfohlene naechste Schritte

1. Read-only Baseline erneut erfassen.
   - `openclaw --version`
   - `openclaw config validate`
   - `openclaw plugins list --json`
   - `openclaw models status --json`
   - `session_status` fuer die betroffene Session

2. Plugin-Registry bereinigen.
   - `openclaw plugins registry --refresh`
   - Danach pruefen, ob `codex` und `discord` weiterhin als stale gewarnt werden.
   - Wenn ja: klaeren, ob diese IDs in beta4 externalisiert/umbenannt wurden oder aus `plugins.allow`/`plugins.entries` entfernt werden muessen.

3. CLI/Gateway-Version angleichen.
   - Safe-Restart-Pfad nutzen, nicht direkt hart restarten.
   - Danach erneut `openclaw health`, `openclaw --version`, Plugin-Warnings und `session_status` pruefen.

4. Erst dann Config-Aenderung vorbereiten.
   - Backup von `/home/piet/.openclaw/openclaw.json`.
   - Ziel: `agents.defaults.agentRuntime.id = "auto"`.
   - Per-Agent `agentRuntime.id = "codex"` fuer Alltagsagenten entfernen.
   - MiniMax M2.7 als ersten Fallback in Defaults und relevanten per-Agent-Ketten setzen.

5. Nach jeder Config-Aenderung validieren.
   - `openclaw config validate`
   - `openclaw models status --json`
   - Check: keine unerwuenschten `agentRuntime.id = "codex"` Overrides mehr.
   - Check: `minimax/MiniMax-M2.7` ist in den aktiven Fallback-Ketten sichtbar.

6. Sessions resetten oder neu starten.
   - Besonders `#atlas-main`/Atlas, weil die aktuelle Session Codex-runtime-gepinnt ist.

7. Live-Probe klein halten.
   - Ein normaler Atlas-Turn nach Reset.
   - Dann gezielt pruefen, ob `auto`/Pi + MiniMax-Fallback in einer neuen Session sichtbar wird.
   - Nicht erwarten, dass ein bereits laufender Codex-Turn mid-turn transparent auf MiniMax replayed.

## Nicht tun

- Nicht blind `embeddedHarness` schreiben; in beta4 ist `agentRuntime` der kanonische Key.
- Nicht `agentRuntime: { "id": "codex", "fallback": "pi" }` schreiben; das aktive Schema zeigt fuer `agentRuntime` nur `id`, kein `fallback`.
- Nicht nur den Default auf `auto` setzen und die per-Agent Overrides vergessen.
- Nicht Plugin-Warnings ignorieren, bevor Runtime-/Fallback-Policy geaendert wird.
- Nicht bestehende Codex-gepinnte Sessions als Beweis fuer neue Runtime-Policy verwenden.

## Uebergabe-Hinweis

Naechster Agent sollte zuerst Registry/Version/Warnings klaeren. Erst wenn die Beta4-Umgebung konsistent ist, sollte die Runtime-Config auf `auto` plus MiniMax-Fallback umgestellt werden. Die eigentliche Stabilisierung ist ein zweistufiger Vorgang: erst Runtime-/Plugin-Sauberkeit herstellen, dann Sessions resetten und den neuen Fallback-Pfad live pruefen.
