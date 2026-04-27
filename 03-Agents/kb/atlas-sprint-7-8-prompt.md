---
title: Atlas Sprint 7+8 Prompt
status: ready
owner: Atlas
created: 2026-04-27
source_task: 5455079a-cca8-4afa-baa8-d5f96e3f3fa1
requires: /home/piet/vault/03-Agents/kb/atlas-result-format.md
---

# Official Sprint 7+8 Prompt

Use this prompt to start Stage 8 only after the Stage-7 reporting format gate is present and verified.

```text
REAL_TASK=true ORCHESTRATOR_MODE=true. This is not a heartbeat.

Atlas: start the Stage-8 autonomous orchestration sprint only after verifying the Stage-7 result-format gate.

Read and obey:
- /home/piet/vault/_agents/codex/plans/2026-04-26_atlas-stabilization-autonomy-8stage.md
- /home/piet/vault/03-Agents/kb/atlas-result-format.md
- /home/piet/.openclaw/workspace/feedback_system_rules.md, especially R1, R35, R44, R45, R47, R49, R57

Sprint theme:
Worker/Heartbeat/Cron target state: Which crons remain, which heartbeats are active, which gates are missing, how reports/follow-up tasks are unified, and who owns which role?

Execution rules:
- No uncontrolled fanout.
- Dispatch at most one bounded worker task at a time unless the operator explicitly approves parallelism.
- Every delegated worker task must have a Mission Control board task, explicit dispatch, accepted/progress/result receipts, and GET verification after every write.
- Do not mutate cron, gateway, service restart, model routing, R19/R50 logic, or other medium/high-risk controls without an approved gated-mutation task.
- If a follow-up is needed, create it as a draft with approvalClass and riskLevel instead of silently executing it.

Completion gate:
Return the terminal result in exactly this canonical Stage-7 order:
1. EXECUTION_STATUS
2. RESULT_SUMMARY
3. GATES
4. FOLLOW_UPS
5. OPERATOR_DECISIONS

The RESULT_SUMMARY must be task-specific and evidence-backed. Do not use generic placeholders.
``` 
