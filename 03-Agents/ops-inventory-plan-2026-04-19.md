---
title: Ops-Inventory Level-Up — Scripts + Crons + Heartbeats sauber indizieren
date: 2026-04-19 16:00 UTC
author: Operator (pieter_pan) direkt
scope: System-Transparenz fuer Operator + Worker-Agents
sprint: [Atlas-Sprint-F] Phase-1 Deep-Audit / [Atlas-Sprint-G] Phase-2 Visualization + Agent-API
status: ready-for-Atlas-bootstrap
---

# Ops-Inventory Level-Up — Plan

## Executive Summary

Ist-Analyse zeigt **massive Fragmentierung**:
- **69+ Scripts** verteilt auf 3 Verzeichnisse (`.openclaw/scripts/` 29, `workspace/scripts/` 25, `mission-control/scripts/` 15+)
- **20+ Crontab-Eintraege** user-crontab
- **14 systemd-user-Units** (5 Services + 9 Timers)
- **24 openclaw-cron-plugin jobs** (separat)
- **HEARTBEAT.md 216 Zeilen** mit Agent-Heartbeat-Flows
- **4 unterschiedliche Scheduler ohne Einheits-View**
- **Keine zentrale Abhaengigkeits-Doku** → Worker-Agents + Operator muessen quer-suchen

**Folge (heute live erlebt):** Atlas musste x-fach rumraten welcher Cron was macht (R33 Cron-Script-Pfad-Integritaet war genau diese Klasse). Operator hat keinen Overview. Neue Agents muessen jedes Mal Spelunk machen.

**Ziel:** Eine strukturierte Knowledge-Base + visuelle Darstellung + Agent-discoverable API. So dass:
- Operator in 30s sieht **"was laeuft wann warum"**
- Worker-Agents in 1 MCP-Call **"was triggert mein Script"** herausfinden
- Neue Scripts automatisch dokumentiert werden (convention-based)

---

## Sprint-Struktur

### Phase-1: [Atlas-Sprint-F] Ops-Inventory Audit + Classification (~2h)
Parallel 3 Agent-Audits + 1 Atlas-Synthesis.

### Phase-2: [Atlas-Sprint-G] Visualization + Agent-API (~3h)
Operator-Approval der Phase-1-Synthesis triggert Phase-2.

**Phase-2 blocked bis Phase-1 done + Operator-OK.**

---

## Phase-1: Atlas-Sprint-F — Deep-Audit

### Sub-F1 (Lens/efficiency-auditor): Script-Inventory-Audit

**Scope:** Deep-walk aller 69+ Scripts in 3 Verzeichnissen.

**Fuer jedes Script extrahieren:**
- `name`, `path`, `runtime` (bash/python/node)
- `purpose` — aus erster Kommentar-Block oder docstring
- `invoked_by` — cron? systemd? HEARTBEAT? manual? sub-script?
- `invokes` — welche anderen scripts/binaries gecalled
- `touches` — files/dirs geschrieben/gelesen (grep for paths)
- `env_vars` — benoetigte Environment-Variablen
- `alerts_to` — Discord-Webhook? Telegram? MC-API?
- `last_modified` + `last_invoked` (log-tail-heuristik)
- `status` — active / archive / broken (via dry-run-test)
- `lifecycle_risk` — high/medium/low (z.B. cleanup-cron = high-risk)

**Output:** `workspace/memory/ops-scripts-audit.jsonl` (1 script per line).

**Methode:** Lens schreibt Python-Parser der scripts-dirs scannt, grep-based metadata-extraction, dry-run where safe.

**Acceptance:** JSONL mit >= 60 Entries, min. 3 lifecycle_risk=high identified, report in `vault/03-Agents/lens-script-inventory-audit-2026-04-19.md`.

### Sub-F2 (Forge/sre-expert): Scheduler-Graph-Audit

**Scope:** Alle 4 Scheduler-Systeme in einheitliche Struktur.

