---
status: done
owner: codex
created: 2026-04-24T20:24:00Z
scope:
  - autonomous-openclaw
  - atlas-follow-task-generation
  - self-healing
  - self-improvement
  - risk-governance
sources:
  - https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/
  - https://openai.github.io/openai-agents-python/guardrails/
  - https://developers.openai.com/api/docs/guides/evaluation-best-practices
  - https://openai.github.io/openai-agents-js/guides/tracing/
  - https://www.anthropic.com/research/trustworthy-agents
  - https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
  - https://www.anthropic.com/engineering/multi-agent-research-system
---

# Autonomous Self-Healing OpenClaw Plan

## Executive Verdict

OpenClaw ist nah an einer sinnvollen Autonomie-Stufe, aber noch nicht bereit fuer unbegrenztes Selbst-Dispatching. Der naechste Schritt ist kein groesserer Agent-Schwarm, sondern ein kontrollierter Autonomie-Kern:

`Proofs -> Findings -> Recommendations -> Risk Tier -> Candidate Tasks -> Approval/Auto-Dispatch -> Verification -> Memory/Learning`

Aktuell sind mehrere Teile bereits vorhanden:
- Proof-Endpunkte: Health, Pickup, Worker-Reconciler, Runtime-Soak, Cost-Governance.
- Mission-Control Taskboard mit Dispatch/Claim/Receipt.
- Auto-Pickup und Worker-Runs.
- Vault als durable Plan-/Report-Speicher.
- Atlas als Orchestrator.

Was fehlt:
- Ein einheitliches Finding-/Recommendation-Schema.
- Eine Policy, wann Atlas aus Empfehlungen selbst Tasks erzeugen darf.
- Harte Risk-Tiers mit Mutationsgrenzen.
- Ein Regression/Eval-Harness fuer Agentenentscheidungen.
- Ein Learning-Ledger, das "Fix hat geholfen" von "Fix war nur Aktivitaet" trennt.
- Duplicate-/Task-Flood-Schutz.

## Source-Based Principles

1. OpenAI beschreibt Agenten als Kombination aus Modell, Tools und klaren Instructions/Guardrails. Nicht jedes Problem braucht das staerkste Modell; kleinere Modelle sind fuer einfache Aufgaben oft sinnvoller. Quelle: https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/
2. OpenAI empfiehlt, Multi-Agent-Systeme nicht frueh zu erzwingen; die Entscheidung fuer Multi-Agent-Architektur soll durch Evals getrieben sein. Quelle: https://developers.openai.com/api/docs/guides/evaluation-best-practices
3. Guardrails muessen vor Tool-Ausfuehrung wirken, wenn Side Effects oder Kosten vermieden werden sollen. OpenAI Agents SDK unterscheidet parallele und blockierende Guardrails; blockierende Guardrails verhindern Tool-Ausfuehrung vorab. Quelle: https://openai.github.io/openai-agents-python/guardrails/
4. OpenAI Agents SDK Tracing macht Agent-Runs, Tool Calls, Handoffs und Guardrail Events sichtbar. Das bestaetigt, dass OpenClaw tracebare Task-/Run-Ketten als Autonomie-Basis braucht. Quelle: https://openai.github.io/openai-agents-js/guides/tracing/
5. Anthropic definiert Agenten als selbstgerichtete Loops aus Planen, Handeln, Beobachten, Anpassen und ggf. Human Check-in. Quelle: https://www.anthropic.com/research/trustworthy-agents
6. Anthropic betont, dass Agenten ohne Evals nach der Prototyping-Phase "blind" werden: Man kann Regressionen, Kosten, Latenz und Fehler nicht belastbar unterscheiden. Quelle: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
7. Anthropic beschreibt Multi-Agent-Systeme als besonders passend fuer parallelisierbare, breite Recherche oder grosse Kontextmengen; sie sind weniger geeignet, wenn alle Agents denselben Kontext teilen muessen oder viele enge Abhaengigkeiten haben. Quelle: https://www.anthropic.com/engineering/multi-agent-research-system

## Live IST

Probe window: 2026-04-24T20:09-20:20Z.

