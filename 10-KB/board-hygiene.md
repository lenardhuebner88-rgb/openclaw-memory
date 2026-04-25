---
title: "Board Hygiene & Lifecycle"
slug: board-hygiene
last_compiled: 2026-04-25T03:30:17.445169Z
compiler: kb-compiler.py@v1-mvp
fact_count: 38
rule_count: 2
memory_level: 3
---

# Board Hygiene & Lifecycle

**Description:** Auto-cleanup of stale drafts, board state management, admin-close API patterns.

**Compiled:** 2026-04-25T03:30:17.445169Z  
**Source:** 38 facts from workspace/memory/facts/*.jsonl, 2 rules from workspace/memory/rules.jsonl

## Key Rules

### R44 — Board-Discipline: Board-Task required before sessions_spawn
*Status: active | Since: 2026-04-19*

Sub-Agent-Arbeit darf nie sessions_spawn-only laufen. Vor jeder delegierten Ausfuehrung MUSS ein Board-Task via taskboard_create_task existieren oder ein vorhandener Task genutzt werden. Wenn kein Board-Task vorhanden ist: zuerst taskboard_create_tas...

### R48 — Board-Hygiene-Cron auto-cancel stale drafts
*Status: kandidiert | Since: 2026-04-19*

Cron */60min admin-close: (A) status=draft AND age>48h -> canceled reason 'auto-cleanup stale draft', (B) status=failed AND completedAt=null AND age>24h -> set completedAt=now (archive ohne status-change).

## Key Facts (Top-20 by Importance)

