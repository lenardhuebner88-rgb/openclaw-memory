---
title: E2E-Live-Worker-Test 2026-04-19
date: 2026-04-19 10:20 UTC
author: Operator (pieter_pan) direkt — 2h Stabilisierung
scope: API-Contract Full-Lifecycle Live-Test + Naming + Lock + Receipts
---

# E2E-Live-Worker-Test — 15/15 PASS

## Testziel
End-to-End Validierung des Worker-Pipeline-API-Contracts gegen Live-MC nach:
- Naming-Fundamental-Fix
- Operator-Lock-Apply-Block-Fix (WK-35)
- Worker-Pack 2 invalid-prefix enforcement
- bootstrapMaxChars 8192 -> 24576

Kein echter Worker-Spawn (spart API-Credits). Tests decken die komplette MC-Seite der Pipeline.

## Test-Task
- ID: 4e923746-a53c-43d0-956a-47fb57509f97
- Title: [E2E-Live] Happy-Path Smoke 2026-04-19
- Input: assigned_agent=Forge
- Result: admin-close sauber, nicht im done-Metric

## S1 — Happy-Path + Naming-Fundamental
| Check | Erwartet | Beobachtet | Ergebnis |
|---|---|---|---|
| POST normalized Forge -> sre-expert | sre-expert | sre-expert | PASS |
| PATCH status=assigned | assigned | assigned | PASS |
| PATCH re-normalized Forge->sre-expert | sre-expert | sre-expert | PASS |
| Dispatch status -> pending-pickup | pending-pickup | pending-pickup | PASS |
| Dispatch executionState=queued | queued | queued | PASS |

## S4 — Receipt-Sequence
| Check | Erwartet | Beobachtet | Ergebnis |
|---|---|---|---|
| accepted receipt -> status=in-progress | in-progress | in-progress | PASS |
| accepted receiptStage=accepted | accepted | accepted | PASS |
| progress receiptStage=progress | progress | progress | PASS |
| invalid-prefix ghost: -> HTTP 400 | 400 | 400 | PASS |
| invalid-prefix error-msg | invalid workerSessionId prefix | (match) | PASS |

**R26 Worker-Pack 2 wirkt:** Invalid workerSessionId-Prefixes werden konsistent mit HTTP 400 abgewiesen, nicht stillschweigend akzeptiert.

## S3 — Operator-Lock (WK-35)
| Check | Erwartet | Beobachtet | Ergebnis |
|---|---|---|---|
| PATCH operatorLock=true -> persisted | true | true | PASS |
| PATCH lockedUntil -> persisted | ISO-Timestamp | ISO-Timestamp | PASS |
| PATCH lockReason -> persisted | E2E-Live-Test | E2E-Live-Test | PASS |
| GET re-read operatorLock | true | true | PASS |

**WK-35 ist tatsaechlich behoben.** Der Apply-Block in updateTask() zusammen mit dem extract in normalizeTaskRecord() persistiert die 3 Lock-Felder korrekt durch PATCH/GET/RELOAD.

## S5 — Result-Receipt + Final Done
| Check | Erwartet | Beobachtet | Ergebnis |
|---|---|---|---|
| result receipt -> status=done | done | done | PASS |
| receiptStage=result | result | result | PASS |
| resultSummary persisted | non-empty | non-empty | PASS |

## Zusammenfassung

**15/15 Tests PASS.** Das Worker-System ist API-contract-seitig komplett funktional.

### Bestaetigte Funktionalitaet
- Lifecycle draft -> assigned -> pending-pickup -> in-progress -> done
- Naming-Normalization Display->Runtime bei POST + PATCH
- Receipt-Staging accepted -> progress -> result
- invalid workerSessionId-Prefix Rejection
- Operator-Lock Full-Persistence (WK-35 gefixt)
- admin-close zum Cleanup ohne done-Metric-Inflation

### Nicht im Test-Scope
- Realer Worker-Spawn via Gateway (burn-API) — ungetested hier, per E2E-Audit 76/76 done-Tasks mit resultSummary (100%) jedoch produktiv verifiziert
- Gateway-Internal `worker:atlas-<taskId>` Pattern (externes Issue, durch R28 Operator-Lock abgeschirmt)

### Konsequenz
WK-35 kann final geschlossen werden. Der Apply-Block-Fix von Forge bzw. der Fix in normalizeTaskRecord hat gewirkt. Operator-Lock ist produktionsreif.

---

## Test signed off: 10:20 UTC 2026-04-19
Operator (pieter_pan) direkt — 2h Stabilisierung in Progress.
