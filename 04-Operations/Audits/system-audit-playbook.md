# System Audit Playbook

**Trigger:** Atlas erhält "mach System Audit" oder "System Audit starten"  
**Rhythmus:** Alle 2–3 Tage empfohlen  
**Dauer:** Phase 1 läuft parallel (~20–30 min), Phase 2–3 folgen automatisch via E2E-Loop

---

## Übersicht

```
Phase 1 — Parallel Audit (alle 4 Agenten gleichzeitig)
  Forge   → System Health, MC-Code, Cron-Fehler
  Lens    → Kosten, Effizienz, Redundanzen
  James   → Technologie, Modelle, externe Änderungen
  Pixel   → MC UI, Dashboard, UX

Phase 2 — Atlas wertet aus (nach Completion-Ping)
  → Kritische Findings → Fix-Tasks erstellen
  → Low-prio → in learnings.md eintragen

Phase 3 — Fix-Sprint (automatisch via worker-monitor)
  Forge/Pixel implementieren Fixes
  Receipt → Discord Report → Atlas-Ping

Phase 4 — Optional: Validation
  Forge prüft ob kritische Fixes live sind
```

---

## Atlas: So startest du einen System Audit

### Schritt 1 — Phase 1 Tasks erstellen und dispatchen

Erstelle genau diese 4 Tasks via `POST http://127.0.0.1:3000/api/tasks` und dispatche sie sofort.

---

#### Task A — Forge: System Health & Code Quality

```json
{
  "title": "[Audit] System Health & Code Quality",
  "assigned_agent": "sre-expert",
  "dispatchTarget": "sre-expert",
  "priority": "high",
  "tags": ["audit", "system-audit"],
  "description": "task id: (nach Erstellung eintragen)\nobjective: Führe einen vollständigen System-Health-Check durch. Prüfe:\n1. Mission Control Logs letzte 7 Tage — Errors, Warnings, 5xx-Responses\n2. TypeScript: cd /home/piet/.openclaw/workspace/mission-control && npx tsc --noEmit — alle Fehler dokumentieren\n3. Cron-Jobs mit consecutiveErrors > 0 aus GET /api/cron/jobs\n4. API-Routen ohne Error-Handler (grep in src/app/api/)\n5. Systemressourcen: Disk (df -h), RAM (free -h), laufende Services (systemctl --user list-units)\n6. worker-monitor.log letzte 50 Zeilen — Anomalien identifizieren\ndefinition of done: Strukturierter Bericht mit allen Findings, priorisiert nach Kritikalität. Kritische Findings klar markiert.\nreturn format: POST http://127.0.0.1:3000/api/tasks/{task_id}/receipt\nHeaders: x-actor-kind: automation, x-request-class: system\nBody: {\"stage\":\"result\",\"resultSummary\":\"<1 Satz Gesamtbefund>\",\"resultDetails\":\"## Kritische Findings\\n<Liste>\\n## Mittlere Findings\\n<Liste>\\n## Empfehlungen\\n<priorisiert>\\n## Offene Punkte\\n<was unklar blieb>\"}"
}
```

---

#### Task B — Lens: Kosten & Effizienz

```json
{
  "title": "[Audit] Kosteneffizienz & Redundanzcheck",
  "assigned_agent": "efficiency-auditor",
  "dispatchTarget": "efficiency-auditor",
  "priority": "high",
  "tags": ["audit", "system-audit"],
  "description": "task id: (nach Erstellung eintragen)\nobjective: Analysiere Kosten und Effizienz der letzten 7 Tage. Prüfe:\n1. GET /api/tasks mit status=done — Kosten pro Agent schätzen (Basis: Model × Token-Schätzung)\n2. Failure-Rate pro Agent: failed / (done + failed)\n3. Retry-Patterns: Tasks mit retryCount > 1 — was sind die Ursachen?\n4. Cron-Jobs: Welche laufen zu oft, zu lang oder sind redundant?\n5. Modell-Effizienz: Werden teure Modelle für simple Tasks genutzt?\n6. Überlappende Jobs: Gibt es Jobs die dasselbe tun (z.B. dispatch-router vs worker-monitor)?\ndefinition of done: Bericht mit konkretem Einsparungspotenzial in % und 3–5 priorisierten Empfehlungen.\nreturn format: POST http://127.0.0.1:3000/api/tasks/{task_id}/receipt\nHeaders: x-actor-kind: automation, x-request-class: system\nBody: {\"stage\":\"result\",\"resultSummary\":\"<1 Satz: Hauptfinding>\",\"resultDetails\":\"## Kostenanalyse\\n<Aufschlüsselung>\\n## Ineffizienzen\\n<priorisiert>\\n## Empfehlungen\\n<konkret, umsetzbar>\\n## Offene Punkte\\n<was fehlt zur vollständigen Analyse>\"}"
}
```

