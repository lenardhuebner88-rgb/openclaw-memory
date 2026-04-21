---
title: Atlas Sprint-Dispatch Prompt — Pipeline Tab Quick-Wins Phase 1
date: 2026-04-21 11:00 UTC
plan-ref: /home/piet/vault/03-Agents/pipeline-tab-quickwins-plan-2026-04-21.md
scope: phase-1-only
status: ready-for-operator-review
---

# Atlas Sprint-Start Prompt — Phase 1 Only

Dieser Text ist als enger Sprint-Start fuer Atlas gedacht. Scope ist ausschliesslich Phase 1 aus dem Plan `pipeline-tab-quickwins-plan-2026-04-21.md`.

---

Atlas,

Sprint-Start: Pipeline-Tab Quick-Wins Phase 1 gemaess
`/home/piet/vault/03-Agents/pipeline-tab-quickwins-plan-2026-04-21.md`

Scope:
- Nur Phase 1 (Daten-Wahrheitsgehalt, P0)
- Nur Tasks 1.1 bis 1.4
- Keine Arbeit an Phase 2, 3 oder 4
- Kein Broad Review
- Keine Nebenbaustellen

Pre-Flight ist Pflicht vor jedem ersten Dispatch:

```bash
/home/piet/.openclaw/scripts/pre-flight-sprint-dispatch.sh /home/piet/vault/03-Agents/pipeline-tab-quickwins-plan-2026-04-21.md
```

Regel:
- Nur bei 7/7 gruen starten
- Wenn irgendein Gate nicht gruen ist: nichts dispatchen, keine Board-Tasks anlegen, Lenard mit exaktem Gate-Fehler pingen

Wichtige Guardrails:
- R49 strikt: keine Claim-/Done-Aussage ohne Verify-Command inline
- R50 strikt: keine Session-Lock-Verletzung
- R54/R55 strikt: Bei `Not connected` oder `Connection closed` zuerst Session-/Gateway-Korrelation pruefen. Kein Abbiegen in Taskboard-HTTP-Backend-RCA, solange Session-Staleness nicht ausgeschlossen ist. Gateway-Restart allein gilt nicht als Heilung; bei HTTP gesund zuerst Session-Rotation bzw. Runtime-Recovery-Pfad einkalkulieren.
- R27 praktisch anwenden: nach jeder Code-Aenderung Deploy/Reload + Warmup, erst dann verifizieren

Board-Flow E2E:
- Vier Tasks strikt sequenziell dispatchen, nicht parallel
- Executor fuer Code-Aenderungen: Forge
- Jeder Task muss vollstaendig ueber MCP laufen: `taskboard_create -> claim -> patch -> verify -> done`
- Kein curl-HTTP-Fallback fuer Taskboard-Aktionen
- Nach jedem Task sofort verifizieren, erst dann den naechsten starten

Dispatch-Reihenfolge:

1. Task `1.1 Filter-Logik failedAt-basiert`
   - File: `src/lib/pipeline-data.ts`
   - Ziel: Zeitfilter fuer failed-Cards auf `failedAt` umstellen

2. Task `1.2 KPI-Subtitle dynamisch`
   - File: `src/app/kanban/PipelineClient.tsx`
   - Ziel: Subtitle folgt aktivem Window-Chip

3. Task `1.3 Stepper-Stage fuer failed`
   - File: `src/lib/task-pipeline-payload.ts`
   - Ziel: failed-Cards markieren die echte Fail-Stage; Feld `failedAtStage` einfuehren

4. Task `1.4 seit-X Label truth-basiert`
   - File: `src/app/kanban/components/TaskPipelineCard.tsx`
   - Ziel: Zeitlabel nach Status aus Truth-Timestamps ableiten, nie aus `updatedAt`

Stop-/Gate-Regeln innerhalb Phase 1:
- Nach Task 1.1 sofort Smoke-Test fahren. Wenn Ergebnis noch `> 0`, Phase 1 blockieren und vor Task 1.2 erst Root Cause klaeren.
- Wenn ein Task fehlschlaegt: nicht ueberspringen, nicht parallel Ersatz-Task aufmachen, sondern stoppen und Findings kompakt melden.
- Wenn MCP-Tool-Fail auftritt: R54/R55 anwenden, keine HTTP-Backend-Diagnose als Erstreaktion.
- Wenn Gateway-OOM waehrend Sprint: sofort Stop und Lenard pingen.

DoD fuer Phase 1:

- Smoke-Test:

```bash
curl -s http://127.0.0.1:3000/api/pipeline/tasks?window=24h \
  | jq '[.cards[] | select(.status=="failed")] | length'
```

Erwartung:
- Ergebnis MUSS `0` sein
- Das ist die verbindliche Truth fuer "failed in last 24h"

- Live-Check auf `http://100.109.144.77:3000/kanban`:
  - KPI-Subtitle wechselt synchron mit dem Filter-Chip
  - Task `8482a1db-572c-4aa5-81d6-ad683341dd1a` zeigt `seit 2d 12h` statt `seit 18h`
  - Failed-Cards zeigen das X auf der wirklichen Fail-Stage, nicht generisch als aktiv laufendes `working`

- Dispatch-Pfad-Verifikation:
  - alle 4 Tasks liefen vollstaendig ueber MCP
  - R49 bei jedem Claim sauber
  - R50-Locks am Ende sauber freigegeben
  - 0 Ghost-Tasks
  - 0 stuck-in-review

Reporting nach jedem Task exakt in diesem Format:
- `EXECUTION_STATUS`
- `RESULT_SUMMARY`
- `CHANGED_FILES`
- `VERIFICATION`
- `RESIDUAL_RISK`

Phase-1-Abschluss:
- Vor/Nach-Screenshots von `/kanban`
- Memory-Update `session_2026-04-21_full_day.md`
- Commit in Mission Control mit Phase-1-Scope im Commit-Body
- Entscheidungsempfehlung an Lenard: `Phase 2 dispatchen: ja/nein`

Nicht Teil dieses Blocks:
- Phase 2 bis 4
- API-Konsolidierung
- SSE/WebSocket
- Naming-Consolidation
- Repo-Hygiene ausserhalb der direkt betroffenen Phase-1-Files

Starte nur, wenn Pre-Flight wirklich gruen ist. Andernfalls keinen Sprint anwerfen, sondern nur den blockierenden Gate-Report liefern.
