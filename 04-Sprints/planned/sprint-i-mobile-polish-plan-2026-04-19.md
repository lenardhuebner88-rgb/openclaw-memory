---
title: Sprint-I Mobile-Polish P1/P2 Plan (v2 — in-depth revision)
date: 2026-04-19
revised_at: 2026-04-19 19:35 UTC (post Sprint-E/F/G/H Autonomous-Cascade)
author: Operator (pieter_pan) + Assistant (Claude) — Live-Recon der neuen Routes
status: planned
type: sprint-plan
trigger_phrase: "Atlas nun nächster Sprint follow #42"
source_findings: Sprint-E Playwright-Mobile-Audit + Sprint-G/H New Routes (/analytics, /ops, /more, /cron-jobs)
prerequisites: Sprint-J (Cascade-Post-Mortem + R47) done; Sprint-E code deployed; Sprint-G G4 Ops-UI + Sprint-H H2 Analytics-Frontend committed
blocking_factors: Sprint-K H-rename muss vor I4-final laufen damit Contrast-Deltas nicht doppelt-gefixt werden
estimated_effort: 16-20h orchestriert (up from 9h in v1, +7-11h durch Deep-Scope)
---

# Sprint-I — Mobile-Polish P1/P2 (v2 in-depth)

## 🔄 Revision History

- **v1** (2026-04-19 17:40 UTC): 4 Subs, 9h, nur /taskboard /kanban /monitoring /alerts /costs
- **v2** (2026-04-19 19:35 UTC, CURRENT): **7 Subs, 16-20h**. Erweitert um:
  - Neue Routes aus Sprint-G (/ops) + Sprint-H (/analytics) + /more (bottom-tab landing) + /cron-jobs
  - Deep-Scope: Safe-Area-Insets, Fluid-Typography, PWA-foundation, Gesture-Support, Battery/Network-Awareness, Mobile-Command-Palette-Alternative
  - Lighthouse Mobile-Score > 90 als Hard-Acceptance
  - E2 Ctrl+K Follow-up (kein physical Ctrl auf Mobile)
  - E3 SSE Battery-Drain-Mitigation (Page Visibility API)

## 🎯 Scope

Residuale Findings aus Sprint-E Playwright-Mobile-Audit + Coverage-Expansion auf neue Routes aus Sprint-G + Sprint-H + E2+E3 Mobile-Follow-ups adressieren. Ziel: **Mission Control ist Mobile-First Production-Ready**, nicht Desktop-First mit Mobile-Hack.

### Aktualisierte Route-Matrix (9 Routes, vorher 5)

| Route | Sprint-Origin | Mobile-Readiness | Sprint-I Scope |
|---|---|---|---|
| `/taskboard` | pre-E | teils (E1 P0-Fixes) | vollständig |
| `/kanban` | pre-E | Post-E4 unified | vollständig |
| `/monitoring` | Sprint-C | Audit-Findings pending | vollständig |
| `/alerts` | Sprint-C | Audit-Findings pending | vollständig |
| `/costs` | pre-E | Audit-Findings pending | vollständig |
| `/dashboard` + `/overview` | E1 Hero-Refactor | Post-E1 solid | verify + polish |
| **`/analytics`** | **Sprint-H H2 (NEW)** | **unbekannt** | **vollständig (KPI-Charts, Velocity, Alert-History)** |
| **`/ops`** | **Sprint-G G4 (NEW)** | **unbekannt** | **vollständig (Script-Table, Dep-Graph, Health-Panel, Scheduler-Table)** |
| **`/more`** | **implicit mit bottom-tab-bar** | **bottom-tab target** | **vollständig** |

Plus Audit weiterer neuer Components:
- `bottom-tab-bar.tsx` (NEW) — Primary-Nav-Pattern auf Mobile
- `bulk-action-bar.tsx` (NEW, E5a) — Sticky-Bottom-Action-Pattern
- `mission-shell.tsx` — Shell-Component für Nav/Safe-Area

**Anti-Scope:**
- Keine neuen Routes (nur bestehende polishen)
- Keine Backend-API-Änderungen (nur UI/CSS/Asset)
- Keine Feature-Deprekation
- Kein Dark-Token-System-Rewrite (→ Sprint-K H9 in dediziertem Sprint)
- Keine Push-Notifications (→ L3-Roadmap)

