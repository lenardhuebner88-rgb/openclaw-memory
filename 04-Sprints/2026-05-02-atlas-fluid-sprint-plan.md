# 2026-05-02 Atlas Fluid Sprint Plan

Goal: Atlas replies quickly, exactly once, with no cron/heartbeat bootstrap pollution and no session rotation during normal Discord use.

Phases:

1. Cron audit, frequency reduction, routing migration plan.
2. Explicit routing policy for alerts channel `1491148986109661334`.
3. Atlas skills slim and bootstrap reduction.
4. `system-bot` agent and migration of system-owned cron triggers.
5. Gateway CPU saturation RCA and fix.

Hard gates:

- Acquire sprint lock before work.
- Run `openclaw doctor` before config changes.
- Run `pre-flight-sprint-dispatch.sh` before each mutation step.
- Backup every changed config/script file first.
- Stop or mark phase `PARTIAL/BLOCKED` on schema errors, service crash, or failed validation.
- Do not disable defense crons, memory orchestrator, auto-pickup, R47/R49/R50 validators.
- Keep 8-tier cron architecture.
- Final live test requires simulated user inbound through Mission Control API for eight Atlas messages.

