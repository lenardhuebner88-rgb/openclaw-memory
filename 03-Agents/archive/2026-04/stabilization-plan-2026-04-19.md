# Stabilization Plan — 2026-04-19 bis 2026-04-25

## Zusammenfassung
| Prio | Items | Aufwand | Zeitslot |
|------|-------|---------|---------|
| P0 | 5 | ~4h | Mo 09:00–13:00 |
| P1 | 4 | ~3h | Mo 13:00–16:00 |
| P2 | 4 | ~4h | Mo Nachmittag/Abend |
| P3 | 7 | ~8h | Diese Woche |
| P4 | 6 | ~6h | Diese/Nächste Woche |
| P5 | 4 | ~3.5h | später |
| **Total** | **30** | **~28.5h** | |

## Empfohlene Morgen-Reihenfolge (2026-04-19)
09:00 — P0 #1 Cleanup
09:30 — P0 #2+#3 parallel (Operator-Lock Forge-Backend + Build-Gate Forge-Infra)
10:30 — P0 #4 task-assignees-Refactor
11:00 — P0 #5 Worker-Pack 2 Receipt-Sequence
12:00 — P1 #6 Legacy re-POST (hängt von #5 ab)
12:30 — Lunch-Break
13:30 — P1 #7+#8 Task-Tab A1+A2 (Pixel)
14:30 — P2 #10 Kosten-Routing (Test 1 Forge-Task mit DeepSeek)
15:30 — P2 #12 KPI-Bug
16:00 — End-Of-Day-Summary

Parken-Regel: nichts aus P4/P5 anfassen, bis P0-P2 durch.

## P0 — Sofort (2026-04-19 09:00–13:00)
#   Pack   Plan   Aufwand
1    Stabilization Phase 5    Cleanup: Ghost-Tasks, Stale-Keys, runs.json Sweep    60min
2    Operator-Lock Forge-Backend    Neue Dispatch-Logik mit resolvedTarget    45min
3    Build-Gate    Forge-Infra    Build-Script Robustheit + Lock-Handling    45min
4    Naming    task-assignees-Refactor (R25-NamingInvariante)    45min
5    Worker-Pack 2    Receipt-Sequence + Single-Write-Prinzip    45min

## P1 — Cleanup + Ehrlichkeit (2026-04-19 13:00–16:00)
#   Pack   Plan   Aufwand
6    Legacy re-POST (4 Naming-Tasks neu)    Stabilization Phase 5    45min
7    Task-Tab A1    FAILED-Counter ehrlich    Task-Tab-v2    30min
8    Task-Tab A2    NBA-Regel reaktiv auf Failed/Review    Task-Tab-v2    30min
9    Worker-Pack 8    Retry-Single-Path    Worker-Hardening    60min

## P2 — Kosten & UI (2026-04-19 Nachmittag/Abend)
#   Pack   Plan   Aufwand
10    Kosten-Routing    Forge→DeepSeek, Lens→MiniMax M2    Stabilization Phase 6    45min
11    Pipeline-v3 Sprint 2    Step-DAG + Inline-Actions    Pipeline-v3    2h
12    WK-26    KPI closed-24h Fix    Finding    30min
13    Costs Zone D    Agent-Ladder UI    Costs-v2    1h

## P3 — Ausbau (Diese Woche)
#   Pack   Plan   Aufwand
14    Worker-Pack 4    Dispatch-Idempotency (dispatchToken)    Worker-Hardening    1h
15    Worker-Pack 5    Stall-Detector    Worker-Hardening    1h
16    Continuation Pack B    Markdown→YAML Seed-Konverter    Continuation    1.5h
17    Continuation Pack E    Cron-Live (DRY_RUN=0)    Continuation    30min
18    Board-Cockpit Phase 2    Navigation-Refactor 13→7 Tabs    Board-Cockpit    3h
19    WK-18    Config-Live-Reload    Finding    1h
20    WK-19    Debounce-Wrapper-Verify in Produktion    Finding    20min

## P4 — Agent-Infra (Diese/Nächste Woche)
#   Pack   Plan   Aufwand
21    src/lib/agent-ui.ts    aus Spark-Display-Guide §5    neu    45min
22    WK-25    Playwright-Smoke für 4 UI-Sprints    Finding    1h
23    Continuation Pack F    Retry-Eskalation    Continuation    1h
24    Board-Cockpit Pack 7    SSE    Board-Cockpit    2h
25    Pipeline-v3 Sprint 2    A11y + Keyboard-Shortcuts    Pipeline-v3    45min

## P5 — Feinschliff (Nice-to-Have)
#   Pack   Plan   Aufwand
27    Prompt-Template Cache-Opt    Task f6d9a2f7 blocked    1h
28    MiniMax M2.7 → M2 Switch    Kosten (20% billiger)    5min
29    WK-28    Monitor HTTP-probe statt systemd-check    Finding    30min
30    Costs Task/Plan-Attribution    Costs-v2 gap-Liste    2h

## Extern — Nicht in Operator-Kontrolle
Gateway-Source-Fix: worker:atlas--Prefix-Hardcoding in openclaw-npm-Package v2026.4.14 (minified). Nur über Package-Update/Issue fixbar. Workaround: R25 resolvedTarget-Fix umgeht Problem für neue Tasks.

---
created: 2026-04-19
owner: Atlas
trigger: Morgen mit "Lade Stabilization-Plan und starte Phase 1" beginnen