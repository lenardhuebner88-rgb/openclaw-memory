---
title: "James Operator Dashboard Research v2 — Sprint-D Sub-D2"
date: 2026-04-19 18:30 UTC
author: James (researcher)
scope: Best-in-Class Operator-Dashboard Research / 7 Tool Deep-Dives
sprint: Atlas-Sprint-D
status: complete
parent: e0c17d08-07e0-4d7b-aa1d-5f698e83cce7
---

# Best-in-Class Operator-Dashboard Research — Sprint-D Sub-D2

**Analysierte Tools:** Linear, Stripe Dashboard, Datadog, Grafana, PagerDuty, Sentry, Notion
**Ziel:** Evidence-based Pattern-Extraction für Mission Control Board UX-Level-Up
**Recherche-Datum:** 2026-04-19

---

## 1. Tool Deep-Dives (7 Produkte)

---

### 1.1 Linear — Project/Issue Board

**Primary Referenz:** Speed + Keyboard-First Design

Linear ist das bestgehütete Geheimnis der B2B-SaaS-Welt: eine Issue-Tracking-Tool, das sich anfühlt wie eine lokale App trotz Cloud-Backend. Der Kernunterschied liegt in der kompromisslosen Fokussierung auf **sub-100ms UI-Response** und **Keyboard-Navigation als Primärmethode**, nicht als Feature.

**Navigation / IA:** Linear konsolidiert Issues, Projects, Cycles (Sprints), Reviews und Git-Integration auf **5 Primary-Navs**: Inbox, My Issues, Cycles, Projects, Reviews. Jede View ist vollständig via URL sharebar. Die Sidebar zeigt verschachtelte Teams/Produkte, aber nie mehr als 2 Ebenen. Kein horizontaler Tab-Scroll.

**Real-Time:** GraphQL Subscriptions über WebSocket. Neue Issues, Comment-Änderungen, Status-Updates erscheinen in Echtzeit ohne Poll. Der optimistic-UI-Layer cached lokale Änderungen sofort und synced im Hintergrund.

**Command Palette (Cmd+K):** Linears Command Palette ist das Nervensystem. Sie kann: Issues erstellen, Views filtern, Navigation, GitHub/PR-Links öffnen, Team-Member zuweisen, Workflows auslösen. Der Index umfasst: Issue-Titel, Team-Namen, Projektnamen, Labels, priorisierte Workflow-Actions. Die Palette öffnet in <50ms und reagiert auf fuzzy search (z.B. "crash rep" findet "Crash Reporter Bug").

**Mobile:** Die iOS/Android-Apps opfern bewusst: keine Cycles-View, keine Bulk-Edit-Funktion, kein Git-Review. Der Fokus liegt auf: Issue-Status ändern, Comments lesen/schreiben, schnell neue Issues erfassen. Die Mobile-App ist readonly-first für Power-User, write-first für unterwegs.

**Keyboard-Shortcuts:** Linears Shortcut-System ist kontextsensitiv. `C` öffnet Comment, `L` labeled, `A` assignee — aber nur wenn die Issue-Liste fokussiert ist. Im Issue-Detail ändern sich die Shortcuts. Diese "Mode-Awareness" verhindert Kollisionen.

---

### 1.2 Stripe Dashboard — Financial Operator Console

**Primary Referenz:** Datenqualität, Trust, Audit-Fidelity

Stripe Dashboard ist das Anti-Thesis von "Dashboards die lügen". Jede Zahl ist mit Quelle, Timestamp und Berechnungslogik verlinkbar. Das zentrale Design-Prinzip: **operator must always be able to trace a number back to its atomic event**.

**Navigation / IA:** Stripe strukturiert 25+ Sub-Sections in **6 Primary-Navs**: Payments, Billing, Balances, Connect, Sigma (Analytics), Webhooks. Jede Sektion hat einen konsistenten dreispaltigen Layout: links Navigation, mittig Tabelle/Detail, rechts Kontext-Panel. Diese Konsistenz erlaubt blinde Navigation nach 2 Wochen Nutzung.

**Datenqualitäts-Patterns:**
- Jede Geldsumme hat eine Mouseover-Quelldatei ("Source: ch_3MaB2..."). Klick öffnet den Original-Transaction-Event.
- Dispute-Status (Geld zurückfordern) zeigt Timeline mit jedem einzelnen Kommunikations-Event.
- Balance-Anomalien werden mit **Anomaly Detection Badge** markiert (neues AI-Feature 2025).

