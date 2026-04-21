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
draft          → assigned, canceled
assigned       → pending-pickup, failed, blocked, canceled
pending-pickup → in-progress, assigned, failed, blocked, canceled
in-progress    → review, done, failed, blocked, canceled
blocked        → assigned, pending-pickup, done, failed, canceled
review         → done, failed, blocked, canceled
done           → []   ← TERMINAL
failed         → assigned
canceled       → []   ← TERMINAL
```

**Wichtig:** `done` und `canceled` sind absolut terminal. `failed` ist fuer den normalen Worker-Lifecycle terminal, darf aber nur ueber den expliziten Recovery-Pfad `POST /api/tasks/{id}/recovery-action` wieder nach `assigned` ueberfuehrt werden. Kein blindes PATCH, kein synthetischer Worker-Receipt.

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
| `pending-pickup` | `true` | `dispatched` | `queued` |
| `in-progress` | `true` | `dispatched` | `active`\* |
| `blocked` | `true`\*\* | `dispatched` | `blocked` |
| `review` | `true` | `completed` | `review` |
| `done` | `true` | `completed` | `done` |
| `failed` | kontextabhaengig | `queued|dispatched|completed` | `failed` |
| `canceled` | `false` | `completed` | `failed` |

\* `in-progress` darf intern auch `stalled` oder `stalled-warning` tragen; operativ bleibt der Business-Status dennoch `in-progress`.
\*\* `blocked` ist Open-State. Der Task bleibt fuer Recovery sichtbar; `dispatchState` bleibt absichtlich `dispatched`.

**Wichtig fuer `failed`:**
- Es gibt bewusst keine einzelne starre `dispatchState`-Kombination mehr.
- Historische Artifact-Shells koennen `queued` sein.
- Live unresolved Fails koennen weiter `dispatched` oder `completed` tragen.
- Die operative Wahrheit fuer Recovery kommt aus `resolvedAt`, `maxRetriesReached` und der aktuellen Recovery-Klassifikation, nicht aus `completedAt` allein.

**Verbotene Kombinationen** (werden von `getImpossibleStateError` abgelehnt):
- `dispatchState=dispatched` + `executionState=queued`
- `dispatchState=completed` + `executionState=active`
- `status=draft` + `dispatched=true`
- `status=done` + `executionState=active`

---

## 3. Atlas Dispatch-Protokoll (KRITISCH)

Atlas dispatcht **nicht** mehr per Direkt-PATCH nach `in-progress`.

Der kanonische Dispatch ist:

```http
POST /api/tasks/{id}/dispatch
```

Danach ist **verpflichtend**:

```http
GET /api/tasks/{id}
```

Der verifizierte Soll-Zustand nach einem erfolgreichen Dispatch ist:

```json
{
  "status": "pending-pickup",
  "dispatched": true,
  "dispatchState": "dispatched",
  "executionState": "queued",
  "workerSessionId": null,
  "acceptedAt": null
}
```

Operative Regeln:
- Kein Direkt-PATCH nach `in-progress` oder `active`.
- Kein synthetisches Setzen von `workerSessionId` als Atlas-Ersatz.
- Kein synthetischer `accepted`-/`started`-Receipt zur "Begradigung".
- Der erste gueltige Worker-Receipt ist der einzige kanonische Claim fuer `pending-pickup -> in-progress`.
- Wenn Atlas direkt per API dispatcht, ist `dispatchToken` Board-Provenance und darf nicht durch Fantasiewerte ersetzt werden.

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

**Pflichtfeld:** `receiptStage` oder `stage` (einer von: `accepted`, `started`, `progress`, `result`, `blocked`, `failed`)

### Stage-Anforderungen

**`accepted` / `started`:**
- Validiert via `validateBoardTransition`
- Setzt `workerSessionId` und `workerLabel` aus Body
- Fuer den ersten Claim eines `pending-pickup`-Tasks ist ein passender `dispatchToken` Pflicht, wenn der Task bereits einen Token traegt
- `accepted` promoted den Task kanonisch nach `in-progress`

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
- Terminal fuer den aktuellen Worker-Lauf
- Setzt `status=failed`, `executionState=failed`
- Schreibt `writeTaskFailed()` in Vault
- Emittiert Task-Lifecycle-Report + Discord-Notification
- Ein erneuter Start darf danach nur ueber `recovery-action:retry` passieren

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
2. Danach wird wieder kanonisch `dispatchTask(...)` aufgerufen
3. Das Retry-Ziel wird aus dem aktuellen Task-Kontext aufgeloest; es geht nicht mehr pauschal immer an `main`

**Wichtig:**
- Recovery ist der einzige legale Weg, einen `failed`/`blocked` Task wieder anzulaufen
- Kein synthetischer Worker-Receipt als Ersatz fuer Recovery
- Vor einem Retry immer Task-State per GET verifizieren

---

## 8. Worker-Pickup-Readiness

**Endpunkt:** `GET /api/worker-pickups`

Ein Task erscheint dort nur, wenn er bereits:
- `status=pending-pickup`
- `dispatched=true`
- `dispatchState=dispatched`

Ein Task gilt dort nur dann als `ready=true`, wenn zusätzlich:
- `hasExecutionContract=true` (Beschreibung enthält alle Pflicht-Marker)
- `workerSessionId` ist leer oder nur ein Gateway-Placeholder
- `status`/`executionState` sind nicht `blocked`
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
3. Atlas dispatcht kanonisch:
   POST /api/tasks/{id}/dispatch
4. Atlas verifiziert per GET:
   status=pending-pickup, dispatched=true, dispatchState=dispatched,
   executionState=queued
5. Worker sendet receipt stage=accepted (+ dispatchToken wenn gefordert)
   → status=in-progress, executionState=active
6. Worker sendet optional receipt stage=started / progress
7. Worker sendet receipt stage=result → status=done, Vault, Discord
```

