---
title: MC-Board Tab-Expansion — Memory + Files + Automations (neu) + Cross-Tab-Integration
version: 1.0
status: in-execution
created: 2026-04-18 evening
owner: Operator + Atlas
sprints: 4 parallel + sequential
---

# MC-Board Tab-Expansion Plan

Vier Abend-Sprints heute (18. April, 18:00-22:00 UTC) — zwei bisher unterausgestattete Tabs (Memory + Files) plus ein neuer Tab (Automations) und eine globale Cross-Tab-Integration. Ziel: Mission Control Board als vollwertiges Operator-Cockpit für ein Multi-Agent-Setup.

## Executive Judgment

Die heute bisher aufgewerteten Tabs (Overview, Costs, Taskboard) decken nur **30 % des Operator-Bedarfs**. Drei zentrale Operator-Fragen werden aktuell nicht gut beantwortet:

1. **"Wo liegt was in meinem Memory?"** — Memory-Tab zeigt Legacy-Listing ohne Bewusstsein für die neue LTM/Working/Archive-Schichten (seit 2026-04-17).
2. **"Was läuft gerade autonom im Hintergrund?"** — 12+ Cron-Jobs, 3 Self-* Scripts, Heartbeats, Watchdog — alles verstreut in Logs, kein zentraler Steuerstand.
3. **"Wo finde ich Datei X?"** — Files-Tab ist Raw-Browser ohne Vault-Struktur-Bewusstsein.

Diese Expansion schließt alle drei Lücken gleichzeitig in einer Abend-Session.

## Ist-Analyse

### Memory-Tab (`/memory`)
**Aktuell:**
- 256 Zeilen page.tsx + 3 Components (MemoryMarkdownView, MemorySearch, CreateTaskButton)
- Liest `memory-screen-data` + `dream-health-data`
- Flat-List-View, Filter nach project/type/status/thread, Text-Search
- Keine Differenzierung zwischen LTM (Invariants), Working, Archive
- Keine Agent-Write-Attribution (wer hat welchen Memory-Eintrag zuletzt berührt)
- Promote/Archive/Delete-Flows fehlen

**Gap:** seit Session-Memory-Modell-Pilot (2026-04-17) existiert eine 3-Schicht-Struktur (`memory/invariants/`, `memory/working/`, `memory/archive/`). Der Tab weiß nichts davon.

### Files-Tab (`/files`)
**Aktuell:**
- 463 Zeilen FilesClient.tsx
- Browse + Edit Agent-Workspaces, direktes Schreiben auf Disk
- 5s-Polling
- Raw Flat-Browser, keine semantische Gruppierung

**Gap:** keine Awareness von Vault-Plans (`/vault/03-Agents/atlas-*.md`), Invariants (`/workspace/memory/invariants/`), Scripts (`/openclaw/scripts/`), Logs (`/workspace/logs/`), Backups (`.bak-*-*`). Operator muss Pfad manuell kennen.

### Fehlender Tab: Automations
**Was das System heute autonom macht (unsichtbar im Board):**
- Auto-Pickup (jede 1min)
- MC-Watchdog (jede 2min)
- Cost-Alert-Dispatcher (jede 2min)
- Worker-Monitor (jede 5min, Dispatch disabled)
- MCP-Taskboard-Reaper (jede 15min)
- Self-Optimizer (jede 15min, Dry-Run)
- Atlas-Heartbeat (jede 1h)
- Script-Integrity-Check (jede 6h)
- 10+ weitere tägliche/wöchentliche Jobs

**Heute morgen-Crisis** (3 gelöschte Scripts) wäre mit einem Automations-Tab in ≤30s sichtbar gewesen — stattdessen 1:36h unentdeckt.

## Recherche — was Agent-Ops-Dashboards brauchen

Aus Analyse von Datadog, Grafana-Agent-Console, Cursor, Anthropic-Workbench, Linear, Sourcegraph-Cody:

**5 Must-Have-Patterns die unserem Board fehlen:**

1. **Activity-Feed** (Who did What When) — chronologischer Strom aller Agent-Aktionen
2. **Automation-Dashboard** mit Kill-Switches pro Job — einheitliche Operator-Kontrolle
3. **Memory-Knowledge-Graph** — visuelle Verbindungen zwischen Invariants, Tasks, Plänen
4. **Decision-Log** — Protokoll aller Atlas-Heartbeat-Entscheidungen mit Begründung
5. **Command-Palette** (cmd+K) — Global-Search über alle Objekte (Tasks, Agents, Files, Memory)

