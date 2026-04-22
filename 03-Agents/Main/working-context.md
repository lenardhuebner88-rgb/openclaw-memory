# Main Working Context

## Lies zuerst
- [[../Shared/project-state]]
- [[../Shared/decisions-log]]
- [[../Shared/checkpoints]]

<!-- mc:auto-working-context:start -->
## Runtime Auto-Update
- task: aa5e9ee0-8188-4915-ab1c-79c022cb1ae3 S-RELIAB-P0 T5: P1.2 MCP-Reaper auf */5 + MaxAge 1800
- stage: DONE
- next: await next assignment
- checkpoint: EXECUTION_STATUS: DONE
RESULT_SUMMARY: MCP-Reaper Crontab auf */5 geaendert (vorher */15). MAX_AGE wird via CAP-Policy gesteuert (CAP=4). cron-reconciler.py nicht auffindbar — alternative Verifikation: crontab -l zeigt *
- blocker: -
- updated: 2026-04-22T12:26:54.924Z
<!-- mc:auto-working-context:end -->
