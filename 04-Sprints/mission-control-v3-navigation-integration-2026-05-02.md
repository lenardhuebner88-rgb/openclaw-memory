# Mission Control V3 — Overview-first Navigation & Panel Integration

Stand: 2026-05-02
Owner: Atlas
Review: Lenard-Korrektur eingearbeitet
Scope: Mission Control V3 soll als Übersichtsplattform starten. Das Taskboard ist nicht der zentrale Hub, sondern ein wichtiger Arbeits-Tab innerhalb eines konsistenten Dashboard-Systems.

## Lenard-Review / Korrektur

Die vorherige Richtung war zu taskboard-zentriert. Korrektur:

- Der erste Einstiegspunkt ist `Overview`.
- `Overview` ist die eigentliche Übersichtsplattform mit KPIs, laufenden Arbeiten, Risiken, Agent-/Team-Zustand und nächsten Entscheidungen.
- `Tasks` ist ein Arbeitsbereich für Detailsteuerung, nicht der Startpunkt.
- Navigation muss oben klar zwischen `Overview`, `Tasks`, `Team`, `Agents` und weiteren Bereichen wechseln lassen.
- V3-Design soll die alte klare Struktur übernehmen, aber visuell moderner und konsistenter machen.

## Ausgangslage

- Mobile Navigation zeigt aktuell bereits Hauptbereiche, wirkt aber noch wie ein Drawer für einzelne Tools.
- `Taskboard` / `Production Table V3` steht optisch noch zu isoliert neben den übrigen Tabs.
- `/ops`, `/alerts`, `/team` nutzen bereits V3-Operator-Patterns: dunkle Layer, Summary-Strips, KPI-Cards, Chips, responsive Cards.
- `/team` Proof-Follow-up ist abgeschlossen und grün: Commit `047b6e4`, zwei frische `qa:v3-tab` Runs PASS.
- Damit ist der Weg frei für eine Navigation-/Overview-Integration als nächster sauberer V3-Schritt.

## Zielbild

Mission Control öffnet immer in einer echten Operator-Übersicht:

1. `Overview` beantwortet: Was läuft gerade? Was braucht Aufmerksamkeit? Was ist als nächstes dran?
2. Top Navigation verbindet die Kernbereiche direkt und sichtbar.
3. Jeder Tab hat eine klare Aufgabe und denselben V3-Rahmen.
4. Taskboard bleibt stark, wird aber als `Tasks`-Arbeitsfläche eingebettet.
5. Panels werden über Cross-links verbunden, damit man aus der Übersicht direkt in Details springen kann.

## Primäre Navigation oben

Empfohlen für Desktop und Tablet:

- `Overview`
- `Tasks`
- `Team`
- `Agents`
- `Alerts`
- `Memory`
- `Automate`
- `More`

Priorität sichtbar oben:

1. Overview
2. Tasks
3. Team
4. Agents
5. Alerts

Alles weitere kann bei Platzmangel in `More` oder sekundäre Gruppen.

## Mobile Navigation

Empfehlung:

- Bottom-Bar maximal 5 Hauptpunkte:
  - Overview
  - Tasks
  - Team
  - Alerts
  - More
- `Agents` bleibt mobil erreichbar über Team-Subnav und Drawer.
- Drawer bleibt Vollnavigation, aber kuratiert und konsistent:
  - Overview
  - Tasks
    - Production Table
    - Pipeline
  - Team
    - Team Overview
    - Agents
  - Alerts
  - Memory
  - Automate
  - More

## Tab-Aufgaben

### Overview — Einstiegspunkt

Zweck: schnellster Überblick über Mission Control.

Inhalte:

- System Health / Gateway / Mission Control Status
- aktive Tasks und laufende Worker-Runs
- Risk / Blocker / Review-Zähler
- letzte wichtige Receipts / Ergebnisse
- Agent-Verfügbarkeit und aktive Owner
- Alerts / Incidents mit Schweregrad
- nächste empfohlene Aktion
- Quick Links in die Detailbereiche

Layout:

- Top: Operator Summary Hero
- Row 1: KPI Cards `Health`, `Active`, `Risk`, `Review`, `Pickup`, `Done today`
- Row 2: `Running Now` + `Needs Attention`
- Row 3: `Team Load` + `Latest Receipts`
- Row 4: `Alerts` + `Next Actions`

### Tasks — Arbeitsfläche

Zweck: operative Task-Steuerung.

Unteransichten:

- `Production Table` = primäre Task-Liste / Taskboard V3
- `Pipeline` = Kanban-/Flow-Ansicht
- optional später `Review Queue`

Wichtig: Tasks ist nicht der Hub, sondern die Detailwerkbank aus der Overview heraus.

### Team — Verantwortlichkeit

Zweck: Wer ist zuständig, verfügbar, belastet?

Inhalte:

- Team-/Agent-Gruppen
- Owner State
- Response Readiness
- Handoff Risk
- aktive Tasks je Owner

### Agents — Agent-Detailsteuerung

Zweck: einzelne Agenten verstehen und steuern.

Inhalte:

- Agent Profile
- Tools / Allowlist
- aktive Session
- Modell / Routing
- letzte Ergebnisse
- Agent-spezifische Tasks

### Alerts — Störungen und Signale

Zweck: Was ist kritisch und was hängt daran?

Inhalte:

- Incident Cards
- Severity KPIs
- betroffene Tasks / Agents
- Action Links zu Tasks und Team

## Panel-Verbindung

Cross-linking wird zentral:

- Overview `Active Tasks` -> Tasks mit Filter `active`
- Overview `Risk` -> Tasks mit Filter `risk/blocker`
- Overview `Agent Load` -> Team oder Agents
- Overview `Alerts` -> Alerts Detail
- Alert Detail -> betroffene Tasks + zuständiger Agent
- Team Agent Card -> Tasks gefiltert auf Agent
- Task Detail -> Agent Detail + Receipts + Proof Artifacts
- Memory -> relevante Sprint-/Decision-Kontexte

## V3 Design-Regeln

- Eine gemeinsame Topbar / Primärnavigation.
- Hero/Summary pro Tab mit einheitlicher Sprache.
- KPI Cards oben, Detailpanels darunter.
- Section Links nur innerhalb eines Tabs, nicht als Ersatz für Topnav.
- Mobile: Bottom-Bar für Hauptbereiche, Section Actions für Unteransichten.
- Keine doppelte Navigation, keine isolierten Spezialseiten.

## Umsetzung in Slices

### Slice 1 — Navigation Taxonomy & Shell

Ziel: Obere Navigation sauber auf Overview-first umbauen.

DoD:

- `Overview` ist erster und aktiver Einstiegspunkt.
- Topnav enthält mindestens `Overview`, `Tasks`, `Team`, `Agents`, `Alerts`.
- Mobile Bottom-Bar startet mit `Overview`.
- Drawer gruppiert sauber nach Hauptbereichen.
- `Taskboard` wird unter `Tasks` eingeordnet, aber nicht als Hub bezeichnet.
- `Kanban` wird als `Pipeline` bezeichnet.
- Keine Datenlogik-Änderungen.
- `npm run typecheck` PASS.
- `qa:v3-tab` PASS für `/overview`, `/taskboard`, `/team`, `/agents` soweit möglich.

### Slice 2 — Overview V3 als echte Übersichtsplattform

Ziel: `/overview` wird der operative Startscreen.

DoD:

- KPI-Grid für Health, Active, Risk, Review, Pickup, Done Today.
- Running Tasks Panel.
- Needs Attention Panel.
- Team/Agent Load Panel.
- Latest Receipts Panel.
- Alerts Summary Panel.
- Next Actions Panel.
- Links führen in Tasks/Team/Agents/Alerts mit sinnvoller Filterung oder Zielroute.

### Slice 3 — Taskboard Integration

Ziel: Taskboard als `Tasks`-Tab visuell und navigativ einbetten.

DoD:

- Header nicht mehr isoliert `Taskboard`, sondern `Tasks / Production Table`.
- Lokale Chips bleiben als View-/Filtersteuerung.
- Backlinks zur Overview.
- Detaildrawer verlinkt zu Agent/Team und Proofs.

### Slice 4 — Cross-panel Linking

Ziel: Panels werden wirklich verbunden.

DoD:

- Overview-KPIs öffnen passende Task-/Agent-/Alert-Ansichten.
- Team Agent Cards öffnen Tasks für Agent.
- Alerts öffnen betroffene Tasks.
- Task Detail öffnet Agent-Detail und Proof-Kontext.

## Konsolidierte Empfehlung

Nächster Pixel-Task sollte nicht `/memory` sein, sondern:

`MissionShell V3 Overview-first Navigation`

Danach folgt:

`Overview V3 Operator Dashboard`

Erst danach weitere Panel-Migrationen wie `/memory`.

Warum:

- Lenards Ziel ist eine Übersichtsplattform, nicht ein schöneres Taskboard.
- Navigation ist die Grundlage, damit alle V3-Seiten zusammengehören.
- Overview muss die Frage beantworten: Was steht gerade an und was läuft gerade?
- Taskboard bleibt wichtig, wird aber bewusst als Detailarbeitsbereich eingeordnet.

## Offene Entscheidung

Vor Dispatch an Pixel sollte Lenard final bestätigen:

- Topnav-Reihenfolge: `Overview | Tasks | Team | Agents | Alerts | Memory | Automate | More`
- Mobile Bottom-Bar: `Overview | Tasks | Team | Alerts | More`
- Sichtbarer Name im Tasks-Tab: `Tasks` oben, Unteransicht `Production Table`

## Update — Team Proof abgeschlossen

Stand: 2026-05-02

- Pixel-Follow-up `272859eb-536f-47c7-9712-55bf429729a9` ist abgeschlossen.
- Commit `047b6e4` stabilisiert `qa:v3-tab` für live/polling routes und behebt `/team` Proof-Instabilität.
- Atlas Final Proof:
  - `npm run typecheck`: PASS
  - `npm run qa:v3-tab -- --route /team --name team-v3-operator-slice-atlas-final-proof --port 3014 --marker "Team Response Surface · v3 operator slice" --outDir qa/results/atlas-final-team-proof-2026-05-02/team`: PASS
  - summary `ok=true`, Desktop/Mobile HTTP 200, Marker present, keine Console/Page Errors, kein Overflow, mobile Touch Targets ok.

Entscheidung: Nächster Fokus ist die Navigationsleiste / Overview-first MissionShell. Kein `/memory`-Rollout als nächster Schritt.
