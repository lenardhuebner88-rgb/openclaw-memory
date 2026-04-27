# Efficiency Auditor Working Context

## Lies zuerst
- [[../Shared/project-state]]
- [[../Shared/decisions-log]]
- [[../Shared/checkpoints]]

<!-- mc:auto-working-context:start -->
## Runtime Auto-Update
- task: 1db3aa49-3e30-4db4-a086-06a747259b4a [Follow-up][Lens] Materializer sequential dispatch policy review
- stage: DONE
- next: await next assignment
- checkpoint: Materializer-Policy Review: direkte Dispatch-Automation nur sequentiell, max 1 aktiver Child-Dispatch und max 2 offene materialisierte Children; bei health!=ok oder worker/pickup Findings nur Preview/Assigned, kein Auto-
- blocker: -
- updated: 2026-04-27T06:11:07.222Z
<!-- mc:auto-working-context:end -->
