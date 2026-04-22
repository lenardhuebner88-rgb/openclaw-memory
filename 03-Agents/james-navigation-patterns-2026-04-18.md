# Navigation + Tab-Consolidation Patterns — Research for Mission Control Clean-Cockpit
**Task:** `af95bda3-f054-4491-891b-8a82d33d8c28`  
**Agent:** James  
**Date:** 2026-04-18  
**Status:** ✅ Completed  
**Scope:** Wave 6 Task 1 — navigation patterns and tab consolidation only

---

## Research Mandate

Reduce Mission Control's 13-tab navigation to 7 tabs. Document best-practice patterns for: (1) tab consolidation, (2) bottom-bar mobile behavior, (3) keyboard shortcuts. Sources: Linear, Notion, Cursor, Discord.

**Constraint:** Research only — no code, no implementation.

---

## Pattern 1 — Priority-Weighted Tab Bar

**Source:** Linear — sidebar navigation  
**URL:** `https://linear.app/docs/your-sidebar`  
**Confidence:** High

### Pattern Description
Tabs are weighted by operational priority. The most triage-critical tab (e.g., "Board" or "Inbox") appears leftmost and is visually prominent. Secondary tabs are quieter. Tertiary tabs collapse into an ellipsis menu.

### ASCII Wireframe

```
┌─────────────────────────────────────────────────────────────────┐
│  [📋 Board]  [📥 Inbox]  [→ Tasks]  [→ Cycles]  [⋯ More]     │
│  ▲ primary   ▲ secondary    collapsed      collapsed            │
└─────────────────────────────────────────────────────────────────┘
```

### Mission Control Applicability
MC has 13 tabs. Collapse 6 into "⋯ More":
- "Board", "Inbox", "Tasks" → keep visible
- "Deployments", "Analytics", "Settings" → ellipsis menu
- Reduce from 13 to 7 visible tabs: Board, Inbox, Tasks, Actors, Costs, Backlog, More

**Effort:** Low. Mostly routing/layout change.

---

## Pattern 2 — Keyboard-First Navigation

**Source:** Linear — keyboard shortcuts (`?` to open shortcut panel)  
**URL:** `https://linear.app/docs/keyboard-shortcuts`  
**Confidence:** High

### Pattern Description
Press `?` → overlay with all shortcuts. Navigation via `G then B` (go to board), `G then I` (go to inbox), `C` (create), `⌘K` (command palette).

### ASCII Wireframe

```
┌─────────────────────────────────────────────────────────────────┐
│                    ⌨ Keyboard Shortcuts                         │
│  ─────────────────────────────────────────────────────────────  │
│  G then B     Go to Board          ⌘K     Command palette      │
│  G then I     Go to Inbox         C       Create new task      │
│  G then T     Go to Tasks         ?       This overlay          │
│  Esc          Close / back                                    │
└─────────────────────────────────────────────────────────────────┘
```

### Mission Control Applicability
MC operators use keyboard heavily. Add `?` shortcut panel. Map `G+B` → Board, `G+I` → Inbox, `G+T` → Tasks. Command palette (`⌘K`) searches across all tabs.

**Effort:** Medium. Requires shortcut registry component.

---

## Pattern 3 — Active-State Breadcrumb Trail

**Source:** Notion — breadcrumb navigation in sidebar  
**URL:** `https://notion.so`  
**Confidence:** High

### Pattern Description
Current location shown as a trail of breadcrumbs, not just a highlighted tab. Allows operator to see exactly where they are and jump back to any ancestor.

### ASCII Wireframe

```
┌─────────────────────────────────────────────────────────────────┐
│  Board › Tasks › costs-v2               [+ New] [⋮]            │
│  ↑ breadcrumb trail                                           │
└─────────────────────────────────────────────────────────────────┘
```

### Mission Control Applicability
Useful when tabs have sub-views. Example: "Board › tasks › [task-id]" shows exactly where the operator is drilling. Prevents disorientation after deep navigation.

**Effort:** Low-medium. Breadcrumb component.

---

## Pattern 4 — Bottom Navigation Bar (Mobile)

**Source:** Discord — mobile tab bar  
**URL:** `https://discord.com`  
**Confidence:** High

### Pattern Description
On mobile/small screens, tabs move to a bottom bar. 4-5 icons max. Current tab has a filled icon + label; others show icon only.

### ASCII Wireframe

```
┌─────────────────────────────────────────────────────────────────┐
│  [Board]   [Inbox]   [Tasks]   [Costs]   [More ⋯]              │
│  ▲ current                                                  ▲    │
└─────────────────────────────────────────────────────────────────┘
```

### Mission Control Applicability
MC's mobile view (3102 viewport) needs bottom bar. 5 items max in bottom bar:
Board | Inbox | Tasks | Costs | More
Everything else in "More" overflow.

**Effort:** Medium. Responsive layout component.

---

## Pattern 5 — Collapsible Sidebar with Keyboard Overlay

