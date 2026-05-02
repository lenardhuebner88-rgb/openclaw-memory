# Atlas Autonomy Policy Matrix v1

Stand: 2026-05-02  
Owner: Forge (Draft), Review: Atlas/Operator

## Purpose
Translate operator intent (“fast alles außer sudo und große Modelländerungen”) into enforceable autonomy classes.

## Source Constraints (authoritative)
- HEARTBEAT hard stops: no unauthorized cron/gateway/restart/model-routing mutations; stop on missing evidence, terminal rerun, ambiguous lock.
- AGENTS hard rules: board-first, verify-after-write, dispatch semantics, receipt discipline, R50 lock authority, no blind redispatch/destructive cleanup.
- Existing autonomy ladder: preview → proposal → one bounded dispatch → wait receipt → follow-up preview.

## Policy Classes

### A) Allowed autonomous (no operator approval)
- Read-only analysis/triage/research with live proof.
- P2/P3 bounded verification/doc/cleanup tasks where anti-scope excludes privileged or control-plane mutations.
- Board hygiene updates that are reversible and proof-backed.

Required gates:
- Duplicate scan
- Explicit DoD + Anti-Scope
- Low risk label
- Verify-after-write proof path

### B) Allowed with bounded task + proof (no manual approval if scope clean)
- Small reversible operational changes in non-critical paths.
- Worker dispatches to Forge/Pixel/Lens/Spark/James when owner + acceptance path are explicit.

Required gates:
- Board task exists and is dispatched correctly
- Receipt contract declared
- Post-write GET/proof checks pass

### C) Requires operator approval
- Cron schedule/ownership/runtime mode changes
- Gateway/service restarts not already task-approved
- Model config/routing changes above minor task-local override
- External side effects with irreversible impact

### D) Deny / hard stop
- Any sudo escalation
- Secrets/auth/token material mutation or exfil paths
- Terminal task rerun/redispatch
- Live lock conflict retries (R50)
- Missing evidence path for claimed mutation
- Unauthorized fanout/mass close/destructive cleanup

## “Major model change” definition (v1)
Class as major if any is true:
1. Default model change for Atlas/main or global default lane.
2. Provider routing/fallback policy change affecting multiple jobs/agents.
3. Budget-impacting premium-lane switch at config scope.
4. Any change to model-router policy used by multiple runtime agents.

Not major (still tracked):
- Explicit per-task payload model for one bounded cron job.
- Temporary one-run override inside a single approved task.

## Boundary specifics
- **sudo**: always deny.
- **secrets/auth**: requires operator approval unless strictly read-only metadata proof.
- **external destructive actions** (deletes, account changes, irreversible writes): require approval.
- **cron/gateway/restart/model routing**: require approved task + preflight gate pass; otherwise deny.

## Decision Matrix (summary)
| Action type | Class | Decision |
|---|---|---|
| Read-only live proof | A | allow |
| P2 bounded cleanup w/ DoD+proof | B | allow |
| Cron mutation without approved task | D | deny |
| Cron mutation with approved task + bounded scope | C | require-approval |
| sudo command | D | deny |
| Default model/provider change | C/D | require-approval or deny |
| Terminal-task redispatch | D | deny |
| Live lock conflict retry | D | deny |
| Missing receipt/proof path | D | deny |

## Reason Codes (v1)
- `OK_LOW_RISK_BOUNDED`
- `OK_READONLY_PROOFED`
- `NEEDS_APPROVAL_CRON_MUTATION`
- `NEEDS_APPROVAL_GATEWAY_RESTART`
- `NEEDS_APPROVAL_MODEL_MAJOR`
- `DENY_SUDO`
- `DENY_TERMINAL_RERUN`
- `DENY_LOCK_CONFLICT_R50`
- `DENY_MISSING_EVIDENCE`
- `DENY_UNAUTHORIZED_FANOUT`
- `DENY_SECRET_AUTH_MUTATION`

## Non-goals (v1)
- No autonomy expansion rollout in this doc.
- No implementation changes to gateway/cron/model routing here.
- No auto-resolution of ambiguous policy conflicts.

## Phase-1 implementation backlog
1. Add preflight evaluator that returns `allow|require-approval|deny` with reason code.
2. Add policy fixtures for hard-stop scenarios.
3. Enforce mandatory evidence fields before result receipts.
4. Add audit log event for every autonomy decision.
5. Add test harness for E2E acceptance set.
