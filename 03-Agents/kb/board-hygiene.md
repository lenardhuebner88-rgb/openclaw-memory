---
title: "Board Hygiene & Lifecycle"
slug: board-hygiene
last_compiled: 2026-04-19T20:46:30.335832Z
compiler: kb-compiler.py@v1-mvp
fact_count: 30
rule_count: 1
memory_level: 3
---

# Board Hygiene & Lifecycle

**Description:** Auto-cleanup of stale drafts, board state management, admin-close API patterns.

**Compiled:** 2026-04-19T20:46:30.335832Z  
**Source:** 30 facts from workspace/memory/facts/*.jsonl, 1 rules from workspace/memory/rules.jsonl

## Key Rules

### R48 — Board-Hygiene-Cron auto-cancel stale drafts
*Status: kandidiert | Since: 2026-04-19*

Cron */60min admin-close: (A) status=draft AND age>48h -> canceled reason 'auto-cleanup stale draft', (B) status=failed AND completedAt=null AND age>24h -> set completedAt=now (archive ohne status-change).

## Key Facts (Top-20 by Importance)

- **[0.66]** `episodic` (2026-04-18T15:20:39 main#3145f347) — Aktuell matched dispatchState=dispatched + nicht active + nicht in-progress -> auch failed/canceled/done als orphaned gemeldet.
- **[0.66]** `episodic` (2026-04-18T15:20:39 main#7ba8af28) — Check C: orphaned NUR wenn dispatchState=dispatched AND execState not in active/queued/review AND status not in in-progress/pending-pickup/review/done/failed/canceled 2.
- **[0.66]** `episodic` (2026-04-18T15:20:39 main#32872c46) — Smoke-Test: 1 synthetic failed-Task, 1 canceled-Task, 1 pending-pickup-Task.
- **[0.66]** `episodic` (2026-04-18T15:20:39 main#51d7019e) — HEARTBEAT.md § Section 2C ergaenzen: "Wenn Task bereits status=failed/canceled (gesetzt durch mc-ops oder worker-monitor): Heartbeat SPAWNED keinen Subagent mehr.
- **[0.66]** `episodic` (2026-04-18T15:20:39 main#25fc66a2) — Aktuell matched dispatchState=dispatched + nicht active + nicht in-progress -> auch failed/canceled/done als orphaned gemeldet.
- **[0.66]** `episodic` (2026-04-18T15:20:39 main#81acfcc6) — Check C: orphaned NUR wenn dispatchState=dispatched AND execState not in active/queued/review AND status not in in-progress/pending-pickup/review/done/failed/canceled 2.
- **[0.66]** `episodic` (2026-04-18T15:20:39 main#8f1c7c8d) — Smoke-Test: 1 synthetic failed-Task, 1 canceled-Task, 1 pending-pickup-Task.
- **[0.66]** `episodic` (2026-04-18T15:20:39 main#d53191cd) — HEARTBEAT.md § Section 2C ergaenzen: "Wenn Task bereits status=failed/canceled (gesetzt durch mc-ops oder worker-monitor): Heartbeat SPAWNED keinen Subagent mehr.
- **[0.66]** `episodic` (2026-04-18T15:20:39 main#e4f16607) — Aktuell matched dispatchState=dispatched + nicht active + nicht in-progress -> auch failed/canceled/done als orphaned gemeldet.
- **[0.66]** `episodic` (2026-04-18T15:20:39 main#1d2119e8) — Check C: orphaned NUR wenn dispatchState=dispatched AND execState not in active/queued/review AND status not in in-progress/pending-pickup/review/done/failed/canceled 2.
- **[0.66]** `episodic` (2026-04-18T15:20:39 main#1c69a426) — Smoke-Test: 1 synthetic failed-Task, 1 canceled-Task, 1 pending-pickup-Task.
- **[0.66]** `episodic` (2026-04-18T15:20:39 main#c9af438d) — HEARTBEAT.md § Section 2C ergaenzen: "Wenn Task bereits status=failed/canceled (gesetzt durch mc-ops oder worker-monitor): Heartbeat SPAWNED keinen Subagent mehr.
- **[0.66]** `episodic` (2026-04-18T15:20:39 main#00441830) — Aktuell matched dispatchState=dispatched + nicht active + nicht in-progress -> auch failed/canceled/done als orphaned gemeldet.
- **[0.66]** `episodic` (2026-04-18T15:20:39 main#4257d42f) — Check C: orphaned NUR wenn dispatchState=dispatched AND execState not in active/queued/review AND status not in in-progress/pending-pickup/review/done/failed/canceled 2.
- **[0.66]** `episodic` (2026-04-18T15:20:39 main#80215616) — Smoke-Test: 1 synthetic failed-Task, 1 canceled-Task, 1 pending-pickup-Task.
- **[0.66]** `episodic` (2026-04-18T15:20:39 main#87903654) — HEARTBEAT.md § Section 2C ergaenzen: "Wenn Task bereits status=failed/canceled (gesetzt durch mc-ops oder worker-monitor): Heartbeat SPAWNED keinen Subagent mehr.
- **[0.66]** `episodic` (2026-04-18T15:20:39 main#ea2f3c57) — Aktuell matched dispatchState=dispatched + nicht active + nicht in-progress -> auch failed/canceled/done als orphaned gemeldet.
- **[0.66]** `episodic` (2026-04-18T15:20:39 main#a48697e9) — Check C: orphaned NUR wenn dispatchState=dispatched AND execState not in active/queued/review AND status not in in-progress/pending-pickup/review/done/failed/canceled 2.
- **[0.66]** `episodic` (2026-04-18T15:20:39 main#763e40ca) — Smoke-Test: 1 synthetic failed-Task, 1 canceled-Task, 1 pending-pickup-Task.
- **[0.66]** `episodic` (2026-04-18T15:20:39 main#a290c0d0) — HEARTBEAT.md § Section 2C ergaenzen: "Wenn Task bereits status=failed/canceled (gesetzt durch mc-ops oder worker-monitor): Heartbeat SPAWNED keinen Subagent mehr.

## Related KB Articles

- [Receipt Discipline](receipt-discipline.md)
- [Scope Governance & operatorLock](scope-governance.md)
- [Sprint Orchestration](sprint-orchestration.md)
- [Sub-Agent Coordination](sub-agent-coordination.md)

## Metadata

- **Topic keywords** (for future recompilation): board-hygiene, R48, admin-close, admin-cleanup, draft, stale, cancel, board open_count
- **Related rules (declared)**: R48, R44
- **Schema version**: KB-article v1-mvp

---

*Auto-compiled from 30 facts + 1 rules by `kb-compiler.py@v1-mvp`. Manual edits will be preserved where possible but may be overwritten on next compile — use `<!-- manual: start --> ... <!-- manual: end -->` to mark preserved sections (future feature).*