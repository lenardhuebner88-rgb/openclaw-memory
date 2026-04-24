# Heartbeat/Cron/Worker Target Plan - 2026-04-24

## Ziel-Architektur Overview

Die stabile Zielstruktur trennt drei Dinge strikt: read-only Health-Signale, Worker-Execution und operator-gesteuerte Reparatur. Heartbeats duerfen keine aktive Atlas/Discord-Session belegen und duerfen keine Worker-Tasks ausloesen. Auto-Pickup bleibt der einzige Dispatch-Owner, Worker-Monitor bleibt Beobachter/Reconciler ohne Dispatch. Mutierende Reparaturen laufen nur ueber lokale Scripts mit Dry-Run-Default oder explizite Operator-Approval.

Kernentscheidung: `active-session` ist Ausnahme fuer echte Operator-Konversation. `isolated-subprocess` ist Standard fuer Worker-Execution. `out-of-band-http` ist Standard fuer Heartbeats, Health, Budget, Freeze, Size und Proofs.

## Session-Topologie-Matrix

| Job-Klasse | Ziel-Mode | Darf aktive Atlas Session beruehren? | Darf Tasks mutieren? | Lock/Guard | Beispiel |
|---|---|---:|---:|---|---|
| Discord/operator conversation | active-session | ja | nur durch Operator/Task-Kontext | R50 + session lock | `agent:main:discord:*` |
| Main orchestration task | isolated-subprocess | nein | ja, wenn `REAL_TASK=true TASK_ID=...` | Auto-Pickup claim lock + R19 marker | Auto-Pickup `main` |
| Specialist worker task | isolated-subprocess | nein | ja, nur eigene Task receipts | Auto-Pickup lock + workerSessionId | Forge/Pixel/Spark/James |
| MC liveness heartbeat | out-of-band-http | nein | minimal heartbeat write only | `flock`, no session | `/api/heartbeat/main` |
| Freeze/lock/size/health scanners | out-of-band-http/file scan | nein | nein, alert only | `flock`, dedupe state | session-freeze, session-health |
| Reconciler/proof endpoints | out-of-band-http | nein | nein | read-only route | `/api/ops/*proof` |
| Repair actions | local script | nein | yes, scoped | `--dry-run` default + `--execute <id>` | worker-reconciler script |
| Heavy memory synthesis | batch subprocess | nein | writes only target artifacts | flock + log cap | memory-orchestrator |

## Frequency + Modell-Matrix

| Job | Ziel-Frequenz | Ist | Modell-Ziel | Ist-Modell | Kosten-Delta |
|---|---:|---:|---|---|---|
| `/api/heartbeat/main` | `*/5` or hourly 07-23, decision needed | `* * * * *` | none | none | neutral; load down if reduced |
| auto-pickup | 1min | systemd 1min | `openclaw/<agent>` only when real task | `openclaw/<agent>` | keep; cost driven by real tasks |
| worker-monitor | 5min | systemd 5min | none unless explicit notify | none | neutral |
| session-freeze-watcher | 5min | systemd 5min | none | none | neutral |
| stale-lock-cleaner | 5min | systemd 5min | none | none | neutral |
| session-health-monitor | 10min | cron 10min | none | none | neutral |
| session-size-guard | 5min + 1min log-only | cron both | none | none | likely reduce noise if consolidated |
| memory-budget-meter | 5min | cron 5min | none | none | neutral |
| r49/r48 governance | 15min/hourly | cron 15min/hourly | none | none | neutral |
| memory-orchestrator hourly/nightly/weekly | current orchestrator cadence | active | Synth: `sonnet-4.6`; planning only `opus-4.7` | config-owned | review separately; no live price counter in this audit |
| validators/watchers if LLM ever required | lowest viable | n/a | `haiku-4.5` | n/a | should reduce cost vs Opus/Sonnet |

Cost note: Active cron surface sampled here is mostly non-LLM. The meaningful monthly cost delta is therefore not from cron heartbeats, but from real worker task spawns and any future LLM-backed synthesis jobs. A precise Euro estimate needs per-model token counters from OpenClaw usage logs.

## ASCII-Interaktions-Diagramm

```text
Operator / Discord
   |
   v
Atlas active session (agent:main:discord:*)  [R50 session lock]
   |
   | creates/updates task intent
   v
Mission Control /api/tasks
   |
   | pending-pickup only
   v
Auto-Pickup timer (1min, sole dispatch owner)
   |-- checks task state
   |-- checks main/non-main session lock
   |-- injects REAL_TASK=true TASK_ID=<id>
   v
isolated openclaw agent subprocess
   |
   | accepted receipt / workerSessionId / heartbeat
   v
Task state: pending-pickup -> claimed -> in-progress -> done/failed/canceled
   ^
   |
Worker-Monitor (5min observer/reconciler, dispatch disabled)

Out-of-band watchers:
  /api/heartbeat/main -> MC heartbeat only
  session-freeze-watcher -> /api/tasks + session file stat, skips main
  session-health-monitor -> session dirs + pid evidence
  session-size-guard/watchdog -> warn/signal only

Repair:
  local scripts --dry-run default -> --execute <id> only
```

## Migrations-Plan

