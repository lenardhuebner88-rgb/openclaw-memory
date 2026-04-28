# Spark-Canary 24h Soak — OOM-Triage Report

## 1. Uptime je Gateway-Prozess bis OOM
- PID 456446: Start 21:13 -> Crash 00:10:25 -> Uptime ~2h57m
- PID 654764: Nach Restart #1 -> Crash 04:21:11 -> Uptime ~4h10m
- PID 893400: Nach Restart #2 -> Crash 08:20:54 -> Uptime ~3h59m
- PID 1132781: Nach Restart #3 -> Crash 11:11:02 -> Uptime ~2h50m

## 2. Aktive Agenten/Sessions +/- 15 Minuten
- 00:10: Keine direkte Agent-Aktivität, chronologische Trigger durch System-Cron/Rotation.
- 04:21: `main` Agent aktiv (Archivierungs-Session).
- 08:20: `sre-expert` aktiv (4 modifizierte Sessions), `main` aktiv (Reset-Logs).
- 11:11: `sre-expert` stark aktiv (5 offene Sessions, u.a. 99820c87).

## 3. Größte trajectory/session files
- Es liegen massive `.reset`-Dateien vor (z.B. `06fd3f33...reset` mit 924 KB, `a7c39241...reset` mit 714 KB).
- Die zentralen `sessions.json` Index-Dateien wachsen ungebremst: `main` liegt bei 5.7 MB und `sre-expert` bei 5.5 MB. Dies überlastet das JSON-Parsing massiv.

## 4. Session-store rotation/backups
- Die OOM-Events (speziell um 00:10) fallen in Backup-Zyklen. Der Watchdog meldet zudem bei Einzel-Sessions (`f39519ae`) einen Growth von bis zu 796% Capacity als Notfall.

## 5. MCP-child accumulation & qmd/taskboard
- Es existieren aktuell 5 redundante MCP-Child-Prozesse (3x `bun` für qmd auf Port 8181 sowie 2x `node taskboard`). Über Restarts hinweg bauen sich verwaiste Prozesse auf. Sie binden OS-RAM (ca. 350 MB), treiben den Gateway-Prozess selbst aber nicht ins OOM.

## 6. Memory Limits & Trigger-Analyse (V8 vs Systemd)
- OS Cgroup Limits für den Service:
  - `memory.high` = 5.0 GB
  - `memory.peak` gemessen bei OOMs = 4.08 GB
  - `MemoryMax` laut systemd = `infinity`
- Trigger-Befund: Da das cgroup-Limit noch Spielraum hat und der Crash-Typ `v8::internal::V8::FatalProcessOutOfMemory` (Stack: `ValueDeserializer::ReadJSObject`) ist, scheitert rein der interne Javascript-V8-Heap an der Deserialisierung extrem großer Datenmengen aus den Session-Caches.

## 7. Hypothesen Ranking
1. **session-store/context growth (RANK 1)**: Massive `sessions.json`-Indexdateien (6 MB) und fehlschlagende Archivierungen sprengen den V8-Heap.
2. **agent trajectory/session growth (RANK 2)**: Festgefahrene Sessions triggern internen Overflow (Watchdog-Alerts).
3. **MCP-child/process accumulation (RANK 3)**: Erhöht System-Baseload (Zombie-Instanzen), aber führt nicht direkt zum Gateway-OOM.
4. **build/load pressure (RANK 4)**: Der Next.js-Build (1.7GB RSS) zieht RAM, ist aber ein separater OS-Prozess.
5. **worker-rotation/spark-specific (RANK 5)**: Widerlegt. Spark-Canary lief nach den Crashes fehlerfrei und ohne Tool-Writes.
6. **unknown (RANK 6)**: Sonstige Leaks.

---

### Recommendation
Patch session store memory leak / cleanup first. Die massiven `sessions.json` Dateien müssen manuell verkleinert/archiviert werden, um den Deserialisierungs-Load beim Gateway-Boot zu nehmen. Anschließend redundante MCP-MCP-Zombies bereinigen und das Soak-Fenster neu starten.

### Risk level
High (Service-Stabilität durch regelmäßige deterministische 4h-Heap-Crashes gefährdet).

### Operator decision needed
Erlaubnis zum drastischen Aufräumen (Pruning) der `sessions.json` Store-Files für `main` und `sre-expert`.

### Next single action
Operator-Ack einholen für direkte File-Korrektur an `sessions.json` im Agent-Environment.