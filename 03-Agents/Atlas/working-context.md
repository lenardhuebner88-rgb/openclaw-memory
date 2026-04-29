# Working Context (Atlas)

## Lies zuerst
- [[../Shared/project-state]]
- [[../Shared/decisions-log]]
- [[../Shared/checkpoints]]


## Focus
-

<!-- mc:auto-working-context:start -->
## Runtime Auto-Update
- task: 3f600b85-17de-4cfa-8e1d-16d723f9b02d [Forge Fix] receipt-materializer negative residual signals must not create follow-up drafts
- stage: CHECKPOINT
- next: continue current task
- checkpoint: Patch + Regression umgesetzt: explizite negative Residual-Signale unterdrücken jetzt Draft-Follow-up-Erzeugung; positive Signale erzeugen weiterhin genau einen deduplizierten Draft. Tests (17/17) + Typecheck grün, Commit
- blocker: -
- updated: 2026-04-29T20:24:07.681Z
<!-- mc:auto-working-context:end -->
