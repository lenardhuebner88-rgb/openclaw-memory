---
title: Sprint-H Board Analytics + Alerting Plan
date: 2026-04-19 21:00 UTC
author: Atlas
scope: Board-KPI-API formalisieren + Alerting-Engine + Frontend-Tableau
status: ready-to-dispatch
type: sprint-plan
trigger_phrase: "Sprint-H dispatch"
prerequisites: Sprint-G G3 (Ops-API) done
blocking_factors: Keine
estimated_effort: ~6h orchestriert
---

# Sprint-H — Board Analytics + Alerting

## Warum Sprint-H

Sprint-G G3 hat `/api/trends` mit Task/Cost/Event-Timelines gebaut. Das Board zeigt bereits `executiveKpis` + `executiveTrends` im Task-Board-UI.

**Lücke:** Keine formale Analytics-API mit Alerting-Schwellen, kein eigenständiger `/analytics` Route, keine automatischen Alerts bei KPI-Anomalien.

## Sprint-H Scope

### H1 (Forge): Analytics-API + Alerting-Engine
**Agent:** Forge (sre-expert)

**Scope:**
1. `/api/analytics` Endpoint — formalisiert die KPI-Struktur als stabile, versionierte API:
   - `summary`: totalCreated, totalDone, totalFailed, avgVelocity, totalCost, periodDays
   - `kpis`: currentThroughput, throughputDirection, avgThroughput7d/30d, blockerCount, recoveryDelta, ownerLoad
   - `trends`: same Struktur wie `executiveTrends` aber mit expliziten Schwellen
   - `alertSignals`: array von aktuell aktiven Alerts (threshold violations)

2. Alerting-Engine für KPI-Anomalien:
   - Throughput-Drop: avgVelocity < 50% des 30d-Average → Alert
   - Blocker-Spike: blockers > 0 → Alert
   - Cost-Overrun: dailyCost > $5 → Warning, > $10 → Alert
   - Owner-Load-Imbalance: ein Agent hat > 80% der offenen Tasks → Warning
   - Recovery-Delta: > 5 recoveries/Tag → Info

3. Alert-Output: Events an `board-event-log` + optional Discord via alert-dispatcher
   - Cooldown: pro Alert-Typ 5min

**Files:**
- `src/app/api/analytics/route.ts` (NEU)
- `src/lib/analytics-engine.ts` (NEU, wiederverwendbar)
- Erweitert `src/lib/taskboard-store.ts` falls nötig

**Acceptance:**
- `GET /api/analytics` → 200,结构和 `/api/trends` kompatibel aber eigenständig
- Alert-Engine: bei Test-Daten mindestens 2 Alert-Signale generierbar
- Cooldown-Logik funktioniert (alert-dispatcher.sh vorhanden, 5min cooldown)
- curl verify `/api/analytics` + `/api/analytics/alerts` → 200

---

### H2 (Pixel): Analytics-Frontend-Route
**Agent:** Pixel (frontend-guru)

**Scope:**
1. `/analytics` Page — eigenständiger Report-Route (kein Tab, eher Modal oder Side-Panel)
   - KPI-Cards: Throughput, Blockers, Recovery, Owner-Load (是一样的 wie Board + Trend-Pfeile)
   - Time-Series Chart: 7d/30d Velocity (Balken + Linie)
   - Cost-Audit: Tageskosten mit Agent-Breakdown (aus trends API)
   - Alert-History: Letzte 10 Alerts mit Timestamp + Typ + Severity
   - Ton-Indikatoren: 🔴 risk, 🟡 warning, 🟢 good

2. Tab in Mission Control Navigation (Bottom-Tab oder Side)
   - `/analytics` Route
   - Toggle: 7d / 30d

