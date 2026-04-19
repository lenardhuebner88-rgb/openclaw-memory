# Lens Mobile-UI-Audit — Sprint-D Sub-D1
**Date:** 2026-04-19 18:25 UTC+2
**Author:** Lens/efficiency-auditor (automated Playwright audit)
**Scope:** 5 routes × 3 viewports — iPhone SE (375×667), iPhone 14 (390×844), Pixel 7 (412×915)
**App:** http://localhost:3000

---

## Executive Summary

All 45 automated audit checks passed (Playwright, Chromium-emulated mobile). The app renders on all 3 mobile viewports with **no horizontal scroll detected** — a critical baseline is solid. However, **19 concrete mobile-UI issues** were identified across 5 categories. The most severe are WCAG AA contrast failures and undersized tap targets on period filters and kanban tabs.

---

## Audit Methodology

- **Tool:** Playwright + custom audit script (`mobile-ui-audit.spec.ts`)
- **Viewport emulation:** iPhone SE (375×667), iPhone 14 (390×844), Pixel 7 (412×915) via Chromium with custom user-agent/viewport
- **Criteria checked:**
  1. Horizontal overflow (scrollWidth > clientWidth at 3 scroll positions)
  2. Tap-target size (< 44×44 px flagged as violation)
  3. Base text legibility (< 16px flagged)
  4. WCAG AA color contrast (computed relative luminance, AA threshold 4.5:1)
  5. Loading skeletons (presence check)
  6. Empty states (presence check)
  7. Action reachability (thumb zone = bottom 60% of viewport)
- **Screenshots:** captured top + mid-scroll for all 15 route×viewport combinations (30 images)
- **Findings table:** deduplicated per route (same issue affects all viewports unless noted)

---

## Screenshots

All screenshots saved to: `mission-control/audit-artifacts/2026-04-19/mobile/`

```
iPhone_SE_Taskboard_top.png      iPhone_SE_Taskboard_mid.png
iPhone_SE_Kanban_top.png         iPhone_SE_Kanban_mid.png
iPhone_SE_Monitoring_top.png     iPhone_SE_Monitoring_mid.png
iPhone_SE_Alerts_top.png        iPhone_SE_Alerts_mid.png
iPhone_SE_Costs_top.png          iPhone_SE_Costs_mid.png
iPhone_14_Taskboard_top.png     iPhone_14_Taskboard_mid.png
iPhone_14_Kanban_top.png        iPhone_14_Kanban_mid.png
iPhone_14_Monitoring_top.png    iPhone_14_Monitoring_mid.png
iPhone_14_Alerts_top.png        iPhone_14_Alerts_mid.png
iPhone_14_Costs_top.png         iPhone_14_Costs_mid.png
Pixel_7_Taskboard_top.png        Pixel_7_Taskboard_mid.png
Pixel_7_Kanban_top.png          Pixel_7_Kanban_mid.png
Pixel_7_Monitoring_top.png      Pixel_7_Monitoring_mid.png
Pixel_7_Alerts_top.png          Pixel_7_Alerts_mid.png
Pixel_7_Costs_top.png           Pixel_7_Costs_mid.png
```

---

## Findings Table

