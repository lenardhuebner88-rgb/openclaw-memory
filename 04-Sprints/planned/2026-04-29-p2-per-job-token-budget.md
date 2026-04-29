---
status: planned
owner: lens
created: 2026-04-29
priority: P2
---

# per-job-token-budget

## Problem
`v3-sprint-watch-5min` erzeugte am 2026-04-29 mehr als 12M Tokens in rund 12 Stunden. Weitere hohe Last kam von `atlas-receipt-stream-subscribe`, `m7-atlas-master-heartbeat.timer` und `mc-task-parity-check-10min`.

## Spec
`dailyTokenBudget` pro `agentTurn`-Job einfuehren. Scheduler/Gateway prueft rollierende 24h-Usage aus `cron/runs/<jobId>.jsonl`; bei Budget-Ueberschreitung wird kein LLM-Turn gestartet und ein `budget-exceeded` Run-Event geschrieben.

## Akzeptanz
Ein Job ueber Budget startet keinen `agentTurn`. Das Run-Log nennt Budget, verbrauchte Tokens, Fenster und naechsten moeglichen Start.

## Risiko / Rollback
Risiko: wichtige Jobs koennen bei falsch gesetztem Budget ausfallen. Rollback: Budget-Gate warn-only oder `dailyTokenBudget=null`.
