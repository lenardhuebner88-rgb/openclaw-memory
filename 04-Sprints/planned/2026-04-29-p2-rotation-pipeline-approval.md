---
status: planned
owner: forge
created: 2026-04-29
priority: P2
---

# rotation-pipeline-approval

## Problem
Watchdog-Signale wurden bisher wiederholt geschrieben, waehrend `auto-pickup` dry-run/duplicate Pfade nahm. Am 2026-04-29 wurde zusaetzlich sichtbar, dass das deduplizierte Alert-File bei spaeterem OK stale bleiben kann.

## Spec
Pipeline sauber definieren: Watchdog schreibt Signal, Live-Consumer verarbeitet outcome-keyed, Action-Log enthaelt `mode=live` plus `rotation_ok`, Watchdog/Alert-State wird bei OK oder Sessionwechsel explizit bereinigt. Approval bleibt ueber Environment-Gate steuerbar.

## Akzeptanz
Naechster `pct >= 95` Trigger erzeugt innerhalb von 5 Minuten einen `mode=live` Action-Log-Eintrag mit `status=consumed` oder `status=failed` und klarer `rotation_detail`. Bei spaeterem `pct < 60` existiert kein stale Alert mehr.

## Risiko / Rollback
Risiko: fehlerhafte Live-Rotation kann aktive Arbeit stoeren. Rollback: `AUTO_PICKUP_ROTATION_CONSUMER_MODE=dry-run` setzen und Drop-in entfernen.
