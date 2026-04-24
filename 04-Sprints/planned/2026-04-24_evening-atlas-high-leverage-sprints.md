# Evening Atlas High-Leverage Sprints - 2026-04-24

Status: planned
Owner: Atlas
Created: 2026-04-24T16:31Z
Source: Codex IST-System-Analyse live
Mode: Atlas orchestrates one sprint at a time; no task flood

## 1. Live IST Snapshot

Probe window: 2026-04-24T16:27-16:30Z on homeserver `/home/piet`.

| Signal | Live Value | Bewertung |
|---|---:|---|
| `/api/health` | `status=ok`, `openTasks=0`, `inProgress=0`, `pendingPickup=0` | green |
| Worker-Reconciler-Proof | `openRuns=0`, `criticalIssues=0` | green |
| Pickup-Proof | `claimTimeouts=0`, historical claim timeouts `14` | active green, history remains risk evidence |
| Runtime-Soak-Proof | `status=ready`, canary executable, `main` cooldown active | green with expected Atlas cooldown |
| Reconcile-Proof | `status=degraded`, `criticalFindings=0`, one recovery-ledger-drift warning | non-blocking warning |
| Memory-Proof | `status=ok`, `pendingEmbeddings=0`, retrieval smokes pass | green |
| Cost-Governance-Proof | no hard spend/quota blockers; OpenAI/MiniMax signals are warnings/mapping artifacts | green for work, watch quota |
| Board snapshot live | `1023 bytes`, `returnedTasks=1` | excellent |
| Board snapshot archive | `143,029 bytes`, `returnedTasks=497` | acceptable but growing |
| Full `/api/tasks` | `1,854,771 bytes`, 498 tasks | still too heavy for normal UI polling |
| API metrics `/api/tasks` | 194,725 GETs, avg 33.58ms | high request volume and huge transfer |
| API metrics `/api/costs` | avg 1515.95ms, last 2472.67ms | performance hotspot |
| API metrics `/api/ops/runtime-soak-proof` | avg 2093.22ms, last 2046.87ms | proof hotspot |

## 2. What Changed Since Earlier P4 Plan

The original `2026-04-24_mc-audit-p4-followup-plan.md` is partly stale:

- P4.1 is completed as MC task `7fe05dd7-957e-484b-b7c7-5f197581d4d4`.
  - Operational Summary now uses snapshots instead of broad `/api/tasks`.
  - Residual risk: archive snapshot is still used for success/cycle metrics.
- P4.2 is completed as MC task `23365e61-b0c8-458d-8fd9-00c58648d3be`.
  - Worker proof noise for legitimate gateway-owned runs was reduced.
- P4.3 is completed as MC tasks `3a251b73-53b2-424e-aed5-3431789d7e64` and `1357a4de-2b58-45fb-8a61-ae68bfadee64`.
  - Runtime-soak self-lock semantics were deployed and live-verified.
- Remaining live issue is not the old P4.1 broad statement, but specific consumers/perf endpoints:
  - `src/components/system-pulse.tsx` still fetches `/api/tasks` every 15s.
  - `/api/costs` and `/api/ops/runtime-soak-proof` are slow enough to become operator-flow drag.

## 2.1 Atlas Handoff Status Ledger

Atlas should treat this table as the current handoff truth for tonight. Do not re-run items marked `done` unless a live gate regresses.

### Already Done / Do Not Restart Tonight

| Item | Live/Board Evidence | Status | Atlas Action |
|---|---|---|---|
| MC Orchestrated Audit Gate | Task `30c36874-bac1-48f4-b424-61a47b151047`, report `/home/piet/vault/03-Projects/reports/audits/2026-04-24_mc-orchestrated-audit-gate-report.md` | done/result | Do not restart; use as source evidence only. |
| P4.1 Board/API-Payload initial cut | Task `7fe05dd7-957e-484b-b7c7-5f197581d4d4`, commit `f8a01ce`, result says Operational Summary moved to snapshots | done | Do not repeat broad P4.1; only address residual `SystemPulse` poll as EVE-1. |
| P4.2 Worker-proof noise reduction | Task `23365e61-b0c8-458d-8fd9-00c58648d3be`, commit `6d9ef0c` | done | Do not reopen unless Worker-Proof regresses. |
| P4.3 Runtime self-lock semantics | Tasks `3a251b73-53b2-424e-aed5-3431789d7e64` and `1357a4de-2b58-45fb-8a61-ae68bfadee64`, commits `1a5c612` plus live rebuild/restart verification | done/live-verified | Do not reopen; use live proof as acceptance baseline. |
| P5 real canaries | Latest main/frontend/specialist canaries are terminal done; pickup proof active claimTimeouts = 0 | done | No extra canary unless an implementation gate requires exactly one targeted smoke. |

