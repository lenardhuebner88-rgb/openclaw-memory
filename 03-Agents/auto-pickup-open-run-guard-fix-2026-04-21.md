# Auto-Pickup Open-Run Guard Fix

## Problem

`/home/piet/.openclaw/scripts/auto-pickup.py` hat stale Task-Locks nach `STALE_LOCK_SEC=600`
entfernt und denselben `pending-pickup`-Task erneut getriggert, obwohl in
`worker-runs.json` bereits ein offener Run fuer denselben `taskId` existierte.

Dadurch entstand eine Retrigger-Schleife:

- Dispatch erzeugt Run-Placeholder in `worker-runs.json`
- kein frueher `accepted`-Receipt
- lokaler Task-Lock wird stale
- auto-pickup retriggert denselben Task erneut

## Fix

Der Auto-Pickup-Pfad nutzt jetzt `worker-runs.json` als zusaetzliche Wahrheit fuer
bereits laufende Pickup-Versuche:

- stale Lock-Cleanup loescht einen Task-Lock nicht mehr, wenn fuer denselben Task
  bereits ein offener Run existiert
- der Hauptloop retriggert einen `pending-pickup`-Task nicht mehr, wenn ein offener
  Run fuer diesen Task gefunden wurde, auch wenn lokal kein Lock mehr existiert
- der Cycle-Log zeigt den neuen Zaehlwert `open_run=<n>`

## Kleinster Eingriff

- keine API-Aenderung
- keine Receipt-Route-Aenderung
- keine systemd-/M7-Aenderung
- nur Guard im Retrigger-Pfad von `auto-pickup.py`

## Validierung

- `python3 -m unittest discover -s /home/piet/.openclaw/scripts/tests -p 'test_auto_pickup.py'`
- `python3 -m py_compile /home/piet/.openclaw/scripts/auto-pickup.py`

## Rest-Risiko

Ein wirklich haengender offener Run wird damit nicht automatisch gerettet; dieser Fall
bleibt weiter Aufgabe von `worker-monitor` bzw. expliziter Recovery. Der Fix stoppt
gezielt die Mehrfach-Trigger-Schleife im Auto-Pickup selbst.
