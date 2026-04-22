---
sprint-id: S-HEALTH
title: Board-Health Cleanup — Legacy-Data-Hygiene (145 consistency-issues)
created: 2026-04-22
status: done
priority: P1
owner: { orchestration: Atlas, inventory: Codex, pattern-analysis: Forge, bulk-close: Forge, manual-review: Operator }
depends-on: []
enables: [/api/health = ok]
source-evidence: "2026-04-22 post-Sprint-M-Close: /api/health degraded mit board.issueCount=145 + dispatch.consistencyIssues=145. Operator-Analyse: 156 terminal tasks ohne finalReportSentAt, 33 stale blockerReasons, 14 maxRetriesReached."
anti-goals:
  - Keine neuen Tasks erstellen
  - Keine Code-Changes an MC-Backend (nur Daten-Cleanup)
  - Keine Re-Execution von tasks (nur status/flags bereinigen)
  - Kein Parallel-Start von S-RELIAB-P1 oder anderen Sprints während Cleanup
pre-flight-gates:
  - Sprint-M v1.2.1 formal closed
  - Backup: tasks.json.bak-pre-s-health-<ISO>
---

# S-HEALTH: Board-Health Cleanup — Legacy-Data-Hygiene

## Problem

`/api/health` zeigt seit Cron-Drift-Resolution weiterhin `degraded`:
```
board.status: degraded (openCount=0, issueCount=145)
dispatch.status: degraded (consistencyIssues=145)
execution.status: degraded (recoveryLoad=2)
```

**Root-Cause:** 145 terminale Tasks (done/failed/canceled) haben **inkonsistente Finalize-Flags**:
- **156 tasks** ohne `finalReportSentAt` aber `status in [done,failed,canceled]`
- **33 tasks** mit stale `blockerReason` trotz terminal status
- **14 tasks** mit `maxRetriesReached=true` aber nicht terminal

Diese historischen Inkonsistenzen triggern Board- und Dispatch-Checks auf "degraded".

**Kein Sprint-M-Scope** — Sprint-M ist clean closed. Das ist **Legacy-Data-Hygiene** die sich akkumuliert hat.

## Scope

- Kategorisieren der 145 Issues nach Pattern
- Bulk-Close-Fixes für sichere Kategorien
- Manual-Review für unklare Fälle
- Root-Cause-Analyse warum Tasks ohne finalReportSentAt in terminal-state kommen
- Regression-Prevention-Note (für S-RPT Backfill-Task später)

## Out-of-Scope

- Code-Changes an worker-terminal-callback / finalize-route (→ S-RPT P0.2 Writer-Migration)
- Backfill-Script für SprintOutcome-Schema (→ S-RPT P0.2c)
- Neue Tasks erstellen oder dispatchen
- Cron-Mutations

## Tasks

### T1 — Inventory + Kategorisierung (Codex, ~45 min)
**Ziel:** Jede der 145 Issues einer von 5 Kategorien zuordnen.
**Deliverable:** `vault/03-Agents/s-health-inventory-2026-04-22.md` mit:
- Pro Kategorie: Count + Sample-IDs (max 5)
- 5 Kategorien:
  - **A1** `missing-finalReport` done-tasks (älter als 7d) → Kandidat für bulk-backfill
  - **A2** `missing-finalReport` recent-tasks (< 7d) → investigate cause
  - **B1** `stale-blockerReason` bei status=done → bulk-clear
  - **B2** `stale-blockerReason` bei status=failed → audit reason, keep if relevant
  - **C** `maxRetriesReached=true, status≠failed` → anomaly, individuelle Untersuchung
- Pattern-Hypothesen: welcher Code-Pfad schreibt inkonsistent?

**DoD:** Inventory-Doc + 5/5 Kategorien mit Counts + Pattern-Hypothesen.
**Anti-Scope:** Keine Bulk-Mutation hier — nur Read-Only-Inventory.

### T2 — Pattern-Analyse + Root-Cause (Forge, ~1h)
**Ziel:** Code-Pfad(e) identifizieren, die zu inkonsistenten Finalize-Flags führen.
**Deliverable:** Update `vault/03-Agents/s-health-inventory-2026-04-22.md` mit:
- Sektion "Root-Cause" mit 1-3 Hypothesen + Code-Pfade (`src/lib/taskboard-store.ts`, `src/app/api/tasks/[id]/finalize/route.ts`, etc.)
- Empfehlung: Fix-Location für S-RPT P0.2