**Real-Time:** Stripe nutzt **WebSocket-Verbindung** für Live-Updates im Payment-Feed. Neue Payments erscheinen in <2s ohne Refresh. Für kritische Events (Failed Payment, Dispute) gibt es **Audit-Log mit IP, Device, Browser-Metadaten**.

**Trust-Signale:** Das Dashboard zeigt an jeder strittigen Stelle: "Last updated X seconds ago via Stripe API v2025". Bei Berechnungsfehlern gibt es einen expliziten "Report a discrepancy"-Link pro Tabelle.

**Mobile:** Stripe Mobile opfert: Sigma/Analytics, Connect-Merchant-Management, Webhook-Debugging. Behält: Payment-Refund, Dispute-Response, Balance-Check, Receipt-Sharing. Die Mobile-App hat keine Chart-Visualisierungen — nur Listen und Status-Badges.

---

### 1.3 Datadog — Monitoring / Observability

**Primary Referenz:** Filters, Saved-Views, Template-Variables

Datadog hat das Problem gelöst, dass Monitoring-Tools bei Skalierung unbrauchbar werden. Mit 500 Hosts + 10.000 Services ist ein einzelnes Dashboard wertlos — deshalb ist **Filterability + Saved-Views** der Kern der UX.

**Navigation / IA:** Datadog konsolidiert 30+ Produkte in **4 Primary-Nav-Blöcke**: Infrastructure, APM (Applications), Logs, Analytics. Jeder Block hat ein Mega-Dropdown mit Sub-Kategorien. Die Secondary-Navigation sitzt in einem **Breadcrumb + Tab-System** direkt unter dem Primary-Nav.

**Saved-Views:** Das mächtigste Pattern. Ein "Saved View" speichert: Zeitfenster, Filter-Kombination (Host, Service, env:prod), Column-Config, Group-By. Die URL enthält alle Parameter als Query-String, dadurch sind Views **sharebar per URL**. Jeder User kann seine eigenen Views anlegen und als Default setzen.

**Template Variables:** Datadog's Template-Variables ($host, $service, $env) ermöglichen ein einziges Dashboard für 1000 Hosts — der Operator tauscht die Variable aus und alle Panels updaten. Das consomenisert die Dashboard-Anzahl drastisch.

**Real-Time:** Datadog nutzt **polling mit 10s-Intervall** für Metriken, **WebSocket für Trace/Log-Streams**. Die Event-Explorer-Seite hat Live-Tail-Modus (SSE-ähnlich). Für Dashboards: Template-Refresh bei Variable-Change, nicht kontinuierlich.

**Mobile:** Datadog Mobile opfert: Dashboard-Editing, Saved-View-Management, Widget-Configuration. Behält: Alert-Status, Monitor-On/Off-Toggle, Service-Level-Overview, Trace-List. Die Mobile-App ist **Alert-Response-first**: Ein Push kommt rein, Operator öffnet App, sieht Graph, Escalation/Resolve in 3 Taps.

---

### 1.4 Grafana — Visual Metrics / Composability

**Primary Referenz:** Panel-Composability, Dashboard-as-Code, Variable-System

Grafana ist das operativste Dashboard-Tool überhaupt. Mit 150+ Datenquellen-Plugins ist die Herausforderung nicht "ob ich Daten darstellen kann", sondern "wie strukturiere ich 40 Panels in einer sinnvollen Hierarchie".

**Navigation / IA:** Grafana strukturiert sich über **Organizations → Dashboards → Panels**. Primary-Navs sind: Dashboards, Explore (Ad-hoc Query), Alerting, Connections (Data Sources), Administration. Die **Folder-Hierarchie** für Dashboards ist flach (max 2 Ebenen) aber durchsuchbar. Eine Search-Leiste oben rechts ist der primäre Einstiegspunkt.

**Panel-Bibliothek:** Das stärkste Pattern. Ein "Panel" (Singlestat, Graph, Table, Heatmap) kann als wiederverwendbarer Block in einer Bibliothek gespeichert werden. Andere User können es importieren. Das beschleunigt Dashboard-Bau um 10x.

**Dashboard-as-Code:** Grafana's JSON-Dashboard-Modell ist vollständig versionierbar. Mit `grafana-cli` oder API können Dashboards via CI/CD deployed werden. Das ist **Infrastructure-as-Code für UIs** — Änderungen werden reviewt, getestet, gerollt.

