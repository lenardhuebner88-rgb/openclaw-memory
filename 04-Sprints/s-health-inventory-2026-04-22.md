# S-HEALTH Inventory — 2026-04-22

> **Status:** T1 (Inventory) ✅ done | T2 (Root-Cause) ✅ done

## Kategorien-Analyse (T1)

| Kat | Beschreibung | Count | Bulk-Action | Status |
|-----|-------------|-------|-------------|--------|
| **A1** | done + kein finalReportSentAt + Alter >7d | 68 | ✅ Backfill (updatedAt) | Safe |
| **A2** | done + kein finalReportSentAt + Alter ≤7d | 64 | ❌ LASSEN | Investigate |
| **B1** | done + blockerReason | 2 | ✅ Clear (done overrides) | Safe |
| **B2** | failed + blockerReason | 14 | ❌ LASSEN | Audit |
| **C** | maxRetriesReached=true + status≠failed | 1 | ❌ LASSEN | Anomaly |

**Total accounted:** 149 (vs 145 in /api/health — small variance from in-flight mutations)

### Samples
- **A1:** `32ca203a`, `ea567bcf`, `ef1addf8`, `7564a27b`, `46ba4de8`
- **B1:** `ef1addf8`, `82bd3f9f`
- **C:** `d4195d3e`

### Pattern-Hypothese
Mehrheit (132/149 = 89%) sind A-Kategorie — missing finalReportSentAt. Das passt perfekt zu Hypothese 1 (report-error + dedup Pfad).

## Root-Cause Analyse (T2)

### Kontext
- Beobachtete Inkonsistenzen: `missing finalReportSentAt`, `stale blockerReason`, `maxRetriesReached` in unpassenden Endzuständen.
- Scope: nur Analyse, keine Code-Mutation.

### Hypothese 1 (hoch): `finalReportSentAt` kann dauerhaft fehlen trotz terminalem Status
- `board-consistency` verlangt bei `status=done` explizit `finalReportSentAt` (`src/lib/board-consistency.ts:66-70`, `92-99`).
- In `emitTaskLifecycleReport()` wird bei Report-Fehler zwar `lastReportedStatus`/`lastReportedAt` gesetzt, aber **nicht** `finalReportSentAt` (`src/lib/task-reports.ts:399-408`).
- Danach kann der gleiche terminale Stage-Report innerhalb des Dedup-Fensters (24h) übersprungen werden (`src/lib/task-reports.ts:79-85`, `290-304`).
- Effekt: Task bleibt mit `lastReportedStatus=result`, aber ohne `finalReportSentAt` hängen.

### Hypothese 2 (hoch): `maxRetriesReached` wird nicht robust auf terminalem Erfolg zurückgesetzt
- `maxRetriesReached` wird bei `result` nur im Erfolgszweig des Report-Writes auf `false` gesetzt (`src/lib/task-reports.ts:354-370`, besonders `367`).
- Wenn Report übersprungen oder fehlgeschlagen ist, fehlt dieses Reset.
- Der `done`-Pfad in `updateTask()` setzt `dispatch/execution/receipt`, aber **kein** `maxRetriesReached=false` (`src/lib/taskboard-store.ts:885-891`).
- Ergebnis: Stale `maxRetriesReached=true` kann in eigentlich gesunden Endzuständen verbleiben.

### Hypothese 3 (mittel): `blockerReason` wird als Failure-Text in `failed` konserviert und als „stale“ gezählt
- Finalize-Route patcht bei `failed` bewusst sowohl `blockerReason` als auch `failureReason` (`src/app/api/tasks/[id]/finalize/route.ts:64-70`).
- `updateTask()` löscht `blockerReason` nur implizit, wenn Status **nicht blocked** ist und kein `blockerReason` gepatcht wird (`src/lib/taskboard-store.ts:853-860`).
- Weil Finalize explizit `blockerReason` mitgibt, bleibt es auf `failed`-Tasks erhalten.
- Je nach Audit-Heuristik wirkt das als „stale blockerReason“, obwohl es aus diesem Pfad intentional ist.

### Hypothese 4 (mittel): strikter Finalize-Precondition kann Flag-Konsistenz brechen
- Finalize akzeptiert nur `receiptStage in {started, accepted}` (`src/app/api/tasks/[id]/finalize/route.ts:35-37`).
- Tasks in `progress`/`stalled-warning` werden nicht finalisiert und können in Zwischenzuständen verbleiben, bis andere Pfade eingreifen.
- Diese Divergenz erhöht die Chance auf partielle Terminal-Flags über alternative Pfade.

### Fazit
Plausibelster Kernfehler ist die Kombination aus:
1) report-error setzt `lastReported*`, aber nicht `finalReportSentAt`, und
2) dedup blockiert zeitnahen Re-Emit,
plus
3) terminale Normalisierung in `updateTask()` resetet `maxRetriesReached` nicht hart.

