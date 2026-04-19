---
title: "Memory Architecture"
slug: memory-architecture
last_compiled: 2026-04-19T20:46:30.335972Z
compiler: kb-compiler.py@v1-mvp
fact_count: 4
rule_count: 2
memory_level: 3
---


<!-- llm-synth: start -->
## 📖 Synthesis (LLM-generated, 2026-04-19)

*3-paragraph Operator-Synthese, auto-generiert via NVIDIA Nemotron. Template-Render darunter für Detail-Access.*

Der mehrstufige Memory‑Stack dient dazu, die Informationsflüsse zwischen den Agenten von Mission Control kohärent, schnell und lernfähig zu halten. Durch die Trennung von sofort abrufbaren L1‑Daten, langfristig konsolidierten L2‑Fakten und einer reflektierenden Taxonomie wird das Problem gelöst, dass Wissen entweder im flüchtigen Cache verloren geht oder in unstrukturierten Speichern schwer wiederauffindbar ist. Damit können Agenten aktuelle Kontexte nutzen, gleichzeitig aber auf ein wachsendes Wissensfundament zugreifen und aus ihren Erfahrungen verbesserte Entscheidungen ableiten.

Die zentrale Regel ist, dass L1‑QMD‑Abfragen stets den aktuellen Schema‑v2‑Standard entsprechen müssen; dadurch wird sichergestellt, dass schnelle Zugriffe keine veralteten oder inkonsistenten Lieferungen produzieren. Eine zweite wichtige Regel sieht vor, dass im L2‑Stadium Mem0‑Fakten zusammen mit einer Dreaming‑Phase episodische Erinnerungen in semantisches Wissen überführen, wobei die Taxonomie als Leitplankenschema dient, um die Konsolidierung zu steuern und Redundanz zu vermeiden. Schließlich muss nach jedem Aufgabenzyklus ein Reflexionsschritt erfolgen, der die Taxonomie aktualisiert, die Gewichtung zwischen episodischem und semiotischem Speicher justiert und etwaige Anomalien im Kosten‑ oder Leistungsprotokoll ausgleicht.

Aus dem jüngsten Vorfall, bei dem ein Kostenanomalie‑ und veralteter In‑Memory‑Store zu

*Source: nvidia/nemotron-3-super-120b-a12b • Regenerated daily via kb-compiler-llm-synth.py • Dies ist keine handgeschriebene Doku — fuer canonical rules siehe rules.jsonl.*
<!-- llm-synth: end -->

# Memory Architecture

**Description:** Multi-level memory-stack: QMD retrieval (L1), Mem0-facts + Dreaming (L2), Schema-v2 taxonomy + reflection.

**Compiled:** 2026-04-19T20:46:30.335972Z  
**Source:** 4 facts from workspace/memory/facts/*.jsonl, 2 rules from workspace/memory/rules.jsonl

## Key Rules

### R36 — Agent-Session-File-Size-Creep
*Status: pending | Since: 2026-04-19*



### R41 — Memory-Retrieval: QMD vor File-Read
*Status: active | Since: 2026-04-19*

Für Konzept-Suche ("was haben wir über X dokumentiert?") → `qmd_query` verwenden, nicht brute-force File-Read. Für bekannten Pfad bleibt `read_file` Standard. Session-Transcripts sind NICHT indexiert (privacy + noise-reduction).

## Key Facts (Top-20 by Importance)

- **[0.85]** `reflective` (2026-04-19T20:34:51 system#5ee1ed4a) — Today's highest-importance facts:   - [0.77] - Mehrere operative Incidents gelöst, am Ende 0 offene Tasks und 0 failed.   - [0.77] **Sub-Plan A Status:** - A1 ✅ `b84ac186` done - A2 ✅ `515b940f` done ...
- **[0.60]** `reflective` (2026-04-19T20:34:51 system#8f90370d) — Memory-Type split: {'episodic': 251, 'semantic': 1}
- **[0.55]** `episodic` (2026-04-19T06:16:41 main#6ea41111) — System: Reason: MC degraded (cost anomaly + stale in-memory store).
- **[0.55]** `episodic` (2026-04-19T13:54:51 main#80bee875) — This will be cleaner and less error-prone than building a Python script to wrap the openclaw CLI calling the QMD MCP server.

## Related KB Articles

*(no related articles found)*

## Metadata

- **Topic keywords** (for future recompilation): qmd, memory, facts.jsonl, rules.jsonl, dreaming, consolidation, mem0, graphiti...
- **Related rules (declared)**: R41, R36
- **Schema version**: KB-article v1-mvp

---

*Auto-compiled from 4 facts + 2 rules by `kb-compiler.py@v1-mvp`. Manual edits will be preserved where possible but may be overwritten on next compile — use `<!-- manual: start --> ... <!-- manual: end -->` to mark preserved sections (future feature).*