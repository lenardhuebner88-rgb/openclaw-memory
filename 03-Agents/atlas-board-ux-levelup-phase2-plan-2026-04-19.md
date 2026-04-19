---
title: "Sprint-E Phase-2 Plan — Board-UX-Level-Up"
date: 2026-04-19 18:31 UTC
author: Atlas (Synthesis D3)
scope: Sprint-E 5 Sub-Tasks Implementation / Phase-2 Board-UX
status: ready-for-operator-approval
parent: e0c17d08-07e0-4d7b-aa1d-5f698e83cce7
---

# Sprint-E Phase-2 Plan — Board-UX-Level-Up (Atlas-Synthesis D3)

**Synthesized from:**
- D1 (Lens): `lens-mobile-ui-audit-2026-04-19.md` — 22 issues, 10 P0
- D2 (James): `james-operator-dashboard-research-v2-2026-04-19.md` — 7 tools, Top-10 patterns, Nav-Blueprint

**Awaiting Operator-Approval before E1 dispatch.**

---

## P0 Findings → Sub-Task Mapping

| Finding | Route | Issue | Severity | Sub-Task |
|---------|-------|-------|----------|----------|
| F1 | All 5 | ☰ hamburger icon contrast ratio 3.74 (AA requires 4.5) | P0 | E1 |
| F2 | All 5 | Description text contrast ratio 3.94 | P0 | E1 |
| F3 | /kanban | ViewToggle "Tasks" button 29px < 44px | P0 | E1 |
| F4 | /kanban | ViewToggle "Agents" button 29px < 44px | P0 | E1 |
| F5 | /alerts | Search input 40px < 44px | P0 | E1 |
| F6 | /alerts | SelectTrigger "All types" 32px < 44px | P0 | E1 |
| F7 | /costs | "Day" period button 40x25px | P0 | E1 |
| F8 | /costs | "Week" period button 54x25px | P0 | E1 |
| F9 | /costs | "Month" period button 56x25px | P0 | E1 |
| F10 | /costs | "Dispatch Investigation" button 32px < 44px | P0 | E1 |

**Root cause file:** `mission-shell.tsx:144` — icon color `rgb(107,114,128)` on dark background
**Secondary files:** `kanban/components/ViewToggle.tsx`, `alerts-client.tsx`, `costs-client.tsx`, `ui/tabs.tsx`

---

## James Top-10 Patterns → Sub-Task Mapping

| Pattern | Source | Sub-Task |
|---------|--------|----------|
| P1: Command Palette (Ctrl+K) | Linear/Notion | E2 |
| P2: Saved Views + URL-shareable filters | Datadog/Grafana | E5 |
| P3: Bottom-Tab-Bar (Mobile) | PagerDuty/Mobile-first | E4 |
| P4: Real-Time SSE Updates | Grafana/Datadog | E3 |
| P5: WCAG AA Color Tokens | Accessibility baseline | E1 |
| P6: Unified Navigation (7 Primaries) | Datadog/Linear IA | E4 |
| P7: Dashboard Hero Card | Linear/Overview | E1 (Dashboard-Hero) |
| P8: Bulk Actions + Multi-Select | Sentry/Linear | E5 |
| P9: Optimistic UI Updates | Linear | E3 |
| P10: Mobile Tap Target 44px Min | Accessibility baseline | E1 |

---

## Dependencies Between E1-E5

```
E1 (P0 Fixes + Dashboard Hero)
  ↓ (E1 must complete before E2)
E2 (Command Palette)
  ↓ (E2 can run parallel with E3 after E1)
E3 (SSE Real-Time) ←→ E4 (Navigation) ←→ E5 (Saved Views)
```

**Rule:** E1 is strictly sequential before E2. E3/E4/E5 can run sequentially (not parallel — pixel is bottleneck).

---

## Sub-E0 (OPTIONAL) — Mobile Emergency Controls

**Status:** OPTIONAL Add-on, piggyback on E3 (SSE + mobile tab bar work)

**Scope:**
- Add panic-button / emergency controls to mobile bottom tab
- Quick-status glance: System OK / Degraded / Incident
- One-tap escalation action

**Files:** `src/components/bottom-tab-bar.tsx` (already touched by E4)

**Note:** This is from ops-inventory-plan. Only do if E3/E4 capacity allows. Not a blocker for E1-E5 completion.

---

## Sub-E1 (Pixel) — P0 Accessibility Fixes + Dashboard Hero

**Agent:** Pixel (frontend-guru)  
**Estimated:** ~45 min

**Files:**
- `src/components/mission-shell.tsx` — hamburger icon color fix (P0 F1, F2)
- `src/components/kanban/components/ViewToggle.tsx` — tap targets → 44px min (F3, F4)
- `src/components/alerts/alerts-client.tsx` — search/filter tap targets → 44px (F5, F6)
- `src/app/costs/costs-client.tsx` + `src/components/ui/tabs.tsx` — period buttons → 44px (F7, F8, F9, F10)
- `src/app/page.tsx` or `src/app/overview/page.tsx` — new Dashboard-Hero component

**Acceptance:**
- `npm run build` passes
- All 10 P0 issues resolved (verify with mobile-ui-audit.spec.ts)
- Dashboard-Hero shows: Board-Status + Cost-Trend + Alert-Count + Cron-Health in 1 card
- Playwright: mobile tap-target checks pass (no 44px violations)

**Deploy-Verify:** curl + Playwright mobile smoke before done

---

## Sub-E2 (Pixel) — Command Palette (Ctrl+K)

**Agent:** Pixel  
**Estimated:** ~30 min  
**Dependency:** E1 complete

