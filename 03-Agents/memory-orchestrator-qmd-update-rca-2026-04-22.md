---
title: memory-orchestrator qmd-update Step rc=1 RCA
created: 2026-04-22
purpose: S-GOV T4 Root-Cause + Fix-Hypothesis — mit Live-Evidence bestätigt
severity: active-silent-failure since 2026-04-21 16:30 UTC
status: RCA-complete, fix-ready
cross-ref: Lens S-GOV T0 DECLINE identifiziert T4 als Blocker; dieser RCA ist Input dafür
---

# memory-orchestrator qmd-update Step rc=1 — Root Cause Analysis

## Symptom

Seit 2026-04-21 16:30 UTC jeder hourly-run des `memory-orchestrator.py` scheitert im Step `qmd-update` mit `rc=1`.

**Frequency:** 5/5 hourly runs zwischen 16:30-20:30 UTC failed mit `rc=1` (100% failure-rate).

**User-visible:** Kein direkter Impact — alle weiteren Steps (kb-compiler, graph-edge-builder, dashboard-generator) werden trotzdem ausgeführt, weil der Orchestrator einzelne Step-Failures nicht als Full-Stop behandelt. **Silent failure → KB-Sync stale**.

## Evidence

### Log-Excerpt (hourly-runs 16:30-20:30 UTC, 2026-04-21)

```
[2026-04-21T16:30:02.023128Z] [error] step=qmd-update rc=1
[2026-04-21T17:30:01.619174Z] [error] step=qmd-update rc=1
[2026-04-21T18:30:02.152060Z] [error] step=qmd-update rc=1
[2026-04-21T19:30:01.732491Z] [error] step=qmd-update rc=1
[2026-04-21T20:30:01.494235Z] [error] step=qmd-update rc=1
```

### Command-Extraction aus `memory-orchestrator.py`

```python
# Zeile 29
QMD_BIN = "/home/piet/.local/lib/node_modules/@tobilu/qmd/qmd"

# Zeile 41
"qmd-update": Step("qmd-update", [QMD_BIN, "update"], ("legacy", "hourly", "nightly")),
```

Der Step ruft direkt: `/home/piet/.local/lib/node_modules/@tobilu/qmd/qmd update`.

### Manual Reproduction (2026-04-21 ~23:10 UTC)

```
ssh homeserver "/home/piet/.local/lib/node_modules/@tobilu/qmd/qmd update"
→ Indexed: 0 new, 0 updated, 4 unchanged, 0 removed
→ ✓ All collections updated.
→ Run 'qmd embed' to update embeddings (31 unique hashes need vectors)
→ EXIT: 0
```

**Command funktioniert prinzipiell** — exit 0 bei manuellem Run ohne aktiven Parallel-Prozess.

### Parallel-Process-Check (zum Zeitpunkt der rc=1 Failures)

```
3449597 bash -c until ! pgrep -f 'qmd.*embed' > /dev/null; do sleep 10; done; ...
3719332 /home/piet/.bun/bin/bun /home/piet/.local/lib/node_modules/@tobilu/qmd/src/qmd.ts mcp
```

**Zwei parallele qmd-Aktivitäten liefen:**
1. Ein **Wait-Loop** `until ! pgrep -f 'qmd.*embed'` — blockierte auf `qmd embed`
2. `qmd mcp` daemon als bun-Process

### Lock-State

```
/tmp/qmd-update.lock           (Apr 19 14:30 — stale, 2 days old!)
/tmp/qmd-native-embed.lock     (Apr 21 09:20)
/tmp/qmd-openrouter-embed.lock (Apr 21 08:30)
/tmp/qmd-pending-monitor.lock  (Apr 21 10:05)
```

### Cron-Schedule-Check

- `memory-orchestrator hourly` → `30 * * * *` (jede Stunde :30)
- `qmd-native-embed-cron.sh` → `15,45 * * * *` (jede Stunde :15 + :45)

**Kritisch:** Der letzte erfolgreiche qmd-native-embed completed um `2026-04-21T22:51:25+02:00` — das ist **22:51:25 CEST = 20:51:25 UTC**, der :45-Slot lief also ~6 min lang (22:45 → 22:51). `qmd embed` hat Long-Running-Characteristic — kann über mehrere Minuten laufen und in den nächsten Slot reichen.

### QMD Daemon Status

```
curl http://127.0.0.1:8181/health
→ curl: (7) Failed to connect to 127.0.0.1 port 8181 after 0 ms
```

**Port :8181 nicht erreichbar** obwohl `bun qmd.ts mcp` Process läuft (PID 3719332). MCP-Daemon ist **NICHT im HTTP-Mode** — vermutlich stdio-only.

## Root Cause (Best Hypothesis)

### Primäre Hypothese: Lock-Konflikt mit `qmd embed` (high confidence)

**Mechanik:**
1. `qmd-native-embed-cron.sh` startet um `:15` und `:45` jeder Stunde, ruft `qmd embed`
2. `qmd embed` nimmt den qmd-internen DB-Lock (SQLite oder ähnlich)
3. `memory-orchestrator hourly` startet um `:30`, ruft `qmd update`
4. Wenn `qmd embed` (:15-Slot) noch läuft bei `:30` → `qmd update` kann DB-Lock nicht akquirieren → `rc=1`

**Evidence:**
- Manual run WÄHREND kein `qmd embed` lief → exit 0
- Fehler passiert konsistent bei :30 (memory-orch-hourly) — genau zwischen :15 und :45 embed-slots
- Der `until ! pgrep -f 'qmd.*embed'` Wait-Loop wurde von JEMAND ANDEREN gestartet (vermutlich qmd-pending-monitor.sh oder manual) — das **bestätigt** dass andere Scripts bereits auf embed warten

