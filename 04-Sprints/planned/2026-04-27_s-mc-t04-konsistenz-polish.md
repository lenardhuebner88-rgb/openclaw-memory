---
name: Sprint-MC-T04 Konsistenz + Polish
description: Atlas-autonomous P1/P2 fixes - Sprachgemisch DE/EN harmonisieren, Section-Links Redundanz, Whitespace-Layout, Agent-Count alignen, Pipeline-Filter komplettieren.
status: planned
since: 2026-04-27
owner: Operator (pieter_pan)
trigger_phrase: "Atlas Sprint MC-T04 Konsistenz starten"
related:
  - vault/04-Sprints/planned/2026-04-27_mc-ui-audit-claude-design-prep.md
autonomy_mode: full
operator_gates: none
---

# Sprint-MC-T04 — Konsistenz + Polish (Atlas-autonom)

**Context:** Audit hat 5 systemische Konsistenz-Probleme gefunden die einzeln "klein" wirken aber zusammen die Cockpit-Lesbarkeit ruinieren: DE/EN-Sprachgemisch, Section-Links wiederholen Top-Nav, Layout-Whitespace 200-400px, Agent-Counts (6 vs 10 vs 4) widersprechen sich quer durch die Pages, Pipeline-Filter fehlen 2 von 6 Agents.

**Trigger:** `Atlas Sprint MC-T04 Konsistenz starten`

**Atlas-Mandate:**
- Volle autonome Steuerung — keine Operator-Approval-Gates
- Atlas trifft Sprach-Decision per Heuristic in P1
- Atlas postet Sprint-Done-Report in `frontend-guru` (1486480170763157516) wenn alle 5 Subs done

---

## Scope-Matrix

| Sub | Title | Owner | Estimate | DoD |
|---|---|---|---|---|
| **K1** | Sprachgemisch DE/EN harmonisieren | Pixel | 2-2.5h | Top-Nav + Tab-Headers + Status-Pills DE; Code-Identifiers EN. Konsistent über alle 11 Pages |
| **K2** | Section-Links Redundanz weg | Pixel | 1.5-2h | Section-Links auf Subpages zeigen nur Sub-Views, keine Top-Nav-Items mehr |
| **K3** | Whitespace-Layout fix | Pixel | 1-1.5h | <300px Schwarz unter Content auf jeder Page (statt 200-400px wie heute) |
| **K4** | Agent-Count Konsistenz | Forge + Pixel | 1.5-2h | Architecture / Pipeline / Team zeigen alle dieselbe User-Facing-Liste (6 Agents). System-Agents in eigene Sub-Section |
| **K5** | Pipeline-Filter James/Spark hinzufügen | Pixel | 30-45 min | /kanban Filter-Pills zeigen alle 6 Agents (Atlas/Forge/Pixel/Lens/James/Spark) |

**Total Estimate:** 6.5-8.5h

---

## K1 — Sprachgemisch DE/EN harmonisieren

### Problem
- Headers: "Mehr" (DE) vs "Analytics" (EN) auf gleicher Page
- "Schnellaktionen" (DE) + "Section Links: Overview/Architecture/Analytics" (EN)
- "Tasks aktiv" (DE) + "TOOLS ACTIVE" (EN)
- Inkonsistenter Look-and-Feel

### Atlas-Decision (autonom, ohne Operator)
**DE = User-Facing-Sprache. EN = Technical-Identifiers.**

Reasoning:
- Operator (pieter_pan) ist deutschsprachig (vault, Discord-Channel sind DE)
- "Mission Control" / "Dashboard" / "Operator" bleiben EN als etablierte Begriffe
- Technische Tokens (API-Pfade, JSON-Keys, Code-Identifiers) bleiben EN

### Mapping (Atlas-binding für Pixel)