**Source:** Cursor — sidebar toggle + `⌘⇧P` command palette  
**URL:** `https://cursor.com/changelog`  
**Confidence:** Medium-High

### Pattern Description
Sidebar collapses to an icon rail (32px). Click icon or press `⌘\` to expand. Collapsed state shows only icon badges (unread count, active indicator). The command palette (`⌘⇧P`) replaces most sidebar navigation when collapsed.

### ASCII Wireframe

```
Collapsed (icon rail):          Expanded:
┌──────┐                  ┌───────────────┐
│ 📋 ● │                  │ 📋 Board      │
│ 📥 3 │                  │ 📥 Inbox (3)  │
│ ⚙    │                  │ ⚙ Settings   │
│      │                  │               │
└──────┘                  └───────────────┘
  32px                        240px
```

### Mission Control Applicability
Operators who know the system well can collapse to rail, reducing cognitive load. Badge counts replace labels. Keyboard (`⌘⇧P`) handles navigation when collapsed.

**Effort:** Medium. Sidebar state + badge counts.

---

## Pattern 6 — Contextual Tab Overflow

**Source:** Linear — dynamic tab priority based on recency  
**URL:** `https://linear.app/docs/display-options`  
**Confidence:** High

### Pattern Description
Tabs that haven't been visited in 24h auto-collapse into "More". When a tab is visited, it surfaces back to visible. The tab bar adapts dynamically to operator behavior.

### ASCII Wireframe

```
Day 1 (all tabs visited):          Day 2 (unused tabs collapsed):
┌──────────────────────────────────────────────────────────────┐
│ [Board] [Inbox] [Tasks] [Deploy] [Actors] [Costs] [More 3]   │
└──────────────────────────────────────────────────────────────┘
```

### Mission Control Applicability
Reduces tab bar to 7 regardless of total tab count. Operators who frequently use "Deployments" see it; those who don't have it in "More". Adaptive, not hard-coded.

**Effort:** Medium. Requires visit-tracking middleware.

---

## Pattern 7 — Command Palette as Navigation Hub

**Source:** Cursor — `⌘K` / `⌘⇧P` as universal navigation  
**URL:** `https://cursor.com/changelog`  
**Confidence:** High

### Pattern Description
`⌘K` opens a searchable command palette. Typing searches commands, tabs, tasks, and recent items simultaneously. No need to remember where something lives — type, jump.

### ASCII Wireframe

```
┌─────────────────────────────────────────────────────────────────┐
│  ⌘K  Search tabs, tasks, commands...                            │
│  ─────────────────────────────────────────────────────────────  │
│  ▶ Board                                                        │
│  ▶ Inbox                                                        │
│  ▶ Tasks                                                        │
│  ───────── Recent ──────────                                   │
│    costs-v2 task #276  (Board › tasks)                         │
│    Forge is overloaded  (Inbox › alert)                         │
└─────────────────────────────────────────────────────────────────┘
```

### Mission Control Applicability
Every tab and major view should be reachable via `⌘K`. Especially valuable in "More" menu — operators don't need to navigate there, just type the name. Combined with Pattern 6, it handles the long-tail navigation problem.

**Effort:** Medium-high. Command palette with tab index.

---

## Top 3 Navigation Recommendations

### #1 — Hard Tab Cap at 7 + "More" Overflow
**Why:** The mandate is 7 tabs. Implement Pattern 1 (Priority-Weighted Tab Bar) + Pattern 6 (Contextual Overflow) together. Hard-cap visible tabs at 7; everything else goes to "More". Sort visible by operational priority (Board → Inbox → Tasks → Agents → Costs → Backlog → More).

**Priority signal:** "Where do I go?" — answered in <1 second.

### #2 — Deploy Keyboard Shortcut Overlay (`?`)
**Why:** Power operators use keyboards. Pattern 2 (`?` panel) + Pattern 7 (Command Palette `⌘K`) are the two highest-leverage keyboard investments. They work on any screen size and reduce mouse dependency significantly.

**Priority signal:** "How do I get there fast?" — answered without touching the mouse.

### #3 — Mobile Bottom Bar with 5-Item Cap
**Why:** MC already has a mobile viewport (3102). Pattern 4 (Bottom Bar) is the standard pattern for small-screen navigation. Hard-cap at 5 items: Board | Inbox | Tasks | Costs | More. Everything else accessible via More.

**Priority signal:** "Can I do this on my phone?" — answered yes for core operations.

---

## Sources

| # | Source | URL |
|---|---|---|
| 1 | Linear Docs — Sidebar | `https://linear.app/docs/your-sidebar` |
| 2 | Linear Docs — Keyboard Shortcuts | `https://linear.app/docs/keyboard-shortcuts` |
| 3 | Notion | `https://notion.so` |
| 4 | Discord (mobile) | `https://discord.com` |
| 5 | Cursor Changelog | `https://cursor.com/changelog` |
| 6 | Linear Docs — Display Options | `https://linear.app/docs/display-options` |

---

*Research by James (agent), 2026-04-18. Research only — no code, no openclaw.json edits.*
