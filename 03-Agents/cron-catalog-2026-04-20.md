---
title: "Cron Catalog 2026-04-20 (Sprint-K H10)"
date: 2026-04-20
status: ACTIVE
scope: Complete inventory of 39 scheduled jobs (+5 env vars) in user-crontab
sprint: K H10 Cron-Consolidation
---

# Cron Catalog — Mission Control / OpenClaw Scheduled Jobs

**Total active crons:** 39
**Total env vars:** 5
**Last audit:** 2026-04-20
**Backup:** `workspace/memory/crontab.bak-pre-h10-20260420`

---

## 📊 Summary by Frequency

| Frequency | Count | Examples |
|---|---|---|
| `* * * * *` (every minute) | 2 | auto-pickup, openclaw-config-guard (R51) |
| `*/2 * * * *` | 3 | mc-watchdog, cost-alert, mc-critical-alert |
| `*/5 * * * *` | 5 | worker-monitor, session-freeze-watcher, memory-budget-meter, sprint-debrief-watch, stale-lock-cleaner |
| `*/10 * * * *` | 2 | atlas-orphan-detect, session-health-monitor (H11) |
| `*/15 * * * *` | 3 | mcp-taskboard-reaper, self-optimizer, r49-claim-validator |
| `*/30 * * * *` | 2 | qmd-update, pr68846-patch-check |
| `0 * * * *` (hourly) | 3 | mc-ops-monitor, rules-render, r48-board-hygiene |
| `30 */1 * * *` | 1 | retrieval-feedback-loop |
| `23 * * * *` | 1 | minions-pr-watch |
| `23,53 * * * *` | 1 | session-size-alert (twice per hour) |
| Daily | 8 | cleanup, kb-compiler, graph-edge-builder, memory-dashboard-generator, kb-compiler-llm-synth, daily-reflection, memory-layer-sweep, config-snapshot-to-vault (R53) |
| Every 6h | 3 | script-integrity-check, openclaw sessions cleanup, mc-memory-guard |
| Weekly (Sun) | 4 | build-artifact-cleanup, sqlite-memory-maintenance, memory-sqlite-vacuum, importance-recalc |
| Quarterly | 1 | memory-layer-quarterly |

---

## 🛡️ Defense Crons (14 — governance + alerting + recovery)

### Heartbeat Monitors (realtime)
| Schedule | Script | Log | Purpose | Source |
|---|---|---|---|---|
| `* * * * *` | auto-pickup.py | `logs/auto-pickup-cron.log` | Pickup pending-pickup tasks via native-messaging | Sprint-A |
| `* * * * *` | openclaw-config-guard.sh | `/tmp/config-guard.log` | R51 schema-validate openclaw.json, rollback on invalid | Sprint-K H13 |
| `*/2 * * * *` | mc-watchdog.sh | (discord-only) | MC /api/health probe + alert | Sprint-A |
| `*/2 * * * *` | cost-alert-dispatcher.py | `logs/cost-alert-dispatcher.cron.log` | Cost-anomaly fan-out to Discord | Sprint-K H8 (RATE_LIMIT=21600s after fix) |
| `*/2 * * * *` | mc-critical-alert.py | `logs/mc-critical-alert.cron.log` | Critical MC signal dispatcher | Sprint-J |

### Stall + Lock Detection (5-10 min tier)
| Schedule | Script | Log | Purpose | Source |
|---|---|---|---|---|
| `*/5 * * * *` | worker-monitor.py (flock) | `scripts/worker-monitor.log` | Stall-detection + orphan-recovery (2min warn threshold) | Sprint-A |
| `*/5 * * * *` | session-freeze-watcher.sh | `/tmp/session-freeze-watcher.log` | Detect frozen agent sessions | Sprint-E |
| `*/5 * * * *` | stale-lock-cleaner.sh | `/tmp/stale-lock-cleaner.log` | R50 Ebene 2 — remove orphan .jsonl.lock | Sprint-K H11 |
| `*/10 * * * *` | atlas-orphan-detect.sh | `logs/atlas-orphan-detect-cron.log` | Atlas-main orphaned-session detector | Sprint-F |
| `*/10 * * * *` | session-health-monitor.py (flock) | `logs/session-health-monitor.cron.log` | R50 Ebene 4 — orphan/zombie/ghost/size-exploded session scan | Sprint-K H11 |

### Governance Validators
| Schedule | Script | Log | Purpose | Source |
|---|---|---|---|---|
| `*/15 * * * *` | mcp-taskboard-reaper.sh (flock) | (silent) | R38 MCP-Zombie-Defense kill >3 taskboard-server procs | Sprint-D |
| `*/15 * * * *` | self-optimizer.py (flock, DRY_RUN) | `logs/self-optimizer.log` | Learns patterns, suggests rules | Sprint-E |
| `*/15 * * * *` | r49-claim-validator.py | `/tmp/r49-validator.log` | R49 claim-verify-before-report (Atlas anti-hallucination) | Sprint-H |
| `0 */1 * * *` | r48-board-hygiene-cron.sh | `/tmp/r48-hygiene.log` | R48 auto-cancel stale drafts + archive null-completedAt fails | Sprint-H |

