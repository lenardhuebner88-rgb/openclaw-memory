---
status: done
owner: codex
created: 2026-04-26
updated: 2026-04-26T19:49Z
scope:
  - auto-pickup first_heartbeat_gate semantics
---

# First-Heartbeat Gate Hardening

## Problem

`first_heartbeat_gate` zaehlte direkt nach einem korrekten `accepted` Receipt noch kurz als `missing`, obwohl `acceptedAt` und ein frisches `lastHeartbeatAt` bereits vorhanden waren.

## Fix

In `/home/piet/.openclaw/scripts/auto-pickup.py` zaehlt jetzt:

- `receiptStage` oder `lastExecutionEvent` in `progress/result/failed/blocked`
- oder `acceptedAt` plus frisches `lastHeartbeatAt`

als `first_heartbeat_gate=ok`.

Das Frischefenster ist ueber `AUTO_PICKUP_FIRST_HEARTBEAT_ACCEPTED_FRESH_SEC` konfigurierbar und steht default auf `120` Sekunden.

## Validierung

- `python3 -m py_compile /home/piet/.openclaw/scripts/auto-pickup.py`
- Direkter Python-Smoke:
  - frisches `acceptedAt + lastHeartbeatAt` -> `('0', 'ok')`
  - alter `acceptedAt + lastHeartbeatAt` -> `('35328', 'missing')`
- `npx vitest run tests/auto-pickup-claimed-no-heartbeat-regression.test.ts --reporter verbose`
  - 1 file passed
  - 3 tests passed
- Live Auto-Pickup Run:
  - `GATE_MATRIX first_heartbeat=pass no_first_heartbeat=0`
- Live Gates:
  - `/api/health`: ok
  - `/api/ops/pickup-proof?limit=20`: ok, `criticalFindings=0`
  - `/api/ops/worker-reconciler-proof?limit=20`: ok, `openRuns=0`, `criticalIssues=0`

## Ergebnis

Der kurzfristige Warn-Noise direkt nach `accepted` ist entfernt, ohne alte/stale Heartbeats faelschlich als gesund zu werten.