**Files:**
- `src/app/analytics/page.tsx` (NEU)
- `src/components/analytics/analytics-client.tsx` (NEU)
- `src/components/analytics/kpi-trend-cards.tsx` (NEU)
- `src/components/analytics/velocity-chart.tsx` (NEU)
- `src/components/analytics/alert-history.tsx` (NEU)
- `src/components/bottom-tab-bar.tsx` (ADD analytics tab)

**Acceptance:**
- `/analytics` → 200
- Playwright: Page load, no crash, KPI cards visible
- Tab in bottom-bar navigiert nach `/analytics`
- Kein Layout-Bruch auf Mobile

---

### H3 (Atlas/Lens): Automated Alerting auf Schwellen
**Agent:** Atlas (main) + Lens (efficiency-auditor)

**Scope:**
1. Cron-Job `analytics-alert-watch` (alle 15min):
   - Pollt `/api/analytics/alerts`
   - Bei neuen Alerts → `alert-dispatcher.sh analytics-alert "<type>: <message>"`
   - Cooldown pro Alert-Typ 30min (nicht 5min wie intern)

2. Alert-Kategorien:
   - `THROUGHPUT_DROP`: avgVelocity < 50% 30d-Average
   - `BLOCKER_DETECTED`: blockerCount > 0
   - `COST_OVERRUN`: dailyCost > $5 → warn, > $10 → alert
   - `OWNER_LOAD_HIGH`: top owner > 80% open tasks

3. Alert-Destination: `#status-reports` (nicht `#alerts` — das ist für System-Alerts)

**Files:**
- `scripts/analytics-alert-watch.sh` (NEU)
- Cron-Eintrag via `openclaw cron add` (schedule: `*/15 * * * *`)
- Alert-dispatcher integration

**Acceptance:**
- Cron-Job existiert und ist enabled
- Test-Trigger zeigt Alert in `#status-reports`
- Cooldown verhindert > 2 Alerts gleichen Typs pro Stunde

---

## Zeit-Schätzung

| Sub | Agent | Zeit |
|-----|-------|------|
| H1 | Forge | ~2h |
| H2 | Pixel | ~2.5h |
| H3 | Atlas+Lens | ~1h |

---

## Anti-Scope

- Keine Änderungen an `/api/trends` (bleibt stable)
- Keine Änderungen an Board-Task-Flows
- Kein neues Datenmodell — nur Aggregation bestehender Daten
- Sprint-I Mobile-Fixes sind Anti-Scope (separate Sprint)

---

## Abhängigkeiten

```
Sprint-G (G3 Ops-API) ──> Sprint-H H1+H2+H3
Sprint-H H3 (Alerting) ──> Sprint-H H1 (API muss first existieren)
Sprint-H H2 (Frontend) ──> Sprint-H H1 (API muss first existieren)
```

---

## Acceptance Sprint-Level

- [ ] Board-Task für H1, H2, H3 in `done`
- [ ] `/api/analytics` → 200 ✅
- [ ] `/api/analytics/alerts` → 200 ✅
- [ ] `/analytics` Page → 200 ✅
- [ ] Bottom-Tab-Bar zeigt Analytics-Tab ✅
- [ ] `analytics-alert-watch` Cron existiert + enabled ✅
- [ ] Git-Commits pro Sub ✅
- [ ] 0 MC-Flap-Incidents (mc-restart-safe R46) ✅

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Analytics-Alerting erzeugt zu viele Alerts → Alert-Fatigue | Mittel | Hoch | H3 Cooldown 30min, nur 4 Alert-Typen |
| `/api/trends` und `/api/analytics` Redundanz → Confusion | Niedrig | Niedrig | Analytics ist aggregiert+alerting, Trends ist rohe Timeline |
| H2 Pixel-Build braucht MC-Restart → Race mit H3 | Mittel | Niedrig | mc-restart-safe serialisiert |

---

**Status:** Sprint-G complete (2026-04-19 20:30). Sprint-H Plan ready for dispatch.

**Trigger-Phrase:** "Sprint-H dispatch"