| Heute | Soll |
|---|---|
| Tab "Tasks" | "Aufgaben" |
| Tab "Alerts" | "Alarme" |
| Tab "Team" | "Team" (bleibt) |
| Tab "Memory" | "Gedächtnis" |
| Tab "Automate" | (raus laut MC-T01) |
| Tab "More" / "Mehr" | "Mehr" (DE wird Norm) |
| "Section Links" | "Unteransichten" |
| "Quick Actions" | "Schnellaktionen" (bleibt) |
| "TOOLS ACTIVE" | "AKTIVE TOOLS" |
| "PIPELINE SIGNAL" | "PIPELINE-SIGNAL" |
| "READ BUDGET" | "LESEBUDGET" |
| "AGENTS LIVE" | "AGENTEN LIVE" |
| "ACTIVE WORK" | "AKTIVE ARBEIT" |
| "NEEDS REVIEW" | "BRAUCHT REVIEW" |
| "QUEUED NEXT" | "ALS NÄCHSTES" |
| "NEEDS ATTENTION" (Card-Badge) | "BRAUCHT FOKUS" |
| "MONITORING" | "BEOBACHTET" |
| "FRESH" | "FRISCH" |
| "STALE" | "VERALTET" |
| "DATA: FALLBACK" | "DATEN: FALLBACK" |
| "DATA: CACHED" | "DATEN: CACHED" (technical, bleibt mixed) |

### Fix-Steps für Pixel
1. Sweep: `grep -rn "Tasks\|Alerts\|TOOLS ACTIVE\|NEEDS REVIEW" mission-control/src/components/ mission-control/src/app/`
2. Per-File Edit nach Mapping
3. Build + Visual-Check auf 5 Beispiel-Pages

### Verify
- `curl -s http://localhost:3000/dashboard | grep -c "AGENTEN LIVE"` ≥1
- `curl -s http://localhost:3000/kanban | grep -c "BRAUCHT FOKUS"` ≥1 (Pixel-Card)
- `curl -s http://localhost:3000/alerts | grep -ic "alarme"` ≥1

---

## K2 — Section-Links Redundanz weg

### Problem
Auf /more, /costs, /analytics, /ops zeigen Section-Links: `Overview / Architecture / Analytics / Ops / Costs / Trends / Files / Calendar` — das wiederholt 6 Top-Nav-Items als zweite Navigation.

### Atlas-Heuristic für Pixel
**Section-Links sollen nur Sub-Views innerhalb der aktuellen Page haben, nicht Querverweise auf andere Top-Level-Pages.**

Beispiel-Anwendung:
- `/costs` Section-Links sollen sein: "Heute / Diese Woche / Diesen Monat" (Time-Range-Tabs) — NICHT "Architecture / Analytics / Ops"
- `/ops` Section-Links: "Overview / Schedulers / Scripts / Health" (existiert teilweise schon, "Overview"-Toggle bleibt)
- `/more` Section-Links: bleiben als Hub-Index OK
- `/analytics` Section-Links: "Operator State / Cost Focus / Health Snapshot / Alert History" (interne Anchor-Links)

### Fix-Steps für Pixel
1. Pro Page: identifiziere `<SectionLinks>` Component
2. Replace mit page-specific Sub-View-Tabs ODER Anchor-Links
3. Wenn Sub-Tabs schon existieren (z.B. /ops Overview/Schedulers/Scripts/Health) → SectionLinks entfernen, nur einen Tab-Bar behalten

### Verify
- /costs zeigt keine "Architecture"-Link mehr
- /analytics zeigt keine "Ops"-Link mehr
- Keine Page hat 2 Navigation-Bars die das gleiche tun

---

## K3 — Whitespace-Layout fix

### Problem
- Audit-Beobachtung: 200-400px schwarzer Whitespace unter dem Content auf /dashboard, /kanban, /memory
- Sieht aus wie min-height-Container der content-height ignoriert

### Atlas-Heuristic für Pixel
1. `grep -rn "min-h-screen\|min-height: 100vh\|h-screen" mission-control/src/app/ mission-control/src/components/layout/`
2. Vermutung: Ein Container hat `min-h-screen` aber Content fließt nicht — Body bekommt extra-space.

