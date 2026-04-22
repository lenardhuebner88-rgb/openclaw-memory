---
title: Atlas Sprints A + B + C Plan 2026-04-19 Evening
date: 2026-04-19 13:40 UTC
author: Operator (pieter_pan) direkt
scope: 3 Sprint-Pakete für Memory + Validation + UX Level-Up
status: 3 Sprints als draft+operatorLock=true im Board
---

# Atlas Sprint-Plan A + B + C — 2026-04-19 Evening

## Kontext

Nach heutigem Stabilization-Marathon (10 Fixes, Memory-Level-1, QMD live, 3 Sprints morgens durchgelaufen) stehen drei strategische Pakete bereit, die das System auf das naechste Level heben.

**Queue-State (draft + operatorLock=true, Auto-Pickup skipped — Atlas unlockt beim Start):**

| Sprint | Task-ID | Priority | Sub-Count | Dauer-Est |
|---|---|---|---|---|
| **A** Validation + Hygiene | `0cfa885f` | **high** | 5 | ~1h |
| **B** Memory-Intelligence Level-2 | `3b0c592c` | medium | 4 | ~1.5h |
| **C** Worker-Pack-8 + Monitoring-UI | `bff4c422` | medium | 5 | ~2h |

## Empfohlene Reihenfolge

**A zuerst** (validiert heutige Arbeit + loest Cost-Noise + schuetzt vor UI-Build-Storm in C).

Danach parallel moeglich: B (Memory-Intelligence) UND C (UX+Pack-8).

## Sprint-A — "Validation + Hygiene"

### Motivation
Wir haben heute 10+ Fixes deployed. Manche nur in Config, nicht live-verified:
- `compaction.mode=safeguard` wurde nie unter Last getestet
- QMD embed laeuft noch (2208+/- vectors)
- Cost-Anomaly seit 3+ Tagen degraded, $362/$3 Limit-Overrun
- Dreaming-Config gesetzt aber naechster 3am-Run noch nicht beobachtet
- 6 neue Scripts nicht im Script-Integrity-Check

### 5 Sub-Tasks

**Sub-A1 (Lens/efficiency-auditor): Cost-Anomaly Deep-Dive**
- Analyse `/api/costs` + `telemetry/cost-events.json`: welches Provider/Model drives?
- Entscheidung: mute/fix/flip
- Output: `vault/03-Agents/cost-anomaly-analysis-2026-04-19.md`

**Sub-A2 (Forge/sre-expert): R36 Context-Overflow Safeguard Live-Test**
- Spawne Long-Running Task mit 50+ tool-calls
- Gateway-log prüfen: soft-threshold 20k tokens triggert pre-compact?
- `recentTurnsPreserve=6` wirkt?
- `qualityGuard` fires retries?
- Output: `vault/03-Agents/safeguard-verify-2026-04-19.md`

**Sub-A3 (Forge): Build-Artifact-Cleanup-Cron**
- Neues `/home/piet/.openclaw/scripts/build-artifact-cleanup.sh`
- Cron: Sonntag 3am
- Actions: `find .next* -mtime +7 -delete`, alte `src-backups/` purge, vacuum alte node_modules-history
- Expected: 3-5 GB/Woche freed

**Sub-A4 (Forge): Script-Integrity-Check erweitern**
- Update `/home/piet/.openclaw/scripts/script-integrity-check.sh`
- Add 6 neue Scripts heute: minions-pr-watch, rules-render, atlas-orphan-detect, pr68846-patch-check, dreaming-cost-guard, rules-query
- Plus: Discord-webhook env-var assertions

**Sub-A5 (Operator passive + Forge): Dreaming Live-Verify (morgen 8am)**
- Nach 3am dreaming-cron beobachten
- `workspace/scripts/dream.log` prüfen
- light/deep/rem-phases actually ran?
- Cost-guard gefeuert?
- Output: `vault/03-Agents/dreaming-verify-2026-04-20.md`

### Acceptance (alle 5 Sub-Done)
- 3+ Reports in Vault
- 1+ Cron-Updates live
- Entscheidung zu Cost-Anomaly dokumentiert
- Sprint-B + Sprint-C Empfehlung (next-step-pointer) in Sprint-A Result-Receipt

## Sprint-B — "Memory-Intelligence Level-2"

### Motivation
Memory-Level-1 ist live (QMD + 3 Collections + stdio MCP). Research zeigte Level-2 Patterns:
- **Letta core/archival/recall**
- **Mem0 fact-extraction (80% token-savings)**
- **Per-Agent Collection-Specialization**
- **Sleep-Time Compute precompute**

### 4 Sub-Tasks

**Sub-B1 (Atlas local + Forge): QMD Embed Finalize + Quality-Test**
- Warte bis `qmd status` zeigt vectors-embedded ≥ 1000
- 5 real-world Vergleichs-Queries (deep_search vs search):
  - "R30 mitigation"
  - "gateway restart race"
  - "atlas orphan"
  - "playwright sprint 3 failure"
  - "session-maintenance config"
- Output: `vault/03-Agents/qmd-hybrid-quality-2026-04-19.md`

**Sub-B2 (Forge): Mem0-Style Fact-Extraction Pipeline**
- Neues `/home/piet/.openclaw/scripts/memory-fact-extractor.sh`
- Cron: 3:30am nach Dreaming
- Logik: liest letzte 24h session-transcripts, extrahiert atomare Facts
  - z.B. "R30 mitigated by PR #68846", "Gateway OOM at 4.3GB peak"
- Output: `workspace/memory/facts/YYYY-MM-DD.jsonl`
- QMD indexiert als 4. Collection `facts`