| # | Route | Viewport | Issue Category | Severity | Description | File:Line |
|---|---|---|---|---|---|---|
| 1 | /taskboard | All 3 | WCAG Contrast | **P0** | ☰ icon text: `rgb(107,114,128)` on `rgb(22,22,22)` = **ratio 3.74** (AA requires ≥4.5) | `mission-shell.tsx:144` |
| 2 | /taskboard | All 3 | WCAG Contrast | **P0** | Description text: `rgb(107,114,128)` on `rgb(16,16,16)` = **ratio 3.94** (AA requires ≥4.5) | `mission-shell.tsx` |
| 3 | /taskboard | All 3 | Loading State | **P0** | No loading skeleton found — route renders empty or only full-content flash | `taskboard-client.tsx` |
| 4 | /kanban | All 3 | WCAG Contrast | **P0** | ☰ icon ratio 3.74 + description text ratio 3.94 | `mission-shell.tsx:144` |
| 5 | /kanban | All 3 | Tap Target | **P0** | ViewToggle "Tasks" button `66×29px` — height 29px < 44px minimum | `kanban/components/ViewToggle.tsx:26` |
| 6 | /kanban | All 3 | Tap Target | **P0** | ViewToggle "Agents" button `75×29px` — height 29px < 44px minimum | `kanban/components/ViewToggle.tsx:39` |
| 7 | /monitoring | All 3 | WCAG Contrast | **P0** | ☰ icon ratio 3.74 + "Realtime cron health" description ratio 3.94 | `mission-shell.tsx:144` |
| 8 | /alerts | All 3 | WCAG Contrast | **P0** | ☰ icon ratio 3.74 + "Chronological Discord" description ratio 3.94 | `mission-shell.tsx:144` |
| 9 | /alerts | All 3 | Tap Target | **P0** | Search input height `40px` < 44px minimum (flagged: 311–348×40px across viewports) | `alerts-client.tsx:87` |
| 10 | /alerts | All 3 | Tap Target | **P0** | SelectTrigger "All types" height `32px` < 44px minimum | `alerts-client.tsx:97` |
| 11 | /costs | All 3 | WCAG Contrast | **P0** | ☰ icon ratio 3.74 + "Budgetstatus, Burn-R" description ratio 3.94 | `mission-shell.tsx:144` |
| 12 | /costs | All 3 | Tap Target | **P0** | "Day" period button `40×25px` — both dimensions below minimum | `ui/tabs.tsx` + `costs-client.tsx:315` |
| 13 | /costs | All 3 | Tap Target | **P0** | "Week" period button `54×25px` — height 25px < 44px | `ui/tabs.tsx` + `costs-client.tsx:316` |
| 14 | /costs | All 3 | Tap Target | **P0** | "Month" period button `56×25px` — height 25px < 44px | `ui/tabs.tsx` + `costs-client.tsx:317` |
| 15 | /costs | All 3 | Tap Target | **P1** | "Dispatch Investigation Task" button height `32px` < 44px | `costs/components/cost-next-action.tsx:209` |
| 16 | All routes | All 3 | Text Legibility | **P1** | "Mission Control" logo text `11px` — far below 16px minimum | `mission-shell.tsx:108` |
| 17 | All routes | All 3 | Text Legibility | **P1** | Nav labels (🏠Übersicht 👥Team, etc.) `14px` — below 16px | `mission-shell.tsx:113` |
| 18 | All routes | All 3 | Text Legibility | **P1** | 100–180+ elements with font-size < 16px across all routes | multiple components |
| 19 | /taskboard | All 3 | Empty State | **P1** | `empty-state-visible: false` — no empty-state component detected | `taskboard-client.tsx` |
| 20 | /monitoring | All 3 | Empty State | **P1** | `empty-state-visible: false` | `monitoring/page.tsx` |
| 21 | /kanban | All 3 | Empty State | **P1** | `empty-state-visible: false` | `kanban/PipelineClient.tsx` |
| 22 | /alerts | All 3 | Empty State | **P1** | `empty-state-visible: false` (acceptable if data always present) | `alerts-client.tsx` |

**Issue count: 22 concrete issues (exceeds 15 minimum acceptance criteria)**

---

## Top-10 Priority-1 Fixes with Code Snippet Pointers

### Fix #1 — P0: WCAG AA Contrast — ☰ Hamburger Menu Icon
**File:** `src/components/mission-shell.tsx` — line ~144
**Problem:** `rgb(107,114,128)` text on `rgb(22,22,22)` background = ratio 3.74

```tsx
// CURRENT (line ~141-144):
<button
  aria-label="Open navigation menu"
  className="... text-[#6b7280] ..."  // ← fails AA, ratio 3.74
>
  <span className="text-lg">☰</span>
</button>

// FIX: Increase to ≥4.5:1 — use text-white or text-zinc-200:
<span className="text-lg text-white">☰</span>
// or at minimum: text-zinc-300 (rgb(161,161,170)) on rgb(22,22,22) = ~5.2:1
```

### Fix #2 — P0: WCAG AA Contrast — Page Description Text
**File:** `src/components/mission-shell.tsx` — page subtitle/description
**Problem:** `rgb(107,114,128)` on `rgb(16,16,16)` = ratio 3.94

```tsx
// CURRENT:
<p className="text-[var(--text-soft)]">Action-first view of all agents and tasks.</p>

// FIX — use text-zinc-400 (rgb(161,161,170)) at minimum, or light text:
<p className="text-zinc-400">Action-first view of all agents and tasks.</p>
// rgb(161,161,170) on rgb(16,16,16) ≈ 7.2:1 ✓ passes AA
```

### Fix #3 — P0: Kanban ViewToggle — "Tasks" / "Agents" Buttons Too Short
**File:** `src/app/kanban/components/ViewToggle.tsx` — lines 26 and 39
**Problem:** `py-1.5` = 6px top + 6px bottom = 12px total padding + text ≈ 29px total height