### Fix-Steps für Pixel
1. Layout-Container check: `app/layout.tsx` oder ähnlich
2. Wenn `min-h-screen` auf einem inner-Container → entfernen oder durch `min-h-[60vh]` ersetzen für graceful empty-states
3. Alternative: `flex flex-col` mit `flex-1` auf main-content statt min-height-hack

### Verify
- /dashboard scroll-down: kein langer Black-Tail mehr unter dem letzten Content-Block
- Browser-DevTools: `getComputedStyle(document.querySelector('main')).minHeight` zeigt entweder `0px` oder `60vh` statt `100vh`
- Mobile: gleiches Verhalten

---

## K4 — Agent-Count Konsistenz

### Problem
- Architecture zeigt 10 Agents (codex, default, efficiency-auditor, frontend-guru, james, main, spark, sre-expert, test-lock, worker)
- Team-Tab sagt "6 agents incl. Spark Relief"
- Pipeline-Filter zeigt nur 4 (Atlas/Forge/Pixel/Lens) — siehe K5

### Atlas-Decision (binding)
**6 User-Facing-Agents:** Atlas (main), Forge (sre-expert), Pixel (frontend-guru), Lens (efficiency-auditor), James (james), Spark (spark)

**4 System-Agents:** codex, default, test-lock, worker — eigene Sub-Section "System Agents" auf Architecture, NICHT in Team/Pipeline

### Fix-Steps für Forge + Pixel

**Forge — Backend:**
1. `/api/agents` Endpoint sollte `category: 'user-facing'|'system'` field haben
2. Default-Filter für `/api/agents?category=user-facing` → 6 results
3. Architecture pulls beide categories

**Pixel — UI:**
1. Architecture-Page: 2 sections "Agents (6)" + "System Agents (4)" 
2. Team-Page: nur user-facing (sollte schon sein, count konsistent)
3. Pipeline (siehe K5 für Filter)
4. Stat-Card auf Architecture: "Active Agents 2/6" statt "2/10"

### Verify
- /architecture: zwei distinkte Sektionen, Top-KPI zeigt "2/6"
- /team: 6 Agent-Cards
- /kanban: 6 Agent-Cards (post K5)
- `curl -s http://localhost:3000/api/agents?category=user-facing | jq '. | length'` → 6

---

## K5 — Pipeline-Filter James/Spark hinzufügen

### Problem
Audit-Beobachtung: /kanban Filter-Pills zeigen `All agents | Atlas | Forge | Pixel | Lens` — James und Spark sind als Cards sichtbar aber nicht filterbar.

### Fix-Steps für Pixel
1. Identifiziere Filter-Component: `grep -rn "All agents\|Atlas.*Forge.*Pixel" mission-control/src/components/kanban/`
2. Filter-Source sollte aus `/api/agents?category=user-facing` kommen (siehe K4) statt hardcoded list
3. Wenn hardcoded: append `'James', 'Spark'` zum Array

### Verify
- /kanban Filter zeigt 6 Pills + "All agents"
- Click "James" → nur James-Card sichtbar
- Click "Spark" → nur Spark-Card sichtbar

---

## Cross-Sprint Receipts + Final-Step

Receipts laut R45/R50.

**Atlas-Sprint-Final-Step:**
1. Alle 5 Subs done → Atlas postet Discord-Report in `frontend-guru`:
   - K1 Sprach-Sweep: X Files, Y Strings ersetzt
   - K2 SectionLinks: bereinigt auf 4 Pages
   - K3 Layout: min-height fix in `<file>`
   - K4 Agent-Counts: konsistent über 3 Pages
   - K5 Filter: 6 Pills live
2. Atlas renamed Plan-Doc nach `vault/04-Sprints/done/`

---

## Notes für Atlas

- K1 (Sprache) ist der größte Sub — Pixel braucht ~2.5h
- K1 + K2 + K3 sind parallel-fähig in Pixel (verschiedene Files)
- K4 + K5 müssen sequenziell: K4 Backend-Endpoint zuerst, K5 nutzt den neuen Endpoint
- Risk-Note: K1 Sprach-Sweep kann Translation-Strings in Tests breaken — Pixel runs `npm test` post-Edit
