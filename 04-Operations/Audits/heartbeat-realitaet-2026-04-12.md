# HEARTBEAT.md — Realität vs. Dokumentation

**Erstellt:** Lens, 2026-04-12  
**Zweck:** Präzise Korrekturvorlage für Forge — was in HEARTBEAT.md stehen sollte vs. was aktuell steht

---

## Was die Doku behauptet (IST — falsch)

HEARTBEAT.md beschreibt einen automatischen Controller-Loop:
1. Board scannen → assigned Tasks erkennen
2. `sessions_spawn(agentId:)` aufrufen → Task dispatchen
3. `runs.json` reconcilen → abgeschlossene Runs abgleichen
4. `PATCH /api/tasks/{id}/complete` oder `/fail` aufrufen
5. Heartbeat-Intervall: 5 Minuten

**Das ist ein nicht-existierender Loop.** Kein dieser Schritte ist im Code implementiert.

---

## Was real passiert (SOLL — korrekte Doku)

| Aspekt | Realität |
|--------|----------|
| Heartbeat-Intervall | **15 Minuten** (nicht 5) |
| Was der Heartbeat tut | Sendet ein Signal / HTTP-Ping an `/api/heartbeat/{agentId}` |
| Board-Scan | ❌ nicht implementiert |
| Automatischer Dispatch | ❌ nicht implementiert (`sessions_spawn(agentId:)` ist zudem gesperrt) |
| runs.json Reconciliation | ❌ nicht implementiert |
| Auto-Complete / Auto-Fail | ❌ nicht implementiert |
| Letzter echter Heartbeat | 2026-04-07 |

**Was das bedeutet:** Tasks werden NICHT automatisch aufgegriffen. Dispatch passiert nur wenn ein Mensch oder Atlas manuell einen Task erstellt und ihn einem Agenten zuweist. Kein autonomer Loop läuft.

---

## Was Forge in HEARTBEAT.md ändern soll

### Abschnitt "Controller Loop" — ersetzen durch:

```
## Heartbeat — aktueller Stand (2026-04-12)

Der Heartbeat sendet alle 15 Minuten einen HTTP-Ping an /api/heartbeat/{agentId}.

### Was der Heartbeat NICHT tut:
- kein automatischer Board-Scan
- kein automatischer Dispatch via sessions_spawn
- keine runs.json Reconciliation
- kein automatisches complete/fail

### Konsequenz:
Tasks werden nur abgearbeitet wenn sie manuell dispatched werden (via Mission Control Board oder Atlas).
Echter autonomer Loop ist ein offener Architektur-Task (DEC-20260412: Atlas-Entscheidung ausstehend).

### Intervall: 15 Minuten (nicht 5 wie historisch dokumentiert)
```

### Abschnitt "Heartbeat-Intervall" — von 5min auf 15min korrigieren

---

## Warum das wichtig ist

Solange HEARTBEAT.md einen funktionierenden Loop beschreibt der nicht existiert:
- Agenten verlassen sich auf Automation die nicht läuft
- Atlas geht davon aus dass Tasks automatisch aufgegriffen werden
- Root-Cause-Diagnosen bei hängenden Tasks beginnen im falschen Bereich
- Neue Agenten lesen falsche Erwartungen in ihr Systemverhalten

---

## Zugehörige Entscheidung

Ob ein echter Heartbeat-Controller implementiert werden soll: **Atlas-Entscheidung, steht aus.**  
Bis dahin: Doku an Realität anpassen, keine falschen Erwartungen wecken.
