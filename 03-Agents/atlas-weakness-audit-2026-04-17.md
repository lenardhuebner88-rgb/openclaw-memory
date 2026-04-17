---
title: Schwachstellen-Audit 2026-04-17 Abend + Fix-Plan
version: 1.0
status: critical-findings
owner: Principal Reliability Auditor (Claude-Session, Operator-delegiert)
created: 2026-04-17T20:25:00Z
scope: log-basierte Audit der 2h-Orchestrator-Session + Cron-Systeme
---

# Schwachstellen-Audit 2026-04-17 Abend-Session

Log-forensische Analyse nach 2h12min Multi-Agent-Betrieb. **13 konkrete Schwachstellen identifiziert**, davon **3 systematisch-kritisch** die das Versprechen des Systems brechen.

## EXECUTIVE JUDGMENT

Die heutige Session hat viele Artefakte produziert (10 Packs, alle 6 Agents beteiligt). Die **Qualitäts-Unterseite** erzählt eine andere Geschichte: drei der "live" laufenden Säulen des Systems sind stumm oder crashen durchgehend:

1. **`worker-monitor.py` crashed seit Stunden mit SyntaxError** — Stall-Detection + Ghost-Kill sind faktisch tot.
2. **`cost-alert-dispatcher.py` suppliert ALLE Alerts als rate_limit** — Discord-Alert-Kette bisher `sent=0`.
3. **Context-Overflow bei Worker-Sessions** (3× in 2h) — Worker brechen in langen Turns ab.

Diese drei allein reichen, um die "System ist stabil"-Aussage zu widerlegen. Das System **sieht stabil aus**, weil Ausfälle kompensiert werden (Auto-Pickup + MC-Watchdog halten Happy-Path), aber die **Observability-Schicht ist kaputt**. Genau das, was wir heute mit Costs-Cockpit-v2 aufgebaut haben.

## FINDINGS

### F1 — CRITICAL: `worker-monitor.py` SyntaxError — Script tot seit unbekannt

```
File "/home/piet/.openclaw/workspace/scripts/worker-monitor.py", line 810
    f'⚠️ **Pending-pickup timeout auto-failed** `{task_id[:8]}`
    ^
SyntaxError: unterminated f-string literal
```

**Impact**: Cron `*/5 * * * *` läuft, Script stirbt beim Parse. Kein Stall-Detector, kein Ghost-Prefix-Kill (Pack 3 Logik die wir extra gebaut haben), kein Orphan-Reconcile. Wurde in heutiger Session **nicht** als Anomaly erkannt weil das Crash-Output in einem eigenen Log verborgen ist, nicht zentral sichtbar.

**Wann eingeführt**: unklar — f-string-Literal unterbrochen deutet auf einen edit der Backtick-escape verletzt hat. Möglicherweise beim Pack 3 Ghost-Prefix-Guard-Einbau heute Mittag.

**Severity**: CRITICAL — alle Pack-3-Gewinne sind nutzlos wenn das Script nicht läuft.

### F2 — CRITICAL: `cost-alert-dispatcher.py` Rate-Limit-Broken

```
2026-04-17T20:18:02Z SUPPRESS kind=flatrate-rate-spike reason=rate_limit
2026-04-17T20:18:02Z SUPPRESS kind=prepaid-burn-above-baseline reason=rate_limit
2026-04-17T20:18:02Z SUPPRESS kind=prepaid-exhaust-before-reset reason=rate_limit
2026-04-17T20:18:02Z SUPPRESS kind=billing-mismatch reason=rate_limit
2026-04-17T20:18:02Z SUMMARY anomalies=4 sent=0 suppressed=4 failures=0
```

Jeder Cycle (alle 2min) zeigt `sent=0 suppressed=4`. Seit Installation der Alert-Kette um 19:32 hat **keine einzige Cost-Alert** den Discord-Channel erreicht.