## 📋 Sub-Tasks (7, war 4)

### Sub-I1: Tap-Target + Thumb-Zone Optimization (all 9 Routes)
**Agent:** Pixel (frontend-guru)
**Scope:**
- Alle Tap-Targets ≥44×44 px (WCAG AA) ODER ≥48×48 px (Material Design — target für Primary-Actions)
- **Thumb-Zone-Analysis**: Primary-Actions in bottom-60% der Viewport-Height (Luke-Wroblewski-Daumenzone)
- Sticky-Bottom-Action-Bars auf Routes mit häufigen Actions: /taskboard (E5a bulk-action-bar), /kanban, /ops
- `bottom-tab-bar.tsx` Deep-Review: Höhe, Touch-Targets, Active-State-Visual, Label-Readability
- Secondary-Nav-Tabs (die 88-113×38px aus E-Audit) auf /costs /alerts /monitoring anheben
- **NEU v2:** Audit auch `/analytics` KPI-Cards (tap-to-drilldown?) und `/ops` Script-Table-Rows (long-press context menu?)
**Files (Hinweis):**
- `src/components/bottom-tab-bar.tsx`
- `src/components/bulk-action-bar.tsx`
- `src/components/costs/cost-sub-nav.tsx` / `alerts-tabs.tsx` / `monitoring-tabs.tsx`
- `src/components/ops/script-table.tsx` (row-actions)
- `src/components/analytics/kpi-trend-cards.tsx` (card-tap-targets)
**Acceptance:**
- Playwright-Mobile-Smoke (9 Routes × 5 Viewports): TAP-TARGET-findings = 0
- Visual-Manual-Check: Primary-Action immer in bottom-60% der Viewport erreichbar
- Bottom-tab-bar auf iPhone SE nicht über 15% der Viewport-Height
**Estimate:** 2.5h (v1 hatte 2h, v2 +30min für neue Routes)

### Sub-I2: Typography + Safe-Area-Insets + Fluid-Type
**Agent:** Pixel (frontend-guru) + James (researcher, 45min Pre-Audit)
**Scope:**
- **Typography-Scale-Reset**: `font-size < 16px` systematisch adressieren (war 302 findings E-Audit)
- **Fluid-Typography**: CSS `clamp(14px, 2.5vw, 18px)` für responsive Skalierung statt fixer Breakpoints
- **Safe-Area-Insets**: `env(safe-area-inset-{top,bottom,left,right})` für iPhone-Notch + Dynamic-Island + Home-Indicator (wichtig für `bottom-tab-bar` + sticky-headers)
- **Dark-Mode als Default** (operators use at night) — toggle-override persistieren in localStorage, respect `prefers-color-scheme: dark`
- **NEU v2:** Line-Height-Scaling (Body 1.5, Headings 1.2) + Text-Contrast-Aware-Ops (oklch tokens sweep, aber NUR Audit — Fix in Sprint-K H9)
- **NEU v2:** `prefers-reduced-motion` Support — keine Auto-SSE-Animations für sensitive users
**James-Pre-Audit (45min):** Best-in-Class Mobile-Typography-Systems in 2025/2026 — Linear, Stripe Dashboard, Datadog Mobile, Vercel Dashboard. Output: 1-Page-Scale-Table + Safe-Area-Pattern + Fluid-Type-Empfehlungen. Datei: `vault/03-Agents/james-mobile-typography-system-2026-04-19.md`
**Pixel-Impl (3h):**
- Tailwind-Config: neue `text-xs-ornament` (12px erlaubt für reine Decorations), `text-sm` (14px metadata), `text-base` (16px content-default), `text-lg-fluid` (clamp)
- Body-Tag `font-feature-settings: "ss01"` (tabular-nums für Dashboards)
- Jeder `text-xs`-Vorkommen: Entscheidung Ornament vs Content (nach James-Guide)
- `env(safe-area-inset-*)` in `mission-shell.tsx`, `bottom-tab-bar.tsx`, Sticky-Headers
- Dark-Mode-Default: `html.dark` class in layout.tsx per-default, localStorage-override-respect
- Keine Color-Token-Changes (bleibt H9-Scope)
**Acceptance:**
- Playwright-Mobile-Smoke: Text<16px-count < 50 (85% Reduktion von 302)
- iPhone-14-Pro-Simulation: Notch-Area nicht von UI überdeckt (safe-area verified)
- `html.dark` as default visible auf Light-Mode-Device (Dark-first-philosophy)
- `@media (prefers-reduced-motion: reduce)` disables SSE-Flash-Animations
**Estimate:** 3.75h (v1 hatte 3h, v2 +45min für Safe-Area + Dark-Default)

