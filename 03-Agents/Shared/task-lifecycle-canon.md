# Task Lifecycle Canon — Vollständige Referenz

> Verfasst: 2026-04-13 | Autor: Claude Code (Lifecycle-Analyse)
> Ziel: Einzige autoritative Quelle für den kompletten Task-State-Machine-Vertrag.
> Alle Dispatch- und Receipt-Protokolle von hier ableiten, nicht von alten Gedächtnisschnipseln.

---

## 1. Die vier State-Dimensionen

Jeder Task trägt gleichzeitig vier Zustandsfelder. Sie müssen konsistent sein — `normalizeTaskRecord()` in `taskboard-store.ts` erzwingt das bei jedem Schreibvorgang.

| Feld | Typ | Bedeutung |
|---|---|---|
| `status` | `TaskStatus` | Business-Status, sichtbar auf dem Board |
| `dispatched` | `boolean` | True wenn Task aktiv an einen Worker übergeben wurde |
| `dispatchState` | `DispatchState` | Technischer Dispatch-Zustand |
| `executionState` | `ExecutionState` | Ausführungs-Fortschritt |

### 1.1 Legale `status`-Werte und Übergänge

```
draft       → assigned, canceled
assigned    → in-progress, failed, blocked, canceled
in-progress → review, done, failed, blocked, canceled
blocked     → assigned, in-progress, done, failed, canceled
review      → done, failed, blocked, canceled
done        → []   ← TERMINAL
failed      → []   ← TERMINAL
canceled    → []   ← TERMINAL
```

**Wichtig:** `done` und `failed` sind absolut terminal. Kein PATCH, kein Move kann sie verlassen. Nur `recovery-action` (retry) kann einen `failed`/`blocked` Task zurück in `assigned` bringen — und nur wenn `maxRetriesReached=false` oder es ein Dispatch-Router-Timeout ist.

### 1.2 `dispatchState`-Übergänge

```
draft → queued → dispatched → completed
```

Jeder Sprung nur in dieser Richtung. Kein Zurück.

### 1.3 `executionState`-Übergänge

```
queued   → active
active   → blocked, review, done, failed
started  → active, blocked, review, done, failed
review   → blocked, done, failed
blocked  → active, review, done, failed
done     → []
failed   → []
```

---

## 2. Kanonische State-Kombinationen (von `normalizeTaskRecord` erzwungen)

| `status` | `dispatched` | `dispatchState` | `executionState` |
|---|---|---|---|
| `draft` | `false` | `draft` | `queued` |
| `assigned` | `false` | `queued` | `queued` |
| `in-progress` | `true` | `dispatched` | `active` |
| `blocked` | `true`\* | `dispatched`\* | `blocked` |
| `review` | `true` | `dispatched` | `review` |
| `done` | `true` | `completed` | `done` |
| `failed` | `true` | `completed`\* | `failed` |
| `canceled` | — | `completed` | — |

\* `blocked` behält `dispatched=true` und `dispatchState=dispatched` (Open-State-Pattern).
\* `failed` erhält immer `executionState=failed`, `dispatchState` bleibt `completed` wenn bereits completed.

**Verbotene Kombinationen** (werden von `getImpossibleStateError` abgelehnt):
- `dispatchState=dispatched` + `executionState=queued`
- `dispatchState=completed` + `executionState=active`
- `status=draft` + `dispatched=true`
- `status=done` + `executionState=active`

---

## 3. Atlas Dispatch-Protokoll (KRITISCH)

Wenn Atlas einen Task an einen Spezialisten oder Worker dispatcht, **muss** der PATCH diese Felder enthalten:

```json
{
  "dispatched": true,
  "dispatchState": "dispatched",
  "status": "in-progress",
  "lastExecutionEvent": "dispatch"
}
```

**Das `status: "in-progress"` ist nicht optional.**