**Impact**: Pack 5 gesamte Implementation ist funktional, wird aber durch State-File-Rate-Limit blockiert. Wahrscheinliche Ursache: Rate-Limit-State-File wurde beim ersten Smoke-Test gefüllt und das 15min-Fenster-Cleanup-File ist defekt, oder Alert-Kinds werden zu früh in den State geschrieben ohne dass sie tatsächlich gesendet werden.

**Severity**: CRITICAL — Der Wert des ganzen Pack 5 ist null ohne funktionierende Delivery.

### F3 — HIGH: Context-Overflow in Worker-Sessions (3× in 2h)

```
[context-overflow-diag] sessionKey=agent:sre-expert:main messages=226 compactionAttempts=0
[context-overflow-diag] sessionKey=agent:sre-expert:main messages=208 compactionAttempts=0
[context-overflow-diag] sessionKey=agent:frontend-guru:main messages=103 compactionAttempts=0
```

Forge hatte 2× Context-Overflow mit 226 und 208 Messages (gleiche Session-File wiederverwendet). Pixel hatte 1× bei 103 Messages. Compaction wurde **0× versucht** bei allen drei.

**Impact**: Worker-Turns brechen mitten drin ab. Keine automatische Compaction trotz Trigger-Bedingung erkannt.

**Severity**: HIGH — Worker-Zuverlässigkeit bricht bei Sessions die wiederholt genutzt werden (wie Pack-Iteration). Skalierungs-Blocker.

### F4 — HIGH: Provider-DNS-Failure sporadisch

```
model=gpt-5.3-codex-spark provider=openai-codex error=LLM request failed: DNS lookup for the provider endpoint failed.
```

2× in 2h — DNS-Auflösung für OpenAI-Codex-Endpoint scheitert sporadisch. Fallback-Chain greift und Session recovered, aber mit ~45s Latenz.

**Impact**: User sieht "Something went wrong" oder Turn dauert 45s länger als nötig. Betrifft Rate-Limit-Fallback-Pfade.

**Severity**: HIGH — treibt Fallback auf langsamere Modelle und erhöht Token-Verbrauch.

### F5 — HIGH: Auto-Pickup-Lock-Stuck für 7min

```
19:38:01 CYCLE pending=1 triggered=0 held=0 young=0 locked=1 no_target=0
...7min lang locked=1...
19:43:01 CLEANUP_TERMINAL removed_locks=1
```

Spark-Task `edd017e9` war 7min in Lock-State ohne dass Auto-Pickup reagiert hat. Lock-Cleanup basiert auf `CLEANUP_TERMINAL` was nur terminal-status-Tasks sieht. Wenn Worker-Turn silent dies (wie Spark initial) → Lock bleibt länger als Stale-Threshold (30min, weit zu lang).

**Severity**: HIGH — Worker-Blocking. Stale-Lock-Threshold sollte 5-10min sein, nicht 30min.

### F6 — MEDIUM: Sandbox + Preflight blockt Worker-Operationen

```
[tools] apply_patch failed: Path escapes sandbox root (~/.openclaw/workspace): /home/piet/.openclaw/scripts/plan_schema.py
[tools] exec failed: exec preflight: complex interpreter invocation detected; refusing to run without script preflight validation
[tools] read failed: EACCES: permission denied, access '/root/.npm-global/lib/node_modules/openclaw/skills/...'
```

Worker-Agents (v.a. Forge) treffen mehrfach auf Sandbox-Grenzen (scripts/-Pfade ausserhalb workspace), Exec-Preflight (`chmod && python && python` Command-Chain-Refusal), und root-owned Files (`/root/.npm-global`). Forge musste Workarounds bauen → Zeitverlust pro Pack.

**Severity**: MEDIUM — Worker-Experience leidet, aber nicht blockierend. Sandbox-Config ist evtl zu eng für Scripts außerhalb MC-Repo.

### F7 — MEDIUM: Edit-Tool-Whitespace-Mismatch

```
[tools] edit failed: Could not find the exact text in /home/piet/vault/03-Agents/spark-cost-story-ux-concept.md
```

Spark's Edit-Tool failed wegen Whitespace-Nicht-Match. Edit-Tool braucht exakten string, auch Trailing-Whitespace. Agent musste Workaround nehmen.

