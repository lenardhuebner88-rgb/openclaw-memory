---
title: Deep Root-Cause-Analyse 2026-04-19 Multi-Sprint-Incident-Cluster
date: 2026-04-19 11:55 UTC
author: Operator (pieter_pan) + Research-Agent Findings
scope: 7 Incident-Klassen, minimale Fixes, architektonischer Ausblick
status: actionable
---

# Deep RCA — 2h Incident-Cluster 2026-04-19

## TL;DR
Die 7 beobachteten Incident-Klassen sind **1 zusammenhaengendes Failure-Mode-Cluster**. Root-Cause: *kein durable External State Store fuer Agent-Lifecycle*. Alle anderen Symptome (Concurrency-Cap, Stall-Threshold, Heartbeat-Classifier, Session-Size) sind Defensive-Mechanismen die fehlen oder unterdimensioniert sind.

**Alle 7 Klassen haben direkte Matches in openclaw/openclaw-GitHub-Issues + 2 ready-to-merge PRs.**

## Incident-Kette 10:29-11:54 UTC

| Zeit | Event | Root |
|---|---|---|
| 09:56 | Auto-Pickup-Trigger fuer Atlas -> HEARTBEAT_OK | R37 |
| 10:29 | Sprint-2 Dispatch 5+ parallele Subs | R30-Aufbau |
| 10:38:29 | **Gateway OOM-Kill** Peak 4.3 GB / Swap 3.5 GB | V8-Heap-Limit |
| 10:38:31 | Atlas-main SIGTERM-kaskade | kein systemd-Service |
| 10:38 | MC BUILD_ID verloren -> Cold-Rebuild 4-6min | Cold-Build |
| 10:39 | Operator-Kill 12->1 MCP-Zombies | R30-Mitigation |
| 10:40-11:05 | Auto-Pickup HOLD concurrency_cap=1, Deadlock | Stall-Threshold 30min |
| 11:14 | Neue Atlas-Session + Ghost-Cleanup | Recovery |
| 11:27-11:29 | Build-Storm 2 parallel builds, MC flap 2min | R29 |
| 11:45 | Mini-Deadlock Zombie 4e59f41c | Threshold-Gap |
| 11:54+ | Queue normalisiert | stable |

## Fuenf-Schichten-Root-Cause

### Schicht 1 — Process-Lifecycle (R30)
`cleanupBundleMcpOnRunEnd: false` in sessions_spawn-Pfad → MCP-Child-Prozesse ueberleben Parent.
- Issue #68827 — exakter Bug dokumentiert
- PR #68846 — Ein-Zeilen-Fix ready-to-merge
- Issue #50186 — systemd `KillMode=process` verstaerkt Problem

### Schicht 2 — Orchestrator-Resilience (Atlas-Orphan)
Atlas-main ist CLI-Subprocess ohne systemd-Service. Gateway-Kill -> Atlas stirbt -> 25min orphan.
- Issue #35802 — "No centralized agent registry"
- Issue #64435 — "Octopus Orchestrator" Lease-Pattern
- Industry: Temporal/BullMQ/K8s nutzen Lease+Heartbeat+durable store

### Schicht 3 — Stall-Detection-Thresholds
`STALL_WARN_MINUTES=10`, `STALL_HARD_MINUTES=30`. Industry-Median: 60-180s.
- Issue #61610 — literaler Match unseres Deadlocks
- Issue #39305 — empfiehlt 90s/180s
- BullMQ default: 30s stalledInterval
- Temporal activity_heartbeat_timeout: 30-120s

### Schicht 4 — Heartbeat-vs-Task-Classifier (R37)
Atlas klassifiziert vagen Auto-Pickup-Prompt als Heartbeat.
- Issue #40631 — gleiche Signatur
- PR #45925 — heartbeat wakes out of cron run sessions
- PR #66755 — detect silent NO_REPLY

### Schicht 5 — Context/Session-Growth (R36)
Atlas-Sessions 7+ MB ohne Compact/Rotation.
- Issue #66360 — session.maintenance no size cap
- Issue #66520 — **Auto-compact never fires when cache hit ~100%** — unser Fall

## Sofort-Fixes (minimal diff, <4h Arbeit)

