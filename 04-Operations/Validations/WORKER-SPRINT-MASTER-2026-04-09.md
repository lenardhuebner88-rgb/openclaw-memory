# Worker Sprint — Master Report
**Datum:** 2026-04-09 | **Sprint:** 5-Phasen | **Alle Agents beteiligt**

---

## Executive Summary

Das Worker-System hat einen **Architektur-Defekt**: 3 konkurrierende Sources of Truth ohne Reconciliation. Der Heartbeat-Controller existiert nur als Dokumentation — nicht als funktionierender Loop. Das ist kein Bug-Fix mehr, das ist ein Redesign.

**Schadensbild:**
- Tasks bleiben in mittleren States hängen (assigned, dispatched)
- `/api/agents/live` und Heartbeat-Status widersprechen sich
- ZOMBIE-Zustände existieren live im Board
- Team-Tab zeigt veraltete Modelle

---

## Phase 1 — Atlas + GPT-5.4: State-Analyse

**Quelle:** `WORKER-PHASE1-ATLAS-2026-04-09.md`

### State-by-State
| State | Status | Problem |
|-------|--------|---------|
| `draft` | ✅ Funktioniert | Korrekt |
| `assigned` | ⚠️ Schwach | Nicht hart mit dispatch/executionState verknüpft |
| `in-progress` | ⚠️ Schwach | Gleiche Lücke |
| `review` | ⚠️ Undokumentiert | Existiert in HEARTBEAT.md aber nicht in API |
| `done` | ✅ Sicher | Terminal-State konsistent |
| `failed` | 🔴 **BROKEN** | Existiert in HEARTBEAT.md aber NICHT im Code |

### Race Prevention
- File Lock + Atomic Write ✅ vorhanden
- Aber schwächer als dokumentiert

---

## Phase 2 — James: Task-Lifecycle Deep-Research

**Quelle:** `WORKER-PHASE2-JAMES-2026-04-09.md`

### 3 konkurrierende Sources of Truth
```
1. tasks.json     → Board-Wahrheit
2. runs.json     → Subagent-Wahrheit
3. /api/agents/live → Session/Overlay-Wahrheit
```

### KERNBEFUND: Heartbeat-Controller existiert NICHT
HEARTBEAT.md beschreibt einen Controller-Flow der so nicht implementiert ist:
- ❌ Board scannen
- ❌ sessions_spawn ausführen
- ❌ runs.json reconciled
- ❌ /api/tasks/{id}/complete|fail aufrufen

**Das ist der Architektur-Defekt.**

### Live-Zombie gefunden
```
status=draft + dispatched=true + dispatchState=dispatched + executionState=queued
```
Genau der Zustand vor dem HEARTBEAT.md warnt.

### Heartbeat vs Live-Session decoupled
- `/api/agents/live`: zeigt frische Aktivität (unserer aktiver Sprint!)
- `/api/heartbeat/status`: sagt "alle Core-Agents down", letzter Beat 2026-04-07
- Das sind 2 Tage her!

### runs.json
- 388 Runs total
- 1 fertiger Run mit `cleanupHandled=false` → Completion-Cleanup funktioniert nicht zuverlässig

---

## Phase 3 — Forge: State-Transition-Validierung

**Quelle:** `WORKER-PHASE3-FORGE-2026-04-09.md`

### Kritische Bugs
| # | Bug | Severity |
|---|-----|----------|
| T1 | `dispatchState=completed` + `executionState=queued` möglich | 🔴 |
| T2 | PATCH-Route keine Transition-Gates | 🔴 |
| T3 | Retry-Logik in `/fail` defect, `retryCount` bleibt auf 1 | 🔴 |
| T4 | `status=failed` fällt auf `draft` zurück | 🔴 |
| T5 | Race-Risk: read-modify-write ohne etag | 🟡 |

### PATCH-Route zu offen
Jeder Client kann beliebigen State setzen ohne Transition-Validation. Das erlaubt inkonsistente Zustände.

---

## Phase 4 — Lens: Performance + Kosten

**Quelle:** `WORKER-PHASE4-LENS-2026-04-09.md`

### Metriken
| Metrik | Wert |
|--------|------|
| Heartbeat-Intervall | **15 Min** (nicht 5 Min wie docs) |
| Heartbeat-Zyklus | ~23.6s |
| Heartbeat-Kosten | $0.67/Tag |
| runs.json | 387 Runs, 349 >24h alt |
| tasks.json | 2193 Zeilen, 108KB, 98 Tasks, 82 done |
| task-board-auto-cleanup | 🔴 FEHLERHAFT (GatewayDrainingError) |

