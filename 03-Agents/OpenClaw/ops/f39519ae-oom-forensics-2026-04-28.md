# f39519ae OOM-Forensik — Hypothesis F (Unknown)

**Datum:** 2026-04-28 23:35 CEST  
**Autor:** Atlas (Read-only Forensik)  
**Session:** f39519ae-b667-454e-963d-05a350967069 (main agent, Atlas)  
**Status:** HYPOTHESIS F — ROOT CAUSE NICHT final lokalisiert

---

## 1. Evidence Table

| # | Evidence | Source | Type | Reliability |
|---|----------|--------|------|-------------|
| E1 | OOM 08:20: Stack `ValueDeserializer::ReadJSObject` + `ReadDenseJSArray` + `ReadTwoByteString` | Journal | Crash-Kontext | ✅ Hoch |
| E2 | OOM 11:11: Stack `node::worker::Message::Deserialize` im JS-Stacktrace | Journal | Crash-Kontext | ✅ Hoch |
| E3 | f39519ae Trajectory: **5.18 MB**, 420 Events, 60× `context.compiled`, 60× `model.completed` | File-Stat | Dateianalyse | ✅ Hoch |
| E4 | messagesSnapshot in model.completed: wächst von 55 (Line 75) → 140 (Line 194) Messages | JSONL line-based parse | Inhalt | ✅ Hoch |
| E5 | messagesSnapshot Rollen: assistant=812, toolResult=812, user=406 (Lines 1-200) | JSONL parse | Inhalt | ✅ Hoch |
| E6 | f39519ae Watchdog pct: 83% → 803% über 7h (05:46–13:23) | `/tmp/session-rotation-watchdog.log` | Log | ✅ Hoch |
| E7 | f39519ae tok-Werte: 545k (08:12), 652k (08:33), 1.14M (10:59), 1.16M (11:31), 1.21M (13:23) | `/tmp/session-rotation-watchdog.log` | Log | ✅ Hoch |
| E8 | OOM 11:11: **8 Rotation-Cycles in 50 Sekunden** (11:10:00–11:10:50) | Journal | Log | ✅ Hoch |
| E9 | OOM 11:11: GC Mark-Compact bei ~2GB Heap → `allocation failure; scavenge might not succeed` | Journal | Crash-Kontext | ✅ Hoch |
| E10 | f39519ae Token-Count liegt bei OOM 11:11 (772%) bei ~1.16M tokens | Watchdog-Interpolation | Schätzung | 🟡 Mittel |
| E11 | f39519ae session.started 04:37 → OOM 04:21 ist NICHT kausal für OOM 04:21 | Timeline | Kausalitätsanalyse | ✅ Hoch |
| E12 | OOM 08:20: f39519ae Watchdog bei 08:12 = 363% (545k tokens), OOM 08:20 = 8min später | Watchdog+Journals | Zeitkorrelation | 🟡 Mittel |
| E13 | OOM 11:11: f39519ae Watchdog bei 10:59 = 762% (1.14M tokens), OOM 11:11 = 12min später | Watchdog+Journals | Zeitkorrelation | 🟡 Mittel |
| E14 | QMD `qmd__search failed: Not connected` um 08:18:50 (vor OOM 08:20) | Journal | Log | 🟡 Niedrig |
| E15 | Model timeouts (kimi-k2.6, MiniMax-M2.7-highspeed) um 08:15 vor OOM 08:20 | Journal | Log | 🟡 Niedrig |
| E16 | `exec denied: allowlist miss` um 11:10:25 vor OOM 11:11 | Journal | Log | 🟡 Niedrig |
| E17 | sessions.json (main) = 5.9 MB / 150 Entries; sessions.json (sre-expert) = 5.7 MB / 150 Entries | File-Stat | Dateianalyse | ✅ Hoch |
| E18 | MCP Child-Prozesse: 5 Instanzen (QMD ×3, Taskboard ×2), ~350 MB kumuliert | ps --forest | Prozess-Analyse | ✅ Hoch |
| E19 | Tool-Calls in f39519ae Trajectory = 0 | JSONL line-based parse | Inhalt | ✅ Hoch |
| E20 | messagesSnapshot enthält 812 toolResult-Einträge als eigenständige Rollen | JSONL parse | Inhalt | ✅ Hoch |

