---
title: Sprint-I Mobile-Polish P1/P2 Plan
date: 2026-04-19
author: Operator (pieter_pan) + Assistant (Claude) Sprint-E Post-Mortem
status: ready-to-dispatch
type: sprint-plan
trigger_phrase: "Atlas nun nächster Sprint follow #42"
source_findings: Sprint-E Playwright-Mobile-Audit 2026-04-19 17:23 UTC
prerequisites: Sprint-E done, Sprint-F Ops-Inventory done (oder parallel)
blocking_factors: H9 Dark-Token-Audit sollte NACH Sprint-I laufen (reduziert Contrast-Fix-Doppelung)
estimated_effort: 9h orchestriert
---

# Sprint-I — Mobile-Polish P1/P2

## 🎯 Scope

Residuale Findings aus dem Sprint-E Playwright-Mobile-Smoke adressieren. E1 hat alle P0 Accessibility-Issues gefixt (17× `min-h-[44px]` deployed, Dashboard-Hero refactored, Kanban ViewToggle live), aber P1/P2 Mobile-UI-Findings wurden bewusst außerhalb des E1-Scopes gehalten:

| Finding | Severity | Betroffen | Count | Sprint-I Sub |
|---|---|---|---|---|
| Secondary-Nav Tap-Targets 88-113 × 38 px (unter 44) | P1 | /costs, /alerts, /monitoring | 8+ Tabs | **I1** |
| Text < 16px Elements | P2 | alle Routes | 171 auf /alerts, 131 auf /costs | **I2** |
| No Loading-Skeleton | P2 | /alerts, /costs, /monitoring | 3 Routes | **I3a** |
| Empty-State missing | P2 | /alerts, /monitoring | 2 Routes | **I3b** |
| Color-Contrast AA Violations (addressed by Sprint-H H9) | P1 | /monitoring ratio 1.10, /alerts ratio 2.57 | 4 Violations | **→ H9** (Sprint-H) |

**Anti-Scope:**
- Keine neuen Routes
- Keine Navigation-Strukturänderungen (E4 hat 7 Primary-Navs final fixiert)
- Kein Dark-Token-Rewrite (gehört zu Sprint-H H9)
- Keine Desktop-Only Änderungen

## 📋 Sub-Tasks

### Sub-I1: Secondary-Nav Tap-Target Uplift (44×44)
**Agent:** Pixel (frontend-guru)  
**Scope:** Sekundäre Nav-Tabs auf `/costs`, `/alerts`, `/monitoring` (ggf. auch `/taskboard`, `/kanban` falls analoge Tabs) von aktuell ~38px Höhe auf **mindestens 44px** anheben. Keine Layout-Verschiebung — Tabs bleiben horizontal, Padding / Height-Klasse hochstellen.  
**Files (Hinweis, letzte Authority hat Pixel):**
- `src/components/costs/cost-sub-nav.tsx` (oder ähnlich)
- `src/components/alerts/alerts-tabs.tsx`
- `src/components/monitoring/monitoring-tabs.tsx`
- Tailwind-Klasse: `py-2` → `py-3` + explicit `min-h-[44px]`  
**Acceptance:**
- Playwright-Mobile-Smoke: TAP-TARGET findings auf `/costs`, `/alerts`, `/monitoring` = 0
- Visual-Diff-Screenshot zeigt gleiche Tabs, nur höher
- Kein horizontal scroll auf iPhone SE 375×667  
**Estimate:** 2h

### Sub-I2: Typography-Scale-Reset (16px Base)
**Agent:** Pixel (frontend-guru) + James (researcher, **kurz vorher**)  
**Scope:** Elements mit `font-size < 16px` systematisch hochstufen auf minimum 16px Base. Micro-Labels (z.B. "Mission Control" 11px Top-Bar) dürfen bei 14px bleiben wenn sie **Ornament** sind, nicht **Content**. Unterscheidung basiert auf: hat das Element eine ARIA-Rolle oder ist es ein Primär-Text?  
**James-Vorarbeit (30 min):**
- Research: Best-in-Class Typography-Scales für Operator-Dashboards (Linear, Datadog, Grafana Mobile)
- Empfehlung: Tailwind-Konfig für `text-xs` (12px) → nur Ornament erlauben, `text-sm` (14px) → Metadata, `text-base` (16px) → Content-default
- Output: `vault/03-Agents/james-mobile-typography-research-2026-04-19.md` (Zielformat: 1 Page, Scale-Table, 3 Beispiele aus anderen Tools)  
**Pixel-Implementation (2.5h):**
- Tailwind-Audit aller `text-xs` Klassen — Liste generieren
- Pro Vorkommen: Entscheidung Ornament vs Content nach James-Guide
- Ersetze Content-Instances durch `text-sm` (14→14 bleibt) oder `text-base` (≥16)
- Kritisch: Playwright-Mobile-Smoke laufen lassen bis Text<16px-Count < 50 (von aktuell 171+131=302 gesamt auf unter 50 = 85% Reduktion)  
**Acceptance:**
- Playwright-Mobile-Smoke Text<16px-Count < 50 auf jedem Route-Viewport
- Visual-Regression-Test: keine UI-Breakage
- Lesbarkeit bei iPhone SE deutlich verbessert (qualitativ bewertet)  
**Estimate:** 3h gesamt

