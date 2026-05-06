# Operational State

## Current
- 2026-05-05 19:32 CEST: Sprint S-Context geplant (Session/Context Management next level).
- Sprint Plan: vault/04-Sprints/planned/2026-05-05_s-context-next-level.md
- Tasks dispatched (P0/P1):
  - T1 (Forge): a633ff1e — QMD OnSessionStart Sync
  - T2 (Atlas): b0da1870 — Bootstrap 16KB Budget
  - T3 (Forge): 4ed8145f — L2 Auto-Sweep
  - T4 (Forge): 91756557 — maxActiveTranscriptBytes 3MB→1MB
- MC/Gateway: healthy (baseline unchanged)

## T10 Session Lifecycle Policy — 2026-05-05 20:30 CEST

Status: draft accepted for operations docs; no runtime/config change made.

Decision matrix:
- NORMAL: context <35%, cacheRead <=250k, totalTokens <=300k, idle irrelevant, no timeout trend -> continue normal work.
- WATCH: context >=35% OR cacheRead >250k OR totalTokens >300k -> keep session; reduce tool-output verbosity, checkpoint concise state, avoid heavy history reads.
- COMPACT-CANDIDATE: context >=50% OR cacheRead >500k OR totalTokens >500k OR cacheRead spike repeats twice within 30min -> prefer explicit checkpoint + measured compaction pilot; no forced compaction during active operator work.
- ROTATE-CANDIDATE: context >=65% OR totalTokens >900k OR cacheRead >900k AND idle >10min AND no active task/operator lock -> write handoff, then rotate only the scoped session.
- STOP/REPORT: repeated timeout/abort (2 in 30min or 3/day), ambiguous session lock, active lock conflict, or compaction causes continuity loss -> stop and report evidence before further lifecycle action.

No-go rules:
- Never rotate active Discord/operator work.
- Never rotate while a task has active workerSessionId/operatorLock/session lock or while a response/run is active.
- Never use rotation as a fix for model, gateway, cron, config, or board-health incidents.
- Never delete sessions/transcripts/checkpoints as part of lifecycle policy without separate explicit approval.

T4 interaction:
- T4 maxActiveTranscriptBytes pilot remains HOLD until this matrix is used as baseline.
- If T4 runs, use 1MB pilot only with before/after metrics: context %, cacheRead, totalTokens, compaction count, timeout/abort count, and operator continuity notes.
- Roll back if compaction frequency, token use, or answer continuity worsens.

Current evaluation:
- Atlas Discord session `agent:main:discord:channel:1486480128576983070`: 96k/272k = 35%, compactions=0, cache currently 95k cached; last visible run done, no abort.
- Policy state: WATCH. No compact, no rotate. Keep session, checkpoint if work continues, reassess after idle >10min or if cache/token spike repeats.

## OpenClaw 2026.5.4 Update Plan — 2026-05-06 07:00 CEST

Documented controlled update plan, not executed yet.
Plan: [[../03-Projects/plans/2026-05-06_openclaw-2026-5-4-controlled-update-plan|OpenClaw 2026.5.4 Controlled Update Plan]]
Key gates: backup config/systemd/state/package, dry-run, config guard, Gateway/MC health, worker/pickup proofs, update via `openclaw update --tag 2026.5.4 --yes`, post-check active version + tool-result-shadow marker, rollback via `openclaw update --tag 2026.5.3-1 --yes` if needed.

## OpenClaw 2026.5.4 Update Executed — 2026-05-06 07:50 CEST

Update executed via transient systemd user unit because direct updater from Discord/Gateway process tree is intentionally blocked.
Backup: /home/piet/.openclaw/backups/openclaw-update-2026-5-4-20260506T052705Z
Unit: openclaw-update-2026-5-4-20260506T054538Z.service
Result nuance: package update/doctor/plugin sync succeeded (2026.5.3-1 -> 2026.5.4), updater exited non-zero during final Gateway health wait because restarted Gateway was already running on port 18789. Live post-gates passed, so no rollback performed.
Post-gates: openclaw status up to date, Gateway app 2026.5.4 active PID 2572457, Gateway /health ok/live, MC board issueCount 0, dispatch consistencyIssues 0, worker proof ok issues 0, pickup proof ok findings 0. MC remains degraded only due to known blocked T15 stale/open task. validate-models: 57 refs valid, 11 enabled cron jobs valid, one existing nightly-self-improvement timeout warning.
T15 note: active package has tool-result persistence/summary code, but literal grep for `tool-result-shadow` marker returned no match; T15 smoke still required before unblocking/closing.

## OpenClaw 2026.5.4 Update Report — 2026-05-06 07:51 CEST

Final execution report written: [[../03-Projects/reports/2026-05-06_openclaw-2026-5-4-update-execution-report|OpenClaw 2026.5.4 Update Execution Report]]
Result: completed; live gates passed; no rollback. Gateway active on 2026.5.4. MC remains degraded only because known T15 shadow/tool-result smoke is still unresolved.

