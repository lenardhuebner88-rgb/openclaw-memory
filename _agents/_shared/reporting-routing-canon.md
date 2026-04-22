# Reporting & Routing Canon

Status: active
Last updated: 2026-04-13

## Zweck
Diese Datei ist die kanonische Team-Wahrheit für Discord-Reporting und Ergebnis-Routing.

## Grundsatz
- Board/Receipt/Event-Log = Source of truth
- Discord-Channels = zielgerichtete Spiegel oder Arbeitsräume, nicht konkurrierende Wahrheiten
- Kein Default-Dumping nach `#atlas-main`
- `#execution-reports` ist Lifecycle-only, nicht fachlicher Ergebnis-Channel

## Channel-Regeln

### `#execution-reports`
Für kompakte Lifecycle-Mirror aus Mission Control:
- dispatch/start
- accepted/started/progress/result/blocked/failed
- knappe Status-Summaries zum Task-Lebenszyklus

Nicht hierhin:
- ausführliche fachliche Resultate
- Architektur-Diskussionen
- allgemeine Alerts

### `#alerts`
Für operative Warnungen mit Handlungsdruck:
- System-Alerts
- Cron-/Runtime-Fehler
- Token-/Gateway-/Monitor-Probleme
- Security- oder Infrastruktur-Auffälligkeiten

Nicht hierhin:
- normale Task-Erfolge
- Routine-Lifecycle-Logs
- fachliche Ergebnisberichte ohne Alarmcharakter

### Agent-Channels
Für fachliche Arbeitsergebnisse und agentenspezifische Kommunikation.
Beispiele:
- Forge/Infra → `#sre-expert`
- Pixel/UI → `#pixel-frontend-guru`
- James/Research → agentenspezifischer Research-Channel
- weitere Specialists jeweils in ihren eigenen Arbeits-Channel

Hierhin gehören:
- fachliche Result-Summaries
- Findings, RCA, Empfehlungen, Fix-Ergebnisse
- agentenspezifische Rückfragen oder Arbeitsartefakte

Nicht hierhin:
- generische Lifecycle-Spam-Events, wenn kein fachlicher Mehrwert enthalten ist

### `#atlas-main`
Für Orchestrierung und Entscheidungen:
- Priorisierung
- Architektur-/Scope-Entscheidungen
- Handoffs an Atlas
- Themen, bei denen explizit Koordination oder Entscheidung nötig ist

Nicht hierhin:
- Default-Ziel für alle Ergebnisse
- Routine-Worker-Resultate ohne Entscheidungsbedarf
- Lifecycle-Mirror aus dem Board

## Operative Ableitung
- Lifecycle-Event eines Tasks → `#execution-reports`
- Alarm/Warnung mit Operator-Bedarf → `#alerts`
- Fachliches Arbeitsergebnis eines Specialists → passender Agent-Channel
- Nur wenn Koordination/Entscheidung nötig ist → `#atlas-main`

## Auffindbarkeit
Diese Regeln sind maßgeblich dokumentiert in:
1. `03-Agents/Shared/reporting-routing-canon.md` (kanonisch)
2. `03-Agents/Atlas/working-context.md` (Atlas-Kurzregel + Verweis)
3. `03-Agents/Worker/working-context.md` (Worker-Kurzregel + Verweis)
4. `mission-control/docs/execution-report-channel.md` (Produkt-/Implementierungsregel für `#execution-reports`)