---

## 🧠 Memory Crons (10 — Memory-Levels 1-6)

### L1 Compilation (daily)
| Schedule | Script | Log | Purpose | Source |
|---|---|---|---|---|
| `0 4 * * *` | kb-compiler.py | `/tmp/kb-compiler.log` | Karpathy-style KB article compilation (10 articles) | Sprint-L |
| `30 4 * * *` | kb-compiler-llm-synth.py | `/tmp/kb-synth.log` | L1-Deep: LLM-synthesis via openai-codex/gpt-5.4-mini + grounding | Sprint-L L1-Finalize |
| `15 4 * * *` | graph-edge-builder.py | `/tmp/graph-edge-builder.log` | L2: Build memory-graph edges from facts + rules | Sprint-L L2 |

### L3+ Feedback Loops
| Schedule | Script | Log | Purpose | Source |
|---|---|---|---|---|
| `30 */1 * * *` | retrieval-feedback-loop.py | `/tmp/retrieval-feedback.log` | L3: Track retrieval effectiveness, refine index | Sprint-L L3 |
| `0 5 * * 0` | importance-recalc.py | `/tmp/importance-recalc.log` | Weekly: Ebbinghaus-decay + importance-rescore facts | Sprint-L |

### L5-L6 Observability
| Schedule | Script | Log | Purpose | Source |
|---|---|---|---|---|
| `*/5 * * * *` | memory-budget-meter.sh | `/tmp/memory-budget.log` | L5: Atlas-session-size watchdog (70% warn, 90% CRIT) | Sprint-L |
| `30 4 * * *` | memory-dashboard-generator.py | `/tmp/memory-dashboard.log` | L6-Lite: Daily dashboard regen | Sprint-L |
| `50 23 * * *` | daily-reflection-cron.py | `/tmp/daily-reflection.log` | Daily reflection + fact-distillation | Sprint-K |

### Maintenance (weekly/quarterly)
| Schedule | Script | Log | Purpose | Source |
|---|---|---|---|---|
| `15 2 * * *` | memory-layer-sweep.py (flock) | `logs/memory-layer-sweep.log` | Daily: move working→episodic | Sprint-B |
| `0 4 1 */3 *` | memory-layer-sweep.py --quarterly (flock) | `logs/memory-layer-quarterly.log` | Quarterly: deep-review + archival | Sprint-B |

---

## 🏗️ Ops + Build Crons (8)

### MC Health + Ops Dashboard
| Schedule | Script | Log | Purpose | Source |
|---|---|---|---|---|
| `0 * * * *` | mc-ops-monitor.sh | `logs/mc-ops-monitor.cron.log` | Hourly MC + Gateway health-snapshot | Sprint-G |
| `7 */6 * * *` | memory-size-guard.sh (flock) | (silent) | Session-file-size creep detection | Sprint-K |
| `23,53 * * * *` | session-size-alert.sh (flock) | (silent) | Twice-hourly: session-size alert | Sprint-F |

### Integrity + Security
| Schedule | Script | Log | Purpose | Source |
|---|---|---|---|---|
| `0 */6 * * *` | script-integrity-check.sh (flock) | `logs/script-integrity.log` | R33 cron-script-path-invariance audit | Sprint-D |
| `0 */6 * * *` | openclaw sessions cleanup | `logs/sessions-cleanup-cron.log` | Agent-session consistency enforcement | Sprint-A |

### Rules + QMD + PR
| Schedule | Script | Log | Purpose | Source |
|---|---|---|---|---|
| `0 * * * *` | rules-render.sh (flock) | `logs/rules-render.log` | Regenerate feedback_system_rules.md from rules.jsonl | Sprint-J |
| `*/30 * * * *` | qmd-update (flock) | `logs/qmd-update-cron.log` | QMD memory-index refresh | Sprint-B |
| `*/30 * * * *` | pr68846-patch-check.sh (flock) | (silent) | Monitor PR #68846 patches | (legacy) |
| `23 * * * *` | minions-pr-watch.sh (flock) | (silent) | Monitor minions PRs | (legacy) |

---

## 🗂️ Build + Cleanup Crons (4)

| Schedule | Script | Log | Purpose | Source |
|---|---|---|---|---|
| `0 3 * * *` | cleanup.sh | (silent) | Daily cleanup routine | (legacy) |
| `0 3 * * 0` | build-artifact-cleanup.sh (flock, Sun) | `logs/build-artifact-cleanup.cron.log` | Weekly: remove stale .next-* artifacts | Sprint-F |
| `17 3 * * 0` | sqlite-memory-maintenance.sh (Sun) | (silent) | Weekly: SQLite memory-db maintenance | Sprint-B |
| `30 3 * * 0` | memory-sqlite-vacuum.sh (Sun) | (silent) | Weekly: SQLite VACUUM | Sprint-B |

