---
title: Stabilization Sprint 2026-04-18 — System-Gaps nach 1-Tag-Autonomie
version: 1.0
status: in-execution
owner: Operator + Atlas
created: 2026-04-18
---

# Stabilization Sprint 2026-04-18

Kurzer, fokussierter Fix-Sprint für 6 Schwachstellen die aus einem Tag Multi-Agent-Autonomie-Betrieb sichtbar geworden sind. Keine Feature-Packs, reines Tightening.

## Executive Judgment

Nach zwei intensiven Arbeitstagen mit Multi-Agent-Orchestrierung ist das System **operativ**, aber sechs **systemische Lücken** blockieren den Schritt von "funktioniert wenn man aufpasst" zu "läuft sauber autonom". Alle Fixes sind klein (15min–4h), reversibel und orthogonal. Keine neuen Features, reine Stabilisierung.

## Root-Cause-Cluster

- **Task-Lifecycle-Terminierung unscharf**: `worker-monitor` orphan-kill setzt kein `resolvedAt` → Health bleibt degraded → Self-Optimizer-Fehlalarme.
- **Agent-Cold-Start-Latenz unberücksichtigt**: James/Spark brauchen 30+min Bootstrap, Monitoring kennt das nicht → Orphan-Kill innerhalb Bootstrap-Fenster.
- **Atlas ohne Board-Awareness**: Tasks werden angelegt ohne GET-Scan auf existierende gleichnamige.
- **UI-Qualitätsgate fehlt**: Pixel deployt ohne automated Smoke-Test.
- **Health + Anomaly-Metrik entkoppelt**: "ok"-Status trotz 4 critical Anomalien unterdrückt legitime Alarme.
- **Atlas ohne Concurrency-Awareness**: Heartbeat triggert neue Tasks, auch wenn Agent X schon lange aktiv ist.

## Target Model

- **Alle terminalen Tasks haben `resolvedAt`** (failed + resolvedAt → Closed im Health-Zähler).
- **Agent-Bootstrap-Toleranzen differenziert** (James/Spark: 30min, Forge/Pixel: 15min).
- **Atlas macht Pre-POST-Board-Scan** und fired nicht blind.
- **UI-Packs haben Playwright-Smoke** als DoD-Pflicht.
- **Health-Status inkludiert Anomaly-Count** (ok nur wenn Anomalien=0 critical).
- **Atlas-Heartbeat respektiert `inProgress_by_agent`** — kein neuer Task wenn Agent X noch aktiv.

## Implementation Pack (6 Fixes, Reihenfolge priorisiert)

### Fix P0-1 — worker-monitor setzt `resolvedAt` beim Orphan-Kill
- **Lead**: Forge
- **File**: `/home/piet/.openclaw/workspace/scripts/worker-monitor.py`
- **Change**: In der `fail_orphan_task`-Funktion (bzw. wo `status=failed` gesetzt wird) zusätzlich `resolvedAt=now()` patchen via API.
- **DoD**: Simulierter Orphan-Task wird gekillt, GET zeigt `resolvedAt != null`, Health bleibt `ok`.
- **Aufwand**: 15min
- **Backup**: `.bak-sp-p01-2026-04-18`

### Fix P1-3 — Atlas Board-Scan-Regel in AGENTS.md
- **Lead**: Atlas (Self)
- **File**: `/home/piet/.openclaw/workspace/AGENTS.md` § Verify-After-Write (neue Unter-Regel)
- **Change**: Neue Zeile: "Vor `POST /api/tasks`: `GET /api/tasks?status=<pending-pickup,in-progress>` + Title-Substring-Match. Bei Match → abort + Kommentar, nicht neuen Task."
- **DoD**: Regel-Text in AGENTS.md ergänzt, Atlas quittiert Lektüre via Self-Task.
- **Aufwand**: 20min

### Fix P0-2 — MCP-Cold-Start-Audit (James-Pattern)
- **Lead**: Forge + James
- **File**: Neues Analyse-Skript + `ACCEPTED_TIMEOUT_MINUTES` pro Agent differenziert in `worker-monitor.py`
- **Change**:
  1. Forge schreibt Audit-Skript das misst: `openclaw agent --agent X --message "ping"` Dauer bis erster Output pro Agent (James, Spark, Lens, Forge, Pixel, Atlas)
  2. Basierend auf Baseline: `AGENT_TIMEOUT_MINUTES = {james: 30, spark: 25, default: 15}` in worker-monitor.py
