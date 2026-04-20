# Codex Independent Review — Sprint-M (2026-04-20)

## Verdict
APPROVE-WITH-MODS

## Summary (≤ 150 words)
Sprint-M is directionally correct: fixing the checker before consolidating schedulers is the right order, and the plan stays within the existing `systemd` / `crontab` / `openclaw-cron` stack. But the current draft is not dispatch-ready. Several live claims in the source analysis are already stale or wrong at review time, the review-gate mislabels task numbers, M4 targets the wrong script, M5 references a nonexistent `openclaw cron set` command, and multiple DoDs are not actually executable within the claimed 16-22h window. I would not reject the architecture; I would require a narrow rewrite of task numbering, live baselines, M4/M5 scope, rollback naming, and verification gates before dispatch.

## Findings by Dimension
### D1 Claim-Verification
`openclaw-cron-heartbeat-analysis-2026-04-20.md:40-47` says `44` crontab entries and `66` active schedules. Live now says otherwise: `crontab -l | grep -v '^#' | grep -v '^$' | wc -l` => `50`, and the HEARTBEAT counting method `... | grep -v '=' | wc -l` => `45`, so the current baseline is not `44`. `systemctl --user list-timers --no-pager` still shows `6 timers listed`, and `jq '.jobs | map(select((.enabled // true) == false)) | length' ~/.openclaw/cron/jobs.json` => `0`, so the `16 enabled / 0 disabled` correction holds. `git -C /home/piet/.openclaw status --short` still returns `fatal: not a git repository`, so the Git gap holds. One corrected claim is itself wrong: analysis `:47` says openclaw-cron jobs have `lastRun: null`, but `jq '.jobs | map(select(.state.lastRunAtMs == null)) | length'` => `0` and `.state.lastStatus == null` => `0`.

### D2 Scope-Completeness
Phase 0 + Phase 1 are mostly represented: regex/path fixes, registry, reconciler, memory consolidation, systemd migration. The main omission is that M4 targets the wrong codepath. The live ENV false-positive mechanism is in [`/home/piet/.openclaw/scripts/script-integrity-check.sh:119`](/home/piet/.openclaw/scripts/script-integrity-check.sh:119)-[/home/piet/.openclaw/scripts/script-integrity-check.sh:144](/home/piet/.openclaw/scripts/script-integrity-check.sh:144), not in [`/home/piet/.openclaw/scripts/cron-health-audit.sh:22`](/home/piet/.openclaw/scripts/cron-health-audit.sh:22)-[/home/piet/.openclaw/scripts/cron-health-audit.sh:79](/home/piet/.openclaw/scripts/cron-health-audit.sh:79). There is also unresolved overlap with H10: the plan frontmatter points to `memory/sprint_k_infra_hardening_plan.md`, but the actual upstream doc is [sprint-k-infra-hardening-plan-2026-04-19.md](/home/piet/vault/03-Agents/sprint-k-infra-hardening-plan-2026-04-19.md), and H10 already contains Layer 2 memory consolidation and Layer 3 timer migration.

### D3 Dependency-Graph
The graph is internally inconsistent. In the M0 review scope, plan lines `46-49` call M4 the reconciler and M5 the memory orchestrator, but the actual tasks are M5=reconciler, M6=memory orchestrator, M7=systemd migration. That means the review gate is asking the wrong dependency questions. The execution graph also allows clobber paths: M4 changes crontab schedule and adds a canary, while M5 writes crontab from registry; Wave 2 runs `M2 + M4` parallel to `M5` (`plan:354-356`), so M5 can overwrite M4 unless registry updates are ordered first. M6 is another contradiction: task header says `Depends on: M3, can run parallel to M5` (`plan:259`), but the DAG puts M6 after M5 (`plan:356`).

### D4 DoD-Quality
Several DoDs are not falsifiable enough or point to nonexistent hooks. M1 says `script-integrity-check invokes it` (`plan:121`), but live grep shows no such integration; [script-integrity-check.sh](/home/piet/.openclaw/scripts/script-integrity-check.sh:1) never calls `cron-health-audit.sh`. M5 says openclaw-cron updates happen via `openclaw cron set <name> ...` (`plan:239`), but `openclaw cron --help` exposes only `add`, `edit`, `enable`, `disable`, `rm`, `run`, `runs`, `status`; there is no `set`. M4 requires “first canary received” (`plan:220`), M7 requires a `24h` soak (`plan:297`), and M8 wants all `66` entries to have `lastRun + lastStatus` populated (`plan:323`) even though the live baseline is `67` schedules and several cadences are daily/weekly. Those are not 16-22h sprint-close criteria.

### D5 Rollback-Integrity
Rollback is not isolated enough yet. Backup names like `cron-health-audit.sh.bak-m1-2026-04-20` (`plan:122`) and the global restore pattern `.bak-m*-2026-04-20` (`plan:396`) are not unique across repeated same-day attempts. M7 updates registry state (`plan:295`) but its rollback only disables timers and re-enables crontab lines (`plan:399`); registry rollback is missing. M6 rollback is explicitly manual surgery (`plan:398`) rather than a single bounded undo path, which weakens the claim that rollback is per-task isolated (`plan:402`).