---

## 2. Was sicher ist (Konklusionen mit E1–E9, E11, E17–E19)

1. **OOMs sind V8-JavaScript-Heap-OMs** (nicht systemd-cgroup Limits), bestätigt durch `FATAL: Reached heap limit Allocation failed - JavaScript heap out of memory` + GC-Metriken bei ~2GB Heap.
2. **Stacktrace zeigt Worker-Message-Deserialisierung** (`node::worker::Message::Deserialize` + `ValueDeserializer::ReadJSObject`). Der Gateway nutzt Worker-Threads, und die crashed beim Deserialisieren großer Objekte.
3. **f39519ae ist die größte Einzelsession**: 5.18 MB Trajectory mit 420 Events. messagesSnapshot in model.completed wächst mit jeder Iteration (55→140 Messages).
4. **f39519ae hat 812 toolResult-Rolle-Einträge** in messagesSnapshot. Diese akkumulieren mit jeder Iteration und vergrößern den Context.
5. **Rotation-Trigger ist real**: 8 Rotation-Cycles in 50 Sekunden vor OOM 11:11. Dies löst paralleles Lesen/Deserialisieren der sessions.json und Trajectory-Files aus.
6. **f39519ae hatte OOM 04:21 NICHT verursacht** (Session startete erst 04:37).
7. **Spark-Canary ist definitiv NICHT die Ursache**: 0 Tool-Calls, Session nach allen OOMs gelaufen.
8. **sessions.json-Dateien sind aufgebläht**: main=5.9MB/150 E. + sre-expert=5.7MB/150 E. = 11.6 MB allein an Index-Flatfiles.

---

## 3. Was nur Hypothese ist

| Hypothese | Annahme | Unsicherheitsgrad |
|-----------|--------|-------------------|
| **H1** | f39519ae messagesSnapshot ist die spezifische "Poison Pill", die den Worker-Deserialize zum Platzen bringt | 🟡 Mittel — Kausalität plausibel, aber nicht bewiesen dass NICHT sessions.json oder andere Sessions das Problem sind |
| **H2** | Die Rotation selbst (8× in 50s) löst durch gleichzeitiges Einlesen mehrerer Trajectory-Files den Heap-Crash aus | 🟡 Mittel — Korrelation klar, Kausalität nicht 100% bewiesen |
| **H3** | QMD-Disconnect + Model-Timeouts erzeugen Rückstau im Worker-Pending-Message-Queue, was das Deserialize-Volumen erhöht | 🟡 Niedrig — nur circumstantial |
| **H4** | MCP-Zombies (5 Instanzen, ~350 MB) erhöhen den OS-Pressure so weit, dass der V8-Heap weniger Headroom hat | 🟡 Niedrig — korreliert, kausal nicht bewiesen |
| **H5** | Worker-Threads erhalten eine strukturierte Nachricht mit >500k Token Content (serialisiert als TwoByteString), die den V8-Heap bei der Deserialisierung sprengt | 🟡 Mittel — Stacktrace deutet darauf hin, aber kein direkter Beweis |
| **H6** | Das Problem liegt nicht in f39519ae selbst, sondern im aggregierten Effekt von 150 Session-Einträgen pro Agent × 6 Agenten, die bei Rotation gleichzeitig gelesen werden | 🟡 Mittel — könnte auch andere Sessions betreffen |

---

## 4. Fix-Optionen (ohne sofortige Umsetzung)

