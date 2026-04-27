---
title: Context-Management Long-Term-Fix für OpenClaw Multi-Agent
date: 2026-04-27
status: proposal
author: Claude (Opus 4.7) via Cowork — basierend auf 3 parallelen Research-Agents
owner: pieter_pan
review-target: Atlas + Forge + sre-expert
discord-channel: 1495737862522405088
---

# Context-Management Long-Term-Fix — OpenClaw

## 1) Diagnose (Stand 2026-04-27 ~17:50 UTC)

**Active context-budget proof (post-restart, MCP-Hardening P0.2 live):**

| Metrik | Ist | Gate | Faktor |
|---|---:|---:|---:|
| contextCompiled | 248,795 B | 80,000 B | 3.1× over |
| traceMetadata | 107,219 B | 10,000 B | 10.7× over |
| toolsSchema | 45,939 B | 20,000 B | 2.3× over |

→ Status **degraded**, trotz Gateway-Restart und runtime-patch.

**Worker-Session-Bloat (Session-Size-Guard alert-only für Worker):**

- agent=sre-expert: 14.6 MB / 3,821 msgs (1× Session)
- 7 weitere Worker-Sessions auf ROTATION-Threshold (>1126 KB)
- Strukturell: rotation **disabled** für Worker → unbegrenztes Wachstum vorgesehen

## 2) Root-Causes

1. **Tool-Schemas dauerhaft im Prompt** — kein Defer/Lazy-Loading (45K bei jedem Compile).
2. **Trajectory-Writer dumped raw tool-output payloads** in `trace.metadata` (107K, append-only ohne Maskierung).
3. **Worker haben keine Hard-Cap-Rotation** — nur Alerts; kein Handoff-zu-Fresh-Session-Pattern.
4. **`context.compiled` wird voll re-emitted** — kein Delta, keine Cache-Hierarchie genutzt.
5. **Keine Per-Worker Token-Budgets** — alle teilen sich denselben Cap, heavy worker drainen andere.
6. **Kein Memory-Tool** — keine Persistence über Rotation.

## 3) State-of-the-Art (Anthropic-Native + GitHub-Research)

### Anthropic-Native (sofort produktiv nutzbar)

| Feature | Beta/GA | ROI |
|---|---|---|
| **Context Editing** (`clear_tool_uses_20250919`, `clear_thinking_20251015`) | Beta-Header `context-management-2025-06-27` | +39 % Perf, **-84 % Tokens** in 100-Turn-Eval |
| **Memory Tool** (`memory_20250818`) | GA | File-based Persistence über Sessions |
| **Tool Search** (`ENABLE_TOOL_SEARCH=auto:5`) | GA | Tools deferred, on-demand-Loading |
| **Prompt Caching** (1h-TTL, `automatic` breakpoint) | GA | Cache-Hit = 0.1× Input-Preis |

### Open-Source-Patterns (portierbar)

- **OpenHands ObservationMaskingCondenser** — Action-Trace voll, Tool-Outputs maskieren ab attention_window=N. → genau für unser Trajectory-Problem.
- **OpenAI Agents nest_handoff_history** — Sub-Agent bekommt summarized parent als single message, function_call/reasoning excluded.
- **Letta MemGPT Tier-Memory** — core (hot, 2K) + recall (warm) + archival (cold, vector-DB).
- **OTEL GenAI Semantic Conventions** — gen_ai.tool.name, gen_ai.usage.input_tokens als bounded trace-schema.

## 4) 4-Layer Architectural Fix

### Layer 1 — Tool-Schema-Deferral  *[Quick Win, 1-2 h]*

Setze in MCP-Runtime: `ENABLE_TOOL_SEARCH=auto:5`

**Effekt:** toolsSchema 45K → ~5K. **Verify:** budget-proof.mjs toolsSchema < gate 20K.

### Layer 2 — Trajectory-Writer-Refactor  *[3-5 d]*