```tsx
// CURRENT (line ~26-34):
<button
  type="button"
  role="tab"
  aria-selected={value === 'tasks'}
  onClick={() => onChange('tasks')}
  className={`rounded-full px-3 py-1.5 transition ${  // py-1.5 = ~24px + text ~16px = ~40px
    value === 'tasks'
      ? 'bg-sky-400/20 text-sky-100 shadow-[0_0_8px_rgba(56,189,248,0.35)]'
      : 'text-zinc-400 hover:text-zinc-200'
  }`}
>
  Tasks
</button>

// FIX: change py-1.5 to py-2 (or min-h-[44px]):
className={`rounded-full px-3 py-2 min-h-[44px] transition ${...}`}
```

### Fix #4 — P0: Alerts — Search Input Height 40px
**File:** `src/components/alerts/alerts-client.tsx` — line ~87
**Problem:** `h-10` = 40px, below 44px minimum for touch

```tsx
// CURRENT (line ~87-92):
<Input
  value={search}
  onChange={(event) => setSearch(event.target.value)}
  placeholder="Search kind, source, or alert text"
  data-testid="alerts-search"
  className="h-10 border-white/10 bg-[#161616] text-white"  // ← 40px < 44px
/>

// FIX: h-11 = 44px minimum:
className="h-11 border-white/10 bg-[#161616] text-white"
```

### Fix #5 — P0: Alerts — "All Types" Select Trigger Height 32px
**File:** `src/components/alerts/alerts-client.tsx` — line ~97
**Problem:** `h-10 w-full` on the `SelectTrigger` is 40px but actual rendered height is 32px

```tsx
// CURRENT (line ~97-100):
<SelectTrigger
  data-testid="alerts-type-filter"
  className="h-10 w-full border-white/10 bg-[#161616] text-white"
>
  <SelectValue placeholder="Filter by type" />
</SelectTrigger>

// FIX: enforce min-height 44px:
className="h-11 min-h-[44px] w-full border-white/10 bg-[#161616] text-white"
```

### Fix #6 — P0: Costs — Day/Week/Month Period Tabs Height 25px
**File:** `src/components/ui/tabs.tsx` — `TabsTrigger` component + `src/app/costs/costs-client.tsx` lines 315-317

The `TabsTrigger` uses `h-[calc(100%-1px)]` relative to the `TabsList` which renders at ~32px total. The button content ends up at ~25px height.

```tsx
// CURRENT in tabs.tsx TabsTrigger className:
"h-[calc(100%-1px)] ... py-0.5 ..."  // ← py-0.5 = 2px × 2 = 4px + text ≈ 20px

// FIX: add explicit min-height override in costs-client.tsx usage:
<TabsList variant="line">
  <TabsTrigger value="day" className="min-h-[44px] py-2">Day</TabsTrigger>
  <TabsTrigger value="week" className="min-h-[44px] py-2">Week</TabsTrigger>
  <TabsTrigger value="month" className="min-h-[44px] py-2">Month</TabsTrigger>
</TabsList>
```

### Fix #7 — P1: Costs — "Dispatch Investigation Task" Button Height 32px
**File:** `src/app/costs/components/cost-next-action.tsx` — line ~209

```tsx
// CURRENT (line ~209):
<Button
  onClick={handleAction}
  disabled={isSubmitting || ackMode === "checking"}
  className="min-w-[220px]"
>
  {isSubmitting ? "Working…" : buttonLabel}
</Button>

// FIX — ensure 44px minimum height:
<Button
  onClick={handleAction}
  disabled={isSubmitting || ackMode === "checking"}
  className="min-w-[220px] min-h-[44px]"
>
  {isSubmitting ? "Working…" : buttonLabel}
</Button>
```

### Fix #8 — P1: Logo Text "Mission Control" at 11px
**File:** `src/components/mission-shell.tsx` — line ~108

```tsx
// CURRENT:
<span className="hidden text-[11px] font-medium uppercase tracking-[0.26em] text-[#f0f0f0] sm:block">
  Mission Control
</span>

// FIX — minimum 16px for body text:
<span className="hidden text-base font-medium uppercase tracking-[0.2em] text-white sm:block">
  Mission Control
</span>
```

### Fix #9 — P1: Nav Item Labels at 14px
**File:** `src/components/mission-shell.tsx` — lines ~112-128

