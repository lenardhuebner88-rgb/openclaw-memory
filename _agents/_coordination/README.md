# Agent Coordination Board

Kleine Struktur für agentische Koordination:

- `live/` — aktuell laufende oder gerade relevante Koordinations-Sessions
- `archive/` — ältere, abgeschlossene oder historisch nur noch referenzierte Session-Notizen

## Retrieval-Reihenfolge
1. `live/`
2. `archive/` nur bei Verlauf, RCA oder Handoff-Historie

## Live sessions

```dataview
TABLE started, ended, task, file.link AS session
FROM "_agents/_coordination/live"
WHERE agent
SORT started DESC
```

## Archive

```dataview
TABLE started, ended, agent, task, file.link AS session
FROM "_agents/_coordination/archive"
WHERE agent
SORT started DESC
LIMIT 30
```

Ohne Dataview: zuerst `ls _agents/_coordination/live/`, nur bei Bedarf danach `archive/` prüfen.