**Severity**: MEDIUM — Agents verlieren Zeit pro Edit-Versuch.

### F8 — MEDIUM: Tool-API-Schema-Mismatches

```
[tools] message failed: guildId required (2× verschiedene Calls)
[tools] canvas failed: node required
```

Mehrere Tool-Calls scheitern an fehlenden Required-Params. Agenten wissen API-Schemas nicht vollständig auswendig. Tool-Doc-Gap oder Prompt-Gap.

**Severity**: MEDIUM.

### F9 — MEDIUM: MCP-Taskboard-Leak ist Band-Aid

```
17:45 mcp-reaper: count=4 cap=3 — killing oldest 1
18:15 mcp-reaper: count=4 cap=3 — killing oldest 1
18:30 mcp-reaper: count=4 cap=3 — killing oldest 1
18:45 mcp-reaper: count=4 cap=3 — killing oldest 1
19:15 mcp-reaper: count=5 cap=3 — killing oldest 2
19:45 mcp-reaper: count=4 cap=3 — killing oldest 1
20:15 mcp-reaper: count=4 cap=3 — killing oldest 1
```

Reaper killt alle 15min im Schnitt 1 MCP-Server. Root-Cause (Gateway schließt MCP-Sockets nicht) **nicht gefixt**. Reaper ist dauerhafte Kompensation eines Upstream-Bugs.

**Severity**: MEDIUM — funktional stabil, aber schlechtes Design-Muster.

### F10 — LOW: Forge Pack-Merge Pack 4+5

Forge hat Pack 4 + 5 in einem Turn unter Pack-4-Task-ID abgeschlossen. Pack-5-Task wurde redundant + musste canceled werden. Output ok, aber Task-Buchhaltung falsch — eine Plan-Runner-Phase-Gate würde diese Metrik verzerren.

**Severity**: LOW.

### F11 — LOW: Forge Spark-Bootstrap-Stille

Spark brauchte beim ersten Trigger 20min ohne accepted-Receipt (Rate-Limit-Fallback-Chain von codex-spark → MiniMax dauerte). Re-Trigger-Operator-Eingriff nötig. Logs zeigen Kausalkette, aber die Spark-Stille war nicht diagnostizierbar ohne Gateway-Log-Dive.

**Severity**: LOW — addressiert durch Worker-Hardening Pack 5 (Stall-Detector, nicht implementiert).

### F12 — LOW: admin-close/Auto-Pickup-Race

Bei Cancel kurz nach Dispatch → Worker nimmt Task trotzdem. admin-close sollte pending-pickup-Locks + aktive-Worker-Trigger explizit stoppen.

**Severity**: LOW.

### F13 — INFO: Worker-Monitor-Log getrennt von Zentral-Logging

worker-monitor.py crashed still in eigener Log-Datei (`/home/piet/.openclaw/workspace/scripts/worker-monitor.log`), war nicht Teil meiner Routine-Checks (auto-pickup.log, mc-watchdog.log, cost-alert-dispatcher.log). Zentrale Log-Aggregation fehlt.

**Severity**: INFO aber Root-Cause-Mechanismus für F1 — wir haben es nicht gesehen weil wir die Log-Datei nicht geprüft haben.

## FIX-PLAN

Sieben Packs. Prio-geordnet, reversibel, Multi-Agent.

### P1 — `worker-monitor.py` Syntax-Fix + Self-Test (IMMEDIATE)
- **Lead: Forge**
- Fix: Line 810 f-string terminator korrigieren.
- Additionally: Python `-m py_compile` Pre-Commit-Check im gleichen Deploy.
- Self-Test: `./worker-monitor.py --dry-run` liefert Exit 0 + Zusammenfassung.
- Cron danach manuell triggern zum Verify.
- **Aufwand**: 20min
- **Impact**: F1 resolved