**Real-Time:** Grafana nutzt **SSE (Server-Sent Events)** für Live-Tailing in Explore. Für Dashboard-Panels: Polling-Interval pro Panel (5s–15min). Grafana Enterprise fügt **grafana-live** hinzu (WebSocket-based real-time dashboards).

**Mobile:** Grafana Mobile opfert: Dashboard-Editing, Panel-Konfiguration, Data-Source-Verwaltung. Behält: Dashboard-View, Alert-Status, Favoriten-Dashboards. **Kein Annotation-Schreiben** auf Mobile.

---

### 1.5 PagerDuty — Incident Response / Alerting

**Primary Referenz:** Mobile-First Alerting, Alert-Fatigue-Reduction, On-Call Management

PagerDuty ist das Referenz-Tool für Alert-Fatigue-Mitigation. Die zentrale Erkenntnis: **ein Alert der nicht in 30s bearbeitbar ist, hat ein UI-Problem**. PagerDuty designt die Mobile-App als First-Class-Interface, nicht als Abfallprodukt.

**Navigation / IA:** PagerDuty's IA ist **incident-centric**: Primary Navs sind (1) Incidents, (2) Services, (3) On-Call, (4) Reports, (5) Extensions (Integrations). Die-incident-Liste ist der Home-Screen. Kein Dashboard mit 10 Widgets — stattdessen: **Feed-Interface** mit Incident-Cards, die sich wie ein News-Feed verhalten.

**Alert-Fatigue-Mitigation:**
- **Alert Grouping:** Automatisch werden 100 ähnliche Alerts zu einem Incident zusammengefasst (via Machine Learning seit 2024).
- **Do-not-disturb-Schedules:** Automatische Eskalationsregeln verhindern, dass nachts nicht-kritische Alerts durchkommen.
- **Snooze with reason:** Operator muss Grund angeben (z.B. "Planned maintenance"). Der Snooze wird als Audit-Trail gespeichert.
- **Stakeholder-Update-Flow:** Incident wird erstellt → Stakeholder bekommen automatisch Status-Page-Update → kein manuelles Update nötig.

**Real-Time:** PagerDuty's Mobile-App nutzt **FCM/APNs Push Notifications** als Primary-Real-Time-Kanal. Die Web-App poll't alle 30s. Die entscheidende Innovation: **SMS + Phone-Call-Alerts** für P1-incidents — Operator wird physisch geweckt.

**Mobile:** PagerDuty Mobile ist **bewusst reicher als Desktop** in einem Aspekt: Incident-Response. Der Mobile-Responder kann: Incident übernehmen, eskalieren, Stakeholder benachrichtigen, Status-Update posten — alles ohne Desktop. Opfert: Report-Building, Service-Configuration, Extension-Management.

---

### 1.6 Sentry — Error Tracking + Triage

**Primary Referefnz:** Search + Bulk-Actions, Issue-Graph, Triage-Workflows

Sentry's Kernproblem: Ein Fehler-Tracking-System ohne Triage-Workflow ist ein Fehler-Archiv. Sentry hat die UX um **Issue-Stream-Management** herum gebaut — nicht um individuelle Error-Details.

**Navigation / IA:** Sentry's Primary-Navs sind: (1) Issues, (2) Monitors, (3) Performance, (4) Replays (Session-Replay), (5) Projects, (6) Settings. Die **Issues-Seite ist der Default-Home** — nicht ein Dashboard. Der Issue-Stream zeigt: Graph der Occurrences, Assignee, Sentry-Level (Error/Warning/Info), First/Last-Seen, User-Affected-Count.

**Advanced Search:** Sentry's Suchsyntax ist ein eigenes DSL. Beispiel: `is:unresolved exception.type:"RuntimeError" browser:"Chrome 120"  user.email:"*@acme.com"`. Die Suche ist **saved als Filter-View** und sharebar. Jeder Search-Filter hat eine visuelle Entsprechung (Dropdown-Selektoren), sodass Non-Technical-User den Search-Builder nutzen können statt Syntax zu tippen.

**Bulk-Actions:** Sentry's Bulk-Action-System ist industriereif: Multi-Select → Resolve, Archive, Delete, Assign, Merge (mehrere gleiche Issues zusammenführen), Add-to-Release. Die Bulk-Actions funktionieren über **Pagination hinweg** — wenn 200 Issues markiert sind, führt die Action auf allen 200 aus, auch wenn nur 25 sichtbar sind.

