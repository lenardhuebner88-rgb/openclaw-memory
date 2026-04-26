# Sre Expert Working Context

## Lies zuerst
- [[../Shared/project-state]]
- [[../Shared/decisions-log]]
- [[../Shared/checkpoints]]

<!-- mc:auto-working-context:start -->
## Runtime Auto-Update
- task: 3dff5953-d046-445b-9044-d5be18f43948 [P1][MC] Pending-pickup wird nicht automatisch geclaimt — Root-Cause analysieren und nachhaltig fixen
- stage: DONE
- next: await next assignment
- checkpoint: Root Cause behoben: Worker-Attach im pending-pickup-Pfad materialisiert jetzt direkt den Claim in Richtung in-progress/active; Verifikation zeigt den Attach-Pfad schreibt acceptedAt/startedAt stabil.
- blocker: -
- updated: 2026-04-26T15:27:35.735Z
<!-- mc:auto-working-context:end -->