### Sub-I3: Loading-States + Empty-States + CLS + Optimistic-UI
**Agent:** Pixel (frontend-guru) + Lens (efficiency-auditor, 30min Pre-Audit)
**Scope:**
- **Loading-Skeletons** für alle 9 Routes (war 3 missing — jetzt 9 verified)
- **Empty-States** für alle Routes + neue `/analytics` (no-data) + `/ops` (no-scripts-monitored)
- **CLS-Prevention**: Skeletons müssen **exakt** das Post-Load-Layout matchen (kein Layout-Shift > 0.1)
- **Optimistic-UI**: `/taskboard` Bulk-Actions (E5a) — UI-Update sofort, Rollback bei API-Fail (nicht waiting for SSE)
- **NEU v2:** Connection-State-Indicator — Mini-Dot in Top-Bar: green (online+SSE), yellow (online+SSE-reconnecting), red (offline). Uses `navigator.onLine` + EventSource `readyState`.
- **NEU v2:** Offline-Action-Queue — Actions (receipt-post, task-patch) in IndexedDB queuen wenn offline, replay bei Reconnect. Uses Service-Worker skeleton.
**Lens-Pre-Audit (30min):** Route × State × Component-Coverage-Tabelle. Datei: `vault/03-Agents/lens-route-state-coverage-audit-v2-2026-04-19.md` (9 routes × 4 states = 36 Cells).
**Pixel-Impl (3.5h):**
- `SkeletonCard`, `SkeletonTable`, `SkeletonChart` Components (in `src/components/ui/skeleton.tsx`) — Layout-exact
- `EmptyState` Component (`icon`, `headline`, `body`, `action`) — einheitlich über Routes
- Suspense-Boundaries + `isLoading` / `data.length === 0` guards
- `<ConnectionStatus>` Component für `mission-shell.tsx` Top-Bar
- ServiceWorker-Scaffold (`public/sw.js` + register in layout.tsx) — nur Offline-Queue, kein Full-PWA
- `useOptimisticBulkAction` hook für Taskboard
**Acceptance:**
- Playwright-Mobile-Smoke: no-loading-skeleton-found = 0 auf allen 9 Routes
- Lighthouse Mobile CLS < 0.1
- Offline-Test: Plane-Mode → Bulk-Action → Back-Online → Action replayed (E2E-Test)
- Connection-Indicator visible + accurate in 3 States
**Estimate:** 4h (v1 hatte 3h, v2 +1h für Connection-Indicator + Offline-Queue)

### Sub-I4: Mobile-Command-Palette (E2-Ctrl+K-Alternative)
**Agent:** Pixel (frontend-guru) — NEU v2
**Scope:** E2 hat Command-Palette mit Ctrl+K eingeführt. Mobile hat kein physisches Ctrl → needs alternative-Trigger:
- **Floating-Action-Button (FAB)** bottom-right: Tap öffnet full-screen Command-Sheet (bottom-sheet-modal)
- **Triple-Tap auf Top-Bar** als Power-User-Shortcut
- **Full-Screen Search-Sheet**: statt Dropdown-Panel auf Desktop, FullScreen-Modal auf Mobile. Keyboard auto-focus, recent-searches unterhalb Input.
- **Voice-Input Integration (optional)**: Web Speech API wenn `navigator.mediaDevices` available → Mic-Icon in Search-Input
- **Result-Categories**: Tasks, Sprints, Scripts, Routes, Actions (ähnlich Cmd-K in Linear)
- Hier auch: deep-link-friendly (`/taskboard?q=sprint-e&filter=done`)
**Files:**
- `src/components/command-palette/*` (probably extend existing E2 work)
- `src/components/command-palette/mobile-sheet.tsx` (NEW)
- `src/components/command-palette/voice-input.tsx` (NEW, optional)
- `src/components/command-palette/fab.tsx` (NEW)
**Acceptance:**
- FAB visible auf Mobile-Viewports (hidden Desktop)
- Triple-Tap-Shortcut tested via Playwright
- Full-screen sheet renders without horizontal-scroll auf iPhone SE
- Voice-Input optional aber `enabled=true` wenn browser supports
- Deep-Link aus Search-Result navigiert korrekt
**Estimate:** 3h

