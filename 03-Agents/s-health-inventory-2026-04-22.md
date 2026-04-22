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