Ohne es bleibt der Task auf `assigned`, `normalizeTaskRecord` setzt `dispatched=false, dispatchState=queued` zurück (weil `assigned` das erzwingt). Das Board zeigt dann falschen State, und der Worker-Monitor klassifiziert den Task falsch.

Optional aber empfohlen:
```json
{
  "workerSessionId": "gateway:{agentId}:{taskId}:{timestamp}",
  "workerLabel": "{agentId}",
  "dispatchTarget": "{agentId}",
  "dispatchChannelId": "{channelId}"
}
```

---

## 4. Gateway-Session-IDs und Orphan-Schwellwerte

Der Worker-Monitor unterscheidet zwei Session-Typen anhand des `workerSessionId`-Präfixes:

| Session-Typ | Präfix | Orphan-Threshold |
|---|---|---|
| Direkter Worker | alles andere | 30 Minuten |
| Gateway-Spawn | `gateway:` | **60 Minuten** |

Gateway-Sessions (Forge, Pixel, Lens, James) brauchen länger zum Starten und Antworten. Der 60-Minuten-Threshold verhindert vorzeitige Orphan-Fails.

**Format der gateway-sessionId:** `gateway:{agentId}:{taskId}:{YYYYMMDDHHMMSS}`

Beispiel: `gateway:sre-expert:abc123:20260413142500`

---

## 5. Worker-Monitor Lifecycle-Schritte (worker-monitor.py)

Der Monitor läuft alle 15 Minuten via Cron und führt folgende Phasen aus:

### 5.1 reconcile()
Untersucht alle `in-progress`-Tasks auf Orphans:
- **Case A:** `dispatched=false` → sofort re-queue (`assigned/queued`)
- **Case B:** `dispatched=true`, kein `workerSessionId`, keine aktive Session → nach 30 Min re-queue
- **Case C:** `dispatched=true`, `workerSessionId` gesetzt:
  - Wenn `gateway:`-Präfix → 60-Min-Threshold
  - Sonst → 30-Min-Threshold
  - Nach Ablauf: Task wird auf `blocked` gesetzt (nicht `failed`)

### 5.2 retry_blocked()
Checkt `blocked`-Tasks:
- Wenn `nextRetryAt` in der Vergangenheit und `maxRetriesReached=false` → recovery-action:retry via API

### 5.3 dispatch()
Checkt `assigned`-Tasks:
- Ruft `POST /api/task-dispatch/{taskId}` mit `target=main` auf
- Atlas übernimmt und re-dispatcht ggf. an Spezialisten

### 5.4 notify()
Postet Discord-Nachrichten für wichtige Statuswechsel (done, failed, blocked).
**Hinweis:** Logging-Doppel-Bug war Fix-Stand 2026-04-13 — `log()` schreibt nicht mehr explizit in LOG_PATH, Cron-Redirect übernimmt das.

### 5.5 detect()
Erkennt neu erstellte Tasks ohne Assignment und assigniert sie an Atlas.

### 5.6 sweep()
Bereinigt Zombie-Sessions und veraltete Locks.

---

## 6. Receipt-Endpoint — Worker-Rückmeldung

**Endpunkt:** `POST /api/tasks/{id}/receipt`

**Pflichtfeld:** `stage` (einer von: `accepted`, `started`, `progress`, `result`, `blocked`, `failed`)

### Stage-Anforderungen

**`accepted` / `started`:**
- Validiert via `validateBoardTransition`
- Setzt `workerSessionId` und `workerLabel` aus Body

**`progress`:**
- Checkpoint wird in Vault geschrieben
- Aktualisiert `progressPercent`

**`blocked` (WICHTIG):**
- Erfordert: `status=in-progress AND dispatched=true AND dispatchState=dispatched`
- Setzt `status=blocked`, behält aber `dispatchState=dispatched` (Open-State!)
- Löscht `workerSessionId` und `workerLabel`
- Schreibt Vault-Checkpoint via `writeTaskBlocked()`
- Emittiert Task-Lifecycle-Report