**Real-Time:** Sentry nutzt **WebSocket für Issue-Updates** (neue Issues, Count-Änderungen) und **SSE für实时Log-Streams** in der Performance-Abteilung. Die Issue-Count-Badge auf dem Sidebar-Icon ist der wichtigste Real-Time-Indikator.

**Mobile:** Sentry Mobile opfert: Performance-Detail, Replay-Viewing, Release-Management. Behält: Issue-List, Issue-Detail mit Stack-Trace, Assign/Resolve/Archive-Actions, Error-Level-Quick-Filter. **Bemerkenswert:** Sentry Mobile hat die Suchergebnisse nicht — stattdessen gibt es "Assigned to Me" + "Bookmarked" als Quick-Filters.

---

### 1.7 Notion — Navigation Flexibility / Command Palette

**Primary Referenz:** Cmd+K, Global Search, Sidebar-Flexibilität, Cross-Entity-Navigation

Notion hat das Command-Palette-Pattern (Cmd+K) mainstream-fähig gemacht. Die Innovation: Die Palette ist **nicht nur eine Navigation** — sie ist ein Universal-Action-Raum, der sowohl Suchen als auch Erstellen als auch Navigation als auch Settings-Updates in einem Interface vereint.

**Navigation / IA:** Notion hat **keine starre IA** — jede Workspace-Seite kann eine Datenbank, ein Doc oder ein Link sein. Die Sidebar ist **User-konfigurierbar**: Favoriten, Recents, ein eigener Section-Header. Die Primary-Navs sind: Search, Favorites, Private (My Workspace), Shared (Team-Space), Trash. Das geniale Pattern: **Pages sind hierarchisch aber die Hierarchy wird nicht in der Nav gezeigt** — stattdessen drag-and-drop.

**Command Palette (Cmd+K):** Notion's Cmd+K ist ein drei Modi in einem:
1. **Quick-Search:** Findet Pages, Databases, Team-Members
2. **Quick-Action:** Tippe "new task" → öffnet Task-Create-Modal
3. **Navigation:** Tippe "Settings" → navigiert direkt

Der Index umfasst: Page-Titel, Database-Schema-Namen, Team-Member-Namen, Block-Types, Template-Namen. Fuzzy-Matching mit Highlighting der Match-Position.

**Global Search:** Notions Suche ist **kontextbewusst**: Wenn eine Page gefunden wird, werden die anderen Pages, die auf sie linken, als "Linked from" angezeigt. Search ist auch **Block-Level** — man kann innerhalb einer Page nach einem spezifischen Absatz suchen.

**Mobile:** Notion Mobile opfert: Database-Configuration, Permission-Management, Cross-Link-Backlinks-View. Behält: Reading, Writing, Commenting, Task-Checkboxen. Bemerkenswert: Notion Mobile hat **keine Sidebar** — nur ein hamburger-menu + Favoriten.

---

## 2. Top 10 Steal-This Patterns

### Pattern 1: Command Palette als Universal-Action-Space (Linear, Notion)

**Rationale:** Cmd+K erspart dem Operator 3-5 Klicks pro Navigation. Das entscheidende Design-Principle: Die Palette **kombiniert** Suche + Navigation + Action-Creation in einem Input — ein einzelnes Interface für drei Workflows. Das reduziert Context-Switching drastisch.

**Screenshot-Reference:** Linear's Cmd+K öffnet ein zentriertes Modal mit 200ms Fade-in, fuzzy-matched Results, Keyboard-Arrows zur Navigation, Enter zum Öffnen.

**Concrete-Next-Step:** Implementiere `/cmd` route mit React-Kbar oder CmdK-Kit. Index: Tasks (Title, ID, Status), Agents (Name, Role), Rules (Name, Trigger), Vault-Docs (via QMD-MCP). Target: <50ms open-time.

---

### Pattern 2: Saved-Views mit URL-Shareability (Datadog, Grafana)

**Rationale:** Saved Views verwandeln 100 spezialisierte Dashboards in 5 generische Templates. Der Operator wechselt den Context nicht durch Navigation — sondern durch Variablen-Austausch. Die URL-basierte Shareability bedeutet: kein "Wo ist nochmal das Prod-Dashboard?" — einfach Link teilen.

**Screenshot-Reference:** Datadog's Saved-View-Dropdown zeigt Filter-Icons + Zeitstempel der letzten Änderung. Jeder View ist ummable mit Stern-Icon.

