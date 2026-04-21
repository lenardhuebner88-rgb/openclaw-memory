---
title: Context-Baseline 2026-04-22 — CE1 Pre-Flight
created: 2026-04-22
purpose: S-CTX-P0 T2 Baseline-Messung vor clear_tool_uses + compaction deployment
measurement-scope: 5 aktuellste Atlas-Sessions (agents/main/sessions/*.jsonl)
---

# Context-Baseline 2026-04-22

**Source directory:** `/home/piet/.openclaw/agents/main/sessions/`
**Sessions analyzed:** 5  ·  **Total JSONL bytes:** 758,011 (740.2 KB)

## Session-Sample

| Session-ID | Modified (UTC) | Total Turns | Σ presented_input (fresh+cacheRead) | Median/Turn | Peak/Turn | Cache-Hit-Rate |
|---|---|---|---|---|---|---|
| `c86995d8...` | 2026-04-21 21:08 UTC | 47 (U10/A37) | 1,860,779 | 52,282 | 88,328 | 83.8% |
| `f3b7d0a3...` | 2026-04-21 21:00 UTC | 3 (U1/A2) | 17,455 | 8,727 | 8,805 | 49.1% |
| `57787b3e...` | 2026-04-21 20:45 UTC | 5 (U0/A5) | 917,937 | 184,243 | 187,226 | 99.2% |
| `dd54a3a3...` | 2026-04-21 20:45 UTC | 3 (U1/A2) | 17,443 | 8,721 | 8,793 | 49.2% |
| `ca6b2cae...` | 2026-04-21 20:43 UTC | 7 (U1/A6) | 348,528 | 71,001 | 74,476 | 70.0% |

## Top-10 Largest tool_result Blocks

| # | Session | Tool | Size (KB) | First 100 chars |
|---|---|---|---|---|
| 1 | `c86995d8...` | `read` | 19.6 | `--- title: Sprint-M — Audit-Integrity + Scheduler-Consolidation sprint-id: M version: 1.2.1 (post-Co` |
| 2 | `ca6b2cae...` | `exec` | 19.6 | `us=done, dispatchState=completed, executionState=done, receiptStage=result. Reporting/Execution-Repo` |
| 3 | `c86995d8...` | `exec` | 19.3 | `# L1 Memory (memory/invariants/) --- 01-truth-order.md --- # Truth Order (Invariant)  1. Live verifi` |
| 4 | `c86995d8...` | `exec` | 19.2 | `PATCH {"task":{"id":"1218d3c3-a50c-40d2-830c-9d74b1a07d1e","title":"S-GOV T0 Lens-Review: Sprint-M v` |
| 5 | `c86995d8...` | `sessions_history` | 18.5 | `{   "sessionKey": "agent:sre-expert:main",   "messages": [     {       "role": "assistant",       "c` |
| 6 | `ca6b2cae...` | `read` | 18.0 | `# HEARTBEAT.md  ## State Machine Konsistenz (KRITISCH)  ### Die 3 States und ihre Beziehungen  Ein T` |
| 7 | `c86995d8...` | `read` | 15.8 | `# Sprint-M Session Closeout + Forge Verification (2026-04-21)  ## Scope - Non-QMD operative Stabilis` |
| 8 | `57787b3e...` | `process` | 11.0 | `=== openclaw memorySearch config ===    495	      },    496	      "maxConcurrent": 2,    497	      "` |
| 9 | `c86995d8...` | `sessions_list` | 8.6 | `{   "count": 5,   "sessions": [     {       "key": "agent:sre-expert:main",       "kind": "other",  ` |
| 10 | `c86995d8...` | `read` | 7.6 | `--- sprint-id: S-GOV title: Governance — Sprint-M Closeout + Vault-Index + Prefect/OTEL Spikes creat` |

## Aggregates

- **Median session presented_input (fresh+cacheRead, sum over turns):** 348,528
- **Median peak-per-session (single turn):** 74,476
- **Overall presented_input (all 5 sessions):** 3,162,142
- **Overall cacheRead:** 2,732,088
- **Overall Cache-Hit-Rate (cacheRead / presented_input):** 86.4% (target ≥70%)
- **toolResult-Share of JSONL volume:** 29.7% (224,907 / 758,011 bytes)
- **Total tool_result blocks counted:** 47

### Tool-Dominance (top 5 by cumulative toolResult bytes)

| Tool | Count | Cumulative (KB) |
|---|---|---|
| `exec` | 17 | 80.9 |
| `read` | 12 | 74.6 |
| `sessions_history` | 1 | 18.5 |
| `process` | 6 | 13.1 |
| `taskboard__taskboard_create_task` | 3 | 11.9 |

## Interpretation

- **toolResult-Anteil-Annahme widerlegt:** Nur 29.7% der JSONL-Bytes sind toolResult-Content. Andere Blöcke (thinking, system-messages, toolCalls) dominieren.
- **Cache-Hit-Rate 86.4% ≥ Ziel 70%** — cache_control-Strategie ist effektiv.
- **Peak-Turns 74,476 tokens (median)** bleiben unter typischen Warning-Thresholds (128K).
- **Top-Tool nach Volumen:** `exec` dominiert die Top-10. Fokus für `clear_tool_uses` / Content-Truncation.

## Reproducibility

Script: `/home/piet/vault/03-Agents/context-baseline-script-2026-04-22.py`

```sh
ssh homeserver 'python3 /home/piet/vault/03-Agents/context-baseline-script-2026-04-22.py'
```

The script picks the 5 most recently modified primary session JSONLs (excludes `.checkpoint.`, `.archived.`, `.lock`, and files < 4 KB), parses each with the same logic as the measurement run, and overwrites this report. Numbers are deterministic for a given snapshot of the sessions directory.
