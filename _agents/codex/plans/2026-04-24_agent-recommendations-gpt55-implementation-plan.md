---
status: done
owner: codex
created: 2026-04-24T20:09:25Z
scope:
  - agent-recommendations
  - model-routing
  - gpt-5.5-evaluation
  - implementation-plan
sources:
  - https://developers.openai.com/api/docs/models
  - https://developers.openai.com/api/docs/models/gpt-5.5
  - https://developers.openai.com/api/docs/models/gpt-5.5-pro
  - https://openai.com/index/new-tools-for-building-agents/
  - https://openai.github.io/openai-agents-js/guides/tracing/
  - https://www.anthropic.com/engineering/multi-agent-research-system
  - https://docs.langchain.com/oss/python/langchain/multi-agent/handoffs
  - https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
---

# Agent Recommendations + GPT-5.5 Implementation Plan

## Executive Verdict

OpenClaw ist aktuell stabil genug fuer gezielte Agenten-Optimierung, aber nicht fuer einen breiten Modell-/Agenten-Umbau. Die beste naechste Stufe ist: Rollen schaerfen, Status-/Kosten-Signale korrigieren, Spark stabilisieren, dann GPT-5.5 als explizite Eskalationsspur fuer wenige hochwertige Aufgaben testen.

Nicht empfohlen: GPT-5.5 sofort als globaler Default fuer alle Agenten. GPT-5.5 ist laut OpenAI das neue starke Modell fuer komplexe Reasoning-/Coding-Arbeit, kostet aber etwa doppelt so viel wie GPT-5.4 und hat bei sehr grossen Prompts einen zusaetzlichen Long-Context-Aufschlag. GPT-5.5 pro ist fuer normale OpenClaw-Worker noch weniger passend, weil es sehr teuer und langsam ist und laut OpenAI fuer harte Probleme teils mehrere Minuten laufen kann.

Empfohlen: GPT-5.5 nur fuer Atlas-Synthese, schwierige Forge-RCA, komplexe Pixel-UI-Architektur und finale Review-Gates. MiniMax bleibt fuer Lens/James wertvoll, aber die Statuslogik muss Tokenplan/Abo-Semantik konsistent behandeln.

## Live IST Snapshot

Probe window: 2026-04-24T20:09-20:18Z.

| Signal | Live Value | Interpretation |
|---|---:|---|
| `/api/health` | `status=ok`, execution ok, costs ok | System ist arbeitsfaehig |
| Worker proof | `status=ok`, `openRuns=1`, `criticalIssues=0` | keine Worker-Criticals; ein legitimer Open Run war kurz sichtbar |
| Pickup proof | `pendingPickup=0`, `claimTimeouts=0`, `criticalFindings=0` | aktiver Pickup-Pfad gruen |
| Runtime soak proof | zeitweise `degraded`, dann wieder `ready`; `blockedBy=[]` | warning/self-lock transient, nicht blockierend |
| Board snapshot | `2469` bytes, 3 draft tasks, 523 archive tasks | Live-Board schlank; Archive waechst |
| Active/Draft tasks | 3 draft tasks | Pixel/Spark warning-only degraded, Forge metrics endpoint |
| Today task stats | James 8/8 done; SRE 16/20 done; Atlas/Main 7/12 done; Spark 6/9 done | James aktuell am saubersten; Spark/Main hatten Failure-Historie |
| Cost health | `/api/health` costs ok; cost-governance health critical 0 | kein harter Kostenblock |
| Budget-status | MiniMax und OpenAI-Codex `tone=critical` in `/api/costs/budget-status` | Status-/Threshold-Semantik ist noch inkonsistent |

## Current Agent Model Matrix

Evidence: `/home/piet/.openclaw/openclaw.json`.