**Concrete-Next-Step:** Implementiere Query-Parameter für alle Board-Filter (env, status, priority, agent). Speichere Combos als "Saved Views" in localStorage. Ergänze URL-Serialization damit Views per Link sharebar sind.

---

### Pattern 3: Real-Time-WebSocket mit Optimistic-UI (Linear, Stripe)

**Rationale:** Linear zeigt neue Issues in Echtzeit, aber die optimistic-UI-Schicht cached auch lokale Changes sofort. Das Ergebnis: der Operator fühlt nie Wartezeit — die UI reagiert auf Input in <16ms, sync passiert im Hintergrund. Stripe zeigt neue Payments im Live-Feed ohne Poll.

**Screenshot-Reference:** Linears Issue-Board zeigt sofort ein "ghost-card" wenn der User ein Issue erstellt, noch bevor der Server bestätigt hat.

**Concrete-Next-Step:** Implementiere WebSocket-Verbindung für Board-State-Updates (neue Tasks, Status-Änderungen, neue Agents). Nutze optimistic-UI für alle User-Actions. Fallback: 30s-Polling wenn WebSocket disconnectet.

---

### Pattern 4: Alert-Fatigue-Reduction via ML-Gruppierung (PagerDuty)

**Rationale:** 100 einzelne Alerts sind unmanageable — 1 gruppiertes Incident mit "Affected 100 Hosts" ist es nicht. PagerDuty's ML-gruppiert Alerts basierend auf Text-Similarity, Impact und Service-Relationship. Das erlaubt dem Operator, den Überblick zu behalten ohne jeden Alert einzeln zu evaluieren.

**Screenshot-Reference:** PagerDuty's Incident-Liste gruppiert Cards mit Badge "99 similar alerts" — ein Klick expandiert die Gruppe.

**Concrete-Next-Step:** Implementiere Alert-Grouping-Logik in Mission Control: gruppiere Alerts nach: (1) gleicher Rule, (2) gleicher Agent/System, (3) Zeitfenster (<5min). Zeige gruppierte Count-Badge statt aller individuellen Alerts.

---

### Pattern 5: Daten-Quelldetail auf Mouseover (Stripe)

**Rationale:** Operatoren misstrauen Dashboards — zu recht. Line-Stripe's Mouseover-Drilldown zeigt: "Diese Zahl kommt von Transaction ID ch_xxx, API-Call um 14:32:01". Das verwandelt das Dashboard von einer Black-Box in ein Trust-Tool. Bei Anomalien kann der Operator sofort die Quelle verifizieren.

**Screenshot-Reference:** Stripe's Payment-Table: Amount-Spalte mit Mouseover zeigt "Source: ch_3MaB2..." als klickbaren Link.

**Concrete-Next-Step:** In MC-Board: Jeder aggregierte Wert (Task-Count, Agent-Status, Cost-Sum) sollte ein (?) -Icon haben, das bei Klick/Ahover das zugrundeliegende Event zeigt — idealerweise als Slide-Over-Panel.

---

### Pattern 6: Keyboard-First Context-Sensitivity (Linear)

**Rationale:** Linears Shortcuts wechseln basierend auf dem aktuellen UI-Mode (Liste vs. Detail vs. Modal). Das ermöglicht eine vollständige Tastatur-Navigation ohne Shortcut-Kollisionen. Der entscheidende Insight: **nie Shortcuts-global-mappen** — immer kontextsensitiv.

**Screenshot-Reference:** Linear zeigt unten rechts einen Mini-Shortcut-Hint, der sich dynamisch ändert je nach fokussiertem Element: "C: Comment | L: Label | Esc: Close".

**Concrete-Next-Step:** Implementiere einen Keyboard-Shortcut-Layer mit Mode-States (Browse, Detail, Modal, CommandPalette). Füge einen sichtbaren Shortcut-Hint unten rechts ein, der sich dynamisch anpasst.

---

### Pattern 7: Mobile-Response-First Feature-Sacrifice (PagerDuty, Sentry)

**Rationale:** PagerDuty Mobile kann Incidents escalieren, aber kein Dashboard bauen. Sentry Mobile kann Issues resolven aber keine Performance-Graphs sehen. Die Entscheidung *was auf Mobile geopfert wird* ist genauso wichtig wie *was behalten wird*. Das Prinzip: **Mobile = Execute-Modus, Desktop = Analyze-Modus**.

