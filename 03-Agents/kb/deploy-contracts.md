---
title: "Deploy Contracts & MC-Restart"
slug: deploy-contracts
last_compiled: 2026-04-19T20:46:30.335588Z
compiler: kb-compiler.py@v1-mvp
fact_count: 12
rule_count: 3
memory_level: 3
---


<!-- llm-synth: start -->
## 📖 Synthesis (LLM-generated, 2026-04-19)

*3-paragraph Operator-Synthese, auto-generiert via NVIDIA Nemotron. Template-Render darunter für Detail-Access.*

Der Kern dieses Themas besteht darin, das Risiko von Race‑Conditions zu eliminieren, die auftreten können, wenn Verträge gleichzeitig bereitgestellt werden, während das Mission‑Control‑System neu gestartet wird oder im degraded Zustand ist. Ohne geeignete Synchronisation führen parallele Deployments zu inkonsistenten Zuständen, veralteten Sessions und fehlgeschlagenen Vertragsverifikationen, was die Betriebssicherheit gefährdet. Der mc‑restart‑safe Wrapper und der Deploy‑Verify‑Contract‑Prozess schaffen eine deterministische Abfolge, die sicherstellt, dass ein Deployment nur nach erfolgreichem Build und nur ein einzelner Vorgang zur gleichen Zeit ausgeführt wird. Dadurch werden KPI‑Einbrüche verhindert und das System bleibt auch nach Neustarts stabil.

Die wichtigste Regel ist, stets zuerst `npm run build` auszuführen und nur bei einem grünen Ergebnis das Deploy‑Skript zu starten; dies stellt sicher, dass nur kompilierbarer Code weiterverarbeitet wird. Zweitens muss das eigentliche Deploy über den mc‑restart‑safe Wrapper erfolgen, der ein Sperrmechanismus bereitstellt, um parallele Ausführungen zu blockieren und gleichzeitig Neustarts des Systems abzufangen, ohne dass der Vorgang abbricht. Drittens folgt unmittelbar nach dem Deploy die Deploy‑Verify‑Contract‑Phase, bei der das bereitgestellte Vertragsartefakt auf Korrektheit geprüft wird; erst bei erfolgreicher Verifikation wird das Deployment als abgeschlossen angesehen, wodurch Regressionsfälle frühzeitig erkannt werden. Diese Muster zusammen reduzieren das Risiko von inkonsistenten Zuständen und verbessern

*Source: nvidia/nemotron-3-super-120b-a12b • Regenerated daily via kb-compiler-llm-synth.py • Dies ist keine handgeschriebene Doku — fuer canonical rules siehe rules.jsonl.*
<!-- llm-synth: end -->

# Deploy Contracts & MC-Restart

**Description:** Deploy-Verify-Contract, parallel-deploy-race prevention via mc-restart-safe wrapper.

