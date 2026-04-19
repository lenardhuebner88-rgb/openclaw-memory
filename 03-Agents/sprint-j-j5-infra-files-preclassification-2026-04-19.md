---
title: Sprint-J J5 Infra-Files Pre-Classification (Forge Time-Saver)
date: 2026-04-19 20:15 UTC
author: Assistant (Claude) — Pre-Analysis for Forge-Dispatch
source: git status + diff inspection 2026-04-19 20:13 UTC
type: forge-handoff-helper
---

# J5 Infra-Files Pre-Classification — Empfohlene Disposition

Forge: diese Tabelle gibt dir eine **pre-analyzed recommendation** pro File. Du verifyest + commitest. Spart dir die git-diff-Walk-Zeit.

## Kategorie A — INTENTIONAL (git commit empfohlen)

| File | Diff-Summary | Empfohlener Commit-Scope | Commit-Message |
|---|---|---|---|
| `next.config.ts` | +10 Zeilen `redirects: /pipeline → /kanban` | Sprint-E E4 Unified-Nav | `chore(sprint-e): persist pipeline→kanban redirect from unified nav` |
| `package.json` | +1 script `typecheck`, +1 dep `fuse.js@^7.3.0` | Sprint-E E2 Command-Palette | `chore(sprint-e): add fuse.js for command palette + typecheck script` |
| `package-lock.json` | paired mit package.json | Sprint-E E2 | (same commit as package.json) |
| `playwright.config.ts` | +2 env vars `OPENCLAW_MONITORING_LOG_DIR` + `OPENCLAW_MONITORING_CRONTAB_PATH` | Sprint-G Ops monitoring-fixture | `test(sprint-g): add monitoring fixture env vars for playwright` |
| `scripts/build.mjs` | Major refactor: `acquireLockWithWait()` function — fixes "aborting after lock-release"-bug vom 2026-04-17 | Critical build-stability fix | `fix(build): retain probe-lock after successful wait instead of abort` |
| `scripts/stability-preflight.mjs` | (diff not shown but intentional) | Likely paired with build.mjs | `chore(stability): update preflight paired with build.mjs fix` |
| `scripts/start-singleton.mjs` | (diff not shown) | Likely build-related | `chore(build): update singleton start script` |
| `deploy.sh` | (diff not shown) | Likely deployment improvement | `chore(deploy): update deploy.sh` (verify diff first!) |
| `src/app/api/agents/concurrency/route.ts` | INTENTIONAL code | Sprint-G or earlier | `feat(agents): update concurrency endpoint` |
| `src/app/api/costs/seed/route.ts` | INTENTIONAL code | Sprint-F/G Ops | `feat(costs): update seed route` |
| `src/app/api/cron-jobs/[id]/route.ts` | INTENTIONAL code | Sprint-G Ops-Dashboard | `feat(ops): cron-jobs crud route updates` |
| `src/app/api/discord/send/route.ts` | INTENTIONAL code | evolving | `chore(discord): update send route` |
| `src/app/api/execution-report/dispatch/route.ts` | INTENTIONAL code | — | `feat(exec-report): dispatch updates` |
| `src/app/api/execution-report/route.ts` | INTENTIONAL code | — | `feat(exec-report): route updates` |
| `src/app/api/files/route.ts` | INTENTIONAL code | — | `feat(files): route updates` |

**Commits aufteilen:** Nicht alle in einen — pro Sprint-Scope gruppieren. 5-7 Commits erwartbar.

## Kategorie B — DATA-DRIFT (git restore, NICHT committen)

| File | Typ | Action |
|---|---|---|
| `data/board-events.json` | Runtime Board-Events | `git restore data/board-events.json` **NIEMALS committen** |
| `data/board-events.jsonl` | Runtime Board-Events | `git restore` |
| `data/tasks.json` | Runtime Task-Store | `git restore` (wird zur Laufzeit constantly neu geschrieben) |
| `data/thread-audit-kpi-baseline.json` | KPI-Baseline runtime | `git restore` UNLESS intentional baseline-update (frag Operator) |
| `data/worker-runs.json` | Runtime Worker-Runs | `git restore` |
| `qa/brain-retrieval-smokepack.json` | Test-config (könnte beides sein) | diff-check; meist DATA-DRIFT |
| `qa/results/brain-retrieval-smokepack.latest.json` | Test-Output | `git restore` (Test-Results fluktuieren) |
| `e2e/fixtures/data/tasks.json` | E2E-Fixture | diff-check: wenn intentional Test-Update → commit; sonst restore |

**Post-Restore-Check:** `git status --short | grep '^ M data/'` sollte danach leer sein (außer intended fixture-updates).

## Kategorie C — DELETED files (intentional)