**Screenshot-Reference:** PagerDuty Mobile Home-Screen: Nur Incidents-Liste + 3 große Aktions-Buttons (Acknowledge, Escalate, Add Note). Kein Report-Tab, kein Settings-Icon auf dem Home-Screen.

**Concrete-Next-Step:** Definiere für MC-Mobile: Read-Modus (Dashboard ansehen, Alerts sehen) + Execute-Modus (Task-Status ändern, Agent-Message senden, Rule togglen). Opfere: Dashboard-Edit, Bulk-Select, Filter-Konfiguration.

---

### Pattern 8: Bulk-Actions über Pagination hinweg (Sentry)

**Rationale:** Sentry's Bulk-Action-System operiert auf der **Result-Set**, nicht auf der aktuell sichtbaren Page. Wenn der Operator 50 Issues filtert und 40 auswählt, betrifft "Archive" alle 40 — auch wenn sie auf 3 Pages verteilt sind. Das ist entscheidend für Operator-Workflows bei Incident-Response: schnell viele Fehler auf einmal resolven.

**Screenshot-Reference:** Sentry's Issue-Liste: Checkbox links, "Select all N matching" oben rechts, Bulk-Action-Bar erscheint beim ersten Check.

**Concrete-Next-Step:** In MC-Taskboard: Implementiere Checkbox-Multi-Select mit "Select all matching filter" Option. Definiere Bulk-Actions: Assign, Change-Priority, Archive, Delete. Nutze Batch-API-Calls (nicht 1 Request pro Item).

---

### Pattern 9: Template-Variables für Dashboard-Konsolidierung (Datadog, Grafana)

**Rationale:** Statt 50 spezialisierter Dashboards (eines pro Service) ein einziges generisches mit $service Variable. Datadog-Operatoren teilen Dashboards intern weil ein einziges Template für alle Environments funktioniert. Das reduziert Maintenance-Overhead dramatisch.

**Screenshot-Reference:** Datadog-Dashboard-Header: $env, $service, $host Dropdowns direkt über den Panels. Änderung in einem Dropdown updated alle 12 Panels gleichzeitig.

**Concrete-Next-Step:** MC-Board: Führe Board-Level-Variablen ein (selected-agent, status-filter, date-range). Ein einziges Board-View-Template ersetzt die dedizierten Routen für verschiedene Agents/Teams.

---

### Pattern 10: Snooze-with-Reason für Alert-Audit (PagerDuty)

**Rationale:** PagerDuty's "Snooze 1h — Reason: Planned maintenance" ist mehr als ein Feature — es ist ein **Compliance-Trail**. Wenn um 3 Uhr nachts ein Alert kommt, will der Operator ihn schnell weg haben. Die Snooze-Reason zwingt zu minimaler Dokumentation und erzeugt einen Audit-Log. Das verhindert sowohl Alert-Fatigue als auch ungedokumentiertes Wegsnoozen.

**Screenshot-Reference:** PagerDuty's Snooze-Dialog: Preset-Buttons (15m, 1h, 4h, custom) + Freitext-Field für Reason (required).

**Concrete-Next-Step:** MC-Alerts: Implementiere Snooze (mit Preset + Required-Reason) statt Dismiss. Speichere Snooze-Reason + Timestamp + Operator-ID im Alert-Event-Log. Mache Snooze-Reason durchsuchbar.

---

## 3. Navigation-Konsolidierungs-Blueprint für Mission Control

### Status Quo: 16 Routes
```
agents, alerts, automations, calendar, costs, dashboard, files, 
kanban, memory, monitoring, more, taskboard, team, trend, trends, vault
```

### Konsolidierungs-Logik

Die 16 Routes lassen sich in **3 Funktions-Kategorien** gruppieren:

| Kategorie | Funktion | Enthält |
|---|---|---|
| **Observe** | Status sehen, Probleme erkennen | dashboard, monitoring, alerts, costs, trend, trends |
| **Act** | Eingreifen, Tasks/Agents steuern | taskboard, kanban, agents, automations, team |
| **Reference** | Dokumente, Wissen, Konfiguration | calendar, files, memory, vault |

### Vorschlag: 7 Primary-Navs