---

#### Task C — James: Technologie & Modell-Research

```json
{
  "title": "[Audit] Technologie & Modell-Research",
  "assigned_agent": "researcher",
  "dispatchTarget": "researcher",
  "priority": "medium",
  "tags": ["audit", "system-audit"],
  "description": "task id: (nach Erstellung eintragen)\nobjective: Recherchiere aktuelle Entwicklungen die unser System betreffen. Prüfe:\n1. Gibt es neuere oder günstigere Modelle für unsere Agent-Profile (Atlas/main, Forge/sre-expert, Lens/efficiency-auditor, Pixel/frontend-guru, James/researcher)?\n2. OpenClaw: Gibt es neue Features oder Breaking Changes im Changelog?\n3. Claude API / Anthropic: Neue Modelle, Features, Preisänderungen?\n4. Gibt es bekannte Probleme mit unseren aktuell genutzten Modellen?\n5. Best Practices für autonome Agenten-Systeme — was machen andere anders/besser?\ndefinition of done: Research-Summary mit konkreten, umsetzbaren Empfehlungen. Jede Empfehlung mit Begründung.\nreturn format: POST http://127.0.0.1:3000/api/tasks/{task_id}/receipt\nHeaders: x-actor-kind: automation, x-request-class: system\nBody: {\"stage\":\"result\",\"resultSummary\":\"<1 Satz: wichtigstes Finding>\",\"resultDetails\":\"## Modell-Empfehlungen\\n<pro Agent>\\n## Neue Features / Breaking Changes\\n<relevant für uns>\\n## Best Practices\\n<was wir übernehmen sollten>\\n## Offene Punkte\\n<was nicht recherchiert werden konnte>\"}"
}
```

---

#### Task D — Pixel: MC UI & Dashboard Audit

```json
{
  "title": "[Audit] Mission Control UI & UX",
  "assigned_agent": "frontend-guru",
  "dispatchTarget": "frontend-guru",
  "priority": "medium",
  "tags": ["audit", "system-audit"],
  "description": "task id: (nach Erstellung eintragen)\nobjective: Auditiere das Mission Control Dashboard auf UI-Probleme und Verbesserungspotenzial. Prüfe:\n1. Öffne MC auf http://127.0.0.1:3000 — alle Hauptseiten laden ohne Fehler?\n2. Task-Board: Stimmen Status-Anzeigen, Agenten-Namen, Priorities mit der API überein?\n3. Gibt es Console-Errors im Browser? (Dev Tools)\n4. Fehlende Features: Was würde den täglichen Workflow für Atlas/Lenard verbessern?\n5. Responsive: Funktioniert das Dashboard auf kleinen Viewports?\n6. Performance: Gibt es auffällig langsame Komponenten oder API-Calls?\ndefinition of done: Liste aller gefundenen Issues mit Schweregrad. Mindestens 3 Verbesserungsvorschläge.\nreturn format: POST http://127.0.0.1:3000/api/tasks/{task_id}/receipt\nHeaders: x-actor-kind: automation, x-request-class: system\nBody: {\"stage\":\"result\",\"resultSummary\":\"<1 Satz Gesamteindruck>\",\"resultDetails\":\"## Kritische UI-Bugs\\n<Liste>\\n## UX-Verbesserungen\\n<priorisiert>\\n## Feature-Requests\\n<mit Begründung>\\n## Offene Punkte\\n<was nicht geprüft werden konnte>\"}"
}
```

---

### Schritt 2 — Alle 4 Tasks dispatchen

Nach Erstellung jedes Tasks sofort dispatchen:

```
PATCH http://127.0.0.1:3000/api/tasks/{task_id}
Headers: x-actor-kind: automation, x-request-class: write
Body: {"dispatched": true, "dispatchState": "dispatched", "lastExecutionEvent": "dispatch"}
```

worker-monitor übernimmt das Spawnen der Agenten — kein manuelles Session-Starten.

---

### Schritt 3 — Board-Hygiene (Atlas selbst, sofort)

