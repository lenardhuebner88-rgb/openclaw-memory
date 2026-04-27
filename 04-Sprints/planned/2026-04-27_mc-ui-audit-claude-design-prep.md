---
date: 2026-04-27
type: sprint-plan
status: draft
owner: pieter_pan
related:
  - vault/03-Projects/plans/claude-code-openclaw-integration-roadmap-2026-04-20.md
  - vault/04-Sprints/planned/2026-04-24_mc-audit-p4-followup-plan.md
  - vault/04-Sprints/planned/s-mc-alerts-dashboard-audit-2026-04-23.md
  - vault/07-Research/design-handoffs/2026-04-20-taskboard/
sources:
  - Live audit der MC-Routes /dashboard /kanban /alerts /team /memory /automate /more /costs /architecture /analytics /ops am 2026-04-27 ~14:00 UTC
  - Browser Chrome MCP gegen http://192.168.178.61:3000
  - Tech-inspect viewport-meta error-boundary skeleton-loader a11y-labels via document.querySelector
---

# MC-UI-Audit + Claude-Design-Prep (Sprint-Plan 2026-04-27)

## TL;DR

Live-Audit aller 11 sichtbaren Mission-Control-Routes brachte **5 P0-Bugs**, **10 P1-UX-Schmerzen**, **10 P2-Polish-Items**. Vor dem nächsten Pixel-Visual-Refresh sollten die P0-Bugs gefixed sein, damit Claude-Design-Iteration auf einer ehrlichen Baseline aufsetzen kann (kein Sinn, eine 404-Route zu redesignen).

Plan: **Phase A** = P0-Bug-Fixes (Forge, ~6h). **Phase B** = Claude-Design-Manual-Pass auf 3 Hebel-Bereiche (User in Web-UI, ~3h). **Phase C** = Pixel implementiert Handoff-Bundle (~8h).

---

## Findings (Audit 2026-04-27)

### P0 — Production-Bugs

| ID | Befund | Ort | Fix-Owner |
|---|---|---|---|
| P0-1 | `/automate` ist 404 trotz Top-Nav-Link | Header-Nav | Forge |
| P0-2 | Mermaid-Graph wird als Plain-Text-Code gerendert | /ops > Dependency graph | Forge |
| P0-3 | DATA: FALLBACK auf 5/6 Agenten (Atlas/Pixel/Lens/Spark/James), nur Forge CACHED | /kanban Agent-Cards | Forge (root-cause) |
| P0-4 | Cost-Inkonsistenz: /analytics zeigt €134.77 Cost Pressure, /costs Cockpit zeigt $0.00/$20.00 | /analytics vs /costs | Forge (source-of-truth) |
| P0-5 | Kein ErrorBoundary im DOM (`document.querySelector('[class*=error-boundary]')` -> null) | global | Pixel |

### P1 — Operator-UX

| ID | Befund | Ort |
|---|---|---|
| P1-1 | Initial-Render-Race: "Online 0/0 · Aktiv 0" springt nach Scroll auf 6/6 · 4 | /dashboard |
| P1-2 | Kein Skeleton-Loader irgendwo (`querySelector` -> null), nur Plain-Text "Loading live pipeline..." | global |
| P1-3 | Alert-Fatigue: 9624 Alerts in 7d, davon 5404 Cost-SUPPRESS-Spam (rate_limit) | /alerts |
| P1-4 | Widerspruch: STALE-1d-Badge + grüner Text "kein Eingriff nötig" auf gleicher Card | /kanban Spark/James |
| P1-5 | Massive Whitespace 200-400px unter Karten | /dashboard /kanban /memory |
| P1-6 | Sprachgemisch DE/EN inkonsistent ("Mehr/Schnellaktionen" + "Overview/Architecture") | /more /costs |
| P1-7 | Section-Links wiederholen Top-Nav (zweite Navigation auf jeder Subpage) | /more /costs /analytics /ops |
| P1-8 | Empty-States ohne Next-Action (alle 0-Karten zeigen "Queue leer" ohne CTA) | /dashboard |
| P1-9 | Suppress-Spam steht in gleicher Liste wie CRITICAL-Alerts (canary-session-rotation-watchdog) | /alerts |
| P1-10 | Keine Acknowledge/Mute-Action pro Alert | /alerts |

### P2 — Polish & Backlog

| ID | Befund |
|---|---|
| P2-1 | Team-Tab ist Listen-Grid, kein Org-Chart (laut Memory geplant) |
| P2-2 | "80% Good" Score auf Agent-Cards unbeschriftet |
| P2-3 | Velocity-Chart Datums-Labels überlappen |
| P2-4 | "Hover for derivation" Tooltip-only (mobile-feindlich) |
| P2-5 | "COMPOSITE EFFECTIVE $" + "Atlas Session 0%" ohne Erklärung |
| P2-6 | Throughput-Card hat Pfeil-Icon ohne Click-Funktion |
| P2-7 | Executive Trend Strip /costs zeigt 6x "new/new" |
| P2-8 | Mission-Statement-Card hat Cursor links (sieht unfinished aus) |
| P2-9 | Pipeline-Filter zeigt nur 4 Agents (James/Spark fehlen im Filter, sind aber als Cards sichtbar) |
| P2-10 | Architecture zeigt 10 Agents (codex/default/test-lock/worker zusätzlich), Team sagt 6 — Inkonsistenz |

---

## Sprint-Plan

### Phase A — P0-Bugs fixen (Forge, ~6h, BLOCKING für Phase B)

**A1** — `/automate` 404 untersuchen: entweder Route implementieren oder Nav-Link entfernen + 410-Redirect setzen. Decision: User. (~30min)