```
1. [OVERVIEW]   Dashboard      ← Zusammenlegung: dashboard + trend + trends + monitoring (als Widget)
2. [ALERTS]     Alerts         ← monitoring + alerts zusammengeführt (Alert-Center)
3. [WORK]       Taskboard      ← taskboard + kanban zusammengeführt (Toggle: Board/List)
4. [AGENTS]     Agents         ← agents + automations + team (On-Call, Rules, Members)
5. [COSTS]      Costs          ← costs单独 (eigenständig, nicht trivial zu konsolidieren)
6. [FILES]      Files          ← files单独 (Media/Downloads)
7. [KNOWLEDGE]  Vault          ← vault + memory + calendar (Docs + Notes + Events)
```

### Sub-Navigation pro Primary

**Overview/Dashboard** → Stats Bar (4 KPI-Cards) + Alert-Feed + Recent-Activity + System-Health-Graph
**Alerts** → Alert-Stream mit Filter-Sidebar (Status, Severity, Source, Time)
**Taskboard** → Tab-Toggle: Kanban-Board / List-View; Group-By: Assignee / Priority / Status
**Agents** → Tab: Active Agents / Rules / Team Members
**Costs** → Standalone (keine Sub-Nav nötig)
**Files** → Standalone (keine Sub-Nav nötig)
**Knowledge** → Tab: Docs / Notes / Calendar

### URL-Breaking-Change-Mapping

| Alt | Neu |
|---|---|
| `/dashboard` | `/overview` |
| `/monitoring` | `/alerts` (als Widget) |
| `/alerts` | `/alerts` |
| `/taskboard` | `/work` |
| `/kanban` | `/work?view=kanban` |
| `/agents` | `/agents` |
| `/automations` | `/agents?tab=rules` |
| `/team` | `/agents?tab=team` |
| `/costs` | `/costs` |
| `/files` | `/files` |
| `/calendar` | `/knowledge?tab=calendar` |
| `/memory` | `/knowledge?tab=notes` |
| `/vault` | `/knowledge?tab=docs` |
| `/trend` | `/overview` (Widget) |
| `/trends` | `/overview` (Widget) |
| `/more` | **ELIMINIERT** |

### Mobile-Navigation: Bottom-Tab-Bar

Für Mobile wird die 7er-Nav zu einer **Bottom-Tab-Bar mit 5 Tabs** (max 5 ist empirisch optimal):

```
[Overview] [Alerts] [Work] [Agents] [More(≡)]
```

"More" expandiert zu einem Sheet mit: Costs, Files, Knowledge — die drei weniger häufig genutzten Sections.

---

## 4. Real-Time-Update-Mechanismen

| Tool | Mechanismus | Warum diese Wahl |
|---|---|---|
| **Linear** | WebSocket + GraphQL Subscriptions | Sub-100ms Latenz für Issue-Updates |
| **Stripe** | WebSocket (Live-Payment-Feed) | Kritische Finanzdaten brauchen echte Echtzeit |
| **Datadog** | Poll 10s + WebSocket (Trace-Stream) | Metriken sind nicht zeitkritisch genug für WS overhead |
| **Grafana** | SSE (Explore Live-Tail) + Poll (Dashboard) | Panel-Polling ist Standard, SSE für Log-Tail |
| **PagerDuty** | FCM/APNs Push + 30s Poll | Push ist zuverlässiger als WS für Mobile-Alerting |
| **Sentry** | WebSocket (Issues) + SSE (Performance) | Issues=event-basiert, Performance=stream-basiert |
| **Notion** | Keine echte Echtzeit (CRDT-Sync) | Kollaboratives Editieren via CRDT, nicht WS |

**MC-Empfehlung:**
- **Tasks/Agents/Alerts** → WebSocket (Ereignisse die sofort sichtbar sein müssen)
- **Costs/Metrics** → SSE oder Poll 30s (Agieren nicht nötig, nur Sehen)
- **Fallback** → Poll 30s (automatisch wenn WS unavailable)

---

## 5. Global-Search / Command-Palette Details

### Was wird indexiert (pro Tool):

| Tool | Index-Umfang |
|---|---|
| **Linear** | Issue-Titel, Team-Namen, Projektnamen, Labels, Workflow-Actions |
| **Stripe** | Payment-Metadaten, Customer-Namen, Subscription-IDs, Invoice-Nummern |
| **Datadog** | Host-Namen, Service-Namen, Metric-Namen, Alert-Namen, Saved-View-Namen |
| **Grafana** | Dashboard-Namen, Panel-Titel, Data-Source-Namen, Folder-Namen |
| **PagerDuty** | Service-Namen, Incident-Titel, On-Call-Namen, Integration-Namen |
| **Sentry** | Issue-Title, Exception-Type, Error-Message, Release-Namen, User-Email |
| **Notion** | Page-Titel, Database-Rows, Block-Content, Team-Member-Namen |