### P2 — `cost-alert-dispatcher.py` Rate-Limit-Bug-Fix (IMMEDIATE)
- **Lead: Forge**
- Rate-Limit-State-File investigieren: `/tmp/mc-costs-alert-state.json`. Prüfen ob `last_sent` Timestamps falsch gesetzt werden (evtl auf `detectedAt` statt `now`), oder ob Suppression vor Send-Versuch triggert.
- Smoke-Test-Mode `COSTS_ALERTS_FORCE_SEND=1` um ersten echten Discord-Alert zu triggern und Alert-Kette live zu verifizieren.
- **Aufwand**: 30min
- **Impact**: F2 resolved, Pack 5 erfüllt Zweck

### P3 — Context-Overflow-Auto-Compaction (HIGH)
- **Lead: Forge**
- Gateway-Config: prüfen ob Compaction-Trigger (200-Messages-Schwelle) aktiv ist. Aktuell `compactionAttempts=0` bei Overflow.
- Wenn Compaction-Hook fehlt: im Worker-Session-Start automatisches `openclaw sessions cleanup --agent <id>` für alte Sessions oder `--compact` Flag.
- Quick Win: Forge-Session die 226 Messages hatte manuell resetten (session-rotation) bevor Pack C dran kommt.
- **Aufwand**: 1-2h
- **Impact**: F3 resolved

### P4 — Auto-Pickup Stale-Lock-Threshold senken (MEDIUM-HIGH)
- **Lead: Forge**
- `STALE_LOCK_SEC` in auto-pickup.py von 1800 (30min) auf 600 (10min) senken.
- Zusätzlich: Check nach 5min ob Task noch `pending-pickup` — wenn ja, Lock als "worker-dead" behandeln und Re-Trigger erlauben.
- **Aufwand**: 15min
- **Impact**: F5 resolved, F11 mitigated

### P5 — Zentrale Log-Aggregation + Health-Endpoint für Scripts (MEDIUM)
- **Lead: Forge**
- Neuer Endpoint `GET /api/ops/script-health` der Output von allen Ops-Scripts zurückgibt: worker-monitor, auto-pickup, cost-alert-dispatcher, mcp-reaper, mc-watchdog.
- Jedes Script schreibt zusätzlich JSON-Heartbeat in gemeinsame Datei `/home/piet/.openclaw/workspace/logs/ops-health.json` (Schema: {script, last_run, exit_code, last_error, critical_count_24h}).
- MC-Board-Addition später (Pack 6 Zone A erweitern oder neue Observability-Mini-Widget).
- **Aufwand**: 2h
- **Impact**: F13 resolved, Diagnose-Tempo +3× bei zukünftigen Incidents

### P6 — Sandbox + Preflight-Relaxation (MEDIUM)
- **Lead: Forge + Operator-Review**
- Sandbox-Root-Config erweitern um `/home/piet/.openclaw/scripts/**` damit apply_patch auch dort funktioniert (heute muss Forge Write umständlich machen).
- Exec-Preflight: Command-Chain-Refusal weicher — erkenne chmod+python als legitime Sequenz.
- Doc-Update: `workspace/AGENTS.md` Abschnitt "Known tool-limits" für Agenten: message-API braucht guildId, canvas braucht node, etc.
- **Aufwand**: 1h
- **Impact**: F6 + F8 resolved

### P7 — MCP-Leak Root-Cause (LONG, parallel)
- **Lead: Forge + James (Research)**
- Gateway-Source dive: warum schließt Gateway MCP-Stdin/Stdout-Pipes nicht nach Session-Ende?
- Falls Upstream-Bug: OpenClaw-Issue-Bericht + Workaround-Dokumentation.
- Parallel: MCP-Taskboard-Prozesse-Pool (statt permanent kill) — existing pool-via-OS-Level.
- **Aufwand**: 3-5 Tage Research + Patch
- **Impact**: F9 resolved dauerhaft

## RISKS

