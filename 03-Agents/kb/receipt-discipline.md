---
title: "Receipt Discipline"
slug: receipt-discipline
last_compiled: 2026-04-19T20:46:30.335402Z
compiler: kb-compiler.py@v1-mvp
fact_count: 34
rule_count: 4
memory_level: 3
---


<!-- llm-synth: start -->
## 📖 Synthesis (LLM-generated, 2026-04-19)

*3-paragraph Operator-Synthese, auto-generiert via NVIDIA Nemotron. Template-Render darunter für Detail-Access.*

Der Kern der Receipt‑Disziplin besteht darin, dass jede Aufgabe im Mission‑Control‑System einen klar definierten Lebenslauf von accepted über progress bis hin zu result durchläuft und dass dieses Muster zuverlässig überwacht wird. Damit werden Situationen vermieden, in denen Aufgaben unbemerkt im System hängen bleiben, weil kein Empfangs‑ oder Fortschrittsbeleg mehr eingeht. Durch das konsequente Einhalten dieses Musters erhalten Operator*innen eine frühzeitige Warnung bei Stillstand und können eingreifen, bevor Arbeit verloren geht oder die Gesamtleistung des Orchestriers leidet.

Die wichtigsten Regeln, die dieses Verhalten sicherstellen, sind zunächst das **accepted‑progress‑result‑Muster**: ein Worker muss unmittelbar nach dem Aufnehmen einer Aufgabe ein accepted‑Receipt senden, während der Ausführung periodisch progress‑Receipts (alle paar Minuten) und nach Abschluss ein result‑Receipt. Zweitens gilt die **Stall‑Detection‑Regel** (R45): bei fehlendem progress‑Receipt für länger als die konfigurierte Schwelle (z. B. 17 Minuten) wird die Aufgabe automatisch als failed markiert und ein orphaned‑Flag gesetzt. Drittens gibt es die **Orphaned‑Task‑Prüfung (Check C)**, die eine Aufgabe als verwaiste kennzeichnet, wenn ihr dispatchState auf dispatched steht, ihr execState nicht zu active, queued oder review gehört und ihr status nicht zu den erlaubten Zuständen in‑progress, pending‑pickup, review, done, failed oder canceled gehört. Diese Regeln verhindern, dass Aufgaben unbemerkt im System verbleiben, indem sie klare Bedingungen für das Fehlen notwendiger Receipts definieren und automatisierte Eskalationsschritte auslösen.

Aus jüngsten Vorfällen lässt sich ableiten, dass das fehlende workerSessionId gleichzeitig mit dem Ausbleiben eines accepted‑Receipts zum schnellen Auslösen der Stall‑Detection führte – etwa bei Aufgabe 090fdc54, die nach 17 Minuten ohne Fortschrittsbeleg automatisch als failed markiert und als orphaned gemeldet wurde. Ein weiteres Ereignis zeigte, dass selbst Aufgaben, die bereits in den Zuständen failed oder c

*Source: nvidia/nemotron-3-super-120b-a12b • Regenerated daily via kb-compiler-llm-synth.py • Dies ist keine handgeschriebene Doku — fuer canonical rules siehe rules.jsonl.*
<!-- llm-synth: end -->

# Receipt Discipline

**Description:** Sub-Agent Receipt-Lifecycle — accepted/progress/result pattern, stall-detection, R45 enforcement.

**Compiled:** 2026-04-19T20:46:30.335402Z  
**Source:** 34 facts from workspace/memory/facts/*.jsonl, 4 rules from workspace/memory/rules.jsonl

## Key Rules

### R22 — Task ohne Result-Receipt ≠ erfolgsfrei
*Status: resolved | Since: 2026-04-18*



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
- **[0.66]** `episodic` (2026-04-18T19:30:55 main#7cdcfb8e) — ⚠️ Orphaned task auto-failed 090fdc54 [Retry] Sprint C-Backend Security-Gate Receipt Abs Reason: Task in-progress/dispatched 17m ago but no workerSessionId and no receipt/accepted received (threshold=...
- **[0.66]** `episodic` (2026-04-18T19:30:55 main#d489467a) — ⚠️ Orphaned task auto-failed 090fdc54 [Retry] Sprint C-Backend Security-Gate Receipt Abs Reason: Task in-progress/dispatched 17m ago but no workerSessionId and no receipt/accepted received (threshold=...
- **[0.66]** `episodic` (2026-04-18T19:04:14 main#755ff0a3) — Description should include Board counts (open/assigned, in-progress, pending-pickup, failed, review), V-Closure states, T1/T3/T2 status, blockers, and next 30min.
- **[0.66]** `episodic` (2026-04-18T19:30:55 main#541c1234) — BOARD_STATUS: failed TIMESTAMP: 2026-04-18T19:30:03.587Z ⚠️ Progress timeout, task stalled 090fdc54 [Retry] Sprint C-Backend Security-Gate Receipt Abschluss Reason: No progress receipt for 17m (thresh...
- **[0.66]** `episodic` (2026-04-18T19:30:55 main#77c4d4b2) — BOARD_STATUS: failed TIMESTAMP: 2026-04-18T19:30:03.587Z ⚠️ Progress timeout, task stalled 090fdc54 [Retry] Sprint C-Backend Security-Gate Receipt Abschluss Reason: No progress receipt for 17m (thresh...
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
- **[0.66]** `episodic` (2026-04-18T19:58:52 sre-expert#744da69d) — - Währenddessen wurde der Task einmal extern auf `failed` gezogen (ghost-fail vom Monitor), ich habe per `recovery-action: retry` wieder aufgenommen, danach erneut `accepted` + final `result`.
- **[0.66]** `episodic` (2026-04-18T19:58:52 sre-expert#8b7de057) — - Währenddessen wurde der Task einmal extern auf `failed` gezogen (ghost-fail vom Monitor), ich habe per `recovery-action: retry` wieder aufgenommen, danach erneut `accepted` + final `result`.
- **[0.66]** `episodic` (2026-04-18T19:58:52 sre-expert#1bb1d33d) — - Währenddessen wurde der Task einmal extern auf `failed` gezogen (ghost-fail vom Monitor), ich habe per `recovery-action: retry` wieder aufgenommen, danach erneut `accepted` + final `result`.

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

*Auto-compiled from 34 facts + 4 rules by `kb-compiler.py@v1-mvp`. Manual edits will be preserved where possible but may be overwritten on next compile — use `<!-- manual: start --> ... <!-- manual: end -->` to mark preserved sections (future feature).*