### Stage 1 - Registry statt Cron-Only-Diff
- Änderung: `defense-jobs.registry.json` im Vault/MC-ops-Bereich erstellen; jede Zeile: name, scheduler, cadence, command, log, mutation class, owner, rollback.
- Risiko: niedrig; read-only Dokumentation.
- Rollback: Datei entfernen oder vorherige Version wiederherstellen.
- Verify: Audit kann Sollliste gegen Registry statt nur `crontab` diffen.
- Go/No-Go: Go, wenn Atlas/Claude keine parallele Registry-Struktur bearbeiten.

### Stage 2 - Auto-Pickup Claim-Handoff Core-Fix Sprint
- Änderung: Kein Live-Hotfix in diesem Audit. Separater Sprint: API-unreachable darf one-shot nicht als fatal crash behandeln; child process lifecycle und claim timeout evidence sauber modellieren; unit tests fuer unclaimed cleanup.
- Risiko: mittel bis hoch, weil Core.
- Rollback: Git revert der Auto-Pickup-Aenderung; systemd timer unveraendert lassen.
- Verify: Real E2E Task fuer `main` und einen Specialist: accepted <= 90s, workerSessionId gesetzt, final result, Worker-Proof 0 critical.
- Go/No-Go: Go nur mit isoliertem Testtask und ohne bestehende Live-Tasks.

### Stage 3 - Heartbeat Policy normalisieren
- Änderung: Entscheiden, ob `/api/heartbeat/main` jede Minute bleiben darf. Falls nein: auf `*/5` oder stündlich 07-23 reduzieren.
- Risiko: niedrig, aber Crontab-Write.
- Rollback-Command: Crontab-Backup aus `/home/piet/.openclaw/backup/...` wieder einspielen.
- Verify: `journalctl _COMM=cron` zeigt neue Cadence; `/api/health` bleibt ok; keine missing-heartbeat false positives.
- Go/No-Go: Go nur nach Operator-Entscheidung zur Frequenz.

### Stage 4 - Forge Heartbeat entmutieren
- Änderung: `forge-heartbeat.sh` in read-only heartbeat und separaten `forge-repair --execute` trennen.
- Risiko: mittel, weil bisher automatische Reparatur wegfaellt.
- Rollback: alte service/script Version aus Backup wiederherstellen.
- Verify: Drei simulierte Health-Fails erzeugen Alert, aber kein `openclaw doctor --fix`.
- Go/No-Go: Go nur, wenn Operator automatische Doctor-Fixes nicht mehr will.

### Stage 5 - Session-Size Guard als Warnsystem festnageln
- Änderung: Rotation watchdog bleibt Signal/Warnung; keine automatische Reroute/aktive Session-Uebernahme.
- Risiko: niedrig.
- Rollback: Watchdog config revert.
- Verify: Log zeigt signal writes/clears, aber keine Task/Session-Mutation.
- Go/No-Go: Go, weil es der Operator-Praeferenz entspricht.

### Stage 6 - E2E Orchestrierter Audit als Gruen-Gate
- Änderung: Atlas bekommt genau einen Audit-Task, der UI-Bugs, Datenstabilitaet und Worker-Proof prueft; keine Task-Flut.
- Risiko: niedrig bis mittel, weil echter Worker-Lauf.
- Rollback: Task canceln, falls pending; keine Core-Aenderung.
- Verify: Result-Receipt, Report im Vault, `/api/health` ok, Worker-Proof 0 critical, keine `dispatched-no-claim` nach Lauf.
- Go/No-Go: Go nach Stage 2 oder als kontrollierter Canary vor Stage 2.

## Kill-Switch

Nur fuer Operator/approved Lauf, nicht in diesem Audit ausgefuehrt:

```bash
# 1. Snapshot
crontab -l -u piet > /home/piet/.openclaw/backup/audit-2026-04-24/crontab.before-kill-switch.bak

# 2. Stop future task pickup by disabling trigger source, not killing live workers
# Prefer approved systemd action only during incident window:
# systemctl --user disable --now m7-auto-pickup.timer

# 3. Keep read-only watchers alive where possible.
# If alert storm: comment only alerting cron lines from backup-restorable crontab.

# 4. Verify
curl -fsS http://127.0.0.1:3000/api/health
curl -fsS 'http://127.0.0.1:3000/api/ops/worker-reconciler-proof?limit=20'

# 5. Rollback
crontab /home/piet/.openclaw/backup/audit-2026-04-24/crontab.before-kill-switch.bak
# systemctl --user enable --now m7-auto-pickup.timer
```

Emergency principle: do not kill active Atlas/worker processes by default. First stop new scheduling, then let current isolated workers finish or fail through receipts.

## Empfohlene Sprint-Zuordnung

| Sprint | Owner | Inhalt | Gate |
|---|---|---|---|
| P4-A | Forge/SRE | Auto-Pickup claim handoff RCA + tests | E2E main + specialist task green |
| P4-B | Atlas-main | Operator heartbeat policy decision + Registry review | Registry accepted, no live drift |
| P4-C | Spark/Efficiency | Session-size and output-noise policy audit | warnings only, no reroute |
| P4-D | Pixel/Frontend | UI button client exception audit | browser console clean on task details |
| P4-E | Atlas-main | Orchestrated MC audit gate | report + health/proof green |

## Recommended Next 3 Actions

1. Do not modify heartbeat session topology now; evidence does not support it as rootcause.
2. Start a dedicated Auto-Pickup Claim-Handoff Sprint with unit tests and one real `main` canary.
3. Decide heartbeat frequency for `/api/heartbeat/main` and document it in the new registry.
