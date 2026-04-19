---
title: Remaining-Plan Mission-Control 2026-04-19 — Autonomer Atlas-Run
date: 2026-04-19 10:28 UTC
author: Operator (pieter_pan) direkt
scope: Verbleibende Sprints nach Stabilization-Close + Sprint-1
status: Atlas-autonom (Operator monitort nur)
---

# Remaining-Plan — Post Sprint-1

## Kontext

**Sprint-1 Kosten-Routing ist `no-go-close`.**
Output: DeepSeek-v3.2 ist als Provider im `openclaw.json` eingetragen (steht als Fallback-Option bereit), aber der Default-Flip wurde verworfen. Begruendung: Forge-Qualitaets-Review ergab 1-2/5 Scores + Spec-Fehler (MiniMax-M2 existiert nicht, nur M2.7).

Empirische Nebenerkenntnisse aus Sprint-1 Live-Run (10:19-10:23 UTC):
- **FIND-A Dispatch-Target-Routing-Bug:** `dispatchTarget=deepseek-v3.2` wird akzeptiert, aber Runtime-Worker resolvt zu `main` statt zum externen DeepSeek-Provider. Routing-Fehler zwischen MC API und Gateway-Spawn.
- **FIND-B Gateway-Restart-Race:** Worker-Monitor hat Forge ghost-gefailed (10:20) waehrend Forge legitim einen `openclaw agent`-CLI-Spawn fuer den Test-Dispatch gemacht hat. Gateway-Restart waehrend Forge-Run hat den Race getriggert.

## Queue-Zustand

| Sprint | Task-ID | Status | Scope |
|---|---|---|---|
| ~~Sprint-1~~ | 5cf569b9 (done) | closed | DeepSeek Fallback-Option, kein Default-Flip |
| **Sprint-2 ENRICHED** | `d99195fb` | draft + locked | Pack 2/4/5 + FIND-A + FIND-B |
| Sprint-3 | `1ada23e9` | draft + locked | Task-Tab A1/A2 + Pipeline-Tab v3 Sprint 2 |

## Sprint-2 Scope (enriched)

### Kern-Packs (aus atlas-worker-system-hardening.md)
- **Pack 2** Receipt-Sequence Enforce: `/api/tasks/[id]/receipt/route.ts` → 409 bei sequence-violation, nextAllowedStages im Body.
- **Pack 4** Dispatch-Idempotency: `dispatchToken` optional im Body, 200 idempotent bei match, 409 bei mismatch.
- **Pack 5** Stall-Detector: `worker-monitor.py` STALL_WARN_MINUTES=10 → `executionState=stalled-warning` + soft-alert; STALL_HARD_MINUTES=30 → `status=failed`.

### Neu (aus Sprint-1 Empirie)
- **FIND-A** Root-Cause doku (dispatchTarget-Routing) + Fix oder Workaround oder WK-38.
- **FIND-B** worker-monitor.py exclude-list fuer legitime `worker:atlas-` CLI-Spawns oder 90s-confidence-Window.

### Acceptance
- Pack 2/4/5: je 1 Acceptance-Test via curl
- FIND-A/B: dokumentierter Root-Cause oder aktiver WK-Eintrag
- Alle Forge-Subs mit `result`-Receipt, kein Ghost-Fail
- `resultSummary` beendet mit Atlas-Next-Step: entweder `GO SPRINT-3` oder `HOLD ROOT-CAUSE:<wk>`

## Sprint-3 Scope (unchanged)

### Task-Tab v2
- **A1** FAILED-Counter Badge im Header + Failed-Cluster-View mit preservedFailureReason
- **A2** NBA-Regel-Engine Auto-Suggest (min. 3 Rules: ready-for-retry bei failed+retryCount<3, needs-receipt bei in-progress+lastProgressAt>5min, candidate-for-operatorLock bei retryCount>=3)

### Pipeline-Tab v3 Sprint 2
- Step-DAG in Task-Drawer als visuelle Lifecycle-Chain accepted → progress → result
- Inline-Actions (Dispatch/Retry/Release-Lock/Admin-Close) pro Step
- Filter-Chip-Leiste (Agent/Stage/Date)
- Mobile-Polish Touch-Targets ≥ 44px

### Acceptance
- A1 live: Badge sichtbar, Cluster-View filterbar
- A2 live: 3+ Rules aktiv mit visual-cue im Board
- Pipeline-v3 Sprint 2: DAG sichtbar, 2+ Inline-Actions funktional, Filter-Chips vorhanden
- Screenshots je Milestone
- E2E-Playwright-Tests fuer A1+A2+Pipeline-Step-DAG

## Autonome Orchestrierung — Atlas-Playbook

Nach User-Start-Prompt (einmalig):
1. Atlas liest Sprint-2 (`d99195fb`), PATCH operatorLock=false
2. Atlas dispatchet 5 Forge-Subs (Pack 2, Pack 4, Pack 5, FIND-A, FIND-B)
3. Atlas wartet auf alle 5 result-Receipts (sequenziell oder parallel je nach Sub-Scope)
4. Atlas consolidiert Result, sendet Sprint-2 result-Receipt
5. **Ohne Operator-Input:** Atlas liest Sprint-3 (`1ada23e9`), PATCH operatorLock=false
6. Atlas dispatchet 3-4 Pixel-Subs (A1, A2, Pipeline-v3 Sprint 2)
7. Atlas wartet auf alle result-Receipts
8. Atlas consolidiert Sprint-3, sendet final result

### Stop-Bedingungen (Atlas meldet zurueck, Operator entscheidet)
- Root-Cause in FIND-A oder FIND-B nicht klaerbar ohne Gateway-Source-Fix (external)
- Forge-Sub schlaegt 2× hintereinander fehl (Retry-Gate)
- MC oder Gateway instabil (Health degraded > 5 Minuten ohne Cost-Anomaly-Kontext)

## Monitoring waehrend Autonom-Run

- Operator-Side (pieter_pan via Claude-Assistant): alle 20min Board-Scan + Cron-Log-Tail
- Eingriffe nur bei Stop-Bedingung oder Instabilitaet
- Ergebnis-Report nach Sprint-3 done: Vault `/home/piet/vault/03-Agents/sprint-2-3-autonomous-report-2026-04-19.md`

## Rules ergaenzen bei Findings

- R38 (potenziell): dispatchTarget-Resolve-Kontrakt (FIND-A)
- R39 (potenziell): worker-monitor Gateway-Restart-Tolerance (FIND-B)

## Rollback

- Pro Pack: git-Revert auf letzten grünen Commit moeglich
- `tasks.json`: kein Schema-Change in diesem Sprint-Block (nur Route-Level)
- Sprint-2/3 Cancel: PATCH status=canceled, Atlas respektiert

## Signed-off

Operator (pieter_pan) 2026-04-19 10:28 UTC. Atlas laeuft autonom, Operator-Monitor per 20min-Tick.