**`result` (Erfolg):**
- Terminal — kein Zurück
- Setzt `status=done`, `dispatchState=completed`, `executionState=done`
- Löscht `workerSessionId` und `workerLabel`
- Schreibt `writeTaskDone()` in Vault
- Emittiert Task-Lifecycle-Report + Discord-Notification

**`failed` (Fehler):**
- Terminal — kein Zurück
- Setzt `status=failed`, `executionState=failed`, `retryCount++` (via worker-monitor)
- Setzt `maxRetriesReached=true` wenn Limit erreicht
- Schreibt `writeTaskFailed()` in Vault
- Emittiert Task-Lifecycle-Report + Discord-Notification

---

## 7. Recovery-Action — Retry-Protokoll

**Endpunkt:** `POST /api/tasks/{id}/recovery-action`

**Body:** `{"action": "retry", "agentId": "{wer retried}"}`

**Voraussetzungen:**
1. Task muss `failed` oder `blocked` sein
2. `maxRetriesReached=false` ODER es ist ein `dispatch-router`-Timeout (Failsafe-Bypass)
3. `nextRetryAt` muss in der Vergangenheit liegen (kein aktives Backoff)

**Was passiert:**
1. Task wird auf `assigned/queued` geprimed (alle Worker-Felder gecleart)
2. `dispatchTask(taskId, 'main')` wird aufgerufen → Atlas bekommt den Task erneut
3. Atlas muss dann selbst entscheiden, ob er direkt bearbeitet oder erneut an Spezialisten delegiert

**Wichtig:** Recovery-Action dispatcht immer an `main` (Atlas), NICHT direkt an den ursprünglichen Spezialisten.

---

## 8. Worker-Pickup-Readiness

**Endpunkt:** `GET /api/worker-pickups`

Ein Task gilt als `ready=true` für Worker-Pickup wenn:
- `hasExecutionContract=true` (Beschreibung enthält alle Pflicht-Marker)
- `workerSessionId` ist leer/nicht gesetzt
- `executionState` ist nicht `done` oder `failed`

**Pflicht-Marker für `hasExecutionContract`:**
- `Task ID:` (regex: `/task id\s*:/i`)
- `Objective:` (regex: `/objective\s*:/i`)
- `Definition of Done` (regex: `/definition of done\s*:?/i`)
- `Return format:` (regex: `/return format\s*:/i`)

Ohne diese Marker lehnt der PATCH-Endpunkt Updates für worker-bound Tasks ab.

---

## 9. Agents-Tab Live-State — Filter-Logik

`GET /api/agents/live` aggregiert den Board-State pro Agent:

**`queued`:** Tasks ohne `dispatched=true` mit `status=assigned` oder (`status=draft AND dispatchState=draft`)

**`active`:** Tasks mit `dispatched=true` und `status` nicht in `done/failed/canceled`

**`fleetHealth`:** Schlechter Wert wenn irgendein Task der Agents `isStuck` ist (= `dispatchState=dispatched` + kein Receipt seit >ORPHAN_THRESHOLD)

Board-State wird immer angezeigt — Live-Runtime-Signals (workerSessionId etc.) beeinflussen nur `fleetHealth`, nicht die Anzeige.

---

## 10. Checkliste: Vollständiger Happy-Path

```
1. Task erstellen (status=draft)
2. Atlas assigned (status=assigned, dispatched=false, dispatchState=queued)
3. Atlas dispatcht Worker:
   PATCH {status:"in-progress", dispatched:true, dispatchState:"dispatched",
          workerSessionId:"gateway:...", lastExecutionEvent:"dispatch"}
4. Worker sendet receipt stage=accepted → Board zeigt acceptedAt
5. Worker sendet receipt stage=started → Board zeigt startedAt
6. Worker sendet receipt stage=progress → Vault-Checkpoint
7. Worker sendet receipt stage=result → status=done, Vault, Discord
```

