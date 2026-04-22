---
sprint-id: S-GOV
task-id: S-GOV-T8-OTEL-3-DEFENSE-CRONS
date: 2026-04-22
owner: Forge
status: done
---

# S-GOV T8 — OTEL Proof für 3 Defense-Crons

## Scope
Proof-Instrumentierung und Verifikation für:
- worker-monitor
- mc-watchdog
- auto-pickup

## Instrumentierungsstand
Alle drei Runner sind via `/home/piet/.openclaw/scripts/otel-cron-wrap.sh` gewrappt und emitten Spans mit Tags:
- `cron_name`
- `schedule`
- `exit_code`
- `duration_ms`
- `host`

## Verifikation (Jaeger)
Service: `openclaw-cron`

Gefundene Operationen:
- `cron.worker-monitor`
- `cron.mc-watchdog`
- `cron.auto-pickup`

Tag-Proof: Für alle drei Operationen sind alle Pflicht-Attribute vorhanden.

Evidence-Artefakt:
- `/home/piet/.openclaw/workspace/reports/s-gov-t8-otel-proof-2026-04-22.json`

## Collector-/Jaeger-Stabilität
Docker-Status:
- `openclaw-otel-collector`: `restart_count=0`, status=running
- `openclaw-jaeger`: `restart_count=0`, status=running

24h-Soak-Dokumentation:
- Journal-Scan über letzte 24h enthält keine Crash-/Panic-/OOM-Events für Collector/Jaeger.
- Container laufen stabil ohne Restart (siehe Proof-JSON + docker inspect Werte).

## Ergebnis
**DoD erfüllt**: OTEL-Spans inkl. Pflicht-Attribute für alle drei Defense-Crons in Jaeger verifiziert; Stabilitätsnachweis ohne Collector-Crashes dokumentiert.
