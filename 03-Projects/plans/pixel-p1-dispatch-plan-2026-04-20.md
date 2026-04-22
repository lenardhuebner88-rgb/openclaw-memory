# Pixel P1 Taskboard-v2 Dispatch — Next-Steps Plan

**Drafted:** 2026-04-20 14:24 CEST
**Author:** Commander (claude-desktop, pre-bot-handoff)
**Status:** awaiting operator approval to execute Step 1+2
**Precondition met:** E2E-verification of Codex' lifecycle-bypass fix PASSED (see §E2E Results below)

---

## Context

Terminal-Claude (Codex) hat am 2026-04-20 die lifecycle-bypass-lücke gefixt (commits `725faea` runtime-hygiene + `92485aa` deploy-restore). Die ursprüngliche Bug-Class: worker-monitor + direkte PATCH-calls konnten Tasks illegal von jedem state nach `in-progress` schieben, was zu `b5f27a85`-style auto-fails führte.

E2E-verification today confirmed: **der guard hält.** Illegale transitions geben HTTP 409 mit klarer Fehlermeldung. Codex' fix funktioniert sustainably.

Pixel-P1 task wurde heute **erfolgreich in draft-state** auf das board gelegt (`a8100ac6-df0b-4e16-b4d6-ac5119730e46`, POST /api/tasks → 201 in 41ms). Der anschließende direkte `/dispatch`-call wurde korrekt abgelehnt (HTTP 409: "Task status 'draft' is not dispatchable — set status to 'assigned' first") — auch das ist **working as designed**, Teil der neuen discipline.

---

## E2E Results (2026-04-20 14:09–14:24 CEST)

| Phase | Check | Ergebnis |
|---|---|---|
| 1 | Deployed commits (725faea + 92485aa) | ✅ vorhanden |
| 1 | MC health overall | `degraded` (unrelated: attentionCount=14 legacy-failed) |
| 1 | MC health board/dispatch | `ok` / `ok` |
| 1 | tasks.json baseline | 327 total (179 done, 134 canceled, 14 failed) |
| 2 | Illegal PATCH `done → in-progress` | ✅ **HTTP 409 rejected** — *"Direct activation blocked. Tasks may not enter active execution through PATCH. Use POST /api/tasks/:id/dispatch to reach pending-pickup, then POST /api/tasks/:id/receipt…"* |
| 3 | 2× monitoring started (journalctl + board-events.jsonl) | ✅ PIDs 786232 + 786233 |
| 4 | POST /api/tasks with pixel-payload (10 KB) | ✅ HTTP 201 in 41ms, id `a8100ac6…` |
| 5 | 90s watch window | 0 transitions (expected — draft-state sticky bis manual promote) |
| 6 | Post-state | status=`draft`, dispatchState=`draft`, executionState=`queued`, dispatched=`false` |
| 6 | board-events captured | 1 (`task-created` via `tasks-route` actor) |

**Verdict: E2E PASS ✅** — Codex' fix ist sustainably deployed. Der neue state-machine-guard ist aktiv und korrekt.

---

## Lifecycle Path (per `src/lib/task-status-transition.ts`)

```
draft
  └─ assigned         (PATCH /api/tasks/:id { "status": "assigned" })
      └─ pending-pickup   (POST /api/tasks/:id/dispatch { target })
          └─ in-progress      (POST /api/tasks/:id/receipt { receiptStage: "accepted|started|progress" })
              └─ review           (POST /api/tasks/:id/complete)
                  └─ done              (POST /api/tasks/:id/finalize)
```

Escape hatches: `failed → assigned` (retry), `* → canceled` (admin-close). `done` und `canceled` sind terminal.

---

## Next Steps — execution order

### Step 1 — Promote draft → assigned

**Action:** `PATCH /api/tasks/a8100ac6-df0b-4e16-b4d6-ac5119730e46 { "status": "assigned" }`

**Rationale:** `draft → assigned` ist legal (TASK_STATUS_TRANSITIONS[draft] = ['assigned', 'canceled']). Nach dem Promote ist der Task dispatchable.

**Expected:** HTTP 200, task-object mit `status: "assigned"`, neue board-event `status-changed`.

**Rollback:** `PATCH { "status": "draft" }` wenn etwas schief geht. Oder full-cancel: `POST /api/tasks/{id}/admin-close`.

**Verification:** `curl -s localhost:3000/api/tasks/{id} | jq '.status'` → `"assigned"`.

---

### Step 2 — Dispatch to Pixel (frontend-guru)

**Action:** `POST /api/tasks/a8100ac6-df0b-4e16-b4d6-ac5119730e46/dispatch { "target": "frontend-guru" }`

**Rationale:** `assigned → pending-pickup` via official dispatch-endpoint. Schreibt `dispatchTarget`, `dispatchedAt`, `dispatched: true`.

**Expected:** HTTP 200/201, task-object mit `status: "pending-pickup"`, `dispatched: true`, board-event `task-dispatched`.

**Rollback:** `POST /api/tasks/{id}/admin-close` wenn dispatch nicht greift.

**Verification:** `curl -s localhost:3000/api/tasks/{id} | jq '{status,dispatched,dispatchTarget,dispatchedAt}'`.

---

### Step 3 — Worker pickup

Pixel wird den task über einen dieser Pfade picken:

**Pfad A (cron-driven, primary):** `worker-monitor.py` läuft alle 5 min (`*/5 * * * *`), scannt tasks.json für status=`pending-pickup` + assigned_agent=`frontend-guru`, schreibt receipt via `POST /api/tasks/{id}/receipt { receiptStage: "accepted" }` → auto-promote zu `in-progress`.

