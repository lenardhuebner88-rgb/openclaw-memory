# Validate Models Cron Gatekeeper

Zeitpunkt: 2026-05-04T22:57:57+02:00

## Bewertung der Aussage

Die Aussage war korrekt: `validate-models.py` hatte bisher nur Agent-Modellreferenzen geprüft. Genau die letzte Fehlerklasse lag aber in `cron/jobs.json`, also bei `payload.model` von Cronjobs. Dadurch konnte ein Cronjob erst zur Laufzeit an der `agents.defaults.models`-Allowlist scheitern.

## Umsetzung

Geändert:

- `/home/piet/.openclaw/scripts/validate-models.py`

Backup:

- `/home/piet/.openclaw/scripts/validate-models.py.bak-20260504T225610-cron-gatekeeper`

Neue harte Prüfungen:

- Alle enabled Cronjobs in `/home/piet/.openclaw/cron/jobs.json` werden gelesen.
- `payload.model` muss in `agents.defaults.models` erlaubt sein.
- `agentId` muss in `agents.list[].id` existieren.
- Fehler werden konkret ausgegeben, z. B. `CRON_MODEL_ALLOWLIST_ERROR` oder `CRON_AGENT_ID_ERROR`.
- Bei echten Fehlern erstellt das Script weiterhin optional einen Mission-Control-Follow-up-Task.

Neue Warnungen, nicht blockierend:

- `delivery.mode=announce` ohne `delivery.to`
- `timeoutSeconds > 600`
- Wartungsartige Cronjobs mit `sessionTarget=current`
- enabled `agentTurn` ohne explizites `payload.model`

## Warum diese Grenzen

Als harte Fehler eignen sich nur Dinge, die sicher zur Ausführung kaputt sind:

- unbekanntes Modell in der Allowlist
- unbekannter Agent

Timeouts und `sessionTarget` sind Architekturhinweise. Sie können absichtlich sein, z. B. `nightly-self-improvement` oder `memory-rem-backfill` mit 900 Sekunden. Deshalb bleiben sie Warnungen.

## Validierung

Ausgeführt:

```bash
python3 -m py_compile /home/piet/.openclaw/scripts/validate-models.py
python3 /home/piet/.openclaw/scripts/validate-models.py
python3 -m json.tool /home/piet/.openclaw/cron/jobs.json
python3 -m json.tool /home/piet/.openclaw/cron/jobs-state.json
/home/piet/.openclaw/scripts/openclaw-morning-launchpad.py --json
```

Ergebnis:

- Script syntax: OK
- Agent-Modellreferenzen: `All 51 cross-provider model references valid`
- Cronjobs geprüft: `13 enabled cron jobs`
- Harte Cron-Fehler: `0`
- Warnungen: `2`
  - `nightly-self-improvement`: `timeoutSeconds=900`
  - `memory-rem-backfill`: `timeoutSeconds=900`
- Launchpad Cron:
  - `currentErrors=0`
  - `historicalErrors=0`
  - `pendingVerification=0`
  - `missingAllowlistModels=0`
  - Cron Verdict: `GREEN`

## Einordnung

Der größte Hebel ist umgesetzt: Wenn künftig ein Cronjob ein Modell bekommt, das nicht in der Allowlist steht, fällt `validate-models.py` sofort mit einem konkreten Fehler aus und nicht erst beim geplanten Cron-Lauf.

## Nicht umgesetzt

Die Migration von `validate-models` aus OpenClaw-Agent-Cron in einen systemd-User-Timer wurde bewusst noch nicht umgesetzt. Das ist sinnvoll, aber ein separater Schritt mit eigener Timer-/Alerting-Definition.

## Nächster sinnvoller Schritt

Morgen als separater kleiner Umbau:

1. `validate-models.py` als systemd-User-Timer laufen lassen.
2. OpenClaw-Cronjob `validate-models` deaktivieren.
3. Nur bei Fehlern nach `#alerts` berichten.

## Nachtrag 23:04 CEST: Nightly-Job inhaltlich und technisch optimiert

Der Cronjob `nightly-self-improvement` wurde zusätzlich geprüft und geschärft.

Live-Befund:

