# Sprint-G G2 — Alert Deduplication (Lens)

**Datum:** 2026-04-19  
**Status:** ✅ Done  
**Agent:** Lens (efficiency-auditor)  
**Board-Task:** `b8b40aaf-9eb6-4149-b361-af1c5c348786`

---

## Problem

5 Alert-Quellen posteten **alle direkt** an `#alerts` bei Overlap → keine Deduplizierung → Alert-Fatigue.

| Quelle | Trigger | Vorher |
|--------|---------|--------|
| `mc-watchdog.sh` | MC health failure / heal | Direkter curl → Discord |
| `mc-critical-alert.py` | MC down >10min, Gateway down, Budget >150% | Direkter urllib → Discord |
| `session-freeze-watcher.sh` | Session idle >10min | Direkter curl → Discord |
| `heartbeat-death-check` (HEARTBEAT.md) | Heartbeat >5min keine Activity | Via worker-monitor.py |
| `lens-cost-check` (systemd) | OpenRouter Tageskosten >$3 | ⚠️ OBSOLETE — ersetzt durch `cost-alert-dispatcher.py` (cron */2) |

---

## Lösung: `alert-dispatcher.sh`

**Pfad:** `~/.openclaw/scripts/alert-dispatcher.sh`

### Cooldown-Logik
- Lock-Datei: `/tmp/alert-cooldown-<source>.lock`
- TTL: **5 Minuten** (300s)
- Wenn Lock existiert und < 5min alt → Alert suppressed (exit 0)
- Wenn Lock nicht existiert oder abgelaufen → Dispatch + Lock setzen

### Usage
```bash
alert-dispatcher.sh <source> <message> [mention]
echo "<msg>" | alert-dispatcher.sh <source> [mention]
```

### Exit Codes
- `0` — dispatched oder suppressed (kein Fehler)
- `1` — ungültige Verwendung
- `2` — Discord POST fehlgeschlagen

---

## Geänderte Files

| File | Änderung |
|------|----------|
| `~/.openclaw/scripts/alert-dispatcher.sh` | **NEU** — Zentraler Dispatcher |
| `~/.openclaw/scripts/mc-watchdog.sh` | `alert()` → `alert-dispatcher.sh mc-watchdog` |
| `~/.openclaw/scripts/mc-critical-alert.py` | `send_discord()` → subprocess → `alert-dispatcher.sh mc-critical` |
| `~/.openclaw/scripts/session-freeze-watcher.sh` | Direkter curl → `alert-dispatcher.sh freeze-watcher` |
| `~/.openclaw/workspace/HEARTBEAT.md` | heartbeat-death-check + lens-cost-check docs aktualisiert |
| `~/.openclaw/workspace/scripts/worker-monitor.py` | stall/pending-pickup alerts → `alert-dispatcher.sh worker-*` |

---

## Verification

### Cooldown-Test
```bash
# Call 1: dispatched, lock gesetzt
$ alert-dispatcher.sh test "msg1"
[DISPATCH] [test] Posting to Discord...
[SENT] [test] Alert dispatched

# Call 2 (innerhalb 5min): suppressed
$ alert-dispatcher.sh test "msg2"
[SUPPRESSED] [test] Alert suppressed (cooldown active)
```

### Alle 5 Quellen zeigen auf Dispatcher
```bash
$ grep -r "alert-dispatcher.sh" ~/.openclaw/scripts/ ~/.openclaw/workspace/scripts/
mc-watchdog.sh:        "$HOME/.openclaw/scripts/alert-dispatcher.sh" mc-watchdog ...
mc-critical-alert.py:  ['/home/piet/.openclaw/scripts/alert-dispatcher.sh', 'mc-critical', ...]
session-freeze-watcher.sh: /home/piet/.openclaw/scripts/alert-dispatcher.sh freeze-watcher ...
worker-monitor.py: subprocess.run(['/home/piet/.openclaw/scripts/alert-dispatcher.sh', 'worker-stall', ...])
worker-monitor.py: subprocess.run(['/home/piet/.openclaw/scripts/alert-dispatcher.sh', 'worker-pending-timeout', ...])
```

---

## Offene Punkte

- `lens-cost-check.service` (systemd) ist **obsolete** — `cost-alert-dispatcher.py` (cron */2) ist der aktuelle Cost-Monitor. Service disabled.
- `worker-monitor.py` hat noch weitere `discord_post()` calls für `#execution-reports` (channel 1486480074491559966) — diese sind **nicht** über den Dispatcher, da das separate Kanäle sind. Nur die `#alerts`-gebundenen Posts (via `ALERTS_DISCORD_CHANNEL_ID`) wurden auf Dispatcher umgestellt.

---

## Cooldown-Per-Source-Tabelle

| Source Key | Lock File | TTL |
|-----------|-----------|-----|
| `mc-watchdog` | `/tmp/alert-cooldown-mc-watchdog.lock` | 5min |
| `mc-critical` | `/tmp/alert-cooldown-mc-critical.lock` | 5min |
| `freeze-watcher` | `/tmp/alert-cooldown-freeze-watcher.lock` | 5min |
| `heartbeat-death` | `/tmp/alert-cooldown-heartbeat-death.lock` | 5min |
| `worker-stall` | `/tmp/alert-cooldown-worker-stall.lock` | 5min |
| `worker-pending-timeout` | `/tmp/alert-cooldown-worker-pending-timeout.lock` | 5min |