**DoD:** Mindestens 1 hypothetisierter Code-Pfad + Referenz zu file:line.
**Anti-Scope:** Keine Code-Writes (Fix kommt in S-RPT P0.2).

### T3 — Bulk-Close-Script für Kategorie A1+B1 (Forge, ~1h)
**Ziel:** Safe bulk-close für eindeutige Fälle.
**Deliverable:** `/home/piet/.openclaw/scripts/s-health-bulk-close.py`
Logik:
- **A1 Kandidaten:** Alle `done`-tasks >7d ohne `finalReportSentAt`
  → Setze `finalReportSentAt = updatedAt` (best-effort-backfill)
- **B1 Kandidaten:** Alle `done`-tasks mit `blockerReason != null`
  → Clear `blockerReason` (done overrides blocker)

Backup: `tasks.json.bak-pre-s-health-<ISO>` vor Mutation.

**DoD:**
- Script läuft im Dry-Run-Mode mit Count-Preview
- Execute nur nach Operator-GO
- Post-Run: /api/health check

**Anti-Scope:** Kein Touch an A2 (recent-tasks), C (anomalies), B2 (failed-blockerReason).

### T4 — Manual-Review A2/B2/C (Operator + Atlas, ~30min)
**Ziel:** Unklare Fälle sichten, case-by-case entscheiden.
**Deliverable:** Discord-Post mit Pro-Kategorie-Entscheidung:
- A2 (missing-finalReport recent): re-send finalize ODER mark done ODER investigate?
- B2 (stale-blockerReason failed): blocker relevant ODER superseded?
- C (maxRetries mit non-terminal status): escalate ODER cancel?

**DoD:** Für jede Kategorie Operator-Decision dokumentiert.
**Anti-Scope:** Kein Bulk-Execute ohne Operator-GO.

### T5 — Verify /api/health=ok (Atlas, ~15min)
**Ziel:** Post-Cleanup Board-Health verifizieren.
**Deliverable:** Final Discord-Report mit:
- `/api/health` JSON (status, checks, metrics)
- Delta vs. pre-Cleanup (145 → N)
- Wenn noch degraded: Rest-Inventory

**DoD:** /api/health.status = "ok" ODER klarer Restbetrag mit Folgetask-Plan.

## Team-Split (zusammengefasst)

| Task | Primary-Owner | Sekundär | Effort |
|---|---|---|---|
| T1 Inventory | **Codex** (pattern-search) | Atlas (orchestrate) | ~45min |
| T2 Root-Cause | **Forge** (code-reading) | Codex (join) | ~1h |
| T3 Bulk-Close-Script | **Forge** (Python) | Atlas (review) | ~1h |
| T4 Manual-Review | **Operator** (decisions) | Atlas (present options) | ~30min |
| T5 Verify | **Atlas** (API-calls + report) | — | ~15min |

**Sequenz:** T1 → T2 (parallel-startbar) → T4 (nach T1 done) → T3 (nach T4 GO) → T5.

## Exit-Criteria

- `/api/health.status` = "ok"
- `dispatch.consistencyIssues` = 0 ODER clear Rest-Plan
- `board.issueCount` = 0 ODER categorical-reason dokumentiert
- Root-Cause in vault dokumentiert für S-RPT P0.2 Referenz
- Keine Task-Regressions (statische test-taskboard-tests grün)

## Rollback

Falls Bulk-Close-Script ungewollte Effekte:
```bash
cp /home/piet/.openclaw/workspace/mission-control/data/tasks.json.bak-pre-s-health-<ISO> \
   /home/piet/.openclaw/workspace/mission-control/data/tasks.json
systemctl --user restart mission-control.service
```

## Cross-References

- Sprint-M v1.2.1 (closed 2026-04-22) — Basis für clean state
- S-RPT P0.2c Backfill — tiefer Fix der Writer-Seite (folgt)
- Codex-Future-Plan-Protocol — Scope-Lock-Regeln für T1-T5

## Dispatch-Trigger (für Atlas)

```
Atlas — Sprint S-HEALTH Board-Cleanup starten.
```

Atlas liest dann `/home/piet/vault/04-Sprints/s-health-board-cleanup-2026-04-22.md` und dispatched gemäß Team-Split-Tabelle.
