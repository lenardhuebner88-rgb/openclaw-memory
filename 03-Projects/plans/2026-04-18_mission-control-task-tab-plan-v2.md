---
title: Mission Control — Task-Tab Operator-Cockpit Plan v2 (Revidiert 2026-04-18 Abend)
date: 2026-04-18 22:05 UTC
author: Principal Product-System Architect (Operator-Live-Review)
status: ready-for-atlas-orchestration
owner: Atlas → Forge + Pixel
version: 2.0 (revidiert nach Live-Screenshot-Audit)
supersedes: 2026-04-18_mission-control-task-tab-plan.md v1
---

# Task-Tab Plan v2 — Ehrlichkeit-First, Foundation-Complete

## Warum v2
v1 wurde heute Abend geschrieben OHNE dass der Taskboard-Live-Zustand bekannt war. Live-Screenshot-Audit (21:56 UTC Desktop + Mobile) zeigt:
1. **Foundation ist groesser als gedacht**: T1 + T3 + Board-Cockpit Pack 1 + Zone C sind schon deployed. Viele UI-Elemente wirken.
2. **Aber 4 massive Ehrlichkeits-Bugs in Live-UI** untergraben Operator-Vertrauen
3. Mobile hat 5 zusaetzliche Bugs, die auf Desktop-Review nicht sichtbar waren

v2 verschiebt Scope von "13 neue Packs" auf "2 Foundation-Completions + 9 Ehrlichkeits-Fixes".

## Ist-Matrix (was live, was draft, was neu)

| Pack | Status | Task-ID | Notiz |
|---|---|---|---|
| T1 Lane-Projection | done | d4e491e6 | canonical computeLane im API |
| T3 WIP-Limits Config | done | 26933c28 | per Agent in openclaw.json |
| Board-Cockpit Pack 1 boardLane-Klassifikation | done | e9353286 | historisch |
| Cockpit Pack 3 Zone C Live-Flow Lanes | done | 2f966898 | historisch |
| T2 Agent-Load-from-Tasks | DRAFT | 9450f894 | Foundation-Rest |
| T4 Receipt-Rename | DRAFT | 5c3cee19 | Foundation-Rest |

## Neue Live-Findings aus Screenshot-Audit (13)

### Ehrlichkeits-Bugs (F-Serie, kritisch)
- F1 FAILED-Counter zaehlt receiptStage statt status - zeigt 67 statt echte 2. Alarm-Trigger fuer Operator-Panik.
- F2 NBA 'All clear' widerspricht FAILED 67 direkt darueber - NBA-Regel muss Failed-Count reflektieren (abhaengig von F1).
- F3 'Later'-Label ist verwirrend - Now 1 / Next 2 / Later 164 sollte 'Archive' heissen.
- F4 '102 dispatched · 92% confidence' ohne Zeitfenster - 24h? All-time? Was ist 'confidence'?

### Lane-Projection-Bugs (Q-Serie)
- Q1 Incident-Lane zeigt done-Tasks - WK-27 war status=done aber in Incident-Lane. Projection nutzt lastReportedStatus statt status.
- Q2 'Dispatch blocked: Task already dispatched' ist keine Fehlermeldung sondern Normalzustand. Sollte entweder weg oder Action-Button werden.
- Q3 Draft-Tasks in Waiting-Lane - Waiting ist fuer pending-pickup. Draft braucht eigene 'Inbox'-Lane oder raus aus Main-View.

### Route / Nav
- R1 /pipeline → 404 - Nav-Label heisst 'Pipeline', Route ist /kanban. User-Bookmarks + Deep-Links brechen. Alias-Route noetig.

### Mobile-Serie
- M1 Status-Bar-Pills truncated ('M u', 'G..', 'D...', 'R...') - unlesbar
- M3 Lane-Tab-Labels truncated ('Sta...' statt 'Stalled')
- M4 Card-Pills Overflow - 'Forge · Wait...' abgeschnitten
- M5 Action-Queue-Text zu lang fuer Mobile (30% Screen)

## Orchestrierungs-Struktur (3 Sub-Plaene)

### Sub-Plan A — Ehrlichkeits-Fixes (KRITISCH, vor allem anderen)
Warum zuerst: Solange FAILED 67 + NBA 'All clear' + Q1 live sind, luegt die UI. Jeder andere Fix baut auf Vertrauen.

| # | Pack | Agent | Est. | Kriterium |
|---|---|---|---|---|
| A1 | F1 FAILED-Counter auf status=failed umstellen | Forge | 20min | Counter zeigt 2 (nicht 67) |
| A2 | F2 NBA-Regel reagiert auf FAILED/REVIEW-Count | Forge | 30min | NBA zeigt konkrete Action wenn F gross 0 |
| A3 | Q1 Incident-Lane-Projection: nur status=failed | Forge | 15min | WK-27-aehnliche done-Tasks nicht in Incident |
| A4 | F3 'Later' → 'Archive' Label | Pixel | 10min | Pill zeigt 'Archive N' |
| A5 | F4 Dispatched-Metric mit Zeitfenster-Context | Pixel | 20min | '102 dispatched today · 92% completion' |

Sub-Plan A Acceptance: Screenshot der Taskboard-Hero zeigt ehrliche Zahlen. NBA reagiert auf FAILED groesser 0.

### Sub-Plan B — Foundation-Completions (T2 + T4)
Die 2 bereits als draft liegenden Tasks.

| # | Pack | Agent | Est. | Task-ID |
|---|---|---|---|---|
| B1 | T2 Agent-Load-from-Tasks (Flag-gated) | Forge | 45min | 9450f894 (draft) |
| B2 | T4 Receipt-Rename (failed → no-receipt fuer canceled) | Forge | 30min | 5c3cee19 (draft) |

