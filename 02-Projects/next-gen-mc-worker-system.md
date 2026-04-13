# Next Generation Mission Control & Worker System — IST/SOLL-Analyse

> Verfasst: 2026-04-13 | Trigger: "Los starten Next Generation MC / Worker System"
> Basis: Vollständige Session-Analyse nach Lifecycle-Fixing (worker-monitor v5, 15+ Fixes)

---

## TEIL 1 — IST-Analyse (Stand 2026-04-13)

### 1.1 Task Board

| Dimension | IST |
|-----------|-----|
| Storage | Einzelne `tasks.json` (file-based, kein DB) |
| Gesamttasks | 224 (201 done, 18 assigned, 5 canceled) |
| State Machine | 4-dimensional: `status × dispatched × dispatchState × executionState` |
| Normalisierung | `normalizeTaskRecord()` erzwingt kanonische Kombinationen bei jedem Write |
| Transitions | Validiert via `validateBoardTransition` — illegale Moves → HTTP 409 |
| Concurrency | Keine DB-Locks — Race Conditions bei parallelen Schreibzugriffen möglich |
| UI | Next.js App (taskboard, kanban, agents, costs, trends, team, memory, calendar) |

**Schwachstellen:**
- Single-file JSON — bei >500 Tasks träge, bei >2000 Tasks gefährlich
- Kein Audit-Log auf Task-Ebene (nur Vault-Checkpoints)
- EADDRINUSE-Bug: Dev- und Prod-Instanz können auf Port 3000 kollidieren
- TypeScript-Fehler in Trends-Routen (tsc --noEmit schlägt fehl)

---

### 1.2 Worker-Monitor

