---
title: Vault Guide — Conventions & How-To
type: doc
status: active
tags: [type/doc, topic/governance]
---

# Vault Guide

> How to work in this vault. Konventionen die nicht in AGENTS.md pro Ordner stehen.

## Navigation

- **Start:** [[Home]] (anpinnen!)
- **Triage:** [[00-Inbox]]
- **Tag-Konvention:** [[_agents/_shared/tag-convention]]
- **Templates:** [[99-Templates]]
- **Plan-Status:** [[_agents/_VAULT-INDEX]]

## Struktur-Prinzip

```
00-Inbox/         Triage (neu)
01-Daily/         Tagebuch (manuell)
02-Docs/          Stabile Doku, Vault-Guide, Schemas, Design-Packs
03-Projects/      Aktive Projekte mit Roadmap
04-Sprints/       Sprint-Pläne + Reports
05-Incidents/     RCAs, Post-Mortems
06-Operations/    Ops, Monitoring, Validations
07-Research/      Externe Recherchen, Benchmarks
08-Backups/       Snapshots (read-only)
09-Archive/       Abgelegtes (read-only)
10-KB/            L1-compilierte Wissensbasis (auto-generiert)
99-Templates/     Vorlagen
_agents/          Agent-Scratch + Coordination
```

## Datei-Typen

| Endung | Zweck |
|--------|-------|
| `.md` | Standard-Markdown-Note |
| `.base` | Obsidian Bases (Tabellen/Cards mit Frontmatter-Filtern) |
| `.canvas` | Canvas-Diagramme |
| `{Folder}/{Folder}.md` | Folder-Note (MOC pro Ordner) |
| `AGENTS.md` | Policy + Writer-Rules pro Ordner |

## Frontmatter-Standard

```yaml
---
title: Mein Document
type: sprint | incident | handover | kb | rule | project | daily | doc | research
status: planning | active | in-progress | done | deprecated | archived
tags: [type/X, status/Y, agent/Z, topic/W]
---
```

Siehe [[tag-convention]] für Namespace-Details.

## Link-Konvention

- **Wikilinks** (`[[...]]`) innerhalb des Vaults
- **Relative Markdown-Links** nur bei externen Files außerhalb Obsidian
- Bei Kollisionen: `[[Pfad/Name]]` statt nur `[[Name]]`
- Alias wenn sinnvoll: `[[Langer/Pfad/Name|Kurzname]]`
- Folder-Links: nutzen `[[FolderName]]` — auflösbar dank `{Folder}/{Folder}.md`

## Daily-Workflow

1. Morgens: [[Home]] → [[00-Inbox]] durchgehen
2. Offenes in Agenten-Context, Triage nach Struktur
3. Neue Einträge in [[01-Daily]] (tagesbezogen) oder [[00-Inbox]] (noch unklar)
4. Abends: `_agents/OpenClaw/daily/` bekommt den auto-Report (nicht hier)

## Automation

| Cron | Zweck |
|------|-------|
| `30 min` | auto-sync Vault → GitHub |
| `nightly 04:00` | L1 KB-Compiler → `10-KB/` |
| `nightly 04:15` | L2 Graph-Edges → memory-graph.jsonl |
| `nightly 04:30` | L6 Memory-Dashboard → `_agents/memory-dashboard.md` |
| `hourly` | L3 Retrieval-Feedback |
| `*/5 min` | L5 Memory-Budget-Meter |

## Obsidian-Plugins

- **Linter** (aktiv): Frontmatter-Hygiene, Whitespace. Config: `.obsidian/plugins/obsidian-linter/data.json`
- **Bases** (core): Tabellen/Cards. Beispiele: `04-Sprints/sprints.base`, `05-Incidents/incidents.base`, `_agents/agent-status.base`

## Hotkeys (siehe `.obsidian/hotkeys.json`)

| Shortcut | Action |
|----------|--------|
| `Ctrl+O` | Quick-Switcher |
| `Ctrl+P` | Command Palette |
| `Ctrl+Shift+F` | Global Search |
| `Ctrl+G` | Graph View |
| `Ctrl+Shift+D` | Daily Note |
| `Ctrl+Shift+R` | Reveal Active File |
| `Ctrl+E` | Toggle Source/Preview |
| `Ctrl+Alt+L` | Lint current file |

## Backup + Sync

- **Server:** `/home/piet/vault/` (authoritative)
- **Desktop:** `C:\Users\Lenar\Obsidian\openclaw-memory\` (Syncthing)
- **Mobile:** Galaxy S24 (Syncthing-Fork)
- **Git:** `lenardhuebner88-rgb/openclaw-memory` (auto-push alle 30 min)