### Not Done / Still Useful

| Item | Evidence | Status | Recommended Atlas Action |
|---|---|---|---|
| EVE-1 SystemPulse `/api/tasks` poll removal | Code still has `src/components/system-pulse.tsx` -> `fetch('/api/tasks')` inside 15s refresh; `/api/tasks` 1,854,771 bytes | not started | Start first tonight. |
| EVE-2 Metrics endpoint for archive/success/cycle aggregates | Draft task `646c087e-bdbe-453f-a833-aeefa4990154`; archive snapshot 143,029 bytes | draft/not done | Start only after EVE-1 is green. |
| EVE-3 Runtime/Cost proof performance cut | `/api/costs` avg ~1516ms; `/api/ops/runtime-soak-proof` avg ~2093ms | not done | Run Spark read-only RCA first; implement only smallest clear cut. |
| EVE-4 Auto-Pickup API-unreachable / claim-handoff hardening | Active proof green, but history has 14 claim timeouts and recent API-unreachable events | not done; contingency | Do not start tonight unless new worker proof/pickup degradation appears. |

### Vault Plans To Treat As Superseded/Stale

| Vault File | Current Assessment | Atlas Handling |
|---|---|---|
| `04-Sprints/planned/2026-04-24_mc-audit-p4-followup-plan.md` | stale because P4.1-P4.3 are done and residual scope changed | Supersede with this evening plan. |
| `04-Sprints/planned/2026-04-24_mc-orchestrated-audit-gate.md` | done through task `30c36874...` and report exists | Move/mark closed later; do not dispatch. |
| `04-Sprints/planned/s-mc-alerts-dashboard-audit-2026-04-23.md` | later MC audit and P4 work supersede it | Use only as historical context. |
| `04-Sprints/planned/sprint-h-board-analytics-plan-2026-04-19.md` | old analytics plan; `/api/analytics` exists and current issues are narrower | Do not run raw. |
| `04-Sprints/planned/sprint-j-cascade-postmortem-plan-2026-04-19.md` | governance lessons absorbed into later R47/R50 work | Do not run raw. |
| `04-Sprints/planned/sprint-k-infra-hardening-plan-2026-04-19.md` | partially superseded; only receipt/cron observability fragments may still matter | Recut later, not tonight. |
| `04-Sprints/planned/sprint-m-audit-integrity-scheduler-consolidation-plan-2026-04-20-v1.2.1.md` | materially superseded by recent cron/heartbeat reports and implemented scheduler work | Recut only the registry part later. |
| `04-Sprints/planned/sprint-reporting-next-action-hardening-plan-2026-04-21.md` | likely superseded by closed S-RPT work | Verify before any future use. |

### Deferred But Still Potentially Valuable

| Vault File | Why Deferred |
|---|---|
| `04-Sprints/planned/s-ctx-p0-2026-04-22.md` | Context proof has no active critical findings; output bloat remains strategic, not tonight's highest lever. |
| `04-Sprints/planned/s-infra-2026-04-22.md` | Needs recut against current worker-proof green state. |
| `04-Sprints/planned/s-integ-w1-2026-04-22.md` | Requires operator/desktop/Claude integration decisions; not a Mission Control evening stabilization sprint. |
| `04-Sprints/planned/sprint-i-mobile-polish-plan-2026-04-19.md` | Too broad until payload/performance path is cleaner. |
| `04-Sprints/planned/sprint-l-memory-kb-compilation-plan-2026-04-19.md` | Memory proof is green; not a bottleneck tonight. |

## 3. Highest-Leverage Sprints For Tonight

### EVE-1 - SystemPulse /api/tasks Poll Elimination

Owner: Forge primary, Pixel secondary sanity check
Priority: P0 for tonight
Risk: low-medium

#### Problem
`SystemPulse` still performs a full `/api/tasks` fetch every 15 seconds. With the current dataset this transfers ~1.85 MB per poll. The live board snapshot is ~1 KB and already contains status/lane counts sufficient for the visible pulse counters.

