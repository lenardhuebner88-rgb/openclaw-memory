# OpenClaw Operational State

## Canonical Paths
- Runtime workspace: `/home/piet/.openclaw/workspace`
- Productive Obsidian vault: `/home/piet/vault`
- OpenClaw config: `/home/piet/.openclaw/openclaw.json`
- Mission Control tasks: `/home/piet/.openclaw/workspace/mission-control/data/tasks.json`
- Worker runs: `/home/piet/.openclaw/workspace/mission-control/data/worker-runs.json`

## Retrieval Entry Points (Agent-Minimum)
1. `03-Agents/Shared/user-profile.md`
2. `03-Agents/Shared/project-state.md`
3. `03-Agents/Shared/decisions-log.md`
4. `03-Agents/OpenClaw/operational-state.md`
5. `01-Daily/YYYY-MM-DD.md`

## Session Updates from 2026-04-10
- Layer3 rollup cron exists (`.cron/layer3-rollup`) and runs daily around 21:10.
- Git receive mode on homeserver vault adjusted with `receive.denyCurrentBranch=updateInstead` for push-into-checked-out-repo flow.
- Hermes no longer active in vault structure.
- Nested `Openclaw peter` path is not an active vault path anymore.