### Sub-I5: Battery + Network Optimization (E3-SSE-Follow-up)
**Agent:** Forge (sre-expert) — NEU v2, Backend-lastig
**Scope:** E3 hat SSE für Real-Time-Board-Updates eingeführt. Auf Mobile:
- **Battery-Drain-Risk**: SSE bleibt open auch wenn App backgrounded
- **Network-Risk**: 2G/Edge/Slow-WiFi — SSE heartbeat floods bandwidth
- **Reconnect-Storm**: ohne Backoff → Server DDoS bei Mobile-Network-Flap
**Fix:**
- **Page Visibility API**: SSE pause bei `document.hidden=true`, resume bei visible. Reduce heartbeat-interval on hidden.
- **Exponential Backoff**: Reconnect-Delay 1s → 2s → 4s → 8s → 16s → 32s max (mit Jitter).
- **Connection-Type Awareness**: `navigator.connection.effectiveType` — Disable SSE on 2G, reduce to long-poll-fallback on 3G.
- **Heartbeat-Tuning**: Mobile-User-Agent → 30s heartbeat (vs Desktop 10s) — halbiert battery-cost ohne UX-Degradation
- **NEU R46 Compliance**: bei MC-Restart-Event → SSE reconnect läuft durch `mc-restart-safe`-Awareness (event-source reconnect nur nach MC-Health 200)
**Files:**
- `src/components/board-events/sse-client.tsx` (or wherever E3 put it)
- `src/lib/sse/sse-adapter.ts` (NEW — reconnect-logic layer)
- `public/sw.js` (extend für SSE-backgroud-handoff)
**Acceptance:**
- DevTools-Mobile-Emulation + Throttle 3G: SSE reconnects < 5 times in 10min
- Page-Background 5min: SSE disconnected (verify via DevTools Network panel)
- Lighthouse Mobile PWA score improves by 10+
- Battery-Usage-Test (Chrome DevTools Battery-Panel): SSE-idle drain < 1% per 15min
**Estimate:** 2.5h

### Sub-I6: Gesture-Support + Viewport-Expansion
**Agent:** Pixel (frontend-guru) — NEU v2
**Scope:**
- **Gesture-Patterns**:
  - Swipe-to-dismiss auf Modals/Drawers (z.B. Task-Detail)
  - Swipe-left-to-archive auf Taskboard-Cards
  - Pull-to-refresh auf Listen-Routes (/taskboard /kanban /ops)
  - Long-press context menu auf Script-Rows (/ops) + Task-Cards
  - Pinch-zoom **lock** auf Charts (/analytics velocity-chart, /ops dependency-graph) — `touch-action: pan-x pan-y`
- **Viewport-Expansion** (war 3 Viewports, jetzt 6):
  - iPhone SE (375×667) — minimum
  - iPhone 14 (390×844)
  - iPhone 15 Pro Max (430×932) — maximum phone
  - Pixel 7 (412×915) — Android-wide
  - Samsung Galaxy Z Fold 5 inner (904×1150) — fold-open edge-case
  - iPad Mini Portrait (768×1024) — tablet-bridge
- **Landscape-Orientation-Handling**: 5 Viewports × 2 orientations = 10 test-runs (Landscape wichtig für Kanban-Workflow)
**Library-Choice:** `@use-gesture/react` oder native TouchEvents — Pixel entscheidet nach 15min POC
**Files:**
- `src/hooks/use-swipe.ts` (NEW)
- `src/hooks/use-pull-to-refresh.ts` (NEW)
- `src/components/ui/long-press-menu.tsx` (NEW)
**Acceptance:**
- Playwright 6 Viewports × 2 Orientations = 12 configs, Tap-Target + Text + Gesture-Smoke alle pass
- Manuell verify: iPad-Mini Portrait zeigt 2-Column statt 1-Column (responsive breakpoint)
- Fold-Open: Content flex-wrap korrekt, kein awkward whitespace
**Estimate:** 3h