- **OTEL-GenAI-Schema** — pro Tool-Call ein bounded Span (Name, usage.tokens, finish_reason), KEINE raw payloads.
- **ObservationMasking** — attention_window=100 events; Action-Trace voll, Outputs darüber → masked.
- **Tiered Storage** — hot (RAM, 10K cap) → warm (jsonl rotate bei 1 MB) → cold (parquet 24h+).
- **Importance-Scoring** (0-1) — Failures=0.9, Routine-Reads=0.1; Eviction = importance ASC, age DESC.

**Effekt:** traceMetadata 107K → ~8K. **Verify:** budget-proof traceMetadata unter Gate.

### Layer 3 — Worker-Lifecycle  *[5-7 d]*

**R51 Worker-Session-Rotation** — Hard-Cap 60 % des Worker-Budgets (~120K von 200K) → forced-handoff. Parent spawnt Fresh Sub-Agent mit compact_summary + open_tasks.jsonl als Bootstrap (Pattern aus Anthropic Multi-Agent-Research-System).

**R52 Per-Agent-Budgets** in `~/.openclaw/config/agent-limits.yaml`:

| Worker | Trigger | Keep tool_uses | Max-Output |
|---|---:|---:|---:|
| sre-expert (read-heavy) | 30 K | 5 | 8 K |
| james (mutating) | 80 K | 8 | 16 K |
| spark (research) | 50 K | 4 | 4 K |
| efficiency-auditor | 40 K | 5 | 12 K |

**Context-Editing-API** aktivieren (Beta-Header `context-management-2025-06-27`) mit edits-Array: clear_thinking_20251015 zuerst (keep 2 turns), dann clear_tool_uses_20250919 mit per-Worker trigger, keep 5–8 tool_uses, **clear_at_least: 15K** (kritisch — sonst zerstört jede Edit-Aktion den Prefix-Cache), exclude_tools für state-mutating Tools (taskboard_update, session_log, memory_*).

**Effekt:** keine 14 MB Sessions mehr; +39 % Perf, -84 % Tokens (Anthropic-Eval). **Verify:** Session-Size-Guard zeigt keine ROTATION-Worker nach 24 h.

### Layer 4 — Memory + Cache  *[3-5 d]*

**Memory-Tool** (`memory_20250818`) je Worker:
- `/home/piet/.openclaw/agents/<worker>/memory/progress.md`
- `open-tasks.jsonl`
- `architecture.md`

Path-Traversal-Validation (regex + pathlib.resolve().relative_to()), Filesize-Caps, TTL-Cleanup. Worker rotiert → neuer Subprozess liest Memory-Dir → resume (Anthropic Multi-session-software-development-Pattern).

**Cache-Hierarchie**:
1. tools + globaler system als Stable Prefix → cache_control: ephemeral, ttl: 1h
2. Worker-spezifischer System-Suffix (sre-expert vs. james) als 2. Breakpoint
3. Message-history → automatic cache_control

**Effekt:** Cache-Hit-Rate von vermutlich <20 % auf >60 %. **Verify:** Response-Header anthropic-cache-input-tokens getrackt.

## 5) Observability — Leading-Indicators

Cron `*/2 * * * * session-vitals-collector.py` → Prometheus + Grafana-Dashboard:

| # | Metrik | Threshold | Bedeutung |
|---|---|---|---|
| 1 | Token-Velocity (tokens/min) | >2× baseline | Worker im Loop |
| 2 | Tool-Call-Density (calls/1K-out) | >5 | Tool-Spam |
| 3 | Cache-Hit-Rate | <40 % | Schema-Drift / Pollution |
| 4 | Output-to-Input-Ratio | <0.05 oder >0.5 | Stuck / Hallucination |
| 5 | Time-Between-Tool-Errors | <30 s | Cascade imminent |
| 6 | Context-Utilization-% per Worker | >70 % | Pre-Rotate-Trigger |
| 7 | Latency-P95-Drift (10min) | +50 % | Context-Rot (>200K tokens) |

3-σ Anomaly-Detection auf Token-Velocity → Auto-Issue auf Board.

