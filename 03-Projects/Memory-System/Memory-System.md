---
title: Memory-System
type: project
status: active
started: 2026-04-09
owner: { architect: Atlas + Operator, research: James, impl: Forge, compiler: L1-cron }
tags: [type/project, status/active, topic/memory-system]
---

# Memory-System

> Tiered Memory-Architektur für den Multi-Agent-Stack. L1-KB bis L6-Dashboard, cron-backed.

## TL;DR

Memory-System ist die Infrastruktur für persistentes + kompiliertes Gedächtnis aller Agents. Tiered: raw events → compiled KB → graph-edges → retrieval-feedback → budget-meter → dashboard. Läuft cron-basiert (6 Layer), schreibt in `/home/piet/.openclaw/workspace/memory/` (live-data) und `/home/piet/vault/10-KB/` (compiled read-only).

## Architektur (Memory-Levels)

| Level | Zweck | Location | Cron |
|-------|-------|----------|------|
| **L0** | Raw agent scratch, learnings | `_agents/*/working-context.md`, `learnings.md` | live |
| **L1** | KB-Compiler (Karpathy-Pattern) | `vault/10-KB/*.md` (10 cross-ref articles) | `0 4 * * *` |
| **L2** | Memory-Graph-Edges (1279 edges) | `~/.openclaw/workspace/memory/graph.jsonl` | `15 4 * * *` |
| **L3** | Retrieval-Feedback-Loop | `~/.openclaw/workspace/memory/retrieval-feedback.jsonl` | `30 */1 * * *` |
| **L5** | Memory-Budget-Meter | `~/.openclaw/workspace/memory/memory-budget.log` | `*/5 * * * *` |
| **L6-Lite** | Auto-Dashboard | `vault/_agents/memory-dashboard.md` | `30 4 * * *` |

*L4 war geplant aber in MVP-Scope entfallen.*

## Aktueller Stand

- ✅ L1 live: 10 KB-Artikel in `10-KB/` (atlas-hallucination-prevention, board-hygiene, build-deploy-regeln, deploy-contracts, incident-response, memory-architecture, receipt-discipline, scope-governance, sprint-orchestration, sub-agent-coordination)
- ✅ L2 live: 1279 Graph-Edges, Query via `graph-query.py`
- ✅ L3 live (aber dünne Signalbasis — ~5 Events/Woche, Erweiterung in P2.7)
- ✅ L5 + L6-Lite live
- ⚠️ Signal-Qualität: L3 unterfüttert. Session 7c136829 (main-Discord-Bot) bei 265% L5-Budget (monitored, nicht kritisch da live)

## Sub-Documents

| File | Inhalt |
|------|--------|
| [[MEMORY]] | System-MEMORY (Result-Routing + KB + Ops-Regeln, 9.5 KB) |
| [[MEMORY-SYSTEM-AUDIT-2026-04-09]] | Initial Audit Report (James) — inventarisiert alle Memory-Dateien |
| [[CONTEXT-MANAGEMENT-SPEC]] | Komplett-Redesign-Spec 2026-04-09 (Hybrid + Tiered-Memory) |
| [[CONTEXT-MANAGEMENT-PLAN]] | Implementation-Plan (Loading-Chains, Tier 0-4, Consolidation) |
| [[CONTEXT-MANAGEMENT-RESULTS-2026-04-09]] | Ergebnisse des ersten Redesign-Runs |
| [[board-memory-analyse-2026-04-09]] | Kombinierte Board+Memory-Analyse |
| [[learnings]] | L0 Learnings-Log (chronologisch, `[date] [category] ...`-Format) |
| [[Memory-System]] | Diese MOC |

## Aktive Workstreams

- [[04-Sprints/s-ctx-p0-2026-04-22|S-CTX-P0]] — Context-Efficiency Baseline + API-Features
- [[04-Sprints/sprint-ce-context-efficiency-2026-04-21|Sprint-CE]] — Quelle von S-CTX-P0
- [[04-Sprints/s-infra-2026-04-22|S-INFRA]] — Infrastructure
- [[04-Sprints/sprint-l-memory-kb-compilation-plan-2026-04-19|Sprint-L]] — Memory-KB-Compilation (MVPs ✅, Deep via L1-Finalize)
- [[04-Sprints/sprint-m-audit-integrity-scheduler-consolidation-plan-2026-04-20-v1.2.1|Sprint-M v1.2.1]] — Scheduler-Consolidation

## Key References

- **Memory-Architecture (KB):** [[10-KB/memory-architecture]]
- **Sub-Agent-Coordination:** [[10-KB/sub-agent-coordination]]
- **Atlas-Hallucination-Prevention:** [[10-KB/atlas-hallucination-prevention]]
- **Live-Dashboard:** [[_agents/memory-dashboard]] (auto-regen nightly)
- **Vault-Index:** [[_agents/_VAULT-INDEX]]

## File-Locations (important!)

```
/home/piet/vault/10-KB/                         L1 compiled (read-only output)
/home/piet/.openclaw/workspace/memory/          Live memory-jsonl-files
  ├── graph.jsonl                               L2 edges
  ├── retrieval-feedback.jsonl                  L3 feedback
  └── memory-budget.log + session-size-guard    L5 budgets
/home/piet/vault/_agents/memory-dashboard.md    L6 dashboard (auto)
```

**Not to confuse:** `vault/memory/` (12 KB, Dead-Storage) ≠ `.openclaw/workspace/memory/` (46 MB, live).

## Defense-Crons (Memory-relevant)

- `*/5 session-freeze-watcher`
- `*/5 memory-budget-meter` (L5)
- `*/5 stale-lock-cleaner`
- `*/10 session-health-monitor`
- `0 4 kb-compiler.py` (L1)
- `15 4 graph-edge-builder` (L2)
- `30 4 memory-dashboard-generator` (L6-Lite)
- `30 */1 retrieval-feedback-loop` (L3)
- `0 5 0 importance-recalc` (weekly)

## Roadmap (offen)

- [ ] **P2.7** L3 Retrieval-Feedback ausweiten (mehr Signal pro Woche) — entblockt P3.4
- [ ] **P3.3** Smart-Connections (Ollama embeddings + ChromaDB) für semantic-search
- [ ] **P3.4** L3 als ML-Training-Signal (hängt P2.7 ab)
- [ ] **P3.5** KB-Compiler als PR-Style-Diff (Eleanor-Konik-Pattern) — Review statt Auto-Merge
- [ ] L3 Signalbasis-Erweiterung (aktuell zu dünn für Training)
