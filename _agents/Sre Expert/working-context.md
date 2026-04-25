# Sre Expert Working Context

## Lies zuerst
- [[../Shared/project-state]]
- [[../Shared/decisions-log]]
- [[../Shared/checkpoints]]

<!-- mc:auto-working-context:start -->
## Runtime Auto-Update
- task: 041e91e4-2f70-4975-8444-ad48536c7d89 [P1][Forge] Plan-Runner Version-Gate auf Live-Version abgleichen oder bewusst dry-run schalten
- stage: CHECKPOINT
- next: continue current task
- checkpoint: Version-Gate-Konsistenz ist hergestellt: plan-runner.env-Allowlist enthält jetzt die Live-Version 2026.4.22 (00bd2cf), und aktuelle runner-start Events gehen nicht mehr in version-gated über, sondern in plan-skip/runner-
- blocker: -
- updated: 2026-04-25T13:54:04.703Z
<!-- mc:auto-working-context:end -->
