---
status: planned
owner: forge
created: 2026-04-29
priority: P2
---

# master-heartbeat-http-refactor

## Problem
`m7-atlas-master-heartbeat.timer` verbrauchte live rund 2.2M Tokens in etwa 12 Stunden, obwohl die eigentliche Arbeit ein deterministischer Shell-/Heartbeat-Check ist.

## Spec
Heartbeat ohne LLM ausfuehren: Shell/HTTP prueft aktive Master-Tasks und schreibt deterministischen Status. LLM wird nur bei Fehlerdiagnose oder expliziter Operator-Anforderung verwendet.

## Akzeptanz
Heartbeat-Run schreibt `M7_HEARTBEAT_OK` ohne `usage.total_tokens`. Die 24h-Tokenlast dieses Jobs geht gegen 0, waehrend der Heartbeat-Proof erhalten bleibt.

## Risiko / Rollback
Risiko: LLM-basierte Fehlererklaerung fehlt im Normalpfad. Rollback: alten `agentTurn`-Job aus jobs.json-Backup wiederherstellen oder Refactor-Flag deaktivieren.