| File | Typ | Action |
|---|---|---|
| `data/tasks.backup-pre-casing-normalization.json` | alter Backup | `git add -u` (commit the delete) |
| `data/tasks.backup-pre-migration.json` | alter Backup | `git add -u` |
| `data/tasks.json.ARCHIVED` | alter Archive | `git add -u` |
| `data/tasks.json.backup-pre-merge` | alter Backup | `git add -u` |
| `data/tasks.json.bak-maxretries-151846` | alter Backup | `git add -u` |
| `data/tasks.json.bak.hygiene-2026-04-02` | alter Backup | `git add -u` |
| `data/tasks.json.bak16` | alter Backup | `git add -u` |
| `docs/AUDIT-PIXEL-UI-2026-04-12.md` | moved to Vault | `git add -u` |
| `docs/BRAIN_PROMOTION_CONTRACT.md` | moved to Vault | `git add -u` |
| `docs/LENS-AUDIT-SPRINT-PLAN-2026-04-12.md` | moved to Vault | `git add -u` |
| `docs/MC-PROD-AUDIT-2026-04-11.md` | moved to Vault | `git add -u` |
| `docs/SPRINT-3-EXECUTIVE-CONTRACT.md` | moved to Vault | `git add -u` |
| `docs/execution-report-channel.md` | moved to Vault | `git add -u` |
| `docs/taskboard-mobile-first-render-smoke.md` | moved to Vault | `git add -u` |
| `src/app/api/agents/live/route.ts.bak.20260413103338` | stale .bak | `git add -u` |
| `src/app/api/costs/anomalies/route.ts.bak-costs-pack4-2026-04-17` | stale .bak | `git add -u` |
| `src/app/api/costs/route.ts.bak-costs-pack1-2026-04-17` | stale .bak | `git add -u` |
| `src/app/api/costs/route.ts.bak-costs-pack3-2026-04-17` | stale .bak | `git add -u` |
| `src/app/api/health/route.ts.bak-stab-p2-5-2026-04-18` | stale .bak | `git add -u` |

**Batch-Commit:** `chore: remove obsolete data-backups and docs (moved to Vault)` — ein Commit für alle Deletes.

## Kategorie D — UNTRACKED .bak files (.gitignore oder DELETE)

| File | Age | Empfohlene Action |
|---|---|---|
| `next.config.ts.bak` | 7d (Apr 12) | **DELETE** — `rm next.config.ts.bak` |
| `next.config.ts.bak2` | 7d (Apr 12) | **DELETE** |
| `next.config.ts.bak-c3-2026-04-18` | 1d (Apr 18) | **KEEP** kurz-Rückfall-Option, in 48h löschen |
| `package.json.bak-p03-2026-04-19` | <1d | **KEEP** (heute erzeugt) |
| `package.json.bak-smoke-2026-04-18` | 1d | **BORDERLINE** — behalten bis Smoke-Tests stable |
| `scripts/build.mjs.bak-2026-04-17` | 2d | **KEEP** — build.mjs ist kritisch, Fallback sinnvoll |

**Future-Proof:** `.gitignore` erweitern um `*.bak*` Pattern? Pro/contra diskutieren — blocks intentional Backup-tracking.

## Empfohlener Commit-Graph (5-7 Commits)

```
1. chore: remove obsolete data-backups and docs (moved to Vault)
   — batch-deletes from Kategorie C
2. fix(build): retain probe-lock after successful wait instead of abort
   — scripts/build.mjs (critical bug)
3. chore(sprint-e): add fuse.js + typecheck for command palette
   — package.json + package-lock.json
4. chore(sprint-e): persist pipeline→kanban redirect from unified nav
   — next.config.ts
5. test(sprint-g): add monitoring fixture env for playwright
   — playwright.config.ts
6. feat(ops/sprint-g): multiple API route updates
   — src/app/api/{agents/concurrency,costs/seed,cron-jobs,discord/send,execution-report,files}/route.ts
   (split wenn Scope unterschiedlich)
7. chore(build): update stability-preflight + start-singleton + deploy.sh
   — scripts/stability-preflight.mjs + scripts/start-singleton.mjs + deploy.sh (nach Diff-Check)
```

## Report-Template für Forge

`vault/03-Agents/infra-files-cleanup-2026-04-19.md`:

```markdown
# Sprint-J J5 Infra-Files Cleanup Report

## Disposition-Tabelle

| File | Classification | Action | Commit SHA | Notes |
|---|---|---|---|---|
| next.config.ts | INTENTIONAL | commit | abc1234 | Sprint-E redirect |
| data/tasks.json | DATA-DRIFT | git restore | — | runtime |
| ... (all ~40 files) ... |

## Commit-Log

- abc1234 chore: remove obsolete data-backups
- def5678 fix(build): retain probe-lock
- ...

## Post-Cleanup git status

(should be empty or only data/*.json fluctuations)

## Findings

- Pre-Classification assistance: [link to this doc]
- Edge-Cases: ...
```

---

**Zeit-Sparer für Forge:** statt ~40 Files einzeln analysieren, nutze diese Tabelle als Start + verify pro File. Estimate von 1-1.5h auf **~45 min reduziert**.
