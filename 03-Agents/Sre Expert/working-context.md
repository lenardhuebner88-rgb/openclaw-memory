# Sre Expert Working Context

## Lies zuerst
- [[../Shared/project-state]]
- [[../Shared/decisions-log]]
- [[../Shared/checkpoints]]

<!-- mc:auto-working-context:start -->
## Runtime Auto-Update
- task: cd59ce53-73eb-4fb0-808a-8c7a184573bf Resilience: agent reconnect after gateway restart
- stage: DONE
- next: await next assignment
- checkpoint: Implemented heartbeat freshness resilience after gateway restart: Mission Control now treats non-terminal non-subagent sessions (including status=active) as fresh, preventing false dark/offline state for Atlas/agents aft
- blocker: -
- updated: 2026-05-01T14:24:01.775Z
<!-- mc:auto-working-context:end -->
