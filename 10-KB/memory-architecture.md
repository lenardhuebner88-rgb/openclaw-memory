---
title: "Memory Architecture"
slug: memory-architecture
last_compiled: 2026-05-01T17:30:17.177192Z
compiler: kb-compiler.py@v1-mvp
fact_count: 16
rule_count: 2
memory_level: 3
---

# Memory Architecture

**Description:** Multi-level memory-stack: QMD retrieval (L1), Mem0-facts + Dreaming (L2), Schema-v2 taxonomy + reflection.

**Compiled:** 2026-05-01T17:30:17.177192Z  
**Source:** 16 facts from workspace/memory/facts/*.jsonl, 2 rules from workspace/memory/rules.jsonl

## Key Rules

### R36 — Agent-Session-File-Size-Creep
*Status: pending | Since: 2026-04-19*



### R41 — Memory-Retrieval: QMD vor File-Read
*Status: active | Since: 2026-04-19*

Für Konzept-Suche ("was haben wir über X dokumentiert?") → `qmd_query` verwenden, nicht brute-force File-Read. Für bekannten Pfad bleibt `read_file` Standard. Session-Transcripts sind NICHT indexiert (privacy + noise-reduction).

## Key Facts (Top-20 by Importance)

- **[0.90]** `procedural` (2026-04-19T21:35:11 system#1f4f56a6) — Pre-Flight-Sprint-Dispatch Script deployed 2026-04-19 20:42 UTC mit 7 Gates: Atlas-session-size R36, operatorLock R47, Board-open_count, MC+Gateway-health, R49-Validator-CRITICAL, Git-dirty-state, Fre...
- **[0.85]** `procedural` (2026-04-19T21:35:11 system#ffb386a3) — Memory Schema v2 Migration 2026-04-19 20:34 UTC: 252 facts upgraded mit memory_type (episodic/semantic/procedural/reflective), importance 0-1, decay_half_life_days, Graphiti-temporal-windows (valid_fr...
- **[0.85]** `semantic` (2026-04-19T21:35:11 system#967225ab) — Defense-Stack Pattern 2026-04-19: 12 automated cron-layers active für governance + memory + monitoring: session-freeze-watcher */5, r49-claim-validator */15, r48-board-hygiene hourly, daily-reflection...
- **[0.66]** `reflective` (2026-04-19T20:34:51 system#5ee1ed4a) — Today's highest-importance facts:   - [0.77] - Mehrere operative Incidents gelöst, am Ende 0 offene Tasks und 0 failed.   - [0.77] **Sub-Plan A Status:** - A1 ✅ `b84ac186` done - A2 ✅ `515b940f` done ...
- **[0.66]** `reflective` (2026-04-19T21:50:01 system#5ee1ed4a) — Today's highest-importance facts:   - [1.00] R49 Atlas Anti-Hallucination Claim-Verify-Before-Report deployed 2026-04-19 20:3   - [0.95] R45 Sub-Agent-Receipt-Discipline deployed 2026-04-19 17:20 UTC ...
- **[0.55]** `episodic` (2026-04-19T21:35:11 system#26e954cf) — Sprint-L Memory-Level-3 MVPs deployed 2026-04-19 20:00-21:30 UTC: L1 KB-Compiler 10 articles, L2 Graph-Edges 1024 edges, L3 Retrieval-Feedback hourly, L4 Per-Agent-Scoping 257 facts migrated, L5 Budge...
- **[0.51]** `episodic` (2026-04-19T21:35:11 system#5f8f0efe) — Memory-Budget-Meter first real CRITICAL caught 2026-04-19 21:20 UTC: Atlas-session 48f8d0f0 explodierte auf 373% (559k tokens / 150k budget) während Forge Sprint-G/H Consolidation-Task. Vorheriger che...
- **[0.51]** `procedural` (2026-04-19T21:35:11 system#098d7a25) — Cron-Audit 2026-04-19 23:00 UTC: 51 aktive Schedules über 3 Scheduler fragmentiert (34 crontab + 6 systemd-timer + 16 openclaw-cron). 0 active errors, historische nur aus Sprint-E MC-Flap 17:00-17:32....
- **[0.46]** `procedural` (2026-04-19T21:35:11 system#8bb6b4eb) — Sprint-K H10 Cron-Inventory-Consolidation + Observability formally added 2026-04-19 23:15 UTC. 5 Layers: L1 Cleanup (DONE), L2 Memory-Orchestrator (1-2h), L3 Systemd-Migration 3 crons (2h), L4 Healthc...
- **[0.42]** `semantic` (2026-04-19T21:35:11 system#1db9c9d9) — 10 Karpathy-KB-Articles compiled 2026-04-19 20:46 UTC in vault/03-Agents/kb/: sprint-orchestration (27f/7r), receipt-discipline (34f/4r), deploy-contracts (12f/3r), atlas-hallucination-prevention (0f/...
- **[0.42]** `semantic` (2026-04-19T21:35:11 system#ba5eb42d) — Memory-Graph 1024 typed edges inferred 2026-04-19 20:47 UTC aus 257 facts: 720 related-to (shared-rule or token-overlap), 241 precedes (temporal same-agent <1h), 63 supersedes (keyword-pattern). graph...
- **[0.39]** `episodic` (2026-04-19T21:35:11 system#258f56ec) — Sprint-G/H Consolidation 2026-04-19 21:16-21:18 UTC (Forge 5a10491a): 4 commits konsolidierten Sprint-G/H autonomous-cascade Arbeit: b941b36 (.bak removes), 5fac96a (sprint-g ops-dashboard), daee0c7 (...
- **[0.38]** `reflective` (2026-04-19T21:50:01 system#8f90370d) — Memory-Type split: {'episodic': 259, 'semantic': 4, 'procedural': 14}
- **[0.37]** `reflective` (2026-04-19T20:34:51 system#8f90370d) — Memory-Type split: {'episodic': 251, 'semantic': 1}
- **[0.17]** `episodic` (2026-04-19T13:54:51 main#80bee875) — This will be cleaner and less error-prone than building a Python script to wrap the openclaw CLI calling the QMD MCP server.
- **[0.15]** `episodic` (2026-04-19T06:16:41 main#6ea41111) — System: Reason: MC degraded (cost anomaly + stale in-memory store).

## Related KB Articles

*(no related articles found)*

## Metadata

- **Topic keywords** (for future recompilation): qmd, memory, facts.jsonl, rules.jsonl, dreaming, consolidation, mem0, graphiti...
- **Related rules (declared)**: R41, R36
- **Schema version**: KB-article v1-mvp

---

*Auto-compiled from 16 facts + 2 rules by `kb-compiler.py@v1-mvp`. Manual edits will be preserved where possible but may be overwritten on next compile — use `<!-- manual: start --> ... <!-- manual: end -->` to mark preserved sections (future feature).*