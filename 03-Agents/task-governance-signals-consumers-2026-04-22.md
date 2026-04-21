---
title: task-governance-signals Consumer Inventory
created: 2026-04-22
purpose: S-RPT T1 Reader-Hygiene Pre-Flight — vollständige Liste aller Consumer bevor resultSummary/resultDetails aus primärem Signal-Pfad entfernt werden
scope: MC-Source + Tests (Crons checked, 0 Treffer)
source-of-data: grep-based inventory 2026-04-22 ~23:10 UTC
---

# `task-governance-signals` Consumer Inventory

## Summary

| Metric | Count |
|---|---|
| **Library public exports** | 1 function + 1 type |
| **Direct consumers (use `getTaskGovernanceSignals`)** | 1 (+1 test) |
| **`resultSummary` reader-sites** (for derived decisions) | 7 |
| **`resultDetails` reader-sites** | 3 |
| **`resultSummary/Details` writer-sites** (mutation/input) | 8 |
| **UI-components with governance-signal display** | 3 |
| **Crons/Scripts referencing governance-signals** | 0 |

---

## A. Library Exports — `src/lib/task-governance-signals.ts` (67 LoC)

```typescript
export type GovernanceSignal = {
  key: 'approval-required' | 'security-gate' | 'review-pending' | 'manual-recovery';
  label: string;
  tone: string;
  detail: string;
};

export function getTaskGovernanceSignals(task: Task): GovernanceSignal[] { ... }
```

**Interne Logik (RELEVANT für S-RPT T1!):**
```typescript
const blockerText = [
  task.blockerReason,
  task.blockedReason,
  task.failureReason,
  task.lastFailureReason,
  task.resultSummary,    // ← S-RPT T1 Ziel: entfernen
  task.resultDetails     // ← S-RPT T1 Ziel: entfernen
]
.filter(Boolean).join(' ').replace(/\s+/g, ' ').trim();

const APPROVAL_PATTERN = /\b(approval|approved|freigabe|sign-off|signoff|operator review|decision|policy|permission|access pending|approval required)\b/i;
const REVIEW_PATTERN   = /\b(review pending|review ausstehend|awaiting review|wartet auf review)\b/i;
```

4 Signal-Typen werden generiert:
1. `security-gate` — triggert nur über strukturierte Felder (`task.securityRequired`, `task.securityStatus`) — ✅ S-RPT-konform
2. `review-pending` — triggert auf **`task.status === 'review'` ODER `executionState === 'review'` ODER `REVIEW_PATTERN` matched blockerText** (welcher resultSummary/resultDetails enthält!) — 🔴 **S-RPT T1 Refactor-Target**
3. `approval-required` — triggert ausschließlich über `APPROVAL_PATTERN` matching blockerText — 🔴 **Risk: wenn resultSummary/resultDetails raus → Signal evtl. 100% verloren falls nicht in strukturiertem Feld**
4. `manual-recovery` — triggert nur über `task.maxRetriesReached` + liest `lastFailureReason/failureReason` für `detail` — ✅ S-RPT-konform

---

## B. Direct Readers of `getTaskGovernanceSignals`

| # | Path:Line | Kategorie | Risk-if-broken |
|---|---|---|---|
| 1 | `src/lib/taskboard-governance-overview.ts:1` | MC-Backend-Aggregator | **Critical** — Board-Übersicht shows Governance-Count |
| 2 | `tests/task-governance-signals.test.ts:3` | Test | Low — needs Fixture-Updates nach P0.1 |

---

## C. `resultSummary` / `resultDetails` Reader-Sites (für derivierte Decisions)

### 🔴 High-Risk Reader (S-RPT T1 Refactor nötig)