**Bei Fehler:**
```
7b. Worker sendet receipt stage=failed
    → status=failed (terminal), retryCount++
8b. Worker-Monitor oder Atlas ruft recovery-action:retry auf
    → status=assigned (zurück zu Schritt 2)
```

**Bei Blockade:**
```
7c. Worker sendet receipt stage=blocked
    → status=blocked, dispatchState bleibt dispatched (Open-State)
8c. Worker-Monitor prüft nextRetryAt, ruft recovery-action:retry
    → status=assigned (zurück zu Schritt 2)
```

---

## 11. Bekannte Fixes (Stand 2026-04-13)

| Fix | Datei | Problem | Lösung |
|---|---|---|---|
| Doppel-Logging | worker-monitor.py | `log()` schrieb in Datei + Cron-Redirect | `log()` schreibt nur noch auf stdout |
| Blinder Gateway-Spawn | worker-monitor.py | Kein Liveness-Check vor Spawn | `gw_probe()` vor jedem `gw_chat()` |
| Falscher Orphan-Threshold | worker-monitor.py | 30 Min auch für Gateway (braucht 60) | `GATEWAY_ORPHAN_THRESHOLD_MINUTES=60` für `gateway:`-Sessions |
| Fehlende workerSessionId | worker-monitor.py | Gateway-Tasks hatten kein workerSessionId → Case B statt C | `patch_bridge_blocked_to_active()` setzt synthetic gateway-sessionId |
| Atlas Dispatch-Protokoll | Atlas working-context.md | `status:"in-progress"` fehlte im PATCH | Protocol-Dokument korrigiert |
| Agents-Tab Filter | agents/live/route.ts | queued/active zeigten 0 trotz Tasks | 3 Filter-Bugs gefixt (queued, activeByBoard, active-Gate) |
| Accepted nicht erzwungen | worker-monitor.py | SPECIALIST_DISPATCH_PROMPT enthielt keinen accepted-Schritt | SCHRITT 1 mit explizitem Receipt-Aufruf im Prompt ergänzt |
| Gateway-Kapazität blind | worker-monitor.py | Kein Status-Check vor Spawn — Überlastung | `/agents/{id}/status` wird vor jedem Spawn geprüft |
| maxRetriesReached lautlos | worker-monitor.py | Tasks stuck ohne Operator-Alert | Discord-Notification bei maxRetriesReached=true |
| Recovery wartet auf Atlas | worker-monitor.py | Recovery-Action dispatcht immer an main — Verzögerung | Nach Recovery direkt `_spawn_specialist()` wenn dispatchTarget bekannt |
| Atlas-Ping nicht idempotent | worker-monitor.py | Completion-Pings bei gw_chat-Fehler verloren | pending-pings.json — Retry über Zyklen hinweg |
| Fehlender Token-Check | worker-monitor.py | Ungültiger/fehlender GW-Token erst beim Spawn sichtbar | validate_gateway_token() am Cron-Start mit Discord-Alert |
| Unkontrollierte Dispatch-Order | worker-monitor.py | Alle ready-Tasks ohne Prio dispatcht | Priority-Sort: [P0] → [P1] → [P2] → Rest in dispatch_ready_tasks() |
| Assigned-Task Stuck blind | worker-monitor.py | Tasks auf assigned ohne Dispatch kein Alert | alert_stuck_assigned_tasks() nach 120 Min Discord-Alert |
| Contract-Blocker stumm | worker-monitor.py | missing-execution-contract in Dispatch-Log unsichtbar | Dispatch loggt Tasks die am Contract scheitern explizit |
| Concurrency unbegrenzt | worker-monitor.py | Atlas dispatcht n Tasks gleichzeitig an einen Agent | MAX_CONCURRENT_PER_AGENT Guard in _spawn_specialist() |
| canceled State-Normalisierung | taskboard-store.ts | canceled ließ dispatchState/executionState undefiniert | normalizeTaskRecord: canceled → dispatched=false, completed, done |
