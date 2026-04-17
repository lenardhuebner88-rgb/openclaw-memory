---
title: Worker System Hardening — Post-Happy-Path
version: 1.0
status: pilot-ready
owner: Principal Architect / Reliability Auditor
created: 2026-04-17
depends_on: e2e_orchestrator_run_2026-04-17.md, mc_hardening_2026-04-17.md
---

# Worker System Hardening — Post-Happy-Path

Umsetzungsplan für die reale Fehlerbild-Härtung des MC-Worker-Systems nach grünem E2E.

## EXECUTIVE JUDGMENT

Der Happy Path ist trivial: assigned → dispatch → pending-pickup → receipt → in-progress → result → done. Das haben wir 5× grün gesehen. Die operative Qualität entscheidet sich bei den **unglücklichen** Pfaden: doppelt dispatched, Agent crasht mitten im Progress, result-receipt ohne vorheriges accepted, stale workerSessionId mit unbekanntem Prefix. Der heutige Code behandelt viele dieser Fälle **implicit** — Transitionen passieren silent, Monitor löscht ghost-states ohne Audit, failure-reasons werden bei admin-close überschrieben. Das funktioniert bis der erste echte Stall auftritt, dann verliert man Incident-Kontext.

Härtung ist kein Großrefactor. Es sind **acht kleine, reversible Schritte**, die die State-Machine explizit machen, Idempotenz herstellen und Monitor-Aktionen audit-fähig.

## ROOT CAUSE

1. **State-Machine ist Daten, nicht Code.** `task-status-transition.ts` ist eine Matrix, aber Tangential-Felder (`executionState`, `dispatchState`, `receiptStage`) driften mit eigener Logik — silent mismatch möglich.
2. **Receipt-Sequence nicht erzwungen.** `/receipt` akzeptiert `progress` ohne vorheriges `accepted`. Erste Ankunft promoted, egal welcher Typ.
3. **Dispatch ist nicht idempotent.** Zweiter Dispatch-Call im engen Zeitfenster trifft pending-pickup → Code returnt still `{ok:true, task}` ohne zweite Notification, aber auch ohne 409. Caller weiß nicht, ob sein Call eine Wirkung hatte.
4. **worker-monitor.py macht destructive Writes ohne Dry-Run.** Ghost-state → `status=failed` in gleichem Cycle. Ein Bug im Prefix-Match kann 10 Tasks gleichzeitig kippen.
5. **failure-reason wird überschrieben.** admin-close, Retry-Logik und monitor-fail schreiben in dasselbe Feld. Wer zuletzt schreibt, gewinnt — Incident-Kontext geht verloren.
6. **Stall-Detection fehlt.** in-progress + `lastActivityAt > 10min ago` ist nicht unterschieden von gesundem in-progress. Nur pending-pickup hat einen Timeout.
7. **Retry-Logik ist opaque.** `retryCount`, `maxRetries`, `nextRetryAt` existieren als Felder, aber wer/wann inkrementiert sie — unklar, kein Single-Path.

## TARGET WORKER LIFECYCLE

```
                       ┌──────────────┐
                       │    draft     │
                       └──────┬───────┘
                              │ PATCH status=assigned (require assigned_agent)
                              ▼
                       ┌──────────────┐
                       │   assigned   │──────────── admin-close ──▶ canceled
                       └──────┬───────┘
                              │ POST /dispatch (idempotent, token-keyed)
                              ▼
                       ┌─────────────────┐
                       │ pending-pickup  │───── 15min no-receipt ──▶ failed(never-picked-up)
                       └──────┬──────────┘
                              │ receipt:accepted (erste, nur accepted erlaubt)
                              ▼
                       ┌──────────────┐
                       │ in-progress  │─── 10min no-activity ──▶ warn → 30min ──▶ failed(stalled)
                       └──────┬───────┘       (soft)               (hard)
                              │ receipt:progress (beliebig oft, extend lastActivityAt)
                              │ receipt:blocked → blocked
                              │ receipt:result → done
                              │ receipt:failed → failed(<reason preserved>)
                              ▼
                       ┌──────────────┐
                       │ done/failed/ │ terminal. Nur admin-close darf zu canceled,
                       │  blocked     │ aber failure-reason bleibt preserved.
                       └──────────────┘
```

Invarianten:
- **Erste Receipt ist IMMER `accepted`.** progress/result/failed vor accepted → 409 mit Hinweis.
- **Terminal-States schreiben failure-reason immutable.** Spätere Writes appenden, überschreiben nicht.
- **workerSessionId-Prefix strikt enforced** auf `{gateway:, main:, monitor:}`. Unbekannt → 400 bei Receipt-Entry, kein silent kill.
- **Dispatch ist idempotent** per `dispatchToken` (Client-generiert, in der Task persistiert). Zweiter Call mit gleichem Token → 200 + `idempotent:true`, kein Duplicate-Notification.

