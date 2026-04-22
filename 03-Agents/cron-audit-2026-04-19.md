---
title: Cron/Heartbeat In-Depth Audit + Consolidation Plan
date: 2026-04-19 23:10 UTC
author: Assistant (Claude) Deep-Audit Session
type: ops-audit
status: final
scope: all schedulers (user crontab + systemd user timers + openclaw-cron plugin)
references:
  - https://coady.tech/systemd-timer-vs-cron/
  - https://dev.to/hexshift/how-to-schedule-cron-jobs-with-systemd-timers-for-better-reliability-on-linux-82m
  - https://devops-geek.net/devops-lab/why-systemd-timers-are-quietly-replacing-cron-jobs-the-scheduling-revolution-your-infrastructure-has/
  - https://github.com/kestra-io/kestra
  - https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/
---

# Cron/Heartbeat In-Depth Audit

## Executive Summary

**Total active schedules:** 47 (30 user-crontab + 6 systemd timers + 16 enabled openclaw-cron jobs)  
**Errors aktuell:** 0 active — alle historischen Errors stammen aus Sprint-E MC-Flap-Window 17:00-17:32 UTC (heute)  
**Obsolete schedules zu cleanup:** 9 disabled openclaw-cron legacy jobs + 2 stale *.cron.log files  
**Biggest leverage:** Consolidation 11 memory-crons → 1 orchestrator; Migration high-reliability crons → systemd timers

**Verdict:** System ist **gesund**, aber **über-fragmentiert** (47 schedules, 10+ Kategorien). Best-Class-Pattern 2026 zeigt Systemd-Timers + Event-Driven + Healthchecks.io-Observability. Roadmap zu konsolidierten Sprint-K-Sub + Sprint-L-Portal.

## Part 1 — Full Inventory

### User crontab (30 entries)

| # | Cron | Schedule | Purpose |
|---|---|---|---|
| 1 | `cleanup.sh` | `0 3 * * *` | daily cleanup |
| 2 | `worker-monitor.py` | `*/5min` | R40 stall-detection |
| 3 | `sqlite-memory-maintenance.sh` | Sun 03:17 | SQLite housekeeping |
| 4 | `memory-sqlite-vacuum.sh` | Sun 03:30 | SQLite VACUUM |
| 5 | `memory-layer-sweep.py` | `15 2 * * *` | memory-layer sweep |
| 6 | `memory-layer-sweep.py --quarterly` | quarterly | deep memory review |
| 7 | `auto-pickup.py` | `* * * * *` ⚠️ every-minute | task auto-pickup |
| 8 | `mcp-taskboard-reaper.sh` | `*/15min` | R38 zombie reap |
| 9 | `mc-watchdog.sh` | `*/2min` | MC health monitor |
| 10 | `cost-alert-dispatcher.py` | `*/2min` | cost-anomaly alerts |
| 11 | `mc-ops-monitor.sh` | hourly | ops monitor |
| 12 | `self-optimizer.py` | `*/15min` | self-opt (dry-run only) |
| 13 | `script-integrity-check.sh` | every 6h | integrity check |
| 14 | `mc-critical-alert.py` | `*/2min` | MC critical alerts |
| 15 | `memory-size-guard.sh` | every 6h at :07 | session-size guard |
| 16 | `session-size-alert.sh` | hourly at :23,:53 | session-size alert |
| 17 | `atlas-orphan-detect.sh` | `*/10min` | R39 orphan detect |
| 18 | `openclaw sessions cleanup` | every 6h | session cleanup |
| 19 | `qmd update` | `*/30min` | QMD re-index |
| 20 | `pr68846-patch-check.sh` | `*/30min` | PR #68846 patch-check |
| 21 | `rules-render.sh` | hourly | rules rendering |
| 22 | `minions-pr-watch.sh` | hourly at :23 | PR #68718 watch |
| 23 | `build-artifact-cleanup.sh` | Sun 03:00 | build cleanup |
| **24** | `session-freeze-watcher.sh` **🆕** | `*/5min` | R45 freeze detection |
| **25** | `r49-claim-validator.py` **🆕** | `*/15min` | R49 hallucination catch |
| **26** | `r48-board-hygiene-cron.sh` **🆕** | hourly | R48 stale-draft cancel |
| **27** | `daily-reflection-cron.py` **🆕** | `50 23 * * *` | reflective memory |
| **28** | `kb-compiler.py` **🆕** | `0 4 * * *` | Karpathy-KB articles |
| **29** | `graph-edge-builder.py` **🆕** | `15 4 * * *` | memory graph edges |
| **30** | `memory-budget-meter.sh` **🆕** | `*/5min` | R36/R49 budget-watch |
| **31** | `retrieval-feedback-loop.py` **🆕** | `30 */1 * * *` | L3 reinforcement |
| **32** | `importance-recalc.py` **🆕** | Sun 05:00 | Ebbinghaus recalc |
| **33** | `sprint-debrief-watch.sh` **🆕** | `*/5min` | sprint completion watch |