#### Evidence
- Live `/api/tasks`: `1,854,771 bytes`.
- Live `/api/board/snapshot?view=live`: `1,023 bytes`.
- Code: `/home/piet/.openclaw/workspace/mission-control/src/components/system-pulse.tsx` calls `fetch('/api/tasks')` inside `setInterval(refresh, 15000)`.
- API metrics: `/api/tasks` has `194,725` GET requests.

#### Scope
- Replace SystemPulse task-count source with `/api/board/snapshot?view=live` summary counts, or introduce a tiny read-only `/api/board/pulse` endpoint if live snapshot summary is insufficient.
- Keep cron and learnings sources unchanged unless strictly necessary.
- Preserve visible SystemPulse behavior.

#### Anti-Scope
- No broad taskboard data-layer rewrite.
- No changes to task creation/edit/admin flows.
- No archive detail payload in the pulse path.

#### Real Use Cases
- Operator opens Mission Control dashboard/taskboard and leaves it open for 10 minutes.
- SystemPulse updates without repeatedly pulling full task history.
- One live draft/open card still appears correctly in pulse counts.

#### Acceptance Gates
- `rg "fetch\(['\"]\\/api\\/tasks" src/components/system-pulse.tsx` returns no normal pulse fetch.
- `/api/board/snapshot?view=live` remains <100 KB; expected current ~1 KB.
- Normal dashboard/taskboard load does not need `/api/tasks` for SystemPulse.
- `npm run typecheck` and focused tests pass.
- Browser smoke: no client console error in dashboard/taskboard pulse area.

#### Rollback
Git revert the SystemPulse change only.

---

### EVE-2 - Metrics Endpoint For Archive/Success/Cycle Counts

Owner: Forge
Priority: P1 for tonight if EVE-1 lands cleanly
Risk: medium

#### Problem
P4.1 moved `OperationalSummary` from full `/api/tasks` to snapshots, but it still fetches `view=archive` for success/cycle metrics. Archive snapshot is far smaller than `/api/tasks`, but it grows with every terminal task and is already 143 KB.

#### Evidence
- P4.1 result reported archive snapshot as follow-up risk.
- Live `/api/board/snapshot?view=archive`: `143,029 bytes`, 497 archive tasks.
- Code: `src/components/operational-summary.tsx` fetches both live and archive snapshot.
- Existing draft task: `646c087e-bdbe-453f-a833-aeefa4990154` `[P4.x][Forge] Optionaler Metrics-Endpoint für Archive-/Success-/Cycle-Metriken prüfen`.

#### Scope
- Build or propose the smallest read-only metrics endpoint that returns only aggregate values needed by OperationalSummary:
  - statusCounts
  - recent done/failed counts
  - success rate inputs
  - cycle-time aggregate
- Then switch OperationalSummary away from archive task list if implementation remains small.

#### Anti-Scope
- No analytics product redesign.
- No full historical reporting rewrite.
- No mutation.

#### Real Use Cases
- Operator opens dashboard after weeks of accumulated terminal tasks.
- OperationalSummary remains fast without downloading hundreds/thousands of archive rows.
- Metrics stay consistent with current snapshot-derived display.

#### Acceptance Gates
- New/changed endpoint returns aggregates only, not full descriptions or task bodies.
- Payload target: <25 KB at current dataset; ideal <5 KB.
- OperationalSummary renders same visible numbers.
- Typecheck + focused route/component tests pass.

#### Rollback
Revert endpoint and OperationalSummary consumer change.

---

### EVE-3 - Runtime/Cost Proof Performance Cut

Owner: Spark audit first, Forge implementation second
Priority: P1/P2 tonight, depending on EVE-1/EVE-2 duration
Risk: medium

#### Problem
The system is green, but two read-only endpoints are slow enough to affect operator confidence and repeated audit loops:
- `/api/costs`: avg ~1516ms, last ~2473ms.
- `/api/ops/runtime-soak-proof`: avg ~2093ms, last ~2047ms.

#### Evidence
- `/api/metrics` live endpoint stats at 2026-04-24T16:29Z.
- Runtime-soak is now semantically correct after P4.3, so the next value is performance/response shape, not semantics.

#### Scope
- Spark first identifies the exact slow sub-steps and recommends one small cut.
- Forge only implements if the cut is obviously bounded:
  - cache a read-only sub-result for a short TTL, or
  - split heavy detail from lightweight summary, or
  - trim repeated expensive filesystem scans.

