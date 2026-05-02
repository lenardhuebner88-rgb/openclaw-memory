---
title: Hermes Langfuse Tracing Gate
status: planned
created: 2026-05-02
owner: Piet
scope: hermes-observability
---

# Hermes Langfuse Tracing Gate

Langfuse is useful for Phase 2/3 observability, but it should be introduced after the lesson loop has value. Tracing should help find loops, cost spikes, and bad tool patterns; it should not become required for Hermes to diagnose incidents.

## Source Decisions

- Use the current Langfuse Python SDK style: `from langfuse import observe` for decorator-based tracing.
- Disable or limit IO capture for sensitive prompts and outputs.
- Add metadata for incident class, runbook, model, provider, and outcome.
- Prefer Docker Compose for self-hosting instead of a raw `docker run`, because Langfuse self-host now expects a multi-service deployment for persistent low-scale use.

## Proposed Environment

- Port: `3001` on homeserver.
- URL: `http://127.0.0.1:3001` first, expose wider only after auth/network review.
- Secrets: generated `NEXTAUTH_SECRET`, database credentials in `.env`, not vault.
- Backup: database volume backup before upgrades.

## Instrumentation Target

Start with one wrapper around the investigation entry point:

```python
from langfuse import observe

@observe(name="hermes_investigate", capture_input=False, capture_output=False)
async def investigate(query: str):
    ...
```

Then add explicit metadata on the active trace/span:

- `incident_class`
- `runbook`
- `model`
- `provider`
- `outcome`
- `lesson_id`

## Gate Before Install

- Lesson static eval passes.
- Bad synthetic lesson is rejected.
- Hermes can run one investigation without tracing.
- Operator accepts Docker/network footprint.

## Not Yet Done

- Docker Compose deployment.
- Hermes code instrumentation.
- Dashboard/secret setup.