| # | Path:Line | Reads | Usage |
|---|---|---|---|
| R1 | `src/lib/task-governance-signals.ts:17` | resultSummary + resultDetails | concatenated zu blockerText (APPROVAL/REVIEW regex match) |
| R2 | `src/components/taskboard/task-card.tsx:285-292` | resultSummary | **Display** in Card wenn `status === 'done'` — OK (cosmetic, not decision) |
| R3 | `src/components/taskboard/taskboard-client.tsx:508` | resultSummary | **Search-Query Match** (user-typed filter) — OK (search tool, not governance decision) |
| R4 | `src/components/taskboard/taskboard-client.tsx:774` | resultSummary | **Text-Fallback** wenn blockerReason/blockedReason/description fehlen — Medium Risk |
| R5 | `src/components/taskboard/task-detail-modal.tsx:116-159` | resultSummary + resultDetails | **Input-Form populate** — OK (user-edits, not machine) |
| R6 | `src/components/taskboard/task-detail-modal.tsx:364` | resultSummary | Timeline-Stage-Detail (`stage: 'result'`) — Medium Risk |

### 🟢 Writer-Only Sites (nicht S-RPT T1 Scope)

| # | Path:Line | Was geschrieben wird |
|---|---|---|
| W1 | `src/app/api/tasks/[id]/receipt/route.ts:83,128,176,177,334,468,572` | receipt-payload writes resultSummary/resultDetails aus Worker-Body; **validation:** `stage === 'result' && !body.resultSummary.trim()` → 400 |
| W2 | `src/app/api/tasks/[id]/finalize/route.ts:45,105` | finalize endpoint reads task.resultDetails für patch |
| W3 | `src/app/api/tasks/[id]/admin-close/route.ts:18,19,72,73` | admin-close: `overrideStatus === 'done' && !body.resultSummary.trim()` → 400 |
| W4 | `src/app/api/tasks/[id]/move/route.ts:18,128` | move endpoint accepts resultSummary im body |

---

## D. UI-Components with Governance-Signal Display

| Component | File | Signals shown |
|---|---|---|
| TaskCard | `src/components/taskboard/task-card.tsx` | resultSummary text block (no governance-signal call) |
| TaskboardGovernanceOverview | `src/lib/taskboard-governance-overview.ts` | **Direct consumer of getTaskGovernanceSignals** |
| TaskDetailModal | `src/components/taskboard/task-detail-modal.tsx` | resultSummary/resultDetails input form |

**Kein anderer UI-Consumer**. `NBA-Indicator`, `Pipeline-Tab`, etc. rufen `getTaskGovernanceSignals` nicht direkt auf.

---

## E. Crons / Scripts — 0 Treffer

`grep -rn task-governance-signals /home/piet/.openclaw/scripts/ /home/piet/.openclaw/workspace/scripts/` = keine Treffer. Crons konsumieren das Signal **nicht** direkt.

---

## F. Recommended Dual-Path-Boundaries (für S-RPT T1)

### Feature-Flag `GOV_SIGNAL_SOURCE=strict|legacy|both` muss aktiv sein in:

| Location | Reason |
|---|---|
| `task-governance-signals.ts:17` | **Zentraler Switch-Point.** `strict` = blockerText excludes resultSummary/resultDetails; `legacy` = heutige Behavior; `both` = generiert beide Signal-Sets für Diff-Vergleich |
| `taskboard-governance-overview.ts` | Aggregator liest Environment-Flag + routes zur korrekten Impl |

### Flag **nicht nötig** in:

- UI-Display-Sites (R2, R3, R5) — das sind `resultSummary`-Reads für Anzeige/Input, keine Governance-Decisions
- Writer-Sites (W1-W4) — schreiben ist Audit-Pfad, bleibt erhalten
- R4 (taskboard-client:774) — ist Fallback-Display, nicht governance-logic

---

## G. High-Risk Sites für S-RPT T1 Refactor

