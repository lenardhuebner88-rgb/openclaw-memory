Wrote report to /home/piet/vault/03-Agents/context-baseline-2026-04-22.md
Total bytes written: 5372
-- SUMMARY --
Sessions: 5
Total JSONL KB: 740.2
Overall input_tokens: 3,162,142
Overall cache_read: 2,732,088
Cache-hit rate: 86.4%
toolResult share: 29.7%
Top tool: exec
2

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

## Content-Type Breakdown (share of JSONL bytes)

| Content Type | Bytes | % of JSONL |
|---|---|---|
| `toolResult` (text content) | 224,907 | 29.7% |
| `thinking` (+ signature) | 16,142 | 2.1% |
| `text` (assistant/user text + signature) | 19,557 | 2.6% |
| `toolCall` (arguments + partialJson) | 46,037 | 6.1% |
| JSON-overhead + metadata (ids, timestamps, usage, signatures in wrappers) | 451,368 | 59.5% |

**Within content-only bytes, toolResult = 73.3%.**

## Interpretation

- **toolResult-Anteil-Annahme (~85%) teilweise bestätigt:** Nur 29.7% der rohen JSONL-Bytes, aber 73.3% der *Content*-Bytes (exkl. JSON-Overhead) sind toolResult. Die Hypothese greift wenn man JSON-Wrapper/Metadaten abzieht — `clear_tool_uses` ist weiterhin die richtige P0-Intervention.
- **Cache-Hit-Rate 86.4% ≥ Ziel 70%** — prompt-caching-Strategie ist effektiv; gesamte Context-Ingestion kostet nur ~14% pro Turn an fresh-input.
- **Peak-Turns 74,476 tokens (median)** bleiben unter typischen Warning-Thresholds (128K).
- **Top-Tool nach Volumen:** `exec` (17 Aufrufe, 80.9 KB kumulativ) dominiert die Top-10. Fokus für `clear_tool_uses` / Content-Truncation; zusammen mit `read` decken die ersten zwei Tools >70% des toolResult-Volumens ab.
- **Caveat:** Zwei der 5 Sessions (`57787b3e`, `ca6b2cae`) wurden während der Messung rotiert (`*.archived.*` / `*.checkpoint.*`-Dateien existieren, z.T. mit >1 MB Inhalt pro rotierter Copy). Die hier gemessenen `.jsonl` enthalten nur den Post-Rotation-Tail. Für volle Session-Längen `--include-rotated`-Variante nutzen (noch nicht implementiert).

## Reproducibility

Script: `/home/piet/vault/03-Agents/context-baseline-script-2026-04-22.py`

```sh
ssh homeserver 'python3 /home/piet/vault/03-Agents/context-baseline-script-2026-04-22.py'
```

The script picks the 5 most recently modified primary session JSONLs (excludes `.checkpoint.`, `.archived.`, `.lock`, and files < 4 KB), parses each with the same logic as the measurement run, and overwrites this report. Numbers are deterministic for a given snapshot of the sessions directory.