**Pfad B (manual dispatch):** Falls worker-monitor nicht greift (cron-lag, flock-held, Pixel-workspace down), kann Atlas manuell via openclaw-gateway dispatchen.

**Expected within ≤5 min:** status transitions: `pending-pickup → in-progress`, `executionState: "running"`, worker-runs.json gets new entry.

**Verification:**
```bash
tail -F /home/piet/.openclaw/workspace/mission-control/data/board-events.jsonl | grep a8100ac6
systemctl --user status openclaw-gateway
jq '[.[] | select(.task_id=="a8100ac6...")] | last' /home/piet/.openclaw/workspace/mission-control/data/worker-runs.json
```

**If Pfad A does not fire within 6 min:** investigate `worker-monitor.log`:
```bash
tail -60 /home/piet/.openclaw/workspace/scripts/worker-monitor.log
flock -n /tmp/worker-monitor.lock || echo "lock held"
```

---

### Step 4 — Monitor Pixel execution

Während Pixel arbeitet:
- Live-feed: `tail -F data/board-events.jsonl | jq 'select(.taskId=="a8100ac6...")'`
- Receipt-cadence: Pixel sendet alle ~30s `receiptStage: "progress"`. Wenn länger als 5 min kein receipt → worker is stuck, check Pixel workspace.
- MC dashboard: `http://huebners:3000/taskboard?focus=in-progress` zeigt den task live.

**Red flags:**
- `executionState: "stalled"` → stale-open watchdog fires
- receipt-stage stuck at `accepted` für > 3 min → Pixel might be booting, check `workspace-frontend-guru` logs
- `status: "failed"` → Pixel reports fail, check `resultSummary` + `failureReason`

---

### Step 5 — Completion + visual QA

Wenn Pixel fertig meldet (`in-progress → review` via `/complete`):

1. **Visual QA:** Pixel liefert Branch-name + screenshots in `resultSummary`. Operator prüft:
   ```bash
   cd ~/.openclaw/workspace/mission-control
   git fetch && git checkout pixel/p1-taskboard-v2
   npm run dev  # → screenshot iPhone-14 breakpoint
   ```
2. **Code-review:** Pixel's diff läuft durch pre-existing review-gate (typecheck + vitest + build).
3. **Finalize:** Wenn review-clean → `POST /api/tasks/{id}/finalize` → `review → done`.
4. **Merge:** Operator (manual) merged Pixel's branch in `master`, pushed, deployed via `deploy.sh`.

---

## Risk register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| worker-monitor lock-held (flock) | low | medium | manuelle cron-force: `rm /tmp/worker-monitor.lock && /home/piet/.openclaw/workspace/scripts/worker-monitor.py` |
| openclaw-gateway not relaying | low | high | restart gateway (CanReload=no, full `systemctl --user restart openclaw-gateway`) |
| Pixel-workspace stale | medium | medium | check `systemctl --user status workspace-frontend-guru` if exists, or `ls -la .openclaw/workspace-frontend-guru/` for last activity |
| taskboard-v2 diff conflicts with current MC | medium | medium | Pixel handles rebase; if deep conflict → revert diff, redraft handoff |
| Test suite breakage from pixel's changes | medium | medium | pre-deploy gate: typecheck + vitest must pass (already enforced by deploy.sh) |
| dispatch-state-machine regression | low | critical | R51 schema-gate + task-status-transition.ts are now canonical; any regression would show as HTTP 409 on legitimate transitions → abort |

---

## Audit trail (existing)

- `2026-04-20 13:30`: Codex deploy (725faea + 92485aa) verified
- `2026-04-20 14:09`: E2E-test pre-flight + invariant test PASSED
- `2026-04-20 14:09`: Pixel task created (a8100ac6), status=draft
- `2026-04-20 14:23`: Direct dispatch attempt on draft — correctly rejected (HTTP 409)
- `2026-04-20 14:24`: Next-steps plan drafted (this doc)

---

## Next audit-entries (after each step)

Template for audit.jsonl:
```json
{"ts":"<ISO>","action":"lifecycle-promote","taskId":"a8100ac6-...","from":"draft","to":"assigned","actor":"operator","verified":"curl /api/tasks/<id>.status==assigned"}
{"ts":"<ISO>","action":"dispatch","taskId":"a8100ac6-...","target":"frontend-guru","response":"HTTP 200","verified":"dispatched==true"}
```

---

## Operator decision points

- **Go for Step 1?** — promote draft → assigned. Single PATCH call, reversible.
- **Go for Step 2 after Step 1 lands clean?** — dispatch to Pixel. Reversible via admin-close.
- **Monitor Pfad A for 6 min before escalating to Pfad B?**

---

## Appendix — commands reference

```bash
# status poll
curl -s http://localhost:3000/api/tasks/a8100ac6-df0b-4e16-b4d6-ac5119730e46 | jq '{status, dispatched, dispatchState, dispatchTarget, executionState, assignee}'

# Step 1
curl -s -X PATCH http://localhost:3000/api/tasks/a8100ac6-df0b-4e16-b4d6-ac5119730e46 \
  -H 'Content-Type: application/json' -d '{"status":"assigned"}'

# Step 2
curl -s -X POST http://localhost:3000/api/tasks/a8100ac6-df0b-4e16-b4d6-ac5119730e46/dispatch \
  -H 'Content-Type: application/json' -d '{"target":"frontend-guru"}'

# worker-monitor force-run
flock -n /tmp/worker-monitor.lock.manual python3 /home/piet/.openclaw/workspace/scripts/worker-monitor.py

# cancel
curl -s -X POST http://localhost:3000/api/tasks/a8100ac6-df0b-4e16-b4d6-ac5119730e46/admin-close \
  -H 'Content-Type: application/json' -d '{"reason":"operator-canceled","actor":"operator"}'
```