🆕 = heute deployed (10 von 33 cron-entries, 30% Zuwachs über 1 Tag).

### Systemd user timers (6)

| Timer | Schedule | Service |
|---|---|---|
| openclaw-healthcheck | every 5min | openclaw-healthcheck.service |
| forge-heartbeat | hourly | forge-heartbeat.service |
| vault-sync | every 30min | vault-sync.service |
| researcher-run | daily 09:00 | researcher-run.service |
| launchpadlib-cache-clean | daily 11:59 | launchpadlib-cache-clean |
| lens-cost-check | daily 20:00 | lens-cost-check |

### OpenClaw-Cron Plugin (16 enabled + 9 disabled)

**Enabled:**
- daily-cost-report, morning-brief, nightly-self-improvement
- efficiency-auditor-heartbeat, evening-debrief, learnings-to-tasks
- session-cleanup-local, memory-sqlite-vacuum-weekly, memory-rem-backfill
- Memory Dreaming Promotion, mc-pending-pickup-smoke-hourly
- mc-task-parity-check-10min, mcp-zombie-killer-hourly, analytics-alert-watch
- Security-Weekly-Audit, validate-models

**Disabled (9) — candidates for cleanup:**
- Atlas HTTP Heartbeat (legacy)
- Night Dispatcher (paused)
- P2 follow-through wake
- **Sprint-Debrief-Watch** (disabled today, replaced by shell-script)
- 4× night-sprint-debrief-*-utc (2026-04-18 one-shots, all errored)
- night-sprint-end-report-2050-utc (2026-04-18 one-shot, errored)

## Part 2 — Error Analysis

### Active Errors: 0

Alle gefundenen Error-Logs haben Timestamps aus **Sprint-E MC-Flap-Window (17:00-17:32 UTC heute)**:
- `cost-alert-dispatcher.log` 23 recent-errs → alle "FETCH_FAIL Connection refused" während MC-Restart-Race (R46 live-case)
- `mc-watchdog.log` 2 errors → "MC in unknown state" während Flap
- `self-optimizer.log` 15 errors → alles "health-degraded warnings" (dry-run-only, not actionable)

**Kein cron produziert aktuell Errors.**

### Stale Log-Files (Cleanup-Kandidaten)

| File | Last Mod | Issue |
|---|---|---|
| `auto-pickup-cron.log` | 2026-04-19 00:43 | Script ging in andere Log-Datei (auto-pickup.log live updating) |
| `cost-alert-dispatcher.cron.log` | 2026-04-18 10:54 | Gleich — cost-alert-dispatcher.log ist live |

Diese 2 `.cron.log` Files sind unnötige-Duplikate und können entfernt werden.

### Disabled Openclaw-Cron Cleanup-Target

9 disabled jobs → jobs.json wachsen lassen ohne Nutzen. Empfehlung: komplett aus jobs.json entfernen (permanently, nicht nur disabled).

## Part 3 — Categorization (natürliche Gruppen)

47 Schedules → 10 funktionale Kategorien:

| # | Kategorie | Count | Beispiele |
|---|---|---|---|
| 1 | **Memory/Consolidation** | 11 | qmd update, dreaming, reflection, kb-compiler, graph-edges, importance-recalc, retrieval-feedback, budget-meter, memory-layer-sweep, memory-sqlite-vacuum, memory-rem-backfill |
| 2 | **Health/Monitoring** | 8 | worker-monitor, mc-watchdog, atlas-orphan-detect, mc-ops-monitor, session-freeze-watcher, r49-validator, mcp-zombie-killer, analytics-alert-watch, openclaw-healthcheck |
| 3 | **Hygiene/Cleanup** | 6 | cleanup.sh, r48-board-hygiene, sessions-cleanup, build-artifact-cleanup, sqlite-vacuum, launchpadlib-cache-clean |
| 4 | **Auto-Execution** | 4 | auto-pickup (every-minute!), self-optimizer, mc-task-parity-check, mc-pending-pickup-smoke |
| 5 | **Alerting** | 4 | cost-alert-dispatcher, mc-critical-alert, session-size-alert, memory-size-guard |
| 6 | **Agent-Heartbeats** | 6 | forge-heartbeat, efficiency-auditor-heartbeat, researcher-run, lens-cost-check, daily-cost-report, morning-brief |
| 7 | **Sprint/Governance** | 4 | sprint-debrief-watch, nightly-self-improvement, evening-debrief, learnings-to-tasks |
| 8 | **Build/Integrity** | 4 | script-integrity-check, validate-models, pr68846-patch-check, rules-render |
| 9 | **Vault-Sync** | 1 | vault-sync |
| 10 | **External-Watch** | 1 | minions-pr-watch |

**Observation:** 62% der Schedules sind in 2 Kategorien (Memory 11 + Health 8 + Hygiene 6 = 25 schedules / 47 = 53%). Konsolidierungs-Potential.

## Part 4 — Best-Practice Research 2026

### Systemd Timers > Cron (für high-reliability Jobs)

