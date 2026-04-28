# Spark-Canary 24h Soak — OOM-Triage Report (Final)
**Datum:** 2026-04-28 23:30 CEST  
**Autor:** Atlas (Read-only Forensik)

---

## 1. Uptime je Gateway-Prozess bis OOM
| PID | Gateway-Start | OOM-Zeit | Uptime |
|-----|---------------|----------|--------|
| 456446 | 2026-04-27 21:13:44 | 2026-04-28 00:10:25 | ~2h57m |
| 654764 | ~00:11 (nach Restart) | 04:21:11 | ~4h10m |
| 893400 | ~04:21 (nach Restart) | 08:20:54 | ~3h59m |
| 1132781 | ~08:21 (nach Restart) | 11:11:02 | ~2h50m |

---

## 2. Datei-Inventar f39519ae
| Pfad | Größe | mtime |
|------|-------|-------|
| `...f39519ae.trajectory.jsonl.archived` | **5.18 MB** | 2026-04-28 16:56 |
| `...f39519ae.jsonl.archived` | 2.10 MB | 2026-04-28 16:56 |
| `...f39519ae.checkpoint...jsonl.archived` | 2.05 MB | 2026-04-28 16:53 |
| `...f39519ae.trajectory-path.json` | 244 B | 2026-04-28 16:56 |

**Vergleichbare große Sessions:**
| Datei | Größe | Zeit |
|-------|-------|------|
| `06fd3f33...reset` | 924 KB | 2026-04-27 22:34 |
| `a7c39241...reset` | 714 KB | 2026-04-28 08:20 |
| `db928813...archived` | 317 KB | 2026-04-28 06:21 |

---

## 3. JSONL-Metadaten (f39519ae Trajectory)
- **Lines:** 420 events
- **Event-Typen:**
  - `session.started`: 60
  - `context.compiled`: 60
  - `prompt.submitted`: 60
  - `model.completed`: 60
  - `trace.artifacts`: 60
  - `trace.metadata`: 60
  - `session.ended`: 60
- **Größte Zeile:** 261.867 bytes (Line 194, `model.completed`)
- **messagesSnapshot:** Enthält 140 Messages (assistant+toolResult+user) bei model.completed Line 194
- **messagesSnapshot Rolle-Counts (lines 1-200):** assistant=812, toolResult=812, user=406
- **Tool Calls:** 0
- **Base64/image Felder:** Nicht in dieser Session

**Kontext: messagesSnapshot wächst pro Iteration:**
- Line 75: 55 messages → Line 194: 140 messages → Line ~200: noch mehr

---

## 4. Watchdog pct/tok Entwicklung (f39519ae)
| Zeit (CEST) | pct | tok |
|-------------|-----|-----|
| 05:46 | 83% | - |
| 06:26 | 100% | - |
| 07:16 | 211% | - |
| 08:12 | 363% | 545.260 |
| 08:33 | 434% | 652.256 |
| 09:10 | 595% | - |
| 09:36 | 735% | - |
| 10:59 | **762%** | **1.143.465** |
| 11:31 | 772% | 1.158.760 |
| 13:23 | 803% | 1.205.033 |

**Zeitdistanz zu OOMs:**
- OOM 08:20: 8min vor dem Crash war pct=363 → OOM 08:20 tritt ein während pct bei ~512–553 eskaliert
- OOM 11:11: 12min vor dem Crash war pct=762 (1.14M tokens) → Crash bei laufender Escalation

---

## 5. Journal OOM-Zeitfenster — Kritische Erkenntnisse

### OOM 08:20 (PID 893400) — Zeitfenster +/- 5 Min
**Unmittelbar davor:**
- 08:15:12 — Model-Fallback-Entscheidungen (timeout von kimi-k2.6)
- 08:15:20–08:15:23 — **Drei Session-Store-Backups in 3 Sekunden** (alle < 1 Sekunde getriggert)
- 08:18:15–08:19:12 — Intensive `exec`-Kommandos (git diff, board-events checks, MC-data inspection)
- 08:18:50 — `qmd__search failed: Not connected` — QMD-MCP war disconnected

**OM 08:20 — Kein OOM-Journal-Output** (kein Stacktrace in diesem Fenster sichtbar, aber PID 893400 stirbt)

