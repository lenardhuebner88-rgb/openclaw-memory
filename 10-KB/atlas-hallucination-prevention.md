---
title: "Atlas Hallucination Prevention"
slug: atlas-hallucination-prevention
last_compiled: 2026-05-02T17:30:18.031333Z
compiler: kb-compiler.py@v1-mvp
fact_count: 8
rule_count: 4
memory_level: 3
---

# Atlas Hallucination Prevention

**Description:** Prevention of Atlas producing fabricated commit-SHAs/session-IDs/done-claims after context-rotation.

**Compiled:** 2026-05-02T17:30:18.031333Z  
**Source:** 8 facts from workspace/memory/facts/*.jsonl, 4 rules from workspace/memory/rules.jsonl

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

- **[1.00]** `procedural` (2026-04-19T21:35:11 system#4eeb1a13) — R49 Atlas Anti-Hallucination Claim-Verify-Before-Report deployed 2026-04-19 20:30 UTC nach Atlas-Hallucinations-Cascade 19:42-20:03 UTC. Atlas-Session d27407ee halluzinierte 2x Commit-SHAs (3dcb614, 9...
- **[0.90]** `procedural` (2026-04-19T21:35:11 system#1f4f56a6) — Pre-Flight-Sprint-Dispatch Script deployed 2026-04-19 20:42 UTC mit 7 Gates: Atlas-session-size R36, operatorLock R47, Board-open_count, MC+Gateway-health, R49-Validator-CRITICAL, Git-dirty-state, Fre...
- **[0.90]** `procedural` (2026-04-19T21:35:11 system#362e267d) — Rules-Stack erweitert auf R1-R49 (49 total) am 2026-04-19. Heute neu: R45 Sub-Agent-Receipt-Discipline, R46 Parallel-Deploy-Serialization, R47 Scope-Lock-Plan-Doc, R48 Board-Hygiene-Cron, R49 Atlas An...
- **[0.85]** `semantic` (2026-04-19T21:35:11 system#967225ab) — Defense-Stack Pattern 2026-04-19: 12 automated cron-layers active für governance + memory + monitoring: session-freeze-watcher */5, r49-claim-validator */15, r48-board-hygiene hourly, daily-reflection...
- **[0.63]** `reflective` (2026-04-19T21:50:01 system#5ee1ed4a) — Today's highest-importance facts:   - [1.00] R49 Atlas Anti-Hallucination Claim-Verify-Before-Report deployed 2026-04-19 20:3   - [0.95] R45 Sub-Agent-Receipt-Discipline deployed 2026-04-19 17:20 UTC ...
- **[0.38]** `semantic` (2026-04-19T21:35:11 system#1db9c9d9) — 10 Karpathy-KB-Articles compiled 2026-04-19 20:46 UTC in vault/03-Agents/kb/: sprint-orchestration (27f/7r), receipt-discipline (34f/4r), deploy-contracts (12f/3r), atlas-hallucination-prevention (0f/...
- **[0.23]** `episodic` (2026-04-19T21:35:11 system#7a59071b) — R49-Claim-Validator first detection 2026-04-19 21:15 UTC: WARNING auf task_not_found 26ed095e-a77a-4b3d-8b50-9ff06635cf92 in sre-expert session. False-positive — ist mcp-zombie-killer-hourly cron-sess...
- **[0.12]** `episodic` (2026-04-19T21:35:11 system#c1d68857) — Atlas-main lief 2026-04-19 evening auf MiniMax-M2.7 statt Codex (primary offline). Sprint-I-Dispatch funktional, 4 parallele Sub-Tasks (Pixel×2 + Forge + Lens) dispatched innerhalb 2min nach /reset. R...

## Related KB Articles

- [Deploy Contracts & MC-Restart](deploy-contracts.md)
- [Incident Response & RCA](incident-response.md)
- [Memory Architecture](memory-architecture.md)

## Metadata

- **Topic keywords** (for future recompilation): hallucination, halluz, R49, R35, R36, context-overflow, session-rotation, fabricated...
- **Related rules (declared)**: R49, R35, R36, R3
- **Schema version**: KB-article v1-mvp

---

*Auto-compiled from 8 facts + 4 rules by `kb-compiler.py@v1-mvp`. Manual edits will be preserved where possible but may be overwritten on next compile — use `<!-- manual: start --> ... <!-- manual: end -->` to mark preserved sections (future feature).*