#### Anti-Scope
- No cost-governance policy changes.
- No canary policy rewrite.
- No hidden mutation in proof endpoints.

#### Real Use Cases
- Operator refreshes runtime proof during live worker audit.
- Atlas uses proof endpoints during orchestration without 2s latency loops.
- Cost panel remains responsive while subscription-token-plan warnings remain visible.

#### Acceptance Gates
- Endpoint response status unchanged and read-only.
- Current visible fields preserved or explicitly versioned.
- p95/last local probe shows visible improvement, target <500ms for summary endpoint or <1s for full proof.
- Tests/typecheck pass.

#### Rollback
Revert only the endpoint optimization.

---

### EVE-4 - Auto-Pickup API-Unreachable / Claim-Handoff Hardening Plan

Owner: Atlas orchestrates; Forge implements only after EVE-1/EVE-2 or tomorrow
Priority: P2 tonight, P0 if new failures appear
Risk: medium-high because core worker path

#### Problem
Active pickup is green, but logs still show fragility around API restart windows and historical claim timeouts.

#### Evidence
- Pickup-Proof active: `claimTimeouts=0`, `activeSpawnLocks=0`, `criticalFindings=0`.
- Pickup-Proof history: `historicalClaimTimeouts=14`.
- Recent events include `ERR_API <urlopen error [Errno 111] Connection refused>` at 15:01-15:02Z.
- Heartbeat/Cron audit found previous `left-over openclaw-agent` and `dispatched-no-claim` evidence.

#### Scope
- No immediate broad fix unless live proof degrades.
- Prepare exact unit/E2E test matrix:
  - API unreachable should not create noisy fatal start-limit cascades.
  - spawned worker must either claim or be cleanly accounted for.
  - historical claim-timeouts remain classified but not active blockers.

#### Anti-Scope
- No unapproved edits to Auto-Pickup core during evening UI/perf sprint.
- No restarts unless implementation explicitly requires deploy gate.

#### Acceptance Gates
- New tests before behavior change.
- Real canary only when runtime-soak says `canExecuteCanary=true` and target agent is eligible.
- Worker/Reconciler/Pickup proof remain zero critical after canary.

## 4. Recommended Tonight Sequence

1. Start **EVE-1** only. This has the clearest live evidence and highest operator-flow payoff.
2. If EVE-1 is green and deployed, start **EVE-2** using the existing draft `646c087e...` as source, or replace it with a clearer scoped task.
3. If time remains, run **EVE-3 as Spark read-only RCA first**, then decide whether Forge should implement.
4. Keep **EVE-4 as contingency/planning** unless pickup proof degrades or Atlas sees new worker failures.

Do not start all four in parallel. Tonight should be sequential, with one live implementation lane at a time.

## 5. Vault Backlog Triage

### Keep / Active For Tonight

| File / Item | Verdict | Reason |
|---|---|---|
| `04-Sprints/planned/2026-04-24_mc-audit-p4-followup-plan.md` | supersede with this evening plan | P4.1-P4.3 are done, residuals changed. |
| MC draft `646c087e...` Metrics Endpoint | keep but refine | Directly maps to EVE-2 and live evidence. |
| `03-Projects/reports/audits/2026-04-24_heartbeat-cron-target-plan.md` | keep as architecture source | EVE-4 and future worker/heartbeat hardening. |

### Close / Supersede Soon

| File | Verdict | Reason |
|---|---|---|
| `04-Sprints/planned/2026-04-24_mc-orchestrated-audit-gate.md` | mark closed or move to closed | Audit task `30c36874...` is done/result and report exists. |
| `04-Sprints/planned/s-mc-alerts-dashboard-audit-2026-04-23.md` | supersede | Covered by later MC audit + P4 follow-ups; only usable as historical evidence. |
| `04-Sprints/planned/sprint-h-board-analytics-plan-2026-04-19.md` | supersede/close after verifying `/api/analytics` current state | API exists; plan is stale and collides with later work. |
| `04-Sprints/planned/sprint-j-cascade-postmortem-plan-2026-04-19.md` | supersede | Governance lessons have been absorbed by later R47/R50 work. |
| `04-Sprints/planned/sprint-k-infra-hardening-plan-2026-04-19.md` | partially supersede | Many items done or moved; extract only unresolved receipt/cron-observability items. |
| `04-Sprints/planned/sprint-m-audit-integrity-scheduler-consolidation-plan-2026-04-20-v1.2.1.md` | supersede by current cron/heartbeat reports | Sprint-M work has been materially implemented; remaining cron registry can become a small new sprint. |
| `04-Sprints/planned/sprint-reporting-next-action-hardening-plan-2026-04-21.md` | likely superseded by S-RPT closed; verify once | Do not run as-is tonight. |

