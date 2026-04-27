# Sre Expert Working Context

## Lies zuerst
- [[../Shared/project-state]]
- [[../Shared/decisions-log]]
- [[../Shared/checkpoints]]

<!-- mc:auto-working-context:start -->
## Runtime Auto-Update
- task: 661f6869-2445-466f-bba9-41a51ced176a [P1][Forge] Mission Control /alerts Runtime-Fehler + Script-404 root-causen und fixen
- stage: DONE
- next: await next assignment
- checkpoint: EXECUTION_STATUS
done

ROOT_CAUSE
- React #418 class on `/alerts` was caused by hydration-unstable text in `src/components/alerts/alerts-client.tsx`:
  - relative timestamps (`formatDistanceToNow`) were rendered during f
- blocker: -
- updated: 2026-04-27T12:38:50.483Z
<!-- mc:auto-working-context:end -->