Das erklärt direkt die beobachteten Cluster `missing finalReportSentAt` + `maxRetriesReached`.


## S-HEALTH-2 Residual Investigation (T3 Follow-up, 15 Items)

### Live Snapshot
- Quelle: `GET /api/board-consistency` (2026-04-22 17:54 UTC)
- Residual Issues: **15**
- Verteilung: **15x `done-state-mismatch`** (keine `draft-stale`/`missing-core-fields`/`open-fixture` mehr im Live-Set)

### Inventory-Table (15/15)
| # | Task ID | Kurzbild | Root-Cause-Klasse | Empfehlung |
|---|---|---|---|---|
| 1 | 9313c40d-c478-4646-ac20-fd218694ac7c | done + `lastReportedStatus=failed` + `finalReportSentAt` gesetzt | RC-A (stale terminal-report marker) | fix |
| 2 | 1ecc4332-5a91-4045-895d-24e1861658f2 | done + `lastReportedStatus=failed` + `finalReportSentAt` gesetzt | RC-A | fix |
| 3 | 3b6e641a-0816-4f6f-a1f7-9a5891c8f683 | done + `lastReportedStatus=failed` + `finalReportSentAt` gesetzt | RC-A | fix |
| 4 | 33144be4-2363-4211-aa24-6e4f5fb19a88 | done + `lastReportedStatus=failed` + `finalReportSentAt` gesetzt | RC-A | fix |
| 5 | 568aa148-c016-45a4-9038-ed987560765f | done + `lastReportedStatus=failed` + `finalReportSentAt` gesetzt | RC-A | fix |
| 6 | 15b34b00-653b-4e0e-af16-f54d0a098d49 | done + `lastReportedStatus=failed` + `finalReportSentAt` gesetzt | RC-A | fix |
| 7 | 1498cc52-5ec8-4696-a98a-06b73331d3f4 | done + `lastReportedStatus=failed` + `finalReportSentAt` gesetzt | RC-A | fix |
| 8 | 0ce7ca00-b4c0-4f58-a0e8-902632f3db75 | done + `lastReportedStatus=failed` + `finalReportSentAt` gesetzt | RC-A | fix |
| 9 | 187af1a6-d851-4ebc-970d-565dfb1bb7d8 | done + `lastReportedStatus=failed` + `finalReportSentAt` gesetzt | RC-A | fix |
| 10 | 87805295-66aa-4ee0-ba59-4fe01356aee9 | done + `lastReportedStatus=failed` + `finalReportSentAt` gesetzt | RC-A | fix |
| 11 | 1e3504a5-27a8-4a6a-b4ef-4ec2ef78bdb6 | done + `lastReportedStatus=failed` + `finalReportSentAt` gesetzt | RC-A | fix |
| 12 | 7ef76135-633d-4c51-9f5e-8a8c2e71a065 | done + `lastReportedStatus=failed` + `finalReportSentAt` gesetzt | RC-A | fix |
| 13 | cfe8dbe9-5492-4ced-b0fb-b2b1814656e8 | done + `lastReportedStatus=failed` + `finalReportSentAt` gesetzt | RC-A | fix |
| 14 | 49a11c0e-b4ee-4669-8933-6ba011136439 | done + report-flags komplett leer (`finalReportSentAt/lastReported*` null) | RC-B (legacy/no-report metadata) | fix |
| 15 | a50dc837-5079-4dd9-8592-137cb6005ade | done + report-flags komplett leer (`finalReportSentAt/lastReported*` null) | RC-B | fix |

### Root-Cause Summary (konsolidiert)
- **RC-A (13/15): stale terminal report marker**  
  Tasks sind fachlich `done`, aber `lastReportedStatus` blieb auf `failed`. Dadurch verletzt die Konsistenzprüfung `reportStatusConsistent` (erwartet `result` oder leer).  
  Relevante Logik: `hasDoneFinalSummaryConsistency()` in `src/lib/board-consistency.ts:66-70`.

- **RC-B (2/15): fehlende Reporting-Metadaten auf done**  
  Zwei alte `done`-Tasks haben weder `finalReportSentAt` noch `lastReported*`; diese fallen direkt durch denselben Done-Consistency-Check.

### Empfohlene Actions (ohne Blind-Patch)
1. **Gezielte Metadaten-Reconciliation (15 IDs only)**
   - RC-A: `lastReportedStatus -> result` (optional `lastReportedAt -> updatedAt`), `finalReportSentAt` unverändert.
   - RC-B: `finalReportSentAt -> updatedAt`, `lastReportedStatus -> result`, `lastReportedAt -> updatedAt`.
2. **Guard für Zukunft:** bei `status=done` im Normalisierungspfad `lastReportedStatus` nie auf `failed` belassen (oder auto-reconcile in Hygiene-Job).
3. **Nachlauf-Verify:** `/api/board-consistency` muss von 15 auf 0 residual fallen, ohne neue Kategorien zu öffnen.