- **[0.95]** `procedural` (2026-04-19T21:35:11 system#91fe24e9) — R47 Scope-Lock auf Plan-Doc-Frontmatter statt Task-ID deployed Sprint-J J2 (commit c268ee0). Live-Case: Sprint-F operatorLock=true auf draft ee455d69 wurde umgangen durch neue Task-IDs (89afba3b, e45a...
- **[0.90]** `procedural` (2026-04-19T21:35:11 system#362e267d) — Rules-Stack erweitert auf R1-R49 (49 total) am 2026-04-19. Heute neu: R45 Sub-Agent-Receipt-Discipline, R46 Parallel-Deploy-Serialization, R47 Scope-Lock-Plan-Doc, R48 Board-Hygiene-Cron, R49 Atlas An...
- **[0.85]** `procedural` (2026-04-19T21:35:11 system#8d84780c) — R48 Board-Hygiene-Cron deployed 2026-04-19 ~19:30 UTC (hourly). Rule: status=draft AND age>48h → admin-close. Motivation: 19 stale tasks manually cleaned by Operator 19:41 UTC (6 drafts 3-8d old + 13 ...
- **[0.85]** `semantic` (2026-04-19T21:35:11 system#967225ab) — Defense-Stack Pattern 2026-04-19: 12 automated cron-layers active für governance + memory + monitoring: session-freeze-watcher */5, r49-claim-validator */15, r48-board-hygiene hourly, daily-reflection...
- **[0.76]** `procedural` (2026-04-19T21:35:11 system#098d7a25) — Cron-Audit 2026-04-19 23:00 UTC: 51 aktive Schedules über 3 Scheduler fragmentiert (34 crontab + 6 systemd-timer + 16 openclaw-cron). 0 active errors, historische nur aus Sprint-E MC-Flap 17:00-17:32....
- **[0.67]** `procedural` (2026-04-19T21:35:11 system#442a3328) — Board-Cleanup 2026-04-19 19:41 UTC durch Operator-Assistant: 19 stale Tasks admin-closed (6 drafts age 3-8d + 13 failed null-completedAt). Board open_count 6→0. Tool: PATCH /api/tasks/<id>/admin-close...
- **[0.62]** `semantic` (2026-04-19T21:35:11 system#1db9c9d9) — 10 Karpathy-KB-Articles compiled 2026-04-19 20:46 UTC in vault/03-Agents/kb/: sprint-orchestration (27f/7r), receipt-discipline (34f/4r), deploy-contracts (12f/3r), atlas-hallucination-prevention (0f/...
- **[0.62]** `procedural` (2026-04-19T21:35:11 system#1c7cd11c) — Sprint-Debrief-Watch openclaw-cron 031f586a disabled 2026-04-19 22:50 UTC nach Timeout-Spam (cron: job execution timed out alle 12min). Ersetzt durch lightweight shell-script /home/piet/.openclaw/scri...
- **[0.50]** `episodic` (2026-04-19T09:15:49 main#7427d8a9) — **Offene Tasks jetzt:** - Naming-Audit → in-progress by Spark - Alte Spark-Tasks (failed/canceled) → aufgeräumt ✅ Soll ich noch einen WK-37 für den `auto-pickup.py` Script-Pfad-Fix (gestern kaputt) al...
- **[0.50]** `episodic` (2026-04-19T09:15:49 main#e4c87be2) — **Offene Tasks jetzt:** - Naming-Audit → in-progress by Spark - Alte Spark-Tasks (failed/canceled) → aufgeräumt ✅ Soll ich noch einen WK-37 für den `auto-pickup.py` Script-Pfad-Fix (gestern kaputt) al...
- **[0.49]** `episodic` (2026-04-19T03:01:37 main#d11a25a2) — Let me now patch it to completed status since the artifact is created: - Assistant: The task workflow can't transition from `canceled` → `done` (the prior failed attempt locked it).
- **[0.49]** `episodic` (2026-04-19T03:01:43 main#8f4c1fe6) — Even the failed path had a tenderness to it, canceled not as ruin but as a door swollen by rain, refusing to close properly.
- **[0.48]** `episodic` (2026-04-18T15:20:39 main#3145f347) — Aktuell matched dispatchState=dispatched + nicht active + nicht in-progress -> auch failed/canceled/done als orphaned gemeldet.
- **[0.48]** `episodic` (2026-04-18T15:20:39 main#7ba8af28) — Check C: orphaned NUR wenn dispatchState=dispatched AND execState not in active/queued/review AND status not in in-progress/pending-pickup/review/done/failed/canceled 2.
- **[0.48]** `episodic` (2026-04-18T15:20:39 main#32872c46) — Smoke-Test: 1 synthetic failed-Task, 1 canceled-Task, 1 pending-pickup-Task.
- **[0.48]** `episodic` (2026-04-18T15:20:39 main#51d7019e) — HEARTBEAT.md § Section 2C ergaenzen: "Wenn Task bereits status=failed/canceled (gesetzt durch mc-ops oder worker-monitor): Heartbeat SPAWNED keinen Subagent mehr.
- **[0.48]** `episodic` (2026-04-18T15:20:39 main#25fc66a2) — Aktuell matched dispatchState=dispatched + nicht active + nicht in-progress -> auch failed/canceled/done als orphaned gemeldet.
- **[0.48]** `episodic` (2026-04-18T15:20:39 main#81acfcc6) — Check C: orphaned NUR wenn dispatchState=dispatched AND execState not in active/queued/review AND status not in in-progress/pending-pickup/review/done/failed/canceled 2.
- **[0.48]** `episodic` (2026-04-18T15:20:39 main#8f1c7c8d) — Smoke-Test: 1 synthetic failed-Task, 1 canceled-Task, 1 pending-pickup-Task.
- **[0.48]** `episodic` (2026-04-18T15:20:39 main#d53191cd) — HEARTBEAT.md § Section 2C ergaenzen: "Wenn Task bereits status=failed/canceled (gesetzt durch mc-ops oder worker-monitor): Heartbeat SPAWNED keinen Subagent mehr.

## Related KB Articles

- [Atlas Hallucination Prevention](atlas-hallucination-prevention.md)
- [Deploy Contracts & MC-Restart](deploy-contracts.md)
- [Incident Response & RCA](incident-response.md)
- [Receipt Discipline](receipt-discipline.md)
- [Scope Governance & operatorLock](scope-governance.md)
- [Sprint Orchestration](sprint-orchestration.md)
- [Sub-Agent Coordination](sub-agent-coordination.md)

## Metadata

- **Topic keywords** (for future recompilation): board-hygiene, R48, admin-close, admin-cleanup, draft, stale, cancel, board open_count
- **Related rules (declared)**: R48, R44
- **Schema version**: KB-article v1-mvp

---

*Auto-compiled from 38 facts + 2 rules by `kb-compiler.py@v1-mvp`. Manual edits will be preserved where possible but may be overwritten on next compile — use `<!-- manual: start --> ... <!-- manual: end -->` to mark preserved sections (future feature).*