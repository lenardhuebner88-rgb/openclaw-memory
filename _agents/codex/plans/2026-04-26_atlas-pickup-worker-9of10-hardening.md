---
agent: codex
date: 2026-04-26
status: active
scope: "Atlas pickup hardening + 3 worker-system sprints"
operator: lenard
---

# Atlas Pickup + Worker-System Hardening

## Live Rootcause

Atlas/main konnte in folgenden Zustand geraten:

- Task bleibt `pending-pickup`
- Worker-Run ist bereits `claimState=claimed`
- Task hat Claim-Bindings wie `workerSessionId` / `acceptedAt`
- aber kein `lastHeartbeatAt`, kein Prozessbeleg, kein Terminal-Receipt

Dadurch behandelten Pickup-Proofs die Task als durch aktive Session-Locks blockiert, waehrend Auto-Pickup sie wegen claimed open run uebersprang. Ergebnis: keine neue Aufnahme, kein sauberer Abschluss.

## Code-Fix

Geaendert:

- `/home/piet/.openclaw/scripts/auto-pickup.py`
- `/home/piet/.openclaw/workspace/mission-control/scripts/followup-dispatch-guard.mjs`
- `/home/piet/.openclaw/workspace/mission-control/tests/auto-pickup-claimed-no-heartbeat-regression.test.ts`

Neuer Runtime-Pfad:

1. Auto-Pickup erkennt alte `pending-pickup`-Runs mit `claimed` aber ohne Heartbeat.
2. Der offene Run wird mit `outcome=requeued-claimed-no-heartbeat` geschlossen.
3. Die Task wird auf `assigned / queued` zurueckgesetzt.
4. Claim-Bindings werden entfernt, damit ein neuer sauberer Pickup moeglich ist.

## Gates

- `python3 -m py_compile /home/piet/.openclaw/scripts/auto-pickup.py`
- Regressionstest: `auto-pickup requeues stale claimed pending-pickup run without heartbeat`
- `npx vitest run tests/auto-pickup-claimed-no-heartbeat-regression.test.ts tests/pickup-proof.test.ts tests/autonomy-draft-create-regression.test.ts`
- `npm run typecheck`
- Worker Proof: `openRuns=0`, `criticalIssues=0`
- Pickup Proof: `pendingPickup=0`, `criticalFindings=0`

## Sprint 1 - Receipt/Run-Wahrheit

Ziel: sicherstellen, dass offene Runs ohne Heartbeat nicht mehr unsichtbar blockieren.

Gate:

- Worker Proof bleibt `ok`.
- Reconciler Dry-run liefert `proposedActions=0`.
- Auto-Pickup Regression bleibt gruen.

Status 2026-04-26T15:47Z: **PASS**

- Neuer Regressionstest erstellt und ausgefuehrt.
- `npx vitest run tests/auto-pickup-claimed-no-heartbeat-regression.test.ts tests/pickup-proof.test.ts tests/autonomy-draft-create-regression.test.ts` -> 3 Files / 21 Tests passed.
- `npm run typecheck` -> passed.
- Worker-Reconciler Dry-run -> `proposedActions=0`.

## Sprint 2 - Pickup/Lock-Recovery

Ziel: stale Claim-/Session-Locks automatisch in einen sicheren Requeue-Zustand bringen, ohne Fanout.

Gate:

- Pickup Proof bleibt `ok`.
- Follow-up Guard Dry-run liefert `proposedActions=0`.
- Auto-Pickup-Livezyklus erzeugt keine neuen blocked-by-active-session-lock Findings.

Status 2026-04-26T15:49Z: **PASS**

- Live-Soak nach Auto-Pickup-Zyklus:
  - Pickup Proof `pendingPickup=0`, `criticalFindings=0`, `activeSessionLocks=0`
  - Worker Proof `openRuns=0`, `criticalIssues=0`
- `followup-dispatch-guard.mjs --dry-run` -> `proposedActions=0`
- `worker-reconciler.mjs --dry-run` -> `proposedActions=0`

## Sprint 3 - Kontrollierte Autonomie-Erweiterung

Ziel: genau eine operator-gated Follow-up-Preview erzeugen und beweisen, dass Autonomie nicht still auto-dispatched.

Gate:

- Draft hat `autoSource=atlas-autonomy`.
- Draft hat `approvalMode=operator`, `approvalClass`, `riskLevel`, `operatorLock=true`.
- Kein Auto-Dispatch ohne Operator-Gate.
- Worker/Pickup-Proofs bleiben gruen.

Status 2026-04-26T16:03Z: **PASS**

- Codex erzeugte eine operator-gated Preview:
  - `a0d6e563-3e9b-4504-a27f-58d74a5100c3`
  - `status=draft`, `dispatchState=draft`, `dispatched=false`
  - `autoSource=atlas-autonomy`
  - `approvalMode=operator`
  - `approvalClass=gated-mutation`
  - `riskLevel=low`
  - `operatorLock=true`
  - `lockReason=atlas-autonomy-awaiting-approval`
- Atlas-Live-Test aus requeued Task:
  - `5298c76a-c6c5-41c2-a139-48288a38d346` -> `done`
  - `1f7df3eb-a505-4db7-9e73-4ec6000acaba` -> `done`
  - Atlas erzeugte genau eine weitere operator-gated Preview:
    - `f05dbb39-f6f6-42ca-b18e-de4267f2e994`
    - `status=draft`, `dispatchState=draft`, `approvalMode=operator`, `approvalClass=safe-read-only`, `operatorLock=true`

## Abschluss-Gate 2026-04-26T16:03Z

- Worker Proof: `status=ok`, `openRuns=0`, `criticalIssues=0`
- Pickup Proof: `status=ok`, `pendingPickup=0`, `criticalFindings=0`
- Reconciler Dry-run: `proposedActions=0`
- Follow-up Guard Dry-run: `proposedActions=0`
- systemd failed units: `0`
- Services/Timer active:
  - `mission-control.service`
  - `qmd-mcp-http.service`
  - `m7-auto-pickup.timer`
  - `m7-worker-monitor.timer`
  - `m7-session-freeze-watcher.timer`

Health bleibt formal `degraded/warning`, weil eine alte failed Parent-Task (`d0007dc7...`) als sichtbares Recovery-Signal zaehlt. Diese ist bewusst nicht still versteckt worden; sie hat jetzt eine operator-gated Follow-up-Preview als naechsten kontrollierten Schritt.

## Stop-Regeln

- Kein Fanout.
- Kein Cron-Auto-Dispatch.
- Keine Modellwechsel.
- Keine sudo-/root-Aktion.
- Bei `criticalIssues>0`, `pendingPickup>0` oder `openRuns>0`: stoppen und Rootcause isolieren.
