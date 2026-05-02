# Atlas Autonomy Phase 1 — Implementation Plan

Stand: 2026-05-02 23:28 Europe/Berlin
Basis:
- `/home/piet/vault/03-Agents/OpenClaw/plans/atlas-autonomy-policy-matrix-v1-2026-05-02.md`
- `/home/piet/vault/03-Agents/OpenClaw/plans/atlas-autonomy-preflight-gate-spec-v1-2026-05-02.md`

## Bewertung Forge-Ergebnis

Forge-Ergebnis ist verwertbar und vollständig für Phase 1:
- Policy-Klassen sind klar: allow, bounded allow, require-approval, deny.
- Harte Grenzen sind sauber: sudo, secrets/auth mutation, terminal rerun, lock-conflict retry, missing evidence.
- Operator-Präferenz ist eingearbeitet: breite Autonomie ja, aber sudo und große Modelländerungen bleiben gesperrt/approval-pflichtig.
- Major model change ist konkretisiert.
- Preflight Contract hat Input, Output, Reason Codes, Audit-Metadaten.
- 8 E2E-Akzeptanzfälle sind definiert.

Live-Verifikation nach Review:
- Task `d98e66aa-9498-4191-9172-4c9ce2b30ccb`: done/result.
- MC Health: ok.
- Worker proof: ok, issues=0.
- Pickup proof: ok, findings=0.

## Einordnung

Das ist noch keine Runtime-Härtung, sondern eine gute Spezifikation. Nächster Schritt darf deshalb nur evaluator-only sein:
- Keine neue Autonomie aktivieren.
- Keine Mutationspfade blockierend verändern.
- Erst reine Entscheidungsfunktion + Tests.

## Phase 1 Tasks

### P1.1 — Pure Preflight Evaluator
Owner: Forge
Risk: low/medium
Goal: Implementiere eine reine Funktion ohne Side Effects.

DoD:
- Modul nimmt Spec-v1 Input entgegen.
- Gibt `allow | require-approval | deny` + reasonCode zurück.
- Keine Writes, keine Dispatches, keine Config-Mutation.
- Unit Tests für alle Reason Codes.

Implementation Target:
- `/home/piet/.openclaw/workspace/scripts/autonomy-preflight-evaluator.mjs`
- Export: `evaluateAutonomyPreflight(input)` als pure function.
- Keine Imports aus runtime write-paths, keine side effects (nur input -> output).

### P1.2 — Schema + Fixture Tests
Owner: Forge
Risk: low
Goal: Input/Output Schema und 8 Acceptance Fixtures.

DoD:
- JSON/Zod/TS Schema für Input/Output.
- 8 dokumentierte E2E Cases als Tests.
- Invalid input -> `DENY_INVALID_INPUT`.

Implementation Target:
- `/home/piet/.openclaw/workspace/scripts/tests/autonomy-preflight-evaluator.test.mjs`
- Input/Output validation in evaluator module (z. B. `zod` via existing workspace dependency).
- Acceptance fixtures für die 8 Spec-Cases plus mindestens 1 invalid-input case.

### P1.3 — Audit-only Integration
Owner: Forge
Risk: medium
Goal: Gate vor autonome Entscheidungsstellen hängen, aber noch nicht erzwingen.

DoD:
- Preflight läuft vor autonomen Dispatch-/Mutation-Versuchen im dry/audit mode.
- Ergebnis wird geloggt/auditiert.
- Keine Aktion wird wegen Gate blockiert.
- Proof: bestehende Flows laufen unverändert.

### P1.4 — Enforcement für harte Denies
Owner: Forge + Atlas Review
Risk: medium
Goal: Nur sichere Hard Stops erzwingen.

DoD:
- `DENY_SUDO`, `DENY_TERMINAL_RERUN`, `DENY_LOCK_CONFLICT_R50`, `DENY_MISSING_EVIDENCE`, `DENY_SECRET_AUTH_MUTATION` blockieren wirklich.
- Require-approval Fälle werden nicht automatisch ausgeführt.
- MC health/proofs grün nach Integration.

### P1.5 — Operator Review + Threshold Tuning
Owner: Atlas + Operator
Risk: low
Goal: “Major model change” und cron/gateway thresholds anhand echter Beispiele feinjustieren.

DoD:
- 5–10 Beispielaktionen klassifiziert.
- Operator bestätigt oder korrigiert Schwellen.
- Policy v1.1 bei Bedarf geschrieben.

## Empfohlene direkte nächste Aktion

Als nächstes nur P1.1 + P1.2 zusammen an Forge geben:
- evaluator-only
- schema/fixtures
- keine Integration
- keine Runtime-Verhaltensänderung

Danach Review. Erst wenn Tests grün sind, P1.3 audit-only Integration.

## Konkrete Ausführung jetzt (freigegeben)

Scope in dieser Bearbeitung:
- Nur P1.1 und P1.2.
- Keine Änderungen an Dispatch/Mutation/Restart/Gateway/Cron Pfaden.
- Kein Eingriff in bestehende Runtime-Entscheidungsstellen.

Akzeptanz-Gate für diesen Schritt:
1. `node --test /home/piet/.openclaw/workspace/scripts/tests/autonomy-preflight-evaluator.test.mjs` läuft grün.
2. Tests decken alle 8 Acceptance-Cases aus Spec-v1.
3. `requiresSudo`, `isTerminalTaskTarget`, `hasSessionLockConflict`, `touchesSecretsAuth`, fehlende evidence führen deterministisch zu deny reason code.
4. Kein anderer Runtime-Code außerhalb der neuen Evaluator/Test-Dateien wird verändert (außer optionalem Script-Eintrag in root `package.json`).

Out-of-Scope in diesem Schritt:
- P1.3 Audit-only Integration.
- P1.4 Enforcement.
- P1.5 Threshold-Tuning mit Operator.