### Sub-I7: Comprehensive Mobile-Audit + Lighthouse-Score
**Agent:** Pixel (frontend-guru) + Lens (efficiency-auditor, 30min parallel)
**Scope:**
- **Playwright-Comprehensive-Suite**: 9 Routes × 6 Viewports × 2 Orientations = **108 test-cases**
- **Lighthouse-Mobile-Audits**: alle 9 Routes, target Performance + Accessibility + Best-Practices + SEO ≥ 90
- **Bundle-Size-Analysis**: next-bundle-analyzer, flag any route > 300 KB first-load JS
- **Image-Optimization**: Audit all `<img>` ohne `next/image`, priorisiere `/dashboard` Hero + `/analytics` Charts
- **Before/After Delta-Table**: Pre-Sprint-I (aus Sprint-E Audit) vs Post-Sprint-I (jetzt)
- **Residual-Findings → Sprint-K Kandidaten**: was ist noch offen? (Contrast H9 gehört nach K)
**Lens-Parallel (30min):** Cost-Impact-Analysis — wie ändert sich Bundle-Size-Quota? Welche neuen Dependencies kosten?
**Report:** `vault/03-Agents/sprint-i-comprehensive-mobile-audit-2026-04-19.md` — 200+ Zeilen
**Acceptance:**
- Lighthouse-Mobile Performance ≥ 90, A11Y ≥ 95, BestPractices ≥ 95, SEO ≥ 90 auf allen 9 Routes
- Playwright 108 configs: 0 Tap-Target-Violations, Text<16px < 50, Skeletons + Empty-States 100%
- Bundle-Size: Keine Route > 400 KB first-load JS (Hard), > 300 KB flag (Soft)
- Before/After-Table zeigt ≥ 80% Reduktion in jedem Finding-Category
**Estimate:** 2.5h (v1 hatte 1h; v2 +1.5h für 6 Viewports × 2 Orientations + Lighthouse)

## 🔗 Dependencies (updated)

```
Sprint-E done ──┐
Sprint-G G4 ────┤  ──> Sprint-I I1 ──┐
Sprint-H H2 ────┤         I2 ───────┤
Sprint-J done ──┤         I3 ───────├── I7 (final audit)
                │         I4 ───────┤
Sprint-K H9 ────┘         I5 ───────┤
  (after I,        I6 ───────┘
   not before)
```

**Parallelization:**
- I1 + I2 + I3 + I4 + I5 + I6 **alle parallel** möglich (disjoint scope)
- Pixel WIP-Limit 2 → max 2 Pixel-Subs gleichzeitig. Suggested batches:
  - Batch 1: I1 (Pixel) + I5 (Forge) parallel — 2.5h max
  - Batch 2: I2 (Pixel nach James-Pre-Audit) + I6 (Pixel) — sequenziell
  - Batch 3: I3 (Pixel nach Lens-Pre-Audit) + I4 (Pixel) — sequenziell
  - Final: I7 nach I1-I6 done — Pixel + Lens parallel

## 🤖 Atlas-Dispatch-Prompt (v2 ready-to-fire)

