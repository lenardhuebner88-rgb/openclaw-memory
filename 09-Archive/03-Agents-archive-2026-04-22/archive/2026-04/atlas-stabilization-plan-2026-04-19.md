---
title: Mission-Control Stabilization-Plan 2026-04-19 Morgen
date: 2026-04-19 09:00 UTC geplant
author: Operator (pieter_pan) nach ~4h Multi-Agent-Stress-Test 2026-04-18
status: ready-for-execution
owner: Operator + Atlas-Orchestrator
priority: P0 (vor allen neuen Features)
---

# Stabilization-Plan 2026-04-19 — Sauber & Nachhaltig

## Warum dieser Plan
Gestern-Abend 4h Multi-Agent-Betrieb hat 6 systemische Schwächen offengelegt. Bevor neue Features gebaut werden, müssen die fundamentalen State-Management + Build-Gate Lücken geschlossen werden. Sonst wiederholen sich heutige Incidents.

## Sechs Learnings aus 2026-04-18 Abend

### L1 — Root-Cause-Fix-Timing
Fix in Dispatch-Pipeline wirkt nur auf NEUE POSTs nach Fix-Deploy. Legacy-Tasks mit pre-fix-Dispatch sind verloren. Gateway cached interne Session-State.

**Regel R27 neu:** Nach Root-Cause-Fix in Dispatch-Pipeline müssen alle pre-fix offenen Tasks entweder (a) canceled + neu POSTed ODER (b) explizit mit state-reset-Migration updated werden. Nur der Fix selbst reicht nicht.

### L2 — Konkurrierende Mutation-Channels
5+ Entities (Operator, Atlas, Auto-Pickup, Worker-Monitor, Retry-Logic) ändern Task-State ohne Koordination. PATCH-Intentionen werden überschrieben.

**Neu: Operator-Lock-Mechanismus:** Task-Feld `operatorLock: boolean` + `lockedUntil: ISO-timestamp`. Wenn gesetzt: Auto-Pickup, Worker-Monitor, Retry-Logic ignorieren Task bis Lock abgelaufen oder released.

### L3 — Build-Gates fehlen
Forge-Tasks können Type/Lint-Errors in Production mergen. Heute: `node:fs` in client-reachable Modul → MC 10min offline.

**Neu: Pre-Merge Build-Gate:**
1. `npm run typecheck` muss grün sein vor `deploy.sh`
2. `server-only`-Import-Check für Files die von Client-Components importiert werden
3. Feedback-Regel R26: "Wenn du `node:*` importierst, muss File entweder `import 'server-only';` haben ODER darf nicht von Client-Components importiert werden"

### L4 — `blocked`-State nicht stabil
Retry-Mechanismus reaktiviert blocked→in-progress. Operator-Intent wird nicht respektiert.

**Fix:** Retry-Logic prüft `operatorLock` (siehe L2). `blocked`+`operatorLock=true` = final bis Operator release.

### L5 — Build-Storm WK-19 unvalidiert
Debounce-Wrapper deployed, aber nicht verifyiert in Produktion. 8× MC-Downtime gestern bestätigt Problem.

**Action:** E2E-Test der Debounce-Wrapper-Kette. Falls Agents noch deploy.sh-direct aufrufen, Prompts anpassen.

### L6 — Timing-Glück als Sicherheit
Einzelne Legacy-Tasks gingen durch Worker-Monitor bevor er zuschlug. Nicht reproduzierbar, nicht verlässlich.

**Fix:** Hart deprecaten: "Legacy-Task retry ohne re-POST ist unzuverlässig — gilt als lost."

## Phasen-Plan 2026-04-19 (09:00-13:30 UTC)

### Phase 1 — Cleanup (09:00-09:30, 30min)
- 8 offene Tasks auf Board durchgehen
- Blocked/failed finalisieren (nicht mehr retrien)
- 4 Legacy-Naming-Tasks canceln: 91264b66 P1-A, 054bc0b6 P1-C, 4f6077cd P2-A, ba8c545a/28d81ae4 Spark-UX
- 1 blocked task releasen: f6d9a2f7 Prompt-Cache-Opt → neu POSTen nach Fix-Validation
- Board: nur noch d566c172 Retry-Smoke + echte incidents

### Phase 2 — Operator-Lock-Feature (09:30-10:30, 60min)
**Neuer Task an Forge:**
- `task.operatorLock: boolean` + `task.lockedUntil?: string` in Schema
- `auto-pickup.py` prüft `operatorLock` und skipped
- `worker-monitor.py` prüft `operatorLock` bei ghost-check und skipped
- Task-POST-Handler akzeptiert beide Felder in PATCH-Body
- Acceptance: PATCH `operatorLock=true` → Task bleibt stable 15min ohne State-Change von Automatik

### Phase 3 — Build-Gate (10:30-11:30, 60min)
**Neuer Task an Forge:**
- `deploy.sh`/`deploy-actual.sh` führt `npm run typecheck` VOR build
- Typecheck fail → deploy abort, lock release, log
- `server-only`-Lint-Rule einführen (eslint-plugin-server-only oder manuell grep pre-commit)
- Acceptance: absichtlicher `node:fs`-Import in client-reachable File → Build abort mit klarem Error

