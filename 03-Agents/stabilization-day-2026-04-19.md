---
title: Stabilization-Day 2026-04-19 — 6 Fixes Deployed
date: 2026-04-19 12:10 UTC
author: Operator (pieter_pan) direkt
scope: Post-Incident Quick-Fix-Session nach R30 Gateway-OOM + Deadlock
status: 6/6 fixes deployed, B2 passive acceptance ongoing
---

# Stabilization-Day 2026-04-19

## Context
Nach dem R30-Incident-Cluster (Gateway-OOM 10:38 UTC, Atlas-Orphan, Deadlock) und der Deep-RCA mit openclaw/openclaw-GitHub-Research habe ich in 20min 6 Fixes deployed die **3 von 5 Root-Causes direkt schliessen**.

## Deployed Fixes

### Fix A1 — KillMode Check
**Status:** ✅ already set (systemd default ist `control-group`)
**Action:** Keine noetig. Fix-Assumption aus Research war fuer unseren systemd-Default unguenstig formuliert.

### Fix A2 — Stall-Thresholds tighten
**Status:** ✅ live
**File:** `/home/piet/.openclaw/workspace/scripts/worker-monitor.py` Line 49-50
**Change:**
```python
STALL_WARN_MINUTES = 10  ->  2
STALL_HARD_MINUTES = 30  ->  5
```
**Backup:** `worker-monitor.py.bak-2026-04-19-stall-fix`
**Impact:** Deadlock-Heilzeit 30min -> 5min (Industry-Standard per Issue #39305)

### Fix B1 — PR #68846 cherry-pick (MCP Child-Cleanup ROOT-FIX)
**Status:** ✅ live, Gateway restarted cleanly
**File:** `/home/piet/.npm-global/lib/node_modules/openclaw/dist/attempt-execution.runtime-xF4aJ1vF.js` Line 371
**Change:**
```js
// BEFORE
cleanupBundleMcpOnRunEnd: params.opts.cleanupBundleMcpOnRunEnd,
// AFTER
cleanupBundleMcpOnRunEnd: params.opts.cleanupBundleMcpOnRunEnd || params.spawnedBy != null,
```
**Backup:** `*.bak-2026-04-19-pr68846`
**Patch-Tracker:** `/home/piet/.openclaw/patches/PR68846-applied.md`
**Impact:** MCP-Child-Prozesse werden bei sessions_spawn-Ende gereaped. **R30-Root beseitigt.**
**Gateway-Restart:** 12:05 UTC, clean up (998 MB peak, 11 Tasks)

### Fix C2 — R37 Wake-vs-Task IPC-Separation
**Status:** ✅ live
**File:** `/home/piet/.openclaw/scripts/auto-pickup.py` `trigger_worker()`
**Change:** Prompt erweitert um `REAL_TASK=true TASK_ID=<id>` Marker + agent=='main' bekommt `ORCHESTRATOR_MODE=true. This is NOT a heartbeat. ...`
**Backup:** `auto-pickup.py.bak-2026-04-19-r37`
**Impact:** Atlas kann Auto-Pickup-Trigger nicht mehr als Heartbeat klassifizieren.

### Fix Bonus — Worker-Monitor Gateway-Healthcheck
**Status:** ✅ live
**File:** `worker-monitor.py` Line 2039
**Change:** `/api/health` -> `/healthz` (Gateway returns 200 auf /healthz, 404 auf /api/health)
**Impact:** Worker-Monitor kann jetzt Atlas-Notify bei Stalled-Tasks triggern (vorher skipped wegen 404).

### Fix R38 — MCP-Zombie-Preventive-Cron (Defense-in-depth)
**Status:** ✅ live, Cron aktiv
**File:** `/home/piet/.openclaw/scripts/mcp-zombie-preventive.sh` (NEW)
**Cron:** `*/15 * * * *` — alle 15min
**Logic:**
- mcp-taskboard-count >= 8 (SOFT_LIMIT) -> Discord-Alert
- mcp-taskboard-count >= 12 (HARD_LIMIT) -> Kill 5 oldest zombies + Alert
**Impact:** Defense-in-depth fuer R30. Falls PR #68846 edge-cases hat, Cron faengt sie ab bevor Gateway-OOM.

## State After Fixes (12:10 UTC)

- MC: active, 200 OK
- Gateway: active, RSS 797 MB (vs 4.3 GB Peak pre-fix)
- MCP-Taskboard-Count: 1 (clean baseline post-restart)
- RAM: 11 GB available
- Board: 3 open tasks (organic flow)

## Active Crons (post-session)

| Cron | Frequency | Purpose |
|---|---|---|
| auto-pickup.py | * * * * * | Task-Dispatch |
| mc-watchdog.sh | */2 * * * * | MC-Service-Recovery |
| worker-monitor.py | */5 * * * * | Stall-Detection (NEW: 2/5 min + /healthz) |
| cost-alert | hourly | Cost-Anomaly |
| memory-size-guard | every 6h | MEMORY.md size |
| session-size-alert | */30 * * * * | Atlas-Session size alert (4 MB) |
| **mcp-zombie-preventive** | **NEW** */15 * * * * | **R38 MCP-Zombie-Kill** |

## Backup-Inventar
```
/home/piet/.openclaw/workspace/scripts/worker-monitor.py.bak-2026-04-19-stall-fix
/home/piet/.openclaw/scripts/auto-pickup.py.bak-2026-04-19-r37
/home/piet/.npm-global/lib/node_modules/openclaw/dist/attempt-execution.runtime-xF4aJ1vF.js.bak-2026-04-19-pr68846
/home/piet/.openclaw/patches/PR68846-applied.md
```

## Incident-Class Coverage

| Klasse | Root-Fix | Defense | Status |
|---|---|---|---|
| R30 MCP-Zombies | B1 PR #68846 | R38 Cron | ✅✅ |
| R37 Heartbeat-FP | C2 Markers | — | ✅ |
| Deadlock (Stall) | A2 Threshold | Worker-Monitor Notify-Fix | ✅✅ |
| Atlas-Orphan | — (deferred) | Session-Resume-Pattern (future) | ⏳ C1 |
| R36 Session-Creep | — | session-size-alert bestehend | ⏳ D |

## Offen / Nachgelagert

### Architectural (Tage-Wochen)
- **C1 Atlas-Resilience** — `openclaw agent` ist One-Shot-CLI. Alternativen: Wrapper-daemon-loop, Session-Resume-Hook, oder warten auf PR #68718 (minions-subsystem). Minimum-Wrapper: Atlas-Heartbeat-Cron der lockierte [Atlas-Sprint-*]-Drafts detektiert und resumed.
- **D1/D2 Session-Management** — Session-Hard-Cap + Force-Compact. Brauchen Design-Input weil openclaw CLI-session-Plugin in config disabled ist.
- **E Architectural** — PR #68718 minions Merge-Watching (durable SQLite Job-Queue).

### Rules

Neu vorgeschlagen (einzutragen in feedback_system_rules.md):
- **R38** Pre-emptive MCP-Zombie-Cleanup bei >8/Prozess-Count.
- **R39** Atlas-main braucht Session-Resume-Pattern nach Gateway-Crash.
- **R40** Pack-5-aequivalente Stall-Thresholds sind Kern-Infra und muessen VOR Scale-Run deployed sein.

## Acceptance-Validation

### B2 — passiver Acceptance-Test ueber naechsten Atlas-Run
**Observable-Metriken:**
- MCP-Taskboard-Count: sollte < 8 bleiben bei normaler Last (R38 Cron-Alarm-Threshold)
- Gateway-RSS: sollte < 2 GB bleiben auch bei Multi-Agent-Dispatch
- Stalled-Tasks: Auto-Fail muss binnen 5min passieren, nicht 30min
- Atlas-HEARTBEAT_OK-Responses: sollten auf 0 fallen

**Alert-Kanaele aktiv:**
- Discord-Webhook bei R38 Threshold-Ueberschreitung
- session-size-alert bei Sessions > 4 MB
- memory-size-guard bei MEMORY.md > 80% bootstrap-Limit

## Bottom Line

6 Fixes in ~20min. **3 von 5 Incident-Root-Causes geschlossen** plus ein Gateway-Healthcheck-Bug + Defense-in-depth Cron. System ist ab sofort materiell stabiler gegen den heutigen Incident-Cluster.

Naechste Runde (wenn User will):
- C1 Atlas-Session-Resume-Pattern
- D1 Session-Hard-Cap mit Rotation
- PR #68718 minions Tracking

## Sign-off

Operator (pieter_pan) 2026-04-19 12:10 UTC. Alle Fixes deployed, documented, reversible via Backups.
