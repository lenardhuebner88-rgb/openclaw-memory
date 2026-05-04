# Cron Pending Verification Cleanup

Zeitpunkt: 2026-05-04T22:53:10+02:00

## Ziel

Die Launchpad-Meldung `Cron: YELLOW` kam nicht von aktuellen Cron-Fehlern, sondern von 8 alten `pendingVerification`-Einträgen in `/home/piet/.openclaw/cron/jobs-state.json`.

Vorheriger Befund:

- `currentErrors=0`
- `missingAllowlistModels=0`
- `pendingVerification=8`
- Ursache: historische Fehlerzustände vor der letzten `jobs.json`-Korrektur.

## Backups

- `/home/piet/.openclaw/cron/jobs.json.bak-20260504T225202-cron-pending-cleanup`
- `/home/piet/.openclaw/cron/jobs-state.json.bak-20260504T225202-cron-pending-cleanup`

## Einzelentscheidungen

| Job | Entscheidung | Begründung |
| --- | --- | --- |
| `daily-cost-report` | behalten, Text geschärft | Passt weiterhin als Werktags-Kostenbericht. Wording war "wöchentlich" trotz Werktags-Schedule; jetzt read-only, keine Stop-/Patch-Aktion. |
| `morning-brief` | behalten | Sinnvoller Startbericht, Modell ist allowlisted. |
| `nightly-self-improvement` | behalten | Bekannter stabilisierender Nightly-Workflow mit bestehenden Sicherheitsgrenzen: keine Config, keine Gateway-Restarts, keine `openclaw.json`-Edits. |
| `efficiency-auditor-heartbeat` | umgebaut zu `lens-cost-readiness-check` | Alter Job konnte bei Budgetüberschreitung Tasks patchen/stoppen. Das passt nicht mehr zu "Stabilität vor Kosten". Neuer Job ist read-only, isoliert, nutzt Lens/Minimax und liefert nur Risikoempfehlung. |
| `session-cleanup-local` | deaktiviert | LLM-Cron darf keine Session-Stores automatisch mutieren. Ersetzt durch deterministische Guards mit Dry-run, Scoped-Live, Backups und Validierung. |
| `validate-models` | behalten | Direkter Validator; Live-Test meldete `All 51 cross-provider model references valid`. |
| `memory-rem-backfill` | behalten | Separater Safe-Backfill mit `delivery.mode=none`; kein aktueller Modell-/Cron-Fehler. |
| `midday-brief` | behalten | Sinnvoller Tagesstatus, Modell ist allowlisted. |

## Änderungen

Geändert wurde nur:

- `/home/piet/.openclaw/cron/jobs.json`
- `/home/piet/.openclaw/cron/jobs-state.json`

Details:

- `daily-cost-report`: Prompt von wöchentlichem Enforcement-Ton auf Werktags-Kostenbericht/read-only angepasst.
- `efficiency-auditor-heartbeat`: umbenannt zu `lens-cost-readiness-check`, `sessionTarget=isolated`, `model=minimax/MiniMax-M2.7-highspeed`, Prompt read-only, keine PATCH/POST/DELETE-Aktionen.
- `session-cleanup-local`: `enabled=false`, Beschreibung verweist auf deterministische Session-Stability-Guards.
- Für die 8 geprüften Jobs wurden alte `lastRunStatus/error`, `lastStatus/error`, `lastError`, `lastErrorReason`, `lastFailureAlertAtMs` entfernt und `consecutiveErrors=0` gesetzt.

## Validierung

Ausgeführt:

```bash
python3 -m json.tool /home/piet/.openclaw/cron/jobs.json
python3 -m json.tool /home/piet/.openclaw/cron/jobs-state.json
python3 /home/piet/.openclaw/scripts/validate-models.py
python3 -m py_compile /home/piet/.openclaw/scripts/openclaw-morning-launchpad.py
/home/piet/.openclaw/scripts/openclaw-morning-launchpad.py --json
```

Ergebnis:

- JSON valid: ja
- Modellreferenzen valid: `All 51 cross-provider model references valid`
- Launchpad Cron:
  - `enabled=13`
  - `currentErrors=0`
  - `historicalErrors=0`
  - `pendingVerification=0`
  - `missingAllowlistModels=0`
  - Cron Verdict: `GREEN`
- Gateway: `active`

## Nicht angefasst

- Kein OpenClaw-Gateway-Restart.
- Kein Mission-Control-Restart.
- Keine Agent-Sessions rotiert.
- Keine produktiven Mission-Control-Daten geändert.

Hinweis: Mission Control war während der Validierung durch einen parallelen `mc-restart-safe --refresh-build 600 codex-board-quality-final-a11y-wire-check` temporär `inactive`; das wurde nicht von diesem Cleanup ausgelöst.

## Nächster Check

Nach Abschluss des parallelen Mission-Control-Builds:

```bash
curl -fsS http://127.0.0.1:3000/api/health | jq
curl -fsS http://127.0.0.1:3000/api/board-consistency | jq
/home/piet/.openclaw/scripts/openclaw-morning-launchpad.py --send --channel 1495737862522405088
```

