# Heartbeat/Cron/Worker Audit - 2026-04-24

## Executive Summary
- Live-Zustand um 2026-04-24T13:41Z: `/api/health` = ok, Worker-Reconciler-Proof = 0 Issues, keine `in-progress` Tasks.
- `ssh homeserver "crontab -l -u piet"` schlug lokal fehl: `Could not resolve hostname homeserver`; Audit nutzte deshalb lokale Host-Wahrheit `crontab -l -u piet` auf `huebners`.
- Die Hypothese "5-min session-freeze-watcher blockiert Atlas aktive Discord-Session" ist durch Code-Evidence nicht bestaetigt: `session-freeze-watcher` ist read-only/out-of-band und ueberspringt `agent=main`.
- Kritischere Evidence liegt im Worker-Spawn/Claim-Pfad: Auto-Pickup zeigt heutige `CLAIM_TIMEOUT`s, Systemd zeigt zeitweise `left-over process ... openclaw-agent`, Worker-Monitor meldet `dispatched-no-claim`.
- Keine Small-Fixes angewendet: alle klaren Risiken betreffen explizit verbotene Core-Logik oder Architektur.
- Modell-Misfits in aktiven Cron-Kommandos: keine eindeutigen aktiven Cron-LLM-Modell-Kommandos gefunden; aktive Worker laufen ueber `openclaw/<agent>`.
- Tool-Allowlist-Dubletten in `lib/node_modules` und `workspace/node_modules` sind byte-identisch, daher kein Fix.
- Ziel: Heartbeats weiter out-of-band halten, Auto-Pickup Claim-Handoff separat haerten, Cron/Systemd-Sollstand in eine kanonische Registry ueberfuehren.

## Inventar-Tabelle

