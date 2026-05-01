---
title: 2026-05-01 S1 Follow-up Pipeline
date: 2026-05-01
status: planned
operatorLock: true
approval: awaiting-operator-go
run_log: /home/piet/.openclaw/workspace/memory/working/2026-05-01-sprint-operator.md
---

# Sprint 1 — Follow-up Pipeline

## Goal

Close the loop after task results. When a task becomes done, failed, or blocked, the system should report it, classify the next action, and create operator-gated follow-up drafts when rules say so.

## Scope

- Create `result-watcher.sh` as a successor/extension to the current sprint debrief watcher.
- Add declarative decision rules in `/home/piet/.openclaw/config/result-decision-rules.yaml`.
- Add follow-up templates in `/home/piet/.openclaw/config/followup-templates/`.
- Add a simple operator approval queue based on channel replies.
- Run one controlled test cycle and clean it up.

## Tasks

1. `S1-T1.1` Result-Watcher service and systemd user timer.
2. `S1-T1.2` Decision-engine rules file.
3. `S1-T1.3` Follow-up templates.
4. `S1-T1.4` Operator approval queue parser and state handling.
5. `S1-T1.5` Test run, evidence, cleanup, and closure doc.

## Safety Rules

- Backup before any script, config, or service mutation.
- No mass-close, no blind re-dispatch, no webhook or token edits.
- No Mission Control build or restart unless explicitly required by a task and preflight is green.
- Health probe after each fix; stop on degraded health or dispatchStateConsistency below 1.
- One active task per agent at a time.

## Acceptance

- `result-watcher.timer` enabled and active.
- `result-decision-rules.yaml` live with done, failed, blocked, and default rules.
- Two templates exist and render without unreplaced placeholders.
- One test cycle proves task result to Discord post to follow-up draft.
- Closure document written to `/home/piet/vault/04-Sprints/closed/2026-05-01_s1-followup-pipeline.md`.

## Operator Gate

Do not start implementation until the operator says `S1 starten`.

