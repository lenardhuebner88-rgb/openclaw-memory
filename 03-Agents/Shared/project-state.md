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

## System Rule — Delegation (2026-04-12)
**Atlas delegiert immer — handelt nie selbst technisch.**
| Aufgabe | Agent |
|---------|-------|
| Code, Infra, Build, Deploy | Forge |
| Root-Cause, Architektur-Risiko | Forge-Opus |
| Recherche, externe Vergleiche | James |
| UI, Frontend, Dashboard | Pixel |
| Kosten, Audit, Konsolidierung | Lens |
| Leichte Forge-Entlastung | Flash (sobald aktiv) |

## Aktive Agenten + Modell-Zuweisung (Stand 2026-04-12)
| Agent | ID | Modell | Pool | Status |
|-------|-----|--------|------|--------|
| Atlas | main | gpt-5.4 | OpenAI Pro (€200 flat) | ✅ aktiv |
| Forge | sre-expert | GPT-5.3 Codex | OpenAI Pro (fix) | ✅ aktiv |
| Lens | efficiency-auditor | gpt-5.4 | OpenAI Pro | ✅ stabilisiert |
| James | researcher | minimax/MiniMax-M2.7-highspeed | MiniMax (€40 token) | ✅ aktiv |
| Pixel | frontend-guru | minimax/MiniMax-M2.7-highspeed | MiniMax | ✅ aktiv |
| Forge-Opus | forge-opus | anthropic/claude-opus-4-6 | Anthropic API Key | ⚠️ Eskalation only |
| Flash | flash | minimax/MiniMax-M2.7-highspeed | MiniMax | ❌ noch nicht aktiv |

Modell-Zuweisungen noch nicht live in openclaw.json — Forge-Task ausstehend.

## Board-Stand 2026-04-12 Abend (letzter Heartbeat)
- done=161 (+37 seit Backup-Restore)
- assigned=6 | draft=1 | failed=0 ✅ | canceled=1
- Erstes Mal sauber (failed=0) seit Backup-Restore

## Phase-4-Sprint Status (2026-04-12 Abend)
- Build ✅ | Vitest 135 Tests ✅ | E2E 9/9 ✅
- Letzter James Gate-Check läuft auf Commit afa88eb
- Commits: 51c0b6e → 86830ab → 27fe521 → e2e7715 → afa88eb
