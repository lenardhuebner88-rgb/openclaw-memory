---
type: audit-report
date: 2026-04-29
status: complete
audit_id: ROUND-5-PER-JOB-WALKTHROUGH
tags: [audit, cron, per-job, system-connections, minimal-fixes]
related:
  - "[[cron-decision-matrix-2026-04-29]]"
  - "[[sprint-closure-2026-04-29-schema-gate-ops]]"
---

# Per-Job Cron Walkthrough — 2026-04-29 ~14:35 UTC

## Methodology

Per-job deep-dive across all 50 active crontab entries:
- **Schedule** + **Script** + **Lock-file**
- **Connections:** what does it call? What depends on it?
- **Recent activity:** log mtime, size, content
- **Value-class:** KEEP_OPTIMAL / KEEP_OK / KEEP_NO_LOG / KEEP_INFREQUENT / KEEP_SILENT / REVIEW

## Summary

| Class | Count | Description |
|---|---|---|
| **KEEP_OPTIMAL** | 20 | Active recently with substantial output |
| **KEEP_NO_LOG** | 16 | No log redirect — output via own log path or by-design silent (intentional) |
| **KEEP_OK** | 7 | Running but with edge characteristics (silent-when-no-issue) |
| **KEEP_INFREQUENT** | 5 | Daily/weekly schedule, log appropriately old |
| **KEEP_SILENT** | 1 | R52 by-design quiet (no-change-no-output) |
| **REVIEW** | 1 | state-collector (resolved: writes JSON, log empty by-design) |
| **DELETE** | 0 | none |
| **MIGRATE** | 0 | none |
| **Total** | 50 | |

## System-Connection Map (Key Hubs)

### `alert-dispatcher.sh` — Discord Alert Hub
**Called by:** mc-critical-alert, gateway-memory-monitor, R52 crontab-schema-gate, R51 config-guard, billing-alert-watch, atlas-orphan-detect, mcp-reapers, session-health-monitor, r48-board-hygiene, r49-claim-validator, R53 vault-frontmatter, cpu-runaway-guard
**Schedule:** *Plus* `0 */6` canary (heartbeat verification)
**Verdict:** ⭐ Critical hub — many one-way dependencies

### `memory-orchestrator.py` — Memory DAG
**Calls:** kb-compiler → graph-edge-builder → memory-dashboard-generator → retrieval-feedback-loop → kb-compiler-llm-synth → daily-reflection-cron → importance-recalc → memory-layer-sweep → sqlite-vacuum
**Schedules:** hourly (30 *), nightly (45 2), weekly (0 5 * * 0), quarterly (0 4 1 */3)
**Verdict:** ⭐ Single entry-point, no duplicates, clean DAG

### Worker System
- `auto-pickup` (systemd-timer m7-auto-pickup) — spawns workers
- `session-size-guard.py` — enforces budgets, optionally rotates workers (feature-flagged)
- `session-rotation-watchdog.py` — monitors active rotation
- `mcp-taskboard-reaper` + `mcp-qmd-reaper` — clean orphan MCP children
- `atlas-orphan-detect.sh` — detects orphan Atlas processes
- `cpu-runaway-guard.sh` — kills runaway CPU consumers

**Verdict:** Well-coordinated, no overlap

### Schema-Gates (R51/R52/R53)
- **R51** openclaw-config-guard.sh + openclaw-config-validator.py — every minute
- **R52** crontab-schema-gate.sh — every minute (added today)
- **R53** vault-frontmatter-validator.py — every 6h (added today)

**Verdict:** Three-layer defense-in-depth against config-drift

## Per-Job Value Map

(Full 50-job breakdown in [[cron-deep-dive-output-2026-04-29.txt]] — saved separately)

### Tier 1: Heartbeat (Every Minute, 5 jobs)
- ✅ inline curl `mc-heartbeat-main` — by-design no-log (POST /api/heartbeat/main)
- ✅ openclaw-config-guard.sh (R51) — silent-when-no-change (size=0 OK)
- ✅ session-size-guard.py --log-only — immediate alert mode
- ✅ state-collector.py — writes JSON to /vault/00-State/live-state.json (33KB fresh)
- ✅ crontab-schema-gate.sh (R52) — silent-when-no-change

**Optimizations applied:** state-collector.py log redirect to /dev/null (was creating 0-byte file in workspace/logs)

### Tier 2: Resource Monitors (Various 5-30min, 8 jobs)
- ✅ All 8 active and reporting correctly
- ✅ gateway-memory-monitor.py: rss 2.4-3.4GB (well below 4GB threshold)
- ✅ session-size-guard.py (full): 1.16MB log of session-size events
- ✅ session-rotation-watchdog.py: active monitoring

### Tier 3: Reapers (Every 5min, 3 jobs)
- ✅ mcp-taskboard-reaper.sh — internal log path, output goes there not stdout
- ✅ mcp-qmd-reaper.sh — same pattern
- ✅ cleanup.sh (daily) — by-design silent