**Files:**
- `src/components/command-palette.tsx` (new)
- `src/app/api/command-search/route.ts` (new)
- `src/components/mission-shell.tsx` — Ctrl+K listener
- `src/lib/qmd-mcp.ts` — vault search via QMD

**Features:**
- Fuzzy search: Tasks (titles), Routes, Vault-docs (via QMD)
- Quick actions: Create Task, Navigate, Filter Board
- Keyboard navigation: arrows + Enter + Esc
- Opens <50ms

**Acceptance:**
- Ctrl+K opens palette on any route
- Search returns results <200ms
- ≥3 entity types indexed
- Playwright: palette opens/closes, search returns results

**Deploy-Verify:** curl + Playwright smoke

---

## Sub-E3 (Forge + Pixel) — Real-Time SSE Board Updates

**Agent:** Forge (SSE backend) + Pixel (UI hook)  
**Estimated:** ~30 min Forge + ~20 min Pixel  
**Dependency:** After E1

**Files:**
- `src/app/api/board-events/route.ts` (extend existing SSE endpoint)
- `src/lib/board-sse.ts` (new, Forge)
- `src/hooks/use-board-sse.ts` (new, Pixel)
- `src/components/mission-shell.tsx` — SSE connection init

**Features:**
- SSE stream for board events
- Board updates appear <2s (no 30s polling)
- Auto-reconnect with exponential backoff
- Fallback to 30s polling if SSE fails
- Feature-flag: toggle back to polling

**Acceptance:**
- SSE connects on page load
- Board reflects new task within 2s
- Reconnect works after network blip
- Fallback polling activates if SSE errors

**Deploy-Verify:** curl /api/board-events SSE + Playwright smoke

---

## Sub-E4 (Pixel) — Unified Navigation (7 Primary Navs)

**Agent:** Pixel  
**Estimated:** ~30 min  
**Dependency:** After E1, can run parallel with E3/E5

**Files:**
- `src/components/mission-shell.tsx` — restructure nav
- `src/components/bottom-tab-bar.tsx` (new)
- `src/app/page.tsx` — redirect to /overview

**7 Primary Navs:**
1. **Dashboard** (Overview) → `/dashboard` or `/overview`
2. **Tasks** (Taskboard + Kanban) → `/taskboard`, `/kanban`
3. **Alerts** → `/alerts`
4. **Team** → `/team`, `/agents`
5. **Memory** → `/memory`, `/vault`
6. **Automate** → `/automations`, `/cron-jobs`
7. **More** → `/costs`, `/trends`, `/files`, `/calendar`

**Mobile:** Bottom-tab-bar with 5 tabs (Dashboard, Tasks, Alerts, Team, More)

**Acceptance:**
- All 16 existing routes still reachable (redirects where needed)
- Mobile bottom-tab visible on all routes
- Nav transitions <100ms

**Deploy-Verify:** curl all 16 routes + Playwright mobile smoke

---

## Sub-E5 (Pixel + Forge) — Saved Views + Bulk Actions

**Agent:** Pixel + Forge  
**Estimated:** ~20 min Forge + ~25 min Pixel  
**Dependency:** After E2 (URL state needed)

**Files:**
- `src/components/board-filters.tsx` (extend)
- `src/components/bulk-action-bar.tsx` (new)
- `src/app/api/tasks/bulk/route.ts` (new, Forge)
- URL state management

**Features:**
- Filter state in URL: `?status=done&agent=sre-expert&priority=P0`
- Shareable view links
- Multi-select with checkboxes
- Bulk actions: cancel, retry, assign, archive

**Acceptance:**
- URL updates on filter change (shareable)
- Bulk action bar appears when ≥1 task selected
- 3 bulk actions work end-to-end

**Deploy-Verify:** curl + Playwright smoke (filter + bulk)

---

## Risks + Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| E1 finds additional P0 issues | niedrig | mittel | Lens audit is comprehensive — same issue class (contrast/tap) |
| SSE impl crashes Gateway | niedrig | hoch | Feature-flag + polling fallback |
| Nav refactor breaks existing routes | mittel | mittel | Keep all routes, only add redirect |
| Pixel session overflow (5 sequential) | mittel | mittel | Handoff after each E, session reset |
| E3/E4/E5 take longer than estimated | mittel | niedrig | E1/E2/E3/E4/E5 sequential — no downstream blocking |

---

## Deploy-Verify Contract (R42)

| Sub | curl verify | Playwright verify |
|-----|-------------|-------------------|
| E1 | `npm run build` | mobile-ui-audit.spec.ts pass |
| E2 | `/api/command-search` 200 | Ctrl+K open/close |
| E3 | `/api/board-events` SSE | board auto-updates |
| E4 | all 16 routes 200 | mobile tab visible |
| E5 | `/api/tasks/bulk` 200 | bulk cancel/retry |

---

## Success-Metrics

| Metric | Current | Target (Phase-2) |
|--------|---------|------------------|
| P0 WCAG issues | 10 | 0 |
| P0 Tap-target violations | 6 | 0 |
| Nav-primary-count | 16 | 7 |
| Command-Palette | none | live (≥3 entity types) |
| Real-time latency | 30s polling | <2s SSE |
| Saved-views | none | URL-shareable filters |

---

**Geschrieben:** 2026-04-19 18:38 Europe/Berlin  
**D1 Report:** `lens-mobile-ui-audit-2026-04-19.md` (commit `2788f67`)  
**D2 Report:** `james-operator-dashboard-research-v2-2026-04-19.md` (commit `4efcd6e`)  
**Awaiting Operator-Approval for Sprint-E Phase-2 Start**
