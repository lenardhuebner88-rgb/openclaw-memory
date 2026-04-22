# Atlas Session Handover

## Stand: 2026-04-21 09:37 UTC — Sprint-M / Plan v1.2

### Zuerst lesen

- [sprint-m-v1.2-session-handover-2026-04-21.md](/home/piet/vault/03-Agents/sprint-m-v1.2-session-handover-2026-04-21.md)
- [sprint-m-followup-status-2026-04-21.md](/home/piet/vault/03-Agents/sprint-m-followup-status-2026-04-21.md)

### Aktueller Wahrheitsstand

- Sprint-M bleibt `READY-WITH-KNOWN-GAPS`.
- `mc-critical-alert` ist live verifiziert und **A**, nicht mehr `B`.
- `memory-orchestrator.py` hatte einen Doppel-Lock-Bug; Minimalfix ist lokal gesetzt, wrapped dry-runs sind grün.
- Der aktuelle operative Engpass ist **nicht** mehr Sprint-M allgemein, sondern ein einzelner Scheduler-Vertragsbruch:
  - live crontab enthält `15,45 * * * * /home/piet/.openclaw/scripts/qmd-native-embed-cron.sh`
  - live reconciler meldet dafür `missing_in_registry`
- Parallel läuft ein 2h-Soak/Proof durch Claude bot für `qmd-native-embed`.

### Verbindliche Regel für den Neustart

Bis der laufende `qmd-native-embed`-Soak fertig ist:

- keine Writes an
  - user crontab
  - `registry.jsonl`
  - `qmd-native-embed-cron.sh`
  - `qmd-pending-monitor.sh`

Danach ist die nächste Pflicht-Reihenfolge:

1. `qmd-native-embed` gegen `registry.jsonl` normalisieren
2. `registry-validate.py` + `cron-reconciler.py --dry-run` erneut prüfen
3. einen realen `memory-orchestrator hourly` live-fire verifizieren

---

## Stand: 2026-04-18 06:00 UTC — Nach Overnight Session

---

## 0. Aktueller System-Status — LESEN ZUERST

**Board: LEER** — 0 nicht-terminale Tasks
- done=51, canceled=35, failed=1 (alter orphan, terminal)
- Keine offenen operativen Tasks

**System operativ:**
- Mission Control ✅ Port 3000
- Gateway ✅ Port 18789
- Build: npm run build ✅
- Alle Agenten konsistent (Naming Audit ✅)

---

## 1. Was gestern (2026-04-17) lief

### Woche-2 Intervention
- SOUL.md verschärft: kein Work ohne Session-Typ-Deklaration
- MEMORY-Truncation Fix (bootstrapMaxChars erhöht)
- AC-06/07/08 Messlücken geschlossen
- Review-Gate verschoben auf Do 22. April

### Mission Control Cockpit (Pixel + Forge)
- Zone A: Heartbeat-Strip mit 4 Lichter (/api/health)
- Zone B: NBA-Banner (/api/board/next-action)
- Zone C: Live-Flow Lanes + Age-Badge (boardLane)
- Zone D: Agent-Load Sidebar (/api/board/agent-load)
- SSE: /api/board/events

### Costs-v2 (Lens + Forge)
- Phase 1 Baseline: $77.94/minimax 275% Overrun
- Budget-Engine, Burn-Rate, Discord-Alerts live
- Costs Heartbeat Strip UI

### pending-pickup Lifecycle
- Smoke Script + Cron aktiv
- Docs: taskboard-pending-pickup.md

### Handoff + Session Guards
- Handoff-Block Pflichtfeld in MC POST /api/tasks
- Max-Session-Length Guard (70% Hint)

---

## 2. Entscheidungen (binding)

- **pending-pickup**: Section 5 HEARTBEAT.md bleibt DEAKTIVIERT. Section 2C Receipt-Timeout (>10min) fängt Stuck-Tasks ab. Synthetischer Attach in auto-dispatch ist DEAKTIVIERT (Sicherheitsgrund).
- **Naming**: 6 Agenten alle konsistent. Nur Spark hatte Chaos (spark-relief → spark), rest sauber.
- **Review-Gate verschoben**: Do 22. April

---

## 3. Offene Punkte (2026-04-18)

| Prio | Was | Status |
|---|---|---|
| P1 | OS Timezone → Europe/Berlin | Lenard selbst |
| P2 | Flash aktivieren? | Offen — Entscheidung |
| P2 | Woche-2 Review Gate Do 22. April | AC-01/09/10 Trends |

---

## 4. Systemregel (unverändert)

**Atlas delegiert immer — handelt nie selbst technisch.**

| Aufgabe | Agent |
|---------|-------|
| Code, Infra, Build, Deploy | Forge (sre-expert) |
| Root-Cause, Architektur-Risiko | Forge-Opus |
| Recherche, externe Vergleiche | James |
| UI, Frontend, Dashboard | Pixel (frontend-guru) |
| Kosten, Audit, Konsolidierung | Lens (efficiency-auditor) |
| Leichte Forge-Entlastung | Spark |
| Leichte Forge-Entlastung | Flash (noch nicht aktiv) |

---

## 5. Operative Leitplanken (unverändert gültig)

- `groupPolicy = allowlist` für Discord + Telegram
- `exec.security = allowlist` für main, sre-expert, sre-expert-fresh
- Mission Control: `npm run build` — kein direkter next build
- Forge nicht blind als Wahrheitsquelle für Gesamtzustand verwenden
- Keine parallelen Großbaustellen
