# 2026-05-02 Cron Audit + Migrationsplan — PARTIAL

Status: PARTIAL  
Zeit: 2026-05-02 00:31 CEST  
Operator-Scope: Atlas flüssig bekommen, ohne Architektur-Bruch.

## Kurzfassung

Der Cron-/Routing-Audit-Schritt wurde read-only abgeschlossen und als Migrationsplan dokumentiert. Es wurden keine Cron-, Config-, Service- oder Source-Mutationen vorgenommen, weil der Sprint-Preflight weiter RED ist. Der nächste A-E-Sprint übernimmt die offenen Blocker gezielt: Phase A/B klären Wartungs-/CPU-/Lock-Ursachen, danach ist der Cron-Migrationsplan entweder direkt anwendbar oder als P0-Folge-Task sauber vorbereitet.

## Erreicht

- Sprint-Lock übernommen, nachdem der alte Lock-Owner nicht mehr lief.
- Live-Health geprüft:
  - Gateway: `{"ok":true,"status":"live"}`
  - Mission Control: `status=ok`, `severity=ok`
  - `pendingPickup=0`, `inProgress=0`
- Kein paralleler Build gefunden.
- Aktuelle Scheduling-Sources inventarisiert:
  - 24 OpenClaw-Jobs in `/home/piet/.openclaw/cron/jobs.json`
  - 50 aktive User-crontab-Einträge
  - 22 systemd-user-Timer
- Relevante Alert-/Cron-Skripte geprüft:
  - `cost-alert-dispatcher.py`
  - `mc-critical-alert.py`
  - `alert-dispatcher.sh`
  - `gateway-memory-monitor.py`
  - `billing-alert-watch.sh`
  - `session-size-guard.py`
  - `daily-ops-digest.py`
  - `openclaw-config-guard.sh`
- Routing-Gefahr bestätigt:
  - `/home/piet/.openclaw/workspace/discord-routing.json` hat weiterhin fallback auf `main`.
  - Channel `1491148986109661334` ist dort nicht explizit gemappt.
  - Channel `1491148986109661334` ist auch in `openclaw.json` nicht als Discord-Channel eingetragen.
- Live-Korrektur zur Vorannahme:
  - `session.maintenance` ist aktuell nicht auf `14d/150` zurückgefallen.
  - Live-Werte: `pruneAfter=2d`, `maxEntries=60`.
- Kein `system-bot` existiert aktuell in `openclaw.json`.

## Exakter Preflight-Blocker

Command:

```bash
/home/piet/.openclaw/scripts/pre-flight-sprint-dispatch.sh /home/piet/vault/04-Sprints/2026-05-02-atlas-fluid-sprint-plan.md --verbose
```

Resultat:

- PASS: Atlas-session-size OK, 64% von 150000 Token-Budget.
- PASS: Plan-Doc operatorLock clear.
- FAIL: Board `open_count=8` zu hoch.
- PASS: Mission Control und Gateway HTTP 200.
- PASS: R49 Validator: 0 CRITICAL in den letzten 60min.
- FAIL: Mission Control Git-Worktree hat 40 real-dirty Dateien.
- PASS: Freeze-Watcher: 0 FREEZE-WARN in den letzten 30min.

Entscheidung: Keine Cron-/Config-Mutation unter RED-Preflight. Frequenzänderungen und Routingmigration warten auf einen grünen oder explizit begründet übersteuerten Gate-Zustand.

## Live-Befunde

- Gateway läuft stabil, aber CPU bleibt hoch: ca. 86% trotz `active=0`.
- Mission Control meldet gesundes Board, aber Preflight zählt mehr offene Board-Arbeit als zulässig.
- OpenClaw-/Discord-Routing ist nicht einheitlich:
  - `workspace/discord-routing.json` enthält operative Channel-Bindings für Atlas/Forge/Pixel.
  - `openclaw.json` enthält Discord-Channel-Einträge mit `agent=null`.
  - Alerts-Channel `1491148986109661334` ist nicht explizit geschützt.
- In den Gateway-Logs bleiben Hinweise auf den eigentlichen aktuellen P0:
  - `pi-trajectory-flush timeoutMs=10000`
  - `SessionWriteLockTimeoutError`
  - langsame Bootstrap-Prep-Zeiten
  - hohe Eventloop-/CPU-Last

## Migrationsplan-Tabelle

### OpenClaw-Jobs

