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
| `debate` | Adversarial Schwachstellenanalyse | 2 | Atlas | 50k |
| `council` | Feature-/Strategieentscheidung | 5-7 | Atlas | 80k empfohlen, 50k Operator-Default als Soft-Start |
| `review` | Pre-Commit-/Architekturreview | 2 | Codex bei Review-Chair | 20k |

## Signaturen
Jeder Beitrag bekommt eine Signaturzeile:

`[agent YYYY-MM-DDThh:mmZ]`

Erlaubte Agent-Signaturen: `[claude-bot]`, `[claude-main]`, `[atlas]`, `[codex]`, `[forge]`, `[pixel]`, `[lens]`, `[james]`.

## Guardrails
- R49: Jeder konkrete File-/SHA-/Session-ID-Claim gehoert ins CoVe-Verify-Log.
- R50: Keine aktive Session per Meeting umgehen. Claude Bot wird ueber Taskboard-Task statt Session-Resume eingebunden.
- Meeting-Files sind append-orientiert. Parallele Writes nur mit `flock`.
- Cron-/Runner-Aktivierung braucht separates Operator-Go.