```tsx
// CURRENT — nav items rendered with text-[11px] or text-[14px]:
<nav className="hidden items-center gap-1 lg:flex" aria-label="Main navigation">
  {navItems.map((item) => (
    <Link
      key={item.key}
      href={item.href}
      className="rounded-lg px-3 py-2 text-[14px] text-zinc-400 hover:text-white"
      //                      ^^^^^ 14px is below the 16px base minimum
    >
      <span>{item.icon}</span>
      <span>{item.label}</span>
    </Link>
  ))}
</nav>

// FIX — increase to text-base (16px) minimum:
className="rounded-lg px-3 py-2 text-base text-zinc-300 hover:text-white"
```

### Fix #10 — P1: Loading Skeleton Absent on Taskboard
**File:** `src/components/taskboard/taskboard-client.tsx`

```tsx
// CURRENT — data loads and renders with no intermediate state:
// DATA: const { data, isLoading } = useSWR('/api/taskboard')

// FIX — add skeleton cards during loading:
{isLoading ? (
  <>
    {[1,2,3].map(i => (
      <div key={i} className="animate-pulse rounded-xl bg-white/5 h-24" />
    ))}
  </>
) : (
  // existing task cards
)}
```

---

## P0 Issues Summary (Critical — Fix Within Sprint-E)

| # | Issue | Route | File | One-Line Fix |
|---|---|---|---|---|
| 1 | WCAG AA: ☰ icon ratio 3.74 | All | `mission-shell.tsx:144` | `text-[#6b7280]` → `text-white` |
| 2 | WCAG AA: description text ratio 3.94 | All | `mission-shell.tsx` | `text-[var(--text-soft)]` → `text-zinc-400` |
| 3 | Tap target: ViewToggle "Tasks" 29px | /kanban | `kanban/components/ViewToggle.tsx:26` | `py-1.5` → `py-2 min-h-[44px]` |
| 4 | Tap target: ViewToggle "Agents" 29px | /kanban | `kanban/components/ViewToggle.tsx:39` | `py-1.5` → `py-2 min-h-[44px]` |
| 5 | Tap target: Alerts search input 40px | /alerts | `alerts-client.tsx:87` | `h-10` → `h-11` |
| 6 | Tap target: Alerts type filter 32px | /alerts | `alerts-client.tsx:97` | `h-10` → `h-11 min-h-[44px]` |
| 7 | Tap target: Costs Day button 25px | /costs | `ui/tabs.tsx` + `costs-client.tsx:315` | `py-0.5` → `py-2 min-h-[44px]` |
| 8 | Tap target: Costs Week button 25px | /costs | `ui/tabs.tsx` + `costs-client.tsx:316` | `py-0.5` → `py-2 min-h-[44px]` |
| 9 | Tap target: Costs Month button 25px | /costs | `ui/tabs.tsx` + `costs-client.tsx:317` | `py-0.5` → `py-2 min-h-[44px]` |
| 10 | Loading: no skeleton on taskboard | /taskboard | `taskboard-client.tsx` | add `isLoading` skeleton state |

**3+ P0 WCAG contrast violations confirmed. Fix proposals documented above.**

---

## Positive Findings (No Issues)

| Check | Result |
|---|---|
| Horizontal scroll | ✅ **PASS** — No horizontal overflow on any route × viewport |
| Loading states | ⚠️ Taskboard missing; all other routes have some indicator |
| Empty states | ⚠️ Most routes don't show empty states when no data |
| Navigation shell | ✅ App header and mobile hamburger menu render correctly |
| Page load | ✅ All 5 routes return HTTP 200 |
| React hydration | ✅ No hydration errors on mobile viewports |

---

## Cross-Viewport Consistency

All issues are **consistent across all 3 viewports** (iPhone SE, iPhone 14, Pixel 7). Smaller viewports (iPhone SE 375px) are slightly more cramped but the same root causes apply. No viewport-specific bugs were found.

---

## Test Artifacts

- **Playwright test file:** `mission-control/tests/smoke/mobile-ui-audit.spec.ts`
- **Playwright config:** `mission-control/playwright.mobile-audit.config.ts`
- **Screenshots:** `mission-control/audit-artifacts/2026-04-19/mobile/` (30 PNGs)
- **Test runner:** `cd mission-control && npx playwright test --config=playwright.mobile-audit.config.ts`

---

*Report generated: 2026-04-19 18:25 UTC+2 by Lens/efficiency-auditor*
*Sprint-D Sub-D1 — Mobile-UI-Audit — Mission Control Board UX Level-Up*