B-Acceptance:
- /api/agents/live.tasks.active matcht /api/tasks?status=in-progress
- receiptStage=no-receipt fuer smoke-canceled Tasks, receiptStage=failed nur fuer echte Failures

### Sub-Plan C — UX/Mobile-Cleanup
Nach A+B.

| # | Pack | Agent | Est. |
|---|---|---|---|
| C1 | Q2 'Dispatch blocked'-Messaging → Action-Button oder weg | Pixel | 30min |
| C2 | Q3 Draft-Tasks eigene Lane 'Inbox' oder raus aus Main-View | Pixel | 25min |
| C3 | R1 Route-Alias /pipeline → /kanban | Forge | 15min |
| C4 | M1 Status-Bar-Pills mobile: vertical stack oder Icon-only | Pixel | 30min |
| C5 | M3/M4 Lane-Tabs + Card-Pills Overflow-Handling | Pixel | 30min |
| C6 | M5 Action-Queue mobile-short version | Pixel | 15min |

C-Acceptance: Mobile-Playwright-Smoke gruen. Alle 4 Status-Pills lesbar im 390px-Viewport.

## Gesamt-Aufwand

| Sub-Plan | Est. | Kritikalitaet |
|---|---|---|
| A Ehrlichkeit | ca. 95min | kritisch |
| B Foundation-Rest | ca. 75min | hoch |
| C UX/Mobile | ca. 145min | mittel |
| Total | ca. 5.5h | |

Wall-Clock bei Parallelisierung (Forge + Pixel gleichzeitig): ca. 3.5h.

## Reihenfolge fuer Atlas

1. Welle 1: A1 + A2 + A3 (Forge, sequenziell) ca. 65min
2. Welle 2: A4 + A5 parallel zu B1 (Pixel + Forge) ca. 45min
3. Welle 3: B2 + C1 + C2 parallel (Forge + Pixel) ca. 55min
4. Welle 4: C3-C6 (Forge + Pixel) ca. 80min

Zwischen Wellen min. 10min Pause gegen WK-19 Build-Storm.

## Risiken

| Risiko | Mitigation |
|---|---|
| A1 aendert Counter-Semantik - andere Stellen brechen | grep nach receiptStage=failed vor Deploy, Migration-Test |
| B1 T2 Agent-Load-Flag on koennte Display-Drift zeigen | Flag default off, Canary via env var |
| C4 Mobile-Refactor kollidiert mit Spark-Audit (bekannt) | Spark-Audit-Empfehlungen vorher lesen |
| Alle Wellen triggern MC-Rebuild → WK-19 | Batch-Merges, max 2 pro Stunde |

## Rollback
- A1, A3: reiner Projection-Fix, einfacher Revert
- A2: feature-flag NBA_REACT_TO_FAILED=1
- B1: AGENT_LOAD_FROM_TASKS=0 (default)
- B2: Migration-Dry-Run first, dann apply
- C-Serie: CSS/Component-Level, isoliert

## ATLAS HANDOFF

### Was Atlas tun soll
1. Diesen Plan laden
2. Sub-Plan A als erstes Welle dispatchen (3 Forge-Tasks sequenziell)
3. Nach Welle 1 deploy verifyen (Screenshot-Probe via Playwright-MCP)
4. Welle 2-4 aufbauend
5. End-Acceptance: Playwright-Smoke + manueller Screenshot-Compare

### Bestehende Task-IDs wiederbenutzen
- B1 = 9450f894 (T2, draft) → dispatchen statt neu anlegen
- B2 = 5c3cee19 (T4, draft) → dispatchen statt neu anlegen

Fuer A1-A5 und C1-C6: neue Tasks anlegen mit Handoff-Markern.

### Regel-Bezug
- R1 Verify-After-Write (Kern jeder Welle)
- R2 keine Placeholder in Task-Description
- R4 keine Direct-Config-Edits (T3 ist schon live)
- R15 atomic Deploy-Sequenz (stop+build+start im gleichen Turn)

## Atlas Retrieval Summary

Zweck: Task-Tab von 'sieht gut aus' auf 'luegt nicht' + 'funktioniert auf Mobile' heben. Foundation ist schon da (T1/T3 + Pack 1/3), nur noch Ehrlichkeits-Fixes + 2 Foundation-Completions + UX-Cleanup.

Top-3 Findings:
1. FAILED-Counter luegt (67 vs echte 2)
2. NBA widerspricht Failed-Count
3. Mobile Status-Pills unlesbar

Aktion: 3 Sub-Plaene A/B/C, 13 Packs, ca. 5.5h Agent-Time (ca. 3.5h Wall-Clock). Foundation-First, Ehrlichkeit-First.

Acceptance: Screenshot-Probe zeigt ehrliche Zahlen + Mobile-Lesbarkeit + Playwright-Smoke gruen.

Bootstrap:
- Dieser Plan: /home/piet/vault/03-Agents/2026-04-18_mission-control-task-tab-plan-v2.md
- Screenshots: Playwright-MCP oder SSH /tmp/mc-*-desktop.png /tmp/mc-*-mobile.png
- Existierende Drafts: T2 = 9450f894, T4 = 5c3cee19

Prerequisites:
- WK-27 done (5ad536ba)
- T1 done, T3 done
- WK-19 Build-Batching morgen als P1 (verhindert Downtime-Storm bei C-Welle)

Empfohlener Ausfuehrungs-Agent: Atlas (Orchestrator) → Forge (Foundation + Projection) + Pixel (UI + Mobile).