## FAILURE MATRIX

| # | Szenario | Detektion | Soll-Verhalten | Audit |
|---|---|---|---|---|
| 1 | Duplicate Dispatch (same token) | dispatchToken-Match | 200 + `idempotent:true`, keine zweite Discord-Msg | board-event `dispatch-idempotent` |
| 2 | Duplicate Dispatch (no token) | Client-Bug | 409 `dispatchToken required for re-dispatch` | board-event `dispatch-rejected` |
| 3 | Pending-Pickup > 15min | monitor-cron | status=failed, `failureReason.category="never-picked-up"`, assignee preserved | board-event + Discord-alert |
| 4 | Progress ohne vorheriges accepted | receipt-sequence-check | 409 `first receipt must be accepted` | board-event `receipt-out-of-order` |
| 5 | Result ohne progress | erlaubt (kurze Tasks) | auto-promote wenn accepted vorher, sonst 409 | — |
| 6 | Stalled in-progress 10min | monitor-cron soft-warn | `executionState=stalled-warning`, Discord-msg, kein fail | board-event |
| 7 | Stalled in-progress 30min | monitor-cron hard | status=failed, `failureReason.category="stalled"`, lastActivity preserved | board-event + Discord-alert |
| 8 | Ghost workerSessionId-Prefix | receipt-API validator | 400 sofort, Receipt nicht persistiert, Task bleibt | api-log `receipt-ghost-prefix` |
| 9 | Orphaned workerRun ohne Task | monitor-cron | workerRun gelöscht, log `orphan-worker-run` | monitor-log |
| 10 | Agent crash mid-progress (TCP reset) | lastActivityAt drift | Behandlung wie #6/#7 | — |
| 11 | admin-close auf failed-Task | close-handler | failureReason preserved, nur `resolvedAt` + status=canceled, board-event `close-preserves-failure` | board-event |
| 12 | Retry-Cap erreicht | retry-handler | `maxRetriesReached=true`, kein neuer Dispatch, requires human-override | board-event `retry-exhausted` |
| 13 | Monitor selbst crasht | externer health-check (systemd) | systemd restart, letzter cycle-log preserved | systemd-journal |

## IMPLEMENTATION PACK

Acht Pakete, in dieser Reihenfolge. Jedes: <200 Zeilen Diff, reversible, Feature-Flag wo möglich.

### Pack 1 — `failureReason` als Struktur (Foundation)
- Typ erweitern: `failureReason?: string` → `failureReason?: { category: 'never-picked-up'|'stalled'|'worker-error'|'dispatch-error'|'admin-override'|'retry-exhausted', message: string, source: 'monitor'|'agent'|'api'|'admin', at: string, preservedFrom?: FailureReason }`.
- `updateTask`-Normalizer: bei Schreiben prüfen ob Feld schon gesetzt → in `preservedFrom` nesten statt überschreiben.
- Migration: bestehende String-Reasons wrappen zu `{category:'worker-error', message:<legacy>, source:'api', at:<updatedAt>}`.

### Pack 2 — Receipt Sequence Enforcement
- `/api/tasks/[id]/receipt/route.ts`: Vor jedem Persist-Write prüfen: `prevStage === undefined` → nur `accepted` erlaubt; `prevStage === 'accepted'` → progress/result/failed/blocked erlaubt; `prevStage === 'progress'` → progress/result/failed/blocked.
- Verletzung → 409 mit `nextAllowedStages` im Body.

### Pack 3 — workerSessionId-Prefix Validator
- Neues Modul `src/lib/worker-session-id.ts` mit `ALLOWED_PREFIXES = ['gateway:', 'main:', 'monitor:']` und `validateWorkerSessionId(id) → {ok, reason}`.
- Receipt-Route + worker-monitor.py rufen vor jedem persist auf. Ghost-Prefix → 400 API / 0-Action Monitor + Log.

### Pack 4 — Dispatch Idempotency
- Task-Type: `dispatchToken?: string`.
- `/api/tasks/[id]/dispatch/route.ts`: akzeptiert optionales `dispatchToken` im Body. Wenn Task bereits dispatched und `dispatchToken === stored` → 200 idempotent. Wenn dispatched und Token fehlt oder anders → 409.
- `sendExecutionReport` nur beim ersten Dispatch-Call.

