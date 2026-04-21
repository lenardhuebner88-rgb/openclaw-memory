---
title: Atlas Sprint-Dispatch Prompt — Pipeline-Tab Quick-Wins
date: 2026-04-21 09:50 UTC
plan-ref: vault/03-Agents/pipeline-tab-quickwins-plan-2026-04-21.md
---

# Atlas-Sprint-Dispatch-Prompt (copy/paste)

Dieser Text kann 1:1 an Atlas im #atlas-main Channel gepostet werden.

---

Atlas, starte Sprint-N "Pipeline-Tab Quick-Wins" gegen den Plan `vault/03-Agents/pipeline-tab-quickwins-plan-2026-04-21.md` auf dem Homeserver.

**Scope:** 4 Phasen, ca. 10 dispatchbare Sub-Tasks. Executor für Code-Änderungen: Forge. Alle Änderungen reversibel via revert-commit. KEIN neues Schema, KEIN API-Break, KEIN SSE-Rework (alles unter Non-Scope im Plan markiert).

**Pre-Flight (Pflicht vor erstem Dispatch):**

```bash
ssh homeserver "/home/piet/.openclaw/scripts/pre-flight-sprint-dispatch.sh /home/piet/vault/03-Agents/pipeline-tab-quickwins-plan-2026-04-21.md"
```

7 Gates müssen grün sein, sonst Sprint ablehnen und Operator benachrichtigen.

**Dispatch-Reihenfolge (strikt seriell pro Phase, innerhalb Phase parallel erlaubt):**

1. **Phase 1 — Daten-Wahrheitsgehalt (P0)** — 4 Tasks an Forge:
   - Task 1.1: Filter-Logik `failedAt`-basiert in `src/lib/pipeline-data.ts`
   - Task 1.2: KPI-Card-Subtitle dynamisch in `src/app/kanban/PipelineClient.tsx`
   - Task 1.3: `currentStage`-Heuristik für `status=failed` in `src/lib/task-pipeline-payload.ts`
   - Task 1.4: "seit X"-Label truth-basiert in `src/app/kanban/components/TaskPipelineCard.tsx`
   - **Gate vor Phase 2:** Smoke-Test aus Plan ausführen, Filter 24h muss 0 Incidents liefern.

2. **Phase 2 — Ehrliche UI-Zustände (P1)** — 3 Tasks an Forge:
   - Task 2.1: Pixel-Badge Single-Source-of-Truth
   - Task 2.2: Stale-Agent-Chip bei `heartbeatAge > 3600s`
   - Task 2.3: "data: fallback"-Chip wenn `fleetHealth.truth.heartbeat !== "live"`
   - **Gate vor Phase 3:** Browser-Check via MC-eigener Visual-Regression oder manuellem Screenshot-Diff.

3. **Phase 3 — Performance-Hygiene** — 4 Tasks an Forge:
   - Task 3.1: Poll-Tiering (agents/live 12s, pipeline* 30s)
   - Task 3.2: ETag + 304 für `/api/pipeline/tasks`. **Hinter Env-Flag** `ENABLE_PIPELINE_ETAG=1`, default off, nach Phase-3-Verify standardmäßig on.
   - Task 3.3: Skeleton-Banner-Dismiss fix
   - Task 3.4: Filter-State in URL-Query
   - **Gate vor Phase 4:** Network-Tab-Check zeigt Poll-Halbierung für pipeline/tasks bei stabilen Daten.

4. **Phase 4 — Naming-Consolidation** — 1 Task an Forge:
   - Task 4.1: Section-Link "Kanban" -> "Pipeline", Command-Search-Aliases ergänzen.

**Regeln für Atlas:**

- R27 (Root-Cause-Fix-Timing): Jede Änderung braucht Deploy + Cache-Warmup vor Smoke-Test. Nicht gegen alten Build messen.
- R48 (Board-Hygiene): Nach Sprint-Abschluss müssen alle erzeugten Tasks terminal sein. Keine verwaisten Drafts.
- R49 (Claim-Validator): Dispatch nur, wenn Task-Claim sauber. Bei dead-claim erst `/api/tasks/:id/admin-close` + Redispatch.
- R50 (Session-Lock-Governance): Parallel-Dispatch nur bei unabhängigen Files. Phase 1 Tasks 1.1-1.4 berühren unterschiedliche Files -> parallel OK. Phase 3 Tasks 3.3+3.4 berühren beide `PipelineClient.tsx` -> seriell.

**Acceptance für den Gesamt-Sprint:**

1. Live-Check auf `http://100.109.144.77:3000/kanban`:
   - KPI-Card "INCIDENT" zeigt Subtitle, der zum Filter-Chip passt
   - Filter "Last 24h" mit aktuellem Bestand zeigt 0 Incidents, nicht 14
   - "seit X"-Labels sind Failed-Alter-basiert, nicht updatedAt-basiert
   - Pixel-Card: entweder Badge UND Inhalt sagen "attention needed", oder beide sagen "idle"
   - Stale-Agent-Chip erscheint bei heartbeatAge > 1h

2. Performance-Check:
   - Network-Tab: 5 agents/live-Requests pro Minute, 2 pipeline/tasks-Requests pro Minute bei stabilem Bestand
   - 304-Response-Rate für pipeline/tasks > 50% bei idle-Zustand

3. Operations-Check:
   - Filter-URL teilbar (`?window=any&stage=incident` etc.)
   - Kein "Loading live pipeline…" nach Daten-Load

4. Clean-Up:
   - Alle Phase-Tasks im Taskboard terminal (`done` oder expliziter Rollback dokumentiert)
   - Keine rote Build- oder Type-Check-Stufe
   - Sprint-Debrief-Doc im Vault: `vault/03-Agents/sprint-n-pipeline-tab-quickwins-debrief-<date>.md`

**Bei Hindernissen:**

- Wenn ein Task scheitert: NICHT einfach überspringen. Phase stoppen, Operator via Discord #atlas-main pingen, Plan-Doc-Sektion zum Findings updaten, auf Entscheidung warten.
- Wenn Smoke-Test unerwartete Zahl liefert (z. B. 14 Incidents bleiben nach Filter-Fix): Ground-Truth-Drift ins Plan-Doc ergänzen, nicht Task als done markieren.

**Start:**

```
ssh homeserver "/home/piet/.openclaw/scripts/pre-flight-sprint-dispatch.sh /home/piet/vault/03-Agents/pipeline-tab-quickwins-plan-2026-04-21.md"
```

Danach Phase 1 dispatchen, mit Forge als primary assignee. Board-Events subscriben bis alle 4 Phase-1-Tasks terminal sind, dann Phase 2 starten.

Gesamt-Erwartung: ~2 Arbeitstage Wall-Clock für Atlas + Forge Coordination, davon ~6-7h reine Code-Zeit.

Report-Channel: #atlas-main. Pro Phase einen Debrief-Post nach Abschluss.
