# OpenClaw Launchpad: Cron-State und Timeout-Fenster — 2026-05-04

## Ziel

Das Morning Launchpad soll morgen nicht wegen alter Fehler unnötig laut sein.

Umgesetzt wurden Punkt 1 und 2:

1. Cron-State-Fehler werden in **aktuell** und **historisch / noch zu verifizieren** getrennt.
2. Gateway-/Timeout-Signale werden in **seit Gateway-Restart**, **letzte 60 Minuten** und **historisches 12h-Fenster** getrennt.

Punkt 3, Atlas Proposal Autonomy, bleibt bewusst für morgen.

## Warum

Vorher wurde das Launchpad gelb/rot, weil alte 12h-Fehler mit aktuellen Blockern vermischt wurden.

Live-Befund:

- `jobs.json` ist inzwischen so weit sauber, dass `missingAllowlistModels=0`.
- `jobs-state.json` enthält aber noch 8 alte Fehlerstände von früheren Cron-Ausführungen.
- Diese Jobs sind nicht automatisch aktuell kaputt; sie müssen beim nächsten geplanten Lauf verifiziert werden.
- Gateway-Logs enthalten viele historische Timeout-/Fallback-Signale aus den Stabilisierungsläufen.
- Seit dem letzten Gateway-Restart gab es keine aktuelle Atlas-/Forge-Fallback-Kette; die aktuellen Signale sind vor allem Discord ACK Timeout Noise.

## Geänderte Datei

- `/home/piet/.openclaw/scripts/openclaw-morning-launchpad.py`

## Technische Änderung

### Cron-State

Neu:

- `cron.currentErrors`
- `cron.historicalErrors`
- `cron.pendingVerification`
- `cron.missingAllowlistModels`

Kriterium:

- Wenn `lastRunAtMs < mtime(jobs.json)`, wird ein alter Cron-Fehler als historisch klassifiziert.
- Wenn der Fehler nach der letzten `jobs.json`-Änderung auftritt, ist er aktuell.

Aktueller Stand beim Dry-run:

```text
currentErrors=0
pendingVerification=8
historicalErrors=8
missingAllowlistModels=0
```

Interpretation:

Config ist nicht aktuell blockiert, aber die nächsten Cronläufe müssen den alten State überschreiben.

### Timeout-/Logfenster

Neu:

- `journalSignals.last60m`
- `journalSignals.sinceGatewayRestart`
- `journalSignals.last12h`

Zusätzlich wurden Modelltimeouts von generischem `timed out` und Discord ACK Timeouts getrennt:

- `modelTimeouts`
- `llmRequestTimeouts`
- `discordAckTimeout`
- `allTimedOut`

Damit kann Atlas morgens GREEN/YELLOW auf Basis aktueller Modellprobleme bewertet werden, ohne dass alte Stabilisierungsläufe alles übersteuern.

## Aktueller Dry-run-Befund

Während der Validierung war Mission Control kurz offline, weil parallel ein anderer Codex-App-Prozess einen kontrollierten Build/Restart ausführte:

```text
/home/piet/.openclaw/bin/mc-restart-safe --refresh-build 600 codex-board-quality-chart-stability
```

Dieser Prozess wurde nicht angefasst.

Launchpad-Logik selbst:

```text
Cron currentErrors=0
Cron pendingVerification=8
Gateway sinceRestart: failover=0, candidateFailed=0, commandLaneTimeout=0
Atlas: keine Overrides, gpt-5.5, openai-codex, runtime pi
```

## Morgen: Punkt 3 separat

Nicht heute umgesetzt:

Atlas Proposal Autonomy.

Morgen sinnvoller nächster Schritt:

1. Erst Morning Launchpad prüfen.
2. Nur wenn Gateway, Mission Control, Guard und Atlas-Session sauber sind:
   - Atlas darf maximal 1 Draft-Task vorschlagen.
   - Kein Dispatch.
   - Keine Ausführung.
   - Keine Config-/Session-/Cron-Mutation.
3. 24h beobachten, bevor Atlas weitere Autonomie bekommt.

## Qualitätsgate

Vor Abschluss:

- `python3 -m py_compile /home/piet/.openclaw/scripts/openclaw-morning-launchpad.py`
- Launchpad Dry-run mit `--json`
- Mission Control Health, sobald paralleler Build fertig ist
- Discord Report nach `1495737862522405088`