```
REAL_TASK=true ORCHESTRATOR_MODE=true. Sprint-I Mobile-Polish v2 in-depth — NICHT heartbeat.

Kontext:
Sprint-E durch (6 Commits: edb0d56, 7f9122c, 10b7274, ea13c39, 06c30c8, 2621d10). Sprint-J durch (Cascade-PostMortem, R47 Governance live).
Sprint-I v2 = Deep Mobile-Polish: 7 Subs über 9 Routes (5 bestehende + /analytics /ops /more /cron-jobs neu aus G+H).
Skalierung gegenüber v1: +Safe-Area-Insets, +Fluid-Typography, +Dark-Default, +Mobile-Command-Palette, +SSE-Battery-Optim, +Gesture-Support, +Lighthouse-Score-Target 90.

Plan-Doku: /home/piet/vault/03-Agents/sprint-i-mobile-polish-plan-2026-04-19.md (v2, 300+ Zeilen)
(qmd deep_search "sprint-i mobile polish v2")

7 Sub-Tasks:
- Sub-I1 (Pixel): Tap-Target + Thumb-Zone 9 Routes, 2.5h
- Sub-I2 (James 45min → Pixel 3h): Typography + Safe-Area + Dark-Default + Reduced-Motion, 3.75h gesamt
- Sub-I3 (Lens 30min → Pixel 3.5h): Loading/Empty-States + CLS + Optimistic-UI + Connection-Indicator + Offline-Queue, 4h gesamt
- Sub-I4 (Pixel): Mobile Command-Palette (FAB + full-screen-sheet + voice), 3h
- Sub-I5 (Forge): SSE Battery + Network Optim (Page Visibility + Exp Backoff + Connection-Type), 2.5h
- Sub-I6 (Pixel): Gesture Support (swipe/pull-refresh/long-press) + Viewport Expansion 6 devices × 2 orientations, 3h
- Sub-I7 (Pixel + Lens 30min): Comprehensive Audit 108 configs + Lighthouse ≥ 90, 2.5h

Playbook:
1. qmd deep_search "sprint-i mobile polish v2"
2. Pre-Reference: qmd deep_search "lens mobile ui audit" + "james operator dashboard research"
3. POST 7 Board-Tasks via taskboard_create_task (R44 PFLICHT!)
4. Dispatch-Order:
   - Batch 1: I1 (Pixel) + I5 (Forge) parallel
   - Batch 2: I2 (Pixel nach James-Pre) parallel zu I6 (Pixel) — Pixel WIP-Limit 2
   - Batch 3: I3 (Pixel nach Lens-Pre) parallel zu I4 (Pixel)
   - Final: I7 nach I1-I6 done
5. R47 compliance: pre-dispatch prüfen dass sprint-i-plan frontmatter operatorLock != true

Constraints:
- R35: "done" nur nach ls-verify + Playwright-Smoke-Pass
- R42/R46: mc-restart-safe PFLICHT (kein direkter systemctl)
- R44: Board-Visibility via taskboard_create_task
- R45: accepted within 60s, progress alle 5min
- R47 (jetzt aktiv): operatorLock-Check am Plan-Doc-Frontmatter
- R40: Pixel/Forge/Lens 2/5min stall; Atlas 10/20min

Anti-Scope:
- Keine Color-Token-Changes (→ Sprint-K H9)
- Keine Push-Notifications (→ L3)
- Keine Backend-API-Änderungen (Fortschritt nur UI/CSS/Asset)

Zeit-Budget: 16-20h orchestriert. Operator monitort passiv.

Return format:
- EXECUTION_STATUS
- RESULT_SUMMARY:
  - 7 Board-Task-IDs + Final-Status
  - 4+ Report-Paths ls-verified: james-typography-system, lens-route-state-v2, sprint-i-comprehensive-audit (MUST), cost-impact (Lens)
  - Lighthouse-Scores-Tabelle (9 routes × 4 categories)
  - Playwright 108-configs Pass-Rate
  - Bundle-Size-Before/After per Route
  - Residual-Findings Liste (→ Sprint-K)
  - Git-Commits-Liste (min 5 expected)

Los.
```

## 📊 Acceptance Sprint-Level (updated)

- [ ] 7 Board-Tasks done (R44-compliant)
- [ ] ≥ 5 Git-Commits auf `main` (I1 + I2 + I3 + I4 + I6 + I5 backend = 6 expected minimum)
- [ ] Playwright Mobile-Smoke 108 configs (9 routes × 6 viewports × 2 orientations): 100% pass Tap-Target, Text<16px < 50 per config, Skeletons + Empty-States 100%
- [ ] Lighthouse-Mobile alle 9 Routes: Performance ≥ 90, A11Y ≥ 95, BestPractices ≥ 95, SEO ≥ 90
- [ ] Safe-Area-Insets verifiziert auf iPhone-14-Pro-Simulation (Notch + Home-Indicator)
- [ ] Dark-Mode als Default (html.dark in layout.tsx)
- [ ] Mobile Command-Palette FAB functional
- [ ] SSE Battery-Test: Background 5min → disconnected; Reconnect mit exponential backoff verified
- [ ] Offline-Action-Queue: Plane-Mode → Bulk-Action → Online → replayed (E2E-proof)
- [ ] Gesture-Patterns: swipe-to-dismiss + pull-to-refresh + long-press auf min 3 Routes functional
- [ ] Bundle-Size: keine Route > 400 KB first-load (Hard-Cap)
- [ ] Comprehensive-Audit-Report 200+ Zeilen in Vault
- [ ] Residual-Findings explizit als Sprint-K-Kandidaten gelistet

