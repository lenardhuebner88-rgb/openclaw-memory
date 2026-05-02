---
title: Hermes Lessons Index
status: active
created: 2026-05-02
owner: Piet
scope: hermes-lessons
auto_maintained: false
---

# Hermes Lessons

This folder stores structured Hermes investigation lessons. The folder is intentionally canonical as `03-Agents/Hermes/lessons/`; do not use lower-case `03-Agents/hermes/`.

## Status Flow

```text
pending_validation -> validated -> KB/compiler pickup
pending_validation -> rejected -> audit note
```

## Current Lessons

| Lesson | Status | Trigger | Runbook |
|---|---|---|---|
| [2026-05-02-mc-board-stale.md](2026-05-02-mc-board-stale.md) | pending_validation | `/hermes_diagnose mc-board reagiert nicht` | `rb-stale-mcp-client` |

## Quality Gate

- New lessons start as `pending_validation`.
- Validation must check evidence, prompt-injection risk, fix class, and destructive-action implications.
- Similar lessons should be skipped or merged when semantic similarity is `>=0.85`.