### Gaps
- Kein harter externer Watchdog
- Keine Archivierung für runs.json/tasks.json
- Heartbeat-Doku passt nicht zur Realität
- Overlap zwischen Heartbeat/Executor/Auto-Fix/Cleanup

---

## Phase 5 — Pixel: E2E UI-Test

**Quelle:** `WORKER-PHASE5-PIXEL-2026-04-09.md`

### Lifecycle Visibility
| State | UI sichtbar? |
|-------|--------------|
| draft | ✅ |
| assigned | ❌ |
| dispatched | ❌ |
| active | ✅ |
| done | ✅ |

**assigned + dispatched sind für User UNSICHTBAR im UI.**

### Team-Tab
- Modelle stark out of sync mit `/api/agents/live`
- Besonders Pixel, Lens, Pulse, Flash betroffen

### API-Bug entdeckt
POST /api/tasks ohne `description` wird abgelehnt — das war früher anders.

---

## Master-Issues-Liste (Priorisiert)

### 🔴 CRITICAL — Architektur

**[M1] Kein Heartbeat-Controller**
- HEARTBEAT.md beschreibt einen Flow der nicht existiert
- Niemand reconciled tasks.json + runs.json + agents/live
- Fix: Heartbeat-Controller als echten Loop implementieren ODER OpenClaw-Gateway nutzen

**[M2] 3 Sources of Truth ohne Reconciliation**
- tasks.json, runs.json, /api/agents/live widersprechen sich
- Fix: Eine Wahrheit definieren, andere als abgeleitete Views

**[M3] status=failed funktioniert nicht**
- Code: kein echter `status=failed`
- Fällt auf `draft` zurück
- Fix: `/api/tasks/[id]/fail` implementieren + State-Machine anpassen

### 🔴 CRITICAL — States

**[M4] Mittlere States (assigned/dispatched) unsichtbar**
- User sieht nur draft/active/done
- Assigned/dispatched Tasks verschwinden im UI
- Fix: UI erweitern oder State-Transitions transparent machen

**[M5] dispatchState/executionState Inkonsistenzen**
- `dispatchState=completed` + `executionState=queued` möglich
- Fix: State-Machine mit harten Konsistenzregeln

**[M6] PATCH-Route keine Transition-Gates**
- Jeder State kann willkürlich gesetzt werden
- Fix: Ingress-Validation in PATCH

### 🟡 MEDIUM — Operations

**[M7] task-board-auto-cleanup fehlerhaft**
- GatewayDrainingError
- Fix: Deaktivieren oder reparieren

**[M8] runs.json wächst unbegrenzt**
- 387 Runs, 349 >24h alt
- Fix: Auto-Archivierung nach 7 Tagen

**[M9] tasks.json Archivierung**
- 82 done-Tasks, viele davon historisch
- Fix: done-Tasks >30 Tage archivieren

**[M10] Team-Tab Modelle out of sync**
- Modelle stimmen nicht mit /api/agents/live
- Fix: /api/team-models API reparieren (war gestern schon gefixt)

### 🟢 LOW — Docs

**[M11] HEARTBEAT.md vs Realität**
- Dokumentierte 5-Min-heartbeat, real 15-Min
- Fix: Docs an Realität anpassen

**[M12] POST /api/tasks ohne description**
- API bricht bei fehlender description
- Fix: description optional machen

---

## Empfohlene Reihenfolge

1. **M3** (status=failed) — am schnellsten zu fixen, größter immediate Impact
2. **M7** (cleanup) — deaktivieren wenn nicht reparabel
3. **M8** (runs.json Archivierung) — prevent future growth
4. **M9** (tasks.json Archivierung) — 82 done-Tasks aufräumen
5. **M4** (UI visibility) — für User-Experience
6. **M1** (Heartbeat-Controller) — Architektur, größte Arbeit

---

## Nicht in diesem Sprint
- M1 komplettes Redesign (braucht Ownernship + Design-Entscheidung)
- Graph-Memory
- Vector-DB
- Neue Agents

---

## Dateien erstellt
- WORKER-PHASE1-ATLAS-2026-04-09.md (sre-expert)
- WORKER-PHASE2-JAMES-2026-04-09.md (researcher)
- WORKER-PHASE3-FORGE-2026-04-09.md (sre-expert)
- WORKER-PHASE4-LENS-2026-04-09.md (efficiency-auditor)
- WORKER-PHASE5-PIXEL-2026-04-09.md (frontend-guru)
