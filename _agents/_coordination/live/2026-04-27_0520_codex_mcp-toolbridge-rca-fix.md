---
agent: codex
started: 2026-04-27T05:20:11Z
ended: 2026-04-27T05:28:59Z
task: "MCP/Toolbridge RCA und nachhaltiger Minimalfix"
touching:
  - /home/piet/.openclaw/scripts/mcp-taskboard-reaper.sh
  - /home/piet/.openclaw/openclaw.json
  - /home/piet/.openclaw/mcp-servers/taskboard/
  - /home/piet/vault/_agents/codex/plans/
  - /home/piet/vault/_agents/codex/daily/
operator: lenard
---

## Plan
- MCP/Toolbridge Ist-Zustand gegen Gateway-/Session-/MCP-Logs analysieren.
- Rootcause-Kette belegen: Reaper vs. MCP-Transport vs. bestehende Session-Bindings.
- Minimalen dauerhaften Fix nur anwenden, wenn reversibel und lokal begrenzt.
- Gates: Script/Config-Validation, Board/Worker proof, Toolbridge-Recovery-Entscheidung.

## Log
- 2026-04-27T05:20:11Z Session gestartet; Coordination geprueft.
- 2026-04-27T05:22Z Rootcause belegt: Reaper killte Taskboard-MCP-Prozesse; danach Atlas-Discord `taskboard__... Not connected`.
- 2026-04-27T05:24Z Taskboard-MCP Surface Drift belegt: `taskboard_dispatch_task` war allowlisted, aber nicht im Server implementiert.
- 2026-04-27T05:25Z Fixes angewendet: Dispatch-Tool, Ingress-Header, stdio Keepalive, HTTP-Transport-Env in taskboard systemd Unit.
- 2026-04-27T05:28Z Gates: `node --check`, manuelles MCP `tools/list`, QMD Client-Smoke, QMD Search, config validate, worker-reconciler dry-run, auto-pickup gate ok.
- Report: /home/piet/vault/_agents/codex/plans/2026-04-27_mcp-toolbridge-rca-fix-report.md
