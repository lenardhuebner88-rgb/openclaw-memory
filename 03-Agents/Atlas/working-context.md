# Working Context (Atlas)

## Lies zuerst
- [[../Shared/project-state]]
- [[../Shared/decisions-log]]
- [[../Shared/checkpoints]]


## Focus
- 2026-05-04 stabilization SSOT: [[../../03-Projects/plans/2026-05-04_openclaw-mission-control-stabilization-final-report|OpenClaw/Mission-Control final report]]. Current operating note: do not rotate Atlas Discord session while active; if idle >10min and cache remains high, rotate only `agent:main:discord:channel:1486480128576983070` with scoped backup/validation.
- Morgen-Start 2026-05-05: [[../../03-Projects/reports/daily/2026-05-04_openclaw-workday-handoff-for-2026-05-05|OpenClaw Workday Handoff]]. Erst Launchpad/Timer/validate-models prüfen, dann produktiv mit Atlas arbeiten. Keine Session-Rotation, solange Atlas aktiv `running` ist.

<!-- mc:auto-working-context:start -->
## Runtime Auto-Update
- task: 79c99121-4cef-4959-9ed6-89b5f38f368c [P3][Forge] Baseline post-restart log noise signals
- stage: CHECKPOINT
- next: continue current task
- checkpoint: Logquellen gesichtet, beginne evidenzbasierte Klassifikation von Restart-Noise vs. eskalationswürdigen Signalen.
- blocker: -
- updated: 2026-05-06T06:51:49.316Z
<!-- mc:auto-working-context:end -->

## Orchestrator Start Compact
- Use compact index first: [[../OpenClaw/orchestration/atlas-orchestrator-start-index]]
- Morning live gate: `/home/piet/.openclaw/workspace/scripts/atlas-morning-health-compact.sh`
- Do not preload detailed orchestration docs unless needed; keep startup context small.

## Runtime Policy Update — 2026-05-05 Long-Run Timeout
- Source: [[../Hermes/atlas-long-run-timeout-analysis-2026-05-05]]
- Atlas Discord turns have a hard embedded-run wallclock budget of 600s (`agents.defaults.timeoutSeconds=600`); recent MC work was killed by wallclock timeout, not tool-count.
- For Mission-Control/build/test/restart work: split after 2-3 heavy tool phases into checkpoint turn with Evidence + next step.
- Delegate heavy gates to Forge/SRE or bounded worker tasks; Atlas stays coordinator/context anchor.
- Do not solve by globally raising timeout unless explicitly approved and schema/support exists.
