---
title: "Sprint Orchestration"
slug: sprint-orchestration
last_compiled: 2026-04-19T20:46:30.335165Z
compiler: kb-compiler.py@v1-mvp
fact_count: 27
rule_count: 7
memory_level: 3
---


<!-- llm-synth: start -->
## 📖 Synthesis (LLM-generated, 2026-04-19)

*3-paragraph Operator-Synthese, auto-generiert via NVIDIA Nemotron. Template-Render darunter für Detail-Access.*

Die zentrale Aufgabe der Sprint‑Orchestrierung in Atlas‑Main besteht darin, die Zusammenarbeit mehrerer Agenten während eines Sprints so zu steuern, dass jede Aufgabe eindeutig verfolgt, rechtzeitig verarbeitet und das Board stets einen korrekten Überblick über den aktuellen Stand bietet. Dabei geht es vor allem darum, das Entstehen von „verwaiste“ Tasks zu verhindern, die sonst das Board verstopfen und die Planung gefährden, sowie sicherzustellen, dass Dispatch‑Entscheidungen nur auf gesunden, verfügbaren Worker‑Sessions beruhen. Auf diese Weise wird die Zuverlässigkeit des gesamten Multi‑Agent‑Systems erhöht und das Team kann sich auf die eigentliche Wertschöpfung konzentrieren, statt ständig nach verlorenen Arbeiten zu suchen.

Die beiden wichtigsten Regeln, die diese Ziele unterstützen, sind zunächst die Orphaned‑Task‑Erkennung: Eine Aufgabe gilt als verwaisst, wenn ihr dispatchState auf „dispatched“ steht, ihr execState weder active, queued noch review ist und ihr Status nicht zu den erlaubten Werten (in‑progress, pending‑pickup, review, done, failed, canceled) gehört; danach wird sie nach einem definierten Schwellenwert automatisch als failed markiert. Diese Regel verhindert, dass Aufgaben unbeaufsichtigt im System verbleiben und das Board verfälscht. Zweitens gilt die Board‑Visibility‑Disziplin: Nur Tasks mit einer gültigen workerSessionId und einem erhaltenen receipt/accepted‑Signal werden als „in‑progress“ angezeigt; alle anderen werden entweder als orphaned gekennzeichnet oder aus der aktiven Ansicht entfernt. Dadurch erhalten Operatoren ein unverfälschtes Bild des tatsächlichen Fortschritts und können frühzeitig eingreifen, bevor ein Problem eskaliert. Zusätzlich wird ein Dispatch‑Pattern angewendet, das neue Tasks nur dann in die Warteschlange stellt, wenn eine freie Worker‑Session vorhanden ist und das execState auf „queued“ gesetzt werden kann; sonst bleibt das Task im dispatched‑Zustand, bis Ressourcen frei werden. Dieses Pattern sorgt für eine gleichmäßige Auslastung und verhindert Überlastungen, die zu OOM‑Ab

*Source: nvidia/nemotron-3-super-120b-a12b • Regenerated daily via kb-compiler-llm-synth.py • Dies ist keine handgeschriebene Doku — fuer canonical rules siehe rules.jsonl.*
<!-- llm-synth: end -->

# Sprint Orchestration

**Description:** How Atlas-main orchestriert multi-agent sprints, dispatch-patterns, Board-visibility discipline.

