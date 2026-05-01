---
title: "Sub-Agent Coordination"
slug: sub-agent-coordination
last_compiled: 2026-05-01T06:30:18.088863Z
compiler: kb-compiler.py@v1-mvp
fact_count: 20
rule_count: 5
memory_level: 3
---

# Sub-Agent Coordination

**Description:** Multi-agent coordination patterns, sub-agent dispatch, visibility-rules, WIP-limits.

**Compiled:** 2026-05-01T06:30:18.088863Z  
**Source:** 20 facts from workspace/memory/facts/*.jsonl, 5 rules from workspace/memory/rules.jsonl

## Key Rules

### R37 — Atlas-Orchestrator-Tasks nicht via Auto-Pickup
*Status: resolved | Since: 2026-04-19*

Atlas-Sprint-Tasks als `draft` + `operatorLock=true` anlegen (Auto-Pickup skipped). Operator startet Atlas-Session manuell mit Trigger-Phrase "Lade <Plan> und starte <Sprint>". Atlas liest Board, erkennt `[Atlas-Sprint-*]`-Prefix und orchestriert Sub...

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

## Key Facts (Top-20 by Importance)

- **[0.51]** `episodic` (2026-04-19T21:35:11 system#5f8f0efe) — Memory-Budget-Meter first real CRITICAL caught 2026-04-19 21:20 UTC: Atlas-session 48f8d0f0 explodierte auf 373% (559k tokens / 150k budget) während Forge Sprint-G/H Consolidation-Task. Vorheriger che...
- **[0.46]** `procedural` (2026-04-19T21:35:11 system#8bb6b4eb) — Sprint-K H10 Cron-Inventory-Consolidation + Observability formally added 2026-04-19 23:15 UTC. 5 Layers: L1 Cleanup (DONE), L2 Memory-Orchestrator (1-2h), L3 Systemd-Migration 3 crons (2h), L4 Healthc...
- **[0.44]** `episodic` (2026-04-19T21:35:11 system#ead36dfd) — Atlas autonomous-cascade Sprint-F+G+H ohne Operator-Approval dispatched 2026-04-19 17:56-19:30 UTC. Sprint-F F1+F2 done autonomously (Lens/Forge), Sprint-G G1-G4 done (4 commits), Sprint-H H1-H3 mit 2...
- **[0.39]** `episodic` (2026-04-19T21:35:11 system#258f56ec) — Sprint-G/H Consolidation 2026-04-19 21:16-21:18 UTC (Forge 5a10491a): 4 commits konsolidierten Sprint-G/H autonomous-cascade Arbeit: b941b36 (.bak removes), 5fac96a (sprint-g ops-dashboard), daee0c7 (...
- **[0.37]** `semantic` (2026-04-19T14:20:24 main#e8798fff) — - **Sprint-B sequence started:** B2-B4 merged into a single delegated Forge task to reduce spawn overhead.
- **[0.29]** `episodic` (2026-04-19T08:24:13 main#4cea56c3) — **Aktueller Stand:** | Task | Status | |------|--------| | WK-35 Retry (Operator-Lock) | pending-pickup → Forge | | Spark Naming-P2 | assigned | | Spark Naming-Audit | assigned | Falls wieder `failed`...
- **[0.29]** `episodic` (2026-04-19T08:24:13 main#1075b705) — **Aktueller Stand:** | Task | Status | |------|--------| | WK-35 Retry (Operator-Lock) | pending-pickup → Forge | | Spark Naming-P2 | assigned | | Spark Naming-Audit | assigned | Falls wieder `failed`...
- **[0.27]** `episodic` (2026-04-19T21:35:11 system#7a59071b) — R49-Claim-Validator first detection 2026-04-19 21:15 UTC: WARNING auf task_not_found 26ed095e-a77a-4b3d-8b50-9ff06635cf92 in sre-expert session. False-positive — ist mcp-zombie-killer-hourly cron-sess...
- **[0.24]** `reflective` (2026-04-19T20:34:51 system#f639b494) — Agent-activity today: {'main': 141, 'sre-expert': 104, 'spark': 3, 'frontend-guru': 2, 'efficiency-auditor': 2}
- **[0.24]** `reflective` (2026-04-19T21:50:01 system#f639b494) — Agent-activity today: {'main': 141, 'sre-expert': 104, 'spark': 3, 'frontend-guru': 2, 'efficiency-auditor': 2, 'system': 25}
- **[0.22]** `episodic` (2026-04-19T09:11:07 main#10b6d408) — Ich habe Option B bereits umgesetzt: **Naming-P2 frisch** → dispatched zu Spark ✅ Naming-Audit (`2d33bb1b`) ist noch assigned (konnte nicht auf failed gesetzt werden wegen `dispatchState=queued` Block...
- **[0.22]** `episodic` (2026-04-19T09:11:07 main#5035d6ac) — Ich habe Option B bereits umgesetzt: **Naming-P2 frisch** → dispatched zu Spark ✅ Naming-Audit (`2d33bb1b`) ist noch assigned (konnte nicht auf failed gesetzt werden wegen `dispatchState=queued` Block...
- **[0.22]** `episodic` (2026-04-19T09:15:49 main#7427d8a9) — **Offene Tasks jetzt:** - Naming-Audit → in-progress by Spark - Alte Spark-Tasks (failed/canceled) → aufgeräumt ✅ Soll ich noch einen WK-37 für den `auto-pickup.py` Script-Pfad-Fix (gestern kaputt) al...
- **[0.22]** `episodic` (2026-04-19T09:15:49 main#e4c87be2) — **Offene Tasks jetzt:** - Naming-Audit → in-progress by Spark - Alte Spark-Tasks (failed/canceled) → aufgeräumt ✅ Soll ich noch einen WK-37 für den `auto-pickup.py` Script-Pfad-Fix (gestern kaputt) al...
- **[0.22]** `episodic` (2026-04-19T10:35:08 main#816f127f) — [Retry after the previous model attempt failed or timed out] worker-monitor (automated): 1 Task(s) abgeschlossen seit letztem Zyklus: - [spark] receipt-seq-test-2: Completed (summary missing, auto-nor...
- **[0.17]** `episodic` (2026-04-19T21:35:11 system#0fa75e5c) — Sprint-I Mobile-Polish v2 dispatched 2026-04-19 ~21:21 UTC via Operator trigger 'Atlas nun nächster Sprint follow #42'. 7 Subs planned (Tap-Targets, Typography+Safe-Area, Loading-States+Offline-Queue,...
- **[0.17]** `episodic` (2026-04-19T10:15:10 main#a4d9c153) — The failure of Forge subagents to execute properly is blocking Sprint 1.
- **[0.17]** `episodic` (2026-04-19T10:15:10 main#521c98a5) — **Confirm subagent spawn failure**: Verify that `openclaw agent` when run with the specific parameters for Forge is failing silently.
- **[0.17]** `episodic` (2026-04-19T11:14:40 main#d97f40ce) — Finder: Die OOM hat laufende Forge-Sessions gekillt, aber Code-Änderungen sind in git.
- **[0.16]** `episodic` (2026-04-19T21:35:11 system#c1d68857) — Atlas-main lief 2026-04-19 evening auf MiniMax-M2.7 statt Codex (primary offline). Sprint-I-Dispatch funktional, 4 parallele Sub-Tasks (Pixel×2 + Forge + Lens) dispatched innerhalb 2min nach /reset. R...

## Related KB Articles

- [Atlas Hallucination Prevention](atlas-hallucination-prevention.md)
- [Board Hygiene & Lifecycle](board-hygiene.md)
- [Deploy Contracts & MC-Restart](deploy-contracts.md)
- [Incident Response & RCA](incident-response.md)
- [Receipt Discipline](receipt-discipline.md)
- [Scope Governance & operatorLock](scope-governance.md)
- [Sprint Orchestration](sprint-orchestration.md)

## Metadata

- **Topic keywords** (for future recompilation): sessions_spawn, taskboard_create_task, pixel, forge, lens, james, spark, frontend-guru...
- **Related rules (declared)**: R44, R37, R40
- **Schema version**: KB-article v1-mvp

---

*Auto-compiled from 20 facts + 5 rules by `kb-compiler.py@v1-mvp`. Manual edits will be preserved where possible but may be overwritten on next compile — use `<!-- manual: start --> ... <!-- manual: end -->` to mark preserved sections (future feature).*