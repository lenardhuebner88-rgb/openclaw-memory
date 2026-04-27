---
title: MCP / Toolbridge RCA Fix Report
date: 2026-04-27
owner: codex
scope: openclaw-mcp-toolbridge
status: yellow
---

# MCP / Toolbridge RCA Fix Report

## Kurzfazit

Die akute Tool-Stoerung war kein reiner Mission-Control-Ausfall. Die Belege zeigen drei gekoppelte Ursachen:

1. `mcp-taskboard-reaper.sh` hatte um `2026-04-27T03:05:01+02:00` bei `count=9 cap=3` mehrere Taskboard-MCP-Prozesse beendet.
2. Danach meldete OpenClaw wiederholt `taskboard__taskboard_* failed: Not connected`.
3. Die Discord-Tool-Allowlist enthielt `taskboard__taskboard_dispatch_task`, aber der Taskboard-MCP-Server bot dieses Tool nicht an.

Zusatzbefund: QMD selbst ist lokal gesund (`qmd status`, QMD-MCP Client-Smoke, QMD-Search ok). QMD-Fehler in Atlas waren daher ebenfalls Toolbridge-/Session-Binding-Probleme, nicht ein kollabierter Index.

## Rootcause-Belege

### Taskboard-MCP Disconnect

- Log: `/home/piet/.openclaw/workspace/logs/mcp-reaper.log`
- Kritische Zeile: `2026-04-27T03:05:01+02:00 mcp-reaper: count=9 cap=3 — killing oldest 6`
- Folgefehler: `/tmp/openclaw/openclaw-2026-04-27.log` mit wiederholtem `taskboard__taskboard_stats failed: Not connected` und `taskboard__taskboard_list_tasks failed: Not connected`.

### Tool-Surface Drift

- Config erlaubt: `tools.byProvider.discord.alsoAllow=["image","taskboard__taskboard_dispatch_task"]`
- Server vor Fix: `server.js` bot nur `list/get/patch/create/stats`.
- Folge: selbst bei reparierter Verbindung haette Discord ein erlaubtes, aber nicht existierendes Dispatch-Tool gesehen.

### QMD

- `qmd status`: Index gesund, `1167 files indexed`, `53616 embedded`, zuletzt aktualisiert.
- QMD-MCP Client-Smoke: Tools `search`, `vector_search`, `deep_search`, `get`, `multi_get`, `status`.
- QMD-Search gegen Vault erfolgreich.

## Applied Fixes

### F1 - MCP-Reaper bereits gehaertet

- Datei: `/home/piet/.openclaw/scripts/mcp-taskboard-reaper.sh`
- Backup: `/home/piet/.openclaw/backup/audit-2026-04-27/mcp-taskboard-reaper.sh.bak-before-safe-cap-20260427T050115Z`
- Effekt:
  - Mindest-Cap `12`
  - Mindestalter `7200s`
  - zu niedriger Env-Cap wird nur angehoben, nicht mehr hart ausgefuehrt.
- Verify: `MCP_REAP_CAP=3 ...` loggt `configured cap=3 below min_cap=12 — using min_cap` und `no action`.

### F2 - Taskboard-MCP Dispatch-Tool nachgezogen

- Datei: `/home/piet/.openclaw/mcp-servers/taskboard/server.js`
- Backup: `/home/piet/.openclaw/backup/audit-2026-04-27/taskboard-server.js.bak-before-dispatch-tool-20260427T0528Z`
- Aenderungen:
  - `taskboard_dispatch_task` in `tools/list` ergaenzt.
  - Handler ruft `POST /api/tasks/<id>/dispatch` mit `taskId`, optional `agentId`, `runTimeoutSeconds`, `dispatchToken`.
  - `mcFetch` setzt jetzt Ingress-Header:
    - GET -> `x-request-class: read`
    - Dispatch -> `x-request-class: admin`
    - andere Mutationen -> `x-request-class: write`
    - jeweils `x-actor-kind: system`
  - Stdio-Prozess bekommt Keepalive + SIGTERM/SIGINT/SIGHUP-Shutdown, damit der MCP-Prozess nicht direkt mit Exit 0 endet.
- Verify:
  - `node --check .../server.js` ok.
  - manueller MCP-stdio `initialize` + `tools/list` zeigt `taskboard_dispatch_task`.

### F3 - Taskboard-MCP systemd Unit korrigiert

- Datei: `/home/piet/.openclaw/systemd/taskboard-mcp.service`
- Backup: `/home/piet/.openclaw/backup/audit-2026-04-27/taskboard-mcp.service.bak-before-http-transport-20260427T0528Z`
- Aenderung:
  - `MCP_TRANSPORT=http`
  - `MCP_HTTP_HOST=127.0.0.1`
  - `MCP_HTTP_PORT=7710`
- Grund: Die Unit startete vorher den Server als stdio-Prozess unter systemd. Als dauerhafter Service ist das nutzlos; falls diese Unit genutzt wird, muss sie HTTP-MCP starten.
- Verify: `systemd-analyze verify` ohne Fehler.

## Validierung

- OpenClaw Config: `openclaw config validate` -> valid.
- Taskboard-MCP Syntax: `node --check` -> ok.
- Taskboard-MCP Toolliste: manuell `tools/list` -> `taskboard_dispatch_task` vorhanden.
- QMD CLI: `qmd status` -> gesund.
- QMD MCP: Client-Smoke -> Toolliste vorhanden.
- QMD Search: `qmd search "OpenClaw autonomy" -c vault --limit 3` -> Treffer.
- Worker-Reconciler: `node scripts/worker-reconciler.mjs --dry-run` -> `proposedActions=0`.
- Auto-Pickup Gate: letzte Zyklen `GATE_MATRIX ... proof_green=pass`.

## Einschränkungen

- Diese Codex-Sandbox kann keine lokalen Listener starten (`listen EPERM`) und keine stabilen localhost-Curls gegen MC machen. Daher wurde HTTP-MCP nicht live gebunden, sondern per Syntax/systemd-Verify plus stdio-Protokoll-Smoke validiert.
- Bestehende Atlas-Discord-Sessions reloaden MCP-Server nicht automatisch. Der Code ist repariert, aber die alte Session kann weiterhin `Not connected` zeigen, bis die Toolbridge/Gateway-Session sauber rotiert oder reloadet.
- Kein Gateway-/Service-Restart wurde in diesem Lauf ausgefuehrt.

## Naechster sicherer Operator-Schritt

1. Atlas-Discord Session sauber rotieren oder Gateway ueber den vorhandenen Safe-Path reloaden.
2. Danach in Atlas pruefen:
   - `taskboard__taskboard_stats`
   - `taskboard__taskboard_list_tasks`
   - `qmd__status`
   - `qmd__search`
   - Toolliste enthaelt `taskboard__taskboard_dispatch_task`.
3. Erst wenn diese Tools verbunden sind, den naechsten Autonomie-Sprint starten.

## Status

`yellow`: Code-/Config-Fixes sind gesetzt und lokal validiert. Das Live-Gate bleibt gelb, bis eine frische Atlas-Toolbridge-Session die Tools tatsaechlich wieder verbunden sieht.
