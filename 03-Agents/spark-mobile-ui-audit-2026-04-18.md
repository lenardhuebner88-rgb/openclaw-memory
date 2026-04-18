# Mobile-UI Audit — Mission Control (360–414px Viewport)
**Date:** 2026-04-18
**Agent:** Spark
**Viewport:** 360px (primary), 414px (max)
**Confidence:** High on structural findings; medium on unseen pages marked ✱

---

## Tabs — Per-Tab Scores

| Tab | Readability (1–5) | Oper. Usefulness (1–5) | Top Problem | Fix |
|-----|------------------|------------------------|-------------|-----|
| Overview Hero | 2 | 4 | `text-4xl` KPIs overflow 360px | Scale KPI font with `clamp()` or `text-2xl` max on mobile |
| Costs | 3 | 3 | Tables hidden below md breakpoint (`hidden md:block`) | Progressive disclosure: summary cards visible, tables behind "Show more" |
| Taskboard | 3 | 4 | Intelligence buckets stack, `text-[10px]` labels unreadable | Raise labels to `text-xs` (12px), increase card tap target |
| Kanban | 3 | 3 | Horizontal scroll with tiny drag handles | Enable scroll-snap, make handles 44px tap target |
| Pipeline | 3 | 3 | `grid-cols-1` stacks fine but column widths fixed | Fluid column widths with `minmax(120px, 1fr)` |
| Team | 4 | 3 | Simple list, mostly readable | Avatar sizes fine; ensure `gap-3` stays on small screens |
| Agents | 3 | 3 | Workload bars truncate at narrow widths | Truncate agent name to 6 chars, bars scale to viewport |

**Readability scoring:** 1 = unusable, 3 = marginal, 5 = clean.  
**Oper. Usefulness:** 1 = no value on mobile, 5 = full operational capability.

---

## General Findings

**Tap Targets:** Kanban drag handles (`w-4 h-4` est.) are **below 44px** — WCAG violation. Cost progress bars are `h-3` (12px) — no tap target. Taskboard cards (`px-4 py-4`) and Overview Hero action cards are OK. Fix: drag handles need `min-h-[44px] min-w-[44px]`.

**Text Truncation:** Overview Hero uses `w-14 shrink-0 truncate` for agent names — at 360px likely cuts off. Taskboard labels at `text-[10px]` (~7px) are below legible minimum. Cost KPIs at `text-4xl` (56px) overflow a 360px row.

**Horizontal Overflow:** Kanban has `overflow-x-auto` — good direction, but no `scroll-snap`. Zone D workload bars at fixed `w-14` per agent overflow at 360px with 6 agents. Cost tables use `hidden md:block` — **data is hidden not reflowed** on mobile.

**Fixed-Width:** MissionShell correctly single-columns at mobile. But cost detail tables need progressive disclosure, not hide-on-mobile.

---

## ASCII Wireframe — Overview Hero Zone A at 360px

```
┌──────────────────────────┐
│ OVERVIEW   Leitstand  ● │
├──────────────────────────┤
│ ZONE B — NBA Banner      │
│ ⚡ Forge: 3/3 FULL      │
├──────────────────────────┤
│ ZONE A — Heartbeats     │
│ ┌─────┐┌─────┐┌─────┐  │
│ │ ●OK ││ ○   ││ ●OK │  │
│ │spark││forge││pixel│  │
│ └─────┘└─────┘└─────┘  │
│ ┌─────┐┌─────┐┌─────┐  │
│ │ ?   ││ ?   ││ ?   │  │
│ │lens ││james││atlas│  │
│ └─────┘└─────┘└─────┘  │
│ (3-col grid, 44px cards) │
├──────────────────────────┤
│ ZONE C — Activity       │
│ (5 items, compact mode)  │
│ 16:01 task done forge   │
│ 15:55 ⚠ anomaly minimax│
│ 15:48 task picked spark │
├──────────────────────────┤
│ ZONE D — Agent Bars     │
│ Forge ████████░░  3/3  │
│ (bars truncate names,    │
│  18-char bar width max)  │
└──────────────────────────┘
```

---

## Mobile Refactor Recommendations

### Priority 1 — First Sprint (High Impact, Low Effort)
1. **Audit all `text-4xl` → `text-2xl sm:text-3xl lg:text-4xl`** on KPI cards and cost headers. Font scales with viewport.
2. **Audit `text-[10px]` / `text-[11px]` → minimum `text-xs` (12px)`** on all labels. Smallest readable on 360px is 11px but 12px is safer.
3. **Add `scroll-snap-type: x mandatory`** to Kanban `overflow-x-auto` container. Users land cleanly on column boundaries.

### Priority 2 — Next Sprint (Moderate Effort)
4. **Reflow Cost tables** from `hidden md:block` to progressive disclosure: show summary KPI row on mobile, "View details" expands or navigates to dedicated cost detail page.
5. **Scale Overview Hero Zone D** agent bars: reduce bar char width from `w-14` to `max-w-[80px]` and truncate agent names to 6 chars on mobile.
6. **Increase Kanban drag handle tap target** to `min-h-[44px] min-w-[44px]`. Also add `cursor-grab` with `cursor-grabbing` on drag.

### Priority 3 — Later
7. **Zone A heartbeats:** collapse to summary badge ("6 agents, 4 healthy") instead of 6 tiny cards on one screen.
8. **Taskboard buckets:** collapse Now/Next/Later into a single scrollable feed on mobile.
9. **Never:** fixed-width data tables on mobile — use progressive disclosure or dedicated mobile pages.

---

*Spark · 2026-04-18 · No code · Input for Pixel mobile refactor sprint*
