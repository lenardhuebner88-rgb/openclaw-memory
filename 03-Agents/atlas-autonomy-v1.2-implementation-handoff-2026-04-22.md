# Atlas Autonomy v1.2 Implementation Handoff

## Scope

Implement Phase 1 from `/home/piet/vault/03-Agents/atlas-autonomy-phase1-phase2-plan-2026-04-22-v1.2.md`.

Phase 2 is not a full build target in the first pass. Only keep its prerequisites intact:

- JSONL records carry `schema_version='v1'`
- data model stays additive
- no design choice in Phase 1 should block later `sprintOutcome` primacy

## Non-Negotiables

- commander-bot is debug-only and must not be referenced in autonomy orchestration
- Mission Control remains the control plane
- runner stays one-shot and is driven by `m7-plan-runner.timer`
- config path is `/home/piet/.openclaw/config/plan-runner.env`
- no writes to `openclaw.json`
- R48 exempt must be implemented before pilot rollout

## Concrete Build Order

1. `plan_schema.py`:
   - add `schema_version`, `autonomy_enabled`
   - add step fields `next_action_type`, `approval_mode`, `risk_level`, `allowed_agents`
   - keep runtime fields out of YAML
2. `test-mini.yaml`:
   - migrate to v1
   - mark one pilot plan with `autonomy_enabled: true`
3. Mission Control data model:
   - add `atlas-autonomy` autoSource
   - add `planId`, `sourceStepId`, `decisionKey`, `approvalMode`, `riskLevel`
   - add approval/reject audit fields
   - update store normalization and all write routes
   - add list filters needed by runner/CLI/UI
4. Approval flow:
   - `POST /api/tasks/<id>/autonomy-approve`
   - `POST /api/tasks/<id>/autonomy-reject`
   - `plan-cli pending-approvals|approve|reject`
5. Runner:
   - fail-closed config parse
   - version gate via OpenClaw CLI version
   - `flock /tmp/plan-runner.lock`
   - state machine for pending/in-progress steps
   - valid Mission Control draft rendering
   - JSONL logs plus dedupe store
6. R48:
   - exempt only tasks with:
     - `autoSource='atlas-autonomy'`
     - `lockReason='atlas-autonomy-awaiting-approval'`
     - `operatorLock=true`
   - keep 168h max wait
7. Scheduler:
   - install `m7-plan-runner.service` and `m7-plan-runner.timer`
   - start in dry-run mode first

## Acceptance

- Autonomy draft persists with `autoSource='atlas-autonomy'`
- draft contains valid execution-contract text for MC
- approve moves draft to `pending-pickup`
- reject moves draft to `canceled` with audit trail
- duplicate parent completion does not create a second draft
- R48 does not close waiting autonomy drafts inside 168h
- kill-switch and version gate stop writes cleanly