## Post-Update Audit Sprint Planned — 2026-05-06 07:55 CEST

Planned Sprint: [[../../04-Sprints/planned/2026-05-06_post-update-audit-worker-model-lox|Post-Update Audit Sprint — Worker + Model LOX Review]]
Purpose: clean post-update transition audit after OpenClaw 2026.5.4. Owners planned: Forge for worker/runtime LOX, Lens for model config/cost/timeout audit, Spark for lightweight operator-edge smoke, Atlas for synthesis. No dispatch yet; next step is Mission Control parent task + bounded worker tasks after operator confirmation or direct go.

## Post-Update Audit Sprint Corrected — 2026-05-06 07:56 CEST

Operator clarified LOX means logs, not logic/orchestration shorthand. Sprint updated: Logs/LOX now covers post-update log errors/warnings and weakness signals. Added Forge T4 for post-update logs plus system-file/update-completeness audit: Gateway/updater/MC/OpenClaw/cron/worker logs, package/plugin/systemd/script/config/build asset freshness, and stale/split-brain risk checks. Atlas synthesis moved to T5.

## Post-Update Audit Sprint Dispatched — 2026-05-06 08:02 CEST

Mission Control sprint execution started under operator-approved full autonomy. Runbook checked: worker-executable analysis/review tasks created as unlocked `status=assigned`, `approvalClass=safe-read-only`, then dispatched. Duplicate scan for planId `S-POST-UPDATE-AUDIT-2026-05-06` was clear before creation.

Tasks:
- Parent Atlas coordination: `2002cd6a-c9d1-4ad0-9bf9-d69dd3afb7bd` (`assigned`, queued; Atlas synthesis owner)
- T1 Forge worker runtime audit: `fe86bb90-7369-4ec2-bf51-43ec3f0d96e8` (`pending-pickup`, `dispatchState=dispatched`)
- T2 Lens model config/cost/timeout audit: `db774139-9f77-4cd9-9cdc-2354b4a9ba75` (`pending-pickup`, `dispatchState=dispatched`)
- T3 Spark operator smoke/doc drift audit: `3010e6b3-cf9d-4226-96b9-fb31f293e13e` (`pending-pickup`, `dispatchState=dispatched`)
- T4 Forge logs/system-file completeness audit: `57c0626f-f49a-485f-94ea-201a5640d9e3` (`pending-pickup`, `dispatchState=dispatched`)

Verification after dispatch: each worker task verified by `GET /api/tasks/<id>`; pickup proof returned `status=ok`, findings `0`. Awaiting worker receipts.

## Post-Update Audit Synthesis — 2026-05-06 08:22 CEST

Post-update audit receipts completed for T1-T4. Result: no rollback signal, no P0 blocker, worker/pickup proofs currently clean, model/cron refs valid, OpenClaw 2026.5.4 active, config valid, cron script paths present. MC remains WATCH/degraded due known T15 stale/open issue, not due a newly detected update failure.

Priorities:
- P1: T15 implementation/readiness follow-up before declaring full GREEN.
- P1: classify cross-task pickup/session-lock warning context as current vs historical/T15-derived.
- P2: decide/document `nightly-self-improvement` 900s timeout exception vs scope reduction.
- P2: clean operator-facing state wording so “update green” and “MC degraded due T15” are not conflated.
- P3: baseline Gateway post-restart websocket connect-failed spikes and isolated tool/file-path journal warnings as known noise unless recurring outside restart windows.

Report: [[../../03-Projects/reports/2026-05-06_post-update-audit-worker-model-lox-report|Post-Update Audit — Worker, Model, Logs, File Completeness]]

## Post-Update P1 Follow-up Dispatched — 2026-05-06 08:25 CEST

Following audit synthesis, Atlas created and dispatched the first P1 follow-up under operator-approved autonomy: Forge task `c313ba6d-11b5-49be-a93f-f9a724ab30b4` — T15 readiness + pickup/session-lock warning classification. Scope is read-only diagnostic: classify T15 readiness blocker and current vs historical/T15-derived lock warning context. Anti-scope: no restarts, config/cron/model changes, direct data edits, task closure/unblock, or cleanup. Verification after dispatch: task is pending-pickup/dispatched, pickup proof ok with 0 findings.

## T15 Runtime Sync Plan Created — 2026-05-06 08:33 CEST

Planned gated fix: [[../../04-Sprints/planned/2026-05-06_t15-runtime-package-sync-plan|T15 Runtime Package Sync + Smoke Plan]]. Forge task created as locked draft/gated mutation: controlled runtime package sync + T15 smoke rerun. Task must preflight first and stop before any runtime mutation/restart for explicit go. No dispatch yet.
