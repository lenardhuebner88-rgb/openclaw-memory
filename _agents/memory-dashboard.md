---
title: "Memory Dashboard"
last_generated: 2026-05-03T10:30:02.442485+00:00
type: memory-dashboard
generator: memory-dashboard-generator.py@v1-L6-Lite
auto_refresh: daily 04:30 UTC (cron)
---

# 🧠 Memory Dashboard

**Last Generated:** 2026-05-03 10:30 UTC  
**Source-of-Truth:** Multiple (QMD-index + facts.jsonl + rules.jsonl + graph.jsonl + kb/* + memory-budget.log)  
**Refresh:** Auto-daily via `memory-dashboard-generator.py` 04:30 UTC. Manual: run script directly.

---

## 1. Memory-Stack Overview

| Level | Component | Status | Notes |
|---|---|---|---|
| **L1** | QMD Hybrid-Retrieval (BM25+Vector+Rerank) | ✅ active | 2088 files indexed |
| **L2** | Fact-Extraction + Rules + Dreaming | ✅ active | 287 facts, 56 rules |
| **L3-MVP** | Schema v2 + Reflection + KB + Graph + Retrieval-Feedback | ✅ active | 1279 graph edges, 8 retrieval-events logged |
| **L5** | Memory-Budget-Meter + Atlas-State-Snapshot | ✅ active | [2026-05-03T10:30:01Z] OK session=f1bf6a47-5b9 size=69800 tokens_est=17450 pct=11% |
| **L6-Lite** | This Static Dashboard | ✅ active | You are reading it |

## 2. Active Rules (49 total)

### API-Regeln (3)

- **R1** [active] Verify-After-Write ist Pflicht
- **R2** [active] Kein unreplaced `{placeholder}` in Task-Description
- **R3** [active] Atlas meldet keinen Erfolg ohne GET-Verify

### Agent-Targeting-Regeln (2)

- **R11** [active] Runtime-ID vs Alias nicht verwechseln
- **R12** [active] Worker-Agents dürfen kein LTM schreiben

### Atlas-Governance (4)

- **R49** [active] Atlas Anti-Hallucination Claim-Verify-Before-Report
- **R54** [active] MCP-Not-Connected erst als Session-/Gateway-Korrelation triagieren
- **R55** [active] Gateway-Restart heilt keine stale MCP-Session-Runtimes
- **R57** [active] Atlas terminal results use canonical Stage-7 format

### Board-Hygiene (1)

- **R48** [kandidiert] Board-Hygiene-Cron auto-cancel stale drafts

### Build & Code-Safety (3)

- **R26** [resolved] Server-Only Import-Disziplin
- **R27** [resolved] Legacy-Task nach Root-Cause-Fix
- **R28** [active] Operator-Lock-Respekt (geplant, Phase 2 Stabilization-Plan)

### Build / Deploy-Regeln (2)

- **R7** [active] Kanonische Build-Sequenz (nicht `deploy.sh`)
- **R8** [active] Jeder Edit bekommt `.bak-<scope>-<datum>`

### Build-Deploy-Regeln (17)

- **R29** [active] Build-Storm-Debounce
- **R30** [pending] MCP-Taskboard-Server-Zombies
- **R31** [pending] API-Ghost-State (List vs Get divergiert)
- **R32** [pending] Dispatch-Gate Atlas-Sonderfall
- **R33** [active] Cron-Script-Pfad-Integrität
- **R34** [resolved] Bootstrap-Limit für MEMORY.md (Agent-Bootstrap-Truncation)
- **R35** [active] Atlas-Self-Report ≠ Board-Truth
- **R36** [pending] Agent-Session-File-Size-Creep
- **R37** [resolved] Atlas-Orchestrator-Tasks nicht via Auto-Pickup
- **R38** [resolved] MCP-Zombie-Defense-in-depth (existierender Reaper + Alert)
- **R39** [active] Atlas-main braucht Session-Resume-Pattern
- **R40** [resolved] Stall-Detection-Thresholds sind Kern-Infra
- **R41** [active] Memory-Retrieval: QMD vor File-Read
- **R42** [active] Deploy-Restart-Discipline via mc-restart-safe
- **R46** [active] Parallel-Deploy-Serialization
- **R50** [active] Session-Lock-Governance fuer Auto-Pickup
- **R52** [active] Auto-Pickup Silent-Fail-Detection

### Codex-Governance (1)

- **R56** [active] Vault-SSOT und Sprint-Read-Order respektieren

### Config-Regeln (4)

- **R4** [active] openclaw.json NIE direkt editieren
- **R5** [active] Kanonischer MC-Service ist User-Level, Port 3000
- **R51** [active] Schema-Validation-Gate fuer openclaw.json
- **R6** [active] `worker-pickup-loop.py` bleibt tot

### Governance (1)

- **R47** [active] Scope-Lock-auf-Plan-Doc nicht Task-ID

### Hygiene (1)

- **R53** [active] Config/Scripts Daily Snapshot in Vault

### Integrations-Regeln (2)

- **R10** [active] Alerts laufen NICHT über MC-API
- **R9** [resolved] Discord-Webhook-Calls brauchen User-Agent

### Multi-Agent-Koordinations-Regeln (6)

- **R18** [active] mc-ops-monitor ist read-only-alerting
- **R19** [active] heartbeat darf keinen Subagent spawnen für terminale Tasks
- **R20** [active] worker-monitor ist run-lifecycle-only
- **R21** [active] Layer-Cleanup-Tasks brauchen Script-Referenz-Check
- **R22** [resolved] Task ohne Result-Receipt ≠ erfolgsfrei
- **R23** [active] Retry-Task nur bei Parent in failed/error-State

### Multi-Agent-Orchestration (2)

- **R44** [active] Board-Discipline: Board-Task required before sessions_spawn
- **R45** [active] Sub-Agent-Receipt-Discipline

### Naming & Runtime-Regeln (2)

- **R24** [resolved] Runtime-ID vs Display-Alias Disziplin (verschärft)
- **R25** [resolved] workerLabel muss beim Dispatch gesetzt werden

### Operator-Eingriff-Regeln (5)

- **R13** [active] Operator greift bei Instabilität ein, nicht bei langsamkeit
- **R14** [active] Tangenten → `spawn_task`, nie mitnehmen
- **R15** [active] Deploy-Sequenz ist atomar im Agent-Turn
- **R16** [active] V8-Heap-Limit muss explizit sein
- **R17** [active] systemd MemoryMax > V8 Heap-Limit

## 3. Facts Today (2026-05-03) — 0 total

*(no facts extracted today yet)*

## 4. Facts All-Time — 287 total

### Last 7 Days

- `2026-04-19`: 154
- `2026-04-18`: 133

### Decay-Status

- Low-importance (<0.3): 262 (91%)
- High-importance (>0.7): 11
- Schema v2: 287

## 5. KB Articles (Karpathy-style cross-refs)

- [10-KB](kb/10-KB.md) — 12 Zeilen
- [AGENTS](kb/AGENTS.md) — 17 Zeilen
- [Atlas Hallucination Prevention](kb/atlas-hallucination-prevention.md) — 64 Zeilen
- [Board Hygiene & Lifecycle](kb/board-hygiene.md) — 70 Zeilen
- [Build & Deploy Rules](kb/build-deploy-regeln.md) — 74 Zeilen
- [Deploy Contracts & MC-Restart](kb/deploy-contracts.md) — 76 Zeilen
- [Hermes Shadow Debug Pattern](kb/hermes-shadow-debug.md) — 33 Zeilen
- [Incident Response & RCA](kb/incident-response.md) — 95 Zeilen
- [Memory Architecture](kb/memory-architecture.md) — 60 Zeilen
- [Receipt Discipline](kb/receipt-discipline.md) — 90 Zeilen
- [Scope Governance & operatorLock](kb/scope-governance.md) — 63 Zeilen
- [Sprint Orchestration](kb/sprint-orchestration.md) — 106 Zeilen
- [Sub-Agent Coordination](kb/sub-agent-coordination.md) — 85 Zeilen

## 6. Memory-Graph — 1279 edges

### Edges by Type

- `related-to`: 933
- `precedes`: 266
- `supersedes`: 71
- `caused-by`: 9

### Top-10 Most-Connected Facts (in-degree)

- `967225ab2f8d` (22 in-edges) — Defense-Stack Pattern 2026-04-19: 12 automated cron-layers active für governance
- `362e267df04c` (19 in-edges) — Rules-Stack erweitert auf R1-R49 (49 total) am 2026-04-19. Heute neu: R45 Sub-Ag
- `c1d688578e59` (18 in-edges) — Atlas-main lief 2026-04-19 evening auf MiniMax-M2.7 statt Codex (primary offline
- `5ee1ed4ac247` (18 in-edges) — Today's highest-importance facts:   - [1.00] R49 Atlas Anti-Hallucination Claim-
- `26e954cf4d0d` (15 in-edges) — Sprint-L Memory-Level-3 MVPs deployed 2026-04-19 20:00-21:30 UTC: L1 KB-Compiler
- `1f4f56a6a7d3` (13 in-edges) — Pre-Flight-Sprint-Dispatch Script deployed 2026-04-19 20:42 UTC mit 7 Gates: Atl
- `5f8f0efea364` (13 in-edges) — Memory-Budget-Meter first real CRITICAL caught 2026-04-19 21:20 UTC: Atlas-sessi
- `4257d42fb7d9` (13 in-edges) — Check C: orphaned NUR wenn dispatchState=dispatched AND execState not in active/
- `a48697e9b5ae` (13 in-edges) — Check C: orphaned NUR wenn dispatchState=dispatched AND execState not in active/
- `9c16dbac1998` (13 in-edges) — If output contains PARITY_CHECK_FAILED or PARITY_CHECK_ERROR, reply with first 1

## 7. Retrieval-Feedback (L3 reinforcement)

- Total access-events logged: 8

### Top-10 Most-Accessed Facts

*(no access-events tracked yet — L3 Retrieval-Feedback MVP is new)*

## 8. Budget-Meter History (last 10)

```
[2026-05-03T09:45:01Z] OK session=f1bf6a47-5b9 size=62327 tokens_est=15581 pct=10%
[2026-05-03T09:50:01Z] OK session=f1bf6a47-5b9 size=62327 tokens_est=15581 pct=10%
[2026-05-03T09:55:01Z] OK session=f1bf6a47-5b9 size=63562 tokens_est=15890 pct=10%
[2026-05-03T10:00:01Z] OK session=f1bf6a47-5b9 size=63562 tokens_est=15890 pct=10%
[2026-05-03T10:05:01Z] OK session=f1bf6a47-5b9 size=67668 tokens_est=16917 pct=11%
[2026-05-03T10:10:01Z] OK session=f1bf6a47-5b9 size=67668 tokens_est=16917 pct=11%
[2026-05-03T10:15:01Z] OK session=f1bf6a47-5b9 size=67668 tokens_est=16917 pct=11%
[2026-05-03T10:20:01Z] OK session=f1bf6a47-5b9 size=68565 tokens_est=17141 pct=11%
[2026-05-03T10:25:01Z] OK session=f1bf6a47-5b9 size=69800 tokens_est=17450 pct=11%
[2026-05-03T10:30:01Z] OK session=f1bf6a47-5b9 size=69800 tokens_est=17450 pct=11%
```

## 9. Active Crons (summary)

- User-crontab: 55 active
- Systemd user-timers: 
- OpenClaw-Cron-Plugin (enabled): 14
- **Total: ~69 schedules**

Full inventory: [cron-audit-2026-04-19.md](cron-audit-2026-04-19.md)

## 10. Reflective Memory Today (0 entries)

*(no reflective entries yet — will be generated at 23:50 UTC by daily-reflection-cron)*


---

*Auto-generated by `memory-dashboard-generator.py@v1-L6-Lite` (Sprint-L L6-Lite MVP). Next run: 04:30 UTC daily.*