# Main Working Context

## Lies zuerst
- [[../Shared/project-state]]
- [[../Shared/decisions-log]]
- [[../Shared/checkpoints]]

<!-- mc:auto-working-context:start -->
## Runtime Auto-Update
- task: 676b5c07-3d3c-4984-8b43-050ad0ddb025 [P1][Atlas] Worker-Pickup Route-Cross-Analyse und Dispatch-Stale-Fix
- stage: DONE
- next: await next assignment
- checkpoint: Root cause: dispatch/pickup eligibility was gating on stale heartbeat state, while proof/runner state showed the board task itself was the only live incident. Fix: cross-checked worker sessions and removed stale-heartbea
- blocker: -
- updated: 2026-04-27T15:03:55.415Z
<!-- mc:auto-working-context:end -->
