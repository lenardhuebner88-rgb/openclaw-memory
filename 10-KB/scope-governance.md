---
title: "Scope Governance & operatorLock"
slug: scope-governance
last_compiled: 2026-05-04T00:30:02.690619Z
compiler: kb-compiler.py@v1-mvp
fact_count: 8
rule_count: 3
memory_level: 3
---

# Scope Governance & operatorLock

**Description:** Plan-Doc-Level scope-lock enforcement, preventing autonomous sprint-dispatch bypass.

**Compiled:** 2026-05-04T00:30:02.690619Z  
**Source:** 8 facts from workspace/memory/facts/*.jsonl, 3 rules from workspace/memory/rules.jsonl

## Key Rules

### R28 — Operator-Lock-Respekt (geplant, Phase 2 Stabilization-Plan)
*Status: active | Since: 2026-04-18*



### R44 — Board-Discipline: Board-Task required before sessions_spawn
*Status: active | Since: 2026-04-19*

Sub-Agent-Arbeit darf nie sessions_spawn-only laufen. Vor jeder delegierten Ausfuehrung MUSS ein Board-Task via taskboard_create_task existieren oder ein vorhandener Task genutzt werden. Wenn kein Board-Task vorhanden ist: zuerst taskboard_create_tas...

### R47 — Scope-Lock-auf-Plan-Doc nicht Task-ID
*Status: active | Since: 2026-04-19*

Atlas MUSS vor Sprint-Dispatch das Plan-Doc-Frontmatter lesen. Wenn operatorLock: true — NICHT dispatchen unabhaengig von Task-IDs.

## Key Facts (Top-20 by Importance)

- **[0.95]** `procedural` (2026-04-19T21:35:11 system#91fe24e9) — R47 Scope-Lock auf Plan-Doc-Frontmatter statt Task-ID deployed Sprint-J J2 (commit c268ee0). Live-Case: Sprint-F operatorLock=true auf draft ee455d69 wurde umgangen durch neue Task-IDs (89afba3b, e45a...
- **[0.90]** `procedural` (2026-04-19T21:35:11 system#362e267d) — Rules-Stack erweitert auf R1-R49 (49 total) am 2026-04-19. Heute neu: R45 Sub-Agent-Receipt-Discipline, R46 Parallel-Deploy-Serialization, R47 Scope-Lock-Plan-Doc, R48 Board-Hygiene-Cron, R49 Atlas An...
- **[0.90]** `procedural` (2026-04-19T21:35:11 system#1f4f56a6) — Pre-Flight-Sprint-Dispatch Script deployed 2026-04-19 20:42 UTC mit 7 Gates: Atlas-session-size R36, operatorLock R47, Board-open_count, MC+Gateway-health, R49-Validator-CRITICAL, Git-dirty-state, Fre...
- **[0.85]** `procedural` (2026-04-19T21:35:11 system#4ab4f0af) — Atlas-State-Snapshot-Generator deployed 2026-04-19 21:26 UTC (L5-Deep). Script extrahiert aktuelle Atlas-Session in strukturiertes Markdown (session-id, git-log, plan-docs, task-IDs, last-assistant-me...
- **[0.85]** `semantic` (2026-04-19T21:35:11 system#967225ab) — Defense-Stack Pattern 2026-04-19: 12 automated cron-layers active für governance + memory + monitoring: session-freeze-watcher */5, r49-claim-validator */15, r48-board-hygiene hourly, daily-reflection...
- **[0.57]** `reflective` (2026-04-19T21:50:01 system#5ee1ed4a) — Today's highest-importance facts:   - [1.00] R49 Atlas Anti-Hallucination Claim-Verify-Before-Report deployed 2026-04-19 20:3   - [0.95] R45 Sub-Agent-Receipt-Discipline deployed 2026-04-19 17:20 UTC ...
- **[0.31]** `semantic` (2026-04-19T21:35:11 system#1db9c9d9) — 10 Karpathy-KB-Articles compiled 2026-04-19 20:46 UTC in vault/03-Agents/kb/: sprint-orchestration (27f/7r), receipt-discipline (34f/4r), deploy-contracts (12f/3r), atlas-hallucination-prevention (0f/...
- **[0.07]** `episodic` (2026-04-19T21:35:11 system#c1d68857) — Atlas-main lief 2026-04-19 evening auf MiniMax-M2.7 statt Codex (primary offline). Sprint-I-Dispatch funktional, 4 parallele Sub-Tasks (Pixel×2 + Forge + Lens) dispatched innerhalb 2min nach /reset. R...

## Related KB Articles

- [Atlas Hallucination Prevention](atlas-hallucination-prevention.md)
- [Board Hygiene & Lifecycle](board-hygiene.md)
- [Deploy Contracts & MC-Restart](deploy-contracts.md)
- [Incident Response & RCA](incident-response.md)
- [Receipt Discipline](receipt-discipline.md)
- [Sprint Orchestration](sprint-orchestration.md)
- [Sub-Agent Coordination](sub-agent-coordination.md)

## Metadata

- **Topic keywords** (for future recompilation): operatorLock, scope-lock, R47, governance, plan-doc, frontmatter, bypass, enforcement_mode
- **Related rules (declared)**: R47, R44, R28
- **Schema version**: KB-article v1-mvp

---

*Auto-compiled from 8 facts + 3 rules by `kb-compiler.py@v1-mvp`. Manual edits will be preserved where possible but may be overwritten on next compile — use `<!-- manual: start --> ... <!-- manual: end -->` to mark preserved sections (future feature).*