- Run-Historie: 32 Läufe
- Erfolgreiche Läufe: 29
- Median erfolgreicher Dauer: ca. 252s
- Längster erfolgreicher Lauf: ca. 667s
- `timeoutSeconds=900` bleibt deshalb begründet.
- Inhaltliches Problem: Der Skill sagte "Forge implementiert, Nightly orchestriert", aber der Cron-Prompt forderte "Implementiere, teste, npm run build". Dadurch hat der Nightly-Job wiederholt selbst Code geändert und zusätzlich manuell nach `#atlas-main` gemeldet, obwohl Cron-Delivery nach `1488976473942392932` konfiguriert war.

Geändert:

- `/home/piet/.openclaw/workspace/skills/nightly-self-improvement/SKILL.md`
  - Version von v3 auf v4.
  - Preflight ergänzt: Mission-Control-Health und Board-Consistency vor Kandidatenauswahl.
  - Klare Grenze: kein Code schreiben, kein Build, kein Restart, keine Config-Änderung.
  - Nur noch maximal ein Forge-Task mit Execution Contract oder `blocked/no-op`.
  - Wiederholungsbremse: letzte 10 Nightly-Einträge prüfen.
  - Generische `fail-soft route hardening`-Wiederholungen nur noch mit Live-Evidence.
  - Keine manuelle Discord-Nachricht; Cron-Delivery übernimmt.
- `/home/piet/.openclaw/cron/jobs.json`
  - `nightly-self-improvement.sessionTarget=current` -> `isolated`
  - Prompt auf Orchestrator-Modus umgestellt.
  - Delivery bleibt `1488976473942392932`.

Backups:

- `/home/piet/.openclaw/workspace/skills/nightly-self-improvement/SKILL.md.bak-20260504T230246-orchestrator-tighten`
- `/home/piet/.openclaw/cron/jobs.json.bak-20260504T230246-nightly-orchestrator-tighten`

Validierung nach Nightly-Optimierung:

- `python3 /home/piet/.openclaw/scripts/validate-models.py`
  - Agent-Modelle: 51/51 valid
  - enabled Cronjobs: 12/12 model/agent valid
  - harte Cron-Fehler: 0
  - verbleibende Warnung: nur `nightly-self-improvement timeoutSeconds=900`
- Launchpad:
  - Overall: `YELLOW`
  - Gateway: `GREEN`
  - Mission Control: `GREEN`
  - Board: `GREEN`
  - Cron: `GREEN`
  - Timers: `GREEN`
  - Logs/Atlas: `YELLOW` wegen historischer Signale/aktiver Atlas-Lage, nicht wegen Cron.

## Nachtrag 23:04 CEST: `memory-rem-backfill` technisch optimiert

`memory-rem-backfill` wurde aus dem OpenClaw-AgentTurn-Pfad entfernt.

Grund:

- Der Job soll nur ein lokales Shell-Script ausführen.
- Historische Runs zeigten wiederholt Modellantworten wie `Stopped` oder `I did not run ...`.
- Das war unnötiger Modell-/Token-/Timeout-Risiko für eine deterministische Shell-Aufgabe.

Geändert:

- `/home/piet/.openclaw/cron/jobs.json`
  - `memory-rem-backfill.enabled=false`
  - `disabledReason=migrated-to-systemd-systemjob-2026-05-04`
  - `systemJob.enabled=true`
  - Command: `/home/piet/.openclaw/scripts/rem-backfill-safe.sh`
  - `successPattern=^REM_BACKFILL_OK`
- `/home/piet/.openclaw/scripts/rem-backfill-safe.sh`
  - eindeutiges Erfolgssignal ergänzt: `REM_BACKFILL_OK out=... bytes=...`
- Neuer Timer:
  - `/home/piet/.config/systemd/user/openclaw-systemjob-memory-rem-backfill.timer`
  - nächster Lauf: `2026-05-05 02:45 CEST`
  - `Persistent=false`, damit kein verpasster Lauf sofort nachgeholt wird.

Backups:

- `/home/piet/.openclaw/cron/jobs.json.bak-20260504T230034-memory-rem-systemjob`
- `/home/piet/.openclaw/scripts/rem-backfill-safe.sh.bak-20260504T230059-systemjob-ok-marker`

