---
title: Sprint-L Memory Level-3 — Knowledge-Base Compilation + Graph-Edges + Retrieval-Feedback
date: 2026-04-19 20:35 UTC
status: planned
type: sprint-plan
trigger_suggestion: "Atlas Sprint-L Memory-KB starten"
estimated_effort: 10-14h orchestriert
prerequisites: Sprint-K done (Infra-Hardening stable), Phase-1+2 Memory-Evolution deployed (schema v2 + reflection-cron)
---

# Sprint-L Memory Level-3 — KB-Compilation + Graph-Edges + Retrieval-Feedback

## Context & Why

**Bereits deployed (Memory-Stack 2026-04-19):**
- ✅ **L1:** QMD hybrid retrieval (BM25+vector+LLM-rerank) auf 3 Collections, 720 files, 2784 vectors
- ✅ **L2:** Mem0-style fact-extraction (daily .jsonl) + Dreaming 3-phase (light/deep/rem) consolidation cron
- ✅ **Schema v2:** Memory-Type Taxonomy (episodic/semantic/procedural/reflective) + Importance-Scoring + Ebbinghaus-Decay + Graphiti-style Temporal-Validity-Windows + Cross-Ref Fields
- ✅ **Reflection-Cron:** Daily end-of-day reflective-memory-generator

**Missing gegenüber best-class 2026 (github/openclaw research):**
1. **Cross-Referenced Knowledge Articles** (Karpathy-KB Pattern via `claude-memory-compiler`) — strukturierte Topic-Artikel aus daily transcripts extrahiert, cross-referenced, versioniert
2. **Memory Graph Edges** (Graphiti/Zep) — Facts als Knowledge-Graph-Nodes mit typed edges (caused-by, supersedes, related-to, precedes)
3. **Retrieval-Feedback-Loop** — tracking welche QMD-Results der Agent tatsächlich nutzt → reinforcement für access_count + importance-recalc
4. **Per-Agent Memory-Scoping** — heute shared-workspace-memory, best-class = per-agent-archival + shared-semantic
5. **Memory-Budget-per-Session** (Letta pattern) — Context-Overflow R36 zeigte Gap; Atlas soll vorbereitend rotieren statt silent fail

## Scope

6 Subs die Memory von Level-2 auf Level-3 heben. 

### Sub-L1: Karpathy-KB-Compiler (4h, Forge + James 30min)
**Agent:** James-Research 30min → Forge-Implementation 3.5h  
**Scope:**
- **James:** Claude-memory-compiler (github.com/coleam00/claude-memory-compiler) Deep-Review + Karpathy LLM Knowledge Base article methodology. Output: `vault/03-Agents/james-kb-compilation-research-2026-04-19.md`
- **Forge:** `workspace/scripts/kb-compiler.py` — reads last 7 days of facts.jsonl + session-logs, clusters by topic-keywords (e.g., "Sprint-Dispatching", "Agent-Context-Management", "Board-Lifecycle", "R45-Receipt-Drift"), produces one cross-referenced markdown-article per topic in `vault/10-KB/<topic>.md`
- Each article: Overview + Key-Rules (cross-ref rules.jsonl) + Key-Cases (cross-ref facts.jsonl) + Related-Articles (cross-ref each other) + Versioning (timestamp, schema_version)
- Cron: `0 4 * * *` (after Dreaming at 03:00)

**Acceptance:**
- ≥8 KB-articles produced on first run (Sprint-Dispatching, Receipt-Discipline, Atlas-Orchestration, Board-Hygiene, Deploy-Contracts, Memory-Architecture, Incident-Response, Rule-Enforcement)
- Each article has ≥3 rule-crossrefs + ≥5 fact-crossrefs
- QMD re-indexing catches them as searchable
- Test query "wie lauten die receipt-rules?" returns kb-article not raw-facts

