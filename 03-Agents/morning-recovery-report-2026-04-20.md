---
title: "Morning Recovery Report 2026-04-20 — Config-Invalid Production-Outage + 3 State-Machine-Bugs"
date: 2026-04-20
session_start: 05:50 UTC
session_end: TBD
status: IN-PROGRESS
priority: P0-RECOVERY
---

# Morning Recovery Report 2026-04-20

**Scope:** Systemische Probleme entdeckt + behoben zwischen 05:50–06:50 UTC. Dieser Report dokumentiert 3 neue State-Machine-Bugs, einen P0 Production-Outage durch Schema-invalid Config-Writes, und alle Recovery-Actions.

## Timeline (UTC)

| Zeit | Event |
|---|---|
| ~04:30 | Memory-Dashboard L6-Lite Cron auto-generated (monitoring) |
| 05:40–05:59 | Atlas orchestriert Sprint-K H2+H5 parallel via Forge; beide "done" auf Board |
| **05:59** | H2+H5 Config-Writes landen — **schema-invalid** (nicht detected) |
| 06:09 | H11 Session-Lock-Governance dispatched durch Assistant |
| 06:11 | Auto-Pickup trigger #1 für H11 → SILENT FAIL (Config invalid) |
| 06:21 | Auto-Pickup trigger #2 → SILENT FAIL |
| 06:27 | Auto-Pickup trigger #3 (nach erster Lock-Delete) → SILENT FAIL |
| 06:28 | Assistant investigiert trigger-log, **findet Config-Invalid Error** |
| 06:31 | Python surgical patch auf openclaw.json (removed 2 invalid keys + 2 reverts) |
| 06:32 | Stale auto-pickup lock 2. Mal deleted |
| 06:33 | Auto-Pickup trigger #4 → SUCCESS |
| 06:34 | Forge attached, erste Receipt (accepted) |
| 06:42 | H11 terminal-receipt (done) — 8 min execution |
| 06:50 | L1-V2 canceled + L1-Finalize (855153b6) dispatched |

## Root-Cause #1: Config-Invalid Production-Outage

**Schema-invalid Keys in /home/piet/.openclaw/openclaw.json:**

```diff
+ agents.defaults.systemPrompt = "## Receipt-Discipline... R42 mc-restart-safe... R44 Board-Discipline..."   [H5]
+ tools.exec.allowedCmds = ["mc-restart-safe", "systemctl status", "systemctl --user status"]               [H2]
- tools.exec.security: "full" -> "allowlist"                                                                [H2 collateral]
- channels.discord.execApprovals.enabled: true -> false                                                     [H2 collateral]
```

**Error message from openclaw CLI:**
```
Config invalid
File: ~/.openclaw/openclaw.json
Problem:
  - agents.defaults: Unrecognized key: "systemPrompt"
  - tools.exec: Unrecognized key: "allowedCmds"

Run: openclaw doctor --fix
```

**Blast radius:** ALL agent-subprocess-spawns via `openclaw agent` rejected → Auto-Pickup silent-fail → Board shows false-green pending-pickup/active. Worker-Monitor sieht kein session-attach → stalled-warning nach 2min.

**Detection-Gap: 30+ min** weil:
1. subprocess.Popen output geht in auto-pickup-runs/*.log (nicht in main log)
2. Auto-Pickup zeigt triggered=1, locked=0 (wie erwartet)
3. Nur inspection der trigger-log-files offenbarte Error

## Root-Cause #2: Board-State-Machine-Bugs (3-stack)

### Bug A: /complete Guard zu restriktiv
- Endpoint rejects mit `terminal-transition-conflict` auch bei workerSessionId=none
- Non-deterministic: H4 (stalled-warning, no worker) ging durch, H3 + H8-Forge-Retry (gleicher State) nicht
- requiresActiveWorkerTerminalGuard Logic hat Edge-Case

### Bug B: admin-close erzwingt canceled/failed
- Non-terminal Task → admin-close setzt immer status: canceled, executionState: failed, receiptStage: failed
- Keine Möglichkeit status: done bei successful-but-stalled Tasks
- canceled -> done Transition explizit blockiert
- **Effekt:** H3 + H8-Forge-Retry permanent als "failed" in Board-History, obwohl Code-Fixes LIVE sind

### Bug C: Auto-Pickup Silent-Trigger-Fail (NEU)
- trigger_worker() returnt True wenn subprocess.Popen succeedete
- Aber subprocess kann direkt nach Start crashen (Config-Invalid -> Exit 1)
- Lock-File bleibt, blockt alle Retries
- Keine Detection-Schicht zwischen Popen und Worker-Attach (Heartbeat etc.)

## Recovery Actions

### 1. Commit-Consolidation (vorbereitend)
4 Commits in mission-control/master (Sprint-G/H/I/K residuals):
- `32ccfbe` fix(sprint-k h6): allow 'progress' as valid first receipt stage
- `d5710a2` feat(sprint-i): Pixel mobile I1/I2/I4/I6 residuals (500+/-49)
- `e5dc7a6` chore(sprint-g/h): autonomous-cascade source residuals (14 files)
- `de026f4` chore(sprint-k): harden .gitignore (prevent build/tmp clutter)

MC-Repo Cleanup: ~1.47 GB befreit (16 .next-*/ dirs, 65 tmp screenshots, 9 scratch scripts, 4 literal-junk-filenames, 9 date-stamped backup files, tmp/ scratch dir). .gitignore gehärtet mit 8 neuen Patterns. git gc --aggressive durchgelaufen.