| Name | Schedule | Command / Quelle | Log-Pfad | Model | Session-Mode | Last-OK / letzte Evidence | Status |
|---|---:|---|---|---|---|---|---|
| session-freeze-watcher | systemd timer 5min | `/home/piet/.config/systemd/user/m7-session-freeze-watcher.timer`, service ExecStart `/home/piet/.openclaw/scripts/session-freeze-watcher.sh` | `/home/piet/.openclaw/workspace/memory/freeze-alerts.log`, alt `/tmp/session-freeze-watcher.log` | none | out-of-band HTTP + file stat; skips `main` | journal: finished 13:41Z, 13:35Z, 13:30Z | OK; not Atlas-active-session |
| r49-claim-validator | cron `*/15` | `crontab:piet:31` `/home/piet/.openclaw/scripts/r49-claim-validator.py` | `/tmp/r49-validator.log`; script writes `/home/piet/.openclaw/workspace/memory/r49-validator.log` | none | out-of-band MC API | cron present | OK by presence; no core finding in sampled logs |
| r48-board-hygiene | cron hourly | `crontab:piet:32` `/home/piet/.openclaw/scripts/r48-board-hygiene-cron.sh` | `/tmp/r48-hygiene.log`; script writes `/home/piet/.openclaw/workspace/memory/r48-hygiene.log` | none | out-of-band MC API | cron present | OK by presence |
| daily-reflection-cron | superseded | `crontab:piet:45` superseded by memory-orchestrator | memory-orchestrator logs | orchestrator-owned | batch | superseded marker | Drift vs Sollliste; intentional M6b migration |
| kb-compiler.py | superseded | `crontab:piet:39` superseded by memory-orchestrator | memory-orchestrator logs | orchestrator-owned | batch | superseded marker | Drift vs Sollliste; intentional M6b migration |
| graph-edge-builder | superseded | `crontab:piet:40` superseded by memory-orchestrator | memory-orchestrator logs | orchestrator-owned | batch | superseded marker | Drift vs Sollliste; intentional M6b migration |
| memory-budget-meter | cron `*/5` | `crontab:piet:24` `/home/piet/.openclaw/scripts/memory-budget-meter.sh` | `/tmp/memory-budget.log`, script target `/home/piet/.openclaw/workspace/memory/memory-budget.log` | none | out-of-band scanner | cron journal at 13:40Z | OK |
| retrieval-feedback-loop | superseded | `crontab:piet:42` superseded by memory-orchestrator hourly | memory-orchestrator logs | orchestrator-owned | batch | superseded marker | Drift vs Sollliste; intentional M6b migration |
| importance-recalc | superseded | `crontab:piet:43` superseded by memory-orchestrator weekly | memory-orchestrator logs | orchestrator-owned | batch | superseded marker | Drift vs Sollliste; intentional M6b migration |
| sprint-debrief-watch | cron `*/5` | `crontab:piet:25` `/home/piet/.openclaw/scripts/sprint-debrief-watch.sh` | `/tmp/sprint-debrief-watch.log` | none | out-of-band scanner | cron journal at 13:40Z | OK |
| memory-dashboard-generator | superseded | `crontab:piet:44` superseded by memory-orchestrator | memory-orchestrator logs | orchestrator-owned | batch | superseded marker | Drift vs Sollliste; intentional M6b migration |
| stale-lock-cleaner | systemd timer 5min | `/home/piet/.config/systemd/user/m7-stale-lock-cleaner.timer`, service ExecStart `/home/piet/.openclaw/scripts/stale-lock-cleaner.sh` | `/home/piet/.openclaw/workspace/memory/stale-lock-cleaner.log` | none | out-of-band lock scanner | journal: scanned 1 alive 0 removed 0 at 13:41Z | OK |
| session-health-monitor | cron `*/10` | `crontab:piet:27` `/home/piet/.openclaw/scripts/session-health-monitor.py` | `/home/piet/.openclaw/workspace/memory/session-health.log` | none | out-of-band session scanner | cron journal at 13:40Z | OK; uses `os.kill(pid,0)` as liveness probe |
| auto-pickup.py | systemd timer 1min | `/home/piet/.config/systemd/user/m7-auto-pickup.timer`, service ExecStart `/home/piet/.openclaw/scripts/auto-pickup-runner.sh` | `/home/piet/.openclaw/workspace/logs/auto-pickup.log` | `openclaw/<agent>` via CLI | isolated subprocess, `start_new_session=True` | journal: finished at 13:41Z; earlier start-limit/leftover process | DEGRADED history, currently quiet |
| Atlas main HTTP heartbeat | cron every minute | `crontab:piet:14` POST `/api/heartbeat/main` | stdout suppressed | none | out-of-band HTTP | cron journal at 13:42Z | OK; frequency differs from stated hourly 07-23 context |
| Forge gateway heartbeat | systemd timer hourly | `forge-heartbeat.timer` -> `/home/piet/.openclaw/scripts/forge-heartbeat.sh` | `/home/piet/.openclaw/outputs/logs/forge-heartbeat.log` | none | out-of-band HTTP; after 3 fails runs `openclaw doctor --fix` | log: latest visible OK 2026-04-24 14:46 CEST | Risk if gateway has repeated failures |
| session-size-guard | cron `*/5` plus `* * * * * --log-only` | `crontab:piet:80-81` | `/home/piet/.openclaw/workspace/logs/session-size-guard.log` | none | out-of-band file scanner/rotation guard | cron journal at 13:40Z and 13:42Z | OK, but noisy/high frequency |
| session-rotation-watchdog | cron `*/2` | `crontab:piet:87` | `/tmp/session-rotation-watchdog.log` | none | signal-file writer | last Atlas signal write/clear 10:26Z/10:36Z | OK; should remain advisory |

## Applied Small-Fixes Log

No Small-Fixes applied.

Rationale:
- The only high-confidence current risk is in Auto-Pickup/Worker-Monitor/Core session handling, explicitly forbidden for in-place modification in this Auftrag.
- `forge-heartbeat.sh` has risky `doctor --fix` behavior, but changing service behavior is beyond "1 job/1 field" because it alters recovery semantics.
- Tool allowlist copies are byte-identical; no duplicate cleanup needed.
- No active cron command had a clear LLM model misfit suitable for a one-line model replacement.

## Findings

### F1 - `homeserver` SSH alias not resolvable from this session
- Problem: Required command `ssh homeserver "crontab -l -u piet"` could not run.
- Evidence: command returned `ssh: Could not resolve hostname homeserver: Name or service not known`.
- Impact: Remote-alias workflow is brittle; current audit used local host truth on `/home/piet`.
- Fix-Vorschlag: Add/repair `Host homeserver` in the operator SSH config, or update runbooks to use local execution when already on `huebners`.

### F2 - 14-Defense-Cron-Sollliste does not match actual control plane
- Problem: Several Soll jobs are now systemd timers or memory-orchestrator-superseded, while crontab still carries historical comments.
- Evidence: `crontab:piet:13,21-23` show M7 systemd migration; `crontab:piet:39-45` show M6b superseded memory jobs.
- Impact: Audits that only diff `crontab -l` produce false missing/duplicate findings.
- Fix-Vorschlag: Create one canonical `defense-jobs.registry.json` with owner, scheduler, active flag, expected log, mutation class, and rollback command.