| job | enabled | old owner | proposed owner | tier | risk | Entscheidung |
|---|---:|---|---|---|---|---|
| daily-cost-report | yes | main | system-bot | T8 daily | medium | SYSTEM-BOT-CANDIDATE. Systemkostenreport, kein User-Turn. |
| morning-brief | yes | main | main | T8 daily | medium | Atlas-owned lassen; Operator-Narrativ. |
| nightly-self-improvement | yes | main | main/system-bot nach Review | T8 daily | high | Defer; kann Arbeit erzeugen und braucht Governance. |
| efficiency-auditor-heartbeat | yes | efficiency-auditor | efficiency-auditor | T8 daily | low | Agent-owned lassen. |
| session-cleanup-local | yes | sre-expert | sre-expert | T6 8h | low | Bereits weg von main; lassen. |
| evening-debrief | yes | main | main | T8 daily | medium | Atlas-owned lassen; Operator-Zusammenfassung. |
| Security-Weekly-Audit | yes | sre-expert | sre-expert | T8 weekly | low | Agent-owned lassen. |
| validate-models | yes | main | system-bot oder sre-expert | T8 daily | medium | SYSTEM-BOT-CANDIDATE. Systemvalidierung soll Atlas nicht bootstrappen. |
| learnings-to-tasks | yes | main | main vorerst | T8 daily | medium | Defer; erzeugt Drafts und braucht Operator-Semantik. |
| memory-rem-backfill | yes | main | unverändert bis Memory-Review | T8 daily | high | Memory-L1-L6-Pfad; nicht blind migrieren. |
| memory-sqlite-vacuum-weekly | yes | worker | worker | T8 weekly | low | Wartung, kein Discord-Routing. |
| mc-pending-pickup-smoke-hourly | yes | sre-expert | sre-expert | T7 hourly | low | Defense/Worker-Smoke; lassen. |
| mcp-zombie-killer-hourly | yes | sre-expert | sre-expert | T7 hourly | low | Defense; lassen. |
| midday-brief | yes | main | main | T8 daily | medium | Atlas-owned lassen; Operator-Zusammenfassung. |
| daily-ops-digest | yes | main | system-bot oder direkter Script-Pfad | T8 daily | medium | SYSTEM-BOT-CANDIDATE falls nicht interaktiv. |
| disabled jobs | no | mixed | no change | n/a | low | Nicht anfassen. |

### User-crontab

| cron | old freq -> proposed freq | owner old -> new | tier | risk | Entscheidung |
|---|---|---|---|---|---|
| mc-heartbeat-main | `* * * * *` -> `*/2 * * * *` | MC API -> MC API | T2 -> T3 | low | Reduzierbar; mehrere Health-Pfade existieren. |
| openclaw-config-guard | keep | config guard -> config guard | T2 | high | Defense/Schema-Gate; nicht anfassen. |
| cost-alert-dispatcher | `*/2 * * * *` -> `*/5 * * * *` | webhook-only -> webhook-only | T3 -> T4 | medium | Reduzierbar; nutzt Webhook-Pfad. |
| mc-critical-alert | `1-59/2 * * * *` -> `*/5 * * * *` | alert-dispatcher -> alert-dispatcher | T3 -> T4 | medium | Reduzierbar nach Smoke-Test. |
| memory-budget-meter | keep | file/log -> file/log | T4 | medium | Session-Rotation-Signal; behalten. |
| sprint-debrief-watch | keep | script -> Discord summary | T4 | medium | Operator-Loop; später mit result-watcher konsolidieren. |
| atlas-orphan-detect | keep | defense -> defense | T5 | high | Explizit geschützt. |
| session-health-monitor | keep | defense -> defense | T5 | high | Defense; behalten. |
| self-optimizer | keep | dry-run -> dry-run | T6 | medium | Schon niedrige Frequenz. |
| r49-claim-validator | keep | defense -> defense | T6 | high | R49 geschützt. |
| r48-board-hygiene-cron | keep | defense -> defense | T7 | high | R48 geschützt. |
| memory-orchestrator | keep | memory -> memory | T7/T8 | high | Memory-L1-L6 geschützt. |
| openclaw sessions cleanup | keep until Phase A | maintenance -> maintenance | T6 | medium | A-E Phase A/C prüft Drift und Lock-Konflikte. |
| qmd-pending-monitor | keep | alert-dispatcher -> alert-dispatcher | T7 | medium | Alert-only; keine Agent-Bootstrap-Belege. |
| pr68846-patch-check | keep | webhook-only -> webhook-only | T6 | low | Webhook-only. |
| minions-pr-watch | keep | webhook-only -> webhook-only | T7 | low | Webhook-only. |
| canary-alert | keep | alert-dispatcher -> alert-dispatcher | T6 | low | Webhook/MC-Alert-only. |
| cpu-runaway-guard | keep | defense -> defense | T4 | high | Geschützter Defense-Cron. |
| session-size-guard | keep | defense -> defense | T4 | high | Geschützter Defense-Cron. |
| session-size-guard-immediate | `* * * * *` -> `*/5 * * * *` | log-only -> log-only | T2 -> T4 | low | Reduzierbar; 5-min Guard existiert bereits. |
| mcp-qmd-reaper | keep | defense -> defense | T4 | high | Geschützter Reaper. |
| mcp-taskboard-reaper | keep | defense -> defense | T4 | high | Geschützter Reaper. |
| session-rotation-watchdog | `*/2 * * * *` -> erst nach Lock-RCA prüfen | session defense -> session defense | T3 -> T4 | high | Nicht vor Phase C ändern. |
| state-collector | `* * * * *` -> `*/2 * * * *` | state -> state | T2 -> T3 | low | Reduzierbar; file-only collector. |
| gateway-memory-monitor | keep | webhook-only -> webhook-only | T4 | medium | Für Phase B wichtig. |
| billing-alert-watch | keep | alert-dispatcher -> alert-dispatcher | T6 | low | Alert-only. |
| crontab-schema-gate | keep | schema gate -> schema gate | T2 | high | Prompt schlug Reduktion vor, aber Sprint-Regeln schützen Self-Validation. |
| cron-runs-tracker | keep | tracker/alert -> tracker/alert | T6 | medium | Für diesen Sprint nützlich. |

