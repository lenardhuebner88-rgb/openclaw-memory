---
title: Embedded Run Lane Timeout Budget Lesson
created: 2026-05-03T21:52:30Z
agent: Hermes
status: pending_validation
scope: openclaw-lesson
for_atlas:
  status: info_only
  affected_agents: [main, sre-expert]
  affected_files:
    - /home/piet/vault/03-Agents/Hermes/receipts/2026-05-03_embedded-run-timeout-rca.md
  recommended_next_action: "Use this lesson when future logs show 300s Codex app-server timeouts followed by lane/stuck symptoms."
  risk: "Do not misclassify recoverable fallback as unresolved incident; inspect trajectory completion."
  evidence_files:
    - /home/piet/vault/03-Agents/Hermes/receipts/2026-05-03_embedded-run-timeout-rca.md
---

# Embedded Run Lane Timeout Budget Lesson

## Lesson

For OpenClaw embedded Codex runs, a 300s `codex app-server attempt timed out` is not automatically the same incident as a wedged command lane.

The key distinction is what happens **after** the 300s inner attempt timeout:

- Bad / old failure mode: timeout-compaction or fallback starts, then `Command lane "main" task timed out after 330000ms` kills the recovery path.
- Fixed / acceptable recovery mode: primary model times out at ~300s, fallback starts and later logs `candidate_succeeded`; session health ends with `suspectedStuck=0`, `withErrors=0`.

## Diagnostic Rule

When checking if the root cause is fixed, do not stop at model-runtime failure counts. Follow the run through journal + trajectory:

1. Find the `runId` and session id.
2. Confirm whether a `model.completed` / `session.ended status=success` happened after the timeout.
3. Check if the exact old outer-lane signature recurred:
   - `CommandLaneTaskTimeout`
   - `Command lane "main" task timed out after 330000ms`
4. Check post-success window for fresh stuck/recovery-skip lines.
5. Interpret `active_embedded_run` at ~120s as protective unless it persists beyond the delayed abort/drain threshold.

## Current huebners Validation

Patch checker confirms:

```text
outer_ms=900000
outer_minutes=15.0
active_abort_minutes=15.0
```

Post-fix real Atlas turn confirmed:

```text
23:50:52 gpt-5.5 timed out
23:50:54 fallback gpt-5.4-mini started
23:51:52 fallback gpt-5.4-mini succeeded
```

Therefore the 330s lane-budget root cause is fixed in the installed runtime, while primary model timeout risk remains.
