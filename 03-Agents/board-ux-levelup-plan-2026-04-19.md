---
title: Mission Control Board — UX-Level-Up Sprint (2 Phasen)
date: 2026-04-19 15:50 UTC
author: Operator (pieter_pan) direkt
scope: Board-UX-Consolidation + Mobile-Audit + Best-in-Class Research + Implementation
sprint: [Atlas-Sprint-D] Phase-1 Research / [Atlas-Sprint-E] Phase-2 Implementation
status: ready-for-Atlas-bootstrap
---

# Mission Control Board — UX-Level-Up Plan

## Executive Summary

Das MC-Board hat heute **16 Routen** (agents, alerts, automations, calendar, costs, dashboard, files, kanban, memory, monitoring, more, taskboard, team, trend, trends, vault). Heute Nachmittag kamen 3 dazu (monitoring, alerts, costs-extended). **Navigation-Fragmentierung + keine Mobile-First-Discipline + keine Real-Time-Updates + keine globale Search/Command-Palette.**

Ein Operator, der unterwegs auf sein Handy schaut ob System stabil läuft, hat kein singuläres Cockpit.

**Ziel:** Konsoliderung auf max. 7 primary-navs, mobile-first Hero + Command-Palette + Real-Time-Updates + Saved-Views. **Evidence-based** via Lens-Audit + James-Research.

## Sprint-Struktur

### Phase-1: Research + Audit (Atlas-Sprint-D, ~2h)
3 Sub-Tasks parallel durch Lens + James + Atlas-Synthesis.

### Phase-2: Implementation (Atlas-Sprint-E, ~3h)
5 Sub-Tasks durch Pixel + Forge, sequenziell UI-Tasks (Build-Storm-Vermeidung).

**Phase-1 MUST finish before Phase-2 starts.** Atlas dispatchet Phase-2 erst nach Atlas-Synthesis-Result.

---

## Phase-1: Atlas-Sprint-D — Research + Audit

### Sub-D1 (Lens/efficiency-auditor): Mobile-UI-Audit

**Scope:** Playwright-basierter Mobile-Audit auf 5 Routen:
- /taskboard
- /kanban
- /monitoring (neu seit 15:42)
- /alerts (neu seit 15:42)
- /costs (erweitert 15:15)

**Methode:**
- 3 viewports: `iPhone SE (375×667)`, `iPhone 14 (390×844)`, `Pixel 7 (412×915)`
- Pro Route: screenshot oben + scrolled + interaction-state
- Prüf-Kriterien:
  - Tap-Target-Size (≥44×44 px)
  - Text-Lesbarkeit (16px+ base)
  - Horizontal-Scroll (verboten)
  - Action-Reachability (Daumen-Zone)
  - Loading-States + Empty-States
  - Color-Contrast WCAG AA

**Output:** `/home/piet/vault/03-Agents/lens-mobile-ui-audit-2026-04-19.md`
- Findings-Tabelle (Route × Viewport × Issue × Priority P0/P1/P2)
- Screenshots in `workspace/audit-artifacts/2026-04-19/mobile/`
- Top-10 Priority-1 fixes mit konkreten Code-Snippet-Pointers

**Acceptance:** Report committed, 15+ concrete issues dokumentiert, 3+ P0-issues mit Fix-Proposal.

### Sub-D2 (James/researcher): Best-in-Class Operator-Dashboard Research

**Scope:** 2025-2026 State-of-the-Art für Multi-System-Operator-Dashboards.

**Deep-Dive auf 7 Produkte:**
1. **Linear** — project/issue-board (primäre Referenz: speed + keyboard)
2. **Stripe Dashboard** — financial-operator-console (Datenqualität, Trust)
3. **Datadog** — monitoring (filters, saved-views)
4. **Grafana** — visual metrics (composability)
5. **PagerDuty** — incident-response (mobile-first, alerts-feed)
6. **Sentry** — error-tracking + triage (search, bulk-actions)
7. **Notion** — navigation-flexibility (command palette, global search)

**Was zu extrahieren:**
- **Top 10 steal-this patterns** mit Screenshot (wenn möglich) + 2-3 Sätze Rationale + concrete implementation-hint
- **Navigation-Information-Architecture** — wie diese Tools 10+ Subsystems zu 5-7 Primary-Navs konsolidieren
- **Mobile-First-Pattern** — welche Desktop-Feature werden bewusst auf Mobile geopfert?
- **Real-Time-Update-Mechanismen** — polling vs SSE vs WebSocket vs manual-refresh
- **Global-Search / Command-Palette** — Ctrl+K Pattern, was wird indexed
- **Alert-Fatigue-Mitigation** — wie 3+ Tools Alert-Noise reduzieren

**Output:** `/home/piet/vault/03-Agents/james-operator-dashboard-research-v2-2026-04-19.md`
- 7 Tool-Deep-Dives (je 1-2 Absätze)
- **Top 10 Steal-This-Patterns** mit concrete-next-step je Pattern
- **Navigation-Konsolidierungs-Blueprint** für MC (16 Routes → 7 Primary-Navs Vorschlag)

