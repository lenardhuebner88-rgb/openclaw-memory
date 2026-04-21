# Sprint N — E2E Stabilization (2026-04-22)

Status: PLAN ONLY
Gate: KEIN Execute, KEIN Dispatch bis Forge-Review grün
Owner: Atlas
Review-Gate: Forge

## Live-Evidenz

```text
=== M1 systemctl status ===
● mission-control.service - Mission Control (Next.js Production)
     Loaded: loaded (/home/piet/.config/systemd/user/mission-control.service; enabled; preset: enabled)
    Drop-In: /home/piet/.config/systemd/user/mission-control.service.d
             └─agent-load-flag.conf
     Active: active (running) since Tue 2026-04-21 20:29:39 CEST; 9min ago
    Process: 3531868 ExecStartPre=/bin/sh -lc test -f /home/piet/.openclaw/workspace/mission-control/.next/BUILD_ID || (cd /home/piet/.openclaw/workspace/mission-control && PATH="/home/piet/.openclaw/workspace/mission-control/node_modules/.bin:$PATH" SKIP_PREFLIGHT=1 npm run build) (code=exited, status=0/SUCCESS)
    Process: 3531878 ExecStartPre=/home/piet/.openclaw/scripts/mission-control-port-guard.sh 3000 (code=exited, status=0/SUCCESS)
    Process: 3531890 ExecStartPre=/bin/sleep 2 (code=exited, status=0/SUCCESS)
   Main PID: 3532031 (next-server (v1)
```

```text
=== M2 grep claude --print ===
/home/piet/.openclaw/scripts/claude-telegram-bridge.py:109:    Run claude --print with the specified model + environment.

=== M2 journal errors ===
2026-04-21T20:09:29+02:00 huebners systemd[1423]: m7-auto-pickup.service: Found left-over process 3502095 (openclaw-agent) in control group while starting unit. Ignoring.
2026-04-21T20:09:29+02:00 huebners systemd[1423]: m7-auto-pickup.service: This usually indicates unclean termination of a previous run, or service implementation deficiencies.
2026-04-21T20:09:29+02:00 huebners systemd[1423]: Starting m7-auto-pickup.service - M7 auto-pickup runner...
2026-04-21T20:09:29+02:00 huebners systemd[1423]: m7-auto-pickup.service: Unit process 3501088 (openclaw) remains running after unit stopped.
2026-04-21T20:09:29+02:00 huebners systemd[1423]: m7-auto-pickup.service: Unit process 3501095 (openclaw-agent) remains running after unit stopped.
2026-04-21T20:09:29+02:00 huebners systemd[1423]: Finished m7-auto-pickup.service - M7 auto-pickup runner.
2026-04-21T20:09:32+02:00 huebners systemd[1423]: m7-session-freeze-watcher.service: Scheduled restart job, restart counter is at 2.
2026-04-21T20:09:32+02:00 huebners systemd[1423]: Starting m7-session-freeze-watcher.service - M7 session-freeze-watcher runner...
2026-04-21T20:09:32+02:00 huebners session-freeze-watcher.sh[3505499]: [2026-04-21T18:09:32Z] checked 2 active tasks, frozen=0
2026-04-21T20:09:32+02:00 huebners systemd[1423]: Finished m7-session-freeze-watcher.service - M7 session-freeze-watcher runner.
```

```text
=== M3 search session retry ===
/home/piet/.openclaw/workspace/memory/2026-04-21-live-recovery.md:156:  - wiederholt `could not fail pending-pickup ... HTTP 409 Conflict` bis zum späten accepted receipt
/home/piet/.openclaw/workspace/HEARTBEAT.md:79:- Bei 409 Conflict: Board neu laden, Zustand prüfen, ggf. Update überspringen
/home/piet/.openclaw/workspace/mission-control/backups/sprint-g-g1-2026-04-19/20260419-200655-step1-systemd/scripts-before/auto-pickup.py.bak-2026-04-19-r37:124:        log("ALERT_SENT", f"kind={kind} transport={transport}")
```

## Milestones

