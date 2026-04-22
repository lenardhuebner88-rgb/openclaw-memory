# Mistakes & Corrections

- Repeated model override usage in cron tasks caused `LiveSessionModelSwitchError`.
  - Correction: remove per-task overrides; use agent default mapping.

- Timeouts were often too short for real workload.
  - Correction: increase conservative timeout budgets and escalate persistent offenders to manual review.

- Dispatch target normalization used display names instead of runtime IDs.
  - Correction: resolve via runtime agent ID mapping (`resolveRuntimeAgentId`).

- Board hygiene drifted (many stale draft/in-progress tasks).
  - Correction: introduce cleanup automation and explicit fail-state handling for orphaned tasks.

- High token spend for blocked outcomes due to poor pre-checks.
  - Correction: add backlog/source checks before expensive LLM analysis.