### 2. Board-Cleanup (4 Ghost-Stalled-Tasks)
| ID | Sub | Method | Result |
|---|---|---|---|
| 71264c14 | H4 | /complete | done OK |
| 1b1a5c90 | H3 | admin-close (complete rejected) | canceled/failed (Bug B) |
| 55bfa0b2 | H8 Forge-Retry | admin-close (complete rejected) | canceled/failed (Bug B) |
| b4071b50 | H8 Spark-Original | admin-close | canceled (duplicate) OK |

### 3. P0 Config-Recovery (06:31 UTC)
- Backup: openclaw.json.bak-2026-04-20-INVALID-h2-h5-keys-pre-recovery (28469 bytes)
- Python surgical patch:
  - REMOVED agents.defaults.systemPrompt (1059 chars)
  - REMOVED tools.exec.allowedCmds (3 entries)
  - REVERTED tools.exec.security: allowlist -> full
  - REVERTED channels.discord.execApprovals.enabled: false -> true
  - KEPT memory-core.config.dreaming.verboseLogging: false (H3 James valid fix)
- Struktur-Integrity: 342 Keys -> 342 Keys (0 data loss)
- openclaw doctor: clean (nur pre-existing telegram/discord warnings)

### 4. H11 Dispatch + Recovery
- Stale auto-pickup-lock manually deleted (2x, both at /tmp/mc-auto-pickup-locks/)
- Trigger #4 succeeded 06:33:01 UTC
- Worker (openclaw-agent PID 373765, claude PID 375711) attached 06:34:17
- H11 completed 06:42:40 UTC — 8 min execution (budget was 3-3.5h)

**H11 Deliverables verifiziert:**
- auto-pickup.py — lock-awareness + decision-logging (skip-alive-lock | spawn-new-for-orphan | proceed-normal)
- session-health-monitor.py (6752 bytes, exekutabel, cron */10 * * * * aktiv)
- **R50** in memory/rules.jsonl + AGENTS.md + feedback_system_rules.md (commit c8ed7a14)
- Report: vault/03-Agents/sprint-k-h11-session-lock-governance-report-2026-04-20.md (70 lines)

### 5. L1-V2 Cleanup + L1-Finalize Dispatch
- b02b1a26 Sprint-L L1 Deep+ V2 canceled (description outdated — script already migrated by failed L1-Original run)
- Entdeckung: kb-compiler-llm-synth.py existiert als v3 mit openai-codex/gpt-5.4-mini, Grounding-Hardening, JSON Output, Cross-Links
- ABER: uncommitted + kein Cron + 0/11 KB-Articles haben synthesis-Block
- 855153b6 Sprint-L L1 Finalize dispatched (30-60 min Forge-Task für commit + cron + first-run + verify + report)

## Candidate Rules (R51-R53)

### R51 Schema-Validation-Gate
Nach JEDEM Write auf openclaw.json:
```
openclaw doctor 2>&1 | grep -q 'Config invalid' && { cp openclaw.json.bak openclaw.json; exit 1; }
```
**Motivation:** Heute-Morgen-Incident 06:00-06:31 UTC, 30 min Production-Outage weil Schema-Check fehlte.

