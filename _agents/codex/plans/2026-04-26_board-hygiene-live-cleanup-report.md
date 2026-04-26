# Board-Hygiene Live Cleanup Report

Stand: 2026-04-26T19:56Z

## Ergebnis

Mission Control ist operativ sauber:

- `/api/health`: `status=ok`, `board.openCount=0`, `metrics.openTasks=0`, `pendingPickup=0`, `failed=0`, `staleOpenTasks=0`.
- `/api/ops/pickup-proof?limit=20`: `status=ok`, `criticalFindings=0`, `pendingPickup=0`, `proposedActions=0`.
- `/api/ops/worker-reconciler-proof?limit=20`: `status=ok`, `openRuns=0`, `criticalIssues=0`, `issues=0`.

## Geschlossen

### Test-Leaks aus Regression-Fixture

Diese drei Tasks waren keine echte Operator-Arbeit. Beleg: `followUpParentTaskId=task-parent-1` und passende `decisionKey`/Titel aus `mission-control/tests/receipt-materializer-flag-off.test.ts`.

- `26981764-259c-4816-810b-dc8691eb9432` - `Sudo follow-up`
  - Status: `canceled`
  - Pfad: `autonomy-reject`, weil der Task als awaiting autonomy approval gesperrt war.
- `a8dad2ef-e21f-4c76-8775-909622466c70` - `Follow-up 2`
  - Status: `canceled`
  - Grund: Fixture-Leak `limit-action-2`.
- `dd9843f2-2511-4b4a-8207-3ef75d751919` - `Follow-up 1`
  - Status: `canceled`
  - Grund: Fixture-Leak `limit-action-1`.

### Erledigt oder ersetzt

- `0d6737ec-2cda-4e9c-996d-fe9495222c0d` - Heartbeat-Timeline / Coverage Matrix
  - Status: `canceled`
  - Grund: Ergebnis war bereits geliefert und in `5c649b87...` zusammengeführt; Task war versehentlich wieder `assigned`.
- `5c649b87-cc2e-45fe-a2e4-e5577c5be72a` - Heartbeat Coverage Policy
  - Status: `canceled`
  - Grund: veralteter Operator-Decision-Draft; Coverage-Befund bleibt dokumentiert, aber kein wartender Board-Draft nötig.
- `a0d6e563-3e9b-4504-a27f-58d74a5100c3` - claimed-no-heartbeat Preview
  - Status: `canceled`
  - Grund: durch First-Heartbeat-Gate-Härtung und Regressionstest ersetzt.

## Behalten

Diese Drafts sind noch echte Backlog-Arbeit, aber nicht aktiv. Falsche Operator-Locks wurden entfernt, außer beim Modellrouting-Draft.

- `7e0396e3-9efb-4d34-90b9-e0e791c4149f`
  - Thema: Taskboard MCP Not-Connected + Atlas Model Routing.
  - Status: `draft`, `operatorLock=true`.
  - Hygiene-Fix: `approvalClass=model-switch-required`, `riskLevel=high`.
  - Grund: kann GPT-5.5/Modellrouting berühren; Operator-Freigabe bleibt hier korrekt.
- `29307251-d2bc-4b1b-ac78-f046b8442329`
  - Thema: m7-Kernel-Timer vs Legacy-Crons.
  - Status: `draft`, `operatorLock=false`.
  - Grund: echter Cron/Timer-Backlog, aber kein Sudo/Modellwechsel.
- `5455079a-cca8-4afa-baa8-d5f96e3f3fa1`
  - Thema: Atlas Reportingformat / Sprint-8 Prompt.
  - Status: `draft`, `operatorLock=false`.
  - Grund: echter Reporting-Backlog, aber kein Sudo/Modellwechsel.
- `081b099d-9227-4544-b9a7-e6a198a7bbe0`
  - Thema: Receipt-Claim operatorLock Drift.
  - Status: `draft`, `operatorLock=false`.
  - Grund: echter Receipt-/Claim-Backlog, aber kein Sudo/Modellwechsel.

## Rest-Risiko

- Die Regression-Tests haben zuvor echte Board-Daten verschmutzt. Die identifizierten Leaks sind geschlossen; künftig sollten materializer tests weiter strikt mit isolierten Testdaten laufen.
- `7e0396e3...` bleibt absichtlich gesperrt, weil dort Modellrouting/GPT-5.5 betroffen sein kann.
- Die drei nicht-gesperrten Drafts sind Backlog, keine aktiven Worker-Runs.

## Nächster sauberer Schritt

Keine neue Parallelkette starten. Wenn weitergearbeitet wird, dann genau ein Sprint:

1. zuerst `081b099d...` Receipt-/Claim-Governance prüfen/fixen,
2. danach `29307251...` Cron/Timer-Konsolidierung,
3. anschließend `5455079a...` Reportingformat finalisieren.

Modellrouting `7e0396e3...` separat behandeln, weil es die von dir definierte Freigabe-Klasse Modellwechsel berührt.