### F3 - Atlas active-session block hypothesis is not supported for `session-freeze-watcher`
- Problem: Operator symptom is Atlas via Discord appearing hung; suspected 5-min heartbeat blocking active session.
- Evidence: `/home/piet/.openclaw/scripts/session-freeze-watcher.sh:22-33` fetches `/api/tasks`; lines 48-49 skip `AGENT=main`; lines 59-80 only resolve/stat worker session files.
- Impact: Fixing `session-freeze-watcher` session topology would not address the observed Atlas Discord hang.
- Fix-Vorschlag: Keep freeze watcher out-of-band; investigate Auto-Pickup main task spawns and Discord session-size/rotation instead.

### F4 - Main heartbeat frequency differs from stated context
- Problem: Context says Atlas HTTP heartbeat hourly 07-23 Europe/Berlin, but actual cron sends `POST /api/heartbeat/main` every minute.
- Evidence: `crontab:piet:14`; cron journal shows the same command at 13:39Z, 13:40Z, 13:41Z, 13:42Z.
- Impact: Low direct session risk because it is HTTP and stdout-suppressed, but it increases MC write/load frequency and can hide real liveness semantics.
- Fix-Vorschlag: Decide canonical heartbeat policy: either every minute as cheap MC liveness, or reduce to `*/5`/hourly and rely on worker proofs for real work state.

### F5 - Worker-Spawn/Claim path shows real degradation
- Problem: Auto-Pickup had claim timeouts and spawned workers that did not claim fast enough; Systemd also saw leftover `openclaw-agent` processes.
- Evidence: `/home/piet/.openclaw/workspace/logs/auto-pickup.log` includes `CLAIM_TIMEOUT` at 08:54Z, 11:03Z, 11:39Z, 12:20Z and later `CLAIM_CONFIRMED`; journal shows `left-over process ... openclaw-agent` around 13:01Z, 13:14Z, 13:21Z.
- Impact: This is the likely rootcause class for "Atlas wirkt haengend": tasks may be spawned, not claim-bound, or continue after oneshot unit completion.
- Fix-Vorschlag: Dedicated Core-Fix Sprint: harden child process lifecycle, first-claim timeout accounting, and proof classification for expected child survival after oneshot.

### F6 - Worker-Monitor reports `dispatched-no-claim`
- Problem: Worker-Monitor flagged tasks stuck without `pickup_claimed`.
- Evidence: `/home/piet/.openclaw/workspace/scripts/worker-monitor.log` reports `dispatched-no-claim` for tasks `84e2299a`, `3bc580cc`, `5539b621`, `30c36874`.
- Impact: Confirms the issue is not just heartbeat noise; there are observable dispatch-to-claim gaps.
- Fix-Vorschlag: Add a real E2E test task that asserts state changes: `pending-pickup -> claimed/accepted -> in-progress -> done`, and validates `workerSessionId`, run record, heartbeat, and final receipt.

### F7 - Auto-Pickup had API-unreachable/start-limit window
- Problem: Around 12:53Z-12:55Z API calls failed with connection refused; systemd entered repeated failures/start-limit before recovering.
- Evidence: `/home/piet/.openclaw/workspace/logs/auto-pickup.log` `ERR_API <urlopen error [Errno 111] Connection refused>`; journal shows `status=1/FAILURE` and `start-limit-hit` around 12:54Z-12:59Z.
- Impact: During MC restart/build windows, Auto-Pickup can create noisy failure alerts and delayed pickup.
- Fix-Vorschlag: Make API-unreachable a non-failing degraded exit for one-shot polling, or make timer backoff explicit; do not change until Core Sprint.

### F8 - Historical traceback in `auto-pickup-cron.log`, current source appears changed after it
- Problem: `auto-pickup-cron.log` contains `UnboundLocalError` from `cleanup_unclaimed_spawn_locks`.
- Evidence: `/home/piet/.openclaw/workspace/logs/auto-pickup-cron.log` tail shows traceback; `stat` shows `/home/piet/.openclaw/scripts/auto-pickup.py` modified at 2026-04-24 14:23 CEST, after that log file's mtime context.
- Impact: Treat as historical unless reproduced; still belongs in Core regression tests.
- Fix-Vorschlag: Add unit test for cleanup of unclaimed spawn locks with no matching task dict and with terminal task.