---

## 📸 Snapshot + Audit Crons (1)

| Schedule | Script | Log | Purpose | Source |
|---|---|---|---|---|
| `0 3 * * *` | config-snapshot-to-vault.sh (flock) | `/tmp/config-snapshot.log` | R53 daily snapshot openclaw.json + scripts/* to vault | Sprint-K H13 |

---

## 🔧 Sprint-Debrief (1)

| Schedule | Script | Log | Purpose | Source |
|---|---|---|---|---|
| `*/5 * * * *` | sprint-debrief-watch.sh | `/tmp/sprint-debrief-watch.log` | Auto-trigger sprint-debrief after completion patterns | Sprint-J |

---

## 🌐 Environment Variables (5)

| Var | Value | Purpose |
|---|---|---|
| `AUTO_PICKUP_ENABLED` | `1` | Master enable for auto-pickup |
| `AUTO_PICKUP_ALERT_CH` | `1491148986109661334` | Discord channel ID for alerts |
| `AUTO_PICKUP_WEBHOOK_URL` | `https://discord.com/api/webhooks/1494679463663898715/...` | Auto-pickup alert webhook |
| `MCP_REAP_CAP` | `3` | Max taskboard-server processes before reaping |
| `MC_WATCHDOG_WEBHOOK_URL` | `https://discord.com/api/webhooks/1494679463663898715/...` | **DUPLICATE** of AUTO_PICKUP_WEBHOOK_URL — same URL |

---

## 🚨 Observed Issues

### Inconsistency 1: Log Path Fragmentation
- `/tmp/*.log` — 18 crons (ephemeral, lost on reboot)
- `logs/*.cron.log` — 11 crons (persistent)
- No logging — 10 crons

**Impact:** Monitoring fragmented. `/tmp/` logs cannot be tailed over reboots. No unified cron-health-audit possible without path-normalization.

**Status:** documented, not fixed yet (would require coordinated crontab + script changes).

### Inconsistency 2: flock Coverage
- Has `flock` guard — 21 crons ✅
- No `flock` — 18 crons ⚠️ (concurrent-run risk if previous instance stalls)

**Impact:** Low — most non-flocked crons are daily (unlikely to overlap).

### Inconsistency 3: Duplicate Webhook Env Var
`AUTO_PICKUP_WEBHOOK_URL` and `MC_WATCHDOG_WEBHOOK_URL` point to same URL. Could consolidate to `DEFENSE_WEBHOOK_URL`. Not fixed (would require coordinated update of all scripts that read either var).

### Clustering at `*/5`
5 crons fire at same minute (0, 5, 10, 15, …). Brief disk-I/O burst every 5min. Not critical but could be staggered in future optimization.

---

## 🛠 Recommendations for Future Sprints

### Sprint-M Candidate: Cron-Infra-v2
1. **Unified log path** — migrate all `/tmp/*.log` to `workspace/logs/cron/`
2. **flock everywhere** — add lock-file guard to remaining 18 non-flocked crons
3. **Single webhook env var** — `DEFENSE_WEBHOOK_URL`
4. **Stagger `*/5` cluster** — offset by minutes to distribute load
5. **cron-health-dashboard** — weekly observability summary

### Sprint-N Candidate: Cron-via-systemd-timers
Consider migration from cron → systemd-timers for:
- Better journal integration (native log-tail)
- Drop-in directory for per-cron modifications
- Cleaner dependency management
- Native retry + backoff

---

## 📝 Recent Additions (last 7 days)

| Date | Cron | Sprint |
|---|---|---|
| 2026-04-20 | config-snapshot-to-vault.sh | K H13 (R53) |
| 2026-04-20 | openclaw-config-guard.sh | K H13 (R51) |
| 2026-04-20 | kb-compiler-llm-synth.py | L L1-Finalize |
| 2026-04-20 | session-health-monitor.py | K H11 (R50 Ebene 4) |
| 2026-04-20 | memory-dashboard-generator.py | L L6-Lite |
| 2026-04-19 | stale-lock-cleaner.sh | K H11 (R50 Ebene 2) |
| 2026-04-19 | r48-board-hygiene-cron.sh | H R48 |
| 2026-04-19 | r49-claim-validator.py | H R49 |
| 2026-04-19 | retrieval-feedback-loop.py | L L3 |
| 2026-04-19 | memory-budget-meter.sh | L L5 |
| 2026-04-19 | kb-compiler.py | L L1 |
| 2026-04-19 | graph-edge-builder.py | L L2 |
| 2026-04-19 | daily-reflection-cron.py | K |
| 2026-04-19 | sprint-debrief-watch.sh | J |

**Growth rate:** ~14 new crons added in last 7 days → complex defense-in-depth stack. H10 Consolidation is timely.

---

*This catalog is auto-verifiable: `crontab -l | grep -vE '^#|^\s*$' | wc -l` should match "Total active crons" count above.*
