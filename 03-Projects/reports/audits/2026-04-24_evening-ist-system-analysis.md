# Evening IST System Analysis - 2026-04-24

## Verdict

Mission Control ist live stabil, aber noch nicht optimal schlank. Der hoechste Hebel fuer heute Abend ist nicht Worker-Rettung, sondern Payload-/Polling-Hygiene im normalen Operator-Flow.

## Live Evidence

Probe window: 2026-04-24T16:27-16:30Z.

| Area | Evidence | Decision |
|---|---|---|
| Health | `/api/health` ok, `openTasks=0`, `inProgress=0`, `pendingPickup=0` | no incident sprint |
| Worker proof | `openRuns=0`, `criticalIssues=0` | worker path currently green |
| Pickup proof | active `claimTimeouts=0`, historical `14` | monitor, do not start core worker fix first |
| Runtime-soak proof | `status=ready`, `main` only cooldown-limited | canary allowed for eligible agents |
| Reconcile proof | degraded only by recovery-ledger drift warning, `criticalFindings=0` | not blocking |
| Board snapshot live | `1023 bytes` | preferred normal UI source |
| Full `/api/tasks` | `1,854,771 bytes` | avoid in normal polling |
| API metrics `/api/tasks` | `194,725` GETs | high-volume endpoint |
| API metrics `/api/costs` | avg `1515.95ms`, last `2472.67ms` | perf hotspot |
| API metrics `/api/ops/runtime-soak-proof` | avg `2093.22ms`, last `2046.87ms` | perf hotspot |
| Memory proof | ok, `pendingEmbeddings=0` | no QMD/memory sprint tonight |
| Cost governance | warnings only; no spend/quota hard blocker | no reroute/block |

## Key Root Findings

1. `SystemPulse` still calls `/api/tasks` in a 15-second interval, while the live board snapshot is already tiny.
2. P4.1-P4.3 were completed as MC tasks, but the Vault P4 follow-up plan still says `planned`; it is now stale and should be superseded by the evening plan.
3. The remaining live P4.x draft for a metrics endpoint is useful, but should be scoped after EVE-1.
4. Worker/claim-handoff risk is real historically, but active proofs are green; do not lead tonight with core worker changes unless new failures appear.
5. Old Vault `planned/` files contain useful history but are not directly runnable as-is; most should be closed/superseded or recut into narrow modern sprints.

## Highest-Leverage Order

1. **EVE-1:** SystemPulse `/api/tasks` poll elimination.
2. **EVE-2:** Metrics endpoint for archive/success/cycle aggregates.
3. **EVE-3:** Runtime/cost proof performance cut.
4. **EVE-4:** Auto-Pickup API-unreachable / claim-handoff hardening plan, only if time remains or pickup proof degrades.

Canonical execution plan:
`/home/piet/vault/04-Sprints/planned/2026-04-24_evening-atlas-high-leverage-sprints.md`

## Backlog Usefulness Summary

Keep and recut:
- `2026-04-24_mc-audit-p4-followup-plan.md` -> superseded by evening plan.
- `646c087e...` metrics endpoint draft -> useful for EVE-2.
- `2026-04-24_heartbeat-cron-target-plan.md` -> source for future worker/heartbeat architecture.

Close/supersede soon:
- `2026-04-24_mc-orchestrated-audit-gate.md` because task `30c36874...` is done/result.
- `s-mc-alerts-dashboard-audit-2026-04-23.md` because later audit/P4 work superseded it.
- old Sprint-H/J/K/M planned docs after extracting any still-current narrow items.

Defer:
- `s-ctx-p0-2026-04-22.md`: context proof has no active critical findings.
- `s-integ-w1-2026-04-22.md`: operator/desktop integration, not a tonight runtime sprint.
- `sprint-i-mobile-polish-plan-2026-04-19.md`: too broad until payload/perf path is cleaner.
- `sprint-l-memory-kb-compilation-plan-2026-04-19.md`: memory proof is currently green.
