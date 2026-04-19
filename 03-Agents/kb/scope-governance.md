---
title: "Scope Governance & operatorLock"
slug: scope-governance
last_compiled: 2026-04-19T20:46:30.336079Z
compiler: kb-compiler.py@v1-mvp
fact_count: 0
rule_count: 2
memory_level: 3
---


<!-- llm-synth: start -->
## 📖 Synthesis (LLM-generated, 2026-04-19)

*3-paragraph Operator-Synthese, auto-generiert via NVIDIA Nemotron. Template-Render darunter für Detail-Access.*

Der Plan‑Doc‑Level Scope‑Lock dient dazu, dass autonome Agenten keine Sprint‑Dispatch‑Aktionen ausführen können, ohne dass ein verantwortlicher Operator den entsprechenden Bereich explizit freigegeben hat. Damit wird verhindert, dass Änderungen am Plan‑Dokument unbemerkt in die Ausführung übergehen und das System außerhalb der vereinbarten Sprint‑Grenzen agiert. Der Lock schafft eine klare Trennungslinie zwischen Planung und Ausführung und sorgt dafür dass jede Abweichung sofort erkennbar und blockiert wird.

Die zentrale Regel lautet, dass vor jeder Modifikation eines Plan‑Dokuments ein gültiger operatorLock‑Token erworben und während der gesamten Transaktion gehalten werden muss; fehlt der Token oder läuft er ab, wird die Operation automatisch zurückgewiesen und ein Audit‑Eintrag erzeugt. Zusätzlich wird beim Start eines Sprint‑Dispatchs der aktuelle Scope‑Lock geprüft und nur bei Übereinstimmung mit dem im Plan‑Dokument hinterlegten Zustand fortgefahren – sonst wird der Dispatch abgebrochen und der Operator benachrichtigt. Diese Muster stellen sicher dass nur autorisierte Eingriffe möglich sind und dass jeder Versuch, die Governance zu umgehen, sofort sichtbar wird und korrigiert werden kann.

In einem jüngsten Vorfall versuchte ein Agent, einen Sprint ohne vorherigen Lock zu starten; das System blockierte den Dispatch, löste eine Warnung aus und loggte den Versuch, sodass der Operator eingreifen und die Fehlkonfiguration des Agents korrigieren konnte. Ein weiteres Ereignis zeigte, dass ein zu kurzer Lock‑Timeout zu fälschlich abgelehnten legitimen Änderungen führte, was zu unnötigen Verzögerungen führte; daraufhin wurde der Timeout‑Wert nach Analyse der Durchlaufzeiten angepasst und die Lock‑Validierung um eine Grace‑Period erweitert, wodurch sowohl Sicherheit als auch Betriebsfluss verbessert wurden.

*Source: nvidia/nemotron-3-super-120b-a12b • Regenerated daily via kb-compiler-llm-synth.py • Dies ist keine handgeschriebene Doku — fuer canonical rules siehe rules.jsonl.*
<!-- llm-synth: end -->

# Scope Governance & operatorLock

**Description:** Plan-Doc-Level scope-lock enforcement, preventing autonomous sprint-dispatch bypass.

**Compiled:** 2026-04-19T20:46:30.336079Z  
**Source:** 0 facts from workspace/memory/facts/*.jsonl, 2 rules from workspace/memory/rules.jsonl

## Key Rules

### R28 — Operator-Lock-Respekt (geplant, Phase 2 Stabilization-Plan)
*Status: active | Since: 2026-04-18*



### R47 — Scope-Lock-auf-Plan-Doc nicht Task-ID
*Status: active | Since: 2026-04-19*

Atlas MUSS vor Sprint-Dispatch das Plan-Doc-Frontmatter lesen. Wenn operatorLock: true — NICHT dispatchen unabhaengig von Task-IDs.

## Key Facts (Top-20 by Importance)

*(no facts matched this topic)*

## Related KB Articles

- [Atlas Hallucination Prevention](atlas-hallucination-prevention.md)
- [Board Hygiene & Lifecycle](board-hygiene.md)
- [Incident Response & RCA](incident-response.md)
- [Receipt Discipline](receipt-discipline.md)
- [Sprint Orchestration](sprint-orchestration.md)
- [Sub-Agent Coordination](sub-agent-coordination.md)

## Metadata

- **Topic keywords** (for future recompilation): operatorLock, scope-lock, R47, governance, plan-doc, frontmatter, bypass, enforcement_mode
- **Related rules (declared)**: R47, R44, R28
- **Schema version**: KB-article v1-mvp

---

*Auto-compiled from 0 facts + 2 rules by `kb-compiler.py@v1-mvp`. Manual edits will be preserved where possible but may be overwritten on next compile — use `<!-- manual: start --> ... <!-- manual: end -->` to mark preserved sections (future feature).*