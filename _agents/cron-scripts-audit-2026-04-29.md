---
type: audit-report
date: 2026-04-29
status: complete
audit_id: ROUND-3-CRON-SCRIPTS
agents: [cron-hygiene-audit, scripts-automation-audit]
related:
  - "[[stabilization-2026-04-29-full]]"
  - "[[r51-schema-gate]]"
  - "[[operator-actions-2026-04-29]]"
tags: [audit, cron, automation, scripts, hygiene, defense-layers]
---

# Cron + Scripts Audit — Round 3 (2-Agent Parallel)

## TL;DR

Zwei parallele Audit-Agenten haben Cron-Architektur (3 Systeme: POSIX, systemd, openclaw-internal)
und Scripts-Codebase (106 scripts, 75sh+31py) systematisch geprüft. **Routing nach
Round-3-Stagger funktioniert mehrheitlich, aber einige strukturelle Lücken bestehen weiter.**

**Kernfindings:**
- ✅ **R51-Schema-Gate REPAIRED** — Validator wurde gestern um 12:35 deployed, das Wiring war initial
  broken (mtime 12:35 für validator, mtime 10:38 für guard). 12:53 re-deployed → live VALIDATOR_OK
  bestätigt um 12:59 mit echtem CHANGE_DETECTED → VALIDATOR_OK → VALID flow.
- ⚠️ **3 Cron-Systeme parallel** ohne klare Hoheits-Doku — POSIX-crontab (51 jobs), systemd-timers
  (14 m7-* + andere), openclaw-internal jobs.json (25 jobs). Doku in MEMORY.md überholt.
- ⚠️ **7 von 13 critical scripts haben null/empty docstrings** — bei Incident schwer zu
  diagnostizieren (auto-pickup.py, openclaw-config-guard.sh, mc-critical-alert.py, r49-claim-validator.py,
  cost-alert-dispatcher.py, session-size-guard.py, openclaw-config-validator.py [NEW]).
- ⚠️ **9 cron-entries ohne flock** — lock-stampede-Risk bei Verzögerungen.
- ⚠️ **221 .bak files / 112MB Backup-Bloat** — mostly >30d, cleanup-Kandidaten.
- ⚠️ **exec.allowlist Schema** — schreibbar nur via CLI/API, nicht via Datei (runtime clobber-protection).
- ✅ **0 hardcoded API-Secrets** in Scripts.
- ✅ **R51 fängt jetzt schema-violations** (size-shrink, agent-list, slug-format, spark-codex, openrouter-auto-last).

---

## Cron-Inventory (3 Systeme)

| System | Count | Quelle | Health |
|---|---|---|---|
| **POSIX crontab** | 51 active jobs | `/var/spool/cron/crontabs/piet` | Restored 11:23 + Re-staggered 12:31 |
| **systemd-Timers (User)** | 14 enabled (m7-* + canary-*) | `~/.config/systemd/user/*.timer` | All passing <2min |
| **openclaw-internal jobs.json** | 25 jobs | `/home/piet/.openclaw/cron/jobs.json` | All `last_run=null` (persistence-bug) |

Total unique: ~90 Jobs verteilt auf 3 Engines.

### Doppelregistrierungen
- ✅ `auto-pickup` ist nur in System B (m7-auto-pickup.timer)
- ✅ `mc-watchdog` ist nur in System B
- ⚠️ `m7-atlas-master-heartbeat` ist in **jobs.json**, NICHT als systemd-timer (MEMORY.md falsch)

### Stampede post-Stagger-Fix
- 9 jobs `*/5` jetzt auf 5 Buckets verteilt (offset 0/1/2/3/4)
- Verbleibend: 4 jobs `* * * * *` (unstaggerbar — every minute)
- 13 jobs feuern @minute=0 verschiedener Stunden — unvermeidlich

### Recent Run-Health (last 1h)
- 7 cron-runs in System C, alle `status=ok` (mit Detail-Caveats)
- billing-alert-watch: 3 runs, no 402-hits ✅
- gateway-memory-monitor: 12 runs, rss 2.4-3.4GB <4GB threshold ✅
- atlas-master-heartbeat (a61b4afe): regularly returning `M7_HEARTBEAT_OK touched=1`