### M1 — ExecReload entschärfen
- **Live-Beleg**
  - `2026-04-21 20:29:39 CEST | Process: 3531868 ExecStartPre=/bin/sh -lc test -f /home/piet/.openclaw/workspace/mission-control/.next/BUILD_ID || (cd /home/piet/.openclaw/workspace/mission-control && PATH="/home/piet/.openclaw/workspace/mission-control/node_modules/.bin:$PATH" SKIP_PREFLIGHT=1 npm run build) (code=exited, status=0/SUCCESS)`
- **Betroffene Datei(en)**
  - `/home/piet/.openclaw/scripts/mission-control-reload.sh`
  - `/home/piet/.config/systemd/user/mission-control.service`
  - optional falls separiert: `/home/piet/.config/systemd/user/mission-control-build.service`
- **Konkrete Aktion**
  - Entferne `npm run build` vollständig aus dem Reload-Pfad von `mission-control-reload.sh`. Verschiebe den Build in `ExecStartPre` oder in eine dedizierte `mission-control-build.service`, die vor dem Start explizit abgeschlossen sein muss.
- **Acceptance-Kriterium**
  - `systemctl --user reload mission-control.service` kehrt in unter 2 Sekunden zurück.
  - `curl -fsS http://127.0.0.1:3000/api/health` liefert während des Reload-Fensters erfolgreich eine Antwort.
  - `systemctl --user status mission-control.service` zeigt keinen `reloading`-State länger als 5 Sekunden.
- **Rollback-Befehl falls der Fix kippt**
  - `cp /home/piet/.config/systemd/user/mission-control.service.bak-pre-sprint-n /home/piet/.config/systemd/user/mission-control.service && cp /home/piet/.openclaw/scripts/mission-control-reload.sh.bak-pre-sprint-n /home/piet/.openclaw/scripts/mission-control-reload.sh && systemctl --user daemon-reload && mc-restart-safe 120 "rollback-sprint-n-m1"`

### M2 — claude --print stdin-Regression
- **Live-Beleg**
  - `2026-04-21T20:09:29+02:00 huebners systemd[1423]: m7-auto-pickup.service: Found left-over process 3502095 (openclaw-agent) in control group while starting unit. Ignoring.`
  - `2026-04-21T20:09:32+02:00 huebners systemd[1423]: m7-session-freeze-watcher.service: Scheduled restart job, restart counter is at 2.`
  - `/home/piet/.openclaw/scripts/claude-telegram-bridge.py:109:    Run claude --print with the specified model + environment.`
- **Betroffene Datei(en)**
  - `/home/piet/.openclaw/scripts/`
  - `/home/piet/.config/systemd/user/m7-auto-pickup.service`
  - `/home/piet/.config/systemd/user/m7-session-freeze-watcher.service`
  - konkrete Wrapper-Datei erst nach `grep -rn 'claude --print' /home/piet/.openclaw/scripts/ /home/piet/.config/systemd/user/` als Schreibziel festziehen
- **Konkrete Aktion**
  - Ermittele die echte Service-Callsite per grep und ersetze jeden nicht-interaktiven `claude --print`-Aufruf ohne Input durch einen expliziten `--prompt`-Parameter oder ein Heredoc. Säubere zusätzlich den Service-Wrapper so, dass ein Lauf ohne Prompt hart abbricht, statt mit Restart-Schleife weiterzulaufen.
- **Acceptance-Kriterium**
  - 30 Minuten nach Fix enthält `journalctl --user -p err --since "30 min ago"` keinen Eintrag mit `Input must be provided`.
  - `systemctl --user --failed --no-pager` liefert eine leere Failed-Units-Liste.
  - `systemctl --user status m7-auto-pickup.service m7-session-freeze-watcher.service --no-pager` zeigt keine steigenden Restart-Counter.
