---
type: audit-report
date: 2026-04-29
status: complete
audit_id: ROUND-6-AUTONOMY-AUDIT-2-AGENT
agents: [live-system-audit, best-in-class-research]
tags: [autonomy, self-healing, follow-up-autonomy, dispatch-autonomy, sota, research]
related:
  - "[[stabilization-2026-04-29-full]]"
  - "[[sprint-closure-2026-04-29-schema-gate-ops]]"
  - "[[cron-per-job-walkthrough-2026-04-29]]"
---

# Autonomy Audit — Self-Healing + Follow-Up + Dispatch (2-Agent Deep-Dive)

## TL;DR

2 parallele Audits durchgeführt: **(1) Live-System** (read-only, 50 cron-jobs + lib-code + MC-API)
und **(2) Best-in-Class Research** (SOTA-Patterns 2025-2026 für Multi-Agent-Autonomie).

Ergebnis: System hat solide **Self-Healing-Foundation** (R51/R52/R53 Schema-Gates,
Reapers, Stale-Lock-Cleaner) und wenig-getestete **Follow-Up-Autonomy**
(`receipt-materializer` mit Approval-Gates). **Dispatch-Autonomy** läuft via
`auto-pickup.py` mit clean Locks. ABER: **5 P0-Gaps live**, alle aus heutigem Audit
mit konkreten Reproducer-Commands.

**SOTA-Vergleich:** Die größten Maturity-Gaps sind:
- Crash-durability (kein Temporal-style event-history-replay)
- Backpressure (cost-alert-watch nur Detection, no admission-control)
- Telemetry (keine OpenTelemetry GenAI conventions)
- Confidence-routed HITL (binary full/allowlist statt threshold-driven)

## Live-System P0 Findings

### 1. ⚠️ Rotation-Consumer Dead-Letter-Loop (KRITISCH, LIVE)

**Was:** `session-rotation-watchdog.py` schreibt seit >30min Emergency-Rotate-Signal
für Session `9f6d6cf5-720` mit **pct=257%** (3.5× über critical 95%-Threshold).
`auto-pickup.py` LIEST das Signal aber `ROTATION_CONSUMER_MODE=dry-run` (default) →
**`idempotent-skip-and-clear`** alle 30 Sekunden. Signal wird re-written jeden 2-min
Cycle. Atlas main session ist im kritischen Zustand für >30min, **keine echte Rotation**.

**Reproduce:**
```bash
ssh homeserver 'tail -50 /home/piet/.openclaw/workspace/logs/auto-pickup.log | grep ROTATION_SIGNAL'
ssh homeserver 'tail -10 /home/piet/.openclaw/workspace/logs/session-rotation-watchdog.log'
```

**Fix (minimal):** `AUTO_PICKUP_ROTATION_LIVE_APPROVED=1` + `AUTO_PICKUP_ROTATION_LIVE_COMMAND` setzen,
ODER signal-clear-condition fixen damit der Loop nicht spammt. **NICHT autonom executable** — Atlas-Lane.

### 2. mcp-taskboard-reaper PID-Resolution gebrochen aus cron-context

**Was:** Reaper logs `gateway_pid=unknown` in letzten 6 Runs trotz Gateway live (PID 3161302).
`systemctl --user show openclaw-gateway` aus cron-context returns empty (kein DBus session).
Layer-1 PID-equality-check matched nie, Fallback auf Layer-2 comm-match (still works).

**Fix (minimal):** Cron-prefix mit `XDG_RUNTIME_DIR=/run/user/1000 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus`.
Oder: `pgrep -fa "openclaw-gateway"` als alternative PID-discovery.
**Riskostufe:** LOW (Reaper läuft mit Layer-2-Fallback).

### 3. r48 Failed-Null-CompletedAt Tasks akkumulieren

**Was:** 45 Tasks haben `status=failed AND completedAt=null`. R48 logged sie als
`FAILED-NEEDS-ARCHIVE` 23× heute, **modifiziert nichts**. Deferred queue wächst unbeschränkt.

**Fix (minimal):** R48-Script erweitern: nach 24h `failed+null-completedAt` → auto-finalize
mit `failureReason='r48-auto-archive'` via `/admin-close` PATCH. Riskostufe LOW
(idempotent + age-gated).

### 4. finalize-Endpoint operator-gated für Cron

