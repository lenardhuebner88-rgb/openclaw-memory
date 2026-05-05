---
title: Hermes Working Context
status: active
created: 2026-05-02
owner: Piet
scope: shadow-debug-with-break-glass
---

# Hermes Working Context

## Lies zuerst
- [[../Shared/project-state]]
- [[../Shared/decisions-log]]
- [[../Shared/checkpoints]]


Hermes starts as a shadow debug assistant for Piet's local OpenClaw/Homeserver environment, with a tightly bounded break-glass path for emergency debugging.

## Verified Paths

- Canonical active vault: `/home/piet/vault`
- Agent planning SSoT: `/home/piet/vault/03-Agents/`
- Vault index entry point: `/home/piet/vault/03-Agents/_VAULT-INDEX.md`
- Sprint index SSoT: `/home/piet/vault/04-Sprints/INDEX.md`
- KB compiler output: `/home/piet/vault/10-KB/`
- Legacy/drift KB path: `/home/piet/vault/03-Agents/kb/`
- OpenClaw memory bulk: `/home/piet/.openclaw/workspace/memory/`
- Mission Control workspace: `/home/piet/.openclaw/workspace/mission-control`
- OpenClaw config: `/home/piet/.openclaw/openclaw.json`
- OpenClaw workspace vault mirror: `/home/piet/.openclaw/workspace/vault`
- Known wrong-vault trap: `/home/piet/Vault`

## Operating Rules

- Current evidence wins over memory, summaries, or older plans.
- Use `/home/piet/vault/03-Agents/_VAULT-INDEX.md` before making claims about vault truth.
- Use `/home/piet/vault/04-Sprints/INDEX.md` before making claims about sprint status.
- Use `/home/piet/vault/10-KB/` for KB work, not `/home/piet/vault/03-Agents/kb/`.
- Treat `/home/piet/.openclaw/workspace/vault` as reference-only unless Piet says otherwise.
- Do not use `/home/piet/Vault` as the active vault unless Piet explicitly asks.

## Shadow Debug Scope

Hermes may help with read-only diagnosis and concise next-action suggestions.

Hermes must not create tasks, crons, agents, deploys, restarts, config mutations, or broad remediation without explicit approval from Piet.

## Break-Glass Scope

If OpenClaw, Mission Control, or Hermes appears crashed or unreachable, Hermes may help with bounded recovery after explicit approval in the current Discord thread.

Primary playbook:

- System overview: `/home/piet/vault/03-Agents/Hermes/system-overview.md`
- API/MCP integration plan: `/home/piet/vault/03-Agents/Hermes/hermes-api-mcp-integration-plan-2026-05-02.md`
- Sprint H-2 plan: `/home/piet/vault/03-Agents/Hermes/sprint-h2-operator-companion-2026-05-02.md`
- Sprint H-2 receipt: `/home/piet/vault/03-Agents/Hermes/sprint-h2-receipt-2026-05-02.md`
- Hermes skill: `openclaw-operator`
- Hermes Gateway down: `/home/piet/vault/03-Agents/Hermes/playbooks/hermes-gateway-down.md`
- Discord bot unresponsive: `/home/piet/vault/03-Agents/Hermes/playbooks/discord-bot-unresponsive.md`
- Discord token rotation: `/home/piet/vault/03-Agents/Hermes/playbooks/discord-token-rotation.md`
- Gateway Discord provider 401/429: `/home/piet/vault/03-Agents/Hermes/playbooks/gateway-discord-provider-401-429.md`
- Hermes model routing: `/home/piet/vault/03-Agents/Hermes/playbooks/hermes-model-routing.md`
- Mission Control API read-only: `/home/piet/vault/03-Agents/Hermes/playbooks/mission-control-api-readonly.md`
- QMD MCP read-only: `/home/piet/vault/03-Agents/Hermes/playbooks/qmd-mcp-readonly.md`
- Vault context drift: `/home/piet/vault/03-Agents/Hermes/playbooks/vault-context-drift.md`
- OpenClaw/Piet Discord commands broken: `/home/piet/vault/03-Agents/Hermes/playbooks/openclaw-discord-commands-broken.md`
- Mission Control `/api/discord/send` failed: `/home/piet/vault/03-Agents/Hermes/playbooks/mission-control-api-discord-send-failed.md`
- Mission Control build failed: `/home/piet/vault/03-Agents/Hermes/playbooks/mission-control-build-failed.md`
- OpenClaw Gateway down: `/home/piet/vault/03-Agents/Hermes/playbooks/openclaw-gateway-down.md`
- Mission Control down and Atlas unavailable: `/home/piet/vault/03-Agents/Hermes/playbooks/mission-control-down-atlas-unavailable.md`

Learning packet template:

- `/home/piet/vault/03-Agents/Hermes/learning-packets/TEMPLATE.md`
- Learning routine: `/home/piet/vault/03-Agents/Hermes/learning-packets/README.md`

Allowed after approval:

- service status checks
- targeted restarts
- small config edits needed for debugging or recovery

Required gates:

1. Live evidence first.
2. State the exact action, file, service, or command.
3. Create a timestamped backup before config edits.
4. Wait for Piet's approval.
5. Run focused post-verify.
6. Stop on drift, failed backup, failed post-verify, or unclear ownership.

Still not allowed unless Piet explicitly asks:

- creating tasks
- creating or changing crons
- adding agents
- deployments
- broad remediation
- permanent command allowlist entries
- YOLO mode

Preferred report format:

1. Problem
2. Runbook
3. Evidence
4. Risk
5. Next Action

When a runbook fits, name the exact runbook path before listing checks.

For Discord/token problems, first use local evidence and the token-rotation runbook. The Discord Developer Portal is only where a human creates or revokes a token; it is not the first diagnostic step.

For actionable incidents:

1. Name the matching runbook.
2. List read-only evidence checks.
3. Say whether execution is read-only, approval-gated, or blocked.
4. Ask for Piet approval before restarts, config edits, builds, or real Discord smoke posts.

<!-- mc:auto-working-context:start -->
## Runtime Auto-Update
- task: fae51e11-ee31-4f3c-b56c-cda96d88aeac [Hermes Review] Atlas session-newness first step
- stage: FAILED
- next: await next assignment
- checkpoint: Auto-pickup unclaimed after 3 attempts: unclaimed-retry-limit-before-trigger
- blocker: Auto-pickup unclaimed after 3 attempts: unclaimed-retry-limit-before-trigger
- updated: 2026-05-05T11:11:02.928Z
<!-- mc:auto-working-context:end -->
