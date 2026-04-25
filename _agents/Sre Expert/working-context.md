# Sre Expert Working Context

## Lies zuerst
- [[../Shared/project-state]]
- [[../Shared/decisions-log]]
- [[../Shared/checkpoints]]

<!-- mc:auto-working-context:start -->
## Runtime Auto-Update
- task: 3b356588-b8d6-4819-bc7d-ed4f919fcdef [P1][RCA+Fix][Forge] Meeting-/Debate-Finalizer-Bruch blockiert Atlas nach Beiträgen vor terminalem Abschluss
- stage: DONE
- next: await next assignment
- checkpoint: Root-Cause: Der Bruch lag im Fallback von meeting-status-post.sh: sobald keine Teilnehmer-Signatur fehlte, wurde pauschal `needs-chairman-finalize` gesetzt, ohne den Synthese-Zustand zu prüfen. Dadurch wurden bereits fac
- blocker: -
- updated: 2026-04-25T08:07:31.065Z
<!-- mc:auto-working-context:end -->
