---
title: Hermes Sprint H-4/H-5 Receipt
status: passed
created: 2026-05-02
owner: Piet
scope: hermes-operator-optimization
---

# Hermes Sprint H-4/H-5 Receipt

## Result

H-4/H-5 completed the first reliability and operating-surface pass for Hermes.

## Implemented

- `privacy.redact_pii=true` in `/home/piet/.hermes/config.yaml`.
- Stage-1 systemd hardening for `hermes-gateway.service`: `NoNewPrivileges`, `PrivateTmp`, `MemoryHigh=1536M`, `MemoryMax=2G`.
- Discord slash-command sync policy set to `off` at service level.
- Code-level slash sync throttle added for future `safe` policy: command hash plus minimum interval.
- Discord tool surface tightened; risky nonessential toolsets disabled.
- Hermes prompt shortened and aligned to MCP-first operator behavior.
- Stale vault docs received Hermes override boxes where older rejected/adoption language could confuse current state.

## Deferred

- `ProtectSystem`, `ProtectHome`, and `ReadWritePaths` are intentionally deferred. They are valuable isolation controls, but can break Hermes tools if introduced before the writable-path map is proven.

## Validation

- `py_compile` for Hermes Discord gateway file: PASS.
- Hermes Discord gateway tests: PASS, 17 tests.
- `hermes mcp test openclaw-readonly`: PASS.
- `hermes mcp test mc-readonly`: PASS.
- `hermes mcp test qmd-vault`: PASS.
- `hermes-gateway.service`: active after restart.
- OpenClaw Gateway health: HTTP 200, live.
- Mission Control health: OK after follow-up check.
- Recent Hermes logs: no active Discord 429 loop observed in the final check window.

## Operating Recommendation

Keep Hermes in Phase 1 for live operations: read-only MCP first, runbook first, approval before restarts/config edits. Move next into Phase 2 documentation and lessons so Hermes becomes easier to use as a peer without loosening security prematurely.
