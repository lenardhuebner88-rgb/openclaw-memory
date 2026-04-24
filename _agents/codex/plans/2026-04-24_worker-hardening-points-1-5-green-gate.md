---
status: done
owner: codex
created: 2026-04-24T18:20:16Z
closed: 2026-04-24T19:01:06Z
scope:
  - worker-claim-truth
  - runner-exit-watchdog
  - health-reconcile-classification
  - auto-pickup-launch-isolation
  - minimax-status-reporting
  - five-agent-soak-suite
---

# Worker Hardening Points 1-5 Green Gate

## Live IST Before

- Mission Control war aktiv, aber Worker-Truth hatte noch mehrere Stabilitaetsluecken: Claim-Bindung, Runner-Exit ohne terminale Receipt, historische Superseded-Failures und Auto-Pickup-Prozess-Isolation.
- Minimax wurde in Status/Kostenlogik wie ein harter Prepaid-Pool behandelt. Das passte nicht zum aktuellen Tokenplan/Abo-aehnlichen Modell.
- Abschluss-Gate wurde nur akzeptiert, wenn Live-Proofs, Tests, Build, Restart, 5-Agent-Canary und 10-Minuten-Stabilitaet gruene Signale liefern.

## Step 1 - Claim-/Heartbeat-Wahrheit in Worker Runs

Umgesetzt:
- `worker-terminal-callback.ts` erweitert Worker-Runs um `claimState`, `claimedAt`, `lastHeartbeatAt`.
- Claim-Rebind setzt jetzt explizit `claimState: claimed`, `claimedAt` und Heartbeat-Evidence.
- Reconciler-Typen und Pickup-Claim-Test angepasst.

Quality Gate:
- `npx vitest run tests/pickup-claim-route.test.ts tests/receipt-run-binding-regression.test.ts tests/worker-run-reconciler.test.ts`
- Ergebnis: 21 Tests passed.
- `npm run typecheck` passed.
- Discord-Step-Report: `1497301706437034246`.

## Step 2 - Runner-Exit-Watchdog Proof/Action

Umgesetzt:
- Neuer Action-Typ `fail-runner-exit-without-terminal-receipt`.
- Stale active runs ohne Heartbeat/Prozess-Evidence werden als Runner-Exit-Fall klassifiziert.
- `scripts/worker-reconciler.mjs` kann den Action-Typ im Dry-run zeigen und gezielt ausfuehren.

Quality Gate:
- Zieltests passed: 21 Tests.
- `npm run typecheck` passed.
- `node scripts/worker-reconciler.mjs --dry-run` zeigte `proposedActions: []`.
- Discord-Step-Report: `1497302468202332160`.

## Step 3 - Superseded/Replacement Gate Health Classification

Umgesetzt:
- Historische Replacement-Gate-Failures mit abgeschlossener Dispatch-Evidence werden als historische Artefakte statt aktive Execution-Probleme klassifiziert.
- Fuenf bekannte superseded Failure Records wurden per Admin-Close mit Backup bereinigt.

Backup:
- `/home/piet/.openclaw/backup/audit-2026-04-24/mission-control-data/tasks.json.step4-superseded-health.bak`

Bereinigte Task IDs:
- `d8deb3b3-a382-47c3-bb4b-dfe46cbf29bb`
- `acaf3eee-38fd-4dd9-9281-f1c583baa5ad`
- `53bce56b-e2aa-43fa-a354-1606922f553a`
- `44d8037a-ea0c-4358-a631-0563fdb33b18`
- `56fc8f1b-1c6d-4a98-b1ee-c9a3319e31f8`

Quality Gate:
- `npx vitest run tests/historical-failure-artifacts.test.ts tests/operational-health.test.ts tests/health-route-ledger.test.ts`
- Ergebnis: 26 Tests passed.
- `npm run typecheck` passed.
- Live `/api/health`: `status=ok`, `recoveryLoad=0`, `attentionCount=0`.
- Discord-Step-Report: `1497303000111386837`.

## Step 4 - Auto-Pickup Launch Isolation

Umgesetzt:
- `auto-pickup.py` kann Worker jetzt per transientem systemd User-Service starten.
- `m7-auto-pickup.service` nutzt `AUTO_PICKUP_LAUNCH_MODE=systemd-service`.
- Claim-Timeout-Cleanup stoppt gezielt die transient gestartete Unit.

Backups:
- `/home/piet/.openclaw/backup/audit-2026-04-24/scripts/auto-pickup.py.step1-launch-isolation.bak`
- `/home/piet/.openclaw/backup/audit-2026-04-24/systemd-user/m7-auto-pickup.service.step1-launch-isolation.bak`

Quality Gate:
- `python3 -m py_compile /home/piet/.openclaw/scripts/auto-pickup.py` passed.
- Dry-run mit `AUTO_PICKUP_LAUNCH_MODE=systemd-service` passed.
- Transient-systemd smoke start/stop passed.
- `systemctl --user start m7-auto-pickup.service` passed.
- Pickup proof ok.
- Discord-Step-Report: `1497303558977224925`.

## Step 5 - Minimax Tokenplan Reporting Fix

Umgesetzt:
- `cost-alert-dispatcher.py` normalisiert Minimax `prepaid-exhaust-before-reset` als Tokenplan-Warnung, nicht als harte Critical/Umroute.
- Mission-Control-Kostenlogik behandelt `TOKEN_PLAN`/`SUBSCRIPTION_TOKEN_PLAN` wie flatrate-aehnliche Tokenplaene.
- Minimax UI/Status-Texte wurden auf Tokenplan-Hinweise umgestellt.
- Billing-Mode-Reference wurde auf `TOKEN_PLAN` aktualisiert.

