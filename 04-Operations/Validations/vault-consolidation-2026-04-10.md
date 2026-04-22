# Vault Consolidation 2026-04-10

## Objective
Pragmatic consolidation slice after Obsidian restructuring with focus on retrieval stability, low context overhead, and removal of inactive Hermes structures.

## What was consolidated
- Canonical retrieval entrypoints fixed to a compact set under:
  - `03-Agents/Shared/`
  - `03-Agents/OpenClaw/operational-state.md`
  - `01-Daily/`
- Home index updated to point to active paths only.
- Shared state and decision files updated with latest operational facts.

## What was deactivated/archived
- `03-Agents/Hermes/` moved to:
  - `06-Archive/2026-04/decommissioned/Hermes`
- Nested placeholder vault `Openclaw peter/` moved to:
  - `06-Archive/2026-04/decommissioned/Openclaw-peter-nested-vault`

## New stable operational artifact
- Added `03-Agents/OpenClaw/operational-state.md` as compact operational source for path truth and current constraints.

## Retrieval impact
- Fewer competing paths for layer-3 context.
- No active Hermes branch in core retrieval tree.
- Explicit canonical root (`/home/piet/vault`) and entrypoint sequence for agents.
- Reduced risk of loading stale nested vault content.
