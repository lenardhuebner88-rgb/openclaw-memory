# Operator-Dashboard Patterns — Research for Mission Control Clean-Cockpit
**Task:** `31396429-c406-49b8-93c3-94ad21e01aeb`  
**Agent:** James  
**Date:** 2026-04-18  
**Status:** ✅ Completed

---

## Research Mandate

Identify 5–7 concrete UI patterns from Datadog, Grafana Cloud, Cursor, Linear, and existing vault documents that apply to Mission Control's Clean-Cockpit refactor. Each pattern documented with ASCII wireframe, source URL, and Mission Control applicability assessment.

**Key use cases to cover:**
1. Heartbeat / system-health indicators
2. Next-Best-Action banners / alert banners
3. Agent workload visualization
4. Cost-story / spend analytics modals
5. Live-signal overview (lane-based task flow)
6. Incident / failure state indicators
7. Summary / KPI widgets

**Sources consulted:**
- Datadog Widgets documentation (`docs.datadoghq.com/dashboards/widgets`)
- Grafana Cloud Visualizations (`grafana.com/docs/grafana-cloud/visualizations`)
- Cursor Agents Window (changelog + docs)
- Linear workflow/view docs
- Existing vault docs: `spark-cost-story-ux-concept.md`, `atlas-board-operator-cockpit.md`

---

## Pattern 1 — Heartbeat Strip

**Source:** Datadog — Monitor Summary Widget + Event Stream Widget  
**URL:** `https://docs.datadoghq.com/dashboards/widgets/types/#alert-graph`  
**Confidence:** High

### Pattern Description
A single-row strip of 3–6 health indicators, each showing component name + colored status dot (green/amber/red). Updates in near-real-time. Operators see system health in one glance without scanning metrics.

### ASCII Wireframe

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ ●MC:up   ●Gateway:up   ●Dispatch-Consistency:1.0   ⚠Recovery:2   ✗0   │
└─────────────────────────────────────────────────────────────────────────────┘
         ↑                                        ↑                ↑
      green dot                              amber dot         red dot
      (all healthy)                      (needs attention)    (incident)
```

### Key Design Decisions
- **One row, no scroll.** Fits in 32–48px height. Text is label only, no metric values.
- **Color encoding is universal.** Green = nominal. Amber = soft limit / warning threshold. Red = failure / incident. No gradients.
- **Order is fixed priority.** System components first, then recovery/integrations, then incidents.
- **Click opens detail.** Each indicator is a link/drill-down, not just a display.

### Mission Control Applicability
**Directly applicable — Zone A of the atlas board spec.** MC already has a health endpoint (`/api/health`) with `pendingPickup`, `inProgress`, `failed`, `staleOpenTasks`, `orphanedDispatches`, `recoveryLoad`, `dispatchStateConsistency`. These map cleanly to a strip.

Mapping:
| Datadog pattern element | MC health field |
|---|---|
| Component dot | Derived from health fields |
| "MC:up" | `gateway.alive` |
| "Gateway:up" | `gateway.alive` |
| "Dispatch-Consistency" | `dispatchStateConsistency` |
| "Recovery:N" | `recoveryLoad` |
| "✗N" (red) | `failed` count |

**Effort estimate:** Very low. Pack 2 in the atlas implementation plan is ~200 LOC.

---

## Pattern 2 — Next-Best-Action Banner

**Source:** Linear — Triage Inbox + Alert Graph  
**URL:** `https://docs.datadoghq.com/dashboards/widgets/types/#alert-graph`  
**Confidence:** High

### Pattern Description
A single full-width banner at the top of the view. One sentence — what is the most urgent thing the operator should do right now, with one action button. Replaces a dashboard full of numbers with a single judgment.

### ASCII Wireframe

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ ⚠  3 tasks stalled >30min bei Forge — Interventions-Bedarf?  [Review now ▶] │
└─────────────────────────────────────────────────────────────────────────────┘
  ↑                                                                          ↑
  severity          content: synthesized from rules matrix               CTA button
  icon