**Compiled:** 2026-04-19T20:46:30.335165Z  
**Source:** 27 facts from workspace/memory/facts/*.jsonl, 7 rules from workspace/memory/rules.jsonl

## Key Rules

### R1 — Verify-After-Write ist Pflicht
*Status: active | Since: 2026-04-17*



### R32 — Dispatch-Gate Atlas-Sonderfall
*Status: pending | Since: 2026-04-19*



### R37 — Atlas-Orchestrator-Tasks nicht via Auto-Pickup
*Status: resolved | Since: 2026-04-19*

Atlas-Sprint-Tasks als `draft` + `operatorLock=true` anlegen (Auto-Pickup skipped). Operator startet Atlas-Session manuell mit Trigger-Phrase "Lade <Plan> und starte <Sprint>". Atlas liest Board, erkennt `[Atlas-Sprint-*]`-Prefix und orchestriert Sub...

### R39 — Atlas-main braucht Session-Resume-Pattern
*Status: active | Since: 2026-04-19*

Bei Atlas-Orphan-State resumed der Operator oder ein Wrapper-Cron die Session via `openclaw agent --session-id <id> --message "continue orchestration"`. Alternativ: Multi-Sprint-Orchestration auf minions-Subsystem (PR #68718 upstream) migrieren sobal...

### R45 — Sub-Agent-Receipt-Discipline
*Status: active | Since: 2026-04-19*

Sub-Agent MUSS innerhalb 60s nach Task-Pickup taskboard_post_receipt mit receipt=accepted posten. Waehrend Arbeit MUSS mindestens alle 5min oder bei jedem Major-Step ein receipt=progress kommen. Status assigned laenger als 2min ohne Receipt = Contrac...

### R46 — Parallel-Deploy-Serialization
*Status: active | Since: 2026-04-19*

Wenn mehrere Sub-Agents parallel laufen UND jeder einen systemctl --user restart mission-control + curl verify Contract im Prompt hat → Deploy-Race-Condition. Fix: sequenzieller Sprint-Flow ODER Deploy-Queue-Lock (nur ein MC-Restart gleichzeitig, Age...

### R47 — Scope-Lock-auf-Plan-Doc nicht Task-ID
*Status: active | Since: 2026-04-19*

Atlas MUSS vor Sprint-Dispatch das Plan-Doc-Frontmatter lesen. Wenn operatorLock: true — NICHT dispatchen unabhaengig von Task-IDs.

## Key Facts (Top-20 by Importance)

- **[0.85]** `reflective` (2026-04-19T20:34:51 system#5ee1ed4a) — Today's highest-importance facts:   - [0.77] - Mehrere operative Incidents gelöst, am Ende 0 offene Tasks und 0 failed.   - [0.77] **Sub-Plan A Status:** - A1 ✅ `b84ac186` done - A2 ✅ `515b940f` done ...
- **[0.77]** `episodic` (2026-04-18T22:29:09 main#0770974b) — **Sub-Plan A Status:** - A1 ✅ `b84ac186` done - A2 ✅ `515b940f` done - A3 ✅ `f1d6a4d4` done (Incident-Lane nur status=failed) A4 ('Later'→'Archive') und A5 (Dispatched-Metric Zeitfenster) sind nicht a...
- **[0.77]** `episodic` (2026-04-19T06:19:24 main#ea5baca6) — The `atlas-main` session (`agent:main:discord:channel:1486480128576983070`) has `status=failed`, `runtimeMs=0`, `startedAt > endedAt` — it crashed on startup with OOM.
- **[0.66]** `episodic` (2026-04-18T15:20:39 main#3145f347) — Aktuell matched dispatchState=dispatched + nicht active + nicht in-progress -> auch failed/canceled/done als orphaned gemeldet.
- **[0.66]** `episodic` (2026-04-18T15:20:39 main#7ba8af28) — Check C: orphaned NUR wenn dispatchState=dispatched AND execState not in active/queued/review AND status not in in-progress/pending-pickup/review/done/failed/canceled 2.
- **[0.66]** `episodic` (2026-04-18T15:20:39 main#25fc66a2) — Aktuell matched dispatchState=dispatched + nicht active + nicht in-progress -> auch failed/canceled/done als orphaned gemeldet.
- **[0.66]** `episodic` (2026-04-18T15:20:39 main#81acfcc6) — Check C: orphaned NUR wenn dispatchState=dispatched AND execState not in active/queued/review AND status not in in-progress/pending-pickup/review/done/failed/canceled 2.
- **[0.66]** `episodic` (2026-04-18T15:20:39 main#e4f16607) — Aktuell matched dispatchState=dispatched + nicht active + nicht in-progress -> auch failed/canceled/done als orphaned gemeldet.
- **[0.66]** `episodic` (2026-04-18T15:20:39 main#1d2119e8) — Check C: orphaned NUR wenn dispatchState=dispatched AND execState not in active/queued/review AND status not in in-progress/pending-pickup/review/done/failed/canceled 2.
- **[0.66]** `episodic` (2026-04-18T15:20:39 main#00441830) — Aktuell matched dispatchState=dispatched + nicht active + nicht in-progress -> auch failed/canceled/done als orphaned gemeldet.
- **[0.66]** `episodic` (2026-04-18T15:20:39 main#4257d42f) — Check C: orphaned NUR wenn dispatchState=dispatched AND execState not in active/queued/review AND status not in in-progress/pending-pickup/review/done/failed/canceled 2.
- **[0.66]** `episodic` (2026-04-18T15:20:39 main#ea2f3c57) — Aktuell matched dispatchState=dispatched + nicht active + nicht in-progress -> auch failed/canceled/done als orphaned gemeldet.
- **[0.66]** `episodic` (2026-04-18T15:20:39 main#a48697e9) — Check C: orphaned NUR wenn dispatchState=dispatched AND execState not in active/queued/review AND status not in in-progress/pending-pickup/review/done/failed/canceled 2.
- **[0.66]** `episodic` (2026-04-18T19:30:55 main#7cdcfb8e) — ⚠️ Orphaned task auto-failed 090fdc54 [Retry] Sprint C-Backend Security-Gate Receipt Abs Reason: Task in-progress/dispatched 17m ago but no workerSessionId and no receipt/accepted received (threshold=...
- **[0.66]** `episodic` (2026-04-18T19:30:55 main#d489467a) — ⚠️ Orphaned task auto-failed 090fdc54 [Retry] Sprint C-Backend Security-Gate Receipt Abs Reason: Task in-progress/dispatched 17m ago but no workerSessionId and no receipt/accepted received (threshold=...
- **[0.66]** `episodic` (2026-04-18T20:22:22 main#9aeccb08) — BOARD_STATUS: failed TIMESTAMP: 2026-04-18T20:20:04.957Z ⚠️ Orphaned task auto-failed b84ac186 [Wave 1 / A1] FAILED-Counter auf status=failed ums Reason: Task b84ac186 has untracked session (worker:at...
- **[0.66]** `episodic` (2026-04-18T20:22:22 main#8df3ff1d) — Auto-failed by wo ⚠️ Orphaned task auto-failed 7fde1e0e [Atlas-Orchestrate] Task-Tab Plan v2 — 4 Wellen A/ Reason: Task 7fde1e0e has untracked session (agent:main:7fde1e0e-a6ab…) and no active runs ex...
- **[0.66]** `episodic` (2026-04-18T20:22:22 main#8e3dfd39) — BOARD_STATUS: failed TIMESTAMP: 2026-04-18T20:20:04.957Z ⚠️ Orphaned task auto-failed b84ac186 [Wave 1 / A1] FAILED-Counter auf status=failed ums Reason: Task b84ac186 has untracked session (worker:at...
- **[0.66]** `episodic` (2026-04-18T20:22:22 main#3913f9bd) — Auto-failed by wo ⚠️ Orphaned task auto-failed 7fde1e0e [Atlas-Orchestrate] Task-Tab Plan v2 — 4 Wellen A/ Reason: Task 7fde1e0e has untracked session (agent:main:7fde1e0e-a6ab…) and no active runs ex...
- **[0.66]** `episodic` (2026-04-18T21:37:14 main#33989bcd) — BOARD_STATUS: failed TIMESTAMP: 2026-04-18T21:30:06.975Z ⚠️ Orphaned task auto-failed 1d598770 [Naming-P2-C] openclaw.json: displayName Feld pro Reason: Task 1d598770 has untracked session (worker:atl...

## Related KB Articles

- [Atlas Hallucination Prevention](atlas-hallucination-prevention.md)
- [Board Hygiene & Lifecycle](board-hygiene.md)
- [Deploy Contracts & MC-Restart](deploy-contracts.md)
- [Incident Response & RCA](incident-response.md)
- [Receipt Discipline](receipt-discipline.md)
- [Scope Governance & operatorLock](scope-governance.md)
- [Sub-Agent Coordination](sub-agent-coordination.md)

## Metadata

- **Topic keywords** (for future recompilation): atlas, orchestrator, orchestration, dispatch, sprint-, taskboard_create_task, sub-task, sub-agent
- **Related rules (declared)**: R37, R44, R47
- **Schema version**: KB-article v1-mvp

---

*Auto-compiled from 27 facts + 7 rules by `kb-compiler.py@v1-mvp`. Manual edits will be preserved where possible but may be overwritten on next compile — use `<!-- manual: start --> ... <!-- manual: end -->` to mark preserved sections (future feature).*