---
sprint-id: S-HANDBOOK
priority: P1
name: System Handbook + Agent Acceleration Plan
description: Incremental rollout plan for a living system handbook generated from live registries, scripts, git history, and runtime health so agents stop re-scanning the whole workspace.
status: done
since: 2026-04-21
owner: Operator (piet)
author: Codex
origin: research + local inventory pass 2026-04-21
---
# System Handbook + Agent Acceleration Plan - 2026-04-21

**Typ:** dedicated implementation plan / operator handover  
**Status:** ready-for-Atlas  
**Primary goal:** reduce agent orientation time and drift by replacing scattered manual ops docs with a generated, versioned, agent-friendly system handbook.  
**Recommended stack:** MkDocs + Material for MkDocs + Mermaid + local generators.  
**Explicit non-goal for phase 1:** do not start with Backstage, do not hand-write a giant wiki, do not build a second truth layer outside the repo.

---

## 1. Why this exists

The workspace already has strong orientation docs, but they are not yet bridged into a durable machine-generated handbook.

### Proven local baseline

- `README.md`, `CONTEXT_MAP.md`, and `docs/operations/WORKSPACE-GROUND-TRUTH.md` already define truth-order and operator entrypoints.
- `docs/operations/CRON.md` is stale relative to live runtime.
- `/home/piet/.openclaw/cron/registry.jsonl` and `/home/piet/.openclaw/cron/jobs.json` already contain machine-readable scheduler truth.
- `/home/piet/.openclaw/cron/cron-reconciler.py` already compares registry vs live crontab vs OpenClaw jobs vs systemd timers.
- Runtime health artifacts already exist, e.g. `workspace/logs/ops-health.json`.
- Git history already contains meaningful "what changed" information, but agents currently have to mine it ad hoc.

### Current friction that this plan must remove

- Agents still need broad `rg`/file crawling for simple structure questions.
- Scheduler truth is fragmented across `crontab`, `jobs.json`, systemd timers, docs, and logs.
- Script responsibility is discoverable only by reading scripts and commit history manually.
- Existing docs drift because they are mostly hand-maintained.
- There is no single short agent bootstrap pack for "how this system is organized today".

---

## 2. Target state

Build a **living system handbook** inside the workspace that has 3 layers:

1. **Machine catalog**
   - canonical generated metadata from registries, scripts, git, and health artifacts
2. **Generated handbook pages**
   - human-readable pages under `docs/system/`
3. **Short curated front door**
   - a tiny bootstrap doc for agents and operators that points into the generated pages

### Expected operator outcome

- one stable front door for system structure
- one generated view for cron/jobs/scripts
- one generated view for "what changed recently"
- a small set of high-signal process diagrams
- drift becomes visible instead of silent

### Expected agent outcome

- less whole-repo searching
- faster startup on cron/script/system questions
- fewer wrong assumptions about production paths and scheduler ownership
- shorter context windows because the right entry docs are small and deterministic

---

## 3. Operating principles

1. **Live verification beats documentation.**
2. **Generated docs outrank hand-written summaries** for inventory-style facts.
3. **Curated docs stay short** and only explain structure, rules, and exceptions.
4. **One source, many views:** registries/logs/git feed both docs and optional UI later.
5. **Do not build a giant bespoke dashboard first.** Build the data model and docs first.
6. **Do not model everything manually.** Only high-value flows get diagrams.

---

## 4. Sprint map

| Sprint | Title | Goal | Estimate | Primary owner |
|---|---|---|---|---|
| **SH1** | Truth Freeze + Catalog Contract | define scope, sources, schema, ownership model | 0.5-1 day | Atlas |
| **SH2** | Generator MVP | generate jobs/scripts/changes pages from live sources | 1-2 days | Atlas |
| **SH3** | Runtime Health + Overrides | add owner/domain/runbook/health overlays | 1-1.5 days | Atlas |
| **SH4** | Flow Maps + Diagrams | add Mermaid flow docs for critical processes | 1-2 days | Atlas |
| **SH5** | Agent Bootstrap + Retrieval | make the handbook the default agent entrypoint | 0.5-1 day | Atlas |
| **SH6** | Publish + Drift Guard | MkDocs site, scheduled regeneration, stale-doc checks | 1-1.5 days | Atlas |
| **SH7** | Optional UI Layer | only after docs are stable: admin pages based on same catalog | optional later | Atlas + Pixel |

---

## 5. Sprint details

## SH1 - Truth Freeze + Catalog Contract

### Objective

Freeze the first durable contract for what the handbook will describe and which files count as source inputs.

### Inputs

