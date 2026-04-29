---
status: planned
owner: forge
created: 2026-04-29
priority: P2
---

# r49-sentinel-source-fix

## Problem
Sentinel/Fake-UUIDs wie `00000000-0000-0000-0000-000000000000` tauchten in Live-Daten-/Resultpfaden auf. P1.6 Source-Audit am 2026-04-29 ergab `0` Treffer in `mission-control/src`, daher liegt die Ursache wahrscheinlich in Test-/Tool-Aufrufen oder Result-Persistenz, nicht in einer offensichtlichen Source-Konstante.

## Spec
Schreiberpfad ueber API-/MCP-Logs, Ingress-Rejects und Board-Events korrelieren. Negative Tests duerfen Sentinel-IDs verwenden, muessen aber als Test/Guard markiert bleiben und duerfen keine produktive Board-Semantik ausloesen.

## Akzeptanz
Alle Sentinel-Vorkommen der letzten 24h sind einer Test-/Guard-Quelle oder einem konkreten Bugpfad zugeordnet. Neue produktive `tasks.json`, `board-events.jsonl` oder `ingress-rejects.jsonl` Eintraege mit Sentinel-ID entstehen nicht mehr.

## Risiko / Rollback
Risiko: zu strenge Guards blockieren legitime negative Tests. Rollback: Guard auf audit-only setzen und betroffene API-Pruefung aus Backup wiederherstellen.