Davon wird **#2 Automations-Dashboard** heute gebaut, **#5 Command-Palette** heute als Cross-Tab-Integration. #1, #3, #4 kommen später.

## Neuer Tab-Vorschlag: **Automations**

### Target-Design

```
┌─────────────────────────────────────────────────────────────────────┐
│  AUTOMATIONS                                            🔄 Live     │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─ Auto-Pickup ────────────────────┐ ┌─ MC-Watchdog ─────────────┐│
│  │ ●  Healthy  · every 1 min        │ │ ● Healthy · every 2 min   ││
│  │ Last: 19:23:01 · 0 triggered     │ │ Last: 19:22:01 · OK       ││
│  │ Next: 19:24:00                   │ │ [Pause] [Log]             ││
│  │ [Pause] [Log] [Edit Env]         │ │                           ││
│  └──────────────────────────────────┘ └───────────────────────────┘│
│  ┌─ Self-Optimizer ─────────────────┐ ┌─ Atlas-Heartbeat ─────────┐│
│  │ ● Dry-Run · every 15 min         │ │ ● Active · hourly 7-23    ││
│  │ Last: 19:15:02 · 2 suggestions   │ │ Last: 19:00:00 · 2 tasks  ││
│  │ [Promote to Live] [Log]          │ │ [Trigger Now] [Log]       ││
│  └──────────────────────────────────┘ └───────────────────────────┘│
│  ... weitere 8+ Cards ...                                          │
├─────────────────────────────────────────────────────────────────────┤
│  GLOBAL ACTIONS                                                      │
│  [Pause All]  [Resume All]  [Export Config]  [View Audit-Log]       │
└─────────────────────────────────────────────────────────────────────┘
```

### Datenquellen
- `crontab -l` (parsed) für Cron-Jobs
- `systemctl --user list-units` für Services
- `/api/ops/script-health` (schon live) als Gesundheits-Signal
- Pro Script eigener Log-File-Tail

### Pflicht-Features
- Pro Automation: Name, Intervall, Last-Run, Next-Run, Status (healthy/degraded/dead), Kill-Switch
- Kill-Switch via ENV-Variable oder Crontab-Kommentierung (reversibel)
- Log-Link öffnet Detail-Modal mit letzten 50 Zeilen
- Global "Pause All" bei Incident

## Die 4 Abend-Sprints

### Sprint A — Memory-Tab Redesign (Pixel, ~90min)
**Ziel:** Tab versteht 3-Schicht-Memory-Struktur.

- Drei Sektionen: **Invariants (LTM)**, **Working**, **Archive**
- Pro Sektion: Tree-View der Files mit Size + Last-Modified
- Filter: Author-Attribution (Atlas, Forge, Lens, etc.)
- Search über alle Schichten
- Actions: "Promote to Invariants" (Working → LTM), "Archive" (Working → Archive)
- Wieder-Verwendung von Pixel Phase-1-Design-Tokens
- **DoD:** Alle drei Schichten sichtbar, Search funktional, Promote-Action triggert Dialog mit Lens-Review-Hinweis

### Sprint B — Files-Tab Redesign (Pixel, ~60min)
**Ziel:** Semantic-Grouped Browser mit Vault-Bewusstsein.

- Smart-Folder-Gruppen links: **Vault-Plans** (`vault/03-Agents/atlas-*.md`), **Invariants** (`memory/invariants/`), **Scripts** (`scripts/`), **Logs** (`workspace/logs/`), **Backups** (filter on `.bak-*`)
- File-Type-Badges (md/py/ts/sh/yaml)
- Diff-View bei Click auf `.bak-*`-File (vergleicht mit Current-Version)
- Last-Modified-Author-Attribution wenn verfügbar (aus board-events)
- **DoD:** 5 Smart-Groups sichtbar, Diff-View für `.bak-*` funktional, Badge-Rendering

### Sprint C — Automations-Tab (Pixel + Forge, ~2h parallel)
**Ziel:** Zentraler Steuerstand für alle autonomen Systeme.

