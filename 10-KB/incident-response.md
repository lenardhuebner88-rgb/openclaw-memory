---
title: "Incident Response & RCA"
slug: incident-response
last_compiled: 2026-04-29T10:30:18.254044Z
compiler: kb-compiler.py@v1-mvp
fact_count: 44
rule_count: 8
memory_level: 3
---

# Incident Response & RCA

**Description:** Incident-detection patterns, RCA methodology, recovery-workflows from today's live-cases.

**Compiled:** 2026-04-29T10:30:18.254044Z  
**Source:** 44 facts from workspace/memory/facts/*.jsonl, 8 rules from workspace/memory/rules.jsonl

## Key Rules

### R15 — Deploy-Sequenz ist atomar im Agent-Turn
*Status: active | Since: 2026-04-17*



### R32 — Dispatch-Gate Atlas-Sonderfall
*Status: pending | Since: 2026-04-19*



### R33 — Cron-Script-Pfad-Integrität
*Status: active | Since: 2026-04-18*



### R35 — Atlas-Self-Report ≠ Board-Truth
*Status: active | Since: 2026-04-19*



### R38 — MCP-Zombie-Defense-in-depth (existierender Reaper + Alert)
*Status: resolved | Since: 2026-04-19*



### R40 — Stall-Detection-Thresholds sind Kern-Infra
*Status: resolved | Since: 2026-04-19*



### R54 — MCP-Not-Connected erst als Session-/Gateway-Korrelation triagieren
*Status: active | Since: 2026-04-21*

Bei MCP-Tool-Fail mit `Not connected` oder `Connection closed` MUSS zuerst die Gateway-Restart-History gegen die betroffene Session-Zeit korreliert werden. Kein vorschneller Backend-/Tool-RCA-Pfad, bevor Session-Staleness ausgeschlossen ist.

### R55 — Gateway-Restart heilt keine stale MCP-Session-Runtimes
*Status: active | Since: 2026-04-21*

Ein Gateway-Restart alleine gilt nicht als Recovery fuer `Not connected` in bestehenden Sessions. Bei Pre-Crash-Sessions: zuerst Session-Rotation oder nach Runtime-Hotfix den ersten lazy-recovery Fail einkalkulieren.

## Key Facts (Top-20 by Importance)

- **[1.00]** `procedural` (2026-04-19T21:35:11 system#4eeb1a13) — R49 Atlas Anti-Hallucination Claim-Verify-Before-Report deployed 2026-04-19 20:30 UTC nach Atlas-Hallucinations-Cascade 19:42-20:03 UTC. Atlas-Session d27407ee halluzinierte 2x Commit-SHAs (3dcb614, 9...
- **[0.90]** `procedural` (2026-04-19T21:35:11 system#1f4f56a6) — Pre-Flight-Sprint-Dispatch Script deployed 2026-04-19 20:42 UTC mit 7 Gates: Atlas-session-size R36, operatorLock R47, Board-open_count, MC+Gateway-health, R49-Validator-CRITICAL, Git-dirty-state, Fre...
- **[0.72]** `reflective` (2026-04-19T20:34:51 system#5ee1ed4a) — Today's highest-importance facts:   - [0.77] - Mehrere operative Incidents gelöst, am Ende 0 offene Tasks und 0 failed.   - [0.77] **Sub-Plan A Status:** - A1 ✅ `b84ac186` done - A2 ✅ `515b940f` done ...
- **[0.72]** `reflective` (2026-04-19T21:50:01 system#5ee1ed4a) — Today's highest-importance facts:   - [1.00] R49 Atlas Anti-Hallucination Claim-Verify-Before-Report deployed 2026-04-19 20:3   - [0.95] R45 Sub-Agent-Receipt-Discipline deployed 2026-04-19 17:20 UTC ...
- **[0.67]** `reflective` (2026-04-19T20:34:51 system#8cef893c) — Incident-Themes today (251 incidents): ['failed', 'output', 'contains', 'parity_check_failed', 'parity_check_error,']
- **[0.67]** `reflective` (2026-04-19T21:50:01 system#8cef893c) — Incident-Themes today (253 incidents): ['failed', 'output', 'contains', 'parity_check_failed', 'parity_check_error,']
- **[0.61]** `reflective` (2026-04-19T20:34:51 system#d57e4ffc) — Today's top fact-categories: incident:251, delivery:1
- **[0.61]** `reflective` (2026-04-19T21:50:01 system#d57e4ffc) — Today's top fact-categories: incident:253, delivery:6, rule:5, pattern:4, config:4
- **[0.56]** `episodic` (2026-04-19T21:35:11 system#ead36dfd) — Atlas autonomous-cascade Sprint-F+G+H ohne Operator-Approval dispatched 2026-04-19 17:56-19:30 UTC. Sprint-F F1+F2 done autonomously (Lens/Forge), Sprint-G G1-G4 done (4 commits), Sprint-H H1-H3 mit 2...
- **[0.50]** `semantic` (2026-04-19T21:35:11 system#1db9c9d9) — 10 Karpathy-KB-Articles compiled 2026-04-19 20:46 UTC in vault/03-Agents/kb/: sprint-orchestration (27f/7r), receipt-discipline (34f/4r), deploy-contracts (12f/3r), atlas-hallucination-prevention (0f/...
- **[0.49]** `episodic` (2026-04-19T21:35:11 system#258f56ec) — Sprint-G/H Consolidation 2026-04-19 21:16-21:18 UTC (Forge 5a10491a): 4 commits konsolidierten Sprint-G/H autonomous-cascade Arbeit: b941b36 (.bak removes), 5fac96a (sprint-g ops-dashboard), daee0c7 (...
- **[0.40]** `episodic` (2026-04-19T08:24:13 main#4cea56c3) — **Aktueller Stand:** | Task | Status | |------|--------| | WK-35 Retry (Operator-Lock) | pending-pickup → Forge | | Spark Naming-P2 | assigned | | Spark Naming-Audit | assigned | Falls wieder `failed`...
- **[0.40]** `episodic` (2026-04-19T08:24:13 main#1075b705) — **Aktueller Stand:** | Task | Status | |------|--------| | WK-35 Retry (Operator-Lock) | pending-pickup → Forge | | Spark Naming-P2 | assigned | | Spark Naming-Audit | assigned | Falls wieder `failed`...
- **[0.39]** `episodic` (2026-04-19T06:19:24 main#ea5baca6) — The `atlas-main` session (`agent:main:discord:channel:1486480128576983070`) has `status=failed`, `runtimeMs=0`, `startedAt > endedAt` — it crashed on startup with OOM.
- **[0.38]** `episodic` (2026-04-18T19:03:43 main#f3ae9ce2) — - Mehrere operative Incidents gelöst, am Ende 0 offene Tasks und 0 failed.
- **[0.38]** `episodic` (2026-04-18T22:29:09 main#0770974b) — **Sub-Plan A Status:** - A1 ✅ `b84ac186` done - A2 ✅ `515b940f` done - A3 ✅ `f1d6a4d4` done (Incident-Lane nur status=failed) A4 ('Later'→'Archive') und A5 (Dispatched-Metric Zeitfenster) sind nicht a...
- **[0.31]** `episodic` (2026-04-19T11:11:36 main#beda73b5) — **Typ: Incident — Sprint-2 Recovery nach OOM** Phase 1: Ghost-Cleanup starten.
- **[0.29]** `episodic` (2026-04-18T19:58:52 sre-expert#744da69d) — - Währenddessen wurde der Task einmal extern auf `failed` gezogen (ghost-fail vom Monitor), ich habe per `recovery-action: retry` wieder aufgenommen, danach erneut `accepted` + final `result`.
- **[0.29]** `episodic` (2026-04-18T19:58:52 sre-expert#8b7de057) — - Währenddessen wurde der Task einmal extern auf `failed` gezogen (ghost-fail vom Monitor), ich habe per `recovery-action: retry` wieder aufgenommen, danach erneut `accepted` + final `result`.
- **[0.29]** `episodic` (2026-04-18T19:58:52 sre-expert#1bb1d33d) — - Währenddessen wurde der Task einmal extern auf `failed` gezogen (ghost-fail vom Monitor), ich habe per `recovery-action: retry` wieder aufgenommen, danach erneut `accepted` + final `result`.

## Related KB Articles

- [Atlas Hallucination Prevention](atlas-hallucination-prevention.md)
- [Deploy Contracts & MC-Restart](deploy-contracts.md)

## Metadata

- **Topic keywords** (for future recompilation): incident, rca, root-cause, mc_health_fail, crash, ooz, oom, gateway...
- **Related rules (declared)**: R32, R33, R35, R38, R40
- **Schema version**: KB-article v1-mvp

---

*Auto-compiled from 44 facts + 8 rules by `kb-compiler.py@v1-mvp`. Manual edits will be preserved where possible but may be overwritten on next compile — use `<!-- manual: start --> ... <!-- manual: end -->` to mark preserved sections (future feature).*