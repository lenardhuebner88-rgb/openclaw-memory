---
title: "Pixel P1 Taskboard v2 — Pre-Flight Analysis (2026-04-20)"
date: 2026-04-20
status: READY_TO_DISPATCH_AFTER_TERMINAL_CLAUDE_DEPLOY
scope: Sprint-M P1 Implementation of Claude Design V2.4 Handoff
prerequisite: Lifecycle-bypass fix deployed (Terminal-Claude work in progress)
---

# Pixel P1 Pre-Flight Analysis

**Purpose:** Audit-ergebnisse + Implementation-plan für Pixel Board-Task **vor** Dispatch.
Ensures zero-surprise execution: alles verifiziert, Conflict-Risk gemanaged.

---

## 1. Handoff-Bundle Audit (complete)

**Location:** `/home/piet/vault/03-Agents/claude-design-handoffs/2026-04-20-taskboard/`
**Status:** VERIFIED — 10 files / 212 KB

### File-Inventory

| File | Size | Content |
|---|---|---|
| `design-canvas.jsx` | 10 KB | Overview canvas mit allen frames |
| `mc-mobile-shared.jsx` | 13 KB | Shared Mobile primitives (StatusPill, AgentBadge, LaneChip, etc.) |
| `mc-tokens.css` | 18 KB | CSS custom properties — brand tokens, spacing, radii |
| `mc-v1.jsx` | 11 KB | V1 Evolutionary Refinement reference |
| `mc-v2.jsx` | 23 KB | **V2 Radical Mobile-Only (iPhone 14 390×844)** |
| `mc-v2-responsive.jsx` | 27 KB | **V2 + Tablet 768 + Desktop 1440** |
| `mc-v2-states-canvas.jsx` | 18 KB | Interaction-states canvas overview |
| `mc-v2-states.jsx` | 29 KB | **5 Modal-states** (Details mobile/desktop, Admin, Retry, Command Palette, AllClear, QuietEmpty) |
| `Taskboard v2 - Mobile Redesign.html` | 33 KB | Rendered standalone HTML prototype |
| `tokens.js` | 7 KB | Shared token object (JS) |

### Modal-States Completeness (CONFIRMED)

Despite Claude Design hitting usage-limit during final polish, **alle 5 Modals sind strukturell vorhanden** in `mc-v2-states.jsx`:

```
const SAMPLE_DETAIL_TASK = { ... }              ← Sample data
function Scrim({ children, onClose }) ...       ← Generic modal scrim
function DetailsSheetMobile({ task })  ...      ← ✅ Mobile bottom-sheet (88% height)
function DetailsModalDesktop({ task }) ...      ← ✅ Desktop centered 640px
function DetailsBody({ task, wide })   ...      ← Shared body-content
function AdminConfirmDialog({ width=440 }) ...  ← ✅ Admin cleanup (rose-tinted)
function RetryConfirmDialog({ used, cap })  ... ← ✅ Retry confirm (violet, 2/3 display)
function DialogBtn(...)                ...      ← Generic dialog button
const CMD_ITEMS = [ ... ]                       ← Command items list
function CommandPalette({ mobile, selectedIdx })← ✅ ⌘K palette (mobile + desktop)
function AllClearHero() ...                     ← ✅ Bonus: 0-incident hero-state
function QuietEmptyLane({ message })   ...      ← ✅ Bonus: empty-lane primitive
```

**Implication:** My earlier "Usage-Limit-Warning" in Pixel prompt was OVERLY CAUTIOUS. Task body updated — Pixel kann direkt mit den Specs arbeiten, nicht inferenz-pflichtig für Modals.

---

## 2. Existing MC Component Audit (reuse-ready)

**Location:** `/home/piet/.openclaw/workspace/mission-control/src/components/taskboard/`