## 🚨 Risk + Mitigation (updated)

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Dark-Mode-Default bricht Light-Mode-User-Expectation | Mittel | Mittel | Opt-out-Toggle in /more, localStorage-persist, respect prefers-color-scheme |
| Fluid-Typography CSS clamp() browser-compat (älter iOS Safari 13) | Niedrig | Mittel | Fallback auf fixed-text-sm in @supports-not |
| Service-Worker offline-queue bricht Sprint-E SSE | Mittel | Hoch | SW scope EXCLUDES /api/board-events; progressive enhancement only |
| @use-gesture/react bundle-size +30KB | Niedrig | Niedrig | Tree-shaking, code-split gesture-code per route |
| I7 Lighthouse-Score 90 unerreichbar wegen E5a SSE-heavy payload | Mittel | Mittel | I5 address reduces SSE-payload; if still < 90, document gap + next-sprint candidate |
| Mobile-Command-Palette FAB kollidiert mit bulk-action-bar | Hoch | Mittel | FAB position-offset bei bulk-mode-active; oder FAB morphs in bulk-context |
| Sprint-K parallel to Sprint-I führt zu Contrast+Typography-Double-Fix | Hoch (wenn geplant parallel) | Mittel | Sprint-K MUST wait for Sprint-I I7 done; documented in dependency-graph |
| Atlas versucht mc-restart parallel zu I5 Forge + I6 Pixel | Mittel | Mittel | R46 mc-restart-safe wrapper, parallel aware (flock) |

## 🎟️ Trigger zum Start

**Phrase:** *"Atlas nun nächster Sprint follow #42"*  
**Prerequisites before dispatch:**
1. Sprint-J all 6 Subs done (R47 deployed)
2. Sprint-H (Atlas Board-Analytics) done — `/analytics` stable
3. Sprint-G G4 `/ops` stable
4. E5a Board-Drift resolved (J6)

## 🔗 Referenzen

- Sprint-E Endreport: Atlas's `sprint-e-final-report-2026-04-19.md`
- Mega-Cascade-Endreport (Sprint-J J4): `autonomous-cascade-endreport-sprints-efgh-2026-04-19.md`
- Lens-D1-Audit: `lens-mobile-ui-audit-2026-04-19.md`
- James-D2-Research: `james-operator-dashboard-research-v2-2026-04-19.md`
- Sprint-J: `sprint-j-cascade-postmortem-plan-2026-04-19.md` (prerequisite)
- Sprint-K (Infra-Hardening renamed): `sprint-k-infra-hardening-plan-2026-04-19.md` (post-I)
- Rules: R1-R47 (R47 new via Sprint-J)
- Mobile-Components New: `bottom-tab-bar.tsx`, `bulk-action-bar.tsx`, `mission-shell.tsx`
- Analytics-Components New: `analytics/{kpi-trend-cards,alert-history,velocity-chart,analytics-client}.tsx`
- Ops-Components New: `ops/{ops-dashboard-client,script-table,kpi-cards,health-panel,dependency-graph,scheduler-table}.tsx`

## 📝 Signoff

Operator (pieter_pan) 2026-04-19 [TIMESTAMP]: v2 ready-to-dispatch **AFTER Sprint-J**.  
Assistant (Claude) 2026-04-19 19:35 UTC: v2-Revision basierend auf Live-Recon neuer Routes + Deep-Mobile-Optimization-Catalog.

---

**Ende Sprint-I v2 Plan.** Nach Abschluss: Sprint-K Infra-Hardening (Contrast H9, deployable queues, worker-monitor-extensions).
