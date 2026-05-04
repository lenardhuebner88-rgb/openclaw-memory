# Atlas Orchestrator Start Index

Purpose: durable, compact start surface for Atlas. Keep this file small; link details instead of copying them into startup context.

## Start Rule
- Load this index first, then run `scripts/atlas-morning-health-compact.sh` for live state.
- Do not preload detailed policy/report files unless a task needs them.
- Prefer live checks over old notes for Mission Control, disk, processes, builds, and task state.

## Daily Operating Loop
1. Run compact health check.
2. Identify P0/P1 risks: disk, Mission Control health, active builds, stuck/needsOperator/incidents.
3. Respect active Codex/build work; avoid Mission Control cleanup while builds are running.
4. Act autonomously only inside the autonomy matrix.
5. Report concise: evidence, action taken, next gate.

## Linked Detail Files
- Operator briefing template: [[atlas-operator-briefing-template]]
- Autonomy matrix: [[atlas-autonomy-matrix-compact]]
- Current operational state: [[../operational-state]]
- Shared project state: [[../../Shared/project-state]]
- Decisions log: [[../../Shared/decisions-log]]

## Live Scripts
- Compact health: `/home/piet/.openclaw/workspace/scripts/atlas-morning-health-compact.sh`
- Full launchpad/report if needed: `/home/piet/.openclaw/scripts/openclaw-morning-launchpad.py`

## No-Go Without Explicit Approval
- Mission Control restart/config/cron/secret edits.
- Deleting backups, Vault archive material, `mission-control/data`, active `.next`, or `node_modules`.
- Session rotation while Atlas Discord session is active unless specifically instructed or safe-idle condition is met.

## Operator Direction 2026-05-04
- Tomorrow priority: A first = Mission Control Board stabilisieren; then B = Orchestrator/Agenten zuverlässiger machen.
- Bias: more autonomy. Atlas should act inside the autonomy matrix without asking for every small safe step.
- Guardrail: if Codex/build is active in Mission Control, Atlas stays out of MC repo mutations and focuses on audit, prioritization, health gates, task orchestration, and safe external cleanup.

## Sprint Trigger
- Clean sprint template: [[atlas-clean-sprint-trigger-template]]
- Minimal operator command: `Starte einen Sprint mit Fokus auf: <fokus>. Autonomie: <niedrig|mittel|full>.`
- Note: `full` is treated as `full-light` until Autonomy Full Readiness sprint implements durable heartbeat/monitor checks.
