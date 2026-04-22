# OpenClaw Home

> Vault Entry Point — zuerst hier lesen. Anpinnen empfohlen.

## Quick Start

1. Lies `[[_agents/_shared/project-state]]`, `[[_agents/_shared/decisions-log]]`, `[[_agents/_shared/checkpoints]]`
2. Öffne den relevanten Agent-Context unten
3. Neue Einträge → [[00-Inbox]]

## Aktive Agenten

| Agent | Worker-ID | Modell | Status | Context |
|-------|-----------|--------|--------|---------|
| Atlas | main | GPT-5.4 | aktiv | [[_agents/Atlas/working-context]] |
| Forge | sre-expert | Codex GPT-5.3 | aktiv | [[_agents/Forge/working-context]] |
| Lens | efficiency-auditor | GPT-5.4 | aktiv | [[_agents/Lens/working-context]] |
| James | researcher | MiniMax M2.7-HS | aktiv | [[_agents/James/working-context]] |
| Pixel | frontend-guru | MiniMax M2.7-HS | aktiv | [[_agents/Pixel/working-context]] |
| Spark | spark | MiniMax M2.7-HS | aktiv | [[_agents/Spark/working-context]] |

**Eskalation only:** Forge-Opus (Claude Opus 4.6)
**Inaktiv:** Flash

## Navigation

| Ordner | Zweck |
|--------|-------|
| [[00-Inbox]] | Triage von neuen Einträgen |
| [[01-Daily]] | Tagebuch (manuell) |
| [[02-Docs]] | Stabile Referenz-Dokumente |
| [[03-Projects]] | Laufende Projekte (Mission-Control, Memory-System) |
| [[04-Sprints]] | Sprint-Pläne und -Reports |
| [[05-Incidents]] | Post-Mortems, RCAs |
| [[06-Operations]] | Ops, Validations, Monitoring |
| [[07-Research]] | Recherchen, Benchmarks |
| [[10-KB]] | Kompilierte Wissensbasis (read-only output von L1) |
| [[_agents]] | Agent-scratch + coordination |
| [[99-Templates]] | Vorlagen — siehe [[99-Templates/AGENTS]] |

## Häufig gebraucht

- [[_agents/_VAULT-INDEX]] — Plan-Status-Index (Single-Source-of-Truth)
- [[_agents/_coordination]] — Live-Session-Board
- [[_agents/OpenClaw/daily]] — End-of-day-Reports
- [[_agents/_shared]] — Team-weite Rules + Decisions
- `feedback_system_rules.md` (Root) — R1-R50 Rule-History

## Leitplanken

- erst `_shared`, dann `OpenClaw`, dann Agent
- Dauerhaftes nach `_shared`, `02-Docs` oder `03-Projects` — niemals lose ablegen
- Atlas delegiert immer — handelt nie selbst technisch
- Neue Dinge → [[00-Inbox]] (Triage durch Librarian)
- Home.md anpinnen — Vault immer hier starten
