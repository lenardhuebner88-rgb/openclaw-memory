# Atlas Clean Sprint Trigger Template

Purpose: Let Lenard start a clean, gated, multi-agent sprint with one short message while Atlas expands missing details safely.

## Minimal Trigger
```text
Starte einen Sprint mit Fokus auf: <fokus>. Autonomie: <niedrig|mittel|full>.
```

Example:
```text
Starte einen Sprint mit Fokus auf: UI Verbesserungen Mission Control Board. Autonomie: full.
```

## Atlas Expansion Defaults
When the minimal trigger is used, Atlas must expand it into:
- Sprint goal
- Scope
- Anti-scope
- Priority
- Agent ownership
- Quality gates
- Autonomy guardrails
- Stop conditions
- Reporting cadence
- Final receipt/report format

## Required Sprint Plan Output
Atlas replies with a compact sprint plan before dispatch unless autonomy is `full` and all gates/anti-scope are obvious.

```text
Sprint: <name>
Goal: <1-2 lines>
Priority: P0/P1/P2/P3
Autonomy: niedrig|mittel|full

Scope:
- ...

Anti-Scope:
- ...

Agents:
- Atlas: orchestration, gates, final receipt
- Pixel: UI/frontend/browser proof when UI is involved
- Forge: backend/runtime/build/restart/security when infra/API is involved
- Lens: audit/read-only/quality/cost when validation is involved
- Spark: small bounded fixes/support tasks
- James: research only when needed

Quality Gates:
- Preflight: health + git/process/disk check
- Board: master task + child tasks verified after write
- Dispatch: status=pending-pickup + dispatchState=dispatched verified
- Heartbeats: started/checkpoint/blocked/done receipts required
- Build/Test: relevant lint/test/build gate
- Live Proof: curl/UI/screenshot/route proof as applicable
- Final: done/blocked/failed receipt with evidence

Stop Conditions:
- active Codex/build touching same repo
- red build gate
- session lock conflict
- missing receipt after timeout
- restart/config/cron/secrets/backups/destructive cleanup needed
- unclear data migration or mass board mutation
```

## Autonomy Levels

### niedrig
Atlas may read, plan, and propose. Ask before task creation, dispatch, code changes, cleanup, restart, config/cron, or Mission Control mutations.

### mittel
Atlas may run read-only checks, create/dispatch safe P2/P3 tasks, coordinate agents, do small documentation/Vault updates, and perform safe cache cleanup. Ask before restart/deploy, config/cron/secrets, backup deletion, major code changes, risky data changes, or conflicts with active Codex/build work.

### full
Atlas may run the sprint autonomously inside explicit gates: create board tasks, dispatch agents, coordinate work, perform safe P1/P2/P3 changes, run quality gates, collect receipts, create follow-ups, and report final state. Atlas still asks before restart/deploy unless explicitly included, config/cron/secrets/model routing, backup/archive deletion, mass board mutation, data migration, destructive cleanup, or Mission Control repo mutation while Codex/build is active.

## Full Autonomy Readiness Gap
True `full` requires a durable sprint heartbeat/monitor mechanism. Until that exists, `full` means `full-light`: Atlas can execute aggressively inside gates, but must manually monitor heartbeats/receipts and stop on missing evidence.

Next planned sprint: **Autonomy Full Readiness**
- Build sprint heartbeat/monitor check
- Define timeout rules
- Verify receipts and child-task progress
- Dry-run with dummy sprint
- Promote `full` from full-light to controlled full autonomy

## Minimal Clarification Rules
Atlas should not ask for missing fields unless safety is blocked. Default assumptions:
- Priority: P1 for stabilization/UI board work, P2 for enhancements
- Restart: not allowed unless stated
- Config/Cron/Secrets: not allowed unless stated
- Backups/Archives: not allowed unless stated
- Codex active in same area: avoid repo mutations, continue audit/orchestration only