### Pack 5 — Stall-Detector in worker-monitor.py
- Neue Thresholds: `STALL_WARN_MINUTES = 10`, `STALL_HARD_MINUTES = 30`.
- Branch für `status === 'in-progress' && executionState === 'active'`:
  - warn-Alter > 10min → PATCH `executionState='stalled-warning'` + Discord-soft.
  - > 30min → status=failed, failureReason preserve.
- `lastActivityAt` wird bei jeder progress-receipt aktualisiert (ist bereits so — verify).

### Pack 6 — Monitor Dry-Run-Mode + Report
- Environment-Flag `WORKER_MONITOR_DRY_RUN=1` → Monitor plant alle Writes in ein Report-File `~/.openclaw/workspace/logs/worker-monitor-plan-<ts>.json`, führt aber nichts aus.
- Cron-Wrapper: bei neuer Monitor-Version 24h Dry-Run zuerst, User-Review, dann Live.

### Pack 7 — failureReason-Preservation bei admin-close
- `admin-close/route.ts`: wenn `currentTask.failureReason` existiert, ins Patch mit `preservedFrom` wrappen und `failureReason: { category:'admin-override', ..., preservedFrom: current.failureReason }` setzen.
- Board-Event mit flag `preservedFailureReason:true`.

### Pack 8 — Retry-Logik Single-Path
- Ein Modul `src/lib/task-retry.ts` mit `attemptRetry(task): RetryDecision`.
- Jeder Call-Site (monitor, admin-retry, receipt-failed) delegiert an dieses Modul.
- Decision enthält: `nextRetryAt`, `retryCount`, `reasonIfBlocked`. Schreibt board-event `retry-decision`.

## FILES / COMPONENTS

| Pack | Files |
|---|---|
| 1 | `src/lib/taskboard-types.ts`, `src/lib/taskboard-store.ts` (normalizeTask + picklist + patch-handler) |
| 2 | `src/app/api/tasks/[id]/receipt/route.ts` |
| 3 | new: `src/lib/worker-session-id.ts`; edit: `src/app/api/tasks/[id]/receipt/route.ts`, `scripts/worker-monitor.py` |
| 4 | `src/lib/taskboard-types.ts`, `src/lib/task-dispatch.ts`, `src/app/api/tasks/[id]/dispatch/route.ts` |
| 5 | `scripts/worker-monitor.py` |
| 6 | `scripts/worker-monitor.py` + systemd-cron wrapper |
| 7 | `src/app/api/tasks/[id]/admin-close/route.ts` |
| 8 | new: `src/lib/task-retry.ts`; edit: `scripts/worker-monitor.py`, recovery-action route, receipt-failed branch |

Alle MC-File-Changes bekommen `.bak-worker-harden-2026-04-17`. Build via gehärtete Sequenz (kein `deploy.sh`).

## RISKS

1. **Receipt-Sequence-Enforcement kippt alte Agents**, die direkt `progress` senden. Mitigation: Pack 2 läuft erst 48h im Warn-Mode (409 nur geloggt, nicht returned), danach hart.
2. **Idempotency-Token bricht Clients ohne Token.** Mitigation: Token optional in Pack 4, erst nach 2 Wochen Pflicht.
3. **Monitor Dry-Run verzögert echte Stall-Erkennung** um 24h. Mitigation: nur bei Deploy neuer Monitor-Version, nicht dauerhaft.
4. **failureReason-Migration kann tasks.json korrumpieren** (Size-Verdopplung). Mitigation: Backup + 1-Task-Test vor Batch.
5. **Stall-Thresholds zu strikt** (10min warn) killt langläufige Legit-Tasks. Mitigation: konfigurierbar per Env, Start-Wert 20/60 statt 10/30.

## TEST PLAN

Erweiterung des existierenden `mc-pending-pickup-smoke.sh` zu einer Suite `mc-worker-hardening-suite.sh` mit 10 Sub-Tests, je einer pro Failure-Matrix-Zeile. Struktur pro Test:

1. Setup: Task erstellen via Smoke-Helper.
2. Action: den Failure-Mode provozieren (z.B. receipt progress ohne accepted).
3. Assert: Status + failureReason.category + board-event vorhanden.
4. Cleanup: admin-close, failureReason preservation verifizieren.

Suite läuft täglich via Cron (nicht stündlich — zu viel Board-Noise). Sub-Test-Pass-Rate muss ≥ 10/10 vor jedem Pack-Merge.

Zusätzlich: **Chaos-Durchlauf** einmalig nach Pack 1–8. Lens fährt eine 2h-Session mit zufälligen Failure-Injections über 20 Tasks. Acceptance: kein Lost-Incident, kein silent kill, keine corrupted tasks.json.

## ROLLBACK