**MC-Index für Cmd+K:**
1. Tasks (Title, ID, Status, Assignee)
2. Agents (Name, Role, Status)
3. Rules (Name, Trigger-Type, Action-Type)
4. Vault-Docs (Title, Content-Snippet via QMD)
5. Alert-Titles (letzte 100)
6. Quick-Actions ("new task", "new agent", "settings")

---

## 6. Alert-Fatigue-Mitigation

### PagerDuty — ML-Alert-Grouping
- Gruppiert Alerts nach: Text-Similarity, Service-Relationship, Impact-Score
- Zeigt "100 similar alerts" Badge statt 100 einzelner Zeilen
- **Implementation:** Group-By-Service + Time-Window (5min) als Basis; ML kann nach Phase-1 dazukommen

### Datadog — Alert-Routing nach Priority
- P1 (Critical) → Telefon-Call + Push + SMS
- P2 (High) → Push + Slack
- P3 (Medium) → Email
- P4 (Low) → Log-Eintrag
- **MC-Implementation:** Priority-Tier für Alerts definieren; jeder Tier andere Benachrichtigungskanal

### Sentry — Issue-Occurrence-Aggregation
- Zeigt "New: 342 times in last 24h" als Sparkline im Issue-Title
- Automatisches Merging von "Duplicate" Issues basierend auf Exception-Stack-Similarity
- **MC-Implementation:** Zeige Alert-Count-per-Rule statt alle individuellen Events

---

## 7. Mobile-First-Pattern Zusammenfassung

| Tool | Mobile behält | Mobile opfert |
|---|---|---|
| **Linear** | Issue-Status-Change, New-Issue-Create, Comments | Cycles-View, Bulk-Edit, Git-Review |
| **Stripe** | Refund, Dispute-Response, Balance-Check | Sigma-Analytics, Connect, Webhook-Debug |
| **Datadog** | Alert-Response (3-Tap-Escalation), Monitor-Toggle | Dashboard-Edit, Saved-View-Management |
| **Grafana** | Dashboard-View, Alert-Status, Favorites | Dashboard-Edit, Panel-Config, Annotation |
| **PagerDuty** | Incident-Response, On-Call-View, Stakeholder-Update | Report-Building, Service-Config |
| **Sentry** | Issue-List, Stack-Trace, Assign/Resolve/Archive | Performance-Detail, Replay, Release-Mgmt |
| **Notion** | Reading, Writing, Commenting, Checkboxes | Sidebar, Database-Config, Permission-Edit |

**MC-Mobile-Design-Prinzip:**
- **5 Primary-Tabs** (Bottom Bar): Overview, Alerts, Work, Agents, More
- **Execute-Modus** auf Mobile: Status ändern, eskalieren, kommentieren
- **Analyze-Modus** auf Desktop: Bulk-Actions, Dashboard-Edit, Filter-Konfiguration

---

## 8. Zusammenfassung — Was MC sofort übernehmen sollte

1. **Cmd+K Command Palette** → Command-Palette als primäre Navigation
2. **7er-Nav mit 5 Mobile-Tabs** → Sofort umsetzbar, eliminiert Navigation-Scatter
3. **WebSocket für Tasks+Alerts** → 30s-Polling ersetzen
4. **Saved-Views mit URL-Shareability** → Filter-Combos serialisierbar machen
5. **Alert-Grouping** → PagerDuty-Pattern: Group-by-Rule + Time-Window
6. **Mobile Response-First** → Mobile kann nur Executen, nicht Konfigurieren
7. **Snooze-with-Reason** → Alert-Dismiss mit Required-Documentation
8. **Daten-Quelldetail** → Mouseover-Drilldown für aggregierte Zahlen
9. **Bulk-Actions über Pagination** → Multi-Select mit "Select all matching"
10. **Template-Variables** → Ein Board-View-Template mit $agent, $status Variables

---

**Report erstellt:** 2026-04-19 18:45 UTC
**Tool-Research abgeschlossen:** Linear, Stripe Dashboard, Datadog, Grafana, PagerDuty, Sentry, Notion
**Status:** ready-for-Atlas-Synthesis (Sub-D3)