### Option 1: Hard Cap Context Payload before Worker postMessage
- **Beschreibung:** Im Worker-Aufruf wird die Nachrichtengröße (messagesSnapshot) begrenzt, bevor `postMessage` aufgerufen wird. Nur die letzten N Messages oder eine Token-Summe < X werden übergeben.
- **Implementierung:** In der Worker-Initialisierung oder im `Message` Serializer die Payload-Größe prüfen und ggf. kappen.
- **Risiko:** Sehr gezielter Fix, aber erfordert Codeänderung im Gateway.
- **Impact auf Spark-Canary:** Keiner.

### Option 2: Do Not structuredClone Full Session Objects
- **Beschreibung:** Die Worker-Kommunikation soll keine vollständigen Session-Objekte per `structuredClone` übergeben. Stattdessen nur Referenzen (Session-IDs) und bei Bedarf Lazy-Load.
- **Implementierung:** Refactoring der Worker-postMessage-Calls, um keine vollständigen `messagesSnapshot`-Arrays zu klonen.
- **Risiko:** Größerer Eingriff in die Architektur.
- **Impact auf Spark-Canary:** Keiner.

### Option 3: Stream JSONL Metadata Instead of Loading Full Arrays
- **Beschreibung:** Die Session-Store-Rotation und Archivierung sollen nur Metadaten (Line-Count, Tokens, Timestamps) streamen, statt vollständige JSONL-Dateien einzulesen.
- **Implementierung:** Streaming-Parser für Trajectory-Files bei Rotation/Backup.
- **Risiko:** Gering — readonly-Architekturänderung.
- **Impact auf Spark-Canary:** Keiner.

### Option 4: Force-Rotate Sessions Above Threshold
- **Beschreibung:** Watchdog-Threshold senken, sodass Sessions mit >300% Token-Count automatisch rotieren, BEVOR sie den V8-Heap kritisch belasten.
- **Implementierung:** Konfigurationsänderung im Watchdog/_rotation_signal_.
- **Risiko:** Gering — Konfigurationsänderung.
- **Impact auf Spark-Canary:** Verhindert Wachstum von f39519ae-artigen Sessions.

### Option 5: Quarantine Oversized Archived Sessions from Hot Path
- **Beschreibung:** Sessions mit Trajectory >2 MB werden nicht mehr in den Hot-Path (sessions.json) aufgenommen, sondern nur als Archiv-Referenz gespeichert.
- **Implementierung:** Bei Rotation: wenn File-Size > X MB → nur Path-Referenz speichern, nicht den vollen Inhalt in den Index laden.
- **Risiko:** Mittel — erfordert Architekturänderung im Session-Store.
- **Impact auf Spark-Canary:** Keiner.

### Option 6: NODE_OPTIONS Heap Increase (Nur Mitigation, kein Root-Fix)
- **Beschreibung:** `NODE_OPTIONS=--max-old-space-size=4096` im Gateway-Environment setzen (4 GB Heap statt ~2 GB default).
- **Implementierung:** systemd Drop-in oder ENV-Änderung.
- **Risiko:** Verschiebung des Problems, kein Root-Fix. Wird bei zukünftigen OOMs wieder passieren.
- **Impact auf Spark-Canary:** Keiner.
- **Hinweis:** Sollte nur als Übergangslösung bis ein echter Fix vorliegt verwendet werden.

---

## 5. Schlussbemerkung

Hypothesis F ist noch nicht abschließend bewiesen. Die Indizien deuten stark auf **Worker-Message-Deserialisierung wachsender Session-Kontexte (H1/H5)** als Root Cause hin, aber **Rotation-Trigger (H2)** und **aggregierte sessions.json-Größe (H6)** bleiben equally plausible Mitverursacher.

Der sicherste nächste Schritt ohne Invasive Code-Änderungen ist **Option 4** (Force-Rotation senken) + **Option 6** (Heap erhöhen als Brücke).

---

*Report generiert: 2026-04-28 23:35 CEST | Atlas Read-only Forensik*
*Keine kompletten Session-Inhalte geparst. Line-based Streaming für alle JSONL-Analysen verwendet.*