### Sub-I3: Loading-Skeleton + Empty-State Coverage
**Agent:** Pixel (frontend-guru) + Lens (efficiency-auditor, **kurz vorher**)  
**Scope:** Routes ohne Loading-Skeleton (`/alerts`, `/costs`, `/monitoring`) bekommen Skeletons. Routes ohne Empty-State (`/alerts`, `/monitoring`) bekommen Empty-State-Components.  
**Lens-Vorarbeit (30 min):**
- Audit aller States pro Route: loading / empty / populated / error
- Pro Route-State: existierendes oder fehlendes UI-Element melden
- Output: `vault/03-Agents/lens-route-state-coverage-audit-2026-04-19.md` (Tabelle Route × State × Component)  
**Pixel-Implementation (2.5h):**
- Pro fehlender Skeleton: nutze existierende `<SkeletonCard>` / `<SkeletonTable>` aus `src/components/ui/skeleton.tsx` (wenn existent, sonst erst anlegen)
- Pro fehlender Empty-State: einfache `<EmptyState icon message action>` Component, wiederverwendbar
- Wire-up: Suspense-Boundary oder `isLoading` / `data.length === 0` guards  
**Acceptance:**
- Playwright-Mobile-Smoke no-loading-skeleton-found Count = 0 auf allen 5 Audit-Routes
- Empty-State-visible: true für Routes mit no-data scenario (via test-fixture)
- Jeder neue State hat `data-testid` für future-testing  
**Estimate:** 3h gesamt

### Sub-I4: Final Playwright Mobile-Audit (0-Findings-Check)
**Agent:** Pixel (frontend-guru)  
**Scope:** Nach I1+I2+I3 done: Playwright-Mobile-Smoke komplett re-run, Tabelle mit Vorher-Nachher-Counts für jede Finding-Klasse. Report als `vault/03-Agents/sprint-i-final-mobile-audit-2026-04-19.md`.  
**Acceptance:**
- Report enthält Before/After Tabelle mit 5 Finding-Klassen (Tap-Target, Text-Size, Loading, Empty-State, Contrast).
- Contrast bleibt auf H9-Niveau (Sprint-H adressiert das — nicht Sprint-I Acceptance-Blocker).
- Alle anderen 4 Klassen: Post-Sprint-I ≤ 10% des Pre-Sprint-I Count.
**Estimate:** 1h

## 🔗 Dependencies

```
Sprint-E done ──┐
                ├──> Sprint-F Ops-Inventory (queued)
                ├──> Sprint-I (this doc) ────┐
Sprint-H H9 ────┘                            ├──> Sprint-I I4 final
                                             │
                                             └──> close Mobile-UX-Chapter 2026-04
```

Sprint-I kann parallel zu Sprint-F starten (disjoint scope: Ops vs UI).  
Sprint-I **sollte** nach Sprint-H H9 starten (oder H9 zuerst absplitten) — sonst überlappen Contrast-Fixes mit Typography.  
**Konservativer Vorschlag:** Sprint-H H9 **erst nach Sprint-I I4** starten, damit Typography-Scale-Änderungen keine neuen Contrast-Issues einführen.

## 🤖 Atlas-Dispatch-Prompt (bei Trigger "follow #42")