### Top 3 Error-Patterns (last 1h)
1. `delivery.channel error: Channel is required` (5/7 sre-expert cron-runs) — Channel-Routing-bug, isolated
2. `atlas-receipt-stream curl-400` mit `status=ok` — exit-code-handling-bug
3. `cc21dba9 Atlas-Reply NO_REPLY` — non-error, recurring

---

## Scripts-Codebase

### Inventory
- **106 scripts** in `/home/piet/.openclaw/scripts/` (75 sh + 31 py)
- ~35 als crontab-target referenziert
- 18 als systemd-target
- ~10 wrappers
- 4 mit Tests, 20 mit `--dry-run`/`DRY_RUN`-Mode

### Documentation Quality (13 critical scripts)

| Script | Header (inline) | Vault-refs | Test/Dry-run |
|---|---|---|---|
| `billing-alert-watch.sh` ⭐ NEW | gut (8+ lines) | 4 | – |
| `openclaw-config-validator.py` ⭐ NEW | mittel (eigentlich gut nach update) | 2 | – |
| `gateway-memory-monitor.py` ⭐ UPDATED | mittel (1 line, expanded with patch-note) | 6 | – |
| `mcp-taskboard-reaper.sh` | gut (8+ lines) | 8 | DRY_RUN |
| `mcp-qmd-reaper.sh` | gut (10+ lines) | 3 | DRY_RUN |
| `auto-pickup.py` | mittel (1 line) | 23 | DRY_RUN + tests |
| `openclaw-config-guard.sh` | **null → R51 update added context** | 6 | – |
| `cost-alert-dispatcher.py` | **null** | 5 | – |
| `mc-critical-alert.py` | **null** | 4 | – |
| `r48-board-hygiene-cron.sh` | gut (8 lines) | 5 | – |
| `r49-claim-validator.py` | **null** | 2 | – |
| `session-size-guard.py` | **null** | 10 | DRY_RUN |
| `cpu-runaway-guard.sh` | gut (6 lines) | 2 | – |

→ **5 von 13 (38%) haben weiterhin null/empty inline docs**. R49-Validator + cost-alert-dispatcher
+ mc-critical-alert sind kritischer Defense-Stack — undocumented.

### Orphan/Dead Scripts
~23 Kandidaten: `chaos-gateway-oom-test.sh`, `streamable-http-soak.sh`, `soak-monitor.sh`,
`pipeline-ui-phase-monitor.sh`, `m7-systemd-migration-rollback.sh`, `claude-design-tunnel-start.sh`,
`google-calendar.py`, `workspace-backup.py`, `mcp-zombie-killer.sh` (Vorgänger von
mcp-taskboard-reaper).