1. **P1 Fix bringt worker-monitor zurück**, der dann latente Ghost-Sessions im aktuellen State aufräumt — evtl unerwartete Task-Fail-Events. Mitigation: Dry-Run-Mode, Discord-Alert-First, kein Auto-Fail am ersten Tag.
2. **P2 Alert-Flood**: wenn Rate-Limit gefixt wird und alle 4 aktuellen Anomalien firen sofort → Discord-Channel-Spam. Mitigation: initial `COSTS_ALERT_RATE_LIMIT=3600` setzen (1/h pro Kind), dann langsam runter.
3. **P3 Compaction bei aktiven Sessions** kann Context-Drop verursachen. Mitigation: nur für >200-Message-Sessions, nicht für in-progress Tasks.
4. **P4 Lock-Threshold 10min** könnte zu aggressiv bei echten langen Turns sein. Mitigation: observieren über 48h, ggf 15min.

## ACCEPTANCE CRITERIA

Pass = 7 von 9.

1. worker-monitor.py läuft erfolgreich über 24h ohne Crash (cron-exit=0).
2. cost-alert-dispatcher sendet ≥1 echte Discord-Message innerhalb 24h.
3. Context-Overflow-Events in 24h: ≤1 (heute: 3 in 2h).
4. Auto-Pickup-Stale-Lock-Zeit im Log immer ≤10min.
5. Neuer `/api/ops/script-health` Endpoint gibt 5 Ops-Scripts zurück mit health=green.
6. Worker-Tool-Failures (sandbox/preflight/schema) reduziert ≤50 % vs heutige 2h-Baseline.
7. MCP-Reaper-Kill-Count ≤5/Tag (heute 8 in 2h = ~48/Tag).
8. Keine Regressionen in bestehenden Packs (Costs-v2 1-5 + Plan-Runner A/D/G funktional).
9. Happy-Path-Smoke-Suite 10/10 grün.

Hard-Stop: #1 (worker-monitor weiterhin tot) oder #2 (keine einzige Alert-Delivery).

## UMSETZUNGSREIHENFOLGE (geschärft durch Atlas-Review 2026-04-17 20:28 UTC)

Atlas-Begründung: "erst Crash fixen, dann Alert-Kette wieder echt machen, dann Lock-Stalls entschärfen, erst danach Compaction sauber angehen. Reliability vor Feature-Arbeit — Pack C darf nicht auf unsicherem Fundament starten."

| Slot | Pack | Aufwand | Wer |
|---|---|---|---|
| Morgen Step 1 | **P1** worker-monitor Syntax-Fix | 20min | Forge |
| Morgen Step 2 | **P2** Alert-Rate-Limit-State fixen | 30min | Forge |
| Morgen Step 3 | **P4** Stale-Lock-Threshold 30→10min | 15min | Forge |
| Morgen Step 4 | **P3** Context-Overflow-Auto-Compaction | 1-2h | Forge + Operator-Observation |
| Mittag | **Pack C** (Plan-Runner Prompt-Templates) | 30-45min | Atlas-Self-Task |
| Nachmittag | **P5** Script-Health-Endpoint | 2h | Forge |
| Spät-Nachmittag | **P6** Sandbox/Preflight-Relaxation | 1h | Forge + Operator-Review |
| Separat-Sprint | **P7** MCP-Leak Root-Cause | 3-5 Tage | Forge + James |

Reliability-Block (P1+P2+P4+P3) muss VOR Pack C abgeschlossen sein. P5+P6 dann parallel zu Pack B/E/F möglich.

## Referenzen

- Log-Quellen: `/home/piet/.openclaw/workspace/logs/auto-pickup.log`, `/mc-watchdog.log`, `/cost-alert-dispatcher.cron.log`, `/mcp-reaper.log`, `/home/piet/.openclaw/workspace/scripts/worker-monitor.log` (!crashing!), `journalctl --user -u openclaw-gateway.service`
- Session-Zeitraum: 2026-04-17 17:35 — 19:47 UTC
- Betroffen: 6 Agents, 10 abgeschlossene Packs, 2 kritische Scripts kaputt
- Parallel-Audit: Atlas hat Session-Report quittiert (3 Empfehlungen), hatte Spark-Stille + admin-close-Race als Concerns eigenständig erkannt
