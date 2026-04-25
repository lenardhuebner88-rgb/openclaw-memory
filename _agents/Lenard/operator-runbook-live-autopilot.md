# Operator Runbook — Erster Live-Autopilot-Lauf

> **Für:** Lenard (Operator)  
> **Status:** Gate D = GO  
> **Erstellt:** 2026-04-25  
> **Version:** 1.0

---

## Wann starten

**Startkriterium — alle müssen erfüllt sein:**
- [ ] Health-Check zeigt `ok` (kein `degraded`)
- [ ] Board hat ≤ 5 offene Tasks
- [ ] `costs: ok` (criticalAnomalies = 0)
- [ ] Keine aktiven Incidents in Discord `#alerts`

**Wer startet:** Atlas oder Operator per Discord  
**Was startet:** `meeting-runner.sh` im Controlled-Fanout-Modus

---

## Während des Laufs — Beobachtungspunkte

**Jede 5 min prüfen:**

| Check | Grenzwert | Was tun |
|---|---|---|
| Health Status | muss `ok` bleiben | `curl /api/health` → status |
| Board Open Tasks | ≤ 10 | `curl /api/health` → board.openCount |
| Failed Tasks neu | 0 ohne klare Ursache | `#execution-reports` beobachten |
| Kosten-Anomalien | ≤ 2, nicht `critical` | `curl /api/costs/anomalies` |
| Agent-Concurrency | kein Agent über Limit | `curl /api/agents/concurrency` |

---

## Abbruchkriterien — SOFORT STOPPEN

**Wenn irgendeines davon eintritt:**

1. Health wird `degraded` — besonders `execution` oder `costs`
2. Board zeigt > 10 offene Tasks
3. Mehr als 2 Failed Tasks in 10 min ohne klare Ursache
4. Kosten-Anomalie mit `severity: critical`
5. Meeting hängt in `running` > 30 min ohne Fortschritt
6. Lenard sagt "Stopp"

**Stop-Kommando:** Discord `#atlas-main` → "STOP" oder Signal an Atlas

---

## Nach dem Lauf — Ergebnisbericht

```
Lauf-Datum:  YYYY-MM-DD
Dauer:        X min
Health:       ok / degraded
Neue Tasks:   N
Failed:       N (ohne klare Ursache)
Kosten:       N Anomalien
Entscheidung: Weiter / Stopp / Anpassung nötig
```

**Wohin:** Discord `#atlas-main` + Board-Task kommentieren

---

## Quick-Check Commands

```bash
# Health
curl -s http://127.0.0.1:3000/api/health | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['status'])"

# Board
curl -s http://127.0.0.1:3000/api/health | python3 -c "import json,sys; d=json.load(sys.stdin); print('open:', d['checks']['board']['openCount'])"

# Costs
curl -s http://127.0.0.1:3000/api/costs/anomalies | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['count'], 'anomalies')"
```

---

## Backup / Rollback

**Wenn etwas schiefgeht:**
- Meeting-Dateien auf `status: aborted` setzen
- Offene Tasks NICHT manuell schließen — Worker-System räumt auf
- NICHT: Config ändern, Cron deaktivieren, Gateway restarten

**Support:** Atlas oder `#sre-expert`

---

*Erstellt von Lens (efficiency-auditor) für Lenard, 2026-04-25*
