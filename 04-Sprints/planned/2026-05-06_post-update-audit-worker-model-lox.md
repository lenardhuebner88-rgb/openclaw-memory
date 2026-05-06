# Post-Update Audit Sprint — Worker + Model LOX Review

Status: planned
Date: 2026-05-06
Owner: Atlas
Trigger: OpenClaw 2026.5.4 update completed; live gates green; Mission Control degraded only due to known T15 shadow/tool-result smoke.
Reference: [[../03-Projects/reports/2026-05-06_openclaw-2026-5-4-update-execution-report|OpenClaw 2026.5.4 Update Execution Report]]

## Objective

Run a structured post-update audit to verify that the updated OpenClaw runtime transitions cleanly into normal operations, with specific focus on LOX-class faults in:

- Worker lifecycle and pickup/reconciler behavior
- Mission Control task/worker state consistency
- Model configuration, model routing, cron model references, and timeout budgets
- Small operational edge cases that could create delayed post-update failures

Working definition for this sprint: LOX = logic, orchestration, and cross-system consistency faults. If the operator uses LOX as a narrower term, update this definition before dispatch.

## Current Baseline

From the update report:

- OpenClaw package updated from `2026.5.3-1` to `2026.5.4`.
- Gateway app active on `2026.5.4`.
- Gateway `/health`: ok/live.
- Mission Control board issueCount: `0`.
- Dispatch consistencyIssues: `0`.
- Worker reconciler proof: ok, no issues.
- Pickup proof: ok, no findings.
- Model validation: 57 refs valid; 11 enabled cron jobs valid.
- Known warning: `nightly-self-improvement` timeout budget >600s.
- Known remaining blocker: T15 shadow/tool-result smoke still unresolved; MC degraded from known stale/open task only.

## Sprint Rules

- Audit-first. No config edits, cron edits, restarts, rollbacks, task mass-closes, or destructive cleanup without explicit Atlas/operator approval.
- Every finding must include evidence path, command/API/source, observed behavior, expected behavior, severity, and proposed next action.
- Do not infer health from old reports; re-check live state during each task.
- If Mission Control API is unavailable, switch to degraded read mode using live state files and mark confidence accordingly.
- T15 is in-scope only as a focused smoke/proof dependency; do not close it unless the smoke passes and Atlas approves closure path.
- Model secrets/tokens are out of scope. Do not print, inspect, rotate, or edit secrets.

## Workstreams

### T1 — Forge: Worker Runtime LOX Audit

Owner: Forge (`sre-expert`)
Priority: P1
Mode: read-only audit unless approved

Scope:
- Verify live Gateway, MC, worker reconciler, pickup, and worker-run state after update.
- Check worker lifecycle transitions: queued -> claimed/running -> terminal receipt.
- Inspect for stale locks, terminal-task pickups, missing receipts, inconsistent `lastReportedStatus`, zombie worker runs, duplicate session locks, and R50 violations.
- Compare MC API truth against live data files only if needed.
- Include focused T15 readiness check: confirm whether 2026.5.4 exposes required tool-result summary/persistence behavior for the pending smoke.

Evidence gates:
- `GET /api/health`
- `GET /api/ops/worker-reconciler-proof?limit=20`
- `GET /api/ops/pickup-proof?limit=20`
- relevant `worker-runs.json` / task detail evidence if API proof indicates issues
- package/runtime version proof

DoD:
- Report lists PASS/WARN/FAIL for each worker subsystem.
- Any LOX finding has exact evidence and a bounded remediation proposal.
- T15 next action is clearly stated: smoke-ready, blocked, or needs implementation follow-up.

Anti-scope:
- No restarts, no direct data edits, no task closure, no config edits.

### T2 — Lens: Model Configuration + Cost/Timeout Audit

Owner: Lens (`efficiency-auditor`)
Priority: P1
Mode: read-only audit

Scope:
- Audit active model configuration after update: agent defaults, per-agent routes, cron jobs, validation warnings, fallback behavior, and cost/timeout fit.
- Verify `validate-models` result live, not only from the report.
- Inspect the known `nightly-self-improvement` >600s timeout warning and classify: accepted exception, config drift, or needs follow-up.
- Check for expensive model routing where cheaper lanes are sufficient, but do not change routing.
- Check for invalid/stale provider aliases, provider/model mismatches, and cron/agent model references that could fail delayed execution.

Evidence gates:
- active config read/validation proof
- model validation output
- cron/model reference list
- timeout budget comparison against current runtime policy

DoD:
- Report lists PASS/WARN/FAIL for model refs, cron refs, agent defaults, timeout budgets, and cost-risk hotspots.
- Produces concrete recommendations with estimated risk/cost impact.
- Flags anything requiring operator approval separately.

Anti-scope:
- No config writes, no model switching, no secret inspection.

### T3 — Spark: Lightweight Edge-Case / UX-Operational Smoke Audit

Owner: Spark (`spark`)
Priority: P2
Mode: bounded read-only + harmless smoke where safe

Scope:
- Look for small post-update rough edges that Forge/Lens may not catch: CLI/status inconsistencies, confusing degraded messages, stale report references, operator-facing wording, obvious doc drift, missed handoff links.
- Run only harmless checks: status reads, route reads, docs/report consistency checks.
- Validate that the operator can understand the current state: “update done, gates green, only T15 degraded.”

Evidence gates:
- `openclaw status` or equivalent live status read
- report/Operational State consistency check
- MC health wording check if available

DoD:
- Short report with top 3 operator-impact issues or “no issues found”.
- Each issue has suggested owner: Forge, Lens, Pixel, Atlas, or no action.

Anti-scope:
- No implementation, no UI changes, no restarts, no edits unless Atlas explicitly converts a finding into a task.

### T4 — Atlas: Synthesis + Go/No-Go Transition Decision

Owner: Atlas
Priority: P1
Depends on: T1, T2, T3

Scope:
- Merge findings into one post-update audit report.
- Decide operational state: GREEN, GREEN-with-known-T15, WATCH, or BLOCKED.
- Create follow-up tasks only for confirmed findings.
- If all clear except T15, propose T15 smoke execution as the next narrow sprint step.

DoD:
- Final report written to Vault.
- Operational State updated with audit outcome.
- Mission Control tasks, if created, have clear DoD/anti-scope and are verified after creation.

## Dispatch Plan

1. Atlas creates/updates Mission Control parent sprint task: `S-POST-UPDATE-AUDIT-2026-05-06`.
2. Dispatch T1 to Forge, T2 to Lens, T3 to Spark in parallel after duplicate-task scan.
3. Wait for receipts.
4. Atlas synthesizes and recommends next action.
5. Only after synthesis: decide whether to execute T15 smoke or remediation tasks.

## Acceptance Criteria

The post-update transition is clean if:

- Gateway and MC live gates remain stable.
- Worker/pickup proofs remain clean or findings are bounded and non-regressive.
- No unknown terminal-task pickup, missing receipt, zombie worker, duplicate lock, or dispatch consistency issue is found.
- Model validation remains valid.
- Known timeout/model warnings are classified and accepted or converted into follow-up tasks.
- T15 remains the only known degraded item, or a clear remediation path exists for new findings.

## Proposed Final Output

Vault report path:
`/home/piet/vault/03-Projects/reports/2026-05-06_post-update-audit-worker-model-lox-report.md`

Operational State update:
- Sprint planned/dispatched/completed state
- Summary of worker audit
- Summary of model audit
- Summary of Spark smoke audit
- Transition decision
