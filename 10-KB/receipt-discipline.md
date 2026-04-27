---
title: "Receipt Discipline"
slug: receipt-discipline
last_compiled: 2026-04-27T10:30:02.768275Z
compiler: kb-compiler.py@v1-mvp
fact_count: 40
rule_count: 6
memory_level: 3
---

# Receipt Discipline

**Description:** Sub-Agent Receipt-Lifecycle — accepted/progress/result pattern, stall-detection, R45 enforcement.

**Compiled:** 2026-04-27T10:30:02.768275Z  
**Source:** 40 facts from workspace/memory/facts/*.jsonl, 6 rules from workspace/memory/rules.jsonl

## Key Rules

### R22 — Task ohne Result-Receipt ≠ erfolgsfrei
*Status: resolved | Since: 2026-04-18*



### R40 — Stall-Detection-Thresholds sind Kern-Infra
*Status: resolved | Since: 2026-04-19*



### R44 — Board-Discipline: Board-Task required before sessions_spawn
*Status: active | Since: 2026-04-19*

Sub-Agent-Arbeit darf nie sessions_spawn-only laufen. Vor jeder delegierten Ausfuehrung MUSS ein Board-Task via taskboard_create_task existieren oder ein vorhandener Task genutzt werden. Wenn kein Board-Task vorhanden ist: zuerst taskboard_create_tas...

### R45 — Sub-Agent-Receipt-Discipline
*Status: active | Since: 2026-04-19*

Sub-Agent MUSS innerhalb 60s nach Task-Pickup taskboard_post_receipt mit receipt=accepted posten. Waehrend Arbeit MUSS mindestens alle 5min oder bei jedem Major-Step ein receipt=progress kommen. Status assigned laenger als 2min ohne Receipt = Contrac...

### R46 — Parallel-Deploy-Serialization
*Status: active | Since: 2026-04-19*

Wenn mehrere Sub-Agents parallel laufen UND jeder einen systemctl --user restart mission-control + curl verify Contract im Prompt hat → Deploy-Race-Condition. Fix: sequenzieller Sprint-Flow ODER Deploy-Queue-Lock (nur ein MC-Restart gleichzeitig, Age...

### R57 — Atlas terminal results use canonical Stage-7 format
*Status: active | Since: 2026-04-27*

Atlas autonomous sprint/task terminal outputs MUST include the five canonical Stage-7 sections in order: EXECUTION_STATUS, RESULT_SUMMARY, GATES, FOLLOW_UPS, OPERATOR_DECISIONS. Result summaries must be task-specific and human-meaningful; generic pla...

## Key Facts (Top-20 by Importance)

- **[0.95]** `procedural` (2026-04-19T21:35:11 system#cfa2ead4) — R45 Sub-Agent-Receipt-Discipline deployed 2026-04-19 17:20 UTC nach Live-Case Sprint-E E2+E3 wo Sub-Agents 2h+ in status=assigned stecken blieben ohne Receipts zu posten. Fix: AGENTS.md Preamble + ses...
- **[0.90]** `procedural` (2026-04-19T21:35:11 system#362e267d) — Rules-Stack erweitert auf R1-R49 (49 total) am 2026-04-19. Heute neu: R45 Sub-Agent-Receipt-Discipline, R46 Parallel-Deploy-Serialization, R47 Scope-Lock-Plan-Doc, R48 Board-Hygiene-Cron, R49 Atlas An...
- **[0.74]** `reflective` (2026-04-19T21:50:01 system#5ee1ed4a) — Today's highest-importance facts:   - [1.00] R49 Atlas Anti-Hallucination Claim-Verify-Before-Report deployed 2026-04-19 20:3   - [0.95] R45 Sub-Agent-Receipt-Discipline deployed 2026-04-19 17:20 UTC ...
- **[0.61]** `episodic` (2026-04-19T21:35:11 system#ead36dfd) — Atlas autonomous-cascade Sprint-F+G+H ohne Operator-Approval dispatched 2026-04-19 17:56-19:30 UTC. Sprint-F F1+F2 done autonomously (Lens/Forge), Sprint-G G1-G4 done (4 commits), Sprint-H H1-H3 mit 2...
- **[0.53]** `semantic` (2026-04-19T21:35:11 system#1db9c9d9) — 10 Karpathy-KB-Articles compiled 2026-04-19 20:46 UTC in vault/03-Agents/kb/: sprint-orchestration (27f/7r), receipt-discipline (34f/4r), deploy-contracts (12f/3r), atlas-hallucination-prevention (0f/...
- **[0.45]** `episodic` (2026-04-19T08:24:13 main#4cea56c3) — **Aktueller Stand:** | Task | Status | |------|--------| | WK-35 Retry (Operator-Lock) | pending-pickup → Forge | | Spark Naming-P2 | assigned | | Spark Naming-Audit | assigned | Falls wieder `failed`...
- **[0.45]** `episodic` (2026-04-19T08:24:13 main#1075b705) — **Aktueller Stand:** | Task | Status | |------|--------| | WK-35 Retry (Operator-Lock) | pending-pickup → Forge | | Spark Naming-P2 | assigned | | Spark Naming-Audit | assigned | Falls wieder `failed`...
- **[0.36]** `episodic` (2026-04-19T10:35:08 main#816f127f) — [Retry after the previous model attempt failed or timed out] worker-monitor (automated): 1 Task(s) abgeschlossen seit letztem Zyklus: - [spark] receipt-seq-test-2: Completed (summary missing, auto-nor...
- **[0.36]** `episodic` (2026-04-19T13:43:51 main#485ac6ca) — Reply with only: EXECUTION_STATUS: <ok|blocked|failed> RESULT_SUMMARY: <5-10 bullet style clauses, concise> Constraints: - No config writes.
- **[0.36]** `episodic` (2026-04-19T13:44:54 efficiency-auditor#09ea09d7) — Reply with only: EXECUTION_STATUS: <ok|blocked|failed> RESULT_SUMMARY: <5-10 bullet style clauses, concise> Constraints: - No config writes.
- **[0.35]** `episodic` (2026-04-19T09:15:49 main#7427d8a9) — **Offene Tasks jetzt:** - Naming-Audit → in-progress by Spark - Alte Spark-Tasks (failed/canceled) → aufgeräumt ✅ Soll ich noch einen WK-37 für den `auto-pickup.py` Script-Pfad-Fix (gestern kaputt) al...
- **[0.35]** `episodic` (2026-04-19T09:15:49 main#e4c87be2) — **Offene Tasks jetzt:** - Naming-Audit → in-progress by Spark - Alte Spark-Tasks (failed/canceled) → aufgeräumt ✅ Soll ich noch einen WK-37 für den `auto-pickup.py` Script-Pfad-Fix (gestern kaputt) al...
- **[0.35]** `episodic` (2026-04-19T09:11:07 main#10b6d408) — Ich habe Option B bereits umgesetzt: **Naming-P2 frisch** → dispatched zu Spark ✅ Naming-Audit (`2d33bb1b`) ist noch assigned (konnte nicht auf failed gesetzt werden wegen `dispatchState=queued` Block...
- **[0.35]** `episodic` (2026-04-19T09:11:07 main#5035d6ac) — Ich habe Option B bereits umgesetzt: **Naming-P2 frisch** → dispatched zu Spark ✅ Naming-Audit (`2d33bb1b`) ist noch assigned (konnte nicht auf failed gesetzt werden wegen `dispatchState=queued` Block...
- **[0.34]** `episodic` (2026-04-18T23:10:26 main#9f563fd5) — **B2 receiptStage** `df9db7de` — failed → no-receipt umbenennen A4 und B2 sind rein kosmetisch/minimal.
- **[0.33]** `episodic` (2026-04-18T19:30:55 main#7cdcfb8e) — ⚠️ Orphaned task auto-failed 090fdc54 [Retry] Sprint C-Backend Security-Gate Receipt Abs Reason: Task in-progress/dispatched 17m ago but no workerSessionId and no receipt/accepted received (threshold=...
- **[0.33]** `episodic` (2026-04-18T19:30:55 main#d489467a) — ⚠️ Orphaned task auto-failed 090fdc54 [Retry] Sprint C-Backend Security-Gate Receipt Abs Reason: Task in-progress/dispatched 17m ago but no workerSessionId and no receipt/accepted received (threshold=...
- **[0.33]** `episodic` (2026-04-18T19:04:14 main#755ff0a3) — Description should include Board counts (open/assigned, in-progress, pending-pickup, failed, review), V-Closure states, T1/T3/T2 status, blockers, and next 30min.
- **[0.33]** `episodic` (2026-04-18T19:30:55 main#541c1234) — BOARD_STATUS: failed TIMESTAMP: 2026-04-18T19:30:03.587Z ⚠️ Progress timeout, task stalled 090fdc54 [Retry] Sprint C-Backend Security-Gate Receipt Abschluss Reason: No progress receipt for 17m (thresh...
- **[0.33]** `episodic` (2026-04-18T19:30:55 main#77c4d4b2) — BOARD_STATUS: failed TIMESTAMP: 2026-04-18T19:30:03.587Z ⚠️ Progress timeout, task stalled 090fdc54 [Retry] Sprint C-Backend Security-Gate Receipt Abschluss Reason: No progress receipt for 17m (thresh...

## Related KB Articles

- [Atlas Hallucination Prevention](atlas-hallucination-prevention.md)
- [Board Hygiene & Lifecycle](board-hygiene.md)
- [Deploy Contracts & MC-Restart](deploy-contracts.md)
- [Incident Response & RCA](incident-response.md)
- [Scope Governance & operatorLock](scope-governance.md)
- [Sprint Orchestration](sprint-orchestration.md)
- [Sub-Agent Coordination](sub-agent-coordination.md)

## Metadata

- **Topic keywords** (for future recompilation): receipt, accepted, progress, result, assigned, in-progress, stall, R45...
- **Related rules (declared)**: R45, R40, R44
- **Schema version**: KB-article v1-mvp

---

*Auto-compiled from 40 facts + 6 rules by `kb-compiler.py@v1-mvp`. Manual edits will be preserved where possible but may be overwritten on next compile — use `<!-- manual: start --> ... <!-- manual: end -->` to mark preserved sections (future feature).*