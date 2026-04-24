---
title: S-UX Phase 0 stateTransitions Writer-Inventar
created: 2026-04-22
purpose: S-UX Phase 0 Pre-Flight — identifiziert welche Sites heute `updatedAt` / `lastActivityAt` schreiben, damit Phase 0 Backend-Fix (stateTransitions[]) klaren Refactor-Scope hat
scope: MC backend code, read-only grep
measurement-date: 2026-04-22 ~23:30 CEST
status: report
---

# S-UX Phase 0 stateTransitions Writer-Inventar

## Summary

**Status heute:** `stateTransitions`-Array existiert **nicht** in tasks.json (grep = 0 Treffer).
**Writer-Sites für `updatedAt` / `lastActivityAt`:** **~40** identifizierte Stellen, verteilt auf **12 Files** (Backend routes + libs).

**Konsequenz für S-UX Phase 0:**
- Jeder dieser Writer-Sites muss auch `stateTransitions.push({state: ..., at: ..., attemptId: ...})` aufrufen, wenn eine semantische State-Transition stattfindet
- Nicht jeder Write ist eine Transition: reine "heartbeat"-Updates (lastActivityAt ohne Status-Change) sollen NICHT in stateTransitions landen → **Semantic filter nötig**

---

## A. Writer-Sites gruppiert nach Responsibility

### A.1 API-Route-Handler (State-Mutations)

| Path | Line(s) | Writes | Transition-Type | stateTransitions needed? |
|---|---|---|---|---|
| `src/app/api/worker-runner/route.ts` | 85 | `lastActivityAt` | heartbeat? | Klären |
| `src/app/api/tasks/[id]/fail/route.ts` | 75 | `lastActivityAt` | failed (terminal!) | **JA** → state='failed' |
| `src/app/api/tasks/[id]/receipt/route.ts` | 367, 465, 528, 553 | `lastActivityAt` | mixed (progress/result/fail) | **JA per stage** |
| `src/app/api/tasks/[id]/complete/route.ts` | 114 | `lastActivityAt` | done | **JA** → state='done' |

### A.2 Libs (Transition-Writers)

| Path | Line(s) | Writes | Transition-Type |
|---|---|---|---|
| `src/lib/task-dispatch.ts` | 278-279, 305-306, 340, 363-364 | `updatedAt` + `lastActivityAt` | dispatched / pickup_claimed (6 writes in 1 flow!) | **JA** state='dispatched' oder 'pickup_claimed' |
| `src/lib/taskboard-store.ts` | 509, 518, 535, 536 | `updatedAt` + `lastActivityAt` | diverse (dispatched/reviewed/admin-close) | **JA** per patch-kind |
| `src/lib/taskboard-routine-check.ts` | 106, 107, 134, 135, 164, 165, 197, 198 | `updatedAt` + `lastActivityAt` | **4 automatic-mutation sites** (routine cleanup) | **Diskutieren** — automatic state-transitions? |
| `src/lib/api-metrics.ts` | 47, 137, 169 | `updatedAt` (metrics-store) | NOT task-state — metrics snapshot-time | **NEIN** — eigenes Feld |
| `src/lib/live-agents-payload.ts` | 101, 267, 297, 299 | `updatedAt` READ (not write) | read-only consumer | **NEIN** |
| `src/lib/taskboard-intelligence.ts` | 189 | `updatedAt` READ | read-only consumer | **NEIN** |

### A.3 UI-Consumer (reads only)

| Path | Line(s) | Reads |
|---|---|---|
| `src/app/kanban/PipelineClient.tsx` | 573 | `updatedAt` für Display | Update auf `stateTransitions` Reader |

---

## B. State-Machine-Implications

**Aus T2.1 S-INFRA + T1 S-RELIAB-P0 zusammenhängend:**

Die vollständige State-Machine ist:
```
created → dispatched → pickup_claimed → running → (progress*)
                    ↓                           ↓
                    cancelled                   done | failed | blocked
```

**Transition-Events die stateTransitions erfassen sollte:**
- `dispatched` (→ tasks-dispatch.ts)
- `pickup_claimed` (→ S-RELIAB-P0 T1 neuer state)
- `running` (→ receipt/route stage='progress' first)
- `progress` N× (→ receipt/route stage='progress' repeat) **– evtl. dedupe?**
- `done` (→ complete/route)
- `failed` (→ fail/route)
- `blocked` (→ receipt/route stage='blocked')
- `canceled` (→ move/route to='canceled')

