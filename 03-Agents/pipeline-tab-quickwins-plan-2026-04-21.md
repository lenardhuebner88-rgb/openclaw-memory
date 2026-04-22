---
title: Mission-Control Pipeline-Tab Quick-Wins Plan 2026-04-21
date: 2026-04-21 09:40 UTC
author: Operator (pieter_pan) nach Live-Audit Pipeline-Tab gegen Homeserver
status: ready-for-execution
owner: Operator + Atlas-Orchestrator + Forge (primary executor)
priority: P1 (Daten-Wahrheitsgehalt -> Operator-Trust)
---

# Pipeline-Tab Quick-Wins — Audit-Befunde + Phasenplan

## Warum dieser Plan
Live-Audit am 2026-04-21 ~09:30 UTC gegen `/kanban` + `/api/pipeline*` + `/api/agents/live` auf `100.109.144.77:3000` hat 10+ Widersprüche zwischen angezeigten Fakten und Ground-Truth in `tasks.json` offengelegt. Kernproblem: Der Pipeline-Tab sagt dem Operator Zahlen, die nicht stimmen. Bevor neue Pipeline-Features gebaut werden, muss die existierende Oberfläche ihre eigenen Daten ehrlich wiedergeben.

## Live-Evidenz (Ground-Truth gegen DOM-State)

### P0 — Daten-Falschdarstellung

**P0-1 · KPI-Card "INCIDENT 14 · Failed in last 24h" ist nicht korrekt**
- Ground-Truth via `curl /api/tasks`: `failed WITHIN last 24h by failedAt = 0`
- Echte `failedAt`-Timestamps: `2026-04-15`, `2026-04-16`, `2026-04-19` (2-6 Tage alt)
- Subtitle "Failed in last 24h" ist hardcoded String, ignoriert den Zeit-Filter-Chip

**P0-2 · Zeitfilter verwendet falschen Timestamp**
- Filter nutzt `lastActivityAt` statt `failedAt`
- Cleanup-/Admin-Jobs bumpen `lastActivityAt` -> terminale Fehler erscheinen wieder "frisch"
- Beispiel: Task `8482a1db-572c-4aa5-81d6-ad683341dd1a`
  - `failedAt = 2026-04-19T21:08:01Z`
  - `updatedAt = 2026-04-20T14:47:06Z`
  - UI zeigt "seit 18h 40m" — suggeriert junge Incident, tatsächlich 2 Tage alt

**P0-3 · Stepper-Inkonsistenz Stage vs. Status**
- 14/14 Incident-Cards: `currentStage = "working"` + `status = "failed"` + `receiptStage = "failed"`
- Visuell: roter X im "WORKING"-Step; Operator interpretiert "arbeitet noch, hat Problem"
- Fakt: Task ist terminal failed, Worker existiert nicht mehr

### P1 — UI-Widersprüche

**P1-1 · Pixel-Card: Badge + Inhalt widersprechen sich**
- Badge zeigt `NEEDS ATTENTION` rot
- Inhalt: "No task needs attention right now"
- Verifiziert via DOM-Snapshot: `contradictoryNeedsAttention = true`

**P1-2 · Kein Stale-Agent-Signal**
- `updatedAgeMinutes = [1, 7, 1080, 120, 1, 1080]` -> zwei Agents seit 18h ohne Heartbeat
- Status-Badge trotzdem `READY` / `MONITORING` / `OFFLINE` ohne visueller Staleness-Warnung
- Dead-Agent wird nicht erkennbar

**P1-3 · Eigene API meldet "unavailable", UI ignoriert es**
- `/api/agents/live` liefert pro Agent: `fleetHealth.truth = {currentTask:"unavailable", currentTool:"unavailable", heartbeat:"fallback"}`
- 6/6 Agents haben alle Truth-Felder auf Fallback-Werten
- UI zeigt trotzdem selbstbewusst "Monitoring work in progress", ohne diese Confidence-Metadaten anzuspielen

**P1-4 · "Loading live pipeline…" bleibt sichtbar**
- Banner persistiert nach Daten-Merge (Skeleton-Unmount-Race)
- DOM-Check: `loadingIndicator = false`, aber Element sichtbar

**P1-5 · Namens-Drift**
- Tab "Tasks" -> Sub-Tab "Pipeline" -> URL `/kanban` -> Section-Link "Kanban"
- Vier Namen für denselben View

### P2 — Performance & Protokoll