**Scheduler-Typen:**
1. **crontab-user** (~20 entries)
2. **systemd-user-timer** (9 timers)
3. **openclaw-cron-plugin** (24 jobs in `/home/piet/.openclaw/cron/jobs.json`)
4. **HEARTBEAT-driven** (agent-heartbeats per AGENTS.md/HEARTBEAT.md)

**Fuer jede Job:**
- `scheduler_type` (crontab/systemd/openclaw-cron/heartbeat)
- `schedule` (cron-syntax, normalisiert)
- `target_script_or_command`
- `target_agent` (falls zugeordnet)
- `depends_on` (andere jobs/scripts/services)
- `alerts_on_fail`
- `expected_runtime`
- `last_success` (via log-analyse)
- `failure_mode` (silent/loud/alert/retry)

**Output:** `workspace/memory/ops-jobs-audit.jsonl` + `vault/03-Agents/forge-scheduler-graph-audit-2026-04-19.md`.

**Plus:** Forge erstellt **ersten Mermaid-Graph draft** der die top-10 kritischsten Job-Abhaengigkeiten zeigt (z.B. auto-pickup -> trigger_worker -> spawn-sub-agent -> mcp-taskboard-reaper -> gateway-health).

**Acceptance:** Mindestens 60 jobs katalogisiert, Mermaid-draft min. 10 nodes + 15 edges, 3+ circular/risk-dependencies identified.

### Sub-F3 (James/researcher): HEARTBEAT-Flow-Analysis + Best-in-Class

**Scope:** 
(a) HEARTBEAT.md Deep-Dive
- 216 Zeilen analysieren: Welche Agent-Heartbeats sind dokumentiert?
- Welche Trigger-Events? Welche Sleep-Regeln (R19 Terminal-Guard, R20 run-lifecycle-only)?
- Ist der Flow vollstaendig beschrieben oder gibt es Gaps?
- Wie stark koppelt HEARTBEAT.md an actual systemd-timer jobs?

(b) Best-in-Class Research (4 Tools):
- **systemctl timer-visualization** (systemd-run, systemd-analyze)
- **Airflow DAG-View** (task-dependencies visualization)
- **Prefect UI** (modern flow-diagram)
- **Dagster asset-lineage** (data-dependency-graph)

**Was extrahieren:**
- Top 5 **steal-this-patterns** fuer Ops-Inventory-Visualization
- Was sollte ein MC-UI-Tab enthalten um Operator **in 30s Ueberblick** zu geben?
- Wie sind Agent-Heartbeat-Chains in Multi-Agent-Systems (CrewAI, AutoGen) visualisiert?
- Machine-readable Formate (YAML/JSONL/SQL/Graph-DB) Trade-offs

**Output:** `vault/03-Agents/james-ops-visualization-research-2026-04-19.md`.

**Acceptance:** HEARTBEAT-Flow-Diagram (ASCII oder Mermaid), 4 Tool-Reviews, Top-5-Patterns, Format-Recommendation.

### Sub-F4 (Atlas-Synthesis): Phase-2 Implementation-Plan

**Scope:** Nach F1+F2+F3 done → Atlas synthesizes zu Phase-2-Plan.

