---
title: Hermes Shadow Debug Pattern
status: stub
created: 2026-05-02
owner: Piet
scope: hermes-kb
source:
  - /home/piet/vault/03-Agents/Hermes/sprint-h2-receipt-2026-05-02.md
  - /home/piet/vault/03-Agents/Hermes/sprint-h3-receipt-2026-05-02.md
---

# Hermes Shadow Debug Pattern

Hermes is active as an operator-facing peer agent with a conservative Phase-1 operating profile. The useful pattern is not passive chat: Hermes reads focused context, uses read-only MCPs first, names the runbook, and returns a compact incident shape.

## Operating Pattern

1. Select the runbook or context file first.
2. Prefer `openclaw-readonly`, `mc-readonly`, and focused `qmd-vault` calls.
3. Report `Problem`, `Evidence`, `Risk`, `Next Action`.
4. Gate restarts/config edits behind live evidence, backup, and Piet approval.
5. Convert resolved incidents into learning packets or KB updates during Phase 2.

## Lessons From H-2/H-3

- PATH drift matters: Hermes initially resolved `openclaw` through the wrong Node.js lane. The durable fix was to call `/home/piet/bin/openclaw` directly in the read-only MCP.
- Discord 429 loops are operational noise until they become persistent. Slash command sync should be off or throttled by command hash and minimum interval.
- Token rotation must distinguish Piet/OpenClaw bot credentials from Hermes credentials. Never replace one with the other.
- QMD is useful for focused vault retrieval, but known incident classes should start from known runbook paths to avoid slow broad searches.

## Next Phase

Phase 2 should turn incidents into short learning packets and memory-safe summaries. Phase 3 can test controlled task participation only after explicit operator approval and receipt discipline.