Pro Pack:
1. **Code**: git revert + `.bak-worker-harden-2026-04-17` als Fallback-Restore.
2. **tasks.json** (nur Pack 1/4 mutieren Schema): Backup `data/tasks.json.bak-worker-harden-<ts>` vor Migration. Rollback = Restore + Restart.
3. **worker-monitor.py**: altes Script als `.bak-worker-harden` parken, Cron-Config zeigt auf Symlink `~/.openclaw/scripts/worker-monitor-current.py` — Rollback = Symlink umhängen, kein neuer Cron-Write.

Globaler Kill-Switch: `WORKER_HARDENING_ENABLED=0` in MC-env + monitor-env → alle neuen Validierungen skippen (nur Logging, kein Reject). Deploy des Kill-Switch = 1 Commit Edit + Build.

## RECOMMENDED EXECUTION AGENT

- **Forge (sre-expert)** — primary. Alle 8 Packs fallen in Infra/Code-Scope, Python-Monitor + TS-State-Machine sind seine Stärke.
- **Lens (efficiency-auditor)** — audit role. Baseline-Messung vor Pack 1 (aktuelle Failure-Rate, Ghost-Kill-Count letzte 30 Tage), After-Messung nach Pack 8, Chaos-Durchlauf.
- **Atlas (main)** — orchestrator. Pack-Promotion-Gate, Discord-Kommunikation bei Rollouts, Kill-Switch-Bedienung bei Incident.
- **Pixel (frontend-guru)** — nur Pack-UI-Badges (stalled-warning, preservedFailureReason) optional, nicht im kritischen Pfad.

Rollen-Invariante: Forge schreibt Code und Tests, Lens misst und reviewt, Atlas entscheidet Live-Rollout. Kein Worker-Agent deployed ohne Lens-Before-After-Report.

## ACCEPTANCE CRITERIA

Alle messbar gegen Baseline Woche 0.

1. **Happy-Path unverändert grün** (Smoke-Suite 10/10, keine Regression).
2. **Failure-Matrix-Suite 10/10 pass** nach Pack 8.
3. **Ghost-Session-Kills: 0** seit Pack 3 (vorher im Schnitt 2–4/Woche laut monitor-log).
4. **Duplicate-Dispatch-Events: erkannt und korrekt behandelt**, manuelle Stichprobe im board-event-log.
5. **failureReason-Preservation: 100 %** bei admin-close von failed-Tasks (Test: 5 manuelle Close-Runs, alle zeigen `preservedFrom` gefüllt).
6. **Monitor Dry-Run-Report** verfügbar und inspizierbar vor jedem Monitor-Deploy.
7. **Stall-Detection**: Chaos-Durchlauf erzeugt ≥ 3 stalled-warning und ≥ 1 stalled-failed Events, alle mit `lastActivityAt` preserved.
8. **Retry-Decisions** kommen ausschließlich aus `task-retry.ts` (grep bestätigt: keine direkten retryCount-Mutationen außerhalb).
9. **MTTR für Stall-Incident** (synthetisch injiziert): ≤ 30min End-to-End (Detection → Discord-Alert → Operator-Reaction).
10. **Keine tasks.json-Korruption** über gesamten Pilotzeitraum (Schema-Validator-Script Exit 0 jeden Morgen).

Pass = 9 von 10. Regression in #1 (Happy-Path) ist Hard-Stop, kein Pass möglich.

---

## Umsetzungsreihenfolge (Prio-geordnet)

1. **Pack 1** (failureReason-Struktur) — Foundation, blockt 5 andere Packs.
2. **Pack 3** (Ghost-Prefix-Validator) — stoppt aktives Datenmüll-Risiko.
3. **Pack 5** + **Pack 6** parallel (Stall-Detector + Dry-Run) — schließt das größte operative Loch.
4. **Pack 7** (Preservation bei admin-close) — klein, sauberer Win.
5. **Pack 2** (Receipt-Sequence) — 48h Warn-Mode, dann hart.
6. **Pack 4** (Dispatch-Idempotency) — nach Receipt-Sequence, weil Client-Contract.
7. **Pack 8** (Retry-Single-Path) — Refactor, letzter Schritt.

Gesamt-Pilotdauer: 10 Arbeitstage bei Forge-Fulltime, 14 bei Teilzeit.

## Referenzen

- `/home/piet/.openclaw/workspace/memory/e2e_orchestrator_run_2026-04-17.md` — Happy-Path-Baseline
- `/home/piet/.openclaw/workspace/mission-control/AGENTS.md` — Task-Lifecycle + Post-Write Verify (Phase 2)
- `/home/piet/vault/03-Agents/atlas-session-memory-operating-model.md` — Session-Typen für Umsetzungs-Sessions
- `scripts/worker-monitor.py` — aktueller Monitor, Ausgangsbasis Pack 5/6
