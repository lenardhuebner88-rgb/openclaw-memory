---
status: planned
owner: forge
created: 2026-04-29
priority: P2
---

# agent-wip-limits-live

## Problem
`mission-control/src/lib/agent-wip-limits.ts` existiert, war im Live-Hot-Path aber nicht importiert. Zusaetzlich ist der Config-Pfad ueber `process.cwd()` fragil.

## Spec
Pfad robust auf `/home/piet/.openclaw/openclaw.json` oder eine zentral konfigurierte OpenClaw-Root aufloesen. Limits aus `agents.list[*].params.wipLimit` lesen und im Spawn-/Dispatch-Pfad sowie im Pre-Atlas-Control-Core erzwingen.

## Akzeptanz
Live-Werte werden erkannt: Atlas/main `3`, Forge/sre-expert `2`, Pixel/frontend-guru `2`, Lens/efficiency-auditor `1`, James `2`, Spark `1`. Dispatch ueber Limit wird deterministisch blockiert und im Proof sichtbar.

## Risiko / Rollback
Risiko: Tasks bleiben laenger in pending, wenn Limits zu streng greifen. Rollback: Import/Feature-Flag deaktivieren und Dispatch-Pfad auf bisherigen Default zuruecksetzen.
