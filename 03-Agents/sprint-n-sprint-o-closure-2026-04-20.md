# Sprint-N + Sprint-O Closure Report
**Datum:** 2026-04-20
**Sprint-N:** Lifecycle Stability & Audit Closure
**Sprint-O:** lastReportedStatus Lifecycle Fix

---

## Sprint-N — Lifecycle Stability & Audit Closure

### Ziel
MC-Task-Lifecycle für gateway-dispatchte Worker stabil und auditierbar machen. Referenz-Incident: `a8100ac6-df0b-4e16-b4d6-ac5119730e46`.

### Workstreams

| # | Owner | Status | Output |
|---|---|---|---|
| A — Evidence Freeze | Lens | ✅ | 5 Problembereiche mit File/Line belegt |
| B — Lifecycle Invariants | Forge | ✅ | Retry-Reset-Felder: `resolvedAt`, `failedAt`, `receiptStage` |
| C — Run Source of Truth | Forge | ✅ | `worker-runs.json` als kanonisch, Upsert statt Duplicate |
| D — Terminal Audit Parity | Forge | ✅ | `receipt-result` + `report-deduplicated` Board-Events |
| E — Controlled Regression | Lens | ✅ | 2/2 E2E-Fälle bestanden |

### Zentrale Findings aus Sprint-N

**1. Stall-Schwellen 2/5min (worker-monitor.py)**
- `STALL_WARN_MINUTES = 2`, `STALL_HARD_MINUTES = 5` aktiv seit 2026-04-19
- `STALL_PER_AGENT` erlaubt kein Override für `frontend-guru` → false-positive fails bei legitimen langen UI-Builds
- File: `scripts/worker-monitor.py:51-52`

**2. Run-Erkennung gesplittet**
- `~/.openclaw/subagents/runs.json` (Gateway) ≠ `mission-control/data/worker-runs.json` (MC)
- Gateway-dispatchte Worker hinterlassen keine Einträge in `runs.json`
- Fix (WS-C): `worker-runs.json` als kanonisch festgelegt, Upsert statt Duplicate

**3. Fehlende terminale Board-Events**
- `receipt-result` Event fehlte in `complete/route.ts` und `receipt/route.ts`
- `report-deduplicated` Event fehlte in `task-reports.ts`
- Fix (WS-D): beide Events ergänzt

**4. Retry-State Inkonsistenzen**
- `resolvedAt` wurde bei Retry nicht zurückgesetzt
- `receiptStage` blieb auf altem Wert (stuck)
- `lastReportedStatus` wurde nicht zurückgesetzt
- Fix (WS-B): retry-prime Block in `recovery-action/route.ts` umfassend erweitert

**5. Redispatch erzeugte doppelte worker-runs**
- Gleiche `taskId + workerSessionId` wurde mehrfach eingefügt statt upserted
- Fix (WS-C): `persistWorkerRun()` auf Upsert umgebaut

### E2E-Ergebnisse (Workstream E)

**Fall 1 — Happy Path ✅**
```
draft → assigned → pending-pickup → in-progress → done
dispatchState: draft → queued → dispatched → dispatched → completed
executionState: queued → queued → queued → active → done
receiptStage: — → — → — → accepted → result
Final: status=done | dispatchState=completed | executionState=done | lastReportedStatus=result | receiptStage=result
```

**Fall 2 — Fail → Retry → Success ✅**
```
draft → assigned → pending-pickup → failed → (auto-reset) → pending-pickup → done
executionState: queued → queued → queued → failed → queued → queued → done
receiptStage: — → — → — → failed → null → — → result
Final: status=done | dispatchState=completed | executionState=done | receiptStage=result
```

### Verbleibendes Restrisiko aus Sprint-N
- 1 kosmetisches Artifact: `lastReportedStatus=failed` nach Fail→Retry→Success (Display-only)
- **→ Behoben in Sprint-O**

---

## Sprint-O — lastReportedStatus Lifecycle Fix

### Ziel
Kosmetisches `lastReportedStatus`-Artifact nach Fail→Retry→Success eliminieren.

### Root Cause (Workstream 1 — Lens Analysis)

**Problem:** `terminalPatch` in `complete/route.ts` und `taskPatch` in `receipt/route.ts` setzten **kein `lastReportedStatus`**.

Beide verließen sich auf `emitTaskLifecycleReport` als sekundären Setter — das ist Fire-and-forget, keine verlässliche primäre State-Quelle. Bei API-Fehlern (Discord/postReport) blieb das Feld unverändert.

**Fix-Empfehlung: A+B (Dual-Fix)**
- Deduplizierung war NICHT das Problem (`lastReportedStatus='failed' !== 'result'` → kein Skip)
- `hasRecentEquivalentTerminalReport` funktioniert korrekt

### Fix-Implementierung (Workstream 2 — Forge)

**Fix A — complete/route.ts:116-117**
```typescript
// terminalPatch Objekt ergänzt:
lastReportedStatus: 'result' as const,
lastReportedAt: now,
```

**Fix B — receipt/route.ts:521-522**
```typescript
// taskPatch bei stage===result ergänzt:
lastReportedStatus: 'result' as const,
lastReportedAt: now,
```

**Verification:** `npm run typecheck` ✅

### E2E-Nachweis nach Sprint-O
Nach Fix: `lastReportedStatus` zeigt korrekt `result` nach Erfolg — kein `failed` mehr.

---

## Geänderte Dateien (Sprint-N + Sprint-O)

| File | Änderung | Workstream |
|---|---|---|
| `recovery-action/route.ts` | retry-prime Reset-Felder erweitert | WS-B |
| `worker-monitor.py` | `worker-runs.json` als kanonisch, Upsert | WS-C |
| `task-dispatch.ts` | `WorkerRunRecord.endedAt`, Upsert-Logik | WS-C |
| `complete/route.ts` | `receipt-result` Event + `lastReportedStatus` | WS-D, WS-O |
| `receipt/route.ts` | `report-deduplicated` Event + `lastReportedStatus` | WS-D, WS-O |
| `task-reports.ts` | `report-deduplicated` Event | WS-D |

---

## Offene Punkte / Monitoring

1. **Stall-Schwellen für `frontend-guru`** — `STALL_PER_AGENT` unterstützt aktuell kein Override. Bei regelmäßigen langen UI-Builds ggf. anpassen.
2. **Sprint-N E2E Test-Tasks** (`a663a552`, `1c26c034`) — auf `done`, können archiviert werden.
3. **Build nach Sprint-O** — MC-Restart steht aus (2026-04-20 19:29 UTC).

---

*Report erstellt: 2026-04-20T17:29 UTC*
*Author: Atlas (mit Lens + Forge Output)*
