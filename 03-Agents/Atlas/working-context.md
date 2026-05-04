# Working Context (Atlas)

## Lies zuerst
- [[../Shared/project-state]]
- [[../Shared/decisions-log]]
- [[../Shared/checkpoints]]


## Focus
- 2026-05-04 stabilization SSOT: [[../../03-Projects/plans/2026-05-04_openclaw-mission-control-stabilization-final-report|OpenClaw/Mission-Control final report]]. Current operating note: do not rotate Atlas Discord session while active; if idle >10min and cache remains high, rotate only `agent:main:discord:channel:1486480128576983070` with scoped backup/validation.

<!-- mc:auto-working-context:start -->
## Runtime Auto-Update
- task: 1839e580-790c-4ddc-88f5-12162c43bd3f [P5 Canary] sre-expert
- stage: CHECKPOINT
- next: continue current task
- checkpoint: No-op canary executed: task body read, anti-scope honored, no config/provider/QMD/routing mutations performed; preparing terminal canary-ok receipt.
- blocker: -
- updated: 2026-05-04T18:04:33.188Z
<!-- mc:auto-working-context:end -->

## Orchestrator Start Compact
- Use compact index first: [[../OpenClaw/orchestration/atlas-orchestrator-start-index]]
- Morning live gate: `/home/piet/.openclaw/workspace/scripts/atlas-morning-health-compact.sh`
- Do not preload detailed orchestration docs unless needed; keep startup context small.
