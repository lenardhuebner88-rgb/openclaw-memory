# Atlas Stabilisierung + Autonomie 8-Stufen-Plan

Stand: 2026-04-26T16:14Z  
Operator-Ziel: Atlas stabilisieren, normale Taskboard-Autonomie ausbauen, Zielniveau 9.5/10 ohne Fanout-Risiko.

## Live-Ist

- `mission-control.service`, `qmd-mcp-http.service`, `m7-auto-pickup.timer`, `m7-worker-monitor.timer`, `m7-session-freeze-watcher.timer`: active.
- Worker-Proof: `openRuns=0`, `criticalIssues=0`.
- Pickup-Proof: `pendingPickup=0`, `criticalFindings=0`.
- `/api/health`: `degraded/warning` wegen genau 1 sichtbarem failed Task `d0007dc7-414e-448e-89b6-2ee6ff6638a4`.
- Atlas Session-Size Rootcause: Guard bewertete beendete Discord-Main-Session `46ffe260...` weiter, weil `sessions.json` `status=done`/`endedAt` nicht berücksichtigt wurde.
- Trajectory-Bloat separat: `.trajectory.jsonl` wächst stark durch wiederholte `trace.metadata`-Events; derzeit sidecar, nicht mehr Rotationstreiber.

## Stufe 1 — Guard-Korrektur fuer Atlas Session-Bloat

Ziel: Keine HARD-Alerts für bereits beendete Atlas-Discord-Sessions.

Umsetzung:
- `session-size-guard.py` ignoriert gebundene Sessions mit `status in {done, failed, canceled}` oder `endedAt`.

Gate:
- `python3 -m py_compile /home/piet/.openclaw/scripts/session-size-guard.py`
- `session-size-guard.py --log-only` sendet `0`.
- Scan zeigt `46ffe260...` nicht mehr als aktiven Alert-Kandidaten.

Status: done.

## Stufe 2 — System-Basis belegen

Ziel: Vor Autonomie keine versteckten Worker-/Pickup-Probleme.

Gate:
- Worker-Proof `criticalIssues=0`.
- Pickup-Proof `criticalFindings=0`.
- Reconciler/Followup-Guard Dry-Runs `proposedActions=0`.

Status: in progress.

## Stufe 3 — Genau eine Autonomie-Preview freigeben

Ziel: Atlas darf einen kleinen, sicheren Follow-up autonom ausführen.

Kandidat:
- `f05dbb39-f6f6-42ca-b18e-de4267f2e994`
- `approvalClass=safe-read-only`
- `riskLevel=low`
- `operatorLock=true`, `lockReason=atlas-autonomy-awaiting-approval`

Gate:
- Approve/Dispatch nur ueber `/api/tasks/:id/autonomy-approve`.
- Kein zweiter Preview parallel.
- Danach Worker-Proof/Pickup-Proof gruen.

Status: pending.

## Stufe 4 — Failed Parent bewusst entscheiden

Ziel: `/api/health` von warning nach ok bringen, ohne Historie zu verstecken.

Kandidat:
- `d0007dc7-414e-448e-89b6-2ee6ff6638a4`

Regel:
- Nicht heimlich admin-close.
- Erst wenn Follow-up/Proof belegt, dass die Ursache nachhaltig behandelt wurde.

Gate:
- Parent bekommt klares Resolution-Artefakt oder bleibt sichtbar als Operator-Decision.

Status: pending.

## Stufe 5 — First-Heartbeat/Claim-Telemetrie haerten

Ziel: Atlas-Pickup nicht erst nach Timeout verstehen.

Soll:
- Board/Proof unterscheidet `waiting-first-heartbeat` von generischem `pending-pickup`.
- Claim ohne ersten Heartbeat bekommt klares Requeue-/Fail-Outcome.
- Kein mehrfacher Alert fuer denselben Task-Key.

Gate:
- Regressionstest fuer claim -> no first heartbeat -> controlled requeue/fail.
- Live-Dry-Run ohne Proposed Actions.

Status: planned.

## Stufe 6 — Autonomie-Policy schärfen

Ziel: Atlas darf sauber Vorschläge erzeugen, aber nicht riskant mutieren.

Policy:
- `safe-read-only`: auto-dispatch nach Proof-Gate moeglich.
- `gated-mutation`: Operator-Freigabe.
- `model-switch-required`: Operator-Freigabe.
- `sudo-required`: Operator-Freigabe.

Gate:
- API-Test: falsche Freigabe-Klasse wird abgelehnt.
- Dashboard/Status zeigt Approval-Klasse sichtbar.

Status: planned.

## Stufe 7 — Reporting vereinheitlichen

Ziel: Jede autonome Arbeit erzeugt denselben Abschlussbeweis.

Minimalformat:
- `EXECUTION_STATUS`
- `RESULT_SUMMARY`
- `GATES`
- `FOLLOW_UPS`
- `OPERATOR_DECISIONS`

Gate:
- Atlas-Result eines Sprints enthaelt alle Felder.
- Follow-up-Drafts tragen `approvalClass` und `riskLevel`.

Status: planned.

## Stufe 8 — Großer Atlas-Sprint als Abschlussgate

Ziel: Ein autonom orchestrierter Sprint bringt das normale Taskboard naeher an 9.5/10.

Sprint-Thema:
> Worker/Heartbeat/Cron Zielbild: Welche Crons bleiben, welche Heartbeats sind aktiv, welche Gates fehlen, wie werden Reports/Folgeaufgaben vereinheitlicht, wer hat welche Rolle?

Regel:
- Atlas orchestriert.
- Codex begleitet, greift nur bei Proof-Fehlern oder kleinen reversiblen Fixes ein.
- Kein Fanout ohne saubere Zwischen-Gates.

Gate:
- 1 großer Atlas-Sprint terminal `done`.
- Mindestens 2 Follow-up-Drafts mit Approval-Klassen.
- Worker-Proof/Pickup-Proof gruen.
- `/api/health` ok oder genau begründete Operator-Decision.

Status: planned.
