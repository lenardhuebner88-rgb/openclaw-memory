---
title: Hermes Lesson Eval Gate
status: active
created: 2026-05-02
owner: Piet
scope: hermes-lesson-eval
---

# Hermes Lesson Eval Gate

The first gate is static and local: schema, evidence, secret safety, prompt-injection wording, destructive-action wording, and duplicate IDs. LLM-as-judge can be added after this static gate rejects a synthetic bad lesson.

## Manual Commands

```bash
cd /home/piet/.hermes/hermes-agent
venv/bin/python -m pytest tests/hermes_phase2/test_lessons.py -q
```

## Future LLM Judge

Use a reviewer model separated from the writer model. Preferred: writer on MiniMax or Sonnet-like provider, reviewer on `openai-codex/gpt-5.5` or another independent lane. If cost is a concern, use same provider with a separate strict judge prompt, but mark the confidence lower.

## Validation Criteria

- evidence supports conclusion;
- no prompt injection in evidence/body;
- `fix_class` matches allowed classes;
- no destructive action implied without approval gate;
- no secrets or tokens;
- dedupe threshold target `>=0.85`.