**Was:** `/api/tasks/[id]/finalize/route.ts` setzt `actorKinds: ['human']` — blockt jeden
cron auto-finalize. Hung-worker → finalize wird nie aufgerufen → state stays orphaned bis
Operator-Action.

**Fix (NICHT minimal):** `actorKinds` um `'system'` erweitern + dedicated cron-cleanup-script.
Erfordert MC-Code-Edit (Atlas-Lane).

### 5. R49 catches Hallucinations aber quarantiniert nicht

**Was:** R49 hat heute **8 WARNINGS** für non-existent task-IDs (`9f07d91b`, `abc44fbd`)
in 4 Cycles wiederholt. R49 alerts aber tut keinen Halt-Action. Atlas referenziert
weiterhin dieselben Fake-IDs.

**Fix (minimal):** R49 schreibt `/tmp/r49-halt-<sessionId>.flag` wenn >=N Halluzinationen
in M Minuten. auto-pickup.py prüft halt-flag vor Worker-Spawn, skipt Atlas-Sessions mit
flag aktiv. **Risiko:** MED (kann legit Atlas-Sessions blocken — gut throttle-tunen).

## Live-System P1 Improvements

| # | Item | Effort |
|---|---|---|
| P1.1 | gateway-memory-monitor: bei CRIT (≥5.5GB) → graceful restart statt nur alert | M |
| P1.2 | cpu-runaway-guard whitelist erweitern (claude/node mission-control) | S |
| P1.3 | R51 invariant für `tools.elevated.allowFrom` (verhindert Discord-User-Removal) | S |
| P1.4 | session-rotation-watchdog → live-mode bridge (rotation-consumer aktivieren) | L |
| P1.5 | autonomy-self-healing.ts: `dry-run` → `live-execute` für A0/A1 risk tiers | M |

## SOTA Comparison Matrix

| Aspect | OpenClaw | SOTA Pattern | Maturity-Gap |
|---|---|---|---|
| Recovery-Semantik | 14 Cron-Defenders + Surgical Patches | Reconciliation Loop (Kubernetes Operator-pattern) | MEDIUM |
| Crash-Durability | session-lock + auto-pickup retry | Temporal Event-History-Replay | **LARGE** |
| Failure-Isolation | mc-critical-alert + manual rollback | Circuit-breaker per Agent-Boundary | MEDIUM |
| Follow-Up-Generation | Operator-triggered ("Atlas next sprint") + receipt-materializer | Reflexion + Tree-of-Thoughts | **LARGE** |
| Self-Evaluation | Codex-review (manual ad-hoc) | Evaluator-Optimizer (separate model) | MEDIUM |
| Dispatch-Modell | Atlas + 5 specialists, claim-based | LangGraph Supervisor | SMALL |
| Autonomy-Gating | full/allowlist/approval (binary) | Confidence-routed HITL (CrewAI 2B-data-driven) | SMALL |
| Memory-Writes | DAG kb→graph→dashboard | WorldDB write-time Reconciler | MEDIUM |
| Backpressure | billing-alert + cost-alert (alerting only) | Token-bucket + priority lanes + admission control | MEDIUM |
| Telemetry | Per-component logs | OpenTelemetry GenAI semantic conventions | **LARGE** |
| HITL | Discord/Telegram operator-interface | Risk-tiered + escalation-ladder + confidence-routing | SMALL |

## Top 10 SOTA Recommendations (Prioritized)

| # | Pattern | Effort | Risk | Why fits |
|---|---|---|---|---|
| 1 | **Evaluator-Optimizer separate-model loop** für Sprint-Outputs | S | LOW | Lens partly does this; ICLR 2024 evidence external > intrinsic self-correct |
| 2 | **OpenTelemetry GenAI Semantic Conventions** | M | LOW | Replaces ad-hoc logs; one trace shows full agent fan-out; CNCF-standard |
| 3 | **Bounded T-A-O Loops + Satisfaction-Gate** | S | LOW | 80%×10=10% workflow success math is real |
| 4 | **Confidence-routed HITL** (extend full/allowlist/approval mit confidence-score) | M | LOW | CrewAI 2B-execution-data: gradual autonomy beats binary |
| 5 | **Token-bucket + Priority-Lane Admission Controller** | M | MED | TPM-aware Circuit-Breaker; ergänzt cost-alert-dispatcher |
| 6 | **Reflexion Episodic Lessons Buffer** per Agent | S | LOW | +11pp HumanEval ohne Fine-Tuning; replaces "morning recovery report" |
| 7 | **Reconciler-style Cron-Consolidation** | L | MED | 14 Cron-Defenders → 4-5 Reconciler; idempotent by design |
| 8 | **Circuit-Breakers Agent-zu-Agent** (error-rate, latency P95, semantic-contract) | M | LOW | Solves cascade-failure (08:09-08:34 outage pattern) |
| 9 | **Saga Compensation** für Multi-Step-Sprints | M | MED | Forge SRE work braucht das; current rollback ad-hoc |
| 10 | **Temporal/Inngest** für Long-Running Orchestration | L | HIGH | Eventual replacement of session-lock + auto-pickup; consolidates crons |

