# 03-Projects — Active Projects & Plans

**Purpose:** In-flight project workspaces, plans, roadmaps, reports.
**Writers:** Human + agents at operator request.
**Readers:** Anyone.

## Structure
- `<project-name>/` — per-project workspace (e.g. `Mission-Control/`)
- `plans/` — architecture & roadmap docs
- `reports/` — audits, analyses, post-sprint reports
- flat `.md` — single-file projects

## Rules
- Sprint-specific docs live in `04-Sprints/`, not here. If a plan turns into a sprint, `git mv` it.
- Reports touching incidents go to `05-Incidents/`; touching research go to `07-Research/`.

## Never touch
- Mission-Control live source code (it lives under `.openclaw/workspace/mission-control/`, not here).