### Defer To Next Days

| File | Verdict | Reason |
|---|---|---|
| `04-Sprints/planned/s-ctx-p0-2026-04-22.md` | day+1/day+2 | Context proof active critical is 0, but historical output bloat remains strategic. |
| `04-Sprints/planned/s-infra-2026-04-22.md` | day+2 after worker proof remains green | Contains old receipt lifecycle overlap; should be recut, not run raw. |
| `04-Sprints/planned/s-integ-w1-2026-04-22.md` | operator-driven, not tonight | Requires desktop/Claude integration decisions and SSHFS tests. |
| `04-Sprints/planned/sprint-i-mobile-polish-plan-2026-04-19.md` | day+3+ | Valuable but broad; run after payload/perf stabilizes. |
| `04-Sprints/planned/sprint-l-memory-kb-compilation-plan-2026-04-19.md` | later | Memory proof is green; not tonight's bottleneck. |

## 6. Next Days Plan

### Day 1: Finish Payload/Perf Hygiene
- EVE-1 SystemPulse full-task poll removal.
- EVE-2 Metrics endpoint for archive/success/cycle aggregates.
- Verify `/api/tasks` request rate drops in `/api/metrics` after normal use.

### Day 2: Worker/Heartbeat Core Hardening
- Recut Auto-Pickup API-unreachable + claim-handoff hardening from EVE-4.
- Build tests before behavior changes.
- Add Defense-Job Registry from heartbeat cron target plan Stage 1.

### Day 3: Backlog Hygiene + Mobile/UI Narrow Polish
- Move stale planned files to closed/superseded with one-line rationale.
- Recut mobile polish into one narrow route sanity sprint rather than broad Sprint-I.
- Keep context-output caps as monitoring unless `context-budget-proof` active findings reappear.

## 7. Atlas Start Prompt

```text
Atlas, bitte starte heute Abend dediziert Sprint EVE-1 aus dem neuen Codex-Plan:

Lies zuerst:
/home/piet/vault/04-Sprints/planned/2026-04-24_evening-atlas-high-leverage-sprints.md
/home/piet/vault/03-Projects/reports/audits/2026-04-24_evening-ist-system-analysis.md

Ziel Sprint EVE-1:
SystemPulse darf im normalen Pulse-/Dashboard-Refresh nicht mehr alle 15 Sekunden das volle /api/tasks Payload ziehen. Live-Evidence: /api/tasks aktuell 1,854,771 bytes; /api/board/snapshot?view=live aktuell 1,023 bytes; src/components/system-pulse.tsx nutzt fetch('/api/tasks') in einem 15s interval.

Arbeitsmodus:
- Erst Live-Baseline erneut prüfen: /api/health, /api/ops/worker-reconciler-proof?limit=20, /api/board/snapshot?view=live, /api/metrics.
- Nur EVE-1 umsetzen. Keine parallelen EVE-2/EVE-3/EVE-4 Tasks starten.
- Kein breiter Data-Layer-Rewrite, keine QMD-Arbeit, keine Provider-/Model-Routing-Änderung.
- Normalen SystemPulse-Task-Zähler auf Snapshot Summary oder eine kleinste read-only Pulse/Summary Route umstellen.
- /api/tasks bleibt Detail/Admin-Endpunkt; nur normaler Pulse-Poll soll entkoppelt werden.

Quality Gates:
- rg "fetch\\(['\"]\\/api\\/tasks" src/components/system-pulse.tsx zeigt keinen normalen Pulse-Fetch mehr.
- Payload-Probe: /api/board/snapshot?view=live bleibt <100 KB.
- npm run typecheck.
- fokussierter Test oder Browser-Smoke: Dashboard/Taskboard laden, Pulse sichtbar, keine client-side exception.
- Nach Deploy/Restart falls noetig: /api/health ok, Worker-Proof criticalIssues=0/openRuns=0.

Return Format:
EXECUTION_STATUS
RESULT_SUMMARY
CHANGED_PATHS
TESTS_AND_GATES
LIVE_PROBES
OPEN_RISKS
NEXT_RECOMMENDED_STEP
```