## 6) Roll-out Plan (4 Wochen)

| Woche | Layer | Effort | Owner |
|---|---|---:|---|
| W1 (28.04–04.05) | L1 Tool-Search + L4 Memory-Tool MVP | 3 PT | Atlas-Lead, james |
| W2 (05.05–11.05) | L3 Hard-Cap + Per-Agent-Budgets + Context-Editing | 5 PT | sre-expert, james |
| W3 (12.05–18.05) | L2 Trajectory-Refactor (OTEL + ObservationMasking) | 5 PT | sre-expert |
| W4 (19.05–25.05) | Observability-Stack + Auto-Tuning | 4 PT | spark, sre-expert |

**Pre-Flight-Gates** (Lessons-Learned 2026-04-20 H2/H5-Outage):
- **R51 Schema-Gate** — config-writes JSON-Schema-validated vor commit
- **R52 Silent-Fail-Detection** — agent-subprocess crash <60 s → Atlas-Ping
- **R53 Config-in-Git** — alle config-changes via PR

## 7) Sofort-Fix für Forge 551c8d74 (Scope-eng)

Die laufende Forge-Task macht **nur** L1 + Trajectory-Payload-Cap:

1. `ENABLE_TOOL_SEARCH=auto:5` in MCP-Runtime setzen
2. trajectory-writer.mjs: raw tool-output payload-Cap bei 2K chars (truncate + sha256-suffix)
3. budget-proof verifiziert: alle drei Gates green
4. **KEIN** Restart ohne separate Freigabe (Memory R49 hold)

Layer 2/3/4 sind separate Sprints (W2-W4).

## 8) Quellen

**Anthropic:**
- [Managing context on the Claude Developer Platform](https://claude.com/blog/context-management)
- [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [How we built our multi-agent research system](https://www.anthropic.com/engineering/built-multi-agent-research-system)
- [Context editing](https://docs.anthropic.com/en/docs/build-with-claude/context-editing)
- [Memory tool](https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/memory-tool)
- [Prompt caching](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching)
- [Agent SDK – Tool search](https://docs.anthropic.com/en/api/agent-sdk/tool-search)
- Cookbook: [memory_cookbook](https://github.com/anthropics/claude-cookbooks/blob/main/tool_use/memory_cookbook.ipynb), [tool_search_alternate_approaches](https://github.com/anthropics/claude-cookbooks/blob/main/tool_use/tool_search_alternate_approaches.ipynb), [automatic-context-compaction](https://github.com/anthropics/claude-cookbooks/blob/main/tool_use/automatic-context-compaction.ipynb)

**Open-Source:**
- OpenHands [condenser_config.py](https://github.com/All-Hands-AI/OpenHands/blob/main/openhands/core/config/condenser_config.py)
- OpenAI Agents [handoffs/history.py](https://github.com/openai/openai-agents-python/blob/main/src/agents/handoffs/history.py), [openai_responses_compaction_session.py](https://github.com/openai/openai-agents-python/blob/main/src/agents/memory/openai_responses_compaction_session.py)
- LangGraph Swarm [handoff.py](https://github.com/langchain-ai/langgraph-swarm-py/blob/main/langgraph_swarm/handoff.py)
- Claude Agent SDK [types.py](https://github.com/anthropics/claude-agent-sdk-python/blob/main/src/claude_agent_sdk/types.py)

**Research:**
- ChromaDB [Context Rot](https://research.trychroma.com/context-rot)
- Letta [MemGPT Paper](https://arxiv.org/abs/2310.08560) + [Memory Concepts](https://docs.letta.com/concepts/memory)
- Cognition AI [Don't Build Multi-Agents](https://cognition.ai/blog/dont-build-multi-agents)
- LangChain [Long-Term Memory in LangGraph](https://blog.langchain.com/launching-long-term-memory-support-in-langgraph)
- Google [Vertex AI Agent Engine Memory Bank](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/sessions/overview)
- OTEL [GenAI Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