**Was Atlas liefert:**
- 5 priorisierte Phase-2-Subs
- Konkrete Format-Entscheidung (JSONL format pro ops-inventory-record)
- Empfohlene Tech-Stack fuer Visualization (Mermaid? D3? React-Flow?)
- Storage-Decision (workspace/memory/*.jsonl vs SQLite vs Graph-DB)
- Refresh-Strategy (manual-run vs daily-cron vs file-watcher)
- Agent-API-Design (MCP-tool? QMD-Collection? REST-endpoint?)

**Output:** `vault/03-Agents/atlas-ops-inventory-phase2-plan-2026-04-19.md`.

**Acceptance:** 5 Phase-2-Subs definiert, Tech-Stack entschieden, ready-for-Operator-Approval.

---

## Phase-2: Atlas-Sprint-G — Visualization + Agent-API (nach Approval)

### Provisorische Sub-Tasks (finalisiert nach Phase-1)

**Sub-G1 (Forge): Structured Ops-Inventory-Store**
- `workspace/memory/ops-inventory.jsonl` (scripts + jobs + heartbeats + systemd-units als einheitliche records)
- Python-Script `ops-inventory-build.py` das nachts aktualisiert
- JSON-Schema dokumentiert

**Sub-G2 (Pixel): MC-UI `/ops` Tab**
- Visueller Dependency-Graph (Mermaid oder React-Flow)
- Filterbar: by-scheduler, by-agent, by-risk, by-last-run-status
- Drill-down per Script/Job: purpose, dependencies, logs-tail, last-N-runs
- Mobile-responsive

**Sub-G3 (Forge): Agent-Discoverable API**
- MCP-Tool `ops_query` (stdio) oder REST `/api/ops/inventory`
- Query-Typen: by-name, by-schedule-type, by-agent, dependencies-of, dependents-of
- Integration mit QMD-Collection 'ops' so Atlas via `search` findet

**Sub-G4 (Atlas/Forge): Auto-Refresh + Cron**
- Daily 2am cron rebuilds ops-inventory.jsonl (parse scripts + crontab + systemd + openclaw-cron + HEARTBEAT)
- File-watcher fuer neue Scripts in 3 dirs → incremental-index
- QMD re-index der ops-Collection

**Sub-G5 (Atlas): AGENTS.md Update + Rule R43**
- AGENTS.md Section "Ops-Inventory-Discovery" — "Wenn du fragst 'was macht Script X?' nutze ops_query statt File-Read"
- Rule R43 in feedback_system_rules.md: "Scripts + Crons + Heartbeats MUESSEN im Ops-Inventory gelistet sein. Neue Scripts: add to inventory im selben commit."

### Stop-Bedingungen Phase-2
- Falls Phase-1 zeigt dass HEARTBEAT.md komplett neu geschrieben werden muss → Scope-Re-Review
- Falls Dependency-Graph > 100 nodes → Focus auf Top-3-Clusters, Rest als Follow-up

---

## Acceptance + Success-Metrics

| Metric | Phase-1 Target | Phase-2 Target |
|---|---|---|
| Scripts katalogisiert | >= 60 | 100% der 69+ |
| Jobs in JSONL | n/a | 60+ (alle 4 Scheduler) |
| Heartbeat-flows dokumentiert | ASCII/Mermaid-Draft | Visualized in UI |
| MC-Tab `/ops` live | n/a | 200 OK + Mermaid rendered |
| Agent-API `ops_query` | n/a | callable via MCP |
| Dependencies identified | 3+ circular/risk | 100% mapped |
| Commits + Deploy-Verify | n/a | Alle via R42 curl-verify |

## Risiken + Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| F1 findet 100+ Scripts (Scale-Explosion) | mittel | mittel | Atlas-Synthesis priorisiert, Rest als backlog |
| F2 Mermaid-Graph wird unlesbar (zu viele Edges) | mittel | mittel | Top-10 clusters, sub-graphs per domain |
| F3 HEARTBEAT.md hat sich veraendert | niedrig | niedrig | James wacht auf R33/R19/R20 rules |
| G1 jsonl-store growth unbounded | niedrig | mittel | append-only + compact-daily |
| G2 UI-Build-Storm durch Pixel | mittel | hoch | Sequenziell, wie Sprint-E |
| G3 MCP-tool-registration konflikt mit qmd/taskboard | niedrig | mittel | Namespace explicit: `ops_*` prefix |

## Rules die greifen

- **R33** Cron-Script-Pfad-Integritaet — Ops-Inventory validiert dies automatisch
- **R35** Atlas-Self-Report ≠ Board-Truth — Reports in Vault, file-verify
- **R41** QMD vor File-Read — neue `ops`-Collection
- **R42** Deploy-Verify-Contract — alle Phase-2 UI-subs via curl
- **R43** (neu, after Phase-2) Ops-Inventory-Discipline

## Signoff

Operator (pieter_pan) 2026-04-19 16:00 UTC. Plan ready, Phase-1 kann sofort starten, Phase-2 nach Operator-Approval.
