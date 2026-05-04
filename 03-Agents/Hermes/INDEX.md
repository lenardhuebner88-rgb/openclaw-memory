---
title: Hermes OpenClaw Index
created: 2026-05-03T18:14Z
agent: Hermes
status: active
scope: atlas-readable-hermes-index
---

# Hermes OpenClaw Index

This is the stable Atlas-readable entry point for Hermes outputs in Piet's canonical vault.

## Current Role

Hermes is Piet's bounded OpenClaw shadow-debug assistant:

- read-only evidence first;
- PERN reports: Problem, Evidence, Risk, Next Action;
- break-glass only with explicit Piet approval;
- no tokens, YOLO, permanent allowlists, or silent runtime mutations;
- lead orchestration remains OpenClaw/Atlas.

## Canonical Paths

```text
Vault SSoT:         /home/piet/vault
Hermes context:     /home/piet/vault/03-Agents/Hermes/
Plans:              /home/piet/vault/03-Agents/Hermes/plans/
Receipts:           /home/piet/vault/03-Agents/Hermes/receipts/
Lessons:            /home/piet/vault/03-Agents/Hermes/lessons/
Playbooks:          /home/piet/vault/03-Agents/Hermes/playbooks/
OpenClaw config:    /home/piet/.openclaw/openclaw.json
Mission Control:    /home/piet/.openclaw/workspace/mission-control
```

Do not treat these as SSoT:

```text
/home/piet/Vault
/home/piet/.openclaw/workspace/vault
```

## Read-only MCP Surfaces

Preferred evidence order:

1. `mc-readonly` — Mission Control health, board, tasks, alerts.
2. `openclaw-readonly` — Gateway health, services, sessions, model status, recent logs.
3. `qmd-vault` — focused vault/KB retrieval.
4. Shell/file reads only when no MCP/API path exists.
5. Mutations only after Piet approval.

## Core Hermes/OpenClaw Skills

Created/available for future use:

```text
openclaw-operator
openclaw-model-routing
minimax-openclaw-token-plan
openclaw-incident-rca
openclaw-config-change-safe
openclaw-discord-ops
openclaw-stability-hardening
```

Use cases:

| Situation | Skill |
|---|---|
| General OpenClaw/Mission Control/Discord incident | `openclaw-operator` |
| Model/provider/runtime/fallback issue | `openclaw-model-routing` |
| MiniMax M2.7/M2.7-highspeed Token Plan issue | `minimax-openclaw-token-plan` |
| RCA/postmortem/incident receipt | `openclaw-incident-rca` |
| Approved config edit | `openclaw-config-change-safe` |
| Discord slash/channel/streaming/send issue | `openclaw-discord-ops` |
| Long-term stability harness/watchdog | `openclaw-stability-hardening` |

## Latest Plans

- `plans/hermes-openclaw-collaboration-improvement-plan-2026-05-03.md` — Phase 2-4 implementation proposal for Hermes/OpenClaw collaboration.

## Latest Receipts / Research

- `receipts/minimax-m27-highspeed-research-summary-2026-05-03.md` — concise MiniMax M2.7-highspeed Token Plan research for Atlas.

## Playbooks / Guardrails

- `playbooks/break-glass-guardrails.md` — optional restart/config-edit guardrails for explicitly approved break-glass work.

## Atlas Handoff Format

Future Hermes plans/receipts should include this block:

```yaml
for_atlas:
  status: info_only | actionable | needs_piet_approval
  affected_agents: []
  affected_files: []
  recommended_next_action: ""
  risk: ""
  evidence_files: []
```

Interpretation:

- `info_only`: ingest context; no action required.
- `actionable`: Atlas/Forge may plan work, still respecting approval gates.
- `needs_piet_approval`: do not mutate until Piet approves in current channel/thread.

## Current Improvement Status

```yaml
phase_2_skills: implemented
phase_3_vault_index: implemented
phase_4_break_glass_guardrails: documented
runtime_config_changes: none
openclaw_restarts: none
```

## 2026-05-04
- `plans/hermes-atlas-review-lane-2026-05-04.md` — Atlas↔Hermes read-only review lane, pilot prompt, receipt contract, and legacy Discord service classification.