- `/home/piet/.openclaw/cron/registry.jsonl`
- `/home/piet/.openclaw/cron/registry.schema.json`
- `/home/piet/.openclaw/cron/jobs.json`
- live `crontab -l`
- `systemctl --user list-timers`
- `/home/piet/.openclaw/scripts/`
- `/home/piet/.openclaw/workspace/scripts/`
- `workspace/logs/*.json`
- workspace git history
- existing orientation docs in workspace root and `docs/operations/`

### Work packages

1. Create `docs/system/` as the future handbook root.
2. Define `catalog.schema.json` or `catalog.schema.yaml` for handbook entities.
3. Decide the first entity kinds:
   - `job`
   - `script`
   - `flow`
   - `status_artifact`
4. Define mandatory fields:
   - `id`
   - `kind`
   - `name`
   - `source_of_truth`
   - `owner`
   - `domain`
   - `entrypoint`
   - `schedule`
   - `dependencies`
   - `outputs`
   - `logs`
   - `last_changed_commit`
   - `last_verified`
5. Define a small overrides file for data not derivable automatically:
   - `docs/system/catalog-overrides.yaml`
6. Write a short handbook root page:
   - what exists
   - what is generated
   - what remains curated

### Deliverables

- `docs/system/README.md`
- `docs/system/catalog.schema.*`
- `docs/system/catalog-overrides.yaml`
- `docs/system/SOURCES.md`

### Acceptance

- every future generator has a stable schema target
- no entity depends on free-form manual prose for basic inventory facts
- source-of-truth paths are explicit and ordered

---

## SH2 - Generator MVP

### Objective

Generate the first useful handbook pages directly from live machine-readable inputs.

### Work packages

1. Build a generator script, e.g. `scripts/system-handbook/generate.py`.
2. Generate:
   - `docs/system/jobs/index.md`
   - `docs/system/scripts/index.md`
   - `docs/system/changes/last-7-days.md`
3. For jobs, merge:
   - cron registry
   - OpenClaw cron jobs
   - live crontab
   - systemd timers
4. For scripts, scan:
   - `.openclaw/scripts`
   - `workspace/scripts`
5. For each item, include:
   - path
   - purpose stub
   - scheduler binding if known
   - last modified commit
   - last filesystem touch
   - related logs if derivable
6. Emit a machine file too:
   - `docs/system/catalog.json`

### Deliverables

- generator script
- first generated catalog JSON
- first generated jobs/scripts/changes pages

### Acceptance

- an operator can answer "which cron/job/script exists?" from generated pages
- generated jobs page covers more than the stale `CRON.md`
- generation is deterministic and rerunnable

---

## SH3 - Runtime Health + Overrides

### Objective

Layer runtime state and human ownership on top of the MVP catalog without breaking deterministic generation.

### Work packages

1. Parse status artifacts such as `workspace/logs/ops-health.json`.
2. Add optional owner/domain/runbook metadata from `catalog-overrides.yaml`.
3. Add generated pages:
   - `docs/system/status/index.md`
   - `docs/system/jobs/health.md`
4. Surface for each critical job:
   - last run
   - exit code
   - current alert state
   - linked log path
5. Add a "missing metadata" report so incomplete ownership is visible.

### Deliverables

- health/status generator support
- generated status pages
- metadata gap report

### Acceptance

- at least the top critical jobs have owner + log + health coverage
- missing ownership no longer hides silently

---

## SH4 - Flow Maps + Diagrams

### Objective

Document only the highest-value process paths as diagrams and short narrative docs.

### Initial flows

- heartbeat / pickup / dispatch
- memory orchestrator
- QMD update / embed / query
- session guard / worker monitor / alert path
- taskboard + receipt + result lifecycle

### Work packages

1. Create `docs/system/flows/`.
2. Add one page per flow with:
   - purpose
   - trigger
   - main steps
   - failure points
   - linked jobs/scripts
3. Render Mermaid diagrams in the docs.
4. Keep each flow page short and reference generated entities instead of duplicating them.

### Deliverables

- 5 high-signal flow pages
- Mermaid diagrams embedded in docs

### Acceptance

- an agent can understand major process ownership without reading all involved scripts
- diagrams describe process relationships, not implementation trivia

---

## SH5 - Agent Bootstrap + Retrieval

### Objective

Make the handbook the new default narrow entrypoint for agents.

### Work packages

1. Add `docs/system/AGENT_BOOTSTRAP.md` capped to a small size.
2. Update relevant root docs to point to the new system handbook entrypoint.
3. Add an "if you need X, read Y" routing table:
   - cron/jobs
   - scripts
   - runtime truth
   - recent changes
   - process maps
4. If retrieval config allows, prioritize handbook pages in QMD indexing/ranking.
5. Add a note for agents:
   - read handbook first
   - fall back to repo-wide search only if handbook is insufficient

