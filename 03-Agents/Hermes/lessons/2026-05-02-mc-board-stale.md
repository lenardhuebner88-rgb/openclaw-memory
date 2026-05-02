---
lesson_id: hermes-2026-05-02-001
date: 2026-05-02
trigger: /hermes_diagnose mc-board reagiert nicht
hypothesis_initial: "Gateway-OOM"
hypothesis_final: "stale stdio-MCP-client pattern; compare incident_taskboard_mcp_not_connected_2026-04-21 before restart assumptions"
evidence:
  - path: /home/piet/vault/03-Agents/Hermes/sprint-h2-receipt-2026-05-02.md
    lines: "QMD/Vault timeout and runbook-first mitigation"
  - path: /home/piet/vault/03-Agents/Hermes/sprint-h3-receipt-2026-05-02.md
    lines: "QMD transient MCP retry observation"
fix_proposed: "Check MCP heartbeat/client freshness before health/restart escalation; restart only if live evidence and Piet approval gate pass."
fix_class: gated-mutation
runbook_match: rb-stale-mcp-client
ttl_days: 90
status: pending_validation
---

# MCP Timeout Before Restart

## Diagnose-Loop

1. Healthcheck: Mission Control and Gateway can be up while one MCP client path is stale or timing out.
2. Vault-Recall: Similar symptoms should first search prior MCP timeout incidents and Hermes H-2/H-3 receipts.
3. Hypothesis: stale stdio or bridge client can mimic a broader service outage.
4. Verify: check MCP tool health, heartbeat freshness, and recent client retry logs before proposing restart.

## Lesson

When MCP tools timeout but core HTTP health stays green, treat client freshness as the first suspect. Check heartbeat/state files and recent MCP retry logs before escalating to a service restart. A restart remains a gated mutation, not a default first fix.

## Suggested Action

Backlog suggestion only: add an alert when the MCP taskboard/reaper path is late by more than 3 minutes, if that latency signal exists reliably.