**Acceptance:** Report committed, 7 tools analysiert, Top-10 patterns mit actionable hints, Nav-Blueprint mit 7 primary-navs.

### Sub-D3 (Atlas-Synthesis): Phase-2 Actionable Plan

**Scope:** Nach D1 + D2 done → Atlas synthesizes beide Reports zu konkretem Phase-2 Sprint-Plan.

**Was Atlas liefert:**
- 5 priorisierte Implementation-Subs (Sprint-E Phase 2)
- Pro Sub: scope, agent (pixel/forge), file-paths, acceptance, estimated-time
- Risks + Mitigations
- Stop-Bedingungen

**Output:** `/home/piet/vault/03-Agents/atlas-board-ux-levelup-phase2-plan.md`

**Acceptance:** Phase-2 Plan documented, 5 Sub-Tasks eindeutig definiert, ready für Operator-Approval oder direct Atlas-Dispatch.

---

## Phase-2: Atlas-Sprint-E — Implementation (nach Phase-1 Approval)

### Provisorische Sub-Tasks (finalisiert nach Phase-1)

**Sub-E1 (Pixel): Mobile-First Board-Home**
- Neue Hero-Component die Live-Status konsoldiert (Board + Costs + Alerts + Monitoring)
- Mobile-first: stacked cards, swipe-gestures, pull-to-refresh
- Desktop: side-by-side layout

**Sub-E2 (Pixel): Command-Palette (Ctrl+K)**
- Globale Search über Tasks, Agents, Rules, Vault-docs (via QMD-MCP)
- Keyboard-first
- Quick-action shortcuts (create task, filter, navigate)

**Sub-E3 (Forge + Pixel): Real-Time SSE Board-Updates**
- Ersetzt 30s-polling mit Server-Sent-Events
- Optimistic-UI-updates bei user-actions
- Fallback zu polling wenn SSE fails

**Sub-E4 (Pixel): Unified Navigation**
- 16 Routes → 7 Primary-Navs per James-Blueprint
- Sub-Navigation per Primary
- Mobile: bottom-tab-bar statt sidebar

**Sub-E5 (Pixel + Forge): Saved-Views + Bulk-Actions**
- User saved-filter-combos
- Multi-select + bulk (cancel, retry, archive, assign)
- URL-shareable views

### Stop-Bedingungen Phase-2

Atlas dispatcht Phase-2 **nicht ohne Operator-Approval** der Phase-1-Synthesis. Falls Phase-1 Findings zeigen dass Scope anders ist (z.B. Lens findet 40 P0 issues), Operator entscheidet Re-Scope.

---

## Acceptance & Success-Metrics

| Metric | Phase-1 Target | Phase-2 Target |
|---|---|---|
| Mobile Playwright-Tests passing | n/a (audit only) | 5/5 Routes mobile-clean |
| Nav-Primary-Count | 16 | 7 |
| Command-Palette | ∅ | live mit ≥3 entity-types |
| Real-Time-Update-Latency | 30s polling | <2s SSE |
| Reports in Vault | 3 | 1 consolidated End-Report |
| Git-Commits mit curl-verify | — | ≥5 (R42 compliance) |

## Risiken + Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Phase-1 Sub-D1 findet 40+ P0 issues | mittel | mittel | Atlas-Synthesis (D3) filtert auf Top-10 |
| Phase-2 Build-Storm durch 5 UI-Subs | mittel | hoch | Sequenzielle Dispatch, wie Sprint-C |
| SSE-Impl (E3) crashed Gateway | niedrig | hoch | Feature-Flag mit fallback zu polling |
| Pixel Session-Overflow bei 5 UI-Subs in Serie | mittel | mittel | Pixel nach jedem Sub handoff, session-reset |
| Nav-Refactor bricht existing Playwright | mittel | mittel | Tests parallel anpassen |

## Rules die greifen

- **R35** Atlas-Self-Report ≠ Board-Truth — Phase-1+2 brauchen Deliverable-Verify
- **R42** (new) Deploy-Verify-Contract — jede UI-Sub braucht curl + playwright verify vor done
- **R36** Context-Overflow — bei 5 UI-Subs in Serie achten auf Atlas-Session-Size
- **R37** Atlas-Orchestrator-Tasks nicht via Auto-Pickup — Operator bootstrapet
- **R40** per-agent threshold — Atlas-main 10/20min, Pixel 2/5min (weil pixel schreibt progress)
- **R41** QMD vor File-Read — Atlas nutzt deep_search für Spark-Audit, James-research contextual

## Sign-off

Operator (pieter_pan) 2026-04-19 15:50 UTC. 2-Phase-Sprint-Plan dokumentiert. Phase-1 kann sofort starten, Phase-2 nach Phase-1-Approval.
