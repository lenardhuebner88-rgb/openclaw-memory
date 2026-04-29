---
status: planned
owner: james
created: 2026-04-29
priority: P2
---

# cron-schema-trennung

## Problem
Cron-Jobs mischen `systemEvent`, Shell-Wrapper und `agentTurn`. Live-Befund: mehrere `agentTurn`-Jobs hatten `sessionTarget=session:...discord:channel`, davon war `v3-sprint-watch-5min` aktiv kritisch.

## Spec
jobs.json-Schema-Gate einfuehren: `payload.kind=systemJob` fuer Shell ohne LLM, `payload.kind=systemEvent` fuer deterministische Events ohne LLM, `payload.kind=agentTurn` nur explizit und niemals direkt in eine Discord-Lounge-Session. Validiert wird `payload.kind`, nicht ein nicht genutztes Top-Level-Feld.

## Akzeptanz
Validator meldet `0` aktive `agentTurn` direct-discord violations. Bestehende deaktivierte Legacy-Jobs werden als `legacy-disabled` dokumentiert oder migriert.

## Risiko / Rollback
Risiko: bestehende Cron-Jobs werden geblockt, wenn sie unklar modelliert sind. Rollback: Gate auf warn-only setzen und jobs.json aus Backup wiederherstellen.