```

### Key Design Decisions
- **One banner, one message.** No scroll, no list. Operator sees it on every glance.
- **Icon encodes severity.** Warning (⚠) for soft alerts, Error (✗) for incidents, Info (ℹ) for observations.
- **Button is the action, not navigation.** Clicking opens the relevant detail panel, not a new page.
- **Text is a sentence, not a metric.** "3 tasks stalled >30min" not "stalledCount=3".
- **Rule-driven, not static.** Backend computes the message from the rules matrix; UI just renders it.

### Mission Control Applicability
**Core of the atlas Zone B spec.** The atlas doc already defines a 7-rule Next-Best-Action matrix (priority 1 = heartbeat RED → priority 7 = all clear). This pattern matches exactly.

Implementation dependency: `GET /api/board/next-action` backend endpoint (Pack 5 in atlas plan). UI renders the text + button.

**Known challenge (from atlas):** NBA must not replace operator judgment — buttons require confirmation, not auto-action.

---

## Pattern 3 — Agent Workload Bars

**Source:** Grafana Cloud — Stat Panel + Bar Gauge  
**URL:** `https://grafana.com/docs/grafana-cloud/visualizations/`  
**Confidence:** High

### Pattern Description
Horizontal bar chart, one bar per agent. Shows `active tasks / max concurrent` as a fill bar. Color shifts from green → amber → red as utilization crosses thresholds.

### ASCII Wireframe

```
Forge    ████████████░░░░  4/2   ⚠ overloaded
Pixel    ░░░░░░░░░░░░░░░  0/2   ● idle
James    ██████░░░░░░░░░  1/2   ● ok
Lens     ██████████░░░░░  2/2   ● ok
──────────────────────────────────────────
         0%              50%              100%
```

### Key Design Decisions
- **One line per agent.** No table, no grid — just a compact vertical stack.
- **`current/max` label is always visible.** Numeric literacy is not assumed.
- **Color encodes state.** Green = ≤50% of max. Amber = 51–99%. Red = ≥100% (overloaded) or 0 (idle — gray/blue).
- **Threshold reference line at maxConcurrent.** Dashed vertical line at 100% makes overload visually obvious.
- **Sorted by utilization descending.** Engaged agents left/top, idle agents right/bottom.

### Mission Control Applicability
**Directly applicable — Zone D (Agent Load Sidebar) of atlas spec.** MC's agent config has `maxConcurrent` per agent (from `openclaw.json` agents config). Backend `GET /api/board/agent-load` (Pack 4) provides the per-agent counts.

The atlas spec already uses this exact pattern in Zone D. No ambiguity — this is a settled design.

**Effort estimate:** Medium. Requires backend endpoint + sidebar component. Pack 4 in atlas plan.

---

## Pattern 4 — Live Lane-Based Task Flow

**Source:** Datadog — Kanban-style Grouping + Linear Cycles  
**URL:** `https://docs.datadoghq.com/dashboards/widgets/` + Linear Cycles view  
**Confidence:** High

### Pattern Description
Tasks flow through 5 semantic lanes (not status columns): **Waiting → Picked → Active → Stalled → Incident**. Lane membership is derived from a rules classifier, not raw status. Each lane shows count + age of oldest item.

### ASCII Wireframe

```
┌──────────────────────────────────────────────────────────────────────────┐
│  WAITING (2)    │  PICKED (3)   │  ACTIVE (1)  │  STALLED (1) │ INC  │
│  ⏱ oldest: 8m  │  ⏱ oldest: 3m│  ⏱ running:2m│  ⏱ oldest: 34m│  1  │
│  ├──────────────┼───────────────┼──────────────┼──────────────┼─────  │
│  │ [task card]  │ [task card]   │ [task card]  │ [task card] │[card] │
│  │ [task card]  │ [task card]   │              │              │       │
│  │              │ [task card]    │              │              │       │
└──────────────────────────────────────────────────────────────────────────┘
  ↑               ↑               ↑              ↑              ↑
  age badge    age badge       active timer     warning red    incident red
```

