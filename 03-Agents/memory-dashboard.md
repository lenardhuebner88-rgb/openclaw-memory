---
title: "Memory Dashboard"
last_generated: 2026-04-19T21:29:12.374612+00:00
type: memory-dashboard
generator: memory-dashboard-generator.py@v1-L6-Lite
auto_refresh: daily 04:30 UTC (cron)
---

# 🧠 Memory Dashboard

**Last Generated:** 2026-04-19 21:29 UTC  
**Source-of-Truth:** Multiple (QMD-index + facts.jsonl + rules.jsonl + graph.jsonl + kb/* + memory-budget.log)  
**Refresh:** Auto-daily via `memory-dashboard-generator.py` 04:30 UTC. Manual: run script directly.

---

## 1. Memory-Stack Overview

| Level | Component | Status | Notes |
|---|---|---|---|
| **L1** | QMD Hybrid-Retrieval (BM25+Vector+Rerank) | ✅ active | 735 files indexed |
| **L2** | Fact-Extraction + Rules + Dreaming | ✅ active | 257 facts, 46 rules |
| **L3-MVP** | Schema v2 + Reflection + KB + Graph + Retrieval-Feedback | ✅ active | 1024 graph edges, 0 retrieval-events logged |
| **L5** | Memory-Budget-Meter + Atlas-State-Snapshot | ✅ active | [2026-04-19T21:25:01Z] OK session=dd82eeec-d02 size=16598 tokens_est=4149 pct=2% |
| **L6-Lite** | This Static Dashboard | ✅ active | You are reading it |

## 2. Active Rules (49 total)

### API-Regeln (3)

- **R1** [active] Verify-After-Write ist Pflicht
- **R2** [active] Kein unreplaced `{placeholder}` in Task-Description
- **R3** [active] Atlas meldet keinen Erfolg ohne GET-Verify

### Agent-Targeting-Regeln (2)

- **R11** [active] Runtime-ID vs Alias nicht verwechseln
- **R12** [active] Worker-Agents dürfen kein LTM schreiben

### Atlas-Governance (1)

- **R49** [active] Atlas Anti-Hallucination Claim-Verify-Before-Report

### Board-Hygiene (1)

- **R48** [kandidiert] Board-Hygiene-Cron auto-cancel stale drafts

### Build & Code-Safety (3)

- **R26** [resolved] Server-Only Import-Disziplin
- **R27** [resolved] Legacy-Task nach Root-Cause-Fix
- **R28** [active] Operator-Lock-Respekt (geplant, Phase 2 Stabilization-Plan)

### Build / Deploy-Regeln (2)

- **R7** [active] Kanonische Build-Sequenz (nicht `deploy.sh`)
- **R8** [active] Jeder Edit bekommt `.bak-<scope>-<datum>`

### Build-Deploy-Regeln (14)

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
- **R46** [active] Parallel-Deploy-Serialization

### Config-Regeln (3)

- **R4** [active] openclaw.json NIE direkt editieren
- **R5** [active] Kanonischer MC-Service ist User-Level, Port 3000
- **R6** [active] `worker-pickup-loop.py` bleibt tot

### Governance (1)

- **R47** [active] Scope-Lock-auf-Plan-Doc nicht Task-ID

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

### Multi-Agent-Orchestration (1)

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

## 3. Facts Today (2026-04-19) — 257 total

### Memory-Type

- `episodic`: 251
- `reflective`: 5
- `semantic`: 1

### Category

- `incident`: 251
- `reflection`: 5
- `delivery`: 1

### Agent

- `main`: 141
- `sre-expert`: 104
- `system`: 5
- `spark`: 3
- `frontend-guru`: 2
- `efficiency-auditor`: 2

### Top-5 High-Importance Facts Today

- **[0.85]** Today's highest-importance facts:   - [0.77] - Mehrere operative Incidents gelöst, am Ende 0 offene Tasks und 0 failed.   - [0.77] **Sub-Pla
- **[0.80]** Incident-Themes today (251 incidents): ['failed', 'output', 'contains', 'parity_check_failed', 'parity_check_error,']
- **[0.76]** - Mehrere operative Incidents gelöst, am Ende 0 offene Tasks und 0 failed.
- **[0.76]** **Sub-Plan A Status:** - A1 ✅ `b84ac186` done - A2 ✅ `515b940f` done - A3 ✅ `f1d6a4d4` done (Incident-Lane nur status=failed) A4 ('Later'→'A
- **[0.76]** The `atlas-main` session (`agent:main:discord:channel:1486480128576983070`) has `status=failed`, `runtimeMs=0`, `startedAt > endedAt` — it c

## 4. Facts All-Time — 257 total

### Last 7 Days

- `2026-04-19`: 124
- `2026-04-18`: 133

### Decay-Status

- Low-importance (<0.3): 0 (0%)
- High-importance (>0.7): 8
- Schema v2: 257

## 5. KB Articles (Karpathy-style cross-refs)

- [Atlas Hallucination Prevention](kb/atlas-hallucination-prevention.md) — 57 Zeilen
- [Board Hygiene & Lifecycle](kb/board-hygiene.md) — 62 Zeilen
- [Build & Deploy Rules](kb/build-deploy-regeln.md) — 72 Zeilen
- [Deploy Contracts & MC-Restart](kb/deploy-contracts.md) — 62 Zeilen
- [Incident Response & RCA](kb/incident-response.md) — 84 Zeilen
- [Memory Architecture](kb/memory-architecture.md) — 48 Zeilen
- [Receipt Discipline](kb/receipt-discipline.md) — 80 Zeilen
- [Scope Governance & operatorLock](kb/scope-governance.md) — 50 Zeilen
- [Sprint Orchestration](kb/sprint-orchestration.md) — 95 Zeilen
- [Sub-Agent Coordination](kb/sub-agent-coordination.md) — 72 Zeilen

## 6. Memory-Graph — 1024 edges

### Edges by Type

- `related-to`: 720
- `precedes`: 241
- `supersedes`: 63

### Top-10 Most-Connected Facts (in-degree)

- `4257d42fb7d9` (13 in-edges) — Check C: orphaned NUR wenn dispatchState=dispatched AND execState not in active/
- `a48697e9b5ae` (13 in-edges) — Check C: orphaned NUR wenn dispatchState=dispatched AND execState not in active/
- `9c16dbac1998` (13 in-edges) — If output contains PARITY_CHECK_FAILED or PARITY_CHECK_ERROR, reply with first 1
- `f3051bebc125` (13 in-edges) — If output contains PARITY_CHECK_FAILED or PARITY_CHECK_ERROR, reply with first 1
- `c1874c000f38` (13 in-edges) — If output contains PARITY_CHECK_FAILED or PARITY_CHECK_ERROR, reply with first 1
- `670524f3646a` (13 in-edges) — If output contains PARITY_CHECK_FAILED or PARITY_CHECK_ERROR, reply with first 1
- `158764a6c016` (13 in-edges) — If output contains PARITY_CHECK_FAILED or PARITY_CHECK_ERROR, reply with first 1
- `babb817f7f30` (12 in-edges) — If output contains PARITY_CHECK_FAILED or PARITY_CHECK_ERROR, reply with first 1
- `6ef35fed9adf` (12 in-edges) — If output contains PARITY_CHECK_FAILED or PARITY_CHECK_ERROR, reply with first 1
- `1bfba500348a` (12 in-edges) — If output contains PARITY_CHECK_FAILED or PARITY_CHECK_ERROR, reply with first 1

## 7. Retrieval-Feedback (L3 reinforcement)

- Total access-events logged: 0

### Top-10 Most-Accessed Facts

*(no access-events tracked yet — L3 Retrieval-Feedback MVP is new)*

## 8. Budget-Meter History (last 10)

```
[2026-04-19T20:48:28Z] OK session=55c774a7-94a size=310175 tokens_est=77543 pct=51%
[2026-04-19T20:50:01Z] CRITICAL session=dee5d735-6c6 size=642513 tokens_est=160628 pct=107%
[2026-04-19T20:55:01Z] OK session=13ad19dc-04b size=289253 tokens_est=72313 pct=48%
[2026-04-19T21:00:01Z] OK session=b2d0f4a7-07c size=210088 tokens_est=52522 pct=35%
[2026-04-19T21:05:01Z] OK session=39f1c029-1db size=5459 tokens_est=1364 pct=0%
[2026-04-19T21:10:01Z] OK session=b2d0f4a7-07c size=221177 tokens_est=55294 pct=36%
[2026-04-19T21:15:01Z] OK session=b2d0f4a7-07c size=258761 tokens_est=64690 pct=43%
[2026-04-19T21:20:01Z] CRITICAL session=48f8d0f0-2f0 size=2239098 tokens_est=559774 pct=373%
[2026-04-19T21:25:01Z] OK session=dd82eeec-d02 size=16598 tokens_est=4149 pct=2%
```

## 9. Active Crons (summary)

- User-crontab: 38 active
- Systemd user-timers: 7
- OpenClaw-Cron-Plugin (enabled): 16
- **Total: ~61 schedules**

Full inventory: [cron-audit-2026-04-19.md](cron-audit-2026-04-19.md)

## 10. Reflective Memory Today (5 entries)

- **[0.70]** Today's top fact-categories: incident:251, delivery:1
- **[0.60]** Memory-Type split: {'episodic': 251, 'semantic': 1}
- **[0.85]** Today's highest-importance facts:   - [0.77] - Mehrere operative Incidents gelöst, am Ende 0 offene Tasks und 0 failed.   - [0.77] **Sub-Plan A Status:** - A1 ✅ `b84ac186` done - A2 ✅ `515b940f` done 
- **[0.50]** Agent-activity today: {'main': 141, 'sre-expert': 104, 'spark': 3, 'frontend-guru': 2, 'efficiency-auditor': 2}
- **[0.80]** Incident-Themes today (251 incidents): ['failed', 'output', 'contains', 'parity_check_failed', 'parity_check_error,']


---

*Auto-generated by `memory-dashboard-generator.py@v1-L6-Lite` (Sprint-L L6-Lite MVP). Next run: 04:30 UTC daily.*