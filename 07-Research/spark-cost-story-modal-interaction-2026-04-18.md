# Cost-Story Modal — Interaction Design
**Base:** `spark-cost-story-ux-concept.md` (Pack 8, Zone C)
**Type:** Interaction Design Artifact
**Date:** 2026-04-18
**Word target:** ≤ 500 + state diagram

---

## State Diagram

```
Modal State Machine
====================

[Idle] --open--> [Loading]
                  │
            data fetch OK
                  │
                  ▼
             [Populated] <-- refresh / tab switch
                  │
            ┌─────┴──────┐
      expand row   copy   flag   close
            │        │      │       │
            ▼        ▼      ▼       ▼
      [Expanded]  [Copied] [Flagged] [Closed]
                         └──────────────┘
                                │
                         back to [Populated]

Error path:
[Loading] --fetch error--> [Error: Retry]
[Populated] --fetch fail--> [Error: Retry]
```

**State descriptions:**
- `Idle` — modal closed, no data in memory
- `Loading` — initial fetch in flight (spinner visible, content skeleton)
- `Populated` — data loaded, timeline + narrative rendered
- `Expanded` — a row was expanded for tool-detail drill-down
- `Copied` — copy confirmed (flash feedback, 1.5 s)
- `Flagged` — issue flagged (confirmation toast, 2 s)
- `Error: Retry` — fetch failed, retry button shown
- `Closed` — modal dismissed, state cleared

---

## Interaction Timing

| Trigger | Action | Timing |
|---------|--------|--------|
| Click "Cost Story" trigger | Open modal, begin data fetch | < 200 ms to skeleton |
| Data fetch success | Render timeline + narrative | < 500 ms |
| Data fetch fail | Show error state + retry | immediate |
| Hover row | Subtle highlight (#f5f5f5 → #ebebeb) | 150 ms ease |
| Click row to expand | Expand row inline, show tool detail | 200 ms ease-out |
| Click "Copy Summary" | Copy to clipboard, flash green | 1.5 s then reset |
| Click "Flag Issue" | Open flag dialog, confirm | modal, no timeout |
| Click "X" or outside | Close, clear state | < 100 ms |
| Tab switch (Today/7d/30d) | Re-fetch, loading skeleton | skeleton immediate |
| Refresh | Re-fetch same window | skeleton + spinner |

**Skeleton:** During Loading state, render three skeleton rows (grey bars matching timeline row height) — not a spinner — to signal structure is loading.

**Narrative generation:** If AI narrative is server-generated, add `gen: ~800 ms` after data fetch. Show a subtle "Generating narrative…" label inline, below the timeline, during that window.

---

## Hover, Click, Empty, Error States

**Hover:** Row background shifts from transparent to `#ebebeb` over 150 ms. Cursor: pointer on actionable rows.

**Click:** Row expands in-place with `max-height` transition (0 → auto, 200 ms ease-out) revealing tool-detail block. Chevron rotates 90°.

**Empty state:** When the selected window has no events, render:
```
┌──────────────────────────────────────────────┐
│  No cost events in this window.               │
│  Try "Today" or expand the date range.       │
│                        [Clear filter]        │
└──────────────────────────────────────────────┘
```
Do not show a blank modal — always render the full chrome with the empty-state message inside the timeline area.

**Error state:**
```
┌──────────────────────────────────────────────┐
│  ✕  Failed to load cost story.               │
│  Check your connection and try again.         │
│                        [Retry]  [Close]     │
└──────────────────────────────────────────────┘
```
No automatic retry — operator must click Retry to preserve control.

---

## Micro-Animations

| Element | Animation |
|---------|-----------|
| Modal entrance | `opacity: 0→1, translateY: 8px→0`, 200 ms ease-out |
| Modal exit | `opacity: 1→0, translateY: 0→8px`, 150 ms ease-in |
| Row expand | `max-height: 0→content`, 200 ms ease-out, overflow hidden |
| Row collapse | reverse of expand, 150 ms ease-in |
| Copy flash | Row background flashes `#d4edda` (green) for 1.5 s |
| Flag confirmation | Toast slides in from top-right, 300 ms, auto-dismiss 2 s |
| Skeleton rows | Shimmer: `background-position` slides left→right, 1.2 s loop |
| Status badge transition | Cross-fade between Normal ↔ Elevated ↔ Critical, 300 ms |

---

## Accessibility Checklist

- [ ] Modal has `role="dialog"` and `aria-modal="true"`
- [ ] Focus is trapped inside modal while open; returned to trigger on close
- [ ] Keyboard: `Esc` closes, `Tab` cycles through interactive elements, `Enter` on rows expands
- [ ] All color state indicators (Normal/Elevated/Critical) paired with text or icon — never color alone
- [ ] Status badge `aria-label` includes human-readable state: `aria-label="Cost status: Normal, $0.042 total"`
- [ ] Copy button has `aria-label="Copy cost summary to clipboard"`
- [ ] Flag button has `aria-label="Flag this cost for review"`
- [ ] Expanded row has `aria-expanded="true"` on the triggering row
- [ ] Error state announces via `role="alert"` so screen readers read the error automatically
- [ ] Timeline table has `aria-label="Cost event timeline"` on the `<table>` element
- [ ] Focus outline visible (no `outline: none` without replacement)
- [ ] Modal contrast ratio: text on background ≥ 4.5:1 (WCAG AA)

**Delta vs. prior concept:** The prior wireframe showed a header badge with `● Normal`. The interaction model specifies the badge must be announced as `Cost status: Normal` via `aria-label` — pure visual color + dot is insufficient for a11y compliance.

---

*Spark · 2026-04-18 · No code · Input for Pixel implementation*
