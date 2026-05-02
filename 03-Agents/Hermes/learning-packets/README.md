---
title: Hermes Learning Routine
status: active
created: 2026-05-02
owner: Piet
scope: hermes-learning
---

# Hermes Learning Routine

Hermes learns from curated operator packets, not raw logs.

## When To Create A Packet

Create one packet after:

- a production incident
- a token/config rotation
- a break-glass recovery
- a repeated operator decision
- a runbook correction
- a clear stop condition discovered during debugging

Do not create packets for routine chatter, exploratory notes, or unverified claims.

## Packet Rules

- Use `/home/piet/vault/03-Agents/Hermes/learning-packets/TEMPLATE.md`.
- Keep one packet to one incident or decision.
- Include live evidence, not memory-only claims.
- Extract one reusable rule.
- Include stop conditions.
- Link runbooks or receipts used.

## Naming

```text
YYYY-MM-DD-short-topic.md
```

Example:

```text
2026-05-02-discord-token-rotation.md
```

## Hermes Behavior

When Piet says "lerne das" or "erstelle Learning Packet":

1. Ask for or identify the concrete incident/fix.
2. Use the template.
3. Keep secrets out.
4. Do not update global memory directly.
5. Save the packet in this folder.

## Existing Packets

- `2026-05-02-discord-token-rotation.md`