### Backup-Bloat
- **221 files / 112.36 MB** total
- Top-old (>30d): `tasks.validation.backup.json` (Mar 31), 7× openclaw.json.backup-* (Apr 11-16),
  4× worker-monitor.py.bak* (~270KB each), 2× sessions/*.jsonl.bak (>4MB each)
- **Cleanup-Empfehlung:** `find /home/piet/.openclaw -mtime +30 -name "*.bak*" -delete` würde ~80MB freisetzen

### Security/Secrets
- **0 hardcoded API-Keys** in scripts/ (sk-ant, sk-or, AIza, ya29 — keine matches)
- **0 Discord-Webhooks** hardcoded (alle via env-var)
- 1× hardcoded webhook-URL in **crontab** (AUTO_PICKUP_WEBHOOK_URL als env) — sollte rotiert werden

### Hygiene-Issues
- **9 cron-entries ohne flock**: memory-budget-meter, sprint-debrief-watch, r49-claim-validator,
  r48-board-hygiene-cron, cleanup, cron-health-audit, qmd-native-embed-cron,
  vault-search-daily-checkpoint, daily-ops-digest
- **21 sh-Scripts mit `set -e` aber ohne trap/cleanup**
- **73 von 75 sh-Scripts** haben hardcoded `/home/piet/`-paths (kein `$HOME`) — nicht portabel
- **13 von 51 Crons** schreiben nach `/tmp/*.log` (volatile, lost on reboot)

---

## Schwachstellen Priorisiert

### P0
1. **R51-Wiring-Bug** — initial deployment failed silently (mtime mismatch). FIXED 12:53 → live tested 12:59 ✅
2. **5 critical Scripts ohne docstring** — `auto-pickup.py`, `mc-critical-alert.py`, `r49-claim-validator.py`,
   `cost-alert-dispatcher.py`, `session-size-guard.py` (R49+R48 kritischer Defense-Stack)

### P1
3. **9 cron-entries ohne flock** — Stampede-Risk (z.B. memory-budget-meter)
4. **`m7-atlas-master-heartbeat` MEMORY.md falsch dokumentiert** (sagt timer, real ist jobs.json-Job)
5. **`sprint-debrief-watch.log` 0 bytes seit 19.04.** — 9d stille Cron, untersuchen
6. **jobs.json `last_run=null`** für ALLE 25 jobs — Persistence-Bug
7. **13 Crons loggen nach /tmp/** — volatile, lost-on-reboot
8. **Schema-Gates fehlen** für `crontab`, `jobs.json`, vault-frontmatter (R51 nur openclaw.json)

### P2
9. **221 .bak files / 112 MB Backup-Bloat** — Cleanup-Sprint nötig
10. **23 Orphan-Scripts** ohne aktiven Caller — archive vs. delete
11. **delivery.channel-Routing für sre-expert Cron** broken (Channel ambiguity)
12. **`atlas-receipt-stream-subscribe` jede Minute** mit ~38s avg duration

---

## Empfehlungen — neue Sprint-Items

### Sprint-DOC (Documentation Hardening)
- Header-Comments füllen für 5 critical scripts (Template: Purpose / Schedule / Failure-modes / Dependencies)
- Vault-Operator-Doc für `openclaw-config-validator.py` (R51-Implementation)

### Sprint-CRON-HYGIENE
- flock zu 9 cron-entries hinzufügen
- Tier-2 Log-Migration (`/tmp/*.log` → `/home/piet/.openclaw/workspace/logs/`)
- jobs.json `last_run`-Persistence-Bug fixen
- sprint-debrief-watch debug

### Sprint-SCHEMA-GATE-EXPANSION (R52 candidate)
- Pre-write diff-check für crontab (catch wipe-events analog zu R51)
- Schema-Gate für jobs.json
- vault-frontmatter validation

### Sprint-CLEANUP
- .bak files >30d delete (~80MB free)
- 23 orphan scripts triagieren (archive/delete/document)
- delivery.channel-Routing fix für sre-expert-Crons

### Sprint-SECURITY
- AUTO_PICKUP_WEBHOOK_URL aus crontab → .env
- $HOME-Substitution in 73 sh-Scripts (Portabilität)

---

## Was sauber läuft ✅

1. **systemd-Timer m7-* alle aktiv und feuern <2min ago** — verifiziert via `list-timers`
2. **Memory-Orchestrator architecturally sauber** — 4 crontab-Tiers (hourly/nightly/weekly/quarterly)
   dispatchen 5 Memory-Layer (kb-compiler, graph-edge-builder, retrieval-feedback, importance-recalc,
   dashboard) einheitlich. KEINE Stampede, KEIN duplicated entry.
3. **Keine fehlenden Skripte** in Crontab — alle 39 referenzierten Files existieren auf disk
4. **0 Discord/API-Secrets** im Script-Repo — sauber
5. **Tests + DRY_RUN-Mode** für die wichtigsten Reaper/Janitor-Skripte
6. **Vault-Doc-Coverage 100%** für die 13 Critical Scripts (jeder hat ≥2 vault refs)
7. **R51 Schema-Gate aktiv** und im 12:59 cron-run live tested
8. **Crontab Re-Stagger** funktioniert — 9 jobs `*/5` jetzt auf 5 minute-buckets verteilt

---

## Cross-Reference

- Full incident: [[stabilization-2026-04-29-full]]
- R51 details: [[r51-schema-gate]]
- Operator-actions: [[operator-actions-2026-04-29]]
- Daily entry: [[daily/2026-04-29]]