**P2-1 · Aggressives Polling**
- 3 Endpoints parallel alle 12s: `/api/agents/live`, `/api/pipeline`, `/api/pipeline/tasks`
- Roundtrips 350-900ms jeweils -> ~2s aggregate pro Tick pro Viewer = 15 req/min/user

**P2-2 · Endpoint-Redundanz**
- `/api/pipeline` + `/api/pipeline/tasks` liefern überlappende Agent-Daten
- Beide iterieren denselben State

**P2-3 · Kein Filter-Persistenz**
- Filter-State nur in React-State; Tab-Wechsel verliert ihn
- Kein Deep-Link auf gefilterte Sicht möglich

---

## Phasenplan (4 Phasen, ca. 2 Arbeitstage Gesamtaufwand)

### Phase 1 — Daten-Wahrheitsgehalt (P0, ca. 2h)

**Ziel:** Dashboard sagt ehrlich, wie viele Incidents wirklich frisch sind.

**Task 1.1 — Filter-Logik auf `failedAt` umstellen**
- File: `src/lib/pipeline-data.ts`
- Change: Zeitfilter unterscheidet nach Status:
  - `status === "failed"` -> filtert auf `failedAt`
  - `status in ("working","dispatched")` -> filtert auf `lastActivityAt` (aktive Signale)
  - `status === "draft"` -> filtert auf `createdAt`
- Acceptance: `curl /api/pipeline/tasks?window=24h` mit aktuellem Bestand -> 0 Incidents

**Task 1.2 — KPI-Card-Subtitle dynamisch**
- File: `src/app/kanban/PipelineClient.tsx`
- Change: Subtitle reflektiert aktiven Zeitfilter-Chip:
  - `window === "2h"` -> "Failed in last 2h"
  - `window === "24h"` -> "Failed in last 24h"
  - `window === "any"` -> "Total incidents (all time)"
- Acceptance: Filter-Chip wechseln -> Subtitle wechselt im selben Frame

**Task 1.3 — Stepper-Stage für Failed**
- File: `src/lib/task-pipeline-payload.ts`
- Change: Bei `status === "failed"`:
  - `currentStage` auf den Stage setzen, in dem der Fehler passierte (heuristisch: letzter `receiptStage` oder Stage vor `failedAt`)
  - Zusätzlich Feld `failedAtStage` (zukunftssicher)
- Acceptance: Task `8482a1db` mit `failedAt` während `working` -> rotes X bei Working, aber Stage-Semantik korrekt nicht mehr "aktiv"

**Task 1.4 — "seit X" Label truth-basiert**
- File: `src/app/kanban/components/TaskPipelineCard.tsx`
- Change: Zeitbasis pro Status:
  - `failed` -> `failedAt`
  - `working` -> `startedAt`
  - `dispatched` -> `dispatchedAt`
  - `draft` -> `createdAt`
- Nie mehr `updatedAt` als Zeitreferenz
- Acceptance: Task mit `failedAt = 2026-04-19T21:08` zeigt "seit 2d 12h" (heute -2 Tage) statt "seit 18h"

**Smoke-Test Phase 1:**
```bash
curl -s http://127.0.0.1:3000/api/pipeline/tasks | jq '.cards | group_by(.status) | map({status: .[0].status, count: length})'
# Vor: 14 "failed" sehen alle 18h alt aus
# Nach: 14 "failed", korrektes Alter pro Task, Filter 24h = 0
```

---

### Phase 2 — Ehrliche UI-Zustände (P1-1 bis P1-3, ca. 1.5h)

**Task 2.1 — Pixel-Badge Single-Source-of-Truth**
- File: Agent-Card-Komponente (vermutlich `AgentPulseCard.tsx` o. ä.)
- Change: Badge-Logik:
  - `activeTasks + reviewTasks > 0` -> `NEEDS ATTENTION`
  - `status === "monitoring"` -> `MONITORING`
  - sonst -> `IDLE`
- Acceptance: Agent mit 0 aktiven Tasks zeigt niemals mehr `NEEDS ATTENTION` + "No task needs attention"

**Task 2.2 — Stale-Agent-Chip**
- File: Agent-Card-Komponente
- Change: Neuer roter Chip "stale · Xh" wenn:
  - `heartbeatAge > 3600s` UND
  - `status !== "offline"`
- Quelle: `fleetHealth.heartbeat`
- Acceptance: James/Spark mit 18h-alter Heartbeat -> Chip sichtbar

**Task 2.3 — Data-Confidence-Transparenz**
- File: Agent-Card-Komponente
- Change: Info-Chip "data: fallback" neben Heartbeat-Timer wenn `fleetHealth.truth.heartbeat !== "live"`
- Acceptance: Aktuell alle 6 Agents zeigen den Chip (weil alle Truth-Felder auf `fallback`/`unavailable`)