### Tier 4: Alert Pipeline (5 jobs)
- ✅ cost-alert-dispatcher.py: 2.5MB log (heavy traffic, anomaly-tracking working)
- ✅ mc-critical-alert.py: 240h silent log = system has been healthy (CORRECT — only logs on CRITICAL)
- ✅ billing-alert-watch.sh: 3h silent = no 402 hits (CORRECT)
- ✅ session-size-alert.sh, alert-dispatcher.sh canary

### Tier 5: Memory & Knowledge (5 jobs)
- ✅ memory-orchestrator.py 4 schedules — alle correctly running
- ✅ vault-search-daily-checkpoint.sh: 30h ago = yesterday 8AM (daily, CORRECT)

### Tier 6: Validators & Governance (6 jobs)
- ✅ self-optimizer.py (DRY_RUN): 377KB log, optimization signals captured
- ✅ r49-claim-validator.py: 365 bytes / 12min (recent activity)
- ✅ r48-board-hygiene-cron.sh: 81 bytes / 30min (recent activity)
- ✅ mc-ops-monitor.sh, rules-render.sh, sprint-debrief-watch.sh

### Tier 7: Health & Detection (5 jobs)
- ✅ atlas-orphan-detect.sh: 135KB log (active alerts captured)
- ✅ session-health-monitor.py: 13MB log (largest log — high-traffic monitoring)
- ✅ cron-health-audit.sh, session-janitor.py, script-integrity-check.sh

### Tier 8: Snapshots & Hooks (4 jobs)
- ✅ config-snapshot-to-vault.sh (daily 0 3) — by-design silent
- ✅ build-artifact-cleanup.sh (weekly 0 3 * * 0): 83.5h ago = last Sunday (CORRECT)
- ✅ openclaw sessions cleanup (every 6h)
- ✅ architecture-snapshot-generator.py (every 30min)

### Tier 9: Quality & Misc (5 jobs)
- ✅ qmd-pending-monitor.sh, qmd-native-embed-cron.sh, qmd update (daily)
- ✅ pr68846-patch-check.sh, minions-pr-watch.sh

### Tier 10: Reporting (3 jobs)
- ✅ per-tool-byte-meter.py: 1.2KB log (recent metrics)
- ✅ daily-ops-digest.py (21:05 daily) — by-design silent until evening
- ✅ R53 vault-frontmatter-validator.py (every 6h, just added)

## Minimal Optimizations Applied (Today, 2026-04-29 14:34 UTC)

### 1. state-collector.py — Log Cleanup
**Pre:** `* * * * * ... >> /home/piet/.openclaw/workspace/logs/state-collector.log 2>&1`
**Post:** `* * * * * ... >/dev/null`
**Reason:** Script writes its real output as JSON to `/vault/00-State/live-state.json` (33KB fresh, mtime now). Stdout is by-design empty. The 0-byte log was just clutter in workspace/logs.
**Risk:** None. Logging behavior unchanged for actual file output.

### 2. cron-runs-tracker.py — Schedule Tuning
**Pre:** `*/5 * * * *` (every 5min)
**Post:** `*/15 * * * *` (every 15min)
**Reason:** Tracker is just an aggregation tool that reads run-files. Sub-15min freshness not needed for monitoring. Saves ~10 process-spawns/h.
**Risk:** None. Aggregation lag now 15min worst-case (was 5min).

### 3. Cleanup
- Deleted empty `/home/piet/.openclaw/workspace/logs/state-collector.log`

## R52 Verification — Production-Test

The optimizations triggered a real R52 cycle. Log evidence:
```
12:34:01 CHANGE_DETECTED old_hash=f79ad62... new_hash=ba0f9e2...
12:34:01   old: bytes=9270 lines=82
12:34:01   new: bytes=9223 lines=82
12:34:01 VALID hash=ba0f9e2ec3c9cec3dda1315d1e35c35f
```
✅ R52 detected the change correctly, evaluated drop% (47/9270 = 0.5%, well below 50% threshold), accepted as VALID, updated last-good. **Production-validated.**

## Why 0 DELETE / 0 MIGRATE

After per-job system-context-aware analysis:
- Every job has a clear purpose in the defense/monitoring pipeline
- No two jobs duplicate function (verified via call-graph analysis)
- All scripts exist + are executable
- Worker-system, alert-system, memory-DAG, schema-gates all have clean separation

The only "redundancy" found: `session-size-guard.py` runs twice (full at `3-59/5` + immediate at `* * * * *`). This is intentional: full check vs immediate ALERT-only. Different lock-files. Different params. **Keep both.**

## State Post-Optimization

```
crontab_active_jobs: 50 (unchanged)
state-collector log: /dev/null (was workspace/logs/, was 0 bytes anyway)
cron-runs-tracker schedule: */15 (was */5)
R52 status: production-validated (just caught real change, accepted VALID)
/api/health: ok, recoveryLoad=0
```

## Cross-Refs

- [[cron-decision-matrix-2026-04-29]] — Round-4 47-jobs KEEP/DELETE/MIGRATE
- [[sprint-closure-2026-04-29-schema-gate-ops]] — R52 deployment
- [[cron-minimal-fixes-2026-04-29]] — Round-4 hygiene fixes
- [[stabilization-2026-04-29-full]] — Day-incident