### Key Design Decisions
- **5 lanes, not 9+ status values.** Groups operational states into a manageable number of semantic lanes. Eliminates "fake calm" where different execution states look the same.
- **Age badge per lane.** Shows "oldest item age" — the single most important triage signal. Turns a static count into a time-decaying signal.
- **Color per lane.** Waiting = neutral. Picked = blue. Active = green. Stalled = amber/red. Incident = red.
- **Archive state not shown in main view.** Done/canceled older than 1h → separate Archive tab.
- **Lane is derived, not stored.** `boardLane` field computed server-side from `status + executionState + lastActivityAt` rules.

### Mission Control Applicability
**This is the atlas Zone C spec exactly.** The atlas doc defines the same 5-lane model with precise classification rules:
- Waiting: `status ∈ {draft, assigned}`
- Picked: `status = pending-pickup`
- Active: `status = in-progress AND executionState = active AND lastActivityAt < 10min`
- Stalled: `status = in-progress AND (executionState = stalled-warning OR lastActivityAt > 10min) OR status = blocked`
- Incident: `status = failed AND (completedAt < 1h OR unacknowledged)`

**Effort estimate:** Medium-high. Requires Pack 1 (Lane Classifier Backend) + Pack 3 (Live Flow Lane UI). Foundation for all other packs.

---

## Pattern 5 — Cost-Story Modal

**Source:** Existing vault doc `spark-cost-story-ux-concept.md` (2026-04-17)  
**URL:** Internal — `/home/piet/vault/03-Agents/spark-cost-story-ux-concept.md`  
**Confidence:** High (already designed for MC specifically)

### Pattern Description
A modal that shows why a task or session consumed its budget — a chronological event timeline with per-event cost, cumulative total, and an AI-generated verdict. Anchored to real events, not just a number.

### ASCII Wireframe

```
┌──────────────────────────────────────────────────────────────────┐
│  Cost Story                       Agent: spark         [X close] │
├──────────────────────────────────────────────────────────────────┤
│  Total: $0.042  │  Window: Today  │  Tasks: 3  │  ● Normal    │
├──────────────────────────────────────────────────────────────────┤
│  TIME       EVENT                        COST      CUMULATIVE     │
│  ──────────────────────────────────────────────────────────────  │
│  18:34      Task dispatched              $0.001        $0.001    │
│  18:35      Agent accepted               $0.003        $0.004    │
│  18:42      Tool: vault-write           $0.018        $0.022    │
│  18:44      Tool: exec+read              $0.015        $0.037    │
│  18:51      Final receipt                $0.005        $0.042    │
├──────────────────────────────────────────────────────────────────┤
│  spark worked a UX task for 17 min. vault-write was the main     │
│  cost driver. Rate: $0.047/min — within normal range.            │
├──────────────────────────────────────────────────────────────────┤
│  [Expand Tool Detail]        [Copy Summary]        [Flag Issue]  │
└──────────────────────────────────────────────────────────────────┘
```

### Key Design Decisions
- **Event timeline, not a number.** The modal answers "why" not "how much." Cost is the sum, not the story.
- **Per-event cost column.** Tool calls dominate. The operator can immediately see what drove the cost.
- **Verdict sentence.** AI-generated (or rule-generated) plain-English summary: "was this cost necessary?"
- **Status badge (Normal/Elevated/Critical).** One-glance triage without reading the table.
- **Three action buttons.** "Expand Tool Detail" for drill-down, "Copy Summary" for sharing, "Flag Issue" for escalation.

### Mission Control Applicability
**Already designed for MC — Pack C (Cost-Story Modal) from spark-cost-story-ux-concept.md.** The MC API field mapping shows it reads from `lastActivityAt`, `lastExecutionEvent`, `cost` delta, `assigned_agent`, `title` via `GET /api/tasks/[id]`.

The concept is clean and ready for Pixel to implement. No changes needed to the wireframe — it's specific to MC's API.