- **DoD**: Audit-Report, worker-monitor nutzt differenzierte Timeouts, Smoke-Test James-Retry mit neuem Timeout endet in-progress ohne Orphan-Kill.
- **Aufwand**: 2h

### Fix P2-5 — Health-Status inkludiert Anomaly-Count
- **Lead**: Forge
- **File**: `mission-control/src/lib/operational-health.ts`
- **Change**: `status` wird `degraded` wenn `/api/costs/anomalies` `count > 0` mit `tone=critical`. Logik: `ok` nur bei keine open-failed + keine critical-anomalies + recoveryLoad=0.
- **DoD**: Aktuell 4 critical Anomalien → Health `degraded`. Nach Acknowledge → `ok`.
- **Aufwand**: 30min

### Fix P2-6 — Atlas Sleep-Mode bei aktivem Agent
- **Lead**: Atlas (Self)
- **File**: `/home/piet/.openclaw/workspace/AGENTS.md` § Heartbeat-Regel
- **Change**: Neue Zeile: "Vor Task-Anlage für Agent X: `GET /api/tasks?assigned_agent=X&status=in-progress` — wenn >0 → skip diesen Pack-Kandidaten, nächster Agent. Nur Tasks anlegen für Agents mit 0 active."
- **DoD**: Regel in AGENTS.md. Heartbeat-Lauf mit aktivem Pixel-Task triggert keinen neuen Pixel-Task.
- **Aufwand**: 20min

### Fix P1-4 — Playwright-UI-Smoke-Test-Framework
- **Lead**: Pixel + Forge
- **File**: Neue `mission-control/tests/ui-smoke/*.spec.ts` + `playwright.config.ts`
- **Change**: Playwright setup, 3 Smoke-Tests (Overview lädt, Costs-Tab lädt, Task-Klick öffnet Detail), GitHub-Actions-Runner-unabhängig (direkt via `npm run test:smoke`).
- **DoD**: 3 Specs grün, als DoD-Pflicht für alle zukünftigen UI-Packs in AGENTS.md gelistet.
- **Aufwand**: 4h

## Files / Components

| Fix | Lead | Primary Files |
|---|---|---|
| P0-1 | Forge | `worker-monitor.py` |
| P0-2 | Forge + James | `worker-monitor.py` + neuer `agent-bootstrap-audit.sh` |
| P1-3 | Atlas | `AGENTS.md` |
| P1-4 | Pixel + Forge | `tests/ui-smoke/*.spec.ts`, `playwright.config.ts` |
| P2-5 | Forge | `src/lib/operational-health.ts` |
| P2-6 | Atlas | `AGENTS.md` |

## Test Plan

Pro Fix integriert. Gesamt-Regression:
- Smoke-Suite weiter 10/10
- Self-Optimizer Dry-Run bleibt ohne False-Positives
- Orphan-Kill + Retry-Zyklus einmal e2e gespielt

## Rollback

Pro Fix ein `.bak-sp-p0X-2026-04-18`. AGENTS.md-Text-Änderungen revertibel via git diff. Keine Schema-Migrationen, keine destructive Ops.

## Recommended Execution Order

**Phase A (schnelle Wins, parallel möglich)** — ~1h
- P0-1 Forge (15min)
- P1-3 Atlas-Self (20min)
- P2-5 Forge (30min)
- P2-6 Atlas-Self (20min)

**Phase B (tieferes Tiefeninvest)** — ~6h
- P0-2 MCP-Cold-Start-Audit (2h)
- P1-4 Playwright-Framework (4h)

## Acceptance Criteria

1. Simulierter Orphan-Kill → Health bleibt `ok`
2. Atlas-Heartbeat erzeugt 0 Duplikat-Tasks in 3 aufeinanderfolgenden Heartbeats
3. James-Retry nach neuen Timeouts → in-progress ohne Orphan-Kill
4. 4 critical Anomalien → Health `degraded` (nicht `ok`)
5. Atlas triggert keinen Pixel-Task wenn Pixel bereits in-progress
6. 3 Playwright-Smoke-Specs grün, CI-fähig
