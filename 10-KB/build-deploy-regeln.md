---
title: "Build & Deploy Rules"
slug: build-deploy-regeln
last_compiled: 2026-04-26T14:30:17.823498Z
compiler: kb-compiler.py@v1-mvp
fact_count: 21
rule_count: 4
memory_level: 3
---

# Build & Deploy Rules

**Description:** Build-sequence, deploy-patterns, systemd-service conventions, V8-heap+memory limits.

**Compiled:** 2026-04-26T14:30:17.823498Z  
**Source:** 21 facts from workspace/memory/facts/*.jsonl, 4 rules from workspace/memory/rules.jsonl

## Key Rules

### R15 — Deploy-Sequenz ist atomar im Agent-Turn
*Status: active | Since: 2026-04-17*



### R26 — Server-Only Import-Disziplin
*Status: resolved | Since: 2026-04-18*



### R5 — Kanonischer MC-Service ist User-Level, Port 3000
*Status: active | Since: 2026-04-17*



### R7 — Kanonische Build-Sequenz (nicht `deploy.sh`)
*Status: active | Since: None*



## Key Facts (Top-20 by Importance)

- **[0.90]** `procedural` (2026-04-19T21:35:11 system#1f4f56a6) — Pre-Flight-Sprint-Dispatch Script deployed 2026-04-19 20:42 UTC mit 7 Gates: Atlas-session-size R36, operatorLock R47, Board-open_count, MC+Gateway-health, R49-Validator-CRITICAL, Git-dirty-state, Fre...
- **[0.85]** `semantic` (2026-04-19T21:35:11 system#967225ab) — Defense-Stack Pattern 2026-04-19: 12 automated cron-layers active für governance + memory + monitoring: session-freeze-watcher */5, r49-claim-validator */15, r48-board-hygiene hourly, daily-reflection...
- **[0.56]** `semantic` (2026-04-19T21:35:11 system#1db9c9d9) — 10 Karpathy-KB-Articles compiled 2026-04-19 20:46 UTC in vault/03-Agents/kb/: sprint-orchestration (27f/7r), receipt-discipline (34f/4r), deploy-contracts (12f/3r), atlas-hallucination-prevention (0f/...
- **[0.33]** `episodic` (2026-04-19T10:35:49 main#1971d4d8) — **Mission Control Ausfall!** `GET /api/tasks/...` → `500 Internal Server Error` `GET /api/health` → (leer/fehlerhaft) Gateway himself ist `live` (Port 18789), aber Mission Control (Port 3000) antworte...
- **[0.33]** `episodic` (2026-04-19T11:11:23 main#1dfb4382) — KONTEXT: - Gateway wurde OOM-killed (Peak 4.3 GB, R30 MCP-Zombies 12 akkumuliert).
- **[0.33]** `episodic` (2026-04-19T13:54:51 main#80bee875) — This will be cleaner and less error-prone than building a Python script to wrap the openclaw CLI calling the QMD MCP server.
- **[0.31]** `episodic` (2026-04-19T06:16:41 main#c6b889c9) — System: [2026-04-19 08:09:29 GMT+2] Gateway restart restart ok (gateway.restart) System: MC neugestartet um 08:02 - cleared degraded state + stale sessions.
- **[0.29]** `episodic` (2026-04-18T18:21:40 sre-expert#8e0d95dc) — updatedAt` - Build + Deploy: `npm run build` (grün), danach `./deploy.sh` erfolgreich - Vorher/Nachher KPI: `closed-24h 54 -> 91` - Regression: `new-blockers-24h=0`, `recovery-delta=0` (plausibel) - C...
- **[0.29]** `episodic` (2026-04-18T18:21:40 sre-expert#b64fc73c) — updatedAt` - Build + Deploy: `npm run build` (grün), danach `./deploy.sh` erfolgreich - Vorher/Nachher KPI: `closed-24h 54 -> 91` - Regression: `new-blockers-24h=0`, `recovery-delta=0` (plausibel) - C...
- **[0.29]** `episodic` (2026-04-18T18:21:40 sre-expert#f065d266) — updatedAt` - Build + Deploy: `npm run build` (grün), danach `./deploy.sh` erfolgreich - Vorher/Nachher KPI: `closed-24h 54 -> 91` - Regression: `new-blockers-24h=0`, `recovery-delta=0` (plausibel) - C...
- **[0.29]** `episodic` (2026-04-18T18:21:40 sre-expert#9033e3e3) — updatedAt` - Build + Deploy: `npm run build` (grün), danach `./deploy.sh` erfolgreich - Vorher/Nachher KPI: `closed-24h 54 -> 91` - Regression: `new-blockers-24h=0`, `recovery-delta=0` (plausibel) - C...
- **[0.29]** `episodic` (2026-04-18T18:21:40 sre-expert#7183c402) — updatedAt` - Build + Deploy: `npm run build` (grün), danach `./deploy.sh` erfolgreich - Vorher/Nachher KPI: `closed-24h 54 -> 91` - Regression: `new-blockers-24h=0`, `recovery-delta=0` (plausibel) - C...
- **[0.29]** `episodic` (2026-04-18T18:21:40 sre-expert#94afd194) — updatedAt` - Build + Deploy: `npm run build` (grün), danach `./deploy.sh` erfolgreich - Vorher/Nachher KPI: `closed-24h 54 -> 91` - Regression: `new-blockers-24h=0`, `recovery-delta=0` (plausibel) - C...
- **[0.29]** `episodic` (2026-04-18T18:21:40 sre-expert#27b752ae) — updatedAt` - Build + Deploy: `npm run build` (grün), danach `./deploy.sh` erfolgreich - Vorher/Nachher KPI: `closed-24h 54 -> 91` - Regression: `new-blockers-24h=0`, `recovery-delta=0` (plausibel) - C...
- **[0.29]** `episodic` (2026-04-18T18:21:40 sre-expert#89d13de0) — updatedAt` - Build + Deploy: `npm run build` (grün), danach `./deploy.sh` erfolgreich - Vorher/Nachher KPI: `closed-24h 54 -> 91` - Regression: `new-blockers-24h=0`, `recovery-delta=0` (plausibel) - C...
- **[0.29]** `episodic` (2026-04-18T18:21:40 sre-expert#9fc928b1) — updatedAt` - Build + Deploy: `npm run build` (grün), danach `./deploy.sh` erfolgreich - Vorher/Nachher KPI: `closed-24h 54 -> 91` - Regression: `new-blockers-24h=0`, `recovery-delta=0` (plausibel) - C...
- **[0.29]** `episodic` (2026-04-18T18:21:40 sre-expert#c91db290) — updatedAt` - Build + Deploy: `npm run build` (grün), danach `./deploy.sh` erfolgreich - Vorher/Nachher KPI: `closed-24h 54 -> 91` - Regression: `new-blockers-24h=0`, `recovery-delta=0` (plausibel) - C...
- **[0.29]** `episodic` (2026-04-18T19:19:18 main#ed9641df) — Build wurde gekillt (OOM?).
- **[0.29]** `episodic` (2026-04-18T19:19:18 main#8fe12e52) — Build wurde gekillt (OOM?).
- **[0.29]** `episodic` (2026-04-18T19:21:20 main#ffca227e) — Build läuft noch (OOM-Kandidat auf huebners).

## Related KB Articles

*(no related articles found)*

## Metadata

- **Topic keywords** (for future recompilation): build, deploy.sh, next.config, systemctl, .next, mc-service, gateway, v8-heap...
- **Related rules (declared)**: R7, R5, R26
- **Schema version**: KB-article v1-mvp

---

*Auto-compiled from 21 facts + 4 rules by `kb-compiler.py@v1-mvp`. Manual edits will be preserved where possible but may be overwritten on next compile — use `<!-- manual: start --> ... <!-- manual: end -->` to mark preserved sections (future feature).*