### systemd-user-Timer

| timer | cadence | Entscheidung |
|---|---:|---|
| m7-auto-pickup.timer | ~1 min | Keep. Auto-pickup geschützt. |
| m7-plan-runner.timer | ~1 min | Keep bis dedizierter Plan-runner-Audit. |
| openclaw-systemjob-atlas-receipt-stream-subscribe.timer | 5 min | Keep, aber in Phase B/C profilieren; Logs zeigen Cleanup-Timeouts. |
| openclaw-systemjob-m7-atlas-master-heartbeat.timer | 5 min | Keep, aber in Phase B/C profilieren; Logs zeigen Cleanup-Timeouts. |
| anomaly-watch/result-watcher | 5 min | Keep. Operator-Awareness. |
| session-freeze/stale-lock/worker-monitor | 5 min | Keep. Defense/Worker. |
| openclaw-systemjob-mc-task-parity-check.timer | 10 min | Keep. Defense-Parity. |
| canary-session-rotation-watchdog/canary-session-size-guard | 10 min | Keep. Canary-Pfad. |
| forge-heartbeat.timer | hourly | Forge-owned lassen. |
| daily/session health/logrotate/researcher timers | daily+ | Keep. |

## Was wartet auf grün?

Folgende Änderungen sind vorbereitet, aber nicht angewendet:

1. Low-risk Frequenzreduktionen:
   - `mc-heartbeat-main`: 1min -> 2min.
   - `state-collector`: 1min -> 2min.
   - `session-size-guard-immediate`: 1min -> 5min.
   - `cost-alert-dispatcher`: 2min -> 5min.
   - `mc-critical-alert`: 2min -> 5min nach Smoke.
2. Expliziter Schutz für Channel `1491148986109661334`.
3. Spätere system-bot-Migration für echte System-Reports:
   - `daily-cost-report`
   - `validate-models`
   - ggf. `daily-ops-digest`

## Wie A-E diesen PARTIAL-Blocker auflöst

- Phase A prüft Maintenance-Drift und Lock-/Cleanup-Nebenwirkungen. Das klärt, ob `openclaw sessions cleanup` oder ein Config-Guard indirekt die Cron-Migration blockiert.
- Phase B prüft den Gateway-Busy-Loop. Wenn die CPU-Last durch Systemjob-/Timer- oder Cron-Trigger verursacht ist, kann die vorbereitete Frequenzreduktion kausal angewendet werden.
- Phase C prüft Session-Write-Locks. Wenn Wartungsjobs parallel zu User-Bootstrap Locks halten, wird die Cron-Migration entweder Teil des Fixes oder ein P0-Folge-Task.

## Pointer

- Detail-Migrationsplan: `/home/piet/vault/04-Sprints/2026-05-02-cron-routing-migration-plan.md`
- Übergangsbericht: `/home/piet/.openclaw/workspace/memory/working/2026-05-02-atlas-fluid-sprint-final.md`
- A-E Abschlussreport-Ziel: `/home/piet/.openclaw/workspace/memory/working/2026-05-02-gateway-busyloop-bootstrap-rca.md`

