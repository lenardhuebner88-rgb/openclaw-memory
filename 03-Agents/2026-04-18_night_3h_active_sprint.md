---
title: Aktiver 3h-Sprint 2026-04-18 Nacht — V-Closure + Task-Tab-Foundation
date: 2026-04-18
window: 18:05 - 21:00 UTC
mode: active-collaboration (Operator-Architect + Atlas-Orchestrator + Forge/Pixel-Exec)
status: in-execution
---

# Aktiver Nacht-Sprint

## Ziel
Zwei Sachen gleichzeitig durchziehen:
1. **V-Sprint vollenden** — alle warnings/gaps aus c3e0e8d4 zu ok machen
2. **Task-Tab Sub-Plan A Foundation** — Projections live (T1–T4)

## Operator-Architect-Rolle (ich)
- Tasks POSTen, dispatchen, verifizieren
- Blocker erkennen, Unblock an Atlas eskalieren
- Nach jedem Task-Done: R1-Verify (Felder tracen)
- Cron-Fires 18:19/18:49/19:19/19:49/20:19/20:49 UTC als harte Check-Points
- End-Summary 20:50 UTC

## Phase 1 — V-Sprint Gap-Closure (18:05-18:50 UTC)

| # | Pack | Agent | Est. | Warum |
|---|---|---|---|---|
| V2b | Artefakt-Disk-Check nachziehen | Forge | 10min | warning → ok |
| V4b | Health-Fail + Build-Timeline Korrelation | Forge | 15min | warning → ok |
| V5b | Playwright-Smoke-Files für memory/files/automations/palette schreiben (leere Shells ok) | Pixel | 20min | gap → ok |
| V6b | KPI-Bug closed-24h=0 — Root-Cause + Minimal-Fix | Forge | 20min | warning → ok (live-Impact: Health-KPI ehrlich) |
| V7b | Discord-Post alternativer Weg (webhook direkt, User-Agent, oder Bash-Script) | Forge | 10min | gap → ok |
| V3-follow | fe36a3eb auf done PATCHen nach git-diff-Check | Atlas | 5min | retry-task schließen |

## Phase 2 — Sub-Plan A Projections (18:50-20:30 UTC)

| # | Pack | Agent | Est. |
|---|---|---|---|
| T1 | Projection `task.lane` canonical + API-Feld | Forge | 60min |
| T3 | WIP-Limits in openclaw.json + Schema | Forge | 20min |
| T2 | /api/agents/live aus Live-Tasks (Flag-gated) | Forge | 45min |
| T4 | receiptStage=failed Rename → no-receipt für canceled-ohne-Receipt | Forge | 30min |

Reihenfolge innerhalb Phase 2: T1 → T3 → T2 → T4. T1 ist Foundation.

## Phase 3 — Sub-Plan B Start (20:30-21:00 UTC)
- T5 Archive raus aus Main-Render (Pixel, 30min) — parallel wenn Forge T4 noch läuft.

## Guardrails
- Keine Deploy-Chain-Kollision (R7/R15) — jeder Merge = atomarer Turn.
- WK-19 Build-Storm-Risiko: max 2 Merges/Stunde, Pause dazwischen.
- Jeder Done-Task: R1-Verify via GET `/api/tasks/:id`.
- Kein Feature-Creep über Scope hinaus.

## Cron-Integration
Fires 18:19, 18:49, 19:19, 19:49, 20:19, 20:49 triggern Snapshot. Ich checke Progress und dispatche nächste Welle. Reports an Operator nur bei Anomalie oder Phasen-Wechsel.

## Acceptance (Ende 21:00 UTC)
- V1–V7 alle ok (keine warning, keine gap)
- T1 Projection `lane` im API-Response für alle Tasks
- T3 WIP-Limits in Config
- T2 Agent-Load aus Tasks (Flag on)
- T4 receiptStage-Migration gelaufen
- Bonus: T5 deployed wenn Budget
- Cron 44591dbe gelöscht, End-Report in Discord + Monitoring-Log
