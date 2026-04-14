# Worker Working Context

## Routing-Kurzregel
- Maßgeblich ist `../Shared/reporting-routing-canon.md`.
- `#execution-reports` = Lifecycle-Mirror
- `#alerts` = operative Warnungen
- Agent-Channels = fachliche Resultate
- `#atlas-main` nur bei Koordinations- oder Entscheidungsbedarf

## Lies zuerst
- [[../Shared/project-state]]
- [[../Shared/decisions-log]]
- [[../Shared/checkpoints]]
- [[../Shared/reporting-routing-canon]]

<!-- mc:auto-working-context:start -->
## Runtime Auto-Update
- task: 7c7ad80e-86f5-4712-9704-75e8259871dd [E2E][Forge] Voller Workflow-Durchlauf einmal sauber verifizieren
- stage: CHECKPOINT
- next: continue current task
- checkpoint: Forge E2E workflow smoke-run: accepted task, advanced execution to started/progress, and prepared terminal receipt validation.
- blocker: -
- updated: 2026-04-14T11:31:31.805Z
<!-- mc:auto-working-context:end -->