| Component | Size | Re-Use Strategy |
|---|---|---|
| `taskboard-client.tsx` | 57 KB | **Minor UI-layer edits only.** Add mobile-single-lane-focus + MorningStatusHero mount. NO state-management refactor. |
| `task-card.tsx` | 13 KB | **Minor enhance.** useSwipe already wired. Add ghost-chevron-indicators für first-view swipe-affordance. |
| `task-detail-modal.tsx` | 36 KB | **Extend.** Add responsive variant: mobile = 88% sheet, desktop = 640px modal. Preserve existing logic. |
| `agent-load-panel.tsx` | 6.5 KB | **Re-use as-is.** Bereits in right-rail deployable. |
| `activity-feed.tsx` | 8 KB | **Re-use as-is.** Ready für right-rail. |
| `system-pulse.tsx` | 6.8 KB | **Re-use as-is.** Heartbeat-Sparkline source logic. |
| `new-task-modal.tsx` | 12.5 KB | **Unchanged.** Not affected. |
| `today-focus.tsx` | 5.5 KB | **Unchanged.** Not affected. |

### Shared Infrastructure (re-use)

- `src/hooks/use-swipe.ts` — already wired in task-card.tsx + task-detail-modal.tsx
- `src/hooks/use-pull-to-refresh.ts` — available
- `src/components/command-palette.tsx` — exists, needs extension für CMD_ITEMS-pattern
- `src/components/bottom-tab-bar.tsx` — 60px+ tap-targets (from Sprint-I)
- `src/components/bulk-action-bar.tsx` — FAB-offset ready

### New Components (Pixel creates)

**Only 1 truly new component needed:**
- `src/components/taskboard/MorningStatusHero.tsx` — NEW

Plus 2 new dialog components (can live in `src/components/ui/` or `src/components/taskboard/`):
- `AdminConfirmDialog.tsx`
- `RetryConfirmDialog.tsx`

---

## 3. Token-Merge Analysis (mc-tokens.css vs globals.css)

**Source:** `/home/piet/vault/03-Agents/claude-design-handoffs/2026-04-20-taskboard/mc-tokens.css` (18 KB)
**Target:** `/home/piet/.openclaw/workspace/mission-control/src/app/globals.css`

**Strategy:** Merge additive — keine Überschreibungen existing violet brand tokens. Pixel soll:
1. mc-tokens.css durchgehen
2. Tokens die in globals.css FEHLEN, additiv hinzufügen
3. Tokens die in globals.css EXIST, Werte vergleichen — bei Delta: Claude Design = source-of-truth für v2-spezifische Tokens, MC = source-of-truth für brand-constants
4. Document alle merge-decisions in Delta-Report

---

## 4. Responsive-Breakpoint-Strategy

| Viewport | Existing Desktop | Claude Design V2 Output | Pixel Strategy |
|---|---|---|---|
| **<768px (mobile)** | 2-col lanes (cramped) | MorningStatusHero + single-lane-focus + chip-swap | **Replace** existing mobile-taskboard-layout with V2 |
| **768-1023px (tablet)** | (unklar, wahrscheinlich 2-col) | 2-col grid + hero full-width | **New implementation** based on responsive variant |
| **≥1024px (desktop)** | 5-lane grid + right-rail | Same 5-lane + horizontal strip-hero + right-rail | **Add hero strip above existing grid**, keep grid + right-rail |

---

## 5. Dispatch Prerequisites (sequential)

**Before Pixel-Task can be safely dispatched:**