Während Phase 1 läuft, erledige Atlas-interne Board-Hygiene:

1. `GET /api/tasks?status=in-progress` — Tasks mit lastActivityAt > 24h ohne Bewegung → auf `assigned` zurücksetzen
2. `GET /api/tasks?status=draft` — Tasks älter als 7 Tage → entweder dispatchen oder canceln
3. `GET /api/tasks?status=failed` — failed Tasks mit klarer Ursache → Recovery-Task erstellen wenn sinnvoll
4. Dokumentiere Muster in `POST /api/learnings` (Kategorie: board-hygiene)

---

## Phase 2 — Atlas wertet Findings aus (nach Completion-Ping)

Wenn alle 4 Audit-Tasks abgeschlossen sind, erhältst du einen Completion-Ping von worker-monitor.

**Vorgehen:**

Für jedes Finding aus den resultDetails:

| Schweregrad | Aktion |
|-------------|--------|
| Kritisch (System down risk, Datenverlust, >$5/Tag Kosten) | Sofort Fix-Task erstellen → Forge dispatchen |
| Mittel (Fehler, UX-Bug, Ineffizienz) | Fix-Task erstellen → Forge/Pixel dispatchen |
| Niedrig (Verbesserung, Nice-to-have) | Eintrag in `POST /api/learnings` |
| Research-Finding (neues Modell, neue Feature) | Draft-Task erstellen für spätere Entscheidung |

**Fix-Task Execution Contract Template:**

```
task id: (nach Erstellung)
objective: <konkreter Fix basierend auf Audit-Finding — was genau zu tun ist>
definition of done: <messbar — tsc grün / UI-Element funktioniert / Kosten gesunken um X%>
return format: POST /api/tasks/{task_id}/receipt mit resultDetails (## Was implementiert / ## Validierung / ## Impact)
```

**Safety-Grenzen bleiben bestehen** — kein Fix der >3 Dateien anfasst, keine Schema-Migrationen, keine openclaw.json-Änderungen ohne Rückfrage.

---

## Phase 3 — Fix-Sprint (automatisch)

worker-monitor dispatcht die Fix-Tasks automatisch. Forge/Pixel:
- Implementieren
- Validieren (`npx tsc --noEmit` muss grün sein)
- Posten Receipt → Discord-Report + Thread mit Details

Du erhältst für jeden Fix einen Discord-Report in #execution-reports.

---

## Phase 4 — Abschluss-Validation (optional, bei kritischen Fixes)

Falls kritische Fixes deployed wurden, erstelle einen abschließenden Forge-Task:

```json
{
  "title": "[Audit-Validation] Post-Fix Health Check",
  "assigned_agent": "sre-expert",
  "description": "task id: (nach Erstellung)\nobjective: Prüfe ob die im letzten System-Audit deployten kritischen Fixes live und stabil sind. Führe aus: npx tsc --noEmit, prüfe MC auf Errors, verifiziere die spezifischen Änderungen.\ndefinition of done: Alle kritischen Fixes sind live, keine neuen Fehler eingeführt.\nreturn format: POST /api/tasks/{id}/receipt mit resultDetails (## Validierungsergebnis / ## Verbleibende Risiken / ## Empfehlung)"
}
```

---

## Audit-Log

Nach Abschluss jedes Audit-Zyklus eintragen:

Datei: `/home/piet/.openclaw/workspace/memory/system-audits.md`

```markdown
## YYYY-MM-DD — System Audit

### Phase 1 Findings
- Forge: <Kernfinding>
- Lens: <Kernfinding>
- James: <Kernfinding>
- Pixel: <Kernfinding>

### Phase 2 Fix-Tasks erstellt
- [Task-ID] <Titel> → <Agent>
- ...

### Phase 3 Status
- <Anzahl> Fixes deployed, <Anzahl> pending

### Impact
<Was ist jetzt besser als vor dem Audit>
```

---

## Hinweise für Atlas

- Alle 4 Phase-1-Tasks **gleichzeitig dispatchen** — sie laufen parallel
- Nicht auf Phase 1 warten bevor du Board-Hygiene machst (Schritt 3 läuft sofort)
- Completion-Ping kommt automatisch von worker-monitor — kein manuelles Prüfen
- Bei unklaren Findings: Forge-Opus für Root-Cause-Analyse einsetzen (nicht Forge)
- Modelle werden durch agent_default/openclaw-Routing aufgelöst — nicht manuell setzen
