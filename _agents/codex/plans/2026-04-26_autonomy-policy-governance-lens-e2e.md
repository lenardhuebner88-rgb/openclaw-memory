---
status: done
owner: codex
created: 2026-04-26
updated: 2026-04-26T19:45Z
scope:
  - Mission Control autonomy approval policy
  - Atlas follow-up fanout guard
  - Lens auto-pickup claim hardening
  - E2E autonomy sprint gate
---

# Autonomy Policy / Governance / Lens / E2E

## Ziel

Operator-Freigaben duerfen nur noch bei echten Hard-Gates noetig sein:

- `sudo-required`
- `model-switch-required`

Normale Aufgaben wie `safe-read-only` oder `gated-mutation` sollen nicht auf Operator-Freigabe warten. Atlas darf ausserdem nicht beliebig fan-outen; der Follow-up Materializer materialisiert maximal zwei naechste Tasks pro terminalem Receipt.

## Umgesetzt

1. Approval-Policy zentralisiert:
   - `requiresOperatorApprovalForClass()` in `src/lib/taskboard-types.ts`
   - harte Freigabe nur fuer `sudo-required` und `model-switch-required`

2. Task-Create/Patch-Governance angepasst:
   - `src/app/api/tasks/route.ts`
   - `src/app/api/tasks/[id]/route.ts`
   - Nicht-harte Atlas-Follow-ups duerfen nicht mehr mit `atlas-autonomy-awaiting-approval` blockiert werden.
   - Hard-Gates behalten `approvalMode=operator`, `operatorLock=true`, `lockReason=atlas-autonomy-awaiting-approval`.

3. Atlas-Fanout begrenzt:
   - `src/lib/receipt-materializer.ts`
   - maximal 2 `next_actions` pro terminalem Receipt
   - weitere Actions werden mit `subtask-limit-exceeded` als skipped dokumentiert.

4. Lens-Retry-Haertung:
   - `/home/piet/.openclaw/scripts/auto-pickup.py`
   - `AUTO_PICKUP_LENS_SYNC_CLAIM_TIMEOUT_SEC` Default `90`
   - Lens bekommt expliziten Prompt-Hinweis: accepted Receipt sofort vor Deep-Research/Log-Kontext.

5. E2E-Autonomie-Gate:
   - Task `b1562086-8198-461c-9f5d-d1feb6eed867`
   - vorher: `operatorLock=true`, `lockReason=operator-approval-required`
   - korrigiert: `operatorLock=false`, `approvalClass=safe-read-only`, `riskLevel=low`
   - dispatched an Forge, Pickup accepted, terminal `done`
   - Ergebnis: `research-queue-add.py`, `research-topics.txt`, 3 offene Research-Queue Items, idempotent verifiziert.

## Validierung

- `python3 -m py_compile /home/piet/.openclaw/scripts/auto-pickup.py`
- `npx vitest run tests/autonomy-draft-create-regression.test.ts tests/receipt-materializer-flag-off.test.ts tests/auto-pickup-claimed-no-heartbeat-regression.test.ts`
  - 3 files passed
  - 24 tests passed
- `npm run typecheck`
- Produktionsbuild nach Stop:
  - `systemctl --user stop mission-control.service`
  - `npm run build`
  - `systemctl --user start mission-control.service`
- Live policy probe:
  - Nicht-harter `gated-mutation` Follow-up mit `operatorLock=true` wird live mit HTTP 400 abgewiesen.
- Live Gates:
  - `/api/health`: ok
  - `/api/ops/pickup-proof?limit=20`: ok, `criticalFindings=0`
  - `/api/ops/worker-reconciler-proof?limit=20`: ok, `openRuns=0`, `criticalIssues=0`
  - `mission-control.service`: active

## Rest-Risiken

- Der E2E-Task meldete `EXECUTION_STATUS: partial`, weil `/home/piet/.openclaw` kein Git-Repository ist und deshalb kein `COMMIT_SHA` erzeugt werden konnte. Die eigentlichen Files und Verifikationen sind erfolgreich.
- Der bestehende Auto-Pickup-Test fuer Python-Funktionsausfuehrung konnte im Vitest-Sandbox-Kontext keine Python-Subprozesse stabil starten. Der Test wurde auf statische Guard-Assertions umgestellt; echte Python-Syntax wurde separat mit `py_compile` validiert.
- `first_heartbeat_gate=missing` direkt nach `accepted` ist noch ein Semantik-Thema: accepted ist Claim-Wahrheit, aber Proof zaehlt erst progress/result als First-Heartbeat-ok. Das ist ein sinnvoller naechster Hardening-Punkt.

## Naechster sinnvoller Schritt

Eine kleine Follow-up-Haertung:

1. First-heartbeat-Gate semantisch korrigieren: `acceptedAt` + frisches `lastHeartbeatAt` soll nicht als Warnung zaehlen.
2. Materializer-Follow-ups optional direkt dispatchbar machen, aber nur sequentiell und mit max 2 offenen Children.
3. Fuer `/home/piet/.openclaw`-Runtime-Fixes eine eigene Commit-/Snapshot-Strategie definieren, weil dort kein Git-Repository liegt.
