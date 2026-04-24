---
agent: codex
started: 2026-04-24T12:48:02Z
ended: null
task: "Auto-pickup/proof E2E hardening"
touching:
  - /home/piet/.openclaw/scripts/auto-pickup.py
  - /home/piet/.openclaw/scripts/tests/test_auto_pickup.py
  - /home/piet/.openclaw/workspace/mission-control/src/lib/pickup-proof.ts
  - /home/piet/.openclaw/workspace/mission-control/tests/pickup-proof.test.ts
  - /home/piet/.openclaw/workspace/mission-control/scripts/runtime-soak-canary.mjs
  - /home/piet/.openclaw/workspace/mission-control/scripts/runtime-soak-e2e-audit.mjs
  - /home/piet/.openclaw/workspace/mission-control/tests/runtime-soak-e2e-audit-script.test.ts
  - /home/piet/vault/_agents/codex/plans/2026-04-24_auto-pickup-proof-e2e-hardening.md
  - /home/piet/vault/04-Sprints/planned/
  - /home/piet/vault/_agents/codex/daily/2026-04-24.md
operator: lenard
---
## Plan
- P1 Auto-Pickup-Crash mit Regressionstest beheben.
- P2 Pickup-Proof historische und aktive Claim-Timeouts trennen.
- P3 E2E-Orchestrated-Audit-Harness fuer Main + Worker bauen.
- Live-Audit ausfuehren, Follow-up-Sprint dokumentieren, Gates abschliessen.

## Log
- 2026-04-24T12:48:02Z Session gestartet; keine offene Coordination mit `ended: null` gefunden.
- 2026-04-24T12:49:06Z P1 abgeschlossen: orphan-lock Regressionstest fuer `cleanup_unclaimed_spawn_locks`; Python compile + Auto-Pickup Tests 14/14 passed; live oneshot success.
- 2026-04-24T12:50:10Z P2 lokal abgeschlossen: Pickup-Proof unterscheidet aktive/historische/total Claim-Timeouts; Vitest pickup-proof 5/5 und typecheck passed.
- 2026-04-24T12:52:03Z P3 lokal abgeschlossen: `runtime-soak-e2e-audit.mjs` + Script-Tests; targeted Vitest 17/17 passed. Dry-run plant Pixel ja, Main noch Cooldown.