**Sub-B3 (Forge): Per-Agent QMD-Collection-Specialization**
```jsonc
openclaw.json:
agents.list.sre-expert.memorySearch.qmd.extraCollections = [mc-src, facts]
agents.list.efficiency-auditor.memorySearch.qmd.extraCollections = [workspace, facts]
agents.list.main.memorySearch.qmd.extraCollections = [vault, workspace, mc-src, facts]
```
Plus Doku in `AGENTS.md`.

**Sub-B4 (Forge): Auto-Compact Pre-Turn Hook bei 3 MB**
- Neues `/home/piet/.openclaw/scripts/agent-precompact-wrapper.sh`
- Wrappt `openclaw agent` call
- Pre-Turn-Check: session-file-size > 3 MB → inject `/compact` instruction PRE-message
- Aktivierung via `agents.defaults.preTurnHook` config ODER direct-exec replacement in `auto-pickup.trigger_worker`

### Acceptance
- B1: Quality-Report mit 5 query-comparisons
- B2: fact-extractor-cron live, erste Facts-JSONL populated, Collection `facts` in QMD indexed
- B3: Per-agent config live, `status` MCP-tool zeigt per-agent extraCollections
- B4: Pre-Turn-Hook live, Test-Turn bei 4MB-mock-session triggert compact

## Sprint-C — "Worker-Hardening Pack-8 + Monitoring-UI"

### Motivation
Worker-Hardening-Plan hat 8 Packs; Pack 1/3/7 live, 2/4/5 heute via Sprint-2 gemerged, **Pack 8 Retry-Single-Path fehlt**. Plus: Daily-Operator braucht Real-Time-Health-Views die aktuell nur via tail'ing logs moeglich sind.

### 5 Sub-Tasks

**Sub-C1 (Forge): Worker-Hardening Pack-8 Retry-Single-Path**
- Neues Modul `src/lib/task-retry.ts` mit `attemptRetry(task): RetryDecision`
- Decision-Schema: `{nextRetryAt, retryCount, reasonIfBlocked}`
- Call-sites migrieren: `worker-monitor retry-dispatch`, `admin-retry route`, `receipt-failed-handler`
- Board-event `retry-decision` bei jedem Call geschrieben
- Acceptance: simulated failed task `retryCount=2` → retry; `retryCount=3` → blocked

**Sub-C2 (Forge): FIND-A DispatchTarget Deep-Fix + E2E-Test**
- Problem aus Sprint-1: `dispatchTarget=deepseek-v3.2` resolvt zu main-worker statt external
- Fix in `task-dispatch.ts` oder gateway-handshake
- Acceptance: POST Task mit `dispatchTarget=openrouter/deepseek-v3.2` → Spawn geht an openrouter-provider nicht main
- Plus Docs

**Sub-C3 (Pixel/frontend-guru): Real-Time-Health-Dashboard MC-Tab**
- Neue Route `/monitoring` ODER Panel in `/taskboard`
- Listet 12+ Crons: last-run, last-alert, status (green/yellow/red), next-scheduled-run
- Datenquelle: parse `workspace/logs/*.log` + crontab
- SSE oder 30s polling

**Sub-C4 (Pixel): Cost-Trend-Panel**
- Extension von `/costs` oder `/costs-cockpit`
- Today vs 7-day-avg per model/provider
- Spend-per-agent Bar-Chart
- Budget-Burn-Projection
- Datenquelle: `telemetry/cost-events.json`

**Sub-C5 (Pixel): All-Alerts-Feed MC-Tab**
- Neue Route `/alerts`
- Parse Discord-Webhook-History via `workspace/logs/*.log`
- Chronologisch, filterbar (by type: cost, mcp-zombie, patch-drift, atlas-orphan)
- 7d Retention, searchable

### Acceptance
- C1: task-retry.ts live, 3 call-sites migrated, acceptance-test passes
- C2: dispatchTarget=openrouter/deepseek-v3.2 resolvt korrekt
- C3: /monitoring live, 12 Crons sichtbar, real-time updates
- C4: Cost-Trend mit 7d + burn-projection
- C5: Alerts-Feed chronologisch, 7d retention
- Playwright-Spec für C3/C4/C5

## Risks + Mitigation

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Sprint-A safeguard-test triggert R36-Overflow erneut | niedrig | hoch | Atlas begrenzt Sub-A2 Scope auf 50 Tool-Calls hart |
| Sprint-B fact-extraction scored wrongly, zu viel noise | mittel | niedrig | minScore 0.7 start, nach 24h tunable |
| Sprint-C UI-Subs triggern Build-Storm | mittel | hoch | Pack-8 + FIND-A VOR UI-Subs, UI-Subs sequenziell nicht parallel |
| Cost-Anomaly-Analyse zeigt active-problem | niedrig | mittel | Sub-A1 empfiehlt Entscheidung, Operator final |

## Stop-Bedingungen

Atlas meldet zurück (blocked) bei:
- FIND-A nur durch Gateway-Source-Fix loesbar (external)
- QMD-Embed crashed erneut (Bun-Segfault wie heute)
- MC-Instabilitaet > 5min (excl. known cost-anomaly)
- Forge-Sub-Task 2× hintereinander fehlgeschlagen

## Monitoring (Operator passiv)

- 20min-Tick Board + Cron-Log
- Keine Eingriffe ausser Stop-Bedingung
- End-Report in Vault nach Sprint-C done

## Sprint-Bootstrap-Prompt für Atlas

Separate Datei: **`atlas-bootstrap-prompt-abc-2026-04-19.md`** in Vault.

## Signed-off

Operator (pieter_pan) 2026-04-19 13:40 UTC. 3 Sprints als draft+locked im Board, Atlas unlockt beim Start, Operator monitort passiv bis Sprint-C done.
