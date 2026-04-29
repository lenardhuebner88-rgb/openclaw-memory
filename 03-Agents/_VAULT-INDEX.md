---
title: Vault Master Index
status: index
last_update: 2026-04-29
maintained_by: claude (manual)
purpose: Single entry-point for "where is the truth?". Pointers only — no content.
---

# Vault Master Index

> Operator + agent entry-point. **This file is just pointers.** Real content lives behind the links.  
> When in doubt, treat the linked file as authoritative, not this one.

---

## 🎯 Sprint status — what's open, what's done

**→ [04-Sprints/INDEX.md](../04-Sprints/INDEX.md)**

Single canonical view of all sprints by priority (P0/P1/P2/Deferred), partial-closures, recent closures, and the cleanup-backlog. **Read this before dispatching a new sprint.**

Folder mechanics (read after the index, not before):
- `04-Sprints/planned/` — open plans (warning: contains stale entries; trust INDEX.md)
- `04-Sprints/active/` — currently-running sprint waves
- `04-Sprints/closed/` — completed sprints with closure-doc
- `04-Sprints/reports/` — execution reports, RCAs, audits
- `04-Sprints/superseded/` — historical / replaced plans
- `04-Sprints/AGENTS.md` — naming + frontmatter rules (PlanSpec)
- `04-Sprints/README.md` — retrieval order for agents

---

## 🤝 Agent coordination

- **[03-Agents/_coordination/HANDSHAKE.md](_coordination/HANDSHAKE.md)** — live SSoT for cross-agent collaboration. §6 supersedes the standalone `agent_team_meetings_plan` (lokal-memory).
- **[03-Agents/_coordination/meetings/README.md](_coordination/meetings/README.md)** — meeting modes (debate / council / review).

## 🧠 Context & memory architecture

- **[03-Agents/context-management-longterm-fix-2026-04-27.md](context-management-longterm-fix-2026-04-27.md)** — 4-Layer architectural proposal (Tool-Schema-Deferral, Trajectory-Maskierung, Worker-Rotation, Caching). Status: review-pending. **Highest token-saving lever.**
- **[03-Agents/james-worker-memory-tool-mvp-2026-04-27.md](james-worker-memory-tool-mvp-2026-04-27.md)** — MVP spec for Worker filesystem-memory (progress.md, open-tasks.jsonl, architecture.md).
- Live memory-system snapshot: `_agents/memory-dashboard.md` (auto-regen hourly via memory-orchestrator).
- Memory-bulk lives under `/home/piet/.openclaw/workspace/memory/` (NOT `vault/memory/` — that's dead-storage).

## 🛡️ Governance & rules

- **Active rule-set:** R1–R51 (R51 = Schema-Gate, deployed 2026-04-29).
- **R51 doc:** [03-Agents/r51-schema-gate.md](r51-schema-gate.md)
- **Defense-Crons:** 50 active in 8 tiers (live snapshot in [stabilization-2026-04-29-full.md](stabilization-2026-04-29-full.md) §"Defense-Crons").
- **R49 violations** (recent task_not_found warnings 2026-04-29): see `04-Sprints/INDEX.md` → P2 §R49-DRIFT-RCA.

## 🔧 Operator-only actions

- **[03-Agents/operator-actions-2026-04-29.md](operator-actions-2026-04-29.md)** — OAuth re-auth, OpenRouter top-up, network-bind tightening. Read before triggering ops-commands.

## 📚 Knowledge base

- `10-KB/` — 10 Karpathy-style topic articles (sprint-orchestration, receipt-discipline, deploy-contracts, atlas-hallucination-prevention, board-hygiene, memory-architecture, scope-governance, sub-agent-coordination, incident-response, build-deploy-regeln). Auto-compiled via `kb-compiler` cron. **Authoritative path** is `10-KB/`, NOT `03-Agents/kb/` (path drift fixed 2026-04-29).

## 🗂️ Other top-level vault folders

- `01-Daily/` — daily reflection notes
- `02-Projects/` (and `03-Projects/`) — project documents and reports
- `_agents/` — auto-generated agent-state files (memory-dashboard etc.)

---

## What you will NOT find here

- Live task-board state — query MCP `sprint_status` or the Mission-Control REST-API, not vault files.
- Code — that lives in `~/.openclaw/workspace/mission-control/` and `~/.openclaw/scripts/`, not in the vault.
- Conversation logs — those are session-local memory.

---

## Maintenance

This master-index is **manually maintained**. Update when:
- A new top-level folder is added under `vault/`.
- A pointer above moves to a new path.
- A "highest-leverage" file (HANDSHAKE, context-fix, operator-actions) is replaced by a newer version.

Quarterly review: walk every link, drop dead pointers, add new high-leverage files.
