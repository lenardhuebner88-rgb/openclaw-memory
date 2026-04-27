# Working Context (Atlas)

## Lies zuerst
- [[../Shared/project-state]]
- [[../Shared/decisions-log]]
- [[../Shared/checkpoints]]


## Focus
-

<!-- mc:auto-working-context:start -->
## Runtime Auto-Update
- task: 2b991048-2a41-47e2-b2db-0a268d8f6eed [P2][Forge] Costs anomaly acknowledge endpoint/UI contract fix
- stage: CHECKPOINT
- next: continue current task
- checkpoint: Found deployment gap: build wrapper skipped rebuild while MC was live, so acknowledge route never entered .next. Re-running canonical build with ALLOW_BUILD_WHILE_RUNNING=1, then safe restart and endpoint verify.
- blocker: -
- updated: 2026-04-27T12:56:25.260Z
<!-- mc:auto-working-context:end -->
