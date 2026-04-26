---
agent: codex
started: 2026-04-26T21:33:42Z
ended: 2026-04-26T21:36:57Z
task: "Atlas QMD MCP Binding pruefen und fixen"
touching:
  - /home/piet/.openclaw/openclaw.json
  - /home/piet/.openclaw/agents/main/
  - /home/piet/vault/_agents/codex/daily/2026-04-26.md
operator: lenard
---

## Plan
- Atlas/main Session-Toolliste gegen QMD-Config pruefen.
- QMD Host-Service nicht erneut als kaputt behandeln, sondern Binding suchen.
- Minimalen Config-/Runtime-Fix nur bei klarer Evidenz anwenden.
- Gate: Atlas bekommt qmd__status/qmd__search wieder in der Toolliste oder klarer Restart-Hinweis.

## Log
- 2026-04-26T21:33:42Z Session gestartet; keine echte live Coordination mit `ended: null` Overlap gefunden.
- 2026-04-26T21:34Z Live-Evidenz: Atlas/main Session `1b744d8a...` laeuft sichtbar auf `gpt-5.5` und hat `qmd__status/search/get/...` in der Toolliste; Tool-Injection ist also vorhanden.
- 2026-04-26T21:34Z Root Cause: Host-QMD war aktuell, aber Atlas/main verwendet eigenen Agent-QMD-Index unter `/home/piet/.openclaw/agents/main/qmd/xdg-cache/qmd/index.sqlite`; dieser war 20h alt und `qmd search "adfc0596"` fand nichts.
- 2026-04-26T21:35Z Minimalfix ausgefuehrt: `qmd update` mit `XDG_CONFIG_HOME=/home/piet/.openclaw/agents/main/qmd/xdg-config` und `XDG_CACHE_HOME=/home/piet/.openclaw/agents/main/qmd/xdg-cache`.
- 2026-04-26T21:35Z Verify gruen: Agent-QMD `qmd search "adfc0596"` findet aktuelle Vault-/Working-Context-Treffer; `qmd status` zeigt `Updated: 1m ago`, vault 654 Dateien, workspace 479 Dateien, mc-src 9 Dateien.
- 2026-04-26T21:36Z Dauerhafte Ursache bleibt: bestehender `qmd-update` Cron aktualisiert laut Registry den globalen Index ohne Agent-XDG; nicht den Atlas/main-Agent-Index. Empfehlung: naechster kleiner Sprint fuer einheitliche QMD-Index-Topologie (globaler Index fuer MCP oder expliziter agent-qmd-refresh mit Lock).
- 2026-04-26T21:36Z Hinweis: aktuelle Codex-Sandbox kann Host-`systemctl`, `ss` und localhost-Ports nicht zuverlaessig pruefen; `mc-watchdog.log` zeigt aber zuletzt wiederholt `OK healthy` bis 21:34Z.
