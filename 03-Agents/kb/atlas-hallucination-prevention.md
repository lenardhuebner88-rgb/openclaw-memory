---
title: "Atlas Hallucination Prevention"
slug: atlas-hallucination-prevention
last_compiled: 2026-04-19T20:46:30.335728Z
compiler: kb-compiler.py@v1-mvp
fact_count: 0
rule_count: 4
memory_level: 3
---

# Atlas Hallucination Prevention

**Description:** Prevention of Atlas producing fabricated commit-SHAs/session-IDs/done-claims after context-rotation.

**Compiled:** 2026-04-19T20:46:30.335728Z  
**Source:** 0 facts from workspace/memory/facts/*.jsonl, 4 rules from workspace/memory/rules.jsonl

## Key Rules

### R3 — Atlas meldet keinen Erfolg ohne GET-Verify
*Status: active | Since: None*



### R35 — Atlas-Self-Report ≠ Board-Truth
*Status: active | Since: 2026-04-19*



### R36 — Agent-Session-File-Size-Creep
*Status: pending | Since: 2026-04-19*



### R49 — Atlas Anti-Hallucination Claim-Verify-Before-Report
*Status: active | Since: 2026-04-19*

Atlas DARF KEINE Commit-SHAs, Session-IDs, Task-IDs oder Done-Claims in Status-Reports schreiben ohne pre-claim Disk-Verify (git log -1 SHA, ls agent-sessions ID.jsonl, curl /api/tasks/ID). Atlas MUSS die Verify-Command inline in den Chat posten dami...

## Key Facts (Top-20 by Importance)

*(no facts matched this topic)*

## Related KB Articles

- [Deploy Contracts & MC-Restart](deploy-contracts.md)
- [Incident Response & RCA](incident-response.md)
- [Memory Architecture](memory-architecture.md)

## Metadata

- **Topic keywords** (for future recompilation): hallucination, halluz, R49, R35, R36, context-overflow, session-rotation, fabricated...
- **Related rules (declared)**: R49, R35, R36, R3
- **Schema version**: KB-article v1-mvp

---

*Auto-compiled from 0 facts + 4 rules by `kb-compiler.py@v1-mvp`. Manual edits will be preserved where possible but may be overwritten on next compile — use `<!-- manual: start --> ... <!-- manual: end -->` to mark preserved sections (future feature).*