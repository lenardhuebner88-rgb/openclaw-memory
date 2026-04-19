---
title: "Sub-Agent Coordination"
slug: sub-agent-coordination
last_compiled: 2026-04-19T20:46:30.336174Z
compiler: kb-compiler.py@v1-mvp
fact_count: 12
rule_count: 4
memory_level: 3
---

# Sub-Agent Coordination

**Description:** Multi-agent coordination patterns, sub-agent dispatch, visibility-rules, WIP-limits.

**Compiled:** 2026-04-19T20:46:30.336174Z  
**Source:** 12 facts from workspace/memory/facts/*.jsonl, 4 rules from workspace/memory/rules.jsonl

## Key Rules

### R37 — Atlas-Orchestrator-Tasks nicht via Auto-Pickup
*Status: resolved | Since: 2026-04-19*

Atlas-Sprint-Tasks als `draft` + `operatorLock=true` anlegen (Auto-Pickup skipped). Operator startet Atlas-Session manuell mit Trigger-Phrase "Lade <Plan> und starte <Sprint>". Atlas liest Board, erkennt `[Atlas-Sprint-*]`-Prefix und orchestriert Sub...

### R40 — Stall-Detection-Thresholds sind Kern-Infra
*Status: resolved | Since: 2026-04-19*



### R45 — Sub-Agent-Receipt-Discipline
*Status: active | Since: 2026-04-19*

Sub-Agent MUSS innerhalb 60s nach Task-Pickup taskboard_post_receipt mit receipt=accepted posten. Waehrend Arbeit MUSS mindestens alle 5min oder bei jedem Major-Step ein receipt=progress kommen. Status assigned laenger als 2min ohne Receipt = Contrac...

### R46 — Parallel-Deploy-Serialization
*Status: active | Since: 2026-04-19*

Wenn mehrere Sub-Agents parallel laufen UND jeder einen systemctl --user restart mission-control + curl verify Contract im Prompt hat → Deploy-Race-Condition. Fix: sequenzieller Sprint-Flow ODER Deploy-Queue-Lock (nur ein MC-Restart gleichzeitig, Age...

## Key Facts (Top-20 by Importance)

- **[0.77]** `episodic` (2026-04-19T08:24:13 main#4cea56c3) — **Aktueller Stand:** | Task | Status | |------|--------| | WK-35 Retry (Operator-Lock) | pending-pickup → Forge | | Spark Naming-P2 | assigned | | Spark Naming-Audit | assigned | Falls wieder `failed`...
- **[0.77]** `episodic` (2026-04-19T08:24:13 main#1075b705) — **Aktueller Stand:** | Task | Status | |------|--------| | WK-35 Retry (Operator-Lock) | pending-pickup → Forge | | Spark Naming-P2 | assigned | | Spark Naming-Audit | assigned | Falls wieder `failed`...
- **[0.66]** `episodic` (2026-04-19T09:11:07 main#10b6d408) — Ich habe Option B bereits umgesetzt: **Naming-P2 frisch** → dispatched zu Spark ✅ Naming-Audit (`2d33bb1b`) ist noch assigned (konnte nicht auf failed gesetzt werden wegen `dispatchState=queued` Block...
- **[0.66]** `episodic` (2026-04-19T09:11:07 main#5035d6ac) — Ich habe Option B bereits umgesetzt: **Naming-P2 frisch** → dispatched zu Spark ✅ Naming-Audit (`2d33bb1b`) ist noch assigned (konnte nicht auf failed gesetzt werden wegen `dispatchState=queued` Block...
- **[0.66]** `episodic` (2026-04-19T09:15:49 main#7427d8a9) — **Offene Tasks jetzt:** - Naming-Audit → in-progress by Spark - Alte Spark-Tasks (failed/canceled) → aufgeräumt ✅ Soll ich noch einen WK-37 für den `auto-pickup.py` Script-Pfad-Fix (gestern kaputt) al...
- **[0.66]** `episodic` (2026-04-19T09:15:49 main#e4c87be2) — **Offene Tasks jetzt:** - Naming-Audit → in-progress by Spark - Alte Spark-Tasks (failed/canceled) → aufgeräumt ✅ Soll ich noch einen WK-37 für den `auto-pickup.py` Script-Pfad-Fix (gestern kaputt) al...
- **[0.66]** `episodic` (2026-04-19T10:35:08 main#816f127f) — [Retry after the previous model attempt failed or timed out] worker-monitor (automated): 1 Task(s) abgeschlossen seit letztem Zyklus: - [spark] receipt-seq-test-2: Completed (summary missing, auto-nor...
- **[0.56]** `semantic` (2026-04-19T14:20:24 main#e8798fff) — - **Sprint-B sequence started:** B2-B4 merged into a single delegated Forge task to reduce spawn overhead.
- **[0.55]** `episodic` (2026-04-19T10:15:10 main#a4d9c153) — The failure of Forge subagents to execute properly is blocking Sprint 1.
- **[0.55]** `episodic` (2026-04-19T10:15:10 main#521c98a5) — **Confirm subagent spawn failure**: Verify that `openclaw agent` when run with the specific parameters for Forge is failing silently.
- **[0.55]** `episodic` (2026-04-19T11:14:40 main#d97f40ce) — Finder: Die OOM hat laufende Forge-Sessions gekillt, aber Code-Änderungen sind in git.
- **[0.50]** `reflective` (2026-04-19T20:34:51 system#f639b494) — Agent-activity today: {'main': 141, 'sre-expert': 104, 'spark': 3, 'frontend-guru': 2, 'efficiency-auditor': 2}

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

*Auto-compiled from 12 facts + 4 rules by `kb-compiler.py@v1-mvp`. Manual edits will be preserved where possible but may be overwritten on next compile — use `<!-- manual: start --> ... <!-- manual: end -->` to mark preserved sections (future feature).*