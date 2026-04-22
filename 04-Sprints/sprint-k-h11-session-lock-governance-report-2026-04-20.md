# Sprint-K H11 Report — Session-Lock-Governance (2026-04-20)

## Kontext
- Incident-Fenster: 2026-04-19 (ca. 4h)
- Symptom: 85 fallback-failures auf eine gelockte Forge-Session (`9b87be6e...jsonl.lock`)
- Wirkung: Auto-Pickup versuchte weiter Trigger/Fallbacks auf denselben Session-Lock statt sauber zu skippen oder mit frischer Session zu starten.

## Root Cause
1. Lock-Konflikte wurden vor Worker-Trigger nicht auf Agent-Session-Ebene geprüft.
2. Bei Lock-Konflikt gab es keinen erzwungenen Session-Rotate-Pfad für neue Worker-Spawns.
3. Kein dedizierter Session-Health-Scan für wiederkehrende Lock-/Ghost-/Oversize-Muster.

## Umgesetzte Lösung (3 Layer)

### Layer 1: Auto-Pickup Lock-Awareness (`/home/piet/.openclaw/scripts/auto-pickup.py`)
- Neu: Session-Lock-Precheck vor Trigger.
- Entscheidungen:
  - `skip-alive-lock` bei alive lock <120s.
  - `spawn-new-for-orphan` bei stale lock >=120s oder dead pid (erzwingt `--session-id`).
  - `proceed-normal` ohne Lock-Konflikt.
- Audit-Logging in `logs/auto-pickup.log` mit Decision-Tags.

### Layer 2: Session Health Monitor (`/home/piet/.openclaw/scripts/session-health-monitor.py`)
- Neu: Scan alle `~/.openclaw/agents/*/sessions` auf:
  - orphan locks,
  - zombie sessions,
  - ghost sessions (<1KB, >30min),
  - size-exploded sessions (>2MB).
- Output: `workspace/memory/session-health.log` (JSONL).
- Alerts nur bei neuen Pattern-Keys (dedupe-state in `/tmp/session-health-monitor-state.json`).
- Cron: `*/10 * * * * flock -n /tmp/session-health-monitor.lock ...`

### Layer 3: Governance R50
- `memory/rules.jsonl`: neue Regel **R50 Session-Lock-Governance**.
- `AGENTS.md`: R50-Abschnitt mit Pflichtflow für Lock-Handling.
- `feedback_system_rules.md` regeneriert via `scripts/rules-render.sh`.

## Test-Evidence

### Simulierter Lock-Test
Command:
```bash
python3 - <<'PY'
# evaluate_session_strategy against alive lock / orphan lock / no lock
PY
```
Output:
- `alive= ('skip-alive-lock', None)`
- `orphan= ('spawn-new-for-orphan', 'test-lock-<uuid>')`
- `none= ('proceed-normal', None)`

### Log-Evidence
`tail -n 12 logs/auto-pickup.log` enthält:
- `decision=skip-alive-lock`
- `decision=spawn-new-for-orphan`
- `decision=proceed-normal`

### Stale-Lock-Cleaner weiterhin aktiv
- Script vorhanden/executable: `/home/piet/.openclaw/scripts/stale-lock-cleaner.sh`
- Cron aktiv: `*/5 * * * * /home/piet/.openclaw/scripts/stale-lock-cleaner.sh ...`

## Integrationshinweis zu R38/R39/R40/R45
- R38: ergänzt um Session-Lock-Ebene (nicht nur MCP-Zombies).
- R39: fresh-session-path reduziert Resume-Konflikte auf gelockten Sessions.
- R40: frühere Erkennung verhindert Stall-Kaskaden.
- R45: Auto-Pickup kann nun lock-aware starten, sodass Receipt-Pflicht nicht an Lock-Retries stirbt.

## Offene Beobachtung nach Deployment
- `session-health-monitor` erster Lauf meldet bestehende historische anomalies (u.a. size-exploded Spark-Checkpoint-Dateien).
- Diese sind Monitoring-Funde, kein neuer Regression-Indikator des H11-Fixes.