**Forge-Backend (~1h):**
- Neuer Endpoint `GET /api/ops/automations` aggregiert:
  - Cron-Jobs aus `crontab -l`
  - systemd-User-Services
  - Integration mit `/api/ops/script-health`
- Response pro Automation: `{name, type, schedule, lastRun, nextRun, status, killSwitchMethod, logPath}`
- Neuer Endpoint `POST /api/ops/automations/:name/pause` (setzt ENV-Flag oder kommentiert Cron-Zeile aus)
- Neuer Endpoint `POST /api/ops/automations/:name/resume` (inverse)

**Pixel-UI (~1h, parallel):**
- Neue Route `/app/automations/page.tsx`
- Grid aus Automation-Cards (design wie Overview-Hero Zone A)
- Pro Card: Status-Pill + Timer + Actions (Pause/Resume/Log)
- Log-Modal (Framer-Motion) öffnet letzte 50 Log-Zeilen
- Global-Bar: "Pause All" mit Confirm-Dialog

- **DoD:** Alle 12+ Automations aufgelistet mit Live-Status, ein Kill-Switch-Toggle funktional getestet (Auto-Pickup pause → 2min keine Trigger → resume → wieder aktiv), Log-Modal rendert real-time tail

### Sprint D — Cross-Tab Command-Palette (Forge, ~60min)
**Ziel:** Globale Search cmd+K über alle Objekte.

- Keyboard-Shortcut `cmd+K` / `ctrl+K` öffnet Modal
- Search-Index beim Modal-Open aufgebaut: Tasks + Memory-Files + Agents + Automations + Vault-Plans + Scripts
- Fuzzy-Match (fuse.js) + Recent-Items
- Click auf Result → navigiert zum jeweiligen Tab mit Focus
- Keyboard-Navigation (up/down/enter)
- **DoD:** cmd+K öffnet Modal auf jedem Tab, Search findet bestehende Task-ID in < 500ms, Navigation zu Tasks-Tab + Task-Detail ausgewählt

## Umsetzungsreihenfolge heute Abend

**Parallel von 18:00-20:00 UTC:**
- Sprint A (Pixel) — Memory-Tab Redesign
- Sprint C-Backend (Forge) — `/api/ops/automations` + Pause/Resume-Endpoints

**Sequenziell von 20:00-22:00 UTC:**
- Sprint B (Pixel nach A)
- Sprint C-UI (Pixel nach B)
- Sprint D (Forge nach C-Backend)

**Spätester Abschluss:** 22:00 UTC. Wenn Sprint D nicht mehr schafft → morgen fortsetzen.

## Files / Components

| Sprint | Lead | Files |
|---|---|---|
| A | Pixel | `src/app/memory/page.tsx`, neue `memory-layers.tsx`, `lib/memory-screen-data.ts` |
| B | Pixel | `src/app/files/FilesClient.tsx`, neue `file-groups.tsx`, `diff-view.tsx` |
| C-BE | Forge | new `src/app/api/ops/automations/route.ts`, new `src/app/api/ops/automations/[name]/pause/route.ts`, `src/lib/automation-registry.ts` |
| C-UI | Pixel | new `src/app/automations/page.tsx`, `automation-card.tsx`, `automation-log-modal.tsx` |
| D | Forge | new `src/components/command-palette.tsx`, `src/lib/search-index.ts`, integration in `src/components/mission-shell.tsx` |

## Risks

1. **Memory-Promote-Action schreibt ins LTM:** nur Atlas darf das (R12). Fix: UI rendert Button nur wenn Atlas als Actor angemeldet, sonst Read-Only-Dialog "Bitte Atlas zur Promote bitten".
2. **Automations-Pause-Toggle falsch verwendet:** Operator pausiert MC-Watchdog aus Versehen. Fix: `Pause All`-Button hat 10s-Cooldown + Confirm-Dialog mit Schadens-Einschätzung.
3. **Command-Palette-Search-Index zu groß:** bei vielen Tasks/Files. Fix: Index-Rebuild nur bei Open, max 5000 Entries.
4. **Parallel-Rebuild-Storm:** Pixel macht 3 UI-Packs hintereinander → ~3× MC-Rebuild. Mitigation: Sprint B+C-UI von selbem Pixel-Turn erfordern nur 1 Build wenn sequenziell im selben Prozess.