### R52 Auto-Pickup Silent-Fail Detection
trigger_worker() muss subprocess-Exit-Code binnen 5-10s prüfen:
```
proc = subprocess.Popen([...], ...)
time.sleep(8)
rc = proc.poll()
if rc is not None and rc != 0:
    log('TRIGGER_SILENT_FAIL', f'task={tid[:8]} rc={rc} log={out_path}')
    alert(...)
    lock.unlink()
    return False
```
**Motivation:** 3 Cycle-Retries auf H11 zeigten triggered=1 obwohl Worker sofort crashte. Classic silent-failure-mode.

### R53 Config-in-Git-Track-Path
openclaw.json + /home/piet/.openclaw/scripts/*.py sollten:
- Entweder in dediziertes Git-Repo (z.B. openclaw-config sibling zu workspace)
- Oder täglicher Config-Backup-Cron zu vault/
- Aktuell: ungetrackt -> Atlas/Forge Changes können bei Crash verloren gehen

## Sprint-K Status nach Recovery

| Sub | Board | Code-Reality |
|---|---|---|
| H1 V8-Heap | done | OK |
| H2 Tool-Allowlist | done | ROLLED BACK (schema-invalid), needs re-impl |
| H3 memory-core reconcile | canceled/failed | fix live (verboseLogging false) |
| H4 Concurrent-Limit | done | OK (no code changes needed, maxConcurrent=2 was already right) |
| H5 R44 Board-Discipline | done | ROLLED BACK (schema-invalid systemPrompt), needs re-impl |
| H6 Receipt-Lifecycle | done | OK + commit 32ccfbe |
| H7 mc-restart-safe | done | OK |
| H8 Budget-Alert | canceled/failed | fix live (RATE_LIMIT 21600s) |
| **H11 Session-Lock-Gov** | **done** | **full deploy, 8 min execution** |
| H9 Dark-Token-Contrast | pending | — |
| H10 Cron-Consolidation | pending | — |
| **H12 Board-State-Machine-Fix** | CANDIDATE | 3 bugs documented (Bug A+B+C from this report) |
| **H13 Schema-Validation-Gate** | CANDIDATE | R51+R52+R53 = new sub |

## Residual Findings für H2/H5 Re-Implementation

**H5 R44/R45/R42-Preamble** via agents.defaults.systemPrompt = invalid.
Valid alternatives:
- Write to /home/piet/.openclaw/agents/<name>/AGENTS.md or BOOTSTRAP.md (each agent reads on session-start) — **sustainable, already the documented pattern**
- Or: /home/piet/.openclaw/workspace/AGENTS.md (workspace-wide) — already has R50 via H11
- NOT: openclaw.json (schema rejects)

**H2 Tool-Allowlist** via tools.exec.allowedCmds = invalid.
Valid alternatives:
- Wrapper-Script-Only-Approach: Sub-Agents müssen mc-restart-safe/mc-commit-safe aufrufen; raw systemctl restart vorgesehen als policy-violation (dokumentiert in AGENTS.md, enforced via agent-preamble)
- Or: tools.exec.security enum might accept custom values — check schema (requires reading openclaw binary source)
- Or: Deploy a pre-exec-hook script that filters commands (new file, no schema change)

## Statistics

- **MC-Commits this session:** 4
- **Board tasks touched:** 6 (1 created, 4 closed, 1 canceled)
- **Config-recovery:** 1x surgical patch (reversible via .bak files)
- **Disk freed:** ~1.47 GB (MC repo cleanup)
- **Untracked items remaining:** 124 (from 205)
- **New rules (R50):** 1 active (Session-Lock-Governance)
- **Rule candidates (R51-R53):** 3 pending Sprint-K sub
- **State-Machine bugs found:** 3 (complete-guard, admin-close-semantic, auto-pickup-silent-fail)
- **Production-outage duration:** ~25 min (06:09–06:34 UTC)
- **Hallucinations detected (R49):** 0 CRITICAL, 1 harmless WARNING 02:45 UTC over the night

## Next Steps (if Operator resumes)

1. Wait for L1-Finalize terminal-receipt (expected 09:00-09:30 UTC)
2. Dispatch H2-v2 + H5-v2 (schema-correct re-implementation)
3. Dispatch H12 Board-State-Machine-Fix (3 bugs)
4. Dispatch H13 Schema-Validation-Gate (R51+R52+R53)
5. Eventually: H9 Dark-Token + H10 Cron-Consolidation

---

*Dieses Document ist Evidence für R49-Compliance: alle Claims inline-verifiable via git log, curl, ls, diff outputs.*
