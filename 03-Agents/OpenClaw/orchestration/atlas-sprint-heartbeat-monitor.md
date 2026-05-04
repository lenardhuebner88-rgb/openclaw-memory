# Atlas Sprint Heartbeat Monitor

Purpose: make `Autonomie: full` safer by giving Atlas a compact read-only monitor for sprint task progress, heartbeats, worker runs, receipts, and stop conditions.

## Script
`/home/piet/.openclaw/workspace/scripts/atlas-sprint-monitor.py`

## Usage
```bash
# Default: active non-terminal tasks
/home/piet/.openclaw/workspace/scripts/atlas-sprint-monitor.py

# Sprint/topic scan
/home/piet/.openclaw/workspace/scripts/atlas-sprint-monitor.py --sprint "UI Verbesserungen Mission Control Board"

# Specific master/child task ids
/home/piet/.openclaw/workspace/scripts/atlas-sprint-monitor.py --task-id "<id1>,<id2>"

# Machine-readable gate
/home/piet/.openclaw/workspace/scripts/atlas-sprint-monitor.py --sprint "..." --json
```

## What It Checks
- Task status vs dispatchState
- last activity age
- last heartbeat age
- worker-run count and active worker-runs
- terminal tasks with missing receipt
- terminal tasks with still-active worker-runs
- done tasks with failed last report mismatch
- dispatched tasks without worker-run evidence

## Exit Codes
- `0`: no monitor issues found
- `2`: monitor found issues
- non-zero stderr read failures indicate data access problems

## Current Scope
Read-only local data monitor using:
- `/home/piet/.openclaw/state/mission-control/data/tasks.json`
- `/home/piet/.openclaw/state/mission-control/data/worker-runs.json`

No API writes, no dispatch, no restarts.

## Remaining Gap For True Full Autonomy
This is the first durable monitor slice. True full autonomy still needs integration into the sprint runner/taskboard flow:
- create master + children
- store tracked task ids
- periodically run monitor
- escalate on exit 2
- prevent final done claims until monitor + build/live gates pass

## Laien-Erklärung
Ein Sprint Heartbeat/Monitor ist wie ein Bauleiter-Checkzettel mit Pulsmesser für einen Sprint.

- Ein Sprint besteht aus mehreren Aufgaben, oft parallel bei verschiedenen Agenten.
- Ein Heartbeat ist ein regelmäßiges Lebenszeichen eines Agenten: gestartet, Fortschritt, blockiert oder fertig.
- Der Monitor ist das Kontrollprogramm, das prüft, ob diese Lebenszeichen und Abschlussnachweise zusammenpassen.

Er beantwortet für Atlas:
- Wer arbeitet gerade woran?
- Hat ein Agent lange nichts gemeldet?
- Ist eine Aufgabe angeblich fertig, aber ohne Abschlussbericht/Receipt?
- Läuft noch ein Worker auf einer Aufgabe, die schon terminal ist?
- Gibt es Widersprüche zwischen Taskstatus, Dispatchstatus und Worker-Runs?

Warum das wichtig ist:
Ohne Monitor müsste Atlas manuell hinterherprüfen, ob Pixel/Forge/Lens/Spark/James wirklich fertig sind. Mit Monitor gibt es eine kompakte Ampel:
- OK: keine offensichtlichen Sprint-Probleme
- WARN: fehlendes Lebenszeichen, fehlendes Receipt oder Status-Widerspruch
- BLOCKER/Stop: Atlas darf nicht „done“ behaupten, bis der Punkt geklärt ist

Kurzform: Der Sprint Heartbeat/Monitor verhindert, dass `Autonomie: full` blind arbeitet. Er zwingt Atlas, vor einem Done-Claim echte Lebenszeichen und Abschlussnachweise zu prüfen.
