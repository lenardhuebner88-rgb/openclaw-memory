# Mission Control Degraded RCA

Datum: 2026-05-02

## Ausgangslage

Im H-2 Test meldete Hermes korrekt einen degraded Mission-Control-Zustand. Die spaetere Live-Pruefung in H-3 zeigte den Zustand wieder gruen.

## Live Evidence H-3

- `/api/health`: HTTP 200, `status=ok`, `severity=ok`.
- `execution.status=ok`.
- `recoveryLoad=0`.
- `attentionCount=0`.
- `/api/board/next-action`: `All clear`, `action=none`.
- `/api/tasks/snapshot`: `total=952`, `open=193`, `done=759`, `staleInProgress=0`.

## Bewertung

Kein akuter Mission-Control-Incident mehr sichtbar.

Der Unterschied zwischen `/api/health` `openTasks=0` und `/api/tasks/snapshot` `open=193` ist wahrscheinlich ein Semantik-Unterschied: Health bewertet aktive/stale/recovery-relevante Arbeit, Snapshot zaehlt alle offenen Tasks. Das sollte nicht als Incident gewertet werden, solange `staleInProgress=0`, `attentionCount=0` und `board/next-action=none` bleiben.

## Next Action

Keine Recovery-Aktion.

Bei neuer Degraded-Meldung:

1. `mc-readonly.mc_health`.
2. `mc-readonly.mc_board_consistency`.
3. `mc-readonly.mc_tasks_snapshot`.
4. Runbook `playbooks/mission-control-api-readonly.md`.
5. Erst nach Live-Evidence ueber Restart/Build-Gate sprechen.