✅ **1. Lifecycle-bypass fix deployed** (Terminal-Claude's current work):
   - Sonst könnte Pixel-Task selbst Bypass auslösen (wie b5f27 heute morgen)
   - Terminal-Claude muss: tests green + commit + mc-restart-safe + live-probe (409 on direct activation)

✅ **2. H12 deployed + verified** (Board-State-Machine-Fix):
   - Task `92cef72c-9dae-4687-8627-ef2b52cf52de` (Forge)
   - Verhindert dass Pixel's Task als canceled/failed geschlossen wird falls state-machine edge-cases
   - Status-Check needed vor Dispatch

⚠️ **3. Ghost-tasks cleanup nach H12 live** (siehe Atlas orchestration plan):
   - 1b1a5c90 H3, 55bfa0b2 H8-Forge-Retry, 855153b6 L1-Finalize
   - Alle re-patchen zu `done` mit korrektem resultSummary
   - Nicht zwingend vor Pixel-Dispatch, aber sauberer Board-State

---

## 6. Success Metrics

**Post-Pixel-Deploy verification:**

- [ ] `http://localhost:3000/taskboard` lädt auf Mobile 390 with MorningStatusHero visible
- [ ] Single-lane-focus chip-swap funktional on mobile
- [ ] Swipe-actions on task-cards trigger correctly
- [ ] Desktop 1440 zeigt 5-lane + horizontal-strip-hero + right-rail
- [ ] Details modal responsive: mobile sheet vs desktop 640px
- [ ] Admin cleanup + Retry confirm dialogs functional
- [ ] Command palette ⌘K öffnet mit CMD_ITEMS
- [ ] All-clear state shows when 0 incidents
- [ ] Empty-lane states zeigen "Nothing waiting"
- [ ] **Visual match vs Claude Design prototype ≥95%**

---

## 7. Risk-Register

| Risk | Severity | Mitigation |
|---|---|---|
| Pixel dispatched BEFORE Terminal-Claude's Lifecycle-fix deployed | 🔴 HIGH | **Wait for deploy signal** — explizit post-commit-Message |
| MC Build breaks on new component (TypeScript errors) | 🟡 MED | Pixel runs `npm run build` + `npm run typecheck` before mc-restart-safe |
| Taskboard-client state-management regression | 🟡 MED | Pixel forbids state-layer edits in task-body |
| Visual-delta >5% vs prototype | 🟢 LOW | Delta-report + optional micro-iteration |
| Merge-conflict with H12 files | 🟡 MED | Verify H12 done + git log before Pixel starts |
| Responsive breakpoint regression on existing desktop | 🟡 MED | Pixel tests at 3 viewports explicitly |

---

## 8. Dispatch Readiness-Checklist

**Before POST /api/tasks:**

- [x] Handoff-bundle audited (10 files, modals complete)
- [x] Existing-component inventory done
- [x] Pixel task-body drafted (vault/03-Agents/pending-sprint-k-tasks/pixel-p1-*)
- [x] Pre-flight analysis document (this file)
- [ ] Terminal-Claude deploy done + verified (live 409 on direct-activation)
- [ ] H12 Board-State-Machine-Fix deployed
- [ ] Current worker-monitor-log zeigt new-prompts (not legacy)
- [ ] Board clean (no stuck pending-pickup tasks from lifecycle-fix deploy)

**Dispatch-Commands (ready to POST):**

```bash
# After all prerequisites met:
ssh homeserver "curl -sS -X POST http://localhost:3000/api/tasks \
  -H 'Content-Type: application/json' \
  -H 'x-actor-kind: human' -H 'x-request-class: write' \
  -d @/home/piet/vault/03-Agents/pending-sprint-k-tasks/pixel-p1-taskboard-v2-task.json"

# Then (extract task-id from response):
ssh homeserver "curl -sS -X PATCH http://localhost:3000/api/tasks/<id> \
  -H 'Content-Type: application/json' \
  -H 'x-actor-kind: human' -H 'x-request-class: write' \
  -d '{\"status\":\"assigned\"}'"

ssh homeserver "curl -sS -X POST http://localhost:3000/api/tasks/<id>/dispatch \
  -H 'Content-Type: application/json' \
  -H 'x-actor-kind: human' -H 'x-request-class: admin' \
  -d '{\"agentId\":\"frontend-guru\"}'"
```

---

## 9. Post-Dispatch Monitoring

**Expected Timeline:**
- 0-60s: Auto-Pickup triggers Pixel worker
- 60s-2min: Pixel sends `accepted` receipt → status promoted to `in-progress` (canonical path, post-fix)
- 2min-5h: Progress-receipts per commit (6 atomic commits planned)
- 5-6h: Result receipt mit file-list + screenshots

**Monitoring-Hooks:**
- Auto-Pickup-Log tail — verify trigger success
- Worker-monitor-log — verify no stalled-warning false-positive
- Board-events-jsonl — verify state-transitions canonical
- 409-counter — if Terminal-Claude fix working, NO 409s should happen für pixel-task

---

*Generated 2026-04-20. Updated when Terminal-Claude deploy complete.*
