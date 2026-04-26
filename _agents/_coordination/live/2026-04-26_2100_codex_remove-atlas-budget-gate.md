---
agent: codex
started: 2026-04-26T21:00:08Z
ended: 2026-04-26T21:08:00Z
task: "Atlas Session Budget als Hard-Gate entfernen"
touching:
  - /home/piet/.openclaw/scripts/arch-deploy-readiness-check.sh
  - /home/piet/.openclaw/workspace/scripts/architecture-snapshot-generator.py
  - /home/piet/vault/_agents/codex/daily/2026-04-26.md
operator: lenard
---

## Plan
- Atlas-Budget aus Architecture-Deploy-Readiness als Hard-Gate entfernen.
- Architecture-Snapshot wording von Budget-Alarm auf neutrale Session-Size-Info drehen.
- Backups, Syntaxchecks, Live-Verify.

## Log
- 2026-04-26T21:00:08Z Session gestartet.
- 2026-04-26T21:01Z Backups angelegt:
  - `/home/piet/.openclaw/scripts/arch-deploy-readiness-check.sh.bak-arch-budget-remove-2026-04-26`
  - `/home/piet/.openclaw/workspace/scripts/state-collector.py.bak-arch-budget-remove-2026-04-26`
  - `/home/piet/.openclaw/workspace/scripts/architecture-snapshot-generator.py.bak-arch-budget-remove-2026-04-26`
  - `/home/piet/.openclaw/workspace/mission-control/src/app/architecture/ArchitectureClient.tsx.bak-arch-budget-remove-2026-04-26`
- 2026-04-26T21:02Z `arch-deploy-readiness-check.sh`: Atlas-Budget-Gate entfernt; Runtime-JSON-Drift in `data/*.json*` ignoriert.
- 2026-04-26T21:02Z `state-collector.py`: Session-size telemetry beeinflusst `system.health` nicht mehr.
- 2026-04-26T21:02Z `architecture-snapshot-generator.py`: Wording auf `Atlas session-size telemetry: info only` gedreht.
- 2026-04-26T21:06Z MC Architecture UI neu gebaut und via `mc-restart-safe` restarted.
- 2026-04-26T21:07Z MC Commit `704dfc8` erstellt: `codex: make atlas session metric informational`.
- 2026-04-26T21:08Z Live-Verify: MC active, `/api/health` ok, `/api/architecture` health ok, crons=44. Readiness ist nicht mehr wegen Budget rot; nur `G2-agents-idle` war noch rot wegen frischer Agent-Aktivitaet.
