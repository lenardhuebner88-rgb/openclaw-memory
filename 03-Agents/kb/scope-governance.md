---
title: "Scope Governance & operatorLock"
slug: scope-governance
last_compiled: 2026-04-19T20:46:30.336079Z
compiler: kb-compiler.py@v1-mvp
fact_count: 0
rule_count: 2
memory_level: 3
---

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