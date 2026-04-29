---
status: planned
owner: forge
created: 2026-04-29
priority: P2
---

# pre-atlas-control-core

## Problem
Cron-agentTurn-Jobs koennen Atlas/main direkt mit Tokenlast fluten. Live-Befund am 2026-04-29: `v3-sprint-watch-5min` schrieb in die Discord-Lounge-Session `agent:main:discord:channel:1486480128576983070` und war der groesste beobachtete Token-Verbraucher.

## Spec
Deterministischen Pre-Hook vor jedem Atlas-Trigger einfuehren. Eingangsdaten: aktuelle Session-pct aus `memory-budget.log`, WIP-Limit, aktive Session-Locks und Drift-Warnings. Bei `pct > 70`, vollem WIP oder aktivem Lock wird der Tick nicht als `agentTurn` gestartet, sondern als blockierter Cron-Run protokolliert.

## Akzeptanz
Ein Cron-Tick mit `pct > 70` erzeugt keinen Atlas-agentTurn. Der passende `runs/<jobId>.jsonl` Eintrag enthaelt `status=blocked-by-control-core` mit Grund.

## Risiko / Rollback
Risiko: legitime Watcher koennen zu konservativ blockiert werden. Rollback: Feature-Flag deaktivieren und letzte jobs.json/Control-Core-Datei aus `/home/piet/.openclaw/backups/` wiederherstellen.