### F9 - Forge heartbeat has mutating fallback behavior
- Problem: On three gateway failures, `forge-heartbeat.sh` runs `openclaw doctor --fix`.
- Evidence: `/home/piet/.openclaw/scripts/forge-heartbeat.sh:20-22`; active `forge-heartbeat.timer` exists in `timers.target.wants`.
- Impact: A heartbeat can become a mutating repair path; this violates the target principle "watchers out-of-band/read-only".
- Fix-Vorschlag: Migration stage: split into read-only heartbeat and separate operator-approved repair action. Do not change live in this audit without approval.

### F10 - Session-size rotation remains noisy/advisory but should not reroute work
- Problem: Rotation watchdog writes Atlas signal files when budget crosses thresholds.
- Evidence: `/tmp/session-rotation-watchdog.log` shows writes/clears for Atlas sessions, e.g. 2026-04-24T06:46Z at 93%, 10:26Z at 86%.
- Impact: Useful warning, but if connected to active routing it can disrupt sessions.
- Fix-Vorschlag: Keep as warning/signal only unless operator explicitly approves rotation behavior; align with user's stated preference.

## Worker-System Befund

### State Machine
1. `queued/assigned` task is made eligible for dispatch.
2. Auto-Pickup polls `pending-pickup` tasks from `/api/tasks`.
3. It evaluates session locks via `/home/piet/.openclaw/scripts/auto-pickup.py:379-431`.
4. It spawns `openclaw agent --agent <agent> --message "REAL_TASK=true TASK_ID=..." --json` with `start_new_session=True` at `/home/piet/.openclaw/scripts/auto-pickup.py:857-888`.
5. Worker must send accepted/claim receipt; Auto-Pickup waits in `wait_for_claim_binding` at `/home/piet/.openclaw/scripts/auto-pickup.py:230-264`.
6. If confirmed, task should move into active claimed/in-progress state with `workerSessionId`.
7. Worker sends progress/result receipt; terminal state becomes `done/failed/canceled`.
8. Worker-Monitor is not dispatch owner by default: `/home/piet/.openclaw/workspace/scripts/worker-monitor.py:75-79` sets `WORKER_MONITOR_DISPATCH_ENABLED=0`.

### Race Conditions / Failure Modes
- API restart window: Auto-Pickup one-shot exits failure on `ERR_API`, systemd retries and can hit start-limit.
- Claim timeout: spawned process exists but task has no confirmed claim within budget.
- Leftover process: oneshot service finishes while child `openclaw/openclaw-agent` remains in cgroup; systemd logs implementation deficiency.
- Discord/non-main session lock is intentionally ignored for Auto-Pickup main target: log shows `SESSION_LOCK_IGNORE ... session=agent:main:discord:... reason=non-main-session`.
- `session-freeze-watcher` does not touch main, so it is not the race owner.

### R19 / R50
- R19 current guard present: Auto-Pickup prompt includes `REAL_TASK=true TASK_ID=...` and for `main` includes `ORCHESTRATOR_MODE=true. This is NOT a heartbeat... Do NOT return HEARTBEAT_OK`.
- In sampled recent logs no fresh `HEARTBEAT_OK` task-execution hit was found.
- R50 not modified. No `operatorLock` or session lock governance changes were applied.

## Werkzeugliste-Abgleich

- `find /home/piet/.openclaw -maxdepth 5 -name tools*.json -o -name allowlist*` found only bundled JS allowlist artifacts under `lib/node_modules/openclaw/dist` and `workspace/node_modules/openclaw/dist`.
- Hash check: paired `allowlist-config-edit-CWwW-8J5.js` hashes match; paired `allowlist-match-BwqmzAfd.js` hashes match.
- No agent-specific `tools*.json` or allowlist divergence found under `/home/piet/.openclaw/agents` at sampled depth.

## Live-Probes

- `/api/health`: `status=ok`, `severity=ok`, `openCount=0`, `inProgress=0`, `pendingPickup=0`.
- `/api/ops/worker-reconciler-proof?limit=20`: `status=ok`, `openRuns=0`, `issues=0`, `criticalIssues=0`.
- `/api/tasks?status=in-progress`: empty `tasks: []`.

## Offene Fragen an Operator

1. Soll der minuetliche `/api/heartbeat/main` als bewusstes Liveness-Signal bleiben, oder auf `*/5`/hourly zur Soll-Liste normalisiert werden?
2. Soll `forge-heartbeat.sh` in einem separaten Sprint auf read-only umgestellt werden, sodass `doctor --fix` nur noch manuell/approved laeuft?
3. Soll der naechste Core-Sprint Auto-Pickup Claim-Handoff als P0 behandeln, inklusive realem E2E-Testtask fuer `main` und einen Specialist-Agent?