### Fix 1: PR #68846 cherry-pick
```typescript
// src/agents/command/attempt-execution.ts — EINE ZEILE
cleanupBundleMcpOnRunEnd: params.opts.cleanupBundleMcpOnRunEnd || params.spawnedBy != null
```
Impact: MCP-Child-Cleanup bei sessions_spawn-Ende. Keine 12-Zombie-Buildups mehr.

### Fix 2: systemd KillMode=control-group
```ini
# /home/piet/.config/systemd/user/openclaw-gateway.service.d/kill-mode.conf
[Service]
KillMode=control-group
```
Impact: Pro Issue #50186 empirisch 10x+ RAM-Reduktion (807 Tasks -> 7, 11.1 GB -> 126 MB).

### Fix 3: Stall-Thresholds tighten
```python
# worker-monitor.py Line 49-50
STALL_WARN_MINUTES = 2
STALL_HARD_MINUTES = 5
```
Plus auto-fail bei `2 × timeoutSeconds` (per #61610).
Impact: Deadlock-Heilzeit 30min -> 5min.

### Fix 4: Atlas als systemd-service
```ini
# /home/piet/.config/systemd/user/openclaw-atlas.service
[Unit]
Requires=openclaw-gateway.service
After=openclaw-gateway.service
[Service]
ExecStart=/home/piet/.openclaw/bin/openclaw agent --agent main --persistent
Restart=on-failure
RestartSec=5s
```
Impact: Atlas-Orphan-Problem permanent geloest.

### Fix 5: Session-Hard-Cap + Force-Compact
Pre-turn-Hook: wenn >3 MB -> `/compact` erzwingen. Hard-Cap 5 MB mit Rotation.
Impact: Session bleibt <3 MB, kein Context-Freeze.

## Architektur-Roadmap (2-4 Wochen)

### 1. PR #68718 minions adopten
Durable SQLite Job-Queue mit:
- Lock-Heartbeat Sub-Sekunden Stall-Detection
- Crash-Recovery via Re-Queue
- Cascade-Cancel
- 9-State-Lifecycle
- Zero new deps (node:sqlite)

Wenn merged: `minions.durability=true` → loest R30+R37+Deadlock+Stall in einem Move.

### 2. Per-task heartbeat
Workers schreiben `last_tool_call_at` alle 10s. Supervisor killt bei staleness.

### 3. Build-storm lock-claim
Jeder Forge-Sub claimed Ressource vor Deploy. Lock 30s nach Release.

### 4. Wake-vs-Task IPC-Separation
Separater Header-Token oder Channel. Schliesst R37 final.

### 5. External Memory Store
Mem0/SQLite Context-Summaries. Atlas context <1 MB auch bei 8h Runs.

## Issues/PRs zum Watchen

| # | Titel | Status | Impact |
|---|---|---|---|
| PR #68846 | fix: reap MCP child processes | Open, merge-ready | R30 geloest |
| PR #68718 | minions durable SQLite job queue | Open, flag-gated | Architektur-Fundament |
| Issue #66520 | Auto-compact never fires with cache-hit | Open | R36 Ursache |
| Issue #61610 | tasks cancel + stuck-running prune | Open | Deadlock |
| Issue #50186 | KillMode=control-group | Open | R30 komplement |
| PR #68450 | dispose bundled MCP runtimes | Open | R30 komplement |

## Zwei-Schritt-Empfehlung

**Schritt 1 — diese Woche (30min + 1h Arbeit):**
- PR #68846 cherry-pick
- KillMode=control-group Flip
- Stall-Thresholds 2/5min
- Atlas systemd-service
- Session-Hard-Cap 5MB

**Schritt 2 — naechste 2-4 Wochen:**
- PR #68718 minions track + merge
- `minions.durability=true` setzen
- Per-task heartbeat migrieren
- External Memory Store integrieren

## Bottom Line

**Wir sind nicht allein.** Alle 7 Klassen sind bekannte openclaw-Bugs mit Fixes in-flight. 2 hoechste Leverage-Moves:

1. **PR #68846 cherry-pick + KillMode-Flip** (30min) — R30 root + 10x RAM-Reduktion
2. **Atlas systemd-service + Stall-Thresholds 2/5min** (1h) — Orphan + Deadlock weg

Strukturelle Cure: **PR #68718 (minions)** merge-watching.

---
Signed-off: Operator (pieter_pan) 2026-04-19 11:55 UTC