### Sub-L2: Memory-Graph-Edges (3h, Forge)
**Agent:** Forge  
**Scope:**
- Extend facts.jsonl schema v2→v3 with `edges: [{target_id, type, weight}]` — typed directed edges between facts
- Edge-Types: `caused-by` (incident X caused Y), `supersedes` (fact Y replaces fact X), `related-to` (weak-link), `precedes` (temporal), `implements` (fact implements rule)
- Script `workspace/scripts/graph-edge-builder.py` — post-hoc inference from existing facts (keyword-matching + temporal-proximity)
- Query-Tool `workspace/scripts/graph-query.py` — traverse edges for retrieval ("show all facts caused-by R45 violation")

**Acceptance:**
- ≥100 edges inferred from existing 252+ facts
- Graph-query works: `graph-query.py --target R45 --edge caused-by` returns matching facts
- Export to Mermaid-Graph format for visualization

### Sub-L3: Retrieval-Feedback-Loop (2h, Forge)
**Agent:** Forge  
**Scope:**
- MCP-wrapper for `qmd_query` / `qmd_search` logs which results were actually used (heuristic: agent continues to cite/quote within next N messages)
- Reinforce `access_count` + `last_accessed` per fact when retrieval → usage
- Recompute `importance` weekly via cron (facts with high access_count climb)
- Optional: add `retrieval_score` feedback per query-result pair → future RAG-tuning

**Acceptance:**
- Retrieval-log: `workspace/memory/retrieval-feedback.jsonl` grows organically
- Weekly importance-recalc visibly lifts frequently-accessed facts
- Dashboard query on "top-10-most-accessed facts this week" returns meaningful list

### Sub-L4: Per-Agent Memory-Scoping (2h, Forge)
**Agent:** Forge  
**Scope:**
- Extend `facts.jsonl` schema `agent` field handling → QMD-Collection per agent OR virtual-view via jq
- Agent-Config addition: `agents.list.<agent>.memory.archival_scope = ["self", "shared"]` — by default Atlas sees everything, Pixel sees only Pixel+shared
- Purpose: Pixel doesn't need to know Forge's sre-Internals; reduces context-noise on sub-agent dispatch

**Acceptance:**
- `qmd_query --agent frontend-guru` returns only Pixel-scoped + shared facts
- Atlas retains cross-agent visibility (default)
- Context-size reduction measurable on sub-agent dispatch (est. 20-30% token-reduction)

### Sub-L5: Memory-Budget-Meter + Proactive-Rotation (2h, Forge)
**Agent:** Forge  
**Scope:**
- Atlas-Session-Size-Monitor: parse session-jsonl live, count tokens (estimate via word-count × 1.3)
- Threshold `MEMORY_BUDGET = 150k tokens`
- At 70% (105k): emit Discord-Warning + instruct Atlas to prepare rotation (save state-snapshot + re-prompt Plan-Doc)
- At 90% (135k): force-rotation (suspend session, start fresh, inject compressed-state-snapshot)
- Target: prevent today's 2026-04-19 19:42 UTC silent-rotation → Hallucination-Cascade (R36 → R49)

**Acceptance:**
- Warning + Forced-Rotation triggered in test-scenario (simulated oversize-session)
- Discord-Alert + Audit-Log entries
- Atlas post-rotation gets state-snapshot in new session (plan-doc path, last-commit, last-task-id)

### Sub-L6: KB + Memory Documentation Portal (1-2h, Pixel)
**Agent:** Pixel  
**Scope:**
- New MC-Route `/memory` — visualizes current memory-stack-state
- Tabs:
  - **Rules** (46, filterable by category)
  - **Facts Today** (live-counter + memory-type-breakdown)
  - **KB Articles** (list from `vault/10-KB/*.md` with last-updated + cross-ref-count)
  - **Graph** (Mermaid-render of recent edges)
  - **Retrieval-Feedback** (top-10 most-accessed, decay-curves)

**Acceptance:**
- Route live, all 5 tabs functional, mobile-responsive (R45 Sprint-I compliant)
- Data-source: server-side API `/api/memory/state` aggregates from facts.jsonl + rules.jsonl + kb/ + retrieval-feedback