**Compiled:** 2026-04-19T20:46:30.335588Z  
**Source:** 12 facts from workspace/memory/facts/*.jsonl, 3 rules from workspace/memory/rules.jsonl

## Key Rules

### R1 — Verify-After-Write ist Pflicht
*Status: active | Since: 2026-04-17*



### R46 — Parallel-Deploy-Serialization
*Status: active | Since: 2026-04-19*

Wenn mehrere Sub-Agents parallel laufen UND jeder einen systemctl --user restart mission-control + curl verify Contract im Prompt hat → Deploy-Race-Condition. Fix: sequenzieller Sprint-Flow ODER Deploy-Queue-Lock (nur ein MC-Restart gleichzeitig, Age...

### R7 — Kanonische Build-Sequenz (nicht `deploy.sh`)
*Status: active | Since: None*



## Key Facts (Top-20 by Importance)

- **[0.55]** `episodic` (2026-04-18T18:21:40 sre-expert#8e0d95dc) — updatedAt` - Build + Deploy: `npm run build` (grün), danach `./deploy.sh` erfolgreich - Vorher/Nachher KPI: `closed-24h 54 -> 91` - Regression: `new-blockers-24h=0`, `recovery-delta=0` (plausibel) - C...
- **[0.55]** `episodic` (2026-04-18T18:21:40 sre-expert#b64fc73c) — updatedAt` - Build + Deploy: `npm run build` (grün), danach `./deploy.sh` erfolgreich - Vorher/Nachher KPI: `closed-24h 54 -> 91` - Regression: `new-blockers-24h=0`, `recovery-delta=0` (plausibel) - C...
- **[0.55]** `episodic` (2026-04-18T18:21:40 sre-expert#f065d266) — updatedAt` - Build + Deploy: `npm run build` (grün), danach `./deploy.sh` erfolgreich - Vorher/Nachher KPI: `closed-24h 54 -> 91` - Regression: `new-blockers-24h=0`, `recovery-delta=0` (plausibel) - C...
- **[0.55]** `episodic` (2026-04-18T18:21:40 sre-expert#9033e3e3) — updatedAt` - Build + Deploy: `npm run build` (grün), danach `./deploy.sh` erfolgreich - Vorher/Nachher KPI: `closed-24h 54 -> 91` - Regression: `new-blockers-24h=0`, `recovery-delta=0` (plausibel) - C...
- **[0.55]** `episodic` (2026-04-18T18:21:40 sre-expert#7183c402) — updatedAt` - Build + Deploy: `npm run build` (grün), danach `./deploy.sh` erfolgreich - Vorher/Nachher KPI: `closed-24h 54 -> 91` - Regression: `new-blockers-24h=0`, `recovery-delta=0` (plausibel) - C...
- **[0.55]** `episodic` (2026-04-18T18:21:40 sre-expert#94afd194) — updatedAt` - Build + Deploy: `npm run build` (grün), danach `./deploy.sh` erfolgreich - Vorher/Nachher KPI: `closed-24h 54 -> 91` - Regression: `new-blockers-24h=0`, `recovery-delta=0` (plausibel) - C...
- **[0.55]** `episodic` (2026-04-18T18:21:40 sre-expert#27b752ae) — updatedAt` - Build + Deploy: `npm run build` (grün), danach `./deploy.sh` erfolgreich - Vorher/Nachher KPI: `closed-24h 54 -> 91` - Regression: `new-blockers-24h=0`, `recovery-delta=0` (plausibel) - C...
- **[0.55]** `episodic` (2026-04-18T18:21:40 sre-expert#89d13de0) — updatedAt` - Build + Deploy: `npm run build` (grün), danach `./deploy.sh` erfolgreich - Vorher/Nachher KPI: `closed-24h 54 -> 91` - Regression: `new-blockers-24h=0`, `recovery-delta=0` (plausibel) - C...
- **[0.55]** `episodic` (2026-04-18T18:21:40 sre-expert#9fc928b1) — updatedAt` - Build + Deploy: `npm run build` (grün), danach `./deploy.sh` erfolgreich - Vorher/Nachher KPI: `closed-24h 54 -> 91` - Regression: `new-blockers-24h=0`, `recovery-delta=0` (plausibel) - C...
- **[0.55]** `episodic` (2026-04-18T18:21:40 sre-expert#c91db290) — updatedAt` - Build + Deploy: `npm run build` (grün), danach `./deploy.sh` erfolgreich - Vorher/Nachher KPI: `closed-24h 54 -> 91` - Regression: `new-blockers-24h=0`, `recovery-delta=0` (plausibel) - C...
- **[0.55]** `episodic` (2026-04-19T06:16:41 main#c6b889c9) — System: [2026-04-19 08:09:29 GMT+2] Gateway restart restart ok (gateway.restart) System: MC neugestartet um 08:02 - cleared degraded state + stale sessions.
- **[0.55]** `episodic` (2026-04-19T06:16:41 main#5347da63) — Nach Restart: tasks.json neu laden, degraded State reset, stale Sessions gone.

## Related KB Articles

- [Incident Response & RCA](incident-response.md)
- [Receipt Discipline](receipt-discipline.md)

## Metadata

- **Topic keywords** (for future recompilation): deploy, mc-restart-safe, systemctl, restart, R42, R46, flock, mc-deploy.lock...
- **Related rules (declared)**: R42, R46, R1, R7
- **Schema version**: KB-article v1-mvp

---

*Auto-compiled from 12 facts + 3 rules by `kb-compiler.py@v1-mvp`. Manual edits will be preserved where possible but may be overwritten on next compile — use `<!-- manual: start --> ... <!-- manual: end -->` to mark preserved sections (future feature).*