### Deliverables

- `docs/system/AGENT_BOOTSTRAP.md`
- root doc links updated
- retrieval note / ranking change if feasible

### Acceptance

- common orientation questions can be answered from bootstrap + handbook without broad search
- bootstrap stays intentionally small

---

## SH6 - Publish + Drift Guard

### Objective

Publish the handbook as a static site and add drift detection so stale summaries become visible quickly.

### Work packages

1. Add MkDocs config at workspace root or under docs tooling path.
2. Enable Material for MkDocs and Mermaid support.
3. Add a scheduled regeneration task, e.g. nightly or hourly depending on cost.
4. Add a stale-doc check:
   - references to missing files
   - pages older than threshold
   - generated pages out of sync with sources
5. Emit one operator-facing report:
   - `docs/system/status/drift-report.md`

### Deliverables

- `mkdocs.yml`
- build script
- scheduled regeneration hook
- drift report

### Acceptance

- docs site builds locally
- generated pages refresh on schedule
- broken references and stale generated pages are reported automatically

---

## SH7 - Optional UI Layer

### Objective

Only after SH1-SH6 are stable, expose the same catalog in Mission Control or another UI.

### Constraint

Do not invent a separate backend or separate metadata model. UI must read the same generated catalog or same generator outputs.

### Possible additions

- `/admin/system-handbook`
- `/admin/crons`
- ownership filters
- "last changed" cards
- health summary views

### Acceptance

- UI is a view over the same truth, not a second truth source

---

## 6. Definition of done for the whole initiative

The initiative is done when all of the following are true:

- there is one stable handbook root under `docs/system/`
- cron/jobs/scripts are generated, not manually curated
- recent changes are visible without ad hoc git mining
- critical process maps exist
- agents have a short bootstrap pack
- docs are rebuilt on schedule
- drift is detected automatically

---

## 7. Risks and anti-patterns

### Do not do this

- do not start with Backstage
- do not build a giant manual wiki first
- do not keep duplicate cron inventories in multiple markdown files
- do not make diagrams for every script
- do not let generated pages contain hand-edited facts

### Main risks

- schema too vague in SH1
- generator overreach in SH2
- hidden ownership gaps in SH3
- too many diagrams in SH4
- oversized bootstrap in SH5
- site build without drift checks in SH6

---

## 8. Recommended implementation order

1. Finish SH1 fully before coding generators.
2. Finish SH2 before editing root docs heavily.
3. Finish SH3 before claiming operator-readiness.
4. Finish SH4 and SH5 before changing agent startup habits.
5. Finish SH6 before calling the handbook durable.
6. Treat SH7 as optional and only after the docs layer proves useful.

---

## 9. Atlas execution contract

Atlas should execute **one sprint at a time**, commit intentionally, and avoid broad side refactors while building the handbook.

### Atlas constraints

- prefer incremental, reviewable diffs
- generated outputs must be reproducible
- do not overwrite existing truth docs blindly
- if a handbook page conflicts with live runtime, fix the generator or source mapping, not the runtime story in prose
- keep hand-written pages short and structural

---

## 10. Atlas trigger prompt

Use this prompt to start Atlas on **SH1 only**:

```text
Setze Sprint SH1 aus `vault/04-Sprints/system-handbook-agent-acceleration-plan-2026-04-21.md` um.

Arbeite nur an SH1, nicht an SH2+.

Ziele:
- `docs/system/` als neue Handbook-Root anlegen
- Quellen und Truth-Order sauber dokumentieren
- ein stabiles Catalog-Schema definieren
- ein kleines `catalog-overrides.yaml` fuer owner/domain/runbook vorbereiten

Wichtige Regeln:
- keine breite Repo-Refaktorierung
- keine UI bauen
- keine Backstage-Einfuehrung
- keine grossen Root-Dokumente umschreiben
- generated-vs-curated sauber trennen

Lies zuerst:
1. `README.md`
2. `CONTEXT_MAP.md`
3. `docs/operations/WORKSPACE-GROUND-TRUTH.md`
4. `/home/piet/.openclaw/cron/registry.schema.json`
5. `/home/piet/.openclaw/cron/cron-reconciler.py`
6. diese Plan-Datei

Ergebnis:
- liefere die SH1-Dateien
- fasse offene Entscheidungen und Rest-Risiken knapp zusammen
- noch keine Generator-Implementierung ausser wenn sie direkt fuer Schema-Validierung noetig ist
```

---

## 11. Operator checkpoint after each sprint

After each sprint Atlas should report only:

- what was added
- what became the new source entrypoint
- what remains manual
- what still drifts
- what should happen next

That keeps the rollout disciplined and prevents another documentation sprawl.