### Phase 4 — task-assignees.ts Clean Refactor (11:30-12:00, 30min)
**Neuer Task an Forge:**
- Aktuell: Hotfix entfernt Config-Loader, nur Defaults
- Clean: `src/lib/task-assignees.ts` (client-safe, nur Constants + Pure Functions)
- Neu: `src/lib/task-assignees-config.server.ts` mit `'server-only'` (lädt openclaw.json)
- Server-side nutzt config-reader, Client bleibt auf Defaults
- Acceptance: P2-C openclaw.json displayName funktioniert wieder, Build grün

### Phase 5 — Naming-Tasks produktiv re-POSTen (12:00-12:45, 45min)
**Atlas + Forge:**
- 4 Legacy-Tasks als frische POSTs neu anlegen (bekommen via task-dispatch.ts:191 jetzt korrekt workerLabel)
- Sequenziell dispatchen (nicht parallel) damit jeder einzeln verifyt wird
- Nach jedem: check `WORKER:`-Feld im Report = Runtime-ID (nicht Alias)
- Acceptance: alle 4 ohne Ghost-Fail durch

### Phase 6 — Kosten-Routing (12:45-13:30, 45min)
**Forge:**
- Neuen Profile `openrouter/deepseek-v3.2` in openclaw.json
- Test-Dispatch 1 Forge-Task mit `dispatchTarget: deepseek-v3.2` 
- Qualität prüfen: 1 typischer Code-Task (z.B. "modify X in Y" ähnlich Naming-P1-A)
- Wenn OK: Forge-Default auf DeepSeek umstellen, GPT-5.4 als Fallback
- Lens auf MiniMax M2 (nicht M2.7) flippen
- Acceptance: Budget-Anomaly sinkt von 135% unter 90% innerhalb 24h

## Regel-Additions für `feedback_system_rules.md`

### R26 — Server-Only Import-Disziplin
Wenn Modul `node:*`/`fs`/`path` importiert: 
- `import 'server-only';` als erste Zeile ODER 
- Nicht von Client-Components importiert werden
Verletzung = Build-Breaker (siehe 2026-04-18 Forge P2-B node:fs Incident).

### R27 — Legacy-Task nach Root-Cause-Fix
Tasks die vor Dispatch-Pipeline-Fix in in-progress/pending-pickup dispatched wurden, können nicht retrofitted werden. PATCH/File-Edit auf workerLabel etc. ändert Gateway-State nicht. Policy: cancel + re-POST.

### R28 — Operator-Lock-Respekt
Automatik-Entities (Auto-Pickup, Worker-Monitor, Retry-Logic, Atlas-Heartbeat) respektieren `operatorLock=true` und skipped die Task. Lock-Ownership beim Operator, Release nur via expliziten PATCH.

## Acceptance (Gesamt-Plan)

Nach Phase 6:
- ☐ 0 ghost-failed Tasks auf Board
- ☐ Build-Gate fängt mindestens 1 absichtlich-falschen Import ab
- ☐ Operator-Lock PATCH bleibt 15min stabil
- ☐ `/pipeline` redirect works, Pipeline-Tab v3 Screenshot zeigt aktuelle Tasks korrekt
- ☐ Forge auf DeepSeek läuft mit akzeptabler Qualität (1 Test-Task)
- ☐ Budget-Anomaly sinkt unter 100% (24h-Monitoring)

## Risiken + Mitigation

| Risiko | Mitigation |
|---|---|
| Operator-Lock zu aggressiv blockiert legitimate Retries | Default `lockedUntil = now + 15min` (auto-expiry) |
| Build-Gate verzögert Deploys um 30s | Typecheck ist inkrementell, worst-case <30s — akzeptabel |
| DeepSeek-Qualität reicht nicht für Forge-Tasks | Fallback auf GPT-5.4 bei 2 Retry-Fails |
| node:fs-Detection false-positives | Whitelist `src/app/api/**` und `src/lib/**.server.ts` |

## ATLAS HANDOFF

### Reihenfolge
Phase 1 (Operator-Clean) → Phase 2+3 parallel (Lock + Build-Gate) → Phase 4 (Refactor) → Phase 5 (re-POST) → Phase 6 (Routing).

### Task-Split für Atlas
Atlas legt pro Phase einen Task an, nicht alles zusammen. Jeder Task hat klaren Scope + Acceptance.

### Prerequisites
- Build-Storm reduzieren: min. 10min zwischen Phase-Merges
- Monitoring: `mc-critical-alert.py` Cron aktiv (seit gestern live)

### Retrieval Summary
Dieser Plan parkt in Vault `/home/piet/vault/03-Agents/atlas-stabilization-plan-2026-04-19.md`. Trigger: "Lade Stabilization-Plan 2026-04-19 und starte Phase 1."

## Nicht-in-Scope für morgen
Werden später addressiert:
- Pipeline-Tab-Plan-v3 Phase 2/3 (Step-DAG, SSE) — nach Stabilization
- Task-Tab v2 Sub-Plan C (Mobile-Polish) — nach Stabilization
- Cost-Anomaly deep-dive
- Gateway-Source-Fix (worker:atlas-Prefix) — externes Issue