## 🔗 Dependencies

```
Sprint-K done ──┐
                ├──> L1 + L2 parallel (disjoint scope)
                ├──> L3 + L4 parallel (after L2 edges exist)
                ├──> L5 (no deps)
                └──> L6 last (visualizes all above)
```

## 🤖 Atlas-Dispatch-Prompt (ready-to-fire)

```
REAL_TASK=true ORCHESTRATOR_MODE=true. Sprint-L Memory-KB Level-3 — NICHT heartbeat.

Kontext:
Memory-Stack deployed bis Level-2 (QMD + Mem0-facts + Dreaming + Schema-v2 + Reflection-Cron).
Research 2026-04-19 zeigte Best-Class Gap: Karpathy-KB-Compilation (claude-memory-compiler), Graphiti-Edges (Zep), Retrieval-Feedback, Per-Agent-Scoping, Letta-Memory-Budget. Sprint-L schließt diese zu Level-3.

Plan-Doku: /home/piet/vault/03-Agents/sprint-l-memory-kb-compilation-plan-2026-04-19.md
(qmd deep_search "sprint-l memory kb")

6 Sub-Tasks:
- Sub-L1 (James 30min → Forge 3.5h): Karpathy-KB-Compiler — cross-ref articles from facts+sessions
- Sub-L2 (Forge 3h): Memory-Graph-Edges + graph-query tool
- Sub-L3 (Forge 2h): Retrieval-Feedback-Loop + weekly importance-recalc
- Sub-L4 (Forge 2h): Per-Agent Memory-Scoping (archival + shared)
- Sub-L5 (Forge 2h): Memory-Budget-Meter + Atlas Proactive-Rotation (prevents R36+R49)
- Sub-L6 (Pixel 1-2h): /memory MC-Route Visualization

Playbook:
1. qmd deep_search "sprint-l memory kb"
2. Pre-Reference: qmd deep_search "memory level up" + "claude-memory-compiler" + "graphiti temporal"
3. POST 6 Board-Tasks via taskboard_create_task (R44 PFLICHT!)
4. Dispatch-Order:
   - Batch 1 parallel: L1 (James first, dann Forge) + L2 (Forge) + L5 (Forge) — Forge WIP-Limit 2-3
   - Batch 2 after L2 done: L3 + L4 parallel
   - Batch 3 final: L6 (Pixel)

Constraints:
- R45/R46/R47/R48/R49 compliance (auto via AGENTS.md Preamble)
- R49 especially: jede "done"-Claim inline verify
- Keine Schema-Breaking-Changes auf facts.jsonl v2 (nur additiv erweitern zu v3)
- Keine MC-Downtime > 2min bei L6 Deploy (mc-restart-safe nutzen)

Anti-Scope:
- Keine neuen Sprint-Patterns
- Keine LLM-Fine-Tuning (out-of-scope)
- Keine Migration auf externe Memory-SaaS (Mem0 Cloud etc.)

Zeit-Budget: 10-14h orchestriert.

Return format:
- EXECUTION_STATUS
- RESULT_SUMMARY:
  - 6 Board-Task-IDs + Final-Status (R49 compliant)
  - Report-Paths (James-Research + jeder Sub) ls-verified
  - ≥8 KB-Articles live in vault/10-KB/
  - ≥100 Graph-Edges inferred + query-testable
  - /memory Route mobile-live
  - Git-Commits-Liste

Los.
```

## 📝 Signoff

Operator (pieter_pan) 2026-04-19 [TIMESTAMP]: ready-to-dispatch after Sprint-K.  
Assistant (Claude) 2026-04-19 20:35 UTC: based on web-research (Mem0/Zep/Letta/OpenMemory/claude-memory-compiler).

---

**Nach Sprint-L:** Memory-Stack ist State-of-the-Art 2026, auf Niveau mit Mem0+Zep+Letta-Hybrid.