| # | Site | Warum High-Risk | Mitigation |
|---|---|---|---|
| 1 | **`task-governance-signals.ts:17-19` blockerText builder** | Zentral — alle 4 Signale hängen daran | Dual-Path-Flag + 10 Fixture-Tasks vor Switch |
| 2 | **`approval-required` regex** | Wenn resultSummary raus aus blockerText, geht Signal 100% verloren falls approval-keyword nur dort steht | **Before refactor:** N=270 Terminal-Tasks scannen, für wie viele gilt: "approval-required wird ausgelöst ABER nur über resultSummary/resultDetails matched" → baseline ermitteln |
| 3 | **`review-pending` regex fallback** | Trigger hat 3 Wege (status='review', executionState='review', REVIEW_PATTERN) — wenn REVIEW_PATTERN nur über resultSummary triggert, dürfte kleine Differenz sein | Post-refactor: metric `signals_triggered_by_status_field` vs. `by_blockerText` vor/nach |
| 4 | **Tests `task-governance-signals.test.ts`** | Bestehende Tests benutzen evtl. resultSummary zum Triggern | Erst Test-Fixtures auditen, dann Refactor |

---

## H. Concrete S-RPT T1 Action-List (für Codex/Forge)

1. **Pre-Fix-Measurement** (30 min):
   - `curl /api/tasks | jq '.tasks | map(select(.status in ["done","failed","blocked"])) | ...'` — wie oft triggert approval-required aktuell?
   - Count: `N_triggered_by_status` vs `N_triggered_by_resultSummary_only`

2. **Fix-Pattern:**
   ```typescript
   // Feature-flag controlled blockerText
   const blockerText = [
     task.blockerReason,
     task.blockedReason,
     task.failureReason,
     task.lastFailureReason,
     ...(process.env.GOV_SIGNAL_SOURCE === 'legacy' || process.env.GOV_SIGNAL_SOURCE === 'both'
         ? [task.resultSummary, task.resultDetails]
         : [])
   ].filter(Boolean).join(' ')...
   ```

3. **New Test-Fixtures:**
   - Task mit `approval` only in `blockerReason` → triggers both modes
   - Task mit `approval` only in `resultSummary` → triggers legacy, NOT strict
   - Task mit `status='review'` → triggers both modes regardless of flag
   - 10 total Fixtures covering all 4 signal types + both modes

4. **Post-Fix-Validation:**
   - Signal-Drop ≤15% auf terminalen Tasks über 72h (Critic-Pflicht aus Plan)
   - `taskboard-governance-overview.ts` aggregates keep structure

5. **Fallback wenn signal-loss > 15%:**
   - Add new structured field `task.governanceHint: 'approval' | 'review' | null` als first-class Schema
   - Writer-Migration (P0.2b): Worker emittiert diese hint explizit, nicht mehr via resultSummary-string

---

## Reproducibility

```bash
# Direct consumers
ssh homeserver "grep -rn 'task-governance-signals\|taskGovernanceSignals' /home/piet/.openclaw/workspace/mission-control/src/ /home/piet/.openclaw/workspace/mission-control/tests/ --include='*.ts' --include='*.tsx'"

# resultSummary/resultDetails reader sites
ssh homeserver "grep -rn 'resultSummary\|resultDetails' /home/piet/.openclaw/workspace/mission-control/src/ --include='*.ts' --include='*.tsx'"

# Full signal body
ssh homeserver "cat /home/piet/.openclaw/workspace/mission-control/src/lib/task-governance-signals.ts"
```

---

## Next-Actions (Handoff to S-RPT T1 Owner)

| ID | Owner | Priority | Due | Reason |
|---|---|---|---|---|
| `gov-prefix-measurement` | codex | P0 | before-refactor | baseline N_triggered_by_status vs resultSummary-only |
| `gov-flag-implementation` | codex | P0 | T1 scope | add GOV_SIGNAL_SOURCE flag + dual-path |
| `gov-test-fixtures` | codex | P0 | T1 scope | 10 new Fixture-Tasks covering both modes |
| `gov-signal-loss-monitoring` | atlas | P1 | 72h post-deploy | metric signal-drop ≤15% |
| `gov-hint-field-fallback` | forge | P2 | if signal-loss > 15% | new structured field + writer-migration (P0.2b) |
