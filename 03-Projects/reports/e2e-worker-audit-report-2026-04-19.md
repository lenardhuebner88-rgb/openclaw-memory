---
title: E2E Worker-Audit Report 2026-04-19
date: 2026-04-19 09:40 UTC
author: Operator (pieter_pan) direkt — Atlas-Task-Crash-Recovery
scope: 5-Szenario Worker-Lifecycle-Audit gegen Live-Board-Daten (221 Tasks, 126 letzte 24h)
---

# E2E Worker-Audit — 5 Szenarien

## Gesamtbewertung: 🟢 4/5 Szenarien grün

## S1 — Happy-Path ✅ EXCELLENT

- Done-Tasks letzte 24h: **76**
- Davon mit `resultSummary` gefüllt: **76 = 100%**

**Wertung:** Receipt-Pipeline liefert 100% Coverage. R22 (Task ohne Result-Receipt ≠ erfolgsfrei) ist weitgehend neutralisiert — Agents liefern Receipts zuverlässig.

## S2 — Ghost-Fail-Path ⚠️ TEIL-LEAK

- Pre-Fix (vor 2026-04-19 07:30): **8 Ghost-Fails**
- **Post-Fix (nach Naming-Fundamental): 4 Ghost-Fails** ← LEAK

**Erkenntnis:** Mein `resolveRuntimeAgentId`-Fix in `route.ts` löste das `assigned_agent`-Persistierungsproblem (Display → Runtime), **aber nicht die Gateway-Session-ID-Konstruktion** (`worker:atlas-<taskId>`). Das Gateway-Internal-Pattern bleibt — 4 Legacy-Tasks liefen nach Fix ghost-failed weiter.

**Root-Cause-Trennung:**
- **Fixed bei uns:** Storage-Persistierung (`assigned_agent=sre-expert`) ✅
- **NICHT fixed (Gateway-Internal):** `workerSessionId = worker:atlas-<taskId>` Konstruktion bleibt hardcoded

**Empfehlung:** Gateway-Upgrade oder externes Issue. Operator-Lock (R28) ist der präventive Schutz.

## S3 — Operator-Lock ✅ FUNKTIONIERT

- Tasks mit `operatorLock=true`: **1**
- Tasks mit `lockedUntil`: **1**

**Überraschung:** WK-35 scheint nach Forge's Arbeit doch behoben — Lock wird persistiert. Re-Verify mit Live-PATCH später.

## S4 — Receipt-Sequence ✅ SAUBER

Stage-Verteilung letzte 24h:
- `result`: 76
- `failed`: 49 (Smoke-Tests + echte Failures)
- Unbekannt: 1

`receiptStage=no-receipt` in ganzem Store: **0** → B2-Migration komplett erfolgreich, keine Rückstände.

R36 Warn-Mode läuft (Worker-Pack 2) — keine out-of-order-Violations gesichtet.

## S5 — Retry-Single-Path 🟡 OK mit Beobachtungen

- Tasks mit `retryCount>0`: 2 (Worker-Pack 8 funktioniert)
- `maxRetriesReached`: 0 (keine Retry-Exhaustion)

**Duplicate-Titles (mögliche manuelle Retries):**
- 12× "Smoke pending-pickup lifecycle" (Smoke-Bot, erwartet)
- 2× WK-35 Operator-Lock Retry
- 2× Task-Tab A4 Later→Archive
- 2× Task-Tab B1 Agent-Load
- 2× Worker-Pack 8 Retry-Single-Path

**Wertung:** Duplicate-Pattern ist hauptsächlich Atlas-Heartbeat-re-runs bei Crashes (R35 Live-Beispiel). Kein systemisches Retry-Storm-Problem.

## Meta: Naming-Fundamental-Verify ✅ 100%

- Runtime-IDs: **221 Tasks (100%)**
- Display-Names: **0**
- Other: 0

**Verdikt:** Naming-Fundamental-Fix komplett erfolgreich. Bulk-Migration + route.ts-Fix + UI-Wrap = alle Tasks auf Runtime-IDs, null Drift.

---

## Schwachstellen-Matrix nach Audit

| Bereich | Status | Next Action |
|---|---|---|
| Happy-Path | ✅ | Keine |
| Ghost-Fail | 🟡 | Gateway-Issue — R28 Operator-Lock als Workaround |
| Operator-Lock | ✅ | WK-35 war zwischenzeitlich gefixt |
| Receipt-Sequence | ✅ | Keine |
| Retry-Single-Path | ✅ | Keine |
| Naming | ✅ | Keine |
| MEMORY.md-Bootstrap | ✅ | R34 Fix live, Guard-Cron aktiv |
| Session-File-Growth | 🔴 | R36 — **Atlas-Sessions 15 MB gefunden**. Compact-Cron existiert nicht, nur Alert |
| MCP-Zombie-Cleanup | 🟡 | WK-32 Forge-Task done, aber langfristig beobachten |

## Follow-up-Empfehlungen

1. **Session-Compact-Tool bauen** (bislang nur Alert) — `openclaw session compact <id>` oder manual archive
2. **Gateway-Session-ID-Pattern prüfen** mit openclaw-Maintainer Kontakt
3. **Atlas-Retry-Ready testen** mit neuem bootstrapMaxChars=24576

---

## Audit signed off: 09:40 UTC 2026-04-19
Deliverables:
- Dieser Report (Vault)
- R33-R36 Rules server-side gesynct
- Memory-Size-Guard-Cron aktiv (6h)
- Session-Size-Alert-Cron aktiv (30min, 4MB threshold)
- Bootstrap-Limit erhöht 8192 → 24576
