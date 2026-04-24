# OpenClaw P6 Pickup/Lock/Health Hardening

Datum: 2026-04-24
Owner: Codex
Scope: Mission Control Stabilisierung nach P5 Canary

## Ziele
- Session-Locks als harte Wahrheit nur bei lebendem Runtime-Prozess blockieren; stale Locks bleiben Warnung.
- Pending-pickup/Claim-Timeout-Zustände read-only beweisbar machen.
- Reconcile nur lokal und targeted ausführen: Default `--dry-run`, Execute nur mit konkretem Task.
- Health-Degradation mit Worker/Pickup/Reconcile/Cost-Signalen erklärbar machen, ohne `/api/health` mutierend zu machen.

## Quality Gates
- `npx vitest run tests/runtime-soak-proof.test.ts tests/runtime-soak-canary-script.test.ts`
- `npx vitest run tests/pickup-proof.test.ts tests/pickup-reconcile-script.test.ts`
- `npx vitest run tests/health-reconciliation-proof.test.ts`
- `npm run typecheck`
- Production Build nach API/UI-Code-Änderungen.
- Kontrollierter Restart von `mission-control.service`.
- Live-Probes: Runtime-Soak, Pickup-Proof, Health-Reconciliation-Proof, Worker-Reconciler-Proof, Reconcile-Proof, Context-Budget-Proof, Cost-Governance-Proof, `/api/health`.

## Statuslog
- 2026-04-24T09:22:56Z P6 neu aufgesetzt, weil der erwartete Codex-Vault-Planpfad im Live-Vault fehlte. Startzustand: P6.1 Code ist im Repo vorhanden, P6.2 Grunddateien sind angelegt, Tests/Gates noch offen.
- 2026-04-24T09:24:25Z P6.1/P6.2 Gate grün: `npx vitest run tests/runtime-soak-proof.test.ts tests/runtime-soak-canary-script.test.ts` und `npx vitest run tests/pickup-proof.test.ts tests/pickup-reconcile-script.test.ts` jeweils erfolgreich. `scripts/pickup-reconcile.mjs` ist ausführbar; Default bleibt Dry-run, Execute bleibt auf `--task-id` begrenzt.
- 2026-04-24T09:26:27Z P6.3 implementiert: `/api/ops/health-reconciliation-proof` als read-only Proof. Kombi-Gate grün: `npx vitest run tests/runtime-soak-proof.test.ts tests/runtime-soak-canary-script.test.ts tests/pickup-proof.test.ts tests/pickup-reconcile-script.test.ts tests/health-reconciliation-proof.test.ts` = 5 Dateien / 18 Tests passed. `npm run typecheck` passed.
- 2026-04-24T09:31:19Z Live-Restsignal klassifiziert: alte terminale Auto-Pickup-Claim-Timeouts zählen nicht mehr als aktive Recovery. Gate grün: `npx vitest run tests/historical-failure-artifacts.test.ts tests/health-reconciliation-proof.test.ts tests/runtime-soak-proof.test.ts tests/pickup-proof.test.ts tests/pickup-reconcile-script.test.ts` = 5 Dateien / 25 Tests passed. `npm run typecheck` passed.
