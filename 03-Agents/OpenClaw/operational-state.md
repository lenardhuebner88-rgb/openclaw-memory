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

## Update 2026-04-12
- Alle working-context.md Merge-Konflikte aufgelöst
- Strikte Delegationsregeln in alle Agent-Contexts eingebaut
- Neue Agent-Contexts: Pixel, Forge-Opus, Flash
- Modell-Zuweisung neu geregelt (noch nicht live in openclaw.json — offener Task für Forge)
- Atlas-Session-Handover aktualisiert — Atlas braucht kein separates Handover-Prompt

- Automated worker pickup trigger received; checking /api/worker-pickups and dispatching ready tasks.
- 2026-04-13T14:51:45Z Dispatch-Check gestartet: assigned Tasks prüfen und gemäß worker-monitor Trigger dispatchen.\n
## Memory Architecture Cleanup (2026-04-15)
- 5 parallel daily-note locations consolidated to 3 with clear ownership
- `workspace/memory/daily/` = OpenClaw native, auto-injected (today+yesterday)
- `vault/01-Daily/` = Human manual notes only, never auto-injected
- `vault/03-Agents/OpenClaw/daily/` = Agent auto-writes, read on-demand
- Removed: `vault/memory/daily/`, vault root loose dailies, `01-Daily/` stubs
- `workspace/memory/` root is now clean — no loose dated files
- MEMORY.md trimmed from 37.5K to 2.7K (was being truncated by bootstrapMaxChars!)
- Dreaming promotion to MEMORY.md disabled via `promotion_target=none` directive
- Dead-agent SQLite DBs archived, dead workspaces archived
- Per-agent AGENTS.md/IDENTITY.md/BOOTSTRAP.md deduplicated via symlinks to workspace-shared/

## Session-Guard (2026-04-20)
- Script: /home/piet/.openclaw/scripts/session-size-guard.py
- Cron: */5 * * * * (full scan) + * * * * * (immediate log scan)
- v1: 9327310f | v2: 3c66a946 | v3: 779f8995 | v4: 15217cdc
- Guard-v4 Status: OPERATIONAL — echte Runtime-Session-Umschaltung + Integrationstest ok
- Thresholds: Warning≥600KB/150msg, HardAlert≥900KB/200msg, RotationTrigger≥1.1MB/250msg
- Immediate-Trigger: alert-only (keine blinde Auto-Rotation)
