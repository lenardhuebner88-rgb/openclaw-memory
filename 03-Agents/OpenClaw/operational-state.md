# OpenClaw Operational State

## Canonical Paths
- Workspace: `/home/piet/.openclaw/workspace`
- Vault: `/home/piet/vault`
- Config: `/home/piet/.openclaw/openclaw.json`
- Mission Control tasks: `/home/piet/.openclaw/workspace/mission-control/data/tasks.json`
- Worker runs: `/home/piet/.openclaw/workspace/mission-control/data/worker-runs.json`

## Read Order
1. `03-Agents/Shared/project-state.md`
2. `03-Agents/Shared/decisions-log.md`
3. `03-Agents/OpenClaw/operational-state.md`
4. passender `03-Agents/<Agent>/working-context.md`
5. `03-Agents/OpenClaw/daily/YYYY-MM-DD.md` für operative Auto-Writes
6. `01-Daily/YYYY-MM-DD.md` nur bei Bedarf für manuellen Tageskontext

## Current Truth
- Produktiver Vault ist `/home/piet/vault`
- Hermes ist kein aktiver Pfad mehr
- `Openclaw peter` ist kein produktiver Vault-Pfad mehr
- Layer3-Rollup läuft täglich über `.cron/layer3-rollup`
- Operative Daily-Auto-Writes gehen nach `03-Agents/OpenClaw/daily`
- `01-Daily` ist nur noch für manuelle menschliche Tagesnotizen gedacht
- Windows-Push in den Homeserver-Vault ist erlaubt über `receive.denyCurrentBranch=updateInstead`

## Automation Active
- Obsidian Git: Pull/Backup/Push aktiv
- Home Note als geführter Einstieg aktiv
- Vault Auto-Write für `task start`, `checkpoint`, `task done` aktiv
- DONE-Dedupe gegen Doppel-Callbacks aktiv