| Agent | Role | Current Primary | WIP | Current Fit | Recommendation |
|---|---|---|---:|---|---|
| Atlas / `main` | Orchestrator, planning, handoff | `openai-codex/gpt-5.4` | 3 | gut fuer Alltag | GPT-5.5 nur fuer weekly/deep planning, final architecture decisions, failed-sprint synthesis |
| Forge / `sre-expert` | Infra, runtime, Mission Control implementation | `openai-codex/gpt-5.3-codex` | 2 | gut fuer enge Code-Fixes, aber viele historische failures | Weiter als Implementer, GPT-5.5 optional fuer RCA/architecture-review before write |
| Pixel / `frontend-guru` | UI, UX, components | `openai-codex/gpt-5.4` | 2 | passend | GPT-5.5 nur fuer komplexe UX/IA-Reviews, nicht fuer kleine UI-Fixes |
| Lens / `efficiency-auditor` | Kosten, Noise, Output, Efficiency | `minimax/MiniMax-M2.7-highspeed` | 1 | gut fuer schnelle Audit-/Policy-Arbeit | Behalten; P0 ist Status-/Tokenplan-Semantik, nicht Modellwechsel |
| James | External validation, research cross-check | `minimax/MiniMax-M2.7-highspeed` | 2 | heute 8/8 done, sehr gutes Signal | Behalten; striktere Quellen-/Receipt-Contracts statt Modellwechsel |
| Spark | Short analysis, ideas, small read-only checks | `openai-codex/gpt-5.3-codex-spark` | 1 | instabiler als gewuenscht; ein aktueller Research+E2E Task failed after 4 attempts | Vor kritischer Nutzung Spark-RCA + A/B mit `gpt-5.4-mini`; GPT-5.5 nicht als Default |

## Web Research Findings

### GPT-5.5

- OpenAI Docs listen GPT-5.5 als neues Frontier-Modell fuer komplexe Reasoning-/Coding-/Professional-Workflows; im Modellvergleich steht GPT-5.5 bei `$5` input und `$30` output pro 1M Tokens, GPT-5.4 bei `$2.50` und `$15`. Quelle: https://developers.openai.com/api/docs/models
- GPT-5.5 hat laut Modellseite 1M Kontext, 128K max output, Reasoning Token Support, Text/Bild input und Text output. Quelle: https://developers.openai.com/api/docs/models/gpt-5.5
- Fuer Prompts ueber 272K input tokens nennt OpenAI einen Aufschlag: 2x input und 1.5x output fuer die volle Session. Quelle: https://developers.openai.com/api/docs/models/gpt-5.5
- GPT-5.5 pro ist fuer schwierige Probleme gedacht, aber mit `$30` input und `$180` output pro 1M Tokens sehr teuer; OpenAI weist darauf hin, dass manche Requests mehrere Minuten dauern koennen und Background Mode sinnvoll ist. Quelle: https://developers.openai.com/api/docs/models/gpt-5.5-pro

Implication for OpenClaw: GPT-5.5 ist ein Eskalationsmodell, kein Cron-/Heartbeat-/Worker-Default.

### Multi-Agent Architecture

- OpenAI positioniert Agents SDK um klare Agenten, Handoffs, Guardrails sowie Tracing/Observability. Quelle: https://openai.com/index/new-tools-for-building-agents/
- OpenAI Agents SDK Tracing erfasst Agent runs, model generations, tool calls, handoffs, guardrails und custom events. Quelle: https://openai.github.io/openai-agents-js/guides/tracing/
- Anthropic beschreibt multi-agent als besonders wertvoll bei parallelisierbarer Recherche, grossen Kontexten und vielen Tools; weniger passend, wenn alle Agents denselben Kontext teilen muessen oder viele Abhaengigkeiten haben. Quelle: https://www.anthropic.com/engineering/multi-agent-research-system
- LangGraph/Handoff-Dokumentation betont, dass bei Handoffs kontrolliert werden muss, welche Nachrichten weitergegeben werden, um Kontext-Bloat und inkonsistente Conversation History zu vermeiden. Quelle: https://docs.langchain.com/oss/python/langchain/multi-agent/handoffs
- Anthropic Eval-Guide betont: Agenten-Evals sollten outcome-basiert sein, komplette Traces/Trajectories erfassen und bei komplexeren Agenten mehrere Grader/Assertions nutzen. Quelle: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents

Implication for OpenClaw: Mehr Agenten oder staerkere Modelle loesen nicht automatisch Stabilitaet. Der groesste Hebel liegt in klaren Handoff-Contracts, kleinerem Kontext, besseren Evals und beobachtbaren Outcomes.

## Recommendations By Agent