- **Rollback-Befehl falls der Fix kippt**
  - `cp /home/piet/.config/systemd/user/m7-auto-pickup.service.bak-pre-sprint-n /home/piet/.config/systemd/user/m7-auto-pickup.service && cp /home/piet/.config/systemd/user/m7-session-freeze-watcher.service.bak-pre-sprint-n /home/piet/.config/systemd/user/m7-session-freeze-watcher.service && systemctl --user daemon-reload && systemctl --user restart m7-auto-pickup.service m7-session-freeze-watcher.service`

### M3 — SESSION_RETRY Cap
- **Live-Beleg**
  - `/home/piet/.openclaw/workspace/memory/2026-04-21-live-recovery.md:156:  - wiederholt could not fail pending-pickup ... HTTP 409 Conflict bis zum späten accepted receipt`
  - `/home/piet/.openclaw/workspace/HEARTBEAT.md:79:- Bei 409 Conflict: Board neu laden, Zustand prüfen, ggf. Update überspringen`
  - `/home/piet/.openclaw/workspace/mission-control/backups/sprint-g-g1-2026-04-19/20260419-200655-step1-systemd/scripts-before/auto-pickup.py.bak-2026-04-19-r37:124:        log("ALERT_SENT", f"kind={kind} transport={transport}")`
- **Betroffene Datei(en)**
  - `/home/piet/.openclaw/scripts/auto-pickup.py`
  - `/home/piet/.openclaw/workspace/logs/auto-pickup.log`
  - optional Alert-Pfad falls separat: `/home/piet/.openclaw/scripts/cost-alert-dispatcher.py`
- **Konkrete Aktion**
  - Ergänze in `auto-pickup.py` eine rollende 10-Minuten-Heuristik pro Task-ID mit hartem Cap von 3 Retries. Der 4. Versuch setzt den Task auf `blocked`, schreibt `ALERT_SENT` in den Logpfad und unterdrückt jeden weiteren Spawn.
- **Acceptance-Kriterium**
  - **Execute-Acceptance:** Code-Cap ist implementiert, per Unit-Test abgedeckt, und der nächste reale 409-Fall erzeugt `blocked` plus `ALERT_SENT` ohne neue Session.
  - **Observation-Followup (separate Task, +2h):** Das Tagesbudget stagniert im Beobachtungsfenster und es gibt keinen Task mit mehr als 3 Retries innerhalb von 10 Minuten.
- **Rollback-Befehl falls der Fix kippt**
  - `cp /home/piet/.openclaw/scripts/auto-pickup.py.bak-pre-sprint-n /home/piet/.openclaw/scripts/auto-pickup.py && systemctl --user restart m7-auto-pickup.service`

## Exit-Gate
- M1 Acceptance erfüllt
- M2 Acceptance erfüllt
- M3 Acceptance erfüllt
- alle drei Acceptance-Kriterien gleichzeitig mindestens 1 Stunde stabil
- bis dahin bleibt Sprint N im Status PLAN/REVIEW, ohne Execute und ohne Dispatch

## Rollback-Matrix
- **M1**
  - Restore der gebackupten `mission-control.service` und `mission-control-reload.sh`
  - `systemctl --user daemon-reload`
  - `mc-restart-safe 120 "rollback-sprint-n-m1"`
- **M2**
  - Restore der gebackupten systemd-Units und des geänderten Wrappers
  - `systemctl --user daemon-reload`
  - `systemctl --user restart m7-auto-pickup.service m7-session-freeze-watcher.service`
- **M3**
  - Restore von `auto-pickup.py`
  - `systemctl --user restart m7-auto-pickup.service`
  - Prüfen, dass keine Block-States fälschlich stehen bleiben

## Out-of-Scope
- **Gateway / 1006**
  - Gehört nicht zum aktuellen E2E-Stabilisierungspfad und würde den Fix-Radius unnötig vergrößern.
- **0-Byte-Buffering / Kosmetik**
  - Kein blocker für Reload, Worker-Start oder Retry-Kosten.
- **Gateway-Memory**
  - Separater Ressourcen-/Architekturpfad, nicht Teil der drei akuten Ausfallmuster.
- **neue R-Regeln**
  - Policy-Erweiterung verändert Governance, löst aber nicht die drei konkreten Live-Störungen.