---

### Phase 3 — Performance-Hygiene (P1-4, P2-1..3, ca. 2.5h)

**Task 3.1 — Poll-Tiering**
- File: Pipeline-Container-Hook (SWR/useEffect)
- Change: Zwei Polling-Timer:
  - `/api/agents/live` bleibt 12s (Heartbeat-sensitiv)
  - `/api/pipeline` + `/api/pipeline/tasks` auf 30s
- Acceptance: Network-Tab zeigt agents/live 5×/min, pipeline 2×/min

**Task 3.2 — ETag/304 für pipeline/tasks**
- File: `src/app/api/pipeline/tasks/route.ts`
- Change: Response-Header `ETag: <sha1(updatedAt+count)>`. Request mit `If-None-Match: <hash>` -> 304 bei No-Change
- Acceptance: Curl mit passendem `If-None-Match` -> HTTP 304, `Content-Length: 0`

**Task 3.3 — Skeleton-Dismiss fix**
- File: `src/app/kanban/PipelineClient.tsx`
- Change: Banner rendern nur wenn `!data?.cards && !error`. Sobald `data.cards` gesetzt -> Banner unmount.
- Acceptance: Reload -> Banner verschwindet mit ersten Karten

**Task 3.4 — Filter-State in URL**
- File: `src/app/kanban/PipelineClient.tsx`
- Change: `useSearchParams` + `router.replace(?stage=…&agent=…&window=…)` bei Filter-Änderung
- Acceptance: Filter setzen -> URL ändert sich -> Reload behält Filter -> Link teilbar

---

### Phase 4 — Naming-Consolidation (P1-5, ca. 15 min)

**Task 4.1 — Kanban -> Pipeline**
- Files:
  - `src/app/api/command-search/route.ts:30` (Entry)
  - Section-Link-Card im Header
- Change:
  - Command-Search Entry-Title bleibt "Pipeline" (ist korrekt), aber Aliases ergänzen
  - Section-Link-Text "Kanban" -> "Pipeline"
  - URL-Route kann `/kanban` als Alias behalten (Breaking Change vermeiden)
- Acceptance: Alle 3 Orte sagen "Pipeline". URL bleibt funktional.

---

## Blast-Radius-Matrix

| Phase | Files | Risk | Rollback |
|---|---|---|---|
| 1 | 4 files, ~6 Logic-Punkte | mittel (Filter-Semantik) | revert commit |
| 2 | 1-2 Komponenten | niedrig (Cosmetics + neue Chips) | revert commit |
| 3 | 3 files + 1 neuer API-Header | mittel (ETag-Cache-Drift bei Schema-Änderung) | ETag hinter Env-Flag |
| 4 | 2 files, 1 String-Tweak | trivial | revert commit |

**Total:** ca. 10 einzelne Commits, jeder <60 min, alle reversibel.

---

## NICHT in diesem Plan (größere Initiativen)

- **E1** `/api/pipeline` + `/api/pipeline/tasks` zu einem Endpoint konsolidieren -> API-Break, eigenes Sprint-Item
- **E2** SSE/WebSocket statt Polling -> Infra-Arbeit (Reconnect, Backpressure)
- **E3** Neue Stage "failed" im DAG-Stepper neben Draft->Dispatched->Working->Review->Done -> Schema-Migration, Lifecycle-Tests anpassen
- **E4** `activityPulse` Semantik dokumentieren + in UI sichtbar machen — heute unbenutzte Zahl im Payload

---

## Ground-Truth-Referenzen (für späteres Nachchecken)

- Audit-Timestamp: `2026-04-21T09:38:09Z` (erster `/api/agents/live` Call)
- Tasks-Snapshot: `/tmp/tasks.json` (homeserver) + `/tmp/pipe.json` (pipeline/tasks)
- DOM-Findings via `javascript_tool` — contradictoryNeedsAttention=true, updatedAgeMinutes=[1,7,1080,120,1,1080]
- Polling-Intervall-Messung: `performance.getEntriesByType('resource')` — 3 Endpoints × 12s
- Task-Stichprobe: `8482a1db-572c-4aa5-81d6-ad683341dd1a` (Forge Vault-Git-Auto-Push)

## Sprint-Dispatch

Siehe separater Atlas-Sprint-Prompt: `pipeline-tab-quickwins-atlas-dispatch-2026-04-21.md`
