# Coordination Meetings

Dieser Ordner enthaelt strukturierte Meeting-Artefakte fuer Debate, Council und Review. Er ist ein gemeinsamer Coordination-Bereich, kein einzelner Agent-Home-Ordner.

## Retrieval-Reihenfolge
1. Aktive Meeting-Dateien mit `status: queued` oder `status: running`.
2. Abgeschlossene Meeting-Dateien des aktuellen Tages.
3. Review-/Amendment-Reports in `03-Agents/codex/plans/`.
4. Historische Meetings nur fuer Evidenz.

## Modi
| Modus | Zweck | Aktive Sprecher | Chairman | Default Budget |
|---|---|---:|---|---:|
| `debate` | Adversarial Schwachstellenanalyse plus MiniMax-Reality-Check | 2 + Lens observer | Atlas | 30k |
| `council` | Feature-/Strategieentscheidung | 5-7 | Atlas | 80k empfohlen, 50k Operator-Default als Soft-Start |
| `review` | Pre-Commit-/Architekturreview | 2 | Codex bei Review-Chair | 20k |

## Signaturen
Jeder Beitrag bekommt eine Signaturzeile:

`[agent YYYY-MM-DDThh:mmZ]`

Erlaubte Agent-Signaturen: `[claude-bot]`, `[claude-main]`, `[atlas]`, `[codex]`, `[forge]`, `[pixel]`, `[lens]`, `[james]`.

## Debate + MiniMax Observer
Debate bleibt inhaltlich Claude-Seite vs. Codex. Lens kann als dritte MiniMax-Observer-Stimme dazukommen, wenn `participants` `lens` enthaelt. Lens soll kurz Kosten-, Tokenplan-, Long-Context- und operative Risikoaspekte pruefen und nicht die Hauptdebatte duplizieren.

## Bounded Two-Loop Discussion
Live-Diskussion in Discord ist als abgesteckter Turn-Prozess erlaubt, nicht als freier Bot-Chat.

Default fuer `debate`:

1. `claude-bot` liest Scope/Ground Truth und schreibt die Claude-Seite.
2. `codex` liest Claude und schreibt die Gegenposition.
3. `lens` liest Claude + Codex und schreibt Reality-/Kosten-/Long-Context-Review.
4. `atlas` liest alle bisherigen Beitraege und moderiert/synthetisiert Runde 1.
5. `claude-bot` reagiert auf Codex/Lens/Atlas.
6. `codex` reagiert auf Claude/Lens/Atlas.
7. `lens` prueft die zweite Runde.
8. `atlas` schreibt Abschluss-Synthese oder blockiert mit klarer Begruendung.

Guardrails:

- Pro `/meeting-turn-next` wird genau ein Turn gestartet.
- `turn-lock` muss `none` sein; offene Meeting-Tasks blockieren den naechsten Turn.
- Alle Kernrollen lesen vorherige Beitraege und reagieren darauf.
- Follow-ups bleiben Preview/Draft; kein Auto-Fanout.
- Finalize bleibt explizites Gate.

## Guardrails
- R49: Jeder konkrete File-/SHA-/Session-ID-Claim gehoert ins CoVe-Verify-Log.
- R50: Keine aktive Session per Meeting umgehen. Claude Bot wird ueber Taskboard-Task statt Session-Resume eingebunden.
- Meeting-Files sind append-orientiert. Parallele Writes nur mit `flock`.
- Cron-/Runner-Aktivierung braucht separates Operator-Go.
