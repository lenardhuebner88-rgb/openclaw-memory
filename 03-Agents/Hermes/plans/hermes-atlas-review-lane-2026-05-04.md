# Hermes ↔ Atlas Read-only Review Lane — 2026-05-04

## Ziel
Hermes wird als Shadow-/Break-glass-Review-Agent nutzbar, ohne sofort als vollautomatischer Mission-Control-Worker in den Dispatch-Pfad zu greifen.

## Scope
- Atlas koordiniert und bleibt Lead.
- Hermes liefert read-only Evidenz, Risiko und nächsten Schritt.
- Keine Restarts, Config-Edits, Cron-Änderungen, Deletes, Deploys oder Task-Mutationen durch Hermes.
- Model-Drift `openai/*` → `openai-codex/*` wird separat durch Codex Terminal bearbeitet.

## Pilot-Task-Typ
`hermes-review`

### Standard-Prompt
```text
You are Hermes in Piet's OpenClaw/Homeserver support context.

TASK_TYPE: hermes-review
MODE: read-only only

Objective:
<one concrete review objective>

Check only with already available read-only evidence/tools. Do not modify files, services, configs, tasks, crons, containers, or sessions.

Return exactly this structure:
status: ok|warning|blocked|failed
summary: <max 5 bullets>
evidence: <max 5 bullets with concrete signals>
risk: <max 3 bullets>
next_action: <one concrete next step>
```

## Pilot-Ausführung
Atlas kann Hermes zunächst per CLI ausführen:

```bash
/home/piet/.hermes/hermes-agent/venv/bin/python -m hermes_cli.main --ignore-rules -z "$(cat /tmp/hermes-task.txt)"
```

Board-Integration in dieser Stufe:
1. Atlas erstellt/führt den Board-Task weiterhin selbst.
2. Atlas sendet die read-only Review-Frage an Hermes CLI.
3. Atlas übernimmt Hermes-Receipt als Evidenz/Kommentar/Result ins Board.

## Live-Pilot vom 2026-05-04
Hermes antwortete im geforderten Format mit `status: warning`.

Verifizierte Signale:
- Hermes CLI erreichbar (`HERMES_OK`).
- Hermes konnte read-only MCP nutzen.
- Mission Control Health/Board/OpenClaw Readonly Endpoints HTTP 200.
- OpenClaw Gateway `/health` HTTP 200 `ok=true,status=live`.
- Receipt-Struktur vollständig: `status`, `summary`, `evidence`, `risk`, `next_action`.

Warnungen aus Pilot:
- Atlas→Hermes Board-Zuweisung ist noch nicht als automatischer Pfad bewiesen.
- `openclaw-discord-bot.service` ist Legacy/Commander und aktuell bewusst inactive; Gateway Discord ist SSoT.
- OpenClaw Model-Status meldete noch `missingProvidersInUse=["openai"]`; separater Codex-Fix.

## Fix/Entscheidung: Legacy Discord Service
`openclaw-discord-bot.service` darf nicht mehr als harter OpenClaw-Discord-Ausfall gewertet werden, solange:
- `openclaw-gateway.service` active/running ist,
- `openclaw status` Discord `ON/OK` meldet,
- Gateway Discord als Single Source of Truth gilt.

Umgesetzt am 2026-05-04:
- `/home/piet/.hermes/mcp/openclaw_readonly_server.py` klassifiziert `openclaw-discord-bot.service` als optional legacy service.
- `openclaw_services_status()` gibt primäre Services und `optional_legacy_services` getrennt zurück.
- Backup: `/home/piet/.hermes/mcp/openclaw_readonly_server.py.bak-atlas-20260504-legacy-discord-optional`.
- Gate: `python3 -m py_compile` erfolgreich; direkter Funktionsaufruf zeigt Gateway required active und legacy Discord optional inactive/dead.

## Nächste Stufe
Nach Codex Model-Drift-Fix:
1. `openclaw models status --json` prüfen: `missingProvidersInUse=[]`.
2. Einen Board-Task `hermes-review` im Adapter-Modus ausführen.
3. Receipt manuell ins Board übernehmen.
4. Erst nach 3 erfolgreichen Receipts `owner=hermes` + Dispatch-Adapter planen.

## Nicht jetzt tun
- Kein `owner=hermes` in Mission Control erzwingen.
- Kein Auto-Pickup für Hermes aktivieren.
- Kein Start des Legacy `openclaw-discord-bot.service`.
- Kein Hermes-YOLO oder mutierende Toolsets.
