---
title: Atlas Result Format
status: active
owner: Atlas
created: 2026-04-27
source_task: 5455079a-cca8-4afa-baa8-d5f96e3f3fa1
---

# Atlas Result Format

This is the canonical Stage-7 completion format for Atlas autonomous work and the gate before Stage 8.

Every terminal Atlas sprint result must contain exactly these five top-level sections, in this order:

## EXECUTION_STATUS

State the final execution state in one line: `done`, `partial`, `blocked`, or `failed`.
Include the task ID and whether the terminal Mission Control receipt was written and verified.

## RESULT_SUMMARY

Human-meaningful summary of what changed and why it matters.
Do not use placeholders such as “Task accepted and completed.”
For orchestrated work, identify which worker outputs were consolidated and what decision Atlas made.

## GATES

List verification gates and their observed result.
Examples: file existence checks, render scripts, tests, build/lint, API GET verify after writes, worker/pickup/health proof.
If a gate could not run, mark it explicitly as `not_run` with the reason.

## FOLLOW_UPS

List follow-up tasks or drafts created by Atlas.
Each follow-up must include `approvalClass` and `riskLevel` when it is intended for Mission Control.
If no follow-up is needed, write `none`.

## OPERATOR_DECISIONS

List decisions needed from the operator before further mutation, dispatch, model routing, service restart, or fanout.
If no decision is needed, write `none`.

## Compatibility note

Some task prompts may request additional delivery headings such as `FILES_CHANGED`, `VALIDATION`, or `NEXT_STEP`.
Those may be added in the final user-facing response, but the canonical Stage-7 sprint-result gate is the five-section format above.
