# Sprint-M Nachtbericht — 2026-04-21 00:22 CEST

## Stand heute
- Wave 1: fertig
- Wave 2: fertig und grün
- Wave 3: technisch fertig
  - M6 fertig
  - M7 fertig
- Wave 4, Wave 5 und Soak: bewusst auf morgen verschoben

## Live-Status jetzt
### Operativ
- OpenClaw Gateway läuft
- Discord läuft
- M7-Timer sind aktiv und eingeplant
- Cutover auf systemd-user-timer für die 5 Kernel-Jobs ist live

### Verifiziert
- `systemctl --user list-timers 'm7-*'` zeigt 5 aktive Timer
- `m7-auto-pickup.timer` aktiv
- `m7-mc-watchdog.timer` aktiv
- `m7-worker-monitor.timer` aktiv
- `m7-session-freeze-watcher.timer` aktiv
- `m7-stale-lock-cleaner.timer` aktiv
- Rollback-Artefakte vorhanden:
  - `/home/piet/.openclaw/scripts/m7-systemd-migration-rollback.sh`
  - `/home/piet/.openclaw/cron/m7-rollback-pointer.txt`
  - `/home/piet/.openclaw/cron/crontab.bak-m7-20260421-000301`
  - `/home/piet/.openclaw/cron/registry.jsonl.bak-m7-20260421-000301`

## Wichtiger Befund
System wirkt **operativ stabil**, aber nicht komplett "grün-grün":
- `cron-reconciler.py --dry-run` war nach Wave 2 grün
- nach M7 ist aktuell ein **Registry-Schema-Thema** sichtbar:
  - `registry-validate.py` schlägt fehl, weil die M7-Updates das Feld `scheduler` in `registry.jsonl` gesetzt haben
  - `registry.schema.json` erlaubt dieses Feld aktuell nicht (`additionalProperties: false`)

### Bedeutung
- Das ist **kein akuter Runtime-Ausfall**
- Die neuen systemd-Timer laufen trotzdem
- Es ist aber ein echter Follow-up für morgen, bevor weiter Richtung M8 / sauberer Schluss gegangen wird

## Empfehlung für die Nacht
- Kein weiterer Umbau
- Nur beobachten, ob M7-Timer weiter sauber feuern
- Morgen zuerst Schema/Registry nachziehen oder M7-Post-Cutover-Status sauber verifizieren, dann Wave 4

## Morgen als nächster sauberer Ablauf
1. M7 Nachkontrolle + Registry/Schema sauber grün ziehen
2. Wave 4 / M6b
3. Wave 5 / M8
4. Soak starten

## Kurzfazit
- **Ja, operativ stabil genug zum Schlafen**
- **Nein, nicht vollständig fertig/grün** wegen Registry-Schema-Nacharbeit nach M7