| Area | Live State | Meaning |
|---|---|---|
| Health | `/api/health status=ok` | Basis stabil |
| Pickup | `pendingPickup=0`, `claimTimeouts=0`, `criticalFindings=0` | aktiver Worker-Pickup gruen |
| Worker proof | `criticalIssues=0`, `openRuns=1` zeitweise | keine Criticals, legitime/self-lock Runs koennen kurzfristig degradieren |
| Runtime soak | transient `degraded`, dann `ready`, `blockedBy=[]` | Warning-only Zustandswechsel muessen besser erklaert werden |
| Board | 526 Tasks, 3 draft, 523 archive | Task-Flood-Schutz wichtig |
| Cost status | Health/Governance ok, aber Budget-Status meldet MiniMax/OpenAI-Codex kritisch | Statuswahrheit noch nicht einheitlich |
| Agent performance today | James 8/8 done; Spark hatte einen 4-attempt Failure; SRE viele historische failures | Agenten sollten unterschiedliche Autonomie-Level bekommen |

## Target Architecture

### Control Loop

```text
          ┌─────────────────────┐
          │  Read-only Proofs   │
          │ health/pickup/cost  │
          └──────────┬──────────┘
                     │
                     ▼
          ┌─────────────────────┐
          │ Finding Classifier  │
          │ severity/risk/scope │
          └──────────┬──────────┘
                     │
                     ▼
          ┌─────────────────────┐
          │ Recommendation Bank │
          │ one issue -> action │
          └──────────┬──────────┘
                     │
                     ▼
          ┌─────────────────────┐
          │ Risk Tier Gate      │
          │ auto/propose/hold   │
          └──────────┬──────────┘
                     │
      ┌──────────────┼─────────────────┐
      ▼              ▼                 ▼
  Auto Task     Operator Approval   Blocked Plan
  low risk      medium risk         high risk
      │              │
      └──────┬───────┘
             ▼
   Dispatch -> Claim -> Heartbeat -> Terminal Receipt
             │
             ▼
      Verification Gate
             │
             ▼
      Learning Ledger / Vault Report
```

### Autonomy Levels

| Level | Name | Allowed Behavior | Examples | Human Gate |
|---:|---|---|---|---|
| A0 | Observe only | Proofs, reports, recommendations | daily audits, live dashboards | no |
| A1 | Auto-create draft | Atlas creates draft tasks from findings | warning-only degraded UI task | no, but no dispatch |
| A2 | Auto-dispatch read-only | Atlas dispatches read-only audits/canaries | cost RCA, source verification, proof diff | no if budget/locks green |
| A3 | Auto-dispatch reversible small fix | Atlas dispatches one bounded fix with rollback | typo/config text, test-only guard, read-only endpoint shape | policy gate required |
| A4 | Propose-only mutating infra | Plan but do not execute | crontab, auto-pickup core, restarts, provider routing | operator approval |
| A5 | Forbidden autonomous | never self-execute | secrets, destructive git, broad rewrites, R19/R50 changes | explicit operator session only |

The near-term target is A2 as default and A3 for narrowly defined small fixes. A4/A5 remain proposal-only.

## What Is Missing

### M1 - Canonical Finding Schema

Today each proof emits useful data, but the actionability is inconsistent. Needed:

```json
{
  "schemaVersion": "finding.v1",
  "id": "cost-tokenplan-critical-tone-minimax",
  "source": "cost-governance-proof",
  "severity": "warning",
  "riskTier": "A2",
  "ownerAgent": "efficiency-auditor",
  "evidence": [{"path": "/api/costs/budget-status", "value": "minimax tone=critical"}],
  "recommendedAction": "create-readonly-rca-task",
  "dedupeKey": "cost-status:minimax-tokenplan-tone",
  "expiresAt": "2026-04-25T20:00:00Z"
}
```

### M2 - Recommendation -> Task Synthesizer

Atlas needs a deterministic script/API that turns findings into task candidates. This must not be free-form prompt-only.

Required fields:
- title
- assigned_agent
- riskTier
- source finding IDs
- definition of done
- anti-scope
- rollback/verify
- max runtime
- max spawned children
- duplicate key

### M3 - Risk Policy Engine

Before dispatch, every candidate task needs a policy decision:

| Risk Factor | Auto Allowed? |
|---|---|
| Read-only API audit | yes, A2 |
| Browser/UI smoke | yes, A2 |
| Local test-only change | maybe, A3 |
| Mission Control source patch | only if narrowly scoped and tests known, A3 |
| Runtime script/core worker change | proposal first, A4 |
| Restart/systemctl/kill/crontab/provider routing | proposal first, A4 |
| Secrets, destructive git, broad rewrite | no, A5 |

### M4 - Duplicate/Flood Control

Atlas must not turn one noisy proof into ten tasks.

Needed:
- `dedupeKey` per finding.
- `cooldownMinutes` per dedupeKey.
- max new tasks per hour.
- max active tasks per agent.
- no replacement task if original is still active unless explicitly superseded.

### M5 - Verification Gates

Autonomy only counts if every self-action proves outcome.

Minimum gates:
- preflight proof snapshot,
- terminal receipt,
- targeted tests or probes,
- postflight proof snapshot,
- delta summary,
- rollback path if regression detected.

### M6 - Learning Ledger

The system needs a durable ledger that says whether the action improved the metric. Without it, it can generate activity but not improvement.

Suggested file or endpoint:
- `data/autonomy-learning-ledger.jsonl` or vault report mirror.

Record:
- finding id,
- action id/task id,
- expected metric,
- pre value,
- post value,
- verdict: improved / neutral / worsened / inconclusive,
- next recommendation.

### M7 - Eval Suite

Use real production traces, not toy prompts.

Initial eval set:
- 10 successful worker canaries.
- 10 historical claim-timeout incidents.
- 10 cost/status anomalies.
- 10 UI client-error or payload incidents.
- 10 cron/heartbeat findings.

Each eval should grade:
- correct owner agent,
- correct risk tier,
- no mutation beyond scope,
- useful DoD,
- duplicate avoidance,
- verification plan quality.

## Main Risks

| Risk | Why It Matters | Control |
|---|---|---|
| Task flood | Atlas could convert noisy warnings into many drafts/dispatches | dedupeKey + max tasks/hour + WIP gate |
| False self-heal | System marks action successful because task completed, not because metric improved | pre/post metric delta + learning ledger |
| Unsafe mutation | Agent "fixes" runtime config or restarts services autonomously | A4/A5 proposal-only policy |
| Retry loops | Same failed action repeats with new wording | retry cap + cooldown + failureCategory |
| Context bloat | Autonomy agents read too much and degrade sessions | R51-R53 caps + summary-only task payloads |
| Model cost runaway | GPT-5.5 or pro used for cheap recurring tasks | model escalation policy + budget gate |
| Eval gaming | Agents optimize result text instead of real outcome | outcome-based gates from live proof endpoints |
| Stale Vault truth | Plans say planned/done incorrectly | live proof first, vault second |
| Cross-agent conflict | Two agents edit same scope | coordination live check and file ownership |
| Security boundary drift | Handoffs/tool calls bypass guardrails | risk-tier policy at dispatch, not prompt-only |

## Dedicated Implementation Plan

### Sprint AUT-1 - Autonomy Finding Schema + Registry

Owner: Forge implementation, Lens review.

Scope:
- Define `AutonomyFinding` and `AutonomyRecommendation` types.
- Build read-only adapter that normalizes outputs from:
  - health,
  - pickup-proof,
  - worker-reconciler-proof,
  - runtime-soak-proof,
  - cost-governance-proof,
  - context-budget-proof.
- No task creation yet.

Acceptance:
- New read-only endpoint or script returns normalized findings.
- Duplicate keys stable.
- Tests include at least cost-tokenplan-warning and worker-open-run examples.

### Sprint AUT-2 - Candidate Task Synthesizer Dry Run

Owner: Atlas + Forge.

Scope:
- Convert normalized findings into draft task candidates.
- Default mode dry-run only.
- No HTTP mutation unless `--execute --finding-id <id>` and risk tier permits.

Acceptance:
- Dry-run produces exactly one task candidate per unique finding.
- Candidate has DoD, anti-scope, owner, riskTier, verify command.
- No duplicate for existing draft/active task with same dedupeKey.

### Sprint AUT-3 - Risk Tier Policy Gate

Owner: Lens policy, Forge implementation, James external review.

Scope:
- Implement A0-A5 policy table.
- Enforce:
  - A2 auto-dispatch read-only only.
  - A3 small-fix only when rollback/test plan exists.
  - A4/A5 proposal-only.