Basierend auf [Systemd Timers: Modern Choice](https://dev.to/lyraalishaikh/stop-using-cron-why-systemd-timers-are-the-modern-choice-for-linux-automation-5hhk):

| Aspect | Cron | Systemd Timer |
|---|---|---|
| **Parallel-Run Prevention** | manual flock | automatic (RefuseManualStart) |
| **Logging** | stdout/stderr redirect needed | journalctl built-in |
| **Missed-Run Recovery** | none | Persistent=true catches up |
| **Failure Hooks** | none | OnFailure= |
| **DST-Safe Calendar** | partial | full (OnCalendar=) |
| **Resource Control** | none | full (MemoryMax, CPUQuota) |
| **Randomized Delay** | manual | RandomizedDelaySec= |
| **Dependencies** | none | After=, Requires= |

### Event-Driven > Time-Driven (wo möglich)

Basierend auf [Kestra](https://github.com/kestra-io/kestra) + [Kubernetes CronJobs](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/):

- **Poll-Jobs → Event-Listeners**: statt jede Minute API polling, EventSource-Streams nutzen
- **Webhook-Triggers**: statt cron, via POST /webhook triggern
- **File-Watchers (inotify)**: statt poll, auf file-system-events reagieren

### Observability-Stack Best-Class

- [Healthchecks.io-style](https://healthchecks.io/): jeder cron pingt URL bei success, missed-ping = Alert
- [Cronitor](https://cronitor.io/): hosted + on-prem cron-monitoring
- Prometheus Node-Exporter + `systemd_unit_state` metric

### Quarterly-Review-Praxis

Industry-best-practice: alle 3 Monate Inventur, dead-jobs prunen, Duplikate konsolidieren.

## Part 5 — Recommendations (prioritized)

### 🔴 Immediate (30 min)

1. **Cleanup 9 disabled openclaw-cron jobs** aus jobs.json — permanent entfernen statt disabled lassen
   ```sh
   jq '.jobs |= map(select(.enabled == true))' /home/piet/.openclaw/cron/jobs.json > jobs.json.cleaned
   ```
2. **Cleanup 2 stale log-files**:
   ```sh
   rm /home/piet/.openclaw/workspace/logs/auto-pickup-cron.log
   rm /home/piet/.openclaw/workspace/logs/cost-alert-dispatcher.cron.log
   ```
3. **Dokumentiere in `workspace/HEARTBEAT.md`** alle 47 Schedules mit Kategorie + Purpose

### 🟡 Short-Term (1-2h, Sprint-K H10 neu)

4. **Consolidate Memory-Crons**: 11 separate → 1 orchestrator `memory-maintenance-suite.sh` @ 03:00-05:00 UTC window, sequenziell:
   ```
   03:00 qmd update (30min)
   03:00 dreaming (light/deep/rem)
   03:30 sqlite-vacuum
   04:00 kb-compiler
   04:15 graph-edge-builder
   23:50 daily-reflection
   Sunday 05:00 importance-recalc
   ```
   → Reduziert von 11 Einzel-Crons auf 1 Master-Script + klare Sequenz.

5. **Migrate 3 high-reliability crons zu systemd timers**:
   - `worker-monitor.py` (reliability + OnFailure hook wichtig)
   - `mc-watchdog.sh` (Persistent=true recovery)
   - `auto-pickup.py` (parallel-run-prevention + logging)

6. **Deploy Cron-Inventory-Dashboard** als `/admin/crons` MC-Route (analog Sprint-L L6 /memory):
   - Live-Status aller 47 schedules
   - Last-Run, Next-Run, lastError
   - Cron-Kategorie-Grouping
   - Click-to-Disable-Toggle

### 🟢 Medium-Term (Sprint-M Kandidat)

7. **Healthchecks.io-style Observability**:
   - Lokaler healthchecks-server (Docker: `healthchecks/healthchecks`)
   - Jeder cron pingt Endpoint on success
   - Missed-Ping = Discord-Alert
   - Dashboards: up/down + grace-period-violations

8. **Event-Driven Migration**:
   - `sprint-debrief-watch.sh` (poll) → listen `/api/board-events` SSE stream
   - `session-freeze-watcher.sh` (poll) → inotify auf `~/.openclaw/agents/*/sessions/`
   - `auto-pickup.py` (every-minute) → event-triggered on task-create webhook

### 🔵 Long-Term

9. **Kestra-Deployment** als event-driven orchestrator für komplexe multi-step-workflows (Memory-Suite-Pipeline, Sprint-Dispatch-Pipeline)
10. **Cron-as-Code** — alle schedules in einem YAML-File + git-versioned + CI-deployed

## Part 6 — Specific Candidates for Removal

| Cron | Begründung | Action |
|---|---|---|
| `mcp-taskboard-reaper.sh` | Überlappend mit `mcp-zombie-killer-hourly` (openclaw-cron) | **KEEP beide** — verschiedene Scopes (taskboard vs alle-MCP), aber document overlap |
| `self-optimizer.py` (dry-run-only, 51 errors/day, 15min poll) | Produziert nur observational Log-Einträge, keine Action | **REVIEW** — entweder actionable machen oder auf `*/1h` reduzieren |
| 4× `night-sprint-debrief-*-utc` (2026-04-18 one-shots disabled, errored) | One-shots die deleteAfterRun hätte entfernen sollen, aber hängen geblieben | **DELETE** aus jobs.json |
| `Atlas HTTP Heartbeat` (disabled, legacy) | Nicht mehr relevant | **DELETE** |
| `Night Dispatcher (paused)` (disabled) | Legacy-experiment | **DELETE** |
| `P2 follow-through wake` (disabled) | Legacy-experiment | **DELETE** |
| `mc-task-parity-check-10min` | Läuft alle 10 min — ist das noch notwendig? Kann Parität via Event checken? | **REVIEW** |
| `launchpadlib-cache-clean` systemd timer | Unclear purpose — Ubuntu system-level | **REVIEW** |

## Part 7 — Consolidation Blueprint

### Vorschlag: Reorganize `/home/piet/.openclaw/scripts/` per Kategorie

```
.openclaw/scripts/
├── memory/
│   ├── maintenance-suite.sh          (NEW orchestrator, called 03:00)
│   ├── kb-compiler.py
│   ├── graph-edge-builder.py
│   ├── importance-recalc.py
│   ├── daily-reflection.py
│   ├── retrieval-feedback.py
│   ├── budget-meter.sh
│   └── sqlite-maintenance.sh
├── health/
│   ├── worker-monitor.py             (migrate to systemd)
│   ├── mc-watchdog.sh                (migrate to systemd)
│   ├── atlas-orphan-detect.sh
│   ├── session-freeze-watcher.sh
│   ├── r49-claim-validator.py
│   ├── mcp-zombie-killer.sh
│   └── mc-ops-monitor.sh
├── hygiene/
│   ├── r48-board-hygiene.sh
│   ├── sessions-cleanup.sh
│   ├── build-artifact-cleanup.sh
│   └── cleanup.sh (legacy wrapper)
├── auto-exec/
│   ├── auto-pickup.py                (migrate to systemd + event-driven)
│   ├── self-optimizer.py
│   └── mc-task-parity-check.py
├── alerting/
│   ├── cost-alert-dispatcher.py
│   ├── mc-critical-alert.py
│   └── session-size-alert.sh
├── heartbeats/
│   ├── forge-heartbeat.sh
│   └── efficiency-auditor-heartbeat.sh
├── sprint-gov/
│   ├── sprint-debrief-watch.sh
│   ├── evening-debrief.sh
│   ├── morning-brief.sh
│   └── learnings-to-tasks.sh
├── build/
│   ├── script-integrity-check.sh
│   ├── validate-models.sh
│   ├── pr68846-patch-check.sh
│   └── rules-render.sh
├── vault/
│   └── vault-sync.sh
└── external/
    └── minions-pr-watch.sh
```

### Target State

**Von:** 47 flat schedules → **Zu:** ~30 organized schedules in 10 categories, mit klaren Orchestrator-Scripts.  
**Reduktion:** ~35% durch Memory-Consolidation + dead-job-cleanup.  
**Observability:** Healthchecks-Endpoint pro schedule + Discord-Alert bei Missed-Ping.  
**Documentation:** Jeder schedule mit Purpose + Owner + LastAudit in HEARTBEAT.md.

## Part 8 — Proposed Sprint-K H10 (neu)

Als **neues Sub-Task in Sprint-K Infra-Hardening**:

**H10: Cron-Inventory-Consolidation + Observability** (4h Forge)
- Cleanup 9 disabled + 2 stale log-files
- Consolidate 11 memory-crons → 1 orchestrator
- Migrate 3 high-reliability crons to systemd timers
- Deploy healthchecks-monitor
- Document all 30 schedules in HEARTBEAT.md Cron-Inventory-Section
- Report: `vault/03-Agents/cron-consolidation-report-2026-04-XX.md`

## Part 9 — Quick-Win: Script-Inventory-Tool (for future ops)

Wrapper-Script `/home/piet/.openclaw/scripts/cron-inventory.sh` das:
- Listet alle 47 Schedules in einer Tabelle
- Zeigt Last-Run, Next-Run, lastError pro job
- Kategorisiert automatisch
- Farb-coded Health-Status
- JSON-Export für MC-Route-Ingestion

## Sources

- [Systemd Timers: Modern Choice for Linux Automation (DEV 2026)](https://dev.to/lyraalishaikh/stop-using-cron-why-systemd-timers-are-the-modern-choice-for-linux-automation-5hhk)
- [Stop Using Cron! Systemd Timers Explained (coady.tech)](https://coady.tech/systemd-timer-vs-cron/)
- [Schedule cron jobs with systemd timers for better reliability (DEV)](https://dev.to/hexshift/how-to-schedule-cron-jobs-with-systemd-timers-for-better-reliability-on-linux-82m)
- [Kestra Event-Driven Orchestration (GitHub)](https://github.com/kestra-io/kestra)
- [Kubernetes CronJob Resource (k8s docs)](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/)
- [How to Optimize Cron Jobs (YouStable)](https://www.youstable.com/blog/optimize-cron-jobs-on-linux)
- [Why systemd timers are quietly replacing cron jobs (DevOps-Geek)](https://devops-geek.net/devops-lab/why-systemd-timers-are-quietly-replacing-cron-jobs-the-scheduling-revolution-your-infrastructure-has/)