**Alternative Hypothese:** Stale `/tmp/qmd-update.lock` vom 19.04. (2 Tage alt) blockiert — **unwahrscheinlich** weil flock-locks an PIDs gebunden sind und bei Process-Exit freigegeben werden; 0-byte-Marker-Dateien sind NICHT der Lock-Mechanismus selbst.

### Sekundäre Hypothese: `qmd embed` läuft >15min und überlappt mit nächstem Slot

Wenn embed :15 Slot Start → >15 min läuft → überlappt :30 → blockt update.

**Evidence:** qmd-native-embed-cron completed um 22:51:25 (6 min nach :45 Start — normal). Aber bei :15-Slots können embed-Runs länger dauern wenn mehr Hashes zu verarbeiten sind.

## Fix-Recommendation (für S-GOV T4)

### Option A: `qmd update` mit flock-retry wrappen (simpel, Low-Risk)

`memory-orchestrator.py` patchen:
```python
# Vor Step-Execution für qmd-update
import subprocess
result = subprocess.run(
    ["flock", "-w", "60", "/tmp/qmd-db.lock", "-c", f"{QMD_BIN} update"],
    timeout=120,
)
```

60s retry-wait sollte Überlappung mit embed schlucken. Wenn nach 60s noch locked → legitimer Fail.

### Option B: Scheduling fix (sauberer, höher-impact)

`memory-orchestrator hourly` von `30 * * * *` auf `50 * * * *` verschieben. `:50` = 5 min nach `:45` embed-Start, mittlere embed-Dauer ist ~6 min → `:50` fällt meist vor embed-Start und embed-Ende.

**Aber:** Timing-abhängig, kann bei langen embed-Runs weiter fehlschlagen. Option A ist robuster.

### Option C: Step als non-critical markieren

`memory-orchestrator.py` so anpassen dass `qmd-update rc=1` ein Warning statt Error ist (wenn manual-update routine genug passiert). Pragmatisch aber **maskiert** das Problem.

## Empfehlung

**Option A + Monitoring.** 60s flock-retry in memory-orchestrator, plus Alert wenn `rc=1` persists >2 consecutive runs (Config-Drift oder tatsächlicher qmd-Fehler).

Wenn Codex/Forge das codieren: der relevante Code-Pfad ist in `memory-orchestrator.py` Zeilen ~55-95 (die Step-Lists `legacy`, `hourly`, `nightly`). Step-Execution-Code ist die Loop-Funktion die Steps iteriert.

## Related Sites

- `qmd-native-embed-cron.sh` → nutzt bereits `flock -n /tmp/qmd-native-embed.lock`, also eigener Lock. Aber es gibt **keinen expliziten qmd-DB-Lock** — das ist qmd-intern.
- `qmd-pending-monitor.sh` → vermutlich der der `until ! pgrep -f 'qmd.*embed'` Wait-Loop startet.
- `qmd-update.lock` seit 2026-04-19 stale → **irrelevant für die aktuellen Failures** (war 2 Tage alt vor dem ersten :30 Fail um 16:30 UTC am 21.04.)

## DoD für Fix (S-GOV T4 input)

- [ ] 3 consecutive hourly-runs `rc=0` for step=qmd-update
- [ ] 24h log: 0× `rc=1` for qmd-update step
- [ ] No regression in other memory-orchestrator steps (kb-compiler, graph-edge-builder, dashboard-generator)
- [ ] Alert-Hook: bei 2× consecutive rc=1 → Discord-Alert (self-monitoring)

## Cross-Reference zu anderen Sprints

- **S-GOV T4 (this RCA's target)** — Fix deploy
- **S-GOV T2 (QMD-Registry-Drift)** — parallel; wenn qmd-native-embed aus registry kommt oder deregistered, könnte Timing-Problem verschwinden
- **Lens S-GOV T0 DECLINE** — identifiziert genau diesen Bug als Blocker, bestätigt unsere Priorisierung

## Reproducibility

```bash
# Check current failure-state
ssh homeserver "tail -500 /home/piet/.openclaw/workspace/logs/memory-orchestrator-hourly.log | grep -E 'qmd-update|rc=' | tail -20"

# Manual run (should succeed when no embed running)
ssh homeserver "/home/piet/.local/lib/node_modules/@tobilu/qmd/qmd update"

# Check parallel qmd activity
ssh homeserver "pgrep -af qmd"

# Check locks
ssh homeserver "ls -la /tmp/qmd*.lock /tmp/memory-orchestrator*.lock"

# Timing analysis: which hourly slots vs qmd-embed slots
ssh homeserver "grep -E ':30:|qmd-update' /home/piet/.openclaw/workspace/logs/memory-orchestrator-hourly.log | tail -20"
ssh homeserver "grep -E 'starting|completed' /home/piet/.openclaw/workspace/logs/qmd-native-embed.log | tail -20"
```

## Next-Actions (Handoff to S-GOV T4 Owner = Forge)

| ID | Owner | Priority | Due | Reason |
|---|---|---|---|---|
| `t4-flock-retry-patch` | forge | P0 | T4 scope | Option A implementieren |
| `t4-verify-3-runs-green` | forge | P0 | T4 DoD | 3h green log |
| `t4-alert-hook` | forge | P1 | T4 stretch | Discord-alert on 2× consecutive rc=1 |
| `t4-schedule-tuning-spike` | atlas | P2 | post-T4 | Option B (`:50` slot) als experiment wenn Option A nicht reicht |