Acceptance:
- Unit tests for each tier.
- Live dry-run classifies current findings correctly.
- No runtime config/core worker mutation can auto-dispatch.

### Sprint AUT-4 - Self-Heal Execution Lane

Owner: Atlas orchestration, Forge implementation.

Scope:
- Allow exactly one low-risk self-heal at a time.
- Preflight -> dispatch -> wait terminal -> postflight -> verdict.
- Initial allowed classes:
  - warning-only UI/report task,
  - cost/status text semantics,
  - read-only proof performance RCA,
  - canary/audit verification.

Acceptance:
- One real self-heal task completes.
- Learning ledger records pre/post.
- If postflight worsens, system creates rollback/proposal task, not another blind fix.

### Sprint AUT-5 - Eval Harness From Production Traces

Owner: Spark RCA/eval, James source review, Lens scoring.

Scope:
- Build 50-case initial eval set from OpenClaw history.
- Graders:
  - risk tier correct,
  - owner correct,
  - no duplicate,
  - verification sufficient,
  - expected metric explicit.

Acceptance:
- Baseline score recorded.
- Any autonomy policy change must pass eval suite before enabling auto-dispatch.

### Sprint AUT-6 - GPT-5.5 Escalation Lane For Autonomy

Owner: Atlas.

Scope:
- GPT-5.5 can be used for:
  - complex RCA synthesis,
  - policy conflicts,
  - final plan review.
- GPT-5.5 cannot be used for:
  - cron heartbeat,
  - cheap read-only checks,
  - every self-heal task,
  - long-context raw log dumps.

Acceptance:
- One read-only GPT-5.5 autonomy review task.
- Compare to GPT-5.4 baseline.
- Escalation only if value is materially better.

## First 7-Day Roadmap

### Day 1

- Fix S-A1 cost/status semantics first because false critical status undermines operator trust.
- Create AUT-1 schema in dry-run.

### Day 2

- AUT-2 synthesizer dry-run.
- Use current 3 draft tasks as dedupe test cases.

### Day 3

- AUT-3 risk policy gate.
- No auto-dispatch yet except read-only canary.

### Day 4

- First A2 autonomous read-only task:
  - Atlas creates and dispatches one proof/audit task from a real finding.
  - Gate: terminal result + postflight proof.

### Day 5

- AUT-5 eval harness v1 from production traces.
- Freeze policy if eval baseline below threshold.

### Day 6

- First A3 reversible small-fix trial if Day 4/5 green.
- Gate: rollback path, targeted tests, postflight improved.

### Day 7

- GPT-5.5 read-only escalation-lane review.
- Decide whether GPT-5.5 becomes optional escalation for Atlas/Forge only.

## Definition Of "Autonomous Enough"

OpenClaw is ready for unattended improvement windows when all are true:

- Last 24h: worker criticals 0.
- Pickup active claimTimeouts 0.
- Cost/status no false hard criticals.
- Candidate task generator dedupes correctly.
- A2 read-only self-dispatch has 10/10 successful runs.
- A3 small-fix lane has 3/3 successful reversible fixes.
- Eval suite passes at >= 90%.
- Every self-action leaves a learning-ledger entry.
- Operator can kill autonomy in under 2 minutes.

## Kill Switch

Minimum required kill switches:

1. `AUTONOMY_ENABLED=false` disables task synthesis/dispatch.
2. `AUTONOMY_MAX_TIER=A1` allows draft-only mode.
3. `AUTONOMY_MAX_NEW_TASKS_PER_HOUR=0` freezes creation.
4. `AUTONOMY_REQUIRE_OPERATOR_APPROVAL=true` forces proposal-only.
5. One documented rollback command/file for each small-fix lane.

## Immediate Next Action

Start with S-A1 + AUT-1:

1. Lens verifies tokenplan/cost status semantics.
2. Forge fixes `/api/costs/budget-status` tone classification.
3. Forge creates normalized autonomy findings dry-run.
4. Atlas does not auto-dispatch fixes yet; it may generate draft candidates only.

This moves the system one real step toward autonomy without pretending that fully unattended mutation is safe today.

Discord posts:
- `1497329987303510158`
- `1497329989295673585`