### D6 Rule-Compliance
R44, R45 and R47 are mostly respected: M0 uses board tasks and operator lock correctly (`plan:34-99`, `feedback_system_rules.md:331-341`, `AGENTS.md:13-18`). R34 is not a blocker: `wc -c ~/.openclaw/workspace/MEMORY.md` => `11165`, while `openclaw.json` has `bootstrapMaxChars: 32768`. The main rule breach is R33: the proposed canary cron line in M4 (`plan:212`) has no `flock`, while R33 requires cron entries to use local locks (`feedback_system_rules.md:234-239`). R8 is also incomplete: only M1 explicitly mandates a pre-edit backup; M2-M4 all mutate the same script or crontab without equivalent backup requirements.

### D7 Cost / Over-Engineering
M5 is the clearest resume-padding candidate. A full cross-scheduler writer is the highest-risk component in the sprint, but a read-only `registry + validator + drift diff` already unlocks M2 and produces most of the operational value. That alone can cut roughly `2-4h` and remove the most dangerous apply path. M6 can also reuse H10’s existing `memory-maintenance-suite.sh` concept (`sprint-k-infra-hardening-plan-2026-04-19.md:197-211`) instead of inventing a fresh orchestrator shape. The 16-22h estimate is low as calendar time because it ignores a 6h canary receipt window and a 24h soak gate.

### D8 Industry-Delta
The plan is aligned on the high-level pattern: registry, reconciler, systemd timers, canary alerting. It is still behind on execution semantics. H10 already captured why timer migration matters: `Persistent=true` for missed-run recovery and `OnFailure=` hooks (`sprint-k-infra-hardening-plan-2026-04-19.md:213-227`), but Sprint-M M7 specifies only `Restart=on-failure` and `StartLimitBurst` (`plan:290-297`). One concrete strengthening pattern without redesign: each scheduler writes a structured run receipt JSONL record (`job`, `scheduled_at`, `started_at`, `finished_at`, `status`) and the audit consumes that ledger instead of log mtimes.

### D9 Risk-Blindspots
Missing risks are more operational than architectural. First, M4/M5/M6 all touch crontab and can race each other. Second, M7 has a duplicate-fire window if timers are enabled before cron lines are disabled and locks drained. Third, registry bootstrap is based on stale counts: if the plan seeds `66` while live is already `67`, the reconciler can encode drift on day one. Fourth, the plan does not mention `systemd --user` bus or linger assumptions even though M7 depends on timer reliability for minute-level jobs.

### D10 Review-Gate-Design
M0 is the right idea, but the receipt schema is not operator-mergeable yet. Atlas uses `APPROVE | APPROVE_WITH_MODS | REJECT` while Lens uses `APPROVE | SIMPLIFY | REJECT`; “SIMPLIFY” is semantically close to “APPROVE_WITH_MODS” but not equivalent. Use one matrix: `verdict`, `blocking_mods[]`, `non_blocking_mods[]`, `cost_delta_h`, `risk_delta`. Decision rule: both `APPROVE` => go; any `REJECT` => halt; otherwise merge all `blocking_mods`, bump plan version, re-review only affected sections.

## Required Modifications (if APPROVE-WITH-MODS)
1. `[M0/M3/M4/M5/M6/M7]` — fix task-number references and dependency graph, and make `M4 -> registry update -> M5 apply` explicit — current review gate asks the wrong questions and allows clobber races.
2. `[M4]` — move ENV-cross-check work from `cron-health-audit.sh` to `script-integrity-check.sh`, and add `flock` to the canary cron line — current task targets the wrong script and violates R33.
3. `[M5]` — replace `openclaw cron set` with the real CLI contract or reduce M5 to read-only diff in Sprint-M — current apply path references a command that does not exist.
4. `[M1/M4/M7/M8]` — rewrite DoDs to bounded pass/fail checks, update live baseline from `66` to the current count, and use timestamped backup names — current completion gates are partially unmeasurable or exceed the stated sprint window.

## Optional Improvements
- Reuse the H10 Layer-2 shape instead of inventing a new memory orchestrator interface.
- Add `Persistent=true` and `OnFailure=` explicitly to M7 so the migration captures the actual systemd reliability gains.
- Add a “re-baseline live counts before M3” pre-step to avoid baking stale inventory into the registry.

## Revised Effort Estimate
Plan claims 16-22h. My estimate: 19-26h hands-on, plus 24h soak/canary wall-clock.

Per-sub breakdown:
- M0 review gate: `0.75-1h`
- M1 regex/tests: `2-3h`
- M2 path/registry audit refactor: `2-3h`
- M3 registry re-baseline + validator: `2-3h`
- M4 ENV/canary/schedule fixes: `1-2h`
- M5 reconciler: `2-3h` if diff-only, `5-7h` if full writer
- M6 memory consolidation: `1.5-3h`
- M7 timer migration: `3-4h` hands-on + `24h` soak
- M8 final audit/baseline/report: `1-2h`

## Top-3 Risks I'd Add
1. Crontab write races between M4, M5 and M6 produce partial or reverted scheduler state.
2. M7 creates a double-fire or no-fire window during cutover if timers and old cron lines overlap or stale locks persist.
3. Registry seeding from stale inventory (`66` vs current live count) causes the reconciler to introduce drift immediately.

## Questions for Operator
1. Soll M5 in Sprint-M bewusst auf `read-only diff + validator` reduziert werden, mit `--apply` erst in einem Folgepack?
2. Soll Sprint-M H10 formell superseden, oder willst du H10 amendieren statt parallele Plan-Dokumente fuer dieselbe Infra-Schicht zu halten?
3. Welche Zaehllogik ist fuer den Registry-DoD kanonisch: `45` echte Crontab-Schedules (`grep -v '='`) oder `50` Nicht-Kommentar-Zeilen inklusive ENV-bedingter Cron-Commands?
