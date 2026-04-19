# Sprint-J J5 Infra-Files Cleanup Report

## Disposition-Tabelle

| File | Classification | Action | Commit SHA |
|---|---|---|---|
| data/tasks.backup-pre-casing-normalization.json | C (obsolete delete) | committed delete | 029fe23 |
| data/tasks.backup-pre-migration.json | C (obsolete delete) | committed delete | 029fe23 |
| data/tasks.json.ARCHIVED | C (obsolete delete) | committed delete | 029fe23 |
| data/tasks.json.backup-pre-merge | C (obsolete delete) | committed delete | 029fe23 |
| data/tasks.json.bak-maxretries-151846 | C (obsolete delete) | committed delete | 029fe23 |
| data/tasks.json.bak.hygiene-2026-04-02 | C (obsolete delete) | committed delete | 029fe23 |
| data/tasks.json.bak16 | C (obsolete delete) | committed delete | 029fe23 |
| docs/AUDIT-PIXEL-UI-2026-04-12.md | C (obsolete delete) | committed delete | 029fe23 |
| docs/BRAIN_PROMOTION_CONTRACT.md | C (obsolete delete) | committed delete | 029fe23 |
| docs/LENS-AUDIT-SPRINT-PLAN-2026-04-12.md | C (obsolete delete) | committed delete | 029fe23 |
| docs/MC-PROD-AUDIT-2026-04-11.md | C (obsolete delete) | committed delete | 029fe23 |
| docs/SPRINT-3-EXECUTIVE-CONTRACT.md | C (obsolete delete) | committed delete | 029fe23 |
| docs/execution-report-channel.md | C (obsolete delete) | committed delete | 029fe23 |
| docs/taskboard-mobile-first-render-smoke.md | C (obsolete delete) | committed delete | 029fe23 |
| src/app/api/agents/live/route.ts.bak.20260413103338 | C (obsolete delete) | committed delete | 029fe23 |
| src/app/api/costs/anomalies/route.ts.bak-costs-pack4-2026-04-17 | C (obsolete delete) | committed delete | 029fe23 |
| src/app/api/costs/route.ts.bak-costs-pack1-2026-04-17 | C (obsolete delete) | committed delete | 029fe23 |
| src/app/api/costs/route.ts.bak-costs-pack3-2026-04-17 | C (obsolete delete) | committed delete | 029fe23 |
| src/app/api/health/route.ts.bak-stab-p2-5-2026-04-18 | C (obsolete delete) | committed delete | 029fe23 |
| scripts/build.mjs | A (intentional) | committed change | 885d153 |
| package.json | A (intentional) | committed change | e6e8b10 |
| package-lock.json | A (intentional) | committed change | e6e8b10 |
| next.config.ts | A (intentional) | committed change | ae76db4 |
| playwright.config.ts | A (intentional) | committed change | e2cf16e |
| src/app/api/agents/concurrency/route.ts | A (intentional) | committed change | 3acd39a |
| src/app/api/costs/seed/route.ts | A (intentional) | committed change | 3acd39a |
| src/app/api/cron-jobs/[id]/route.ts | A (intentional) | committed change | 3acd39a |
| src/app/api/discord/send/route.ts | A (intentional) | committed change | 3acd39a |
| src/app/api/execution-report/dispatch/route.ts | A (intentional) | committed change | 3acd39a |
| src/app/api/execution-report/route.ts | A (intentional) | committed change | 3acd39a |
| src/app/api/files/route.ts | A (intentional) | committed change | 3acd39a |
| scripts/stability-preflight.mjs | A (intentional) | committed change | c2fa810 |
| scripts/start-singleton.mjs | A (intentional) | committed change | c2fa810 |
| deploy.sh | A (intentional) | committed change | c2fa810 |
| data/board-events.json | B (data-drift) | git restore | — |
| data/board-events.jsonl | B (data-drift) | git restore | — |
| data/tasks.json | B (data-drift) | git restore | — |
| next.config.ts.bak | D (>3d .bak) | deleted (untracked) | — |
| next.config.ts.bak2 | D (>3d .bak) | deleted (untracked) | — |

## Commit-Log (7)

- 029fe23 chore: remove obsolete data-backups and docs
- 885d153 fix(build): retain probe-lock after successful wait
- e6e8b10 chore(sprint-e): add fuse.js + typecheck for command palette
- ae76db4 chore(sprint-e): persist pipeline→kanban redirect
- e2cf16e test(sprint-g): monitoring fixture env for playwright
- 3acd39a feat(sprint-g): multiple API route updates
- c2fa810 chore(build): stability-preflight + start-singleton + deploy.sh