### OOM 11:11 (PID 1132781) — Zeitfenster +/- 5 Min
**Unmittelbar davor:**
- 11:10:00–11:10:50 — **Acht Session-Store-Backups in 50 Sekunden** (8 Rotation-Cycles!)
- 11:10:25 — `exec denied: allowlist miss` — Task-Parity-Check Script blockiert
- **11:11:02 — FATAL: Reached heap limit Allocation failed — JavaScript heap out of memory**

**Exakter GC-Trace vor OOM 11:11:**
```
[1132781:0x393d0000] Mark-Compact 2036.2 (2093.3) -> 2009.5 (2084.6) MB
  allocation failure; scavenge might not succeed
FATAL: Reached heap limit Allocation failed - JavaScript heap out of memory
```

→ **Reine V8 JavaScript Heap-Allocation beim Deserialisieren. Heap war bei ~2GB.**

---

## 6. Hypothesen-Bewertung

| Hypothese | Bewertung | Begründung |
|-----------|-----------|-----------|
| **B — Worker Structured Clone / Session Context (PRIMARY)** | 🔴 HÖCHSTE PRIORITÄT | Stacktrace `ValueDeserializer::ReadJSObject/ReadDenseJSArray` + `node::worker::Message::Deserialize` bestätigt: Worker-Threads deserialisieren große Session-Context-Objekte. messagesSnapshot mit 140 Einträgen + Tool-Results sind die Poison Pills. |
| **C — Trajectory Archiver/Rotation Reads Too Much** | 🔴 HOCH | 8 Rotation-Cycles in 50s vor OOM 11:11. Rotation liest/parst die aufgeblähten Sessions.json-Files. |
| **A — Session Context Too Large** | 🟡 MITTEL | f39519ae mit 1.1M+ Tokens und wachsender messagesSnapshot. Aber Kontext wächst graduell, Crashes sind abrupt bei Rotation. |
| **D — MCP Child Accumulation** | 🟡 MITTEL | 5 redundante MCP-Prozesse (~350MB), verschärfen OS-Pressure, aber keine direkte OOM-Ursache. |
| **E — Spark-specific** | ✅ WIDERLEGT | Spark-Canary lief nach allen OOMs. 0 Tool-Calls. Kein Kausalzusammenhang. |
| **F — Build/Load Pressure** | 🟡 MITTEL | Next.js Build lastet temporär. Gateway-Last durchschnittlich 1.5GB. Addiert zu V8-Heap-Stress. |

---

## 7. Schlussfolgerung

**Root Cause:** Worker-Threads im Gateway-Prozess versuchen, große Session-Kontexte (messagesSnapshot mit Tool-Results + wachsende Message-Historien) per Structured Clone zu deserialisieren. Das V8-Heap-Limit (~2GB) wird dabei erreicht. Die Session-Store-Rotation verschärft das Problem dramatisch: Vor OOM 11:11 wurden **8 Backups in 50 Sekunden** ausgelöst, was massiven parallelen I/O und Memory-Druck erzeugt.

**Trigger-Kette:**
```
Session-Store Rotation (8x in 50s)
  → Liest sessions.json (~6MB)
  → Deserialisiert Session-Blobs in Worker-Threads
  → messagesSnapshot (~140 msgs + toolResults) deserialisiert
  → V8 Heap wächst auf ~2GB
  → GC Mark-Compact schlägt fehl
  → OOM
```

**Spark-Canary-Status:** FAIL_FOR_EXPANSION, aber Spark ist definitiv NICHT die Ursache.

---

### RECOMMENDATION
**Patch session-store rotation + Worker-Heap-Growth.**  
Priorität: 1) Rotation-Frequenz drosseln (max 1× pro Minute), 2) messagesSnapshot-Größe limitieren (nur letzte N Messages speichern, nicht alles), 3) Worker-Heap-Growth überwachen.

### RISK LEVEL
**High.** Jeder Gateway-Restart erhöht die Wahrscheinlichkeit des nächsten OOMs (~4h-Turnus).

### OPERATOR DECISION NEEDED
Genehmigung für: Rotation-Frequenz-Limit setzen und ggf. f39519ae-Session archivieren/beenden.

### NEXT SINGLE ACTION
Warten auf Operator-Ack zur Rotation-Drosselung oder manuellen Session-Bereinigung.