**A2** — Mermaid-Render in /ops: Mermaid-Library laden und render in `<pre>` ersetzen durch SVG-Output. (~1h)

**A3** — DATA: FALLBACK Root-Cause: per-agent untersuchen warum 5/6 nicht live-source haben. Vermutung: Source ist tasks.json statt SSE-stream. Forge debuggt. (~2h)

**A4** — Cost-Source-of-Truth: einigen ob `/api/costs` oder `/api/analytics` die Wahrheit ist. Andere Page muss daraus deriveiren statt parallel rechnen. (~2h)

**A5** — ErrorBoundary global einziehen (Next.js error.tsx + per-tab error.tsx). (~30min Pixel)

### Phase B — Claude-Design-Manual-Pass (User in Web-UI, ~3h, NICHT-BLOCKING parallel zu A)

Workflow laut deinem [W3-Plan](vault/03-Projects/plans/claude-code-openclaw-integration-roadmap-2026-04-20.md):

> Claude Design hat KEINE API/SDK/MCP (release 2026-04-17). Manual Pipeline: MC-Repo -> Claude Design Web-UI feeden -> Iterieren -> Handoff-Bundle exportieren -> Pixel implementiert.

**B1** — MC-Repo (oder relevante Sub-Components) in Claude Design Web-UI feeden. Falls schon aus 2026-04-20-taskboard-Iteration bekannt, dort ansetzen. (~30min)

**B2** — In Claude Design **3 priorisierte Iterations** ziehen:

1. **Skeleton + Empty-State System** (löst P1-2, P1-8 systemweit)
   - Pulsing skeleton card-template
   - Empty-state mit Title + Subtitle + 1 Suggested-Action-Button
   - Anwendbar auf Dashboard 0-Karten, Pipeline Loading, alle Listen

2. **Alert-Feed Hierarchy** (löst P1-3, P1-9, P1-10)
   - Severity-Color-Tokens (info/warn/error/critical) klar getrennt
   - Group-Collapse für SUPPRESS-Stream (eine Zeile statt 5404)
   - Acknowledge + Mute pro Alert + per Group

3. **Dashboard Drei-Karten Refinement** (löst P1-1 visuell)
   - Bessere Number-Typography (jetzt: nackte 0)
   - State-Differenzierung Loading/Empty/Active als visuelle Variants
   - Skeleton-Variant aus B2.1 wiederverwenden

**B3** — Export Handoff-Bundle pro Iteration -> `vault/07-Research/design-handoffs/2026-04-27-mc-audit/` mit Sub-Folders `skeletons/`, `alerts/`, `dashboard/`. (~30min)

### Phase C — Pixel implementiert Handoff (Pixel, ~8h, nach Phase B)

**C1** — Skeleton + Empty-State als shared Components in `mission-control/src/components/ui/`. (~3h)

**C2** — Alerts-Page Refactor mit Handoff-Tokens. Suppress-Group-Collapse implementieren. (~3h)

**C3** — Dashboard Drei-Karten mit neuen Variants verdrahten. (~2h)

### Backlog (nicht in diesem Sprint)

- P1-4, P1-5, P1-6, P1-7 -> Pixel-Polish-Sprint danach
- P2-1 (Org-Chart) -> eigener Sprint, da custom Visualisierung (react-flow), nicht Claude-Design-Scope
- P2-9, P2-10 -> Forge-Konsistenz-Pass (Filter/Architecture/Team alle 6 vs 10 Agents alignen)

---

## Verification (DoD pro Phase)

**Phase A done wenn:**
- `curl http://192.168.178.61:3000/automate` -> 200 oder Nav-Link weg
- `/ops` Dependency-Graph zeigt SVG (curl + grep `<svg`)
- `document.querySelectorAll('[class*=fallback]')` auf /kanban zeigt <=1 (statt 5)
- /costs und /analytics zeigen denselben Cost-Wert (visual diff)
- React-Throw-Test triggert Error-Boundary statt White-Screen

**Phase B done wenn:**
- `ls vault/07-Research/design-handoffs/2026-04-27-mc-audit/` zeigt 3 Subfolder mit je INDEX.md + tokens.json + components/

**Phase C done wenn:**
- `document.querySelector('[class*=skeleton]')` auf jeder Page nicht mehr null während Loading
- /alerts zeigt Suppress-Stream als 1 Group-Card statt 5404 Einzeleinträge
- Dashboard Drei-Karten haben skeleton/empty/active visual variants im Storybook

---

## Open Questions für User

1. **A1 Decision:** `/automate` ausbauen oder Nav-Link entfernen?
2. **A4 Decision:** Welche Cost-API ist Source-of-Truth — `/api/costs` oder `/api/analytics/cost-pressure`?
3. **B1 Scope:** Komplettes MC-Repo in Claude Design feeden oder nur `mission-control/src/components/` Sub-Tree?
4. **C-Timing:** Pixel direkt nach Phase B starten oder erst auf weiteres User-Review der Handoffs warten?

---

## Notes

- Memory-File `session_2026-04-19_full_day.md` erwähnt "Sprint-I Mobile-Polish v2 6/7 done" — die Mobile-Findings hier (P1-2, P2-4) deuten an dass der Polish nicht durchgehalten wurde. Forge-Investigation könnte sich lohnen.
- Memory ist 7-9 Tage alt — alle obigen Befunde sind frisch (live-audit), nicht aus Memory abgeleitet.
- Claude-Design-Web-UI braucht Claude Pro/Max-Subscription (laut Roadmap-Doc Section 5).
- Es gibt KEINE OpenClaw-Verbindung zu Claude Design — manueller Mensch-im-Loop-Workflow ist W3-Stand. W4 wartet auf Anthropic-API/MCP-Release.
