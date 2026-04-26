---
status: done
created: 2026-04-26T17:47:13Z
agent: codex
scope: atlas-orchestrator-optimization-implementation
---

# Atlas Orchestrator Optimization Implementation Report

## Ergebnis

Atlas ist fuer den Discord-Default-Pfad deutlich schlanker und stabiler:

- Bootstrap-Kontext wurde begrenzt: `bootstrapMaxChars=16000`, `bootstrapTotalMaxChars=42000`.
- Atlas-spezifische Context-Limits wurden gesetzt: `postCompactionMaxChars=12000`, `toolResultMaxChars=4000`, `memoryGetMaxChars=10000`.
- Trajectory-Events schreiben keine grossen Roh-Prompts/Tool-Definitionen mehr, sondern Hashes, Zaehler und Byte-Metriken.
- `agent:main:discord:*` nutzt jetzt einen schlanken Default-Tool-Modus ohne Shell-/Edit-/Cron-/Media-/Session-Spawn-Tools.
- Ein reproduzierbares read-only Gate liegt unter `/home/piet/.openclaw/scripts/atlas-orchestrator-budget-proof.mjs`.

## Geaenderte Dateien

| Datei | Zweck |
|---|---|
| `/home/piet/.openclaw/openclaw.json` | Bootstrap-/Context-Limits fuer Atlas reduziert |
| `/home/piet/.npm-global/lib/node_modules/openclaw/dist/selection-DGLE6AvW.js` | Trajectory-Compaction + Atlas-Discord-Tool-Mode |
| `/home/piet/.openclaw/scripts/atlas-orchestrator-budget-proof.mjs` | Read-only Proof fuer Atlas Session/Context/Tool Budget |

Backups:

- `/home/piet/.openclaw/backup/atlas-orchestrator-opt-20260426/openclaw.json.bak`
- `/home/piet/.openclaw/backup/atlas-orchestrator-opt-20260426/selection-DGLE6AvW.js.bak`

## Vorher/Nachher

Vorher, Live-Trajectory `46ffe260-6056-4a00-8cc6-4bc8916e4ecd.trajectory.jsonl`:

- Datei: 8.18 MB
- `trace.metadata`: ca. 104 KB pro Event
- `context.compiled`: bis ca. 245 KB
- Tool-Schema: ca. 42 KB
- Tools: 37
- Systemprompt: ca. 98 KB

Nachher, Atlas-Discord-Smoke `9878ea73-26b8-4667-b9bb-538502094cc0.trajectory.jsonl`:

- Datei: 12 KB
- `trace.metadata`: 3.3 KB
- `context.compiled`: 1.5 KB
- Tool-Schema: 17 KB
- Tools: 21
- Systemprompt: ca. 67 KB
- Budget-Proof: `status=ok`

## Implementierte Gates

`/home/piet/.openclaw/scripts/atlas-orchestrator-budget-proof.mjs` prueft:

- neueste und groesste Atlas/Main-Trajectory
- `trace.metadata` Ziel < 10 KB
- `context.compiled` Ziel < 80 KB
- Tool-Schema Ziel < 20 KB
- Bootstrap-Total Ziel <= 42 KB

Letzter Gate-Status:

```json
{
  "status": "ok",
  "latest": {
    "bytes": 12001,
    "maxTraceMetadataBytes": 3284,
    "maxContextCompiledBytes": 1546,
    "maxToolsBytes": 17055,
    "maxToolsCount": 21,
    "compactedEvents": 2
  },
  "findings": []
}
```

## Validierung

Ausgefuehrt:

- `/home/piet/.openclaw/tools/node-v22.22.0/bin/node --check /home/piet/.npm-global/lib/node_modules/openclaw/dist/selection-DGLE6AvW.js`
- `/home/piet/.openclaw/tools/node-v22.22.0/bin/node --check /home/piet/.openclaw/scripts/atlas-orchestrator-budget-proof.mjs`
- `openclaw config validate`
- `systemctl --user restart openclaw-gateway.service`
- Atlas-Smoke mit `agent:main:discord:*`: Antwort `ATLAS_DISCORD_TOOLMODE_OK`
- `/api/health`
- `/api/ops/worker-reconciler-proof?limit=20`
- `/api/ops/pickup-proof?limit=20`
- `systemctl --user is-active openclaw-gateway.service mission-control.service openclaw-discord-bot.service`

Live-Gates:

- Health: ok
- Worker-Reconciler-Proof: ok, `openRuns=0`, `criticalIssues=0`
- Pickup-Proof: ok, `pendingPickup=0`, `criticalFindings=0`
- Services: `openclaw-gateway`, `mission-control`, `openclaw-discord-bot` active

## Tool-Mode Details

Atlas Discord Default behält:

- `read`
- `message`
- `agents_list`
- `update_plan`
- `sessions_list`
- `sessions_history`
- `session_status`
- `web_fetch`
- `memory_search`, `memory_get`
- `qmd__*`
- `taskboard__taskboard_create_task`, `get_task`, `list_tasks`, `patch_task`, `stats`

Atlas Discord Default entfernt:

- `exec`, `process`
- `edit`, `write`, `apply_patch`
- `cron`
- `gateway`
- `sessions_spawn`, `sessions_send`, `sessions_yield`, `subagents`
- `canvas`, `nodes`, `image`, `pdf`, `tts`

Damit bleibt Atlas im Discord-Normalbetrieb Orchestrator/Dispatcher, nicht Maintenance-Executor. Maintenance muss ueber Worker, expliziten Task oder nicht-Discord-Pfad laufen.

## Rollback

Schnell-Rollback:

```bash
cp /home/piet/.openclaw/backup/atlas-orchestrator-opt-20260426/openclaw.json.bak /home/piet/.openclaw/openclaw.json
cp /home/piet/.openclaw/backup/atlas-orchestrator-opt-20260426/selection-DGLE6AvW.js.bak /home/piet/.npm-global/lib/node_modules/openclaw/dist/selection-DGLE6AvW.js
systemctl --user restart openclaw-gateway.service
```

Verify:

```bash
openclaw config validate
systemctl --user is-active openclaw-gateway.service
curl -sS http://127.0.0.1:3000/api/health
```

## Rest-Risiken

- Die Runtime-Aenderung liegt in gebuendeltem `dist`; ein OpenClaw-Update kann sie ueberschreiben. Das sollte als Upstream-/Patch-Sprint sauber in Source/Extension-Form nachgezogen werden.
- `systemPrompt` ist mit ca. 67 KB noch nicht Zielwert < 35 KB. Der naechste Hebel ist echte Kernelisierung von `AGENTS.md`/`HEARTBEAT.md`, nicht nur Truncation.
- `message` bleibt ein schweres Tool, ist aber fuer Discord-Operatorbetrieb bewusst behalten.
- Fuer Maintenance braucht Atlas weiter einen expliziten Pfad, weil Discord-Default jetzt keine Shell-/Edit-/Cron-Tools mehr hat.

## Naechster Sprint

Sprint D: Atlas Kernel v1

- `HEARTBEAT.md` in aktive Checkliste + Archivteil splitten.
- `MEMORY.md` nur noch via QMD/Retrieval nutzen; Dauerprompt auf Kernregeln begrenzen.
- Ziel: `systemPrompt.chars < 45000`, spaeter < 35000.
- Gate: neuer Atlas-Discord-Smoke + Budget-Proof `status=ok`.

