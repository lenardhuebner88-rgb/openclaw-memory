# Auto-Pickup Proof + E2E Hardening

Datum: 2026-04-24
Owner: Codex
Scope: Auto-Pickup-Edge-Crash, Proof-Signalqualitaet, wiederholbarer Real-Test-Harness.

## Ziel
Das System gilt erst als gruen, wenn Auto-Pickup-Edge-Cases getestet sind, historische Claim-Timeouts nicht mehr als aktuelle Stoerung missverstanden werden und ein orchestrierter Live-Audit Main + Worker unter laufendem Heartbeat prueft.

## P1 Auto-Pickup-Crash
- Rootcause fuer `UnboundLocalError: task` in `cleanup_unclaimed_spawn_locks` isolieren.
- Regressionstest fuer malformed/legacy Lock-Zustand ergaenzen.
- Minimalfix im Runtime-Script, keine breite Cron-/Gateway-Aenderung.
- Gate: Python-Tests gruen, `m7-auto-pickup.service` ohne Traceback.

## P2 Pickup-Proof-Signalqualitaet
- `claimTimeouts` in historisch vs. aktuell/aktiv trennen.
- Alte Log-Tail-Timeouts duerfen Proof nicht degradieren.
- Neue aktive Pending-Pickup-/Claim-Probleme bleiben Warn/Critical.
- Gate: Vitest fuer historische vs aktive Timeout-Klassifizierung, Live-Proof ohne alte Timeout-Degradation.

## P3 E2E-Orchestrated Audit
- Neues lokales Script `scripts/runtime-soak-e2e-audit.mjs`.
- Default `--dry-run`; echte Mutation nur mit `--execute`.
- Sequenziell genau ein Worker-Canary und optional Main-Canary mit `--allow-main`.
- Audit prueft: dispatch, accepted/result, `workerSessionId`, keine Open Runs, kein neuer Claim-Timeout, kein Child-Canary, Health/Pickup/Worker/Runtime final gruen.
- Gate: Script-Test + Live-Audit-Report.

## Follow-up Sprint Gate
- Sprint-Dokument in `04-Sprints/planned/` anlegen.
- Enthalten: Scope, Real-Use-Cases, Gates, offene Risiken fuer P4.

## Statuslog
- 2026-04-24T12:48:02Z Plan angelegt.
- 2026-04-24T12:49:06Z P1 Gate gruen: Regressionstest fuer orphan Lock ohne passende Task ergaenzt; `python3 -m py_compile auto-pickup.py` und Auto-Pickup-Unittests 14/14 passed. Live `m7-auto-pickup.service` oneshot endete `status=0/SUCCESS`, Timer active/waiting. Cron-Log enthaelt nur alte Tracebacks, keine neue Exception nach Fix.
- 2026-04-24T12:50:10Z P2 lokal gruen: Pickup-Proof trennt `claimTimeouts` (aktive Task-Findings), `historicalClaimTimeouts` und `totalClaimTimeoutEvents`. Regressionstest fuer resolved/historische Claim-Timeouts ergaenzt; `tests/pickup-proof.test.ts` 5/5 passed, `npm run typecheck` passed. Live-Deploy folgt mit P3-Build.
- 2026-04-24T12:52:03Z P3 lokal gruen: `scripts/runtime-soak-e2e-audit.mjs` angelegt. Default dry-run, execute nur mit `--execute`; plant Worker + optional Main, wartet optional auf Eligibility, prueft terminale Receipts, Health/Pickup/Worker/Runtime, neue Claim-Timeouts und Child-Canaries. Tests `runtime-soak-e2e-audit-script`, `runtime-soak-canary-script`, `pickup-proof` 17/17 passed. Live-Dry-run: Pixel sofort ausfuehrbar, Main korrekt im Cooldown.