**Bei Fehler:**
```
7b. Worker sendet receipt stage=failed
    → status=failed, executionState=failed
8b. Atlas/Operator macht RCA und entscheidet:
    - historisches Artefakt? → sauber admin-close / dokumentieren
    - echter offener Fail? → recovery-action:retry
9b. recovery-action:retry
    → status=assigned, dann wieder dispatch → pending-pickup
```

**Bei Blockade:**
```
7c. Worker sendet receipt stage=blocked
    → status=blocked, dispatchState bleibt dispatched (Open-State)
8c. Atlas/Operator entscheidet explizit Recovery, Reassign oder Nacharbeit
    → nie blind retriggern, nie synthetischen accepted-Receipt schreiben
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
| Recovery wartet auf Atlas | worker-monitor.py | Frueher dispatchte Recovery-Action pauschal an `main` — Verzoegerung | Nach Recovery direkt `_spawn_specialist()` wenn dispatchTarget bekannt |
| Atlas-Ping nicht idempotent | worker-monitor.py | Completion-Pings bei gw_chat-Fehler verloren | pending-pings.json — Retry über Zyklen hinweg |
| Fehlender Token-Check | worker-monitor.py | Ungültiger/fehlender GW-Token erst beim Spawn sichtbar | validate_gateway_token() am Cron-Start mit Discord-Alert |
| Unkontrollierte Dispatch-Order | worker-monitor.py | Alle ready-Tasks ohne Prio dispatcht | Priority-Sort: [P0] → [P1] → [P2] → Rest in dispatch_ready_tasks() |
| Assigned-Task Stuck blind | worker-monitor.py | Tasks auf assigned ohne Dispatch kein Alert | alert_stuck_assigned_tasks() nach 120 Min Discord-Alert |
| Contract-Blocker stumm | worker-monitor.py | missing-execution-contract in Dispatch-Log unsichtbar | Dispatch loggt Tasks die am Contract scheitern explizit |
| Concurrency unbegrenzt | worker-monitor.py | Atlas dispatcht n Tasks gleichzeitig an einen Agent | MAX_CONCURRENT_PER_AGENT Guard in _spawn_specialist() |
| canceled State-Normalisierung | taskboard-store.ts | canceled ließ dispatchState/executionState undefiniert | normalizeTaskRecord: canceled → dispatched=false, completed, done |
