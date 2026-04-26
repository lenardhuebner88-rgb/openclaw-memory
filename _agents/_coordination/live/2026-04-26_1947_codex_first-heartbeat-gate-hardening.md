---
agent: codex
started: 2026-04-26T19:47:44Z
ended: 2026-04-26T19:50Z
task: "first_heartbeat_gate acceptedAt + fresh lastHeartbeatAt semantisch haerten"
touching:
  - /home/piet/.openclaw/scripts/auto-pickup.py
  - /home/piet/.openclaw/workspace/mission-control/tests/auto-pickup-claimed-no-heartbeat-regression.test.ts
  - /home/piet/vault/_agents/codex/plans/
  - /home/piet/vault/_agents/codex/daily/2026-04-26.md
operator: lenard
---

## Plan
- `first_heartbeat_metrics()` so anpassen, dass `acceptedAt` + frischer `lastHeartbeatAt` als ok zaehlt.
- Regressionstest ergaenzen.
- Python/Vitest/Live-Gates pruefen.

## Log
- 2026-04-26T19:47:44Z Session gestartet.
- 2026-04-26T19:48Z `first_heartbeat_metrics()` angepasst: `acceptedAt` + frisches `lastHeartbeatAt` zaehlt als ok.
- 2026-04-26T19:49Z py_compile, direkter Python-Smoke, Vitest und Live-Gates gruen.
- 2026-04-26T19:49Z Report geschrieben: /home/piet/vault/_agents/codex/plans/2026-04-26_first-heartbeat-gate-hardening.md.