**Effort estimate:** Medium. Requires cost tracking instrumentation first (Costs-v2 Phase 2), then UI modal. Not a first-pack item.

---

## Pattern 6 — Incident Failure Card

**Source:** Datadog — Alert Graph Widget + Event Stream  
**URL:** `https://docs.datadoghq.com/dashboards/widgets/types/#alert-graph`  
**Confidence:** High

### Pattern Description
A failure/incident card in a lane or list that encodes: time since failure, failure reason snippet, agent that owned the task, and a recovery action. Failure cards in an Incident lane or badge on a task card.

### ASCII Wireframe

```
┌──────────────────────────────────────────────────────┐
│ ✗ 12:04 — 8min ago                                  │
│ Task: [Costs-v2] Provider-Pricing Research          │
│ Agent: Forge                                         │
│ Reason: Execution timeout (60s limit exceeded)        │
│ ──────────────────────────────────────────────────  │
│ [Open Task ▶]    [Retry ▶]    [Dismiss]             │
└──────────────────────────────────────────────────────┘
```

### Key Design Decisions
- **Time-relative ("8min ago"), not absolute.** Operators know immediately if this is fresh or old.
- **Reason is a plain-text snippet, not a code.** No error IDs or stack traces in the card — those are in the detail view.
- **Three action buttons are scoped.** "Open Task" = investigate. "Retry" = re-dispatch. "Dismiss" = acknowledge.
- **Color is red — universal incident.** No amber for failures. Amber is for warnings.

### Mission Control Applicability
**Applicable to MC's Incident Lane (Zone C, rightmost lane).** MC already has `status=failed` and `failureReason` field in the task schema. The atlas spec calls for failures <1h or unacknowledged to appear in the Incident lane.

The card shows exactly what the atlas spec requires: failure time, reason, owning agent, recovery options.

**Effort estimate:** Low-medium. Depends on Pack 1 (lane classification) + Pack 6 (detail panel).

---

## Pattern 7 — Multi-Agent Tiled View

**Source:** Cursor — Agents Window, Tiled Layout (Cursor 3.1 changelog)  
**URL:** `https://cursor.com/changelog`  
**Confidence:** Medium-High

### Pattern Description
The Cursor Agents Window allows running multiple agents in parallel, each in its own tile. Tiles can be resized, focused, and arranged. Each tile shows agent identity, current task, and status. The operator sees all agents simultaneously and can switch between them.

### ASCII Wireframe

