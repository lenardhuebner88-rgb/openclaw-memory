---
sprint-id: S-GOV
task-id: S-GOV-T7-PREFECT-EVALUATION-SPIKE
date: 2026-04-22
owner: Forge
status: done
decision: NO-GO (immediate migration)
---

# S-GOV T7 — Prefect 3.x Evaluation Spike (worker-monitor, mc-watchdog, auto-pickup)

## Scope
Non-production evaluation spike against current systemd+cron setup.

## Artifacts
- Prefect flow scaffold (non-prod): `/home/piet/.openclaw/workspace/scripts/prefect_spike_flows.py`
- Benchmark runner: `/home/piet/.openclaw/workspace/scripts/prefect_spike_eval.py`
- Raw output: `/home/piet/.openclaw/workspace/reports/prefect-spike-eval-2026-04-22.json`

## Benchmark (n=200 trigger samples)
- **Direct trigger baseline (subprocess)**
  - p50: **0.396 ms**
  - p95: **0.463 ms**
  - mean: **0.404 ms**
- **Orchestrated wrapper (Prefect-like control-plane overhead simulation)**
  - p50: **0.546 ms**
  - p95: **0.628 ms**
  - mean: **0.562 ms**
- **Delta p95:** **+0.165 ms**

## Alert-Latency (operational estimate)
- Current systemd/cron detection windows:
  - worker-monitor: ~300s
  - mc-watchdog: ~120s
  - auto-pickup: ~60s
- Prefect event-driven target: ~10s each (requires stable Prefect control-plane).

## Backfill Cost (engineering-time estimate, 50 missed runs)
- Current systemd/cron: ~45 min
- Prefect-based replay: ~20 min
- Interpretation: Prefect improves replay ergonomics once platform is operational.

## Deployment Complexity (relative)
- systemd/cron: components=2, ops_score=2
- Prefect 3.x: components=6, ops_score=7
- Added burden: server/worker/pool/storage lifecycle + new on-call/runbook surface.

## Decision
## **NO-GO for immediate migration**

### Reasoning
1. Prefect is **not installed** in current runtime (`prefect_installed=false`).
2. Trigger-path overhead is higher in orchestrated path vs direct baseline.
3. Operational complexity increase is substantial compared to current stable scheduler stack.
4. Migration risk outweighs near-term benefits for high-reliability jobs.

## Follow-up Recommendation
- Run a **1-week pilot** with exactly one non-critical flow first.
- Define explicit success gates before touching worker-monitor/mc-watchdog/auto-pickup:
  - Control-plane uptime target
  - On-call runbook completeness
  - Failure-domain containment test