## Test Plan

- Sprint A: synthetic Memory-Layer-File in Working erstellt → sichtbar in UI → Promote-Button öffnet Dialog → Atlas-Self-Task getriggert
- Sprint B: `.bak-*`-File anklicken → Diff gegen aktuelle Datei korrekt
- Sprint C: Auto-Pickup pausieren → 2min Log prüfen (keine Trigger) → resume → Trigger wieder da
- Sprint D: cmd+K auf Overview-Tab → "costs" tippen → Costs-Tab in Liste → Enter navigiert

## Rollback

Pro Sprint `.bak-tab-expansion-2026-04-18`. UI-Feature-Flags: `NEXT_PUBLIC_MEMORY_LAYERS=1`, `NEXT_PUBLIC_FILES_SMART=1`, `NEXT_PUBLIC_AUTOMATIONS_TAB=1`, `NEXT_PUBLIC_COMMAND_PALETTE=1`. Bei Problem Flag auf 0 → altes UI.

## Acceptance Criteria (Pass 8/10)

1. Memory-Tab zeigt 3 Schichten getrennt, Tree-View funktional
2. Files-Tab hat 5 Smart-Groups, Diff-View funktional
3. Automations-Tab listet ≥12 Automations mit Live-Status
4. Automations-Tab Pause-Toggle für Auto-Pickup testgetrieben erfolgreich
5. Log-Modal rendert real-time (2s-Refresh)
6. Command-Palette öffnet via cmd+K auf allen Tabs
7. Command-Palette-Search findet Task + Memory-File + Automation in <500ms
8. Mobile-Layout aller 3 Tabs responsive (aus Spark-Mobile-Audit berücksichtigt)
9. Playwright-Smoke-Tests für alle 3 Tabs grün (aus P1-4 Framework)
10. Operator kann im Automations-Tab in ≤10s ablesen "welcher Job ist gerade dead"

## Recommended Agents

- **Pixel** (frontend-guru): Sprint A, B, C-UI — UI-Lead
- **Forge** (sre-expert): Sprint C-BE, D — Backend + Cross-Tab
- **Spark** (spark): optional Parallel-Task Mobile-Review für Automations-Tab nach C-UI (30min)
- **Atlas**: Orchestrator + Review der Promote-to-LTM-UX-Flows in Sprint A
- **Lens**: End-Review (22:00 UTC) — sind die 3 Tabs operativ nutzbar gemäß 10-Sekunden-Test?

## Post-Sprint-Integration

Wenn alle 4 Sprints durch:
- Board hat **6 hochwertige Tabs**: Overview, Costs, Tasks, Memory, Files, Automations
- Command-Palette als Cross-Tab-Glue
- Nächster logischer Schritt (morgen): Phase-2-Navigation 13→7 Tabs finalisieren + Tabs-Tab mit unified Activity-Feed

## Execution Tracking (2026-04-18 18:55 UTC)

| Sprint | Task ID | Board | Status |
|---|---|---|---|
| A | SPRINT-A-MEMORY-TAB-2026-04-18 | b246ba0f-858e-4909-a7f8-0c70cc133493 | ✅ DONE 19:08 |
| C-Backend | SPRINT-C-BACKEND-AUTOMATIONS-API-2026-04-18 | fe36a3eb-09fa-47c6-818b-c8299d4509a1 | ✅ DONE 19:10 |
| B | SPRINT-B-FILES-TAB-2026-04-18 | 65b3f58e-733d-43d5-9797-37930137e872 | ✅ DONE 19:19 |
| C-UI | SPRINT-C-UI-AUTOMATIONS-TAB-2026-04-18 | f696c9e3-af66-4505-9baa-a48dc9a6394b | ✅ DONE 19:29 |
| D | SPRINT-D-COMMAND-PALETTE-2026-04-18 | 1733f39d-f1e9-4c63-91aa-e778a6c79545 | ✅ DONE 19:19 |

## Trigger für Atlas

```
Lade /home/piet/vault/03-Agents/atlas-mc-board-tab-expansion-2026-04-18-evening.md
und starte Sprint A + C-Backend parallel.
Pixel bekommt Memory-Tab Redesign, Forge bekommt Automations-API.
Voller Verify-Cycle + Board-Scan.
```