Backups:
- `/home/piet/.openclaw/backup/audit-2026-04-24/scripts/cost-alert-dispatcher.py.minimax-token-plan.bak`
- `/home/piet/.openclaw/backup/audit-2026-04-24/mission-control-memory/billing-modes-reference.yaml.minimax-token-plan.bak`

Quality Gate:
- `python3 -m py_compile /home/piet/.openclaw/scripts/cost-alert-dispatcher.py` passed.
- Dispatcher smoke: Minimax wird als `warning`/`token-plan-quota-observe` formatiert.
- `npx vitest run tests/cost-governance-proof.test.ts tests/cost-governance-script.test.ts`
- Ergebnis: 7 Tests passed.
- `npm run typecheck` passed.
- Production build passed.
- `mc-restart-safe 120 "codex-worker-hardening-minimax-step"` passed.
- Live `/api/costs/budget-status`: Minimax `mode=flatrate`, `tone=ok`.
- Discord-Step-Report: `1497305224564576276`.

## Additional Gate Fix - Context Budget Proof

Umgesetzt:
- Session-size warning alerts bleiben jetzt warning und werden nicht als aktive critical blocker gewertet.
- Critical bleibt nur fuer Rotation/Hard-Level.

Quality Gate:
- `npx vitest run tests/context-budget-proof.test.ts tests/runtime-soak-proof.test.ts`
- Ergebnis: 22 Tests passed.
- `npm run typecheck` passed.
- Production build passed.
- `mc-restart-safe 120 "codex-context-budget-proof-fix"` passed.
- Live `/api/ops/context-budget-proof`: `status=ok`, `activeCriticalFindings=0`.

## Five-Agent Soak Suite

Gestartete echte Canary-Tasks:
- Forge / `sre-expert`: `53737803-14f2-41a9-a491-80cd2889f6f4` -> done/result, `canary-ok`.
- Pixel / `frontend-guru`: `842886a7-7a5c-4842-9eac-11442079b324` -> done/result, `canary-ok`.
- Lens / `efficiency-auditor`: `5272e0cf-55d3-4ba5-9ae6-13b76dd5c893` -> done/result, health read-only pass.
- Spark: `39b6036d-97f8-40fe-a480-e97a0270a67a` -> done/result, `canary-ok`.
- James: `cc00085c-4e12-4582-91ed-381dc295f998` -> done/result, accepted/completed.

Hinweis:
- Main war wegen Agent-Session-Cooldown nicht Canary-eligible. Fuer das 5-Agent-Gate wurden deshalb fuenf eligible Worker-Agenten genutzt.

## 10-Minuten-Stabilitaetstest

Artefakt:
- `/tmp/codex-10min-stability-2026-04-24.jsonl`

Ergebnis:
- 11 Samples von `2026-04-24T18:48:15Z` bis `2026-04-24T18:58:46Z`.
- `allGreen: true`.
- Letztes Sample:
  - `/api/health`: `ok`
  - Pickup-Proof: `ok`, `pendingPickup=0`, `claimTimeouts=0`, aktive Locks `0`
  - Worker-Proof: `ok`, `openRuns=0`, `criticalIssues=0`
  - Runtime-Soak-Proof: `ready`, `blockedBy=[]`
  - Board Snapshot: `1786` bytes

## Final Live Gate

- `mission-control.service`: active.
- `m7-auto-pickup.timer`: active.
- `openclaw-gateway.service`: active.
- `/api/ops/runtime-soak-proof`: `ready`, `blockedBy=[]`, `workerCriticalIssues=0`, `openRuns=0`, `contextActiveCriticalFindings=0`.
- `/api/board/snapshot?view=live`: `1786` bytes.
- Final Discord Green Report: `1497311642516717720`.

## Residual Risks

- `totalClaimTimeoutEvents=15` ist historisch, nicht aktiv. Sollte im naechsten Sprint als Verlauf getrennt von Live-Risiko angezeigt werden.
- James liefert noch ein sehr generisches Resultat (`Task accepted and completed.`). Pickup ist gruen, aber Receipt-Qualitaet sollte als eigener Sprint gehaertet werden.
- Ein Runtime-Sample war kurz `degraded`, aber ohne `blockedBy` und ohne critical signals. Empfehlung: Warning-only Degraded besser im Soak-Report ausweisen.
- OpenAI/Codex Kostenlogik erzeugt weiterhin Nicht-Minimax-Warnungen zu flatrate/billing mismatch. Das war nicht Teil des Minimax-Fixes.
- Working Tree ist breit dirty/untracked; nicht alle Aenderungen stammen aus diesem Lauf.

## Naechste 5 Stabilitaetshebel

1. James Receipt-Qualitaet erzwingen: generische Abschlussmeldungen als schwaches Resultat markieren und konkrete Output-Felder verlangen.
2. OpenAI/Codex Subscription-Kostenlogik analog Minimax entlaermen: keine `$3 Limit`-Criticals fuer Abo/OAuth-Flatrate-Pfade.
3. Auto-Pickup systemd-service Mode in eine explizite Regression-Suite aufnehmen, inklusive Unit-ID, Stop-Verhalten und Claim-Timeout-Cleanup.
4. Runtime-Soak-Report um Warning-only Degraded Samples erweitern, damit gruen nicht mit stillen Warnungen verwechselt wird.
5. Context/Tool-Output Guard am Ursprung haerten: `sessions_history`/Introspection-Ausgaben hart cappen, damit keine 70KB+ Tool-Outputs erneut Soak-Gates stoeren.
