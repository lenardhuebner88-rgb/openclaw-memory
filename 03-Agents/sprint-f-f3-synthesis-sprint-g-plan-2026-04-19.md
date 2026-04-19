# Sprint-F F3: Synthesis + Sprint-G Plan
**Datum:** 2026-04-19 19:57 UTC+2
**Author:** Atlas

---

## Phase-1 Audit Results Summary

### F1 — Lens Script Inventory (✅ done)
- **86 scripts** audited | 24 high-risk (28%) | 7 broken (mis-categorized .mjs)
- 40 bash, 29 python, 17 node
- Invoked by: 58 manual, 26 cron, 15 HEARTBEAT, 8 systemd

### F2 — Forge Scheduler Graph (✅ done)
- **65 scheduler entries** | 4 types | 35 high-risk | 10 broken
- Types: crontab-user (24), openclaw-cron-plugin (24), heartbeat-driven (11), systemd-user-timer (6)

---

## Critical Findings (must-fix before Sprint-G)

### 🔴 P0 — Broken Schedulers (10 entries)
| Scheduler | Broken Jobs | Impact |
|-----------|-------------|--------|
| systemd-user-timer | 4 failed services (forge-heartbeat, lens-cost-check, openclaw-healthcheck, researcher-run) | Agent health checks broken |
| openclaw-cron-plugin | Sprint-Debrief-Watch (consecutiveErrors=26) | Evening debriefs nicht zugestellt |

### 🔴 P0 — Alert-Fatigue Chain (redundant)
`mc-watchdog.sh` → `mc-critical-alert.py` → `session-freeze-watcher.sh` → heartbeat-death-check
→ Alle 5 alarmieren `#alerts` bei Overlap → keine Deduplizierung

### 🟡 P1 — High-Risk Script Cluster
- 11 high-risk in `~/.openclaw/scripts/` (zombie killers, task reapers)
- 14+ backups of `worker-monitor.py` → Iteratives debugging, alte Versionen bleiben liegen
- Build pipeline (`build.mjs`, `build-lock.mjs`, `stability-preflight.mjs`) = HIGH risk, keine Checkpoints

### 🟡 P1 — Stabilization Mode Tradeoff
Heartbeat: Auto-Respawn + Zombie-Detection + Orphaned-Detection alle bewusst deaktiviert
→ Manual Operations Last höher, aber System stabiler

---

## Sprint-G: Ops-Visualization + Cleanup

### G1 (Forge) — Broken Scheduler Fix
**Scope:** Fix 10 broken scheduler entries
- systemd failed services: `systemctl --user restart` + verify
- Sprint-Debrief-Watch: cron schedule korrigieren oder als `broken` markieren

### G2 (Lens) — Alert-Dedupe Chain
**Scope:** Konsolidiere 5 redundante Alert-Quellen → 1 zentraler Alert-Dispatcher
- `mc-watchdog.sh`, `mc-critical-alert.py`, `session-freeze-watcher.sh`, heartbeat-death-check, lens-cost-check
- Cooldown-Logik: wenn Alert X in letzten 5min → Alert Y suppressed
- Output: 1 canonical alert flow → `#alerts`

### G3 (Atlas) — Ops Dashboard
**Scope:** MC Dashboard Route `/ops` mit:
- Scheduler-Status-Table (4 Typen, 65 entries, filterbar)
- Script-Inventory-View (86 scripts, risk farben)
- Dependency-Graph (Mermaid embedded)
- Live-Health-Checks per Typ

### G4 (Pixel) — Dashboard UI
**Scope:** UI für `/ops` route
- Risk-Farben: 🔴 high, 🟡 medium, 🟢 low
- Filter bar: nach type, risk, status
- Click-to-expand: job details, last run, next run
- Refresh button + auto-refresh indicator

---

## Estimated Times
| Sub | Agent | Time |
|-----|-------|------|
| G1 | Forge | ~45min |
| G2 | Lens | ~30min |
| G3 | Atlas | ~20min |
| G4 | Pixel | ~45min |

---

## Risks
- G1 systemd fixes erfordern careful verify (restart kann MC transient unterbrechen)
- G2 Alert-Chainänderung muss mit `#alerts` Monitoring kompatibel bleiben
- G3/G4 hängen von G1+G2 sauberen Daten ab

---

**Status:** Sprint-F F1+F2 complete. Sprint-G Plan ready for Operator Approval.

---

## Sprint-G Final Status (2026-04-19 20:29 UTC+2)

| Sub | Board | Agent | Status | Result |
|-----|-------|-------|--------|--------|
| G1 Broken Schedulers | `ba5e654b` | Forge | ✅ done | 4 systemd fixed, 0 failed, Debrief-Watch consecutiveErrors=0 |
| G2 Alert-Dedupe | `b8b40aaf` | Lens | ✅ done | alert-dispatcher.sh (5min cooldown), 5 sources consolidated |
| G3 Ops-Dashboard API | `42fa712d` | Forge | ✅ done | 4 endpoints, 65 schedulers, 86 scripts, curl 200 |
| G4 Ops-Dashboard UI | `0423431e` | Pixel | ✅ done | /ops route, 4 tabs, KPI cards, filter tables, curl 200 |

### G4 Changed Files:
- `src/app/ops/page.tsx`
- `src/components/ops/ops-dashboard-client.tsx`
- `src/components/ops/kpi-cards.tsx`
- `src/components/ops/dependency-graph.tsx`
- `src/components/ops/scheduler-table.tsx`
- `src/components/ops/script-table.tsx`
- `src/components/ops/health-panel.tsx`
- `src/components/mission-shell.tsx`
- `src/components/bottom-tab-bar.tsx`
- `src/lib/memory-layers.ts` (typecheck fix)
- `tailwind.config.ts` (typecheck fix)

### Verification Summary:
- `/api/ops` → 200 ✅
- `/api/ops/schedulers` → 200 ✅
- `/api/ops/scripts` → 200 ✅
- `/api/ops/health` → 200 ✅
- `/ops` → 200 ✅
- `npm run build` ✅
- `systemd --failed` → 0 ✅
- alert-dispatcher cooldown test: dispatch + suppress ✅

**Sprint-G abgeschlossen** — System nun vollständig inventarisiert + visualisiert.
