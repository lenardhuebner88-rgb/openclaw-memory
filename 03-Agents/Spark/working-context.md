# Spark Working Context

## Lies zuerst
- [[../Shared/project-state]]
- [[../Shared/decisions-log]]
- [[../Shared/checkpoints]]

<!-- mc:auto-working-context:start -->
## Runtime Auto-Update
- task: 461c0020-43a9-4140-9544-adf2fc9aafd4 [P3][Forge] AUTONOMY_PAUSED Killswitch-File existence-only
- stage: DONE
- next: await next assignment
- checkpoint: AUTONOMY_PAUSED now has a file-existence-only contract in the automation layer: the file lives at /home/piet/.openclaw/workspace/AUTONOMY_PAUSED, pause() creates it, resume() removes it, and the row is surfaced as a file
- blocker: -
- updated: 2026-04-27T18:33:18.550Z
<!-- mc:auto-working-context:end -->
