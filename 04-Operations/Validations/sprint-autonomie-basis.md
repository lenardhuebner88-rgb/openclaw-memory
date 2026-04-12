# Sprint: Autonomie-Basis
**Erstellt:** Lens, 2026-04-12 (code-validiert via SSH)
**Ziel:** Minimaler autonomer Betrieb — Tasks werden ohne menschliches Zutun aufgegriffen, ausgeführt, abgeschlossen
**Owner:** Atlas (Orchestration) + Forge (Umsetzung)

---

## Was bereits implementiert ist (nicht nochmal bauen)

Direkt aus dem Code verifiziert:

| Bereich | Status |
|---------|--------|
| `fail/route.ts` — status=failed mit Retry + Backoff | ✅ fertig |
| PATCH-Route Transition-Gates (`DISPATCH_TRANSITIONS`, `getImpossibleStateError`) | ✅ fertig |
| board-consistency (`/api/board-consistency` → `{"status":"ok","issueCount":0}`) | ✅ fertig |
| Security-check.sh (`--scope workspace`) → gibt aktuell `STATUS: OK` zurück | ✅ ok |
| `worker-pickups` API (`GET /api/worker-pickups`) | ✅ fertig |
| `worker-runner` API (`POST /api/worker-runner`) | ✅ fertig |
| `worker-monitor.py` (alle 15 Min, erkennt hängende Sessions) | ✅ läuft |

---

## Die zwei echten Lücken

### Lücke 1 — Kein Dispatch-Loop

`worker-pickups` listet bereite Tasks. `worker-runner` attached Worker.
**Aber nichts ruft beides automatisch auf.**

`worker-monitor.py` erkennt hängende Sessions, spawnt aber keine neuen.
Der Loop `dispatched → Session spawnen → ausführen → complete` fehlt.

### Lücke 2 — Execution Contract Pflicht

`worker-runner` lehnt Tasks ab wenn `description` nicht folgende 4 Felder enthält:
```
task id: <id>
objective: <was zu tun ist>
definition of done: <wann fertig>
return format: <wie Ergebnis zurückmelden>
```
Tasks ohne dieses Format → `blocked: missing execution contract` sofort bei Dispatch.
Atlas muss Tasks in diesem Format erstellen — das ist aktuell nirgends formalisiert.

---

## Vor dem Sprint — Atlas entscheidet (5 Min)

> **Dispatch-Loop: Wo soll er laufen?**
> - Option A: `worker-monitor.py` erweitern (bereits als Cron aktiv, alle 15 Min)
> - Option B: Neues `dispatch-loop.py` als separater Cron (sauberere Trennung)
>
> **Empfehlung:** Option A — monitor.py hat bereits Cron-Slot, Infra-Overhead minimal.

---

## Phase 1 — Blocked Tasks freischalten
**Owner:** Forge | **Aufwand:** ~30 Min | **Keine Atlas-Entscheidung nötig**

### Task P1-A: 8 Security-blocked Tasks terminieren

Security-check.sh gibt aktuell OK zurück. Die 8 Tasks aus 2026-04-11 haben aber noch `securityRequired: true` + `blockerReason: "Security check failed (critical)"` im JSON-State und kommen deshalb nicht weiter.

**Vorgehen:**
```bash
# Für jeden der 8 Task-IDs: complete-Endpoint neu aufrufen
# Die IDs:
# 2e89fa6f, 4a7bbc73, 4cc89b06, 939e95b5, 377a6912, ff4d92ba, 0339bc12, 9673093b

curl -X POST http://127.0.0.1:3000/api/tasks/2e89fa6f/complete \
  -H 'Content-Type: application/json' \
  -H 'x-actor-kind: system' \
  -H 'x-request-class: write' \
  -d '{"resultSummary": "Manually cleared after security gate resolved"}'
# → Wiederholen für alle 8 IDs
# Wenn Task bereits done: response enthält alreadyDone:true — ok
```

**Erfolgskriterium:**
- Alle 8 Tasks auf `done` oder `failed` (kein `blocked` mehr)
- Board zeigt 0 security-blocked Tasks

---

## Phase 2 — Execution Contract in Atlas-Kontext verankern
**Owner:** Atlas (Konfiguration) | **Aufwand:** ~20 Min

### Task P2-A: Execution Contract Format in HEARTBEAT.md + Atlas working-context

Atlas muss beim Erstellen von Tasks dieses Format verwenden:

```
task id: {task_id}
objective: {was der Agent tun soll}
definition of done: {wann der Task als erfolgreich gilt}
return format: {wie der Agent das Ergebnis zurückmelden soll — z.B. POST /api/tasks/{id}/complete mit resultSummary}
```

**Vorgehen:**
1. In `HEARTBEAT.md` Abschnitt "Task-Erstellung" ergänzen: Execution Contract ist Pflicht
2. In Atlas `working-context.md` als Regel eintragen: jeder neue Task braucht Execution Contract