### Atlas / Main

Decision: Atlas bleibt Orchestrator, aber WIP und Handoff-Scope muessen streng bleiben.

What Atlas should do:
- Nur 1 Sprint gleichzeitig orchestrieren, ausser Tasks sind wirklich unabhaengig.
- GPT-5.5 nur fuer:
  - final architecture synthesis,
  - failed-sprint postmortems,
  - cross-agent planning,
  - high-risk migration decisions.
- Keine normale Heartbeat-/Cron-/Canary-Arbeit auf GPT-5.5.

Implementation plan:
1. Add a documented `modelEscalationPolicy` concept: `default`, `escalate:gpt-5.5`, `prohibit:gpt-5.5`.
2. Atlas task prompt must declare: why escalation is needed, expected output, max context budget, rollback/no-write policy.
3. Gate: one Atlas GPT-5.5 dry planning task with no writes; compare output quality vs GPT-5.4 on same source snapshot.

Quality gate:
- Worker proof critical 0 before/after.
- Task result contains actionable plan, source evidence, residual risk.
- No additional spawned tasks unless explicitly asked.

### Forge / SRE Expert

Decision: Forge remains primary implementer for Mission Control/runtime, but should not own broad chaos or architecture changes without a preflight contract.

What Forge should do next:
- P0: Finish `/api/costs/budget-status` tokenplan threshold semantics.
- P1: Metrics endpoint for archive/success/cycle aggregates.
- P2: Auto-pickup systemd-service regression tests and unit metadata.

Model recommendation:
- Keep `openai-codex/gpt-5.3-codex` for small code changes.
- Use GPT-5.5 only for RCA/planning before a risky infra change, not for every patch.

Quality gate:
- Focused test + `npm run typecheck`.
- Live proof endpoint unchanged/read-only where relevant.
- One targeted canary if worker/runtime touched.

### Pixel / Frontend Guru

Decision: Pixel should be used more narrowly: operator clarity, visible warning semantics, UI error prevention.

What Pixel should do next:
- Implement warning-only degraded display so `degraded` without blockers is understandable.
- Keep Board/UI heartbeat on lightweight snapshot paths.
- Add one browser smoke for task details and one dashboard smoke after warning display change.

Model recommendation:
- Keep GPT-5.4 for UI.
- GPT-5.5 only for a larger IA/UX audit or complex design-system consolidation.

Quality gate:
- No client-side exception.
- Snapshot payload remains <100 KB.
- Browser console clean on dashboard/task detail.

### Lens / Efficiency Auditor

Decision: Lens has the best fit for cost/noise/policy because it is cheap and focused, but the current budget-status semantics must be fixed.

What Lens should do next:
- P0 analysis for Minimax/OpenAI-Codex budget-status mismatch:
  - `/api/health` costs ok,
  - cost-governance critical 0,
  - but `/api/costs/budget-status` marks MiniMax/OpenAI-Codex critical due generic flatrate token threshold.
- Define tokenplan display rules:
  - tokenplan usage = warning/observe,
  - no auto-reroute,
  - no "pool depletion" for subscription/tokenplan paths,
  - separate RPM/TPM warning from money budget.

Model recommendation:
- Keep MiniMax highspeed primary.
- Do not move Lens to GPT-5.5.

Quality gate:
- `/api/health` remains ok.
- `/api/costs/budget-status` no longer renders MiniMax Tokenplan as hard critical unless actual provider error/quota rejection exists.
- Discord #status wording: observe/warning, not hard block.

### James

Decision: James is currently strong for external cross-checks and completed 8/8 today. Keep it as validation/research agent, not implementer.

What James should do next:
- External source validation for cost/model assumptions.
- Source-backed release checks for GPT-5.5, OpenRouter and MiniMax.
- Independent review of Atlas/Forge plans before implementation.

Model recommendation:
- Keep MiniMax highspeed primary.
- Require citation/result contract for all research tasks.

Quality gate:
- Every result has source list, confidence, date checked, and "what changed since local assumption".
- No generic "accepted/completed" result summaries.

### Spark

Decision: Spark needs stabilization before it owns critical research+E2E tasks.