| Dimension | IST |
|-----------|-----|
| Runtime | Python-Script, 1356 Zeilen, Cron alle 15 Minuten |
| Phasen | reconcile → retry → dispatch → sweep → assigned-timeout → notify → detect |
| Dispatch-Kanal | Gateway chatCompletions (`gateway:18789`) |
| Agent-Fleet | Forge (max 3), Pixel (max 2), Lens (max 1), James (max 1) |
| Orphan-Detection | 30 min (direkt) / 60 min (gateway-prefix) |
| Accepted-Timeout | 10 min — kein accepted-Receipt → auto-fail |
| Atlas-Notify | Pingt Atlas bei assigned Tasks — Atlas dispatcht manuell via PATCH |
| Retry-Logik | recovery-action → direkt `_spawn_specialist()` wenn dispatchTarget bekannt |
| Observability | Discord-Notifications (#execution-reports), Log-File, keine Metriken |

**Schwachstellen:**
- **15-Minuten-Takt ist zu langsam** — neuer Task wartet bis zu 15 min auf ersten Dispatch
- **Atlas ist Dispatch-Flaschenhals** — worker-monitor kann nicht selbst von `assigned` → `in-progress`
- **Event-getrieben fehlt** — kein Webhook/SSE wenn Task erstellt wird
- **Single-Point-of-Failure** — Cron-Ausfall → kein Monitoring, kein Alert
- **Kein Health-Dashboard** — Auslastung, Failure-Rate, MTTR unsichtbar

---

### 1.3 Agent-Fleet

| Agent | Gateway-ID | Modell | Max parallel | Status |
|-------|-----------|--------|-------------|--------|
| Atlas | main | Opus | 1 | Aktiv — Orchestrator |
| Forge | sre-expert | Sonnet | 3 | Aktiv — Code/Infra |
| Forge-Opus | forge-opus | Opus | 1 | Aktiv — Architektur |
| Pixel | frontend-guru | Sonnet | 2 | Aktiv — UI/Frontend |
| Lens | efficiency-auditor | Sonnet | 1 | Aktiv — Kosten/Audit |
| James | researcher | Sonnet | 1 | Aktiv — Research |
| Spark/Flash | spark | Haiku | ? | Geplant — Entlastung |

**Schwachstellen:**
- Kein Heartbeat-Monitoring pro Agent (nur Discord-Ping bei Abschluss)
- Spark/Flash nicht aktiv — repetitive Tasks landen bei Forge/Pixel
- Forge-Opus nur manuell getriggert — kein automatisches Eskalations-Routing
- Kein Cost-Tracking pro Task/Agent in Echtzeit

---

### 1.4 Bekannte offene Defekte (18 Tasks auf Board)

**P0 (sofort):**
- BRAVE_API_KEY + weiterer API-Key im Log geleakt — noch nicht rotiert
- EADDRINUSE / Restart-Storm — Code-Level-Fix fehlt

**P1 (diese Woche):**
- TypeScript-Fehler in Trends/UI
- Atlas Step-8 Trigger-Policy fehlt (Fehlalarm-Risiko)
- Reporting-Ingestion aus Discord nicht deterministisch
- dispatchTask ignoriert agentId-Override im Retry-Pfad
- Timeout-Escalation-Reset in recovery-action unvollständig

**P2/P3:**
- Trend-Dashboard für Costs/Velocity fehlt
- Forge/Pixel Failure-Pattern-Audit ausstehend
- Live-Runtime-Parität nach Pixel-Audit nicht verifiziert

---

## TEIL 2 — SOLL-Analyse: Next Generation MC & Worker System

### Vision

> Ein vollständig autonomes, selbst-heilendes Multi-Agent-System, das ohne manuelle Intervention Aufgaben empfängt, priorisiert, verteilt, überwacht und abschließt — und dabei Kosten, Auslastung und Qualität in Echtzeit transparent macht.

---

### 2.1 Tier 1 — Stabilitätsfundament (Voraussetzung für alles)

**Ziel:** Zero unplanned downtime, TypeScript clean, Security hardened.

| Maßnahme | Owner | Aufwand |
|----------|-------|---------|
| EADDRINUSE systemd-Guard: Port-Konflikt-Schutz in Service-File | Forge | Klein |
| TypeScript vollständig grün (tsc --noEmit) | Pixel | Mittel |
| Alle geleakten API-Keys rotiert + Log-Redaction hardened | Forge | Klein |
| MC Restart-Runbook + Dev-Port-Guardrails dokumentiert | Forge | Klein |
| `/trends` 404 und `/team` React-Error behoben | Pixel | Klein |
| Timeout-Escalation Retry-State vollständig zurückgesetzt | Forge | Klein |
| dispatchTask agentId-Override im Retry-Pfad korrekt | Forge | Klein |

**Definition of Done:** MC läuft ohne manuelle Eingriffe 72h durch, tsc grün, alle P0-Keys rotiert.

---

### 2.2 Tier 2 — Autonomie-Upgrade (Kernziel)

**Ziel:** Atlas braucht keinen manuellen Dispatch mehr. Das System arbeitet selbst.

#### 2.2.1 Worker-Monitor → Event-driven Service

Statt Cron alle 15 min: **dauerhafter Prozess** mit WebSocket/SSE-Verbindung zu MC.

```
MC → SSE-Event: task:created / task:updated
→ worker-monitor reagiert sofort (<1s Latenz)
→ kein 15-min-Warten mehr
```

Fallback: Cron als Watchdog alle 5 min (wenn SSE tot).

**Technisch:**
- `worker-monitor.py` wird zu `worker-monitor-service.py` (asyncio + aiohttp)
- PM2 / systemd-Unit statt Cron
- Health-Endpoint: `GET /worker-monitor/health`

#### 2.2.2 Autonomer Atlas-Dispatch — Direct Dispatch Mode

Aktuell: Atlas muss manuell PATCH senden. Soll: worker-monitor dispatcht direkt.

```
Task status=assigned → worker-monitor prüft:
  1. hasExecutionContract?
  2. dispatchTarget gesetzt?
  3. Agent-Slot frei (concurrency check)?
→ Wenn ja: PATCH direkt (kein Atlas-Zwischenschritt nötig)
→ Atlas nur noch für: neue Tasks erstellen, Prioritäten setzen, Blocking-Entscheidungen
```

**Voraussetzung:** Execution Contract als Pflichtformat bei Task-Erstellung. Atlas entscheidet, wer der Task-Owner ist — Dispatch-Mechanik übernimmt worker-monitor.

#### 2.2.3 Selbst-heilender Retry-Zyklus

Aktuell: failed → worker-monitor retries → Atlas entscheidet erneut.

Soll: **Vollautomatischer Retry ohne Atlas-Intervention:**
```
failed → recovery-action → direct spawn des letzten dispatchTarget
→ maxRetriesReached → automatische Eskalation zu Forge-Opus
→ Forge-Opus analysiert → erstellt Fix-Task → Atlas wird informiert
```

#### 2.2.4 Atlas Step-8 Trigger-Policy (harte Signalschwelle)

Atlas reagiert nur auf:
- `receipt/stage=result` (terminal success)
- `receipt/stage=failed` + `maxRetriesReached=true`
- Explizite Operator-Trigger

Kein Reagieren auf: kurze Session-Sichtlücken, "appears live" Logs, vorzeitige reconcile-Outputs.

---

### 2.3 Tier 3 — Observability & Intelligence

**Ziel:** Vollständige Sichtbarkeit auf alle relevanten Metriken.

#### 2.3.1 Live-Metriken-Dashboard

Neue MC-Seite `/dashboard` (oder Erweiterung bestehend):

| Metrik | Quelle |
|--------|--------|
| Tasks/Stunde (Throughput) | tasks.json + timestamps |
| Agent-Utilization % | in-progress / max per agent |
| MTTR (Mean Time to Resolution) | createdAt → doneAt |
| Failure-Rate pro Agent | failed / total |
| Cost/Task | model-usage × token-preise |
| Swap/RAM live | system-monitor API |
| Cron-Health | letzter erfolgreicher worker-monitor Lauf |

#### 2.3.2 Trend-Dashboard (Costs + Velocity)

Task `de16016f` bereits auf Board:
- 7-Tage / 30-Tage Ansicht
- Kosten-Trend pro Agent/Tag
- Task-Velocity (geschlossen/Tag)
- Agent-Auslastung über Zeit

#### 2.3.3 Atlas Reporting-Ingestion (deterministisch)

Discord `#execution-reports` → strukturierter Ingest:
```
Execution-Report empfangen
→ parse: taskId, agent, resultSummary, findings[]
→ für jedes finding: automatisch Task-Entwurf erstellen
→ Atlas reviewed + dispatcht
```

Idempotenz: Dupe-Guard via Message-ID.

---

### 2.4 Tier 4 — Scale & Intelligence (Langfrist)

| Feature | Beschreibung |
|---------|-------------|
| **Spark/Flash aktiv** | Haiku-basierter Entlastungsagent für repetitive Tasks (Textformatierung, Klassifizierung, einfache Transforms) |
| **Multi-Model-Routing** | Automatische Modellwahl: Haiku für simple Tasks, Sonnet für Standard, Opus nur für Architektur/Blockade |
| **Semantisches Task-Memory** | Agents greifen auf Ergebnisse vergangener ähnlicher Tasks zu — kein Doppel-Research |
| **Predictive Concurrency** | Atlas schätzt Task-Dauer anhand historischer Daten und plant Slots voraus |
| **Backlog-Autonomie** | Atlas generiert selbst neue Tasks aus System-Health-Daten wenn Backlog leer ist |
| **Self-Improving Prompts** | Prompt-Qualität wird anhand von Failure-Rates gemessen und automatisch verbessert |

---

## TEIL 3 — Roadmap

### Phase 1 — Stabilisierung (Sofort, laufend)
Alle 18 Board-Tasks abarbeiten. Ende: Zero P0/P1 Defekte, tsc grün, Security clean.

```
Trigger: System stabilisiert → Atlas dispatcht aktuelle 18 Tasks
Dauer: ~1-2 Wochen (autonom)
```

### Phase 2 — Autonomie-Upgrade (nach Phase 1)
Tier 2 Maßnahmen. Worker-Monitor-Service, Direct-Dispatch, Step-8 Policy.

```
Trigger: "Los starten Next Generation MC / Worker System"
Tasks: ~5-7 Forge-Tasks + 1-2 Pixel-Tasks
Dauer: ~1 Woche
```

### Phase 3 — Observability (parallel zu Phase 2)
Tier 3: Metriken-Dashboard, Trend-Dashboard, Reporting-Ingestion.

```
Tasks: 2-3 Pixel-Tasks (Dashboard), 1 Forge-Task (Ingest-Pipeline)
Dauer: ~1 Woche
```

### Phase 4 — Scale & Intelligence (nach Phase 2+3)
Tier 4: Spark aktivieren, Multi-Model-Routing, Semantisches Memory.

```
Trigger: Phases 2+3 vollständig deployed und 72h stabil
Dauer: laufend / iterativ
```

---

## TEIL 4 — Trigger-Wort für Atlas

Wenn Lenard sagt:

> **"Los starten Next Generation MC / Worker System"**

Dann erstellt Atlas sofort folgende Tasks (in dieser Reihenfolge):

**Phase 2 — Worker-Monitor-Service:**
1. `[P0][NextGen] worker-monitor-service.py: asyncio + SSE statt Cron` → Forge
2. `[P0][NextGen] Direct-Dispatch: worker-monitor dispatcht assigned→in-progress ohne Atlas` → Forge
3. `[P1][NextGen] Atlas Step-8 Trigger-Policy: harte Signalschwelle implementieren` → Forge
4. `[P1][NextGen] Reporting-Ingestion: Discord→Task deterministisch mit Dupe-Guard` → Forge
5. `[P1][NextGen] Autonomer Retry: maxRetriesReached → Forge-Opus-Eskalation` → Forge

**Phase 3 — Observability:**
6. `[P1][NextGen] Live-Metriken-Dashboard: Throughput, MTTR, Failure-Rate, Utilization` → Pixel
7. `[P1][NextGen] Trend-Dashboard: Costs/Velocity 7d/30d` → Lens (T6 bereits auf Board)
8. `[P2][NextGen] Spark/Flash aktivieren und in Fleet integrieren` → Forge

**Alle Tasks mit vollständigem Execution Contract dispatchen — Concurrency-Limits beachten.**

---

## Anhang — Relevante Referenzen

- [[../03-Agents/Shared/task-lifecycle-canon]] — vollständige Lifecycle-Referenz
- [[../03-Agents/Atlas/working-context]] — Atlas Dispatch-Protokoll
- [[../04-Operations/Audits/system-audit-playbook]] — Audit-Playbook
- worker-monitor.py: `/home/piet/.openclaw/workspace/scripts/worker-monitor.py`
- MC Source: `/home/piet/.openclaw/workspace/mission-control/src/`
