# Project State

## Active System Focus
- Obsidian Vault ist jetzt der produktive Informationsanker
- Ziel: stabile Retrieval-Pfade, wenig Kontextverschwendung, wenig manuelle Pflege
- Aktive Kernpfade: `03-Agents/Shared/*`, `03-Agents/OpenClaw/operational-state.md`, agent-spezifische `working-context.md`

## Current Priorities
- Mission Control stabil halten
- OpenClaw + Vault-Automation robust halten
- kleine produktive Slices statt Umbauten
- Kontext nur dort halten, wo er wiederverwendbar ist

## Important Projects
### Mission Control
- Produktion aktiv auf Port 3000
- Mobile Phase 2 offen
- Build kann in knapper Umgebung an OOM/SIGKILL scheitern

### Vault / Memory System
- Struktur konsolidiert am 2026-04-10
- Home Note, Auto-Rollup, Auto-Write und DONE-Dedupe aktiv
- Hermes ist decommissioned

### Home Server
- OpenClaw läuft bereits
- Immich bleibt strikt getrennt

### Telegram Bridge
- stabil als systemd user service

## Not Active / Removed from Core Context
- Hermes als aktiver Agentenpfad
- nested placeholder vault `Openclaw peter`

## Retrieval Rule
- erst Shared State
- dann OpenClaw Operational State
- dann Agent Working Context
- erst danach Details oder Archive