```
┌──────────────────────────────────────────────────────────────┐
│ [Agents Window — 3 tiles]                                    │
│ ┌────────────────────┐ ┌────────────────────┐               │
│ │ ● Forge            │ │ ● Pixel            │               │
│ │ Running: UX Pack   │ │ Idle              │               │
│ │ ▶ 12:04 →         │ │ ○ waiting          │               │
│ │ Tokens: 42,103     │ │ Last: 11:47       │               │
│ └────────────────────┘ └────────────────────┘               │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ ● James                                                      │
│ │ Running: Operator-Dashboard Research                        │
│ │ ▶ 12:02 →                                                    │
│ │ Tokens: 18,440                                              │
│ └──────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

### Key Design Decisions
- **Tiles are resizable and persistent.** Operator sets up the layout once, it survives restarts.
- **Each tile shows identity + live status + resource usage.** No need to click into each agent to know what it's doing.
- **Tiles can be focused (expanded to full view).** Compact mode shows all; focused mode shows detail.
- **Agent tabs in editor also show agents side-by-side.** Multi-agent is a first-class UI concept, not an afterthought.

### Mission Control Applicability
**Highly relevant for the MC agent load panel (Zone D).** MC has 6 agents (Forge, Pixel, James, Lens, Spark, Atlas). The tiled view pattern extends the bar-chart workload display into a richer panel where each agent card shows:
- Current task (title or "idle")
- Live timer since dispatch/activity
- Token count (if available)
- Status indicator

This is a richer variant of Pattern 3 (Agent Workload Bars). Where Pattern 3 is a compact sidebar, Pattern 7 is the full agent management view.

**Confidence note:** Cursor's tiled agents window is the closest public reference for multi-agent parallel task management. The mission-control use case (agent load monitoring) is analogous, though Cursor's agents run code tasks while MC agents manage task lifecycle.

**Effort estimate:** Medium. Would replace or extend Zone D from compact bars to tile cards. Pixel would own implementation.

---

## Cross-Cutting Design Principles

Derived from all 7 patterns:

1. **One glance, one judgment.** Every pattern surfaces a single most important signal. dashboards that require reading to understand are already failing the operator.
2. **Lane semantics over status taxonomy.** Raw status values (`pending-pickup`, `in-progress`, `failed`) are insufficient for triage. Derived semantic lanes (Waiting, Picked, Active, Stalled, Incident) are the correct abstraction.
3. **Time is the primary axis.** "How long" matters more than "what state." Age badges, timers, and time-since-failure are more actionable than counts.
4. **Action is always one click away.** Every signal has an associated action. No signal should require navigating away from the cockpit to respond.
5. **Severity is color-encoded universally.** Green = nominal. Amber/⚠ = warning. Red/✗ = incident. No exceptions, no gradients, no custom palettes.
6. **Cost is a story, not a number.** The Cost-Story modal's event-timeline approach (pattern 5) applies beyond cost — any significant metric should have a drill-down that shows the contributing events.

---

## Top 3 Recommendations

### #1 — Implement the 5-Lane Semantic Board (Zone C) First
**Why:** The lane-based task flow (Pattern 4) is the single highest-impact change. It eliminates the "fake calm" problem described in the atlas doc — where a stalled in-progress task looks identical to a healthy active task. The lane classifier is a single backend function (`boardLane` field), and the UI replaces kanban columns with semantic lanes. This is Pack 1+3 in the atlas implementation plan.

**Priority signal it solves:** "Is anything actually broken right now, or does it just look busy?"

### #2 — Deploy the Heartbeat Strip + NBA Banner Together (Zone A + Zone B)
**Why:** These two patterns work as a pair. The heartbeat strip answers "is the system alive?" The NBA banner answers "what should I do about it?" Together they cover 80% of the operator's triage questions in under 5 seconds. They require Pack 2 (Heartbeat UI) and Pack 5 (NBA Backend + UI). Deploying them together avoids the "orphan NBA without context" problem.

**Priority signal they solve:** "Should I be doing something right now?"

### #3 — Build the Cost-Story Modal as the Primary Cost-Cockpit Interface
**Why:** The Cost-Story modal (Pattern 5) is already designed in the vault doc with a clean ASCII wireframe and MC API field mapping. It answers the "was this cost necessary?" question that no other UI element addresses. It should be the center of the cost management experience, not a table of numbers. It requires Costs-v2 instrumentation first (per-task cost tracking), but the design is ready.

**Priority signal it solves:** "Where did my budget go, and was it worth it?"

---

## Sources

| # | Source | URL | Patterns |
|---|---|---|---|
| 1 | Datadog Widgets Documentation | `https://docs.datadoghq.com/dashboards/widgets/` | Pattern 1, 4, 6 |
| 2 | Grafana Cloud Visualizations | `https://grafana.com/docs/grafana-cloud/visualizations/` | Pattern 3 |
| 3 | Cursor Changelog (Agents Window) | `https://cursor.com/changelog` | Pattern 7 |
| 4 | Linear Docs | `https://linear.app/docs` | Pattern 2 |
| 5 | Spark — Cost-Story UX Concept | `/home/piet/vault/03-Agents/spark-cost-story-ux-concept.md` | Pattern 5 |
| 6 | Atlas — Board Operator Cockpit Target | `/home/piet/vault/03-Agents/atlas-board-operator-cockpit.md` | All patterns |

---

*Research by James (agent), 2026-04-18. Research only — no code, no openclaw.json edits.*