## Top 5 Anti-Patterns to Avoid

1. **Full-autonomy ohne termination-conditions** (AutoGPT/BabyAGI failure: infinite loops)
2. **Intrinsic self-correction only** (ICLR 2024: Models can't reliably self-correct)
3. **Same controller reconciling multiple Kinds** (Kubebuilder: one reconciler per concern)
4. **Naive exponential backoff under TPM pressure** (causes oscillation)
5. **"Fully autonomous" marketing** (CrewAI 2B-data: gradual outperforms)

## Quick-Wins Roadmap (von SOTA-Empfehlungen)

### Phase 1 (1-2 Tage, S/LOW)
- **Reflexion Lessons Buffer:** vault file pro Agent mit gelernten Patterns, pre-conditions next-sprint
- **Bounded T-A-O Termination:** explicit max-iter + satisfaction-gate in Atlas-Sprint-Plans
- **R49 Halt-Flag:** P0-Fix #5 — auto-quarantine hallucinating sessions
- **R48 Auto-Finalize:** P0-Fix #3 — clean accumulating failed-null-completedAt

### Phase 2 (3-5 Tage, M/LOW-MED)
- **Evaluator-Optimizer Pattern:** Lens als formal Pre-Merge-Gate für Sprint-Outputs
- **OpenTelemetry GenAI:** Trace-Header durch alle Agent-Calls
- **Circuit-Breakers** auf agent-to-agent boundaries
- **Confidence-routed HITL:** confidence-score zu jeder Autonomy-Decision

### Phase 3 (1-2 Wochen, M/MED-HIGH)
- **Token-Bucket Admission Controller** vor Gateway
- **Saga Compensation** für Multi-Step-Sprints
- **session-rotation-watchdog Live-Mode** (P0-Fix #1 echter Recovery-Pfad)

### Phase 4 (Architektur-Sprint, L/HIGH)
- **Reconciler-style Cron-Consolidation** (14 Defenders → 4-5 Reconciler)
- **Temporal/Inngest Migration** für Durable Execution

## Key References (Top 10)

1. [Anthropic — Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)
2. [Shinn et al. — Reflexion](https://arxiv.org/abs/2303.11366) (NeurIPS 2023)
3. [Yao et al. — Tree of Thoughts](https://arxiv.org/abs/2305.10601)
4. [Practical Guide to Production-Grade Agentic AI](https://arxiv.org/html/2512.08769v1) (Dec 2025)
5. [CrewAI Flows — Production Multi-Agent Guide 2026](https://www.jahanzaib.ai/blog/crewai-flows-production-multi-agent-guide)
6. [Temporal — Orchestrating Ambient Agents](https://temporal.io/blog/orchestrating-ambient-agents-with-temporal)
7. [LangGraph Supervisor](https://github.com/langchain-ai/langgraph-supervisor-py)
8. [OpenTelemetry GenAI Observability](https://opentelemetry.io/blog/2025/ai-agent-observability/)
9. [Backpressure Patterns for LLM Pipelines](https://tianpan.co/blog/2026-04-15-backpressure-llm-pipelines)
10. [Resilient Microservices Recovery Patterns](https://arxiv.org/html/2512.16959v1)

## Cross-Refs

- [[stabilization-2026-04-29-full]] — heute deployed: R51, R52, R53
- [[sprint-closure-2026-04-29-schema-gate-ops]] — Schema-Gate-Sprint
- [[cron-per-job-walkthrough-2026-04-29]] — 50-job per-job analysis
