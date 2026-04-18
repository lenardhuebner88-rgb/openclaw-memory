# pending-pickup Recovery — Best Practices Research
**Task:** SPARK-PENDING-PICKUP-001  
**Agent:** Spark  
**Date:** 2026-04-18  
**Status:** Done

---

## Context

Task `6f6d32a9` failed with orphan timeout; Task `dc43610c` was canceled. The pending-pickup state in Mission Control represents a dispatched task that was never accepted by the target agent. Two remediation paths are evaluated.

---

## Option A: Automatic Receipt Timeout + Fallback

### What the docs say

OpenClaw's built-in background task system (docs: `automation/tasks.md`) has a **`lost` terminal state**:

> `lost` — the runtime lost authoritative backing state after a **5-minute grace period**.

This applies per task:
- ACP tasks: backing ACP child session metadata disappeared
- Subagent tasks: backing child session disappeared from the target agent store
- Cron tasks: cron runtime no longer tracks the job as active

The task lifecycle diagram shows:
```
queued --> running --> succeeded | failed | timed_out | cancelled | lost
```

### What this means for pending-pickup

The `lost` state is a **runtime-level** orphan detector — it fires when the OpenClaw task backing session disappears for >5 min. It does **not** directly address the **MC Board-level** `pending-pickup` state, which is a Mission Control store concept sitting above the OpenClaw task system.

However, the 5-minute grace period is the nearest built-in equivalent to a receipt timeout. To use it as a recovery mechanism:

**Implementation approach:**
1. A cron or heartbeat script polls `GET /api/tasks?status=pending-pickup`
2. For each task: if `dispatchedAt` is > 15 min ago and no `lastActivityAt` update occurred → treat as stuck
3. Action: send a "fallback receipt" (auto-accept) OR mark as `failed` with reason `receipt-timeout`
4. Optionally: re-dispatch to same or fallback agent

**Tradeoffs:**
| Pro | Con |
|-----|-----|
| Leverages built-in `lost` mechanism | `lost` is runtime-level, not MC Board-level |
| 5-min grace is documented, tested | 5 min may be too short for long-running agent startups |
| No new API surface needed | No built-in MC-level receipt timeout exists — must be layered on |

**Risks:**
- Agent may still be starting up legitimately → false positive auto-fail
- Auto-accepting a stuck task moves it to `in-progress` but the real agent session is dead → orphan with `in-progress` status instead
- Requires careful differentiation: genuinely slow start vs. dead session

**Sources:** OpenClaw docs `automation/tasks.md` (task lifecycle, `lost` state)

---

## Option B: Heartbeat Orphan Detection Reaktivierung

### Current state (HEARTBEAT.md Section 5)

HEARTBEAT.md Section 5 is **DEAKTIVIERT — STABILIZATION MODE**:

```
### 5. Orphaned Tasks starten
> ⛔ DEAKTIVIERT — STABILIZATION MODE — Keine Spawns.
```

The original intent was: scan for `status=pending-pickup` tasks that were never picked up, then auto-start (respawn) the agent. The local implementation already exists in HEARTBEAT.md logic for Sections 2A/2B (stale active/queued task detection), which could be extended to cover pending-pickup.

### Implementation approach

Reactivate Section 5 with a modified mandate: instead of auto-spawning, **auto-receipt + alert**:

1. Heartbeat checks `GET /api/tasks?status=pending-pickup`
2. If `dispatchedAt` + 15 min < now → orphan detected
3. Send accepted receipt: `PATCH /api/tasks/{id}` with `status=in-progress, executionState=active, receiptStage=accepted`
4. Then immediately send result receipt: `PATCH ... { status: failed, failureReason: "orphan-timeout — agent never accepted" }`
5. Alert to #alerts channel with task ID and age

Alternative (less aggressive): instead of failing immediately, re-dispatch once to a fallback agent or the same agent after cooldown.

**Tradeoffs:**
| Pro | Con |
|-----|-----|
| Uses existing heartbeat infrastructure | Was explicitly disabled — root cause may recur |
| Closes the loop: no forever-stuck pending-pickup | Re-spawning into a broken agent still fails |
| Allows differentiation: retry vs. fail-fast | Risk of kill-spawn loop if agent is fundamentally broken |

**Risks:**
- If the agent has a real but long startup (e.g., cold model init), 15-min timeout is too aggressive
- The original Section 5 was disabled for stabilization — reactivating without fixing root cause = same outcome
- Kill-spawn loops accumulate cost

**Sources:** HEARTBEAT.md Section 5 (DEAKTIVIERT), Section 2A/2B (existing orphan detection patterns)

---

## Recommendation

**Option B (Heartbeat Orphan Detection Reaktivierung) is the better foundation**, but with two changes vs. the original Section 5:

1. **Don't respawn blindly** — the original Section 5 was DEAKTIVIERT because it caused loops. Instead: fail-fast with alert, let Atlas decide.
2. **Extend Section 2A** (stale active tasks) to also catch `pending-pickup` orphans with `dispatchedAt` > 15 min — this is a minimal, non-destructive addition that uses existing patterns.

**Option A** is a good fallback for external monitoring (e.g., a dedicated cron job outside the heartbeat) but should not replace the heartbeat approach because:
- The `lost` state is runtime-level and doesn't propagate to the MC Board
- A separate cron provides defense-in-depth but can't fix what's already stuck

**Immediate next step:** Implement a `pending-pickup` check in the existing stale-task detection (Section 2) as a first safe step, before touching Section 5 reactivation.

---

## Sources Consulted

- OpenClaw Docs: `automation/tasks.md` (task lifecycle, `lost` state)
- OpenClaw Docs: `gateway/heartbeat.md` (heartbeat contract, `HEARTBEAT_OK`)
- OpenClaw Docs: `concepts/retry.md` (retry policy — not directly relevant but noted)
- HEARTBEAT.md Sections 2A, 2B, 5 (current implementation)
- GitHub Issues: login required, no public results accessible
- OpenClaw Discord: not accessible via web_fetch

---

*Research by Spark · 2026-04-18 · No implementation · Input for Atlas decision*
