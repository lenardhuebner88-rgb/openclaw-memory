---
title: Hermes Sprint H-7 Phase 2 Lesson Loop
status: active
created: 2026-05-02
owner: Piet
scope: hermes-phase2-lessons
sources:
  - Langfuse official docs
  - DeepEval official docs
---

# Sprint H-7: Phase 2 Lesson Loop & Vault Integration

## Goal

Hermes should produce structured lessons after investigations, but only through a quality gate that prevents false lessons from making Hermes, Atlas, or Forge worse.

## Best-Practice Decisions

- Keep lesson creation append-only and schema-bound.
- Keep generated lessons at `status: pending_validation` until a separate reviewer/eval path accepts them.
- Use a second judge model or at least a separate judge prompt for validation.
- Do not activate cron until manual extraction and rejection tests pass.
- Store lessons in the canonical path `/home/piet/vault/03-Agents/Hermes/lessons/`.
- Let the KB compiler consume validated lesson files through Vault, not through Hermes runtime state.
- Add Langfuse as an optional tracing layer after the lesson loop is useful; tracing should not be a dependency for diagnosis.
- Preserve Hermes' native learning loop: validated lessons should feed Hermes `skill_manage`, built-in memory, and session-search workflows instead of replacing them.

## Native Hermes Learning Contract

Hermes already has a built-in learning system:

- `session_search`: raw cross-session recall from Hermes conversations.
- Built-in memory: compact persistent facts and user/environment preferences.
- `skill_manage`: procedural memory; creates or patches reusable skills.
- Curator: weekly background maintenance for agent-created skills.

Vault Lessons therefore serve as the **auditable evidence gate**, not as a second opaque memory. After validation, each lesson gets one promotion target:

| Lesson Type | Promotion Target | Rule |
|---|---|---|
| Stable environment fact | Hermes memory | Store only compact fact, no incident narrative. |
| Reusable diagnostic procedure | `openclaw-operator` skill patch | Add to incident matrix, pitfalls, or verification prompts. |
| One-off incident history | Vault lesson only | Keep searchable, do not pollute skills. |
| Runbook correction | Hermes playbook patch | Update exact runbook after backup and validation. |
| Operator preference | Hermes memory + maybe skill wording | Only if Piet explicitly stated the preference. |

## Architecture

```text
Hermes sessions/audit
  -> lesson_extractor (manual first)
  -> 03-Agents/Hermes/lessons/*.md (pending_validation)
  -> lesson_eval gate
  -> validated/rejected
  -> lesson_promotion (proposal only)
  -> skill_manage / memory / runbook patch / KB compiler path
```

## Gates

### Gate A: Schema

- Lesson files must have YAML frontmatter.
- Required keys: `lesson_id`, `date`, `trigger`, `hypothesis_initial`, `hypothesis_final`, `evidence`, `fix_proposed`, `fix_class`, `runbook_match`, `ttl_days`, `status`.
- `status` starts as `pending_validation`.

### Gate B: Evidence

- Every conclusion needs at least one evidence item.
- Evidence must be local and secret-safe.
- Evidence cannot instruct the agent to execute a command.

### Gate C: Reward-Hacking Defense

- Writer and reviewer must be separated.
- Bad synthetic lesson must be rejected before auto-validation is allowed.
- Similarity/dedupe threshold target: `>=0.85` means skip or merge.

### Gate D: Cron Activation

Cron stays disabled until:

- at least 3 manual pending lessons are generated;
- at least 1 intentionally bad lesson is rejected;
- recall on a known prior incident finds the matching lesson in under 5 seconds.

## Implementation Slices

1. H-7.1: Vault structure, schema, template, index, sample lesson.
2. H-7.2: Manual extractor from Hermes session JSONL to candidate lesson draft.
3. H-7.3: Static eval gate for schema/evidence/security/dedupe.
4. H-7.4: Native Hermes promotion proposal: classify validated lessons into memory, skill, runbook, or vault-only targets.
5. H-7.5: Optional LLM judge integration with second model.
6. H-7.6: Cron/timer proposal, disabled by default.
7. H-7.7: Optional Langfuse tracing plan and deployment gate.

## Stop Conditions

- No live audit/source stream exists and session JSONL is insufficient for extraction.
- Eval cannot reject the synthetic bad lesson.
- A generated lesson proposes destructive action without approval gate.
- Any token or secret appears in a lesson.

## Exit Criteria

- `lessons/INDEX.md` exists and lists pending/validated/rejected lessons.
- Manual extractor can create a draft lesson without writing secrets.
- Eval tests pass locally.
- Promotion harness can propose native Hermes targets without mutating memory or skills.
- KB stub explains how lessons become usable by Hermes and OpenClaw.
- Cron and Langfuse remain documented but not active until gates pass.
