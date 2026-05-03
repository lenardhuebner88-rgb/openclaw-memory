---
title: "Deploy Contracts & MC-Restart"
slug: deploy-contracts
last_compiled: 2026-05-03T03:30:17.795588Z
compiler: kb-compiler.py@v1-mvp
fact_count: 25
rule_count: 4
memory_level: 3
---

# Deploy Contracts & MC-Restart

**Description:** Deploy-Verify-Contract, parallel-deploy-race prevention via mc-restart-safe wrapper.

**Compiled:** 2026-05-03T03:30:17.795588Z  
**Source:** 25 facts from workspace/memory/facts/*.jsonl, 4 rules from workspace/memory/rules.jsonl

## Key Rules

### R1 — Verify-After-Write ist Pflicht
*Status: active | Since: 2026-04-17*



### R42 — Deploy-Restart-Discipline via mc-restart-safe
*Status: active | Since: 2026-04-19*

Wenn eine Task einen Mission-Control-Restart erfordert, MUSS mc-restart-safe <timeout> <tag> verwendet werden. Direktes systemctl --user restart mission-control ist verboten. mc-restart-safe serialisiert via Deploy-Lock, wartet bis /api/health 200 li...

### R46 — Parallel-Deploy-Serialization
*Status: active | Since: 2026-04-19*

Wenn mehrere Sub-Agents parallel laufen UND jeder einen systemctl --user restart mission-control + curl verify Contract im Prompt hat → Deploy-Race-Condition. Fix: sequenzieller Sprint-Flow ODER Deploy-Queue-Lock (nur ein MC-Restart gleichzeitig, Age...

### R7 — Kanonische Build-Sequenz (nicht `deploy.sh`)
*Status: active | Since: None*



## Key Facts (Top-20 by Importance)

- **[1.00]** `procedural` (2026-04-19T21:35:11 system#4eeb1a13) — R49 Atlas Anti-Hallucination Claim-Verify-Before-Report deployed 2026-04-19 20:30 UTC nach Atlas-Hallucinations-Cascade 19:42-20:03 UTC. Atlas-Session d27407ee halluzinierte 2x Commit-SHAs (3dcb614, 9...
- **[0.95]** `procedural` (2026-04-19T21:35:11 system#9f4e0cd7) — R46 Parallel-Deploy-Serialization deployed 2026-04-19 17:22 UTC nach Sprint-E E2+E3 MC-Flap-Loop (9 Restarts in 11min). Fix: mc-restart-safe wrapper mit flock /tmp/mc-deploy.lock, verifiziert via para...
- **[0.95]** `procedural` (2026-04-19T21:35:11 system#cfa2ead4) — R45 Sub-Agent-Receipt-Discipline deployed 2026-04-19 17:20 UTC nach Live-Case Sprint-E E2+E3 wo Sub-Agents 2h+ in status=assigned stecken blieben ohne Receipts zu posten. Fix: AGENTS.md Preamble + ses...
- **[0.95]** `procedural` (2026-04-19T21:35:11 system#91fe24e9) — R47 Scope-Lock auf Plan-Doc-Frontmatter statt Task-ID deployed Sprint-J J2 (commit c268ee0). Live-Case: Sprint-F operatorLock=true auf draft ee455d69 wurde umgangen durch neue Task-IDs (89afba3b, e45a...
- **[0.90]** `procedural` (2026-04-19T21:35:11 system#51750d99) — mc-restart-safe wrapper deployed at /home/piet/.local/bin/ + ~/.openclaw/bin/ — flock-basiert, serialisiert MC-restarts via /tmp/mc-deploy.lock. Proof-of-Concept verified: 2 parallel calls → A acquire...
- **[0.90]** `procedural` (2026-04-19T21:35:11 system#362e267d) — Rules-Stack erweitert auf R1-R49 (49 total) am 2026-04-19. Heute neu: R45 Sub-Agent-Receipt-Discipline, R46 Parallel-Deploy-Serialization, R47 Scope-Lock-Plan-Doc, R48 Board-Hygiene-Cron, R49 Atlas An...
- **[0.90]** `procedural` (2026-04-19T21:35:11 system#1f4f56a6) — Pre-Flight-Sprint-Dispatch Script deployed 2026-04-19 20:42 UTC mit 7 Gates: Atlas-session-size R36, operatorLock R47, Board-open_count, MC+Gateway-health, R49-Validator-CRITICAL, Git-dirty-state, Fre...
- **[0.85]** `procedural` (2026-04-19T21:35:11 system#8d84780c) — R48 Board-Hygiene-Cron deployed 2026-04-19 ~19:30 UTC (hourly). Rule: status=draft AND age>48h → admin-close. Motivation: 19 stale tasks manually cleaned by Operator 19:41 UTC (6 drafts 3-8d old + 13 ...
- **[0.85]** `procedural` (2026-04-19T21:35:11 system#4ab4f0af) — Atlas-State-Snapshot-Generator deployed 2026-04-19 21:26 UTC (L5-Deep). Script extrahiert aktuelle Atlas-Session in strukturiertes Markdown (session-id, git-log, plan-docs, task-IDs, last-assistant-me...
- **[0.57]** `reflective` (2026-04-19T21:50:01 system#5ee1ed4a) — Today's highest-importance facts:   - [1.00] R49 Atlas Anti-Hallucination Claim-Verify-Before-Report deployed 2026-04-19 20:3   - [0.95] R45 Sub-Agent-Receipt-Discipline deployed 2026-04-19 17:20 UTC ...
- **[0.41]** `episodic` (2026-04-19T21:35:11 system#26e954cf) — Sprint-L Memory-Level-3 MVPs deployed 2026-04-19 20:00-21:30 UTC: L1 KB-Compiler 10 articles, L2 Graph-Edges 1024 edges, L3 Retrieval-Feedback hourly, L4 Per-Agent-Scoping 257 facts migrated, L5 Budge...
- **[0.38]** `procedural` (2026-04-19T21:35:11 system#098d7a25) — Cron-Audit 2026-04-19 23:00 UTC: 51 aktive Schedules über 3 Scheduler fragmentiert (34 crontab + 6 systemd-timer + 16 openclaw-cron). 0 active errors, historische nur aus Sprint-E MC-Flap 17:00-17:32....
- **[0.31]** `semantic` (2026-04-19T21:35:11 system#1db9c9d9) — 10 Karpathy-KB-Articles compiled 2026-04-19 20:46 UTC in vault/03-Agents/kb/: sprint-orchestration (27f/7r), receipt-discipline (34f/4r), deploy-contracts (12f/3r), atlas-hallucination-prevention (0f/...
- **[0.07]** `episodic` (2026-04-18T18:21:40 sre-expert#8e0d95dc) — updatedAt` - Build + Deploy: `npm run build` (grün), danach `./deploy.sh` erfolgreich - Vorher/Nachher KPI: `closed-24h 54 -> 91` - Regression: `new-blockers-24h=0`, `recovery-delta=0` (plausibel) - C...
- **[0.07]** `episodic` (2026-04-18T18:21:40 sre-expert#b64fc73c) — updatedAt` - Build + Deploy: `npm run build` (grün), danach `./deploy.sh` erfolgreich - Vorher/Nachher KPI: `closed-24h 54 -> 91` - Regression: `new-blockers-24h=0`, `recovery-delta=0` (plausibel) - C...
- **[0.07]** `episodic` (2026-04-18T18:21:40 sre-expert#f065d266) — updatedAt` - Build + Deploy: `npm run build` (grün), danach `./deploy.sh` erfolgreich - Vorher/Nachher KPI: `closed-24h 54 -> 91` - Regression: `new-blockers-24h=0`, `recovery-delta=0` (plausibel) - C...
- **[0.07]** `episodic` (2026-04-18T18:21:40 sre-expert#9033e3e3) — updatedAt` - Build + Deploy: `npm run build` (grün), danach `./deploy.sh` erfolgreich - Vorher/Nachher KPI: `closed-24h 54 -> 91` - Regression: `new-blockers-24h=0`, `recovery-delta=0` (plausibel) - C...
- **[0.07]** `episodic` (2026-04-18T18:21:40 sre-expert#7183c402) — updatedAt` - Build + Deploy: `npm run build` (grün), danach `./deploy.sh` erfolgreich - Vorher/Nachher KPI: `closed-24h 54 -> 91` - Regression: `new-blockers-24h=0`, `recovery-delta=0` (plausibel) - C...
- **[0.07]** `episodic` (2026-04-18T18:21:40 sre-expert#94afd194) — updatedAt` - Build + Deploy: `npm run build` (grün), danach `./deploy.sh` erfolgreich - Vorher/Nachher KPI: `closed-24h 54 -> 91` - Regression: `new-blockers-24h=0`, `recovery-delta=0` (plausibel) - C...
- **[0.07]** `episodic` (2026-04-18T18:21:40 sre-expert#27b752ae) — updatedAt` - Build + Deploy: `npm run build` (grün), danach `./deploy.sh` erfolgreich - Vorher/Nachher KPI: `closed-24h 54 -> 91` - Regression: `new-blockers-24h=0`, `recovery-delta=0` (plausibel) - C...

## Related KB Articles

- [Build & Deploy Rules](build-deploy-regeln.md)
- [Incident Response & RCA](incident-response.md)
- [Receipt Discipline](receipt-discipline.md)

## Metadata

- **Topic keywords** (for future recompilation): deploy, mc-restart-safe, systemctl, restart, R42, R46, flock, mc-deploy.lock...
- **Related rules (declared)**: R42, R46, R1, R7
- **Schema version**: KB-article v1-mvp

---

*Auto-compiled from 25 facts + 4 rules by `kb-compiler.py@v1-mvp`. Manual edits will be preserved where possible but may be overwritten on next compile — use `<!-- manual: start --> ... <!-- manual: end -->` to mark preserved sections (future feature).*