---
title: Hermes Sprint H-7 Receipt
status: partial-pass
created: 2026-05-02
owner: Piet
scope: hermes-phase2-lessons
---

# Hermes Sprint H-7 Receipt

## Result

Phase 2 Lesson-Loop is implemented as a controlled alpha, not yet as an active cron. This gives Hermes a structured path to write lessons without letting false lessons enter the KB unchecked.

## Backup

- `/home/piet/backups/hermes-phase2-lessons-20260502-234207`

## Implemented

- Plan: `/home/piet/vault/03-Agents/Hermes/plans/sprint-h7-phase2-lesson-loop-2026-05-02.md`
- Lessons index: `/home/piet/vault/03-Agents/Hermes/lessons/INDEX.md`
- Lesson template: `/home/piet/vault/03-Agents/Hermes/lessons/TEMPLATE.md`
- First pending sample lesson: `/home/piet/vault/03-Agents/Hermes/lessons/2026-05-02-mc-board-stale.md`
- Eval docs: `/home/piet/vault/03-Agents/Hermes/eval/README.md`
- Static lesson schema/eval module: `/home/piet/.hermes/hermes-agent/hermes_phase2/lesson_schema.py`
- Manual session extractor: `/home/piet/.hermes/hermes-agent/hermes_phase2/lesson_extractor.py`
- Native learning promotion classifier: `/home/piet/.hermes/hermes-agent/hermes_phase2/lesson_promotion.py`
- Tests: `/home/piet/.hermes/hermes-agent/tests/hermes_phase2/test_lessons.py`
- Promotion tests: `/home/piet/.hermes/hermes-agent/tests/hermes_phase2/test_lesson_promotion.py`
- Langfuse gate doc: `/home/piet/vault/03-Agents/Hermes/plans/langfuse-tracing-gate-2026-05-02.md`
- Vault index and Sprint index updated with Phase-2 pointers.
- `openclaw-operator` skill updated with Lesson Promotion rules so validated lessons can become native Hermes skill/memory improvements.

## Validation

- `venv/bin/python -m pytest tests/hermes_phase2/test_lessons.py tests/hermes_phase2/test_lesson_promotion.py -q`: PASS, 4 tests.
- Bad synthetic lesson rejection test: PASS.
- Manual extractor dry-run: PASS, found 2 candidate Hermes session files.
- Promotion classifier dry-run: PASS, current pending sample stays `vault-only` and is not promoted.
- Frontmatter check for new lesson/eval/plan files: PASS.

## Intentional Non-Activation

- No cron/timer was installed.
- No Langfuse container was started.
- No auto-validation was enabled.

Reason: the quality gate must prove recall and false-lesson rejection before any automatic writing loop is allowed to affect the KB.

## Native Hermes Learning Preservation

The adapted design preserves Hermes' built-in learning loop:

- session history remains in Hermes session-search;
- stable facts can be promoted to built-in memory only after validation;
- reusable procedures should patch `openclaw-operator` via `skill_manage`;
- one-off incident history stays in Vault lessons;
- curator remains enabled and can maintain agent-created skills.

The promotion classifier currently proposes targets only; it does not mutate memory, skills, runbooks, or KB output.

## Next Gates

1. Run the extractor manually on one known investigation and inspect the candidate.
2. Add a real rejected lesson fixture and confirm rejection still passes.
3. Add optional LLM judge with reviewer model separated from writer model.
4. Only then propose a systemd timer or Hermes cron for periodic extraction.
