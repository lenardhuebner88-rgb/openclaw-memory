# Cost-Story Modal — UX Concept
**Pack:** Costs-v2, Pack 8  
**Type:** UX Prototype (Markdown Artifact)  
**Scope:** Zone C — Cost-Story Modal, no implementation  
**Word count target:** 300–600

---

## User Story (3 Sentences)

As an operator I open the Cost-Story modal to understand **why** a task or session consumed its budget — separating justified cost spikes from runaway loops or misconfigurations. The modal presents a chronological cost narrative anchored to real events, not just a number. I leave with a clear answer: *was this cost necessary, and what do I do next?*

---

## ASCII Wireframe (~90 chars)

```
┌──────────────────────────────────────────────────────────────┐
│  Cost Story                          Agent: spark  [X close] │
├──────────────────────────────────────────────────────────────┤
│  Total: $0.042  │  Window: Today  │  Tasks: 3  │  ● Normal  │
├──────────────────────────────────────────────────────────────┤
│  TIME       EVENT                        COST      CUMULATIVE│
│  ─────────────────────────────────────────────────────────── │
│  18:34      Task dispatched              $0.001        $0.001 │
│  18:35      Agent accepted               $0.003        $0.004 │
│  18:42      Tool: vault-write            $0.018        $0.022 │
│  18:44      Tool: exec+read              $0.015        $0.037 │
│  18:51      Final receipt                $0.005        $0.042 │
├──────────────────────────────────────────────────────────────┤
│  spark worked a UX task for 17 min. vault-write was the main │
│  cost driver. Rate: $0.047/min — within normal range.        │
├──────────────────────────────────────────────────────────────┤
│  [Expand Tool Detail]       [Copy Summary]       [Flag Issue] │
└──────────────────────────────────────────────────────────────┘
```

---

## MC API Field Mapping

| Modal Element | MC API Field | Endpoint |
|---|---|---|
| Event timestamp | `lastActivityAt` / `createdAt` | `GET /api/tasks/[id]` |
| Event label | `lastExecutionEvent` | `GET /api/tasks/[id]` |
| Cost (per event) | `cost` delta | computed from task history |
| Cumulative | `cost` running total | client-side |
| Agent | `assigned_agent` / `dispatchTarget` | `GET /api/tasks/[id]` |
| Task title | `title` | `GET /api/tasks/[id]` |
| Window filter | `createdAt` range | `GET /api/tasks?createdAt>=…` |
| Status badge | derived from `executionState` | `GET /api/tasks/[id]` |
| Narrative | AI-generated from event chain | client-side |

---

## Three Narratives (Today, 2026-04-17)

**N1 — UX Sprint ($0.042, 17 min)**
Spark dispatched to a UX-prototype at 18:34. Three events (accept, vault-write, exec+read) built cost steadily. vault-write dominated. Verdict: *proportional to work, no anomaly.*

**N2 — Restart Loop ($0.31, 80 min)**
Forge session ran 01:30–02:50 during MC's 170+ restart cycle. Each restart re-triggered health checks, compounding cost. Cost-Story would flag the spike at 40 min and surface systemd restarts as amplifiers. Verdict: *fix the restart policy, not the agent.*

**N3 — Batched Packs ($0.89, 1 hour)**
Eight consecutive Forge sessions (Packs 1–8, 10:00–12:42), each billing independently. Aggregated under a batch window. Verdict: *within hourly budget but visible cluster — consider batch-cost threshold alert.*

---

## Operator Core Questions

1. **Justified?** Narrative + event timeline show whether spend produced value or was eaten by retries.
2. **Pattern or one-off?** Window selector + task-count badge reveal outliers vs. recurring clusters.
3. **Act now?** Status badge (Normal / Elevated / Critical) gives one-glance answer; [Flag Issue] escalates without leaving.

---

*Spark · 2026-04-17 · No code · Input for Pixel design pass*
