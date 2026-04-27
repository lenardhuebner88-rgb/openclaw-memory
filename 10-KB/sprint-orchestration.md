---
title: "Sprint Orchestration"
slug: sprint-orchestration
last_compiled: 2026-04-27T07:30:18.001475Z
compiler: kb-compiler.py@v1-mvp
fact_count: 47
rule_count: 9
memory_level: 3
---

# Sprint Orchestration

**Description:** How Atlas-main orchestriert multi-agent sprints, dispatch-patterns, Board-visibility discipline.

**Compiled:** 2026-04-27T07:30:18.001475Z  
**Source:** 47 facts from workspace/memory/facts/*.jsonl, 9 rules from workspace/memory/rules.jsonl

## Key Rules

### R1 — Verify-After-Write ist Pflicht
*Status: active | Since: 2026-04-17*



### R32 — Dispatch-Gate Atlas-Sonderfall
*Status: pending | Since: 2026-04-19*



### R37 — Atlas-Orchestrator-Tasks nicht via Auto-Pickup
*Status: resolved | Since: 2026-04-19*

Atlas-Sprint-Tasks als `draft` + `operatorLock=true` anlegen (Auto-Pickup skipped). Operator startet Atlas-Session manuell mit Trigger-Phrase "Lade <Plan> und starte <Sprint>". Atlas liest Board, erkennt `[Atlas-Sprint-*]`-Prefix und orchestriert Sub...

### R39 — Atlas-main braucht Session-Resume-Pattern
*Status: active | Since: 2026-04-19*

Bei Atlas-Orphan-State resumed der Operator oder ein Wrapper-Cron die Session via `openclaw agent --session-id <id> --message "continue orchestration"`. Alternativ: Multi-Sprint-Orchestration auf minions-Subsystem (PR #68718 upstream) migrieren sobal...

### R42 — Deploy-Restart-Discipline via mc-restart-safe
*Status: active | Since: 2026-04-19*

Wenn eine Task einen Mission-Control-Restart erfordert, MUSS mc-restart-safe <timeout> <tag> verwendet werden. Direktes systemctl --user restart mission-control ist verboten. mc-restart-safe serialisiert via Deploy-Lock, wartet bis /api/health 200 li...

### R44 — Board-Discipline: Board-Task required before sessions_spawn
*Status: active | Since: 2026-04-19*

Sub-Agent-Arbeit darf nie sessions_spawn-only laufen. Vor jeder delegierten Ausfuehrung MUSS ein Board-Task via taskboard_create_task existieren oder ein vorhandener Task genutzt werden. Wenn kein Board-Task vorhanden ist: zuerst taskboard_create_tas...

### R45 — Sub-Agent-Receipt-Discipline
*Status: active | Since: 2026-04-19*

Sub-Agent MUSS innerhalb 60s nach Task-Pickup taskboard_post_receipt mit receipt=accepted posten. Waehrend Arbeit MUSS mindestens alle 5min oder bei jedem Major-Step ein receipt=progress kommen. Status assigned laenger als 2min ohne Receipt = Contrac...

### R46 — Parallel-Deploy-Serialization
*Status: active | Since: 2026-04-19*

Wenn mehrere Sub-Agents parallel laufen UND jeder einen systemctl --user restart mission-control + curl verify Contract im Prompt hat → Deploy-Race-Condition. Fix: sequenzieller Sprint-Flow ODER Deploy-Queue-Lock (nur ein MC-Restart gleichzeitig, Age...

### R47 — Scope-Lock-auf-Plan-Doc nicht Task-ID
*Status: active | Since: 2026-04-19*

Atlas MUSS vor Sprint-Dispatch das Plan-Doc-Frontmatter lesen. Wenn operatorLock: true — NICHT dispatchen unabhaengig von Task-IDs.

## Key Facts (Top-20 by Importance)

- **[1.00]** `procedural` (2026-04-19T21:35:11 system#4eeb1a13) — R49 Atlas Anti-Hallucination Claim-Verify-Before-Report deployed 2026-04-19 20:30 UTC nach Atlas-Hallucinations-Cascade 19:42-20:03 UTC. Atlas-Session d27407ee halluzinierte 2x Commit-SHAs (3dcb614, 9...
- **[0.95]** `procedural` (2026-04-19T21:35:11 system#cfa2ead4) — R45 Sub-Agent-Receipt-Discipline deployed 2026-04-19 17:20 UTC nach Live-Case Sprint-E E2+E3 wo Sub-Agents 2h+ in status=assigned stecken blieben ohne Receipts zu posten. Fix: AGENTS.md Preamble + ses...
- **[0.95]** `procedural` (2026-04-19T21:35:11 system#9f4e0cd7) — R46 Parallel-Deploy-Serialization deployed 2026-04-19 17:22 UTC nach Sprint-E E2+E3 MC-Flap-Loop (9 Restarts in 11min). Fix: mc-restart-safe wrapper mit flock /tmp/mc-deploy.lock, verifiziert via para...
- **[0.95]** `procedural` (2026-04-19T21:35:11 system#91fe24e9) — R47 Scope-Lock auf Plan-Doc-Frontmatter statt Task-ID deployed Sprint-J J2 (commit c268ee0). Live-Case: Sprint-F operatorLock=true auf draft ee455d69 wurde umgangen durch neue Task-IDs (89afba3b, e45a...
- **[0.90]** `procedural` (2026-04-19T21:35:11 system#1f4f56a6) — Pre-Flight-Sprint-Dispatch Script deployed 2026-04-19 20:42 UTC mit 7 Gates: Atlas-session-size R36, operatorLock R47, Board-open_count, MC+Gateway-health, R49-Validator-CRITICAL, Git-dirty-state, Fre...
- **[0.90]** `procedural` (2026-04-19T21:35:11 system#362e267d) — Rules-Stack erweitert auf R1-R49 (49 total) am 2026-04-19. Heute neu: R45 Sub-Agent-Receipt-Discipline, R46 Parallel-Deploy-Serialization, R47 Scope-Lock-Plan-Doc, R48 Board-Hygiene-Cron, R49 Atlas An...
- **[0.85]** `semantic` (2026-04-19T21:35:11 system#967225ab) — Defense-Stack Pattern 2026-04-19: 12 automated cron-layers active für governance + memory + monitoring: session-freeze-watcher */5, r49-claim-validator */15, r48-board-hygiene hourly, daily-reflection...
- **[0.85]** `procedural` (2026-04-19T21:35:11 system#4ab4f0af) — Atlas-State-Snapshot-Generator deployed 2026-04-19 21:26 UTC (L5-Deep). Script extrahiert aktuelle Atlas-Session in strukturiertes Markdown (session-id, git-log, plan-docs, task-IDs, last-assistant-me...
- **[0.74]** `reflective` (2026-04-19T21:50:01 system#5ee1ed4a) — Today's highest-importance facts:   - [1.00] R49 Atlas Anti-Hallucination Claim-Verify-Before-Report deployed 2026-04-19 20:3   - [0.95] R45 Sub-Agent-Receipt-Discipline deployed 2026-04-19 17:20 UTC ...
- **[0.74]** `reflective` (2026-04-19T20:34:51 system#5ee1ed4a) — Today's highest-importance facts:   - [0.77] - Mehrere operative Incidents gelöst, am Ende 0 offene Tasks und 0 failed.   - [0.77] **Sub-Plan A Status:** - A1 ✅ `b84ac186` done - A2 ✅ `515b940f` done ...
- **[0.69]** `episodic` (2026-04-19T21:35:11 system#26e954cf) — Sprint-L Memory-Level-3 MVPs deployed 2026-04-19 20:00-21:30 UTC: L1 KB-Compiler 10 articles, L2 Graph-Edges 1024 edges, L3 Retrieval-Feedback hourly, L4 Per-Agent-Scoping 257 facts migrated, L5 Budge...
- **[0.65]** `episodic` (2026-04-19T21:35:11 system#5f8f0efe) — Memory-Budget-Meter first real CRITICAL caught 2026-04-19 21:20 UTC: Atlas-session 48f8d0f0 explodierte auf 373% (559k tokens / 150k budget) während Forge Sprint-G/H Consolidation-Task. Vorheriger che...
- **[0.65]** `procedural` (2026-04-19T21:35:11 system#098d7a25) — Cron-Audit 2026-04-19 23:00 UTC: 51 aktive Schedules über 3 Scheduler fragmentiert (34 crontab + 6 systemd-timer + 16 openclaw-cron). 0 active errors, historische nur aus Sprint-E MC-Flap 17:00-17:32....
- **[0.61]** `episodic` (2026-04-19T21:35:11 system#ead36dfd) — Atlas autonomous-cascade Sprint-F+G+H ohne Operator-Approval dispatched 2026-04-19 17:56-19:30 UTC. Sprint-F F1+F2 done autonomously (Lens/Forge), Sprint-G G1-G4 done (4 commits), Sprint-H H1-H3 mit 2...
- **[0.58]** `procedural` (2026-04-19T21:35:11 system#8bb6b4eb) — Sprint-K H10 Cron-Inventory-Consolidation + Observability formally added 2026-04-19 23:15 UTC. 5 Layers: L1 Cleanup (DONE), L2 Memory-Orchestrator (1-2h), L3 Systemd-Migration 3 crons (2h), L4 Healthc...
- **[0.57]** `episodic` (2026-04-19T21:35:11 system#b98ffbd8) — Sprint-E Board UX-Level-Up Phase-2 complete 2026-04-19 16:51-17:31 UTC mit 6 Commits auf main: edb0d56 (WCAG + Hero), 7f9122c (Command Palette), 10b7274 (SSE Backend), ea13c39 (Unified Nav), 06c30c8 (...
- **[0.54]** `episodic` (2026-04-19T21:35:11 system#258f56ec) — Sprint-G/H Consolidation 2026-04-19 21:16-21:18 UTC (Forge 5a10491a): 4 commits konsolidierten Sprint-G/H autonomous-cascade Arbeit: b941b36 (.bak removes), 5fac96a (sprint-g ops-dashboard), daee0c7 (...
- **[0.53]** `semantic` (2026-04-19T21:35:11 system#1db9c9d9) — 10 Karpathy-KB-Articles compiled 2026-04-19 20:46 UTC in vault/03-Agents/kb/: sprint-orchestration (27f/7r), receipt-discipline (34f/4r), deploy-contracts (12f/3r), atlas-hallucination-prevention (0f/...
- **[0.53]** `procedural` (2026-04-19T21:35:11 system#1c7cd11c) — Sprint-Debrief-Watch openclaw-cron 031f586a disabled 2026-04-19 22:50 UTC nach Timeout-Spam (cron: job execution timed out alle 12min). Ersetzt durch lightweight shell-script /home/piet/.openclaw/scri...
- **[0.45]** `semantic` (2026-04-19T14:20:24 main#e8798fff) — - **Sprint-B sequence started:** B2-B4 merged into a single delegated Forge task to reduce spawn overhead.

## Related KB Articles

- [Atlas Hallucination Prevention](atlas-hallucination-prevention.md)
- [Board Hygiene & Lifecycle](board-hygiene.md)
- [Build & Deploy Rules](build-deploy-regeln.md)
- [Deploy Contracts & MC-Restart](deploy-contracts.md)
- [Incident Response & RCA](incident-response.md)
- [Receipt Discipline](receipt-discipline.md)
- [Scope Governance & operatorLock](scope-governance.md)
- [Sub-Agent Coordination](sub-agent-coordination.md)

## Metadata

- **Topic keywords** (for future recompilation): atlas, orchestrator, orchestration, dispatch, sprint-, taskboard_create_task, sub-task, sub-agent
- **Related rules (declared)**: R37, R44, R47
- **Schema version**: KB-article v1-mvp

---

*Auto-compiled from 47 facts + 9 rules by `kb-compiler.py@v1-mvp`. Manual edits will be preserved where possible but may be overwritten on next compile — use `<!-- manual: start --> ... <!-- manual: end -->` to mark preserved sections (future feature).*