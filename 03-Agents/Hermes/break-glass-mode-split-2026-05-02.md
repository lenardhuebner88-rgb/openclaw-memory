# Hermes Betriebsmodi: Normalmodus und Break-Glass

Datum: 2026-05-02

## Normalmodus

Hermes arbeitet als Shadow-Debug-Assistant.

Erlaubte Standardquellen:

- `mc-readonly` fuer Mission Control.
- `openclaw-readonly` fuer OpenClaw Gateway, Discord Bot, Modelle, Sessions und begrenzte Logs.
- `qmd-vault` fuer Vault-/KB-Kontext.
- `skills` fuer Runbook-Auswahl.
- `session_search` fuer Hermes-eigene Sitzungshistorie.

Normalmodus bedeutet:

- Lagebild liefern.
- Runbook auswaehlen.
- Evidence/Risk/Next Action formulieren.
- Keine Mutationen vorschlagen, bevor MCP/API-Evidence vorliegt.

## Break-Glass-Modus

Break-Glass ist nur fuer Incidents gedacht, in denen OpenClaw/Atlas/Mission Control nicht handlungsfaehig sind.

Vor jedem Restart:

1. Live-Evidence.
2. exakter Service und Command.
3. erwarteter Post-Check.
4. explizite Piet-Freigabe im aktuellen Discord-Thread.

Vor jeder Config-Aenderung:

1. Live-Evidence.
2. exakter Datei-/Key-Pfad.
3. timestamped Backup.
4. explizite Piet-Freigabe im aktuellen Discord-Thread.
5. fokussierter Post-Check.

## Aktuelle Toolentscheidung

Terminal und File bleiben in Hermes verfuegbar, weil Piet Hermes im Notfall fuer Debugging und Recovery nutzen will.

Die Betriebsdisziplin kommt daher ueber:

- `openclaw-operator` Skill.
- MCP-first Tool Preference.
- Runbooks im Vault.
- explizite Approval-Gates fuer Restarts und Config-Edits.

## Perspektive

Wenn Hermes spaeter staerker getrennt werden soll, ist die naechste Ausbaustufe ein zweites Profil:

- `hermes-normal`: nur MCP/Skills/Memory, kein Terminal/File.
- `hermes-breakglass`: Terminal/File erlaubt, aber nur in dediziertem Incident-Thread.