**Heartbeat-only Updates (NICHT Transition):**
- worker-runner/route.ts:85 (reine Liveness)
- routine-check pure cleanup patches (wenn Status unchanged)

**→ S-UX Phase 0 braucht explizit:**
1. Helper `recordStateTransition(task, state, attemptId?)` in `taskboard-store.ts`
2. Jede Writer-Site: prüfen ob `patch.status` Transition-semantik hat → `recordStateTransition()` aufrufen
3. `attemptId` aus S-FND T2 als optionaler Parameter

---

## C. Coordination-Matrix

| Sprint | Touchpoint | Konflikt? |
|---|---|---|
| **S-FND T2** `attemptId` | S-UX T1 nutzt attemptId in stateTransitions-Entries | Depends-on. S-FND T2 first. |
| **S-RELIAB-P0 T1** `pickup_claimed`-state | S-UX T1 stateTransitions muss diesen State kennen | Parallel OK, State-Machine-Update gemeinsam |
| **S-RPT T1** governance-signals.ts | Liest `task.status` — keine Schema-Änderung für tasks.json, nur additive stateTransitions[] | Kein Konflikt |
| **S-INFRA T2** worker-monitor.py | Liest `task.lastActivityAt` für Stall-Detection → später auch stateTransitions[] analog | Parallel OK |

---

## D. Konkrete S-UX Phase 0 Task-Breakdown

**T1a Schema-Definition** (~30 min, Forge):
- Typ-Definition `StateTransition` in `src/lib/taskboard-types.ts`
- Tasks-Schema erweitert mit `stateTransitions?: StateTransition[]` (optional, backward-compatible)
- Migration-Script: bestehende Tasks bekommen leeres Array

**T1b Helper + Call-Site-Migration** (~2-3h, Forge):
- `recordStateTransition(patch, task)` Helper in `taskboard-store.ts`
- 8 State-Transition-Writer-Sites integrieren (siehe A.1 + A.2)
- 4 "heartbeat-only" Sites EXPLIZIT ausschließen (kein stateTransitions-Append)
- Test: 10 synthetische Task-Lifecycles, korrekte Transitions aufgenommen

**T1c Reader-Migration** (~1h, Forge):
- Pipeline-Tab nutzt `stateTransitions.filter(s => s.state === 'failed').at` statt `updatedAt`
- PipelineClient.tsx:573 refactor
- Feature-Flag `STATE_TRANSITIONS_V1=0|1` für Dual-Read

**DoD:**
- 10 synthetische Lifecycles in stateTransitions korrekt
- Pipeline-Tab zeigt korrekte "failed at" Timestamps
- Alte `updatedAt` / `lastActivityAt` semantisch erhalten
- Heartbeat-only Updates erzeugen keine spurious Transitions

---

## E. Reproducibility

```bash
# Writer-Sites find
ssh homeserver "cd /home/piet/.openclaw/workspace/mission-control && grep -rn 'updatedAt\s*[:=]\|lastActivityAt\s*[:=]' src/ --include='*.ts' --include='*.tsx' | grep -v 'interface\|type\|\.spec\|test'"

# Existing stateTransitions (should be 0)
ssh homeserver "cd /home/piet/.openclaw/workspace/mission-control && grep -rn 'stateTransitions' src/"
```

---

## F. Next-Actions (Handoff to S-UX T1 Owner = Forge)

| ID | Owner | Priority | Due | Reason |
|---|---|---|---|---|
| `ux-phase0-schema-def` | forge | P0 | T1a start | StateTransition type in taskboard-types.ts |
| `ux-phase0-helper` | forge | P0 | T1b start | recordStateTransition() in taskboard-store.ts |
| `ux-phase0-writer-migration` | forge | P0 | T1b main | 8 Writer-Sites integrieren |
| `ux-phase0-reader-migration` | forge | P1 | T1c | Pipeline-Tab Phase-0-Consumer |
| `ux-phase0-coordinate-sfnd-t2` | atlas | P0 | pre-T1a | attemptId-Feld verfügbar stellen |
| `ux-phase0-coordinate-sreliab-p0-t1` | atlas | P1 | T1b concurrent | pickup_claimed-state in FSM |
