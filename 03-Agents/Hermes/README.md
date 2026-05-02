---
title: Hermes Agent Folder
status: active
created: 2026-05-02
owner: Piet
scope: hermes-agent-docs
---

# Hermes Agent

Hermes is active in Piet's OpenClaw/Homeserver environment as an operator-facing peer agent. Phase 1 is intentionally conservative: read-only diagnosis, runbook use, incident summaries, and approval-gated break-glass support. Phase 2/3 can expand into task support, lessons, and memory contribution after explicit operator gates.

## Read First

1. [system-overview.md](system-overview.md) — services, paths, MCP surface, response shape.
2. [working-context.md](working-context.md) — current scope, break-glass gates, playbook routing.
3. [AGENTS.md](AGENTS.md) — Hermes-specific scope, approval, and coordination rules.
4. [playbooks/](playbooks/) — operational runbooks.
5. [learning-packets/README.md](learning-packets/README.md) — lessons loop.
6. [lessons/INDEX.md](lessons/INDEX.md) — Phase-2 structured lessons.
7. [plans/sprint-h7-phase2-lesson-loop-2026-05-02.md](plans/sprint-h7-phase2-lesson-loop-2026-05-02.md) — current Lesson-Loop implementation plan.

## Core Runtime

- Hermes app/user ID: `1500199614706483210`
- Service: `hermes-gateway.service`
- Config: `/home/piet/.hermes/config.yaml`
- Default model: `MiniMax-M2.7`
- Fallback lane: `openai-codex/gpt-5.5`
- MCPs: `qmd-vault`, `mc-readonly`, `openclaw-readonly`

## Current Phase

| Phase | Status | Meaning |
|---|---|---|
| Phase 1 | active | Read-only MCP, runbooks, debug support, approval-gated break-glass. |
| Phase 2 | planned | Lessons, learning packets, KB stubs, memory-safe summaries. |
| Phase 3 | planned | Controlled task participation with receipts and explicit operator approval. |

## Security Rules

- Prefer read-only MCP tools before shell checks.
- No config edits without timestamped backup.
- No restarts without live evidence and Piet approval.
- Keep `privacy.redact_pii=true`.
- Never replace the Hermes Discord token with the Piet/OpenClaw token.

## Learning Model

Hermes has native learning through session search, built-in memory, skills, and the curator. Vault lessons do not replace that loop. They are the reviewed evidence layer that decides what should be promoted into native Hermes memory or skill behavior.

## Receipts

Sprint receipts live in this folder. The sprint index pointer is `/home/piet/vault/04-Sprints/INDEX.md`.