```
REAL_TASK=true ORCHESTRATOR_MODE=true. Sprint-I Mobile-Polish P1/P2 — NICHT heartbeat.

Kontext:
Sprint-E durch (E1-E5 commits: edb0d56, 7f9122c, 10b7274, ea13c39, [E5-commits]).
Playwright-Mobile-Smoke zeigte Post-E1 residuale P1/P2 Findings die bewusst außerhalb E1-Scope blieben.
Sprint-I adressiert diese systematisch.

Plan-Doku: /home/piet/vault/03-Agents/sprint-i-mobile-polish-plan-2026-04-19.md
(nutze qmd deep_search "sprint-i mobile polish" um Plan zu lesen)

4 Sub-Tasks:
- Sub-I1 (Pixel): Secondary-Nav Tap-Targets 44×44 auf /costs /alerts /monitoring (2h)
- Sub-I2 (James Research 30min → Pixel Implementation 2.5h): Typography-Scale-Reset, Text<16px unter 50 (3h gesamt)
- Sub-I3 (Lens Audit 30min → Pixel Implementation 2.5h): Loading-Skeletons + Empty-States für /alerts /costs /monitoring (3h gesamt)
- Sub-I4 (Pixel): Final Playwright 0-Findings Report (1h)

Playbook:
1. qmd deep_search "sprint-i mobile polish" um Plan zu lesen
2. Pre-Research: qmd deep_search "lens mobile ui audit" + "james operator dashboard research v2" (Sprint-D D1+D2 Baselines)
3. POST 4 Board-Tasks via taskboard_create_task (R44 compliance!)
4. Dispatch-Order:
   - James-Research (I2-prep) + Lens-Audit (I3-prep) **parallel**
   - Nach beiden done: I1 (Pixel) + I2-Impl (Pixel) + I3-Impl (Pixel) **sequenziell** (alle Pixel, WIP-Limit 2)
   - I4 final nach I1+I2+I3 done

Constraints:
- MC-Restart via `mc-restart-safe 120 "sprint-i-sub-<id>"` (R46 Pflicht!)
- Receipt-Discipline R45: jeder Sub postet `accepted` within 60s, `progress` alle 5min
- Keine Breaking-Changes an bestehenden Routes (nur Klassen-Changes / Component-Additionen)
- Sprint-I Anti-Scope: keine neuen Routes, keine Navigation-Änderung, kein Dark-Token-Rewrite (→ H9)

Rules:
- R35: "done" nur nach ls-verify der Report-Files + git-log-Check der Commits
- R41: QMD deep_search vor File-Brute-Read
- R42/R46: mc-restart-safe verwenden statt systemctl restart
- R44: alle Sub-Tasks über taskboard_create_task, nicht sessions_spawn-only
- R45: Receipt-Discipline — kein assigned > 2min ohne accepted-receipt
- R40: Pixel/James/Lens 2/5min stall-threshold respektieren; Atlas-main 10/20min override

Zeit-Budget: ~9h orchestriert. Operator monitort passiv.

Return format:
- EXECUTION_STATUS
- RESULT_SUMMARY mit:
  - 4 Board-Task-IDs + Commits
  - 3 Report-File-Paths (James-Research + Lens-Audit + I4-Final-Report, ls-verified!)
  - Playwright-Vorher-Nachher-Tabelle aus I4
  - Count-Reductions pro Finding-Klasse
  - Optional: Residual-Findings-Liste als Sprint-I-Follow-up-Kandidaten

Los.
```

## 📊 Acceptance Sprint-Level

- [ ] 4 Board-Tasks in `done`, alle R44-Board-visible (nicht session-spawn-only)
- [ ] 3 Git-Commits (I1, I2, I3) auf `main`
- [ ] James-Research-Report in Vault (ls-verified)
- [ ] Lens-Route-State-Audit-Report in Vault (ls-verified)
- [ ] I4-Final-Audit-Report in Vault mit Before/After-Tabelle
- [ ] Playwright Mobile-Smoke: Tap-Target-Findings = 0, Text<16px-Count < 50, Loading-Skeleton-Coverage = 100%, Empty-State-Coverage = 100%
- [ ] 0 MC-Flap-Incidents durch mc-restart-safe-Nutzung
- [ ] 0 R45-Violations (alle Subs posten Receipts)

## 🚨 Risk + Mitigation

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Typography-Scale-Reset bricht Desktop-Layout | Mittel | Hoch | I2 Playwright-Desktop-Smoke zusätzlich; I4 validiert |
| Loading-Skeleton erhöht Initial-Bundle > 10% | Niedrig | Mittel | Lazy-load Skeleton-Component |
| I2 verändert 200+ Klassen-Instances → Merge-Konflikt wahrscheinlich wenn Sprint-F parallel | Mittel | Niedrig | Sprint-F hat disjoint file-scope (Ops-Scripts), kein echter Konflikt |
| Pixel WIP-Limit 2 → I1+I2-Impl+I3-Impl sequenziell = lange Queue | Mittel | Mittel | James + Lens Vor-Audits parallel zu I1 laufen lassen |
| Atlas Sub-Dispatch vergisst R44/R45/R46 (Preamble erst seit 2026-04-19 17:21 UTC live) | Niedrig | Hoch | Dispatch-Prompt oben enthält **explizit** alle 3 Rules als Constraints |

## 🔗 Referenzen

- Sprint-E Endreport: `vault/03-Agents/sprint-e-endreport-2026-04-19.md` (Quelle der Findings)
- Lens-D1-Audit Baseline: `vault/03-Agents/lens-mobile-ui-audit-2026-04-19.md`
- James-D2-Research Baseline: `vault/03-Agents/james-operator-dashboard-research-v2-2026-04-19.md`
- Sprint-H Plan: `memory/sprint_h_infra_hardening_plan.md` (H9 Dark-Contrast addressiert verbleibende Findings)
- Rules: R35, R40, R41, R42, R44, R45, R46 (alle in `workspace/memory/rules.jsonl`)

## 📝 Signoff

Operator (pieter_pan) 2026-04-19 17:30 UTC: **ready-to-dispatch**.  
Trigger-Phrase zum Start: **"Atlas nun nächster Sprint follow #42"**

---

**Ende Sprint-I Plan.** Nach Abschluss: Sprint-J offen für Entscheidung (L3-Ziele aus Next-Level-Roadmap oder Maintenance-Sprint).
