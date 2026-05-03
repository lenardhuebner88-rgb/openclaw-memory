---
title: OpenClaw Stability Follow-ups - 2026-05-03
status: active
created: 2026-05-03
owner: Piet
agent: Hermes
---

# OpenClaw Stability Follow-ups

This note captures the follow-ups surfaced by the 2026-05-03 stability-harness run and the Hermes receipt-writing warning.

## Context

- Commander bot deactivation is now intentional.
- MiniMax M2.7 routing has been enabled in the OpenClaw config.
- The stability harness must reflect that new target state.
- Hermes still reported a receipt-writing failure to Vault with an inline fallback.

## Follow-ups

1. Keep the stability harness aligned with the new service state.
   - `openclaw-discord-bot.service` may be `inactive/dead` or `inactive/exited`.
   - Gateway must remain `active/running`.
   - Memory timer must remain `active/waiting`.

2. Fix the Hermes receipt-writing path.
   - The receipt should land in Vault, not only inline.
   - The `Errno 2` / `%s` failure should be traced to the exact writer path and removed.

3. Keep MiniMax routing intentional.
   - `efficiency-auditor` should prefer `minimax/MiniMax-M2.7-highspeed`.
   - `james` should prefer `minimax/MiniMax-M2.7`.
   - OpenAI remains the fallback path for the main operational agents.

## Current Status

- Implemented:
  - Stability harness service gate updated for the disabled Commander state.
  - MiniMax M2.7 routing added to the active config.
- Still open:
  - Hermes receipt-writing fix to Vault.
  - Any agent-auth drift in isolated runtime envs if the smoke harness is run outside the main auth context.

## Next Check

- Re-run the stability harness after the next auth-sane smoke window.
- Confirm the harness no longer fails on the intentionally disabled Commander.
- Confirm the Hermes receipt is materialized into Vault and not only shown inline.
