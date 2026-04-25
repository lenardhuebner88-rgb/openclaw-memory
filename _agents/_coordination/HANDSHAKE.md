# Atlas ↔ Codex Handshake

Kleiner Arbeitsstandard für gemeinsame Vault-Arbeit.

## 1. Vor neuer Arbeit
- Zuerst `_agents/_coordination/live/` prüfen.
- Bei Pfad- oder Scope-Überschneidung nicht parallel loslaufen, sondern kurz abstimmen.

## 2. Ownership
- Codex arbeitet primär in `_agents/codex/`.
- Atlas/Claude räumt Codex-Artefakte nicht still um.
- Gemeinsame Strukturänderungen nur in klaren Shared-Bereichen.

## 3. Strukturänderungen
- Nur kleiner, klar benannter Scope.
- Immer mit kurzer Navigationshilfe (`README.md` oder Index-Hinweis).
- Keine verdeckte Massenmigration nebenbei.

## 4. Retrieval first
- Ablage immer so, dass operative Suche zuerst bei Live-/Plan-Arbeit landet.
- Reports, Historie, Archive und superseded Material klar getrennt halten.

## 5. Default-Reihenfolge bei Unklarheit
1. live
2. planned / aktive Arbeit
3. reports nur für Evidenz
4. archive / superseded nur für Historie

## 6. Meeting-Modi

Meeting-Artefakte liegen unter `_coordination/meetings/`. Sie sind gemeinsame Coordination-Dateien und gehoeren keinem einzelnen Agent-Home.

### Trigger
- Chat: `Team-Meeting Debate zu <topic>`
- Chat: `Team-Meeting Council zu <topic>`
- Chat: `Team-Meeting Review fuer <target>`
- Discord: `/meeting-debate <topic>`
- Discord: `/meeting-council <topic>`
- Discord: `/meeting-review <target>`

### Teilnehmer- und Chairman-Matrix
| Modus | Aktive Teilnehmer | Chairman | Pflicht fuer Heterogenitaet |
|---|---|---|---|
| Debate | Claude Bot oder Claude Main vs. Codex, optional Lens als MiniMax-Observer | Atlas | Claude-Seite + Codex; Lens ersetzt diese Heterogenitaet nicht |
| Council | Atlas, Claude Bot, Forge, Pixel, Lens, James, Codex | Atlas | Claude Bot + Codex |
| Review | Autor + Reviewer | Codex, wenn Review-Chair benoetigt ist | Autor-Seite + Codex |

Claude Main ist interaktive Operator-Voice und Trigger-Layer. Claude Bot ist die serverseitige Claude-Seite fuer Discord-Trigger. Wenn Claude Main offline ist, ersetzt Claude Bot die Claude-Seite im Debate.

Lens kann im Debate als dritte MiniMax-Observer-Stimme eingebunden werden. Rolle: Kosten-/Tokenplan-/Long-Context-/Reality-Check mit kurzer, evidenzbasierter Notiz. Lens ist kein dritter Hauptdebattant und kein Ersatz fuer Claude-vs-Codex.

### Bounded Two-Loop Discussion
Debates duerfen als echte Diskussion in Discord laufen, aber nur mit Turn-Lock und maximal zwei Iterationsrunden. Alle Kernrollen muessen vorherige Beitraege lesen und darauf reagieren:

1. `claude-bot`
2. `codex`
3. `lens`
4. `atlas`
5. `claude-bot`
6. `codex`
7. `lens`
8. `atlas`

`/meeting-turn-next <meeting-id>` startet genau einen Turn. Der naechste Turn ist blockiert, solange `turn-lock != none` ist oder noch ein offener Meeting-Task existiert. Das ist bewusst kein Cron, kein Loop und kein freier Chat.

### Signatur-Konvention
Jeder Meeting-Post bekommt eine Signaturzeile mit UTC-Minute:

- `[claude-bot YYYY-MM-DDThh:mmZ]`
- `[claude-main YYYY-MM-DDThh:mmZ]`
- `[atlas YYYY-MM-DDThh:mmZ]`
- `[codex YYYY-MM-DDThh:mmZ]`
- `[forge YYYY-MM-DDThh:mmZ]`
- `[pixel YYYY-MM-DDThh:mmZ]`
- `[lens YYYY-MM-DDThh:mmZ]`
- `[james YYYY-MM-DDThh:mmZ]`

### Budget-Defaults
| Modus | Default | Warnung | Hard Stop | Begruendung |
|---|---:|---:|---:|---|
| Debate | 30k | 24k | 30k | Claude-vs-Codex plus kurze Lens/MiniMax-Observer-Notiz; bei mehr Turns auf Council wechseln. |
| Council | 80k empfohlen | 64k | 80k | 5-7 Agenten + 3 Phasen brauchen mehr Raum; bei 50k Council auf 5 Teilnehmer begrenzen. |
| Review | 20k | 16k | 20k | Review ist fokussiert und soll keine Council-Diskussion werden. |

### R49/R50
- R49: Jeder File-Path-, Commit-SHA-, Session-ID- oder Live-Status-Claim muss im `CoVe-Verify-Log` belegt werden.
- R50: Meetings duerfen keine aktiven Session-Locks umgehen. Claude Bot wird bevorzugt via Taskboard-Task eingebunden, nicht per direktem Session-Resume in eine aktive Main-Session.
- Token-/Runner-Crons duerfen nur mit separatem Operator-Go aktiviert werden.