**Erfolgskriterium:**
- HEARTBEAT.md enthält das Template
- Atlas working-context hat die Regel

---

## Phase 3 — Dispatch-Loop implementieren
**Owner:** Forge | **Aufwand:** ~60-90 Min | **Abhängigkeit:** Atlas-Entscheidung (Option A oder B)

### Task P3-A: worker-monitor.py um Dispatch-Logik erweitern (Option A)

Der bestehende Loop `main()` erkennt bereits hängende Sessions. Ergänzen:

**Neue Funktion `dispatch_ready_tasks()`:**
```python
# 1. GET http://127.0.0.1:3000/api/worker-pickups
#    → tasks mit ready=True
# 2. Für jeden ready Task:
#    a. POST /api/worker-runner {taskId: id}  → Worker attachen
#    b. Subagent spawnen via OpenClaw CLI:
#       openclaw sessions spawn --agent {assignee} --prompt "{task_brief}"
#    c. session_key in runs.json eintragen (für späteres Monitoring)
# 3. Logging: jede Aktion in worker-monitor.log
```

**Wichtig:** Nicht mehr als `MAX_CONCURRENT = 3` Tasks gleichzeitig spawnen.

**Vorgehen:**
1. `worker-monitor.py` lesen, `dispatch_ready_tasks()` Funktion ergänzen
2. In `main()` vor der hanging-run-Erkennung aufrufen
3. Testen mit einem echten Test-Task (ohne echten Schaden)

**Erfolgskriterium:**
- `worker-monitor.py` läuft ohne Error durch einen vollen Zyklus
- Ein Test-Task mit gültigem Execution Contract wird automatisch aufgegriffen

---

## Phase 4 — E2E-Test
**Owner:** Atlas orchestriert | **Startet nach:** Phase 3 grün

### Testszenario 1 — Happy Path (Autonomer Lifecycle)
```
1. Atlas erstellt Task mit Execution Contract:
   title: "E2E Test Autonomy"
   description: |
     task id: {generated-id}
     objective: Erstelle /tmp/autonomy-test.txt mit Inhalt "autonomy works"
     definition of done: Datei existiert mit korrektem Inhalt
     return format: POST /api/tasks/{id}/complete mit resultSummary

2. Task auf dispatched setzen
3. Kein manueller Eingriff — 15 Min warten (worker-monitor Zyklus)
4. Erwartung: Task auf done, Datei existiert
```
**Pass:** `status=done` ohne menschlichen Eingriff

---

### Testszenario 2 — Fehler-Recovery
```
1. Task mit Execution Contract erstellen
   objective: führe /bin/does-not-exist aus
2. Dispatchen, warten
3. Erwartung: status=failed, retryCount=1, kein Loop zurück zu draft
```
**Pass:** `status=failed`, nicht `status=draft`

---

### Testszenario 3 — Contract-Guard
```
1. Task OHNE Execution Contract erstellen (nur normaler Text in description)
2. Dispatchen
3. Erwartung: blocked mit "missing execution contract"
4. Atlas ergänzt Contract, re-dispatcht
5. Erwartung: diesmal aufgegriffen
```
**Pass:** System blockt korrekt und recovert nach Contract-Ergänzung

---

### Testszenario 4 — Parallelbetrieb
```
1. 3 Tasks mit Execution Contract gleichzeitig dispatchen (Forge, James, Pixel)
2. 15+ Min warten
3. Erwartung: alle 3 unabhängig aufgegriffen und abgeschlossen
```
**Pass:** Kein gegenseitiges Blockieren

---

## Sprint-Reihenfolge für Atlas

```
Sofort:  P1-A → Forge (blocked tasks freischalten, 30 Min)
         P2-A → Atlas selbst (Execution Contract verankern, 20 Min)
                    ↓
         P3-A → Forge (Dispatch-Loop, 60-90 Min)
                    ↓
         E2E-Tests 1-4 → Atlas orchestriert
```

**Forge-Opus-Trigger:** Nur wenn Dispatch-Loop-Architektur unklar wird (sessions_spawn API unbekannt)

---

## Definition of Done

- [ ] Alle 8 security-blocked Tasks terminiert
- [x] Execution Contract Template in Atlas working-context.md ← **von Lens erledigt 2026-04-12**
- [ ] Execution Contract Template in HEARTBEAT.md (Forge-Aufgabe, Datei auf Server)
- [ ] worker-monitor.py dispatcht ready Tasks automatisch
- [ ] Testszenario 1 grün (Happy Path autonom, kein manueller Eingriff)
- [ ] Testszenario 2 grün (Fehler → failed, kein draft-Loop)
- [ ] Testszenario 3 grün (Contract-Guard funktioniert)
- [ ] Testszenario 4 grün (Parallelbetrieb ohne Blockierung)
- [ ] worker-monitor.log zeigt mindestens 2 saubere Dispatch-Zyklen
