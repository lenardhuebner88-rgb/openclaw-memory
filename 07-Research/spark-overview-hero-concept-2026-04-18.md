# Overview Hero — Zone A/B/C/D UX Concept
**Date:** 2026-04-18
**Type:** UX Prototype (Markdown Artifact)
**Scope:** Overview tab hero section, Zones A–D, no implementation
**Style:** Consistent with `spark-cost-story-ux-concept.md`

---

## User Story (3 Sentences)

As an operator I open the Overview tab and immediately see a live snapshot of system health, upcoming work, and agent capacity — without scrolling or filtering. The hero section answers three questions at a glance: *what needs me now, what is running, and is anything on fire?* I use the Overview as my cockpit before diving into Task Board or Pipeline details.

---

## Desktop ASCII Wireframe (100 chars wide)

```
┌──────────────────────────────────────────────────────────────┬────────────────┐
│  OVERVIEW HERO                                    Fri 18 Apr │ 14:08 Europe  │
├──────────────────┬───────────────────┬──────────────────────┴────────────────┤
│  ZONE A — Heartbeats (6)           │  ZONE B — Next-Best-Action Banner       │
│  ┌────┐┌────┐┌────┐┌────┐┌────┐┌────┐ │  ⚡ Forge: 3 active — capacity full │
│  │HB-1││HB-2││HB-3││HB-4││HB-5││HB-6│ │  ⚡ Lens: anomaly detected — action   │
│  │ ●  ││ ●  ││ ○  ││ ●  ││ ●  ││ ○  │ │  ⚡ spark: idle — 2 free slots      │
│  │OK  ││OK  ││STALE││OK  ││OK  ││STALE│ │                                       │
│  └────┘└────┘└────┘└────┘└────┘└────┘ │                                       │
├──────────────────┴───────────────────┴──────────────────────────────────────┤
│  ZONE C — Live Activity Stream (last 10 board events)                        │
│  ─────────────────────────────────────────────────────────────────────────── │
│  14:08 · task done · [Forge] MC Restart Loop Root Cause — RC documented     │
│  14:04 · task picked · [Spark] pending-pickup Recovery — researching        │
│  14:02 · agent load · Atlas/main at 1/1 · sre-expert at 3/3 ⚡ FULL        │
│  13:55 · anomaly · minimax prepaid burn above baseline ⚠                     │
│  13:51 · task failed · [Forge] Pipeline Tab UX — orphan timeout            │
│  13:48 · board event · Lifecycle report emitted for task 82fc...            │
│  13:41 · cost spike · openai-codex flatrate-rate-spike detected ⚠           │
│  13:38 · task picked · [Pixel] UI-Research Operator-Dashboard — accepted   │
│  13:30 · task done · [Lens] SelfOpt Dry-Run-Log-Review                     │
│  13:22 · heartbeat OK · spark · interval=30m · no anomalies                │
├──────────────────────────────────────────────────────────────────────────────┤
│  ZONE D — Agent Workload Bars (6 agents)                                    │
│  ─────────────────────────────────────────────────────────────────────────── │
│  Atlas        ██████████░░░░░░░░  1/1  ●                               │
│  Forge        ████████████████░░  3/3  ⚡ FULL                            │
│  Pixel        ██████░░░░░░░░░░░░  0/2                                     │
│  Lens         ██████░░░░░░░░░░░░  0/1                                     │
│  James        ████░░░░░░░░░░░░░░  0/1                                     │
│  Spark        ████░░░░░░░░░░░░░░  0/2                                     │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Zone A — Six Heartbeats (Concrete Representation)

Each heartbeat card shows:

```
┌──────────┐
│  spark   │   ← agent label (dispatchTarget)
│  ●       │   ← status dot: ●=active  ○=stale  ◐=idle
│  OK      │   ← state text: OK | STALE | IDLE | DEAD
│  30m     │   ← interval (from heartbeat config)
│  11:08   │   ← last heartbeat timestamp (lastActivityAt)
└──────────┘
```

**State logic:**
- `● OK` — lastActivityAt < 5 min ago → heartbeat healthy
- `○ STALE` — lastActivityAt 5–15 min ago → heartbeat missed
- `◐ IDLE` — lastActivityAt > 15 min AND agent has no active tasks
- `✕ DEAD` — lastActivityAt > 30 min OR no heartbeat record ever

**API source:** `GET /api/tasks?status=in-progress` filtered by `assigned_agent` + `lastActivityAt`  
**API source (events):** `GET /api/board/events?limit=10` or board-events stream  
**Note:** If an agent has no heartbeat record at all, show `? UNK` (unknown) instead of STALE/DEAD.

---

## Zone B — Next-Best-Action Banner (5 Priority Rules)

Banner shows the single most urgent recommended action. Rules evaluated in priority order:

**Rule 1 (P0 — Critical):** An anomaly exists with `severity=high`  
→ Show: `⚠ {provider} {kind} — {recommended_action}`  
→ Source: `GET /api/costs/anomalies`

**Rule 2 (P1 — Agent at capacity):** Any agent has `activeCount == maxConcurrent`  
→ Show: `⚡ {agent} at {activeCount}/{maxConcurrent} — capacity full`  
→ Source: `GET /api/board/agent-load`

**Rule 3 (P2 — Stale tasks):** Any task has `lastActivityAt` > 10 min AND `status=in-progress`  
→ Show: `🐢 {n} stale task(s) — last activity > 10 min ago`  
→ Source: `GET /api/tasks?status=in-progress`

**Rule 4 (P3 — Pending-pickup):** Any task has `status=pending-pickup`  
→ Show: `📬 {n} task(s) pending pickup — may need manual dispatch`  
→ Source: `GET /api/tasks?status=pending-pickup`

**Rule 5 (P4 — All clear):** No rule 1–4 fires  
→ Show: `✓ All systems nominal — {n} tasks running, {n} agents idle`  
→ Source: computed from board state

**Multiple matches:** Show only the highest-priority rule. Lower-priority items are visible in the activity stream (Zone C).

---

## Zone C — Live Activity Stream (Last 10 Board Events)

Each line: `{timestamp} · {event_kind} · {description} [{optional_agent}] {status_icon}`

**Event kinds and icons:**
| Event | Icon | Description format |
|---|---|---|
| task picked | 📬 | `task picked · [{agent}] {task_title_truncated}` |
| task done | ✅ | `task done · [{agent}] {task_title_truncated}` |
| task failed | ❌ | `task failed · [{agent}] {task_title_truncated} — {failureReason_short}` |
| task canceled | ➖ | `task canceled · [{agent}] {task_title_truncated}` |
| anomaly detected | ⚠ | `{provider} {kind} · severity={severity}` |
| agent load change | ⚡ | `{agent} at {n}/{max} · {state}` |
| board event | 📋 | `{event_detail}` (lifecycle, audit, etc.) |
| heartbeat OK | 💓 | `{agent} · interval={interval} · no anomalies` |
| cost spike | 💰 | `{provider} {kind} detected` |

**API source:** `GET /api/board/events?limit=10` — assumption: such endpoint exists or board-events.jsonl is readable  
**Fallback:** Polling `GET /api/tasks?limit=5&sort=updatedAt:desc` as a proxy for recent activity  
**Assumption:** If an event type has no structured endpoint, use task list + costs/anomalies as the two live feeds and interleave them by timestamp.

---

## Zone D — Six Agent Workload Bars

**Bar logic:**
```
█ = one active task slot   ░ = empty slot
{n}/{max} = active/maxConcurrent   state = NORMAL | ELEVATED | FULL
```

**Full bar (capacity 100%):**
```
Forge ████████████████████ 3/3 ⚡ FULL
```

**Normal bar (capacity < 80%):**
```
Atlas ██████████░░░░░░░░░ 1/1 ●
```

**State indicators:**
- `●` — NORMAL: `activeCount < maxConcurrent * 0.8`
- `⚡` — ELEVATED: `activeCount >= maxConcurrent * 0.8` AND `activeCount < maxConcurrent`
- `⚡ FULL` — FULL: `activeCount == maxConcurrent`

**API source:** `GET /api/board/agent-load` (available in current MC)  
**Agents shown:** Atlas, Forge, Pixel, Lens, James, Spark — in display name order

---

## Mobile Fallback Sketch

On mobile (≤480 px), the hero stacks vertically:

```
┌─────────────────────────────┐
│ OVERVIEW   Fri 18 Apr 14:08 │
├─────────────────────────────┤
│ ZONE B — Banner (full width)│
│ ⚡ Forge at 3/3 — capacity  │
├─────────────────────────────┤
│ ZONE A — Heartbeats (grid) │
│ ┌─────┐┌─────┐┌─────┐     │
│ │ ● OK││ ○   ││ ● OK│     │
│ │spark││forge││pixel│     │
│ └─────┘└─────┘└─────┘     │
├─────────────────────────────┤
│ ZONE D — Workload Bars     │
│ Forge  ████████░░  3/3 ⚡  │
│ Atlas  ██░░░░░░░  1/1     │
│ Pixel  ░░░░░░░░░  0/2      │
├─────────────────────────────┤
│ ZONE C — Activity (scroll) │
│ (same format, 5 items max) │
└─────────────────────────────┘
```

**Mobile constraints:**
- Zone A: 3-column grid, each card compact (agent name + dot only)
- Zone C: show 5 most recent items, "show more" link
- Zone D: truncate agent names to 6 chars, bar ≤ 20 chars wide

---

## Three Core Operator Questions

1. **What needs me right now?**  
   Zone B banner + Zone A stale indicators give a one-glance answer. If Zone B is empty (Rule 5 fires), nothing requires immediate attention.

2. **Is the system healthy?**  
   Zone D workload bars show capacity pressure at a glance. Zone C anomaly events surface cost or stability issues. Zone A heartbeat dots show agent liveness.

3. **What happened recently?**  
   Zone C activity stream covers the last ~10 board events. Task completions, failures, dispatches, and anomalies are interleaved chronologically so the operator can reconstruct recent history without leaving the Overview.

---

## Implementation Notes (Assumptions Stated)

| Item | Assumption |
|------|-----------|
| Board events endpoint | `GET /api/board/events` is assumed to exist; if not, fallback to task list polling |
| Zone A heartbeat data | Derived from `lastActivityAt` on active task records + `GET /api/board/agent-load` |
| NBA priority | Rules evaluated server-side or client-side; Zone B shows only top-firing rule |
| Bar rendering | Client-side; max bar width = terminal pixel width or 20 chars |
| Anomaly API | `GET /api/costs/anomalies` confirmed live with real data today |

---

*Spark · 2026-04-18 · No code · Input for Pixel implementation pass*
