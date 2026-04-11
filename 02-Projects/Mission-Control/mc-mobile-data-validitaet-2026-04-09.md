# MC Mobile — Daten Validität Report
**Datum:** 2026-04-09
**Analysierte App:** Mission Control Mobile (http://192.168.178.61:3000)
**Tabs analysiert:** Dashboard (/), Agents (/agents), Tasks (/taskboard), Team (/team), More (/more)

---

## Tab: Dashboard (`/`)
### Befund: PROBLEM

### Datenkorrektheit:
- Dashboard zeigt KEINE live Operations-Daten. Es ist eine reine Landing-Page mit drei Navigation-Buttons ("Open Taskboard", "Agents", "Team").
- Keine Workload Heatmap, kein System Health Summary, keine Operational Summary vorhanden.
- Text sagt "Live operations are available below" — aber darunter sind nur Links, keine Live-Daten.

### Freshness:
- N/A (keine Live-Daten vorhanden)

### Konsistenz:
- Keine konsistenzrelevanten Daten

### Issues:
1. **Dashboard ist keine echte Übersicht** — es fehlt eine operative Zusammenfassung mit KPIs, Agent-Status und aktiver Arbeit.
2. **"More" Tab existiert nicht** — von Dashboard aus kein Zugang zu Einstellungen oder zusätzlichen Funktionen.

---

## Tab: Agents (`/agents`)
### Befund: PROBLEM

### Datenkorrektheit:
- **Model-Feld zeigt "unknown"** für 3 von 7 Agents:
  - Pixel (frontend-guru): model="unknown" — `/api/team-models` sagt aber `minimax/MiniMax-M2.7-highspeed`
  - Pulse (model-monitor): model="unknown" — nicht in `/api/team-models` enthalten
  - Spark (ideen): model="unknown" — nicht in `/api/team-models` enthalten
- **Model-Mismatch Forge:** agents/live zeigt `MiniMax-M2.7-highspeed`, aber `/api/team-models` sagt `openai-codex/gpt-5.3-codex`
- **team-models API unvollständig:** Nur 4 Agents zurückgegeben (main, sre-expert, frontend-guru, efficiency-auditor); quick, model-monitor, ideen fehlen komplett.
- **Fallback-Mismatch:** `/api/fallback-check` zeigt 2 Findings:
  - main: expected=`minimax/MiniMax-M2.7-highspeed`, actual=`MiniMax-M2.7-highspeed` (Provider-Präfix fehlt)
  - sre-expert: expected=`gpt-5.3-codex`, actual=`MiniMax-M2.7-highspeed` (komplett falsch)

### Freshness:
- Refresh-Intervall: 15 Sekunden (SWR) ✅
- agents/live updatedAt: aktuell ✅
- Pulse (model-monitor): `lastActive` fehlt komplett im JSON — weder timestamp noch leerer String
- Flash (quick): `lastActive` = 6730 min (≈ 4.5 Tage) alt, aber status="offline" — stale timestamp als current value
- Spark (ideen): status="offline" aber lastActive zeigt nur 49 min — widersprüchlich

### Konsistenz:
- **Workload API** zeigt `name="frontend-guru"` (Agent-ID statt Display-Name "Pixel") für frontend-guru
- `/api/agents/live` zeigt korrekt `name="Pixel"` — Workload und Live stimmen nicht überein
- Agents-Tab zeigt "4/7 online" im Status-Label, Workload API zeigt aber "free" für 5 von 7 Agents

### Issues:
1. **[KRITISCH] Model "unknown" für 3 Agents** — Pixel, Pulse, Spark zeigen "unknown" obwohl echte Modelle konfiguriert sind
2. **[KRITISCH] Model-Mismatch Forge** — agents/live zeigt falsches Model (MiniMax statt GPT-5.3-Codex)
3. **[HOCH] team-models API unvollständig** — nur 4/7 Agents, quick/model-monitor/ideen fehlen
4. **[HOCH] fallback-check aktiv** — 2 Agents mit Model-Divergenz
5. **[MITTEL] Workload name inconsistency** — "frontend-guru" statt "Pixel" in workload API
6. **[MITTEL] Pulse lastActive fehlt** — JSON-Feld komplett absent
7. **[NIEDRIG] Flash lastActive stale** — 4.5 Tage alter Timestamp als current

---

## Tab: Tasks (`/taskboard`)
### Befund: OK (mit Einschränkungen)

### Datenkorrektheit:
- 62 Tasks insgesamt: 58 done, 4 draft
- Alle Tasks haben vollständige Felder (title, status, updatedAt, lastActivityAt) ✅
- Keine "unknown", null, "-" oder leere Cards sichtbar ✅
- Task-Board hat 5 Spalten: Review, In Progress, Assigned, Draft, Done
- 4 Draft-Tasks sind Sprint-bezogene Tasks (Sprint 6.1–6.3, Sprint 5.5) — korrekter Zustand

### Freshness:
- Draft-Tasks sind alle von heute (2026-04-09) ✅
- Keine stale-Tasks im Board sichtbar ✅

### Konsistenz:
- **10 Done-Tasks ohne resultAt** — diese Tasks sind done aber haben kein `resultAt` timestamp
  - Prüfen: Haben diese Tasks wirklich kein Ergebnis produziert oder fehlt nur das Feld?
- Kein dispatchState/Status-Widerspruch ✅ (keine Tasks mit dispatchState=completed aber status≠done)

### Issues:
1. **[MITTEL] 10 Done-Tasks ohne resultAt** — möglicherweise fehlende Ergebnisdokumentation
2. **[NIEDRIG] Keine visuelle stale-Indikatoren** im Taskboard-UI — keine optische Kennzeichnung von alten Timestamps

---

## Tab: Team (`/team`)
### Befund: PROBLEM

### Datenkorrektheit:
- Team-Seite zeigt 7 Agents mit Karten (Atlas als Leader + 6 Agents in Gruppen)
- **memoryStats hardcoded:** `{ entries: 247, openDecisions: 3, lastUpdated: "2 hours ago" }`
  - Dieser Wert wird statisch in `getTeamScreenData()` gesetzt — keine Live-Abfrage
- **costStats hardcoded:** `{ todayCost: "$2.34", monthCost: "$67.89", burnRate: "$3.45/day" }`
  - Ebenfalls statisch in `getTeamScreenData()` — keine Live-Kostenabfrage
- Agent-Cards zeigen korrekte Rollen, Status-Dots, Health-Score (0–100%)
- SoulEditLink zeigt korrekte Pfade zu SOUL.md Dateien ✅

### Freshness:
- Team-Karten aktualisieren sich alle 15s via SWR ✅
- memoryStats und costStats werden NIEMALS aktualisiert — zeigen statische Werte
- "2 hours ago" als lastUpdated ist irreführend wenn die Daten Tage alt sind

### Konsistenz:
- Team-Seite bezieht Model-Daten aus `/api/agents/live` (overlay.model) — damit gelten die gleichen Model-unknown-Probleme wie im Agents-Tab
- System Health Panel zeigt onlineCount basierend auf SWR-live-Daten ✅

### Issues:
1. **[KRITISCH] memoryStats komplett statisch** — 247 entries, 3 openDecisions sind Hardcoded, keine Live-Abfrage
2. **[KRITISCH] costStats komplett statisch** — "$2.34", "$67.89", "$3.45/day" sind Fake-Daten
3. **[MITTEL] "lastUpdated: 2 hours ago" irreführend** — memoryStats werden gar nicht aktualisiert

---

## Tab: More (`/more`)
### Befund: PROBLEM

### Datenkorrektheit:
- **HTTP 404 — Seite existiert nicht**

### Freshness:
- N/A

### Konsistenz:
- N/A

### Issues:
1. **[KRITISCH] /more Route existiert nicht** — 404 bei Zugriff. Die Route fehlt komplett in `src/app/`
2. **[MITTEL] Fehlende Settings/Configuration-Seite** — kein Ort für Agent-Konfiguration, Cron-Job-Verwaltung, etc.

---

## TOP 5 Kritischste Daten-Probleme (nach Priorität)

### 1. ⚠️ Model "unknown" für 3 Agents + Model-Mismatch Forge
- **Betroffen:** Agents-Tab, Team-Tab
- **Problem:** Pixel, Pulse, Spark zeigen "unknown" als Model; Forge zeigt falsches Model
- **Root Cause:** `getAgentOverlay()` in `live-agent-data.ts` kann Model nicht aus sessions.json auflösen; `/api/team-models` ist unvollständig
- **Impact:** Keine Model-Transparenz, keine Kostenkontrolle möglich

### 2. ⚠️ Team costStats und memoryStats sind komplett hartcodiert
- **Betroffen:** Team-Tab
- **Problem:** `$2.34 today / $67.89 month` und `247 entries / 3 open decisions` sind statische Fantasiewerte
- **Root Cause:** In `getTeamScreenData()` direkt eingesetzt statt live abgefragt
- **Impact:** Falsche Kostenübersicht, falsche Memory-Statistiken — Entscheidungen auf Basis Fake-Daten

### 3. ⚠️ /more Route fehlt komplett (404)
- **Betroffen:** Navigation
- **Problem:** "More" Tab existiert nicht — 404 Error
- **Root Cause:** Keine Route in `src/app/more/` implementiert
- **Impact:** Kein Zugang zu Settings, Cron-Verwaltung, etc.

### 4. ⚠️ Fallback-Check aktiv mit 2 Findings
- **Betroffen:** Agents-Tab, Dashboard (implizit)
- **Problem:** main und sre-expert haben Model-Divergenz zwischen expected vs actual
- **Root Cause:** Provider-Präfix-Inkonsistenz (`minimax/` vs ohne Präfix) und Forge nutzt完全是 falsches Model
- **Impact:** Modell-Switching funktioniert nicht korrekt, Billing可能会durcheinander

### 5. ⚠️ Workload API name inconsistency
- **Betroffen:** Agents-Tab, Dashboard
- **Problem:** `frontend-guru` zeigt "frontend-guru" statt "Pixel" in workload API; `lastActive=null` für 4 Agents
- **Root Cause:** Workload-Logik nutzt Agent-ID statt Display-Name aus anderer Quelle
- **Impact:** Inkonsistente Darstellung zwischen Tabs, `null` lastActive für offline Agents irreführend

---

## Zusammenfassung

| Tab | Befund | Kritische Issues |
|-----|--------|-----------------|
| Dashboard (/) | ⚠️ PROBLEM | Dashboard keine Live-Daten |
| Agents (/agents) | ⚠️ PROBLEM | Model unknown, Mismatch, Stale timestamps |
| Tasks (/taskboard) | ✅ OK | 10 Done-Tasks ohne resultAt |
| Team (/team) | ⚠️ PROBLEM | Fake costStats, Fake memoryStats |
| More (/more) | ❌ 404 | Route fehlt |

**Gesamtbewertung: 3 von 5 Tabs haben kritische Datenprobleme.**
