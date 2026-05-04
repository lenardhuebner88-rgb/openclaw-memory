# Validate Models SystemJob Migration

Zeitpunkt: 2026-05-04T23:17:42+02:00

## Ziel

`validate-models` soll nicht mehr selbst als OpenClaw-LLM-Cron laufen. Der Guard prüft jetzt Modelle und Cron-Payloads; deshalb darf er nicht wieder durch genau den Modell-/Allowlist-Pfad blockiert werden, den er überwachen soll.

## Entscheidung

`validate-models` wurde aus dem enabled OpenClaw `agentTurn` Cronpfad herausgenommen und als deterministischer `systemJob` über systemd User Timer betrieben.

## Backups

- `/home/piet/.openclaw/cron/jobs.json.bak-20260504T231617-validate-models-systemjob`
- `/home/piet/.openclaw/cron/jobs-state.json.bak-20260504T231617-validate-models-systemjob`

## Geändert

Neue Datei:

- `/home/piet/.openclaw/scripts/validate-models-systemjob.sh`

Neue systemd Timer-Datei:

- `/home/piet/.config/systemd/user/openclaw-systemjob-validate-models.timer`

Geändert:

- `/home/piet/.openclaw/cron/jobs.json`

## Neue Laufweise

Timer:

```ini
OnCalendar=*-*-* 07:50:00
AccuracySec=1min
Persistent=false
Unit=openclaw-systemjob@881bd75e-191e-4f1e-b605-b9f8ec95795a.service
```

Cron-Metadaten:

- Job: `validate-models`
- ID: `881bd75e-191e-4f1e-b605-b9f8ec95795a`
- `enabled=false`
- `disabledReason=migrated-to-systemd-systemjob-2026-05-04: deterministic config/cron guard; avoids LLM/agentTurn self-blocking.`
- `systemJob.enabled=true`
- Command: `/home/piet/.openclaw/scripts/validate-models-systemjob.sh`
- Timeout: `120s`
- Erfolgssignal: `VALIDATE_MODELS_OK`

## Validierung

Ausgeführt:

```bash
bash -n /home/piet/.openclaw/scripts/validate-models-systemjob.sh
/home/piet/.openclaw/scripts/validate-models-systemjob.sh
python3 -m json.tool /home/piet/.openclaw/cron/jobs.json
python3 -m json.tool /home/piet/.openclaw/cron/jobs-state.json
systemctl --user enable --now openclaw-systemjob-validate-models.timer
python3 /home/piet/.openclaw/scripts/openclaw-systemjob-runner.py 881bd75e-191e-4f1e-b605-b9f8ec95795a
/home/piet/.openclaw/scripts/openclaw-morning-launchpad.py --json
curl -fsS http://127.0.0.1:3000/api/health
curl -fsS http://127.0.0.1:3000/api/board-consistency
```

Ergebnis:

- Wrapper syntax: OK
- Wrapper manuell: `VALIDATE_MODELS_OK`
- systemd Timer: enabled + active
- nächster Timer-Lauf: `2026-05-05 07:50 CEST`
- systemJob Runner: exit `0`
- Runlog:
  - `status=ok`
  - `provider=system`
  - `model=shell`
  - `usage.total_tokens=0`
  - `durationMs=61`
- Launchpad:
  - Cron: `GREEN`
  - `currentErrors=0`
  - `pendingVerification=0`
  - `missingAllowlistModels=0`
- Mission Control: `ok`
- Board Consistency: `ok`

## Wirkung

Der wichtigste Modell-/Cron-Guard läuft jetzt ohne Modell, ohne Tokens und ohne LLM-Fallbacks. Dadurch kann er sich nicht mehr selbst durch eine Modell-Allowlist-Fehlkonfiguration blockieren.

## Rollback

```bash
cp /home/piet/.openclaw/cron/jobs.json.bak-20260504T231617-validate-models-systemjob /home/piet/.openclaw/cron/jobs.json
cp /home/piet/.openclaw/cron/jobs-state.json.bak-20260504T231617-validate-models-systemjob /home/piet/.openclaw/cron/jobs-state.json
systemctl --user disable --now openclaw-systemjob-validate-models.timer
systemctl --user daemon-reload
python3 /home/piet/.openclaw/scripts/validate-models.py
```

## Nächster Morgen-Check

Morgen nach 07:50 CEST prüfen:

```bash
tail -5 /home/piet/.openclaw/cron/runs/881bd75e-191e-4f1e-b605-b9f8ec95795a.jsonl
systemctl --user list-timers openclaw-systemjob-validate-models.timer --all --no-pager
/home/piet/.openclaw/scripts/openclaw-morning-launchpad.py --json
```