Live evidence:
- Latest Spark task `[Research+E2E][Spark] GPT-5.3 Codex Spark Stand pruefen...` failed after 4 attempts.
- Spark canary itself passed earlier, so the issue is not total pickup failure; likely task complexity/model/receipt/runtime mismatch.

What Spark should do next:
- Run a read-only RCA on its failed task:
  - Was failure model-related, timeout-related, prompt-contract-related, or receipt-related?
- A/B test Spark primary:
  - current `openai-codex/gpt-5.3-codex-spark`,
  - `openai-codex/gpt-5.4-mini`,
  - MiniMax highspeed fallback only for short synthesis.

Model recommendation:
- Do not switch Spark to GPT-5.5 by default.
- Consider GPT-5.4-mini as safer primary if A/B shows better terminal receipt and lower failure rate.

Quality gate:
- 3 small Spark tasks in a row terminal `done/result`.
- No open run left behind.
- Result summaries include concrete evidence.

## Proposed Implementation Sprints

### S-A1 P0 - Cost/Status Semantics Finalization

Owner: Lens analysis, Forge implementation, James external check.

Goal:
Make Minimax/OpenAI-Codex subscription/tokenplan reporting consistent across `/api/health`, `/api/costs/anomalies`, `/api/ops/cost-governance-proof`, `/api/costs/budget-status`, and Discord #status.

Why first:
The operator explicitly flagged Minimax status noise. Live data shows the first fix reduced health/governance criticals, but budget-status still marks MiniMax critical.

Gate:
- `curl /api/costs/budget-status` shows MiniMax tokenplan as observe/warn, not hard critical.
- #status text says no auto-reroute/no hard block for tokenplan.
- Cost governance health critical remains 0.
- Targeted cost tests + typecheck.

### S-A2 P1 - Spark Reliability + Model A/B

Owner: Spark read-only RCA, Forge if fix is needed.

Goal:
Determine why Spark failed a research+E2E task after 4 attempts and whether `gpt-5.4-mini` is a better primary than `gpt-5.3-codex-spark`.

Gate:
- RCA report identifies root category.
- Three tiny Spark tasks pass consecutively.
- No runtime/pickup criticals.
- No model default change until A/B evidence is documented.

### S-A3 P1 - GPT-5.5 Escalation Lane

Owner: Atlas.

Goal:
Add a policy, not a broad default switch: GPT-5.5 is allowed only for high-value planning/RCA/final review tasks with explicit reason and context budget.

Gate:
- One read-only Atlas GPT-5.5 planning canary.
- Compare with GPT-5.4 result quality.
- Keep default primary unchanged unless evidence shows clear value.

### S-A4 P2 - Agent Handoff Contract Hardening

Owner: Forge + James.

Goal:
Turn current prompt-level receipt quality rules into measurable soft/hard guards:
- terminal result must not be generic,
- handoff must include owner, task id, source evidence, done/open/residual risk,
- failed/blocked must include exact blocker category.

Gate:
- James/Forge/Pixel canary result summaries pass contract.
- UI shows weak result warning where applicable.

### S-A5 P2 - Observability/Tracing Alignment

Owner: Lens + Forge.

Goal:
Bring OpenClaw closer to modern agent observability patterns:
- trace id per task/run,
- handoff span/event,
- model/provider used,
- terminal outcome,
- cost/status mapping.

Gate:
- One task can be traced from dispatch -> claim -> heartbeat -> result -> cost attribution.
- Existing proof endpoints remain read-only.

## Recommended Next Dispatch Order

1. Lens: `S-A1` analysis, no code.
2. James: external source check for S-A1 assumptions and GPT-5.5 release details.
3. Forge: implement S-A1 if Lens+James agree.
4. Spark: S-A2 RCA/A-B, read-only first.
5. Atlas: S-A3 GPT-5.5 escalation-lane planning canary.

Do not run all five simultaneously. Start with S-A1 because it directly affects operator trust in #status and prevents false reroute decisions.

## Operator-Facing Summary

The team does not need more agents right now. It needs stronger contracts, cleaner status truth, and selective model escalation. GPT-5.5 should become the "expensive brain for hard planning/review", not the engine for heartbeat, cron, cheap audits or every worker.

Discord posts:
- `1497329987303510158`
- `1497329989295673585`
