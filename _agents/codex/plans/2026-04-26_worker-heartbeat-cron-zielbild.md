# Worker / Heartbeat / Cron Zielbild

EXECUTION_STATUS: partial

RESULT_SUMMARY:
- Atlas orchestriert, Forge ist der Ziel-Worker fuer Infra-/Monitor-Hardening, Lens fuer Audit/Analyse, Pixel fuer UI, Spark fuer Kurzanalysen, James fuer Recherche.
- Live-Probe zeigt: `/api/health=ok`, `/api/ops/pickup-proof` ist sauber (`pendingPickup=0`, `criticalFindings=0`), aber Heartbeat ist nicht flach gruen: nur `main` ist online, 5 von 6 Core-Agents sind im Store down.
- Systemd- und Cron-Landschaft ist breit, aber funktional klar: m7-Kern-Timer, Monitoring-, Hygiene-, Memory- und Guard-Crons laufen parallel; das Zielbild muss Redundanz sichtbar machen, nicht blind weiter fanouten.

GATES:
- Probe `systemctl --user list-timers --all --no-legend` ausgefuehrt.
- Probe `crontab -l` ausgefuehrt.
- Probe `src/lib/heartbeat-data.ts`, `src/lib/pickup-proof.ts`, `src/app/api/worker-pickups/route.ts`, `src/app/api/heartbeat/status/route.ts` gelesen.
- Live-JSON geprueft:
  - `/api/health`: ok / severity ok
  - `/api/ops/pickup-proof`: pendingPickup=0, openPlaceholderRuns=0, criticalFindings=0, proposedActions=0
  - `/api/heartbeat/status`: total=6, online=1, down=5
- Zwei Draft-Follow-ups im Board erstellt und als Draft verifiziert:
  - `e46b58a1-b6a5-42cf-80f0-c88c43120be2` — `approvalClass=safe-read-only`, `riskLevel=low`
  - `7c995854-8c81-47de-947e-a570ceefd212` — `approvalClass=gated-mutation`, `riskLevel=medium`

FOLLOW_UPS:
- `e46b58a1-b6a5-42cf-80f0-c88c43120be2` — Cron/Timer Zielbild rationalisieren — approvalClass=safe-read-only — riskLevel=low
- `7c995854-8c81-47de-947e-a570ceefd212` — Worker/Heartbeat Gates hardenen — approvalClass=gated-mutation — riskLevel=medium

OPERATOR_DECISIONS:
- Darf Atlas die Cron-Landschaft weiter konsolidieren oder bleiben m7- und Legacy-Crons vorerst parallel?
- Soll ein eigener first-heartbeat-Gate in den Worker-Monitor eingebaut werden?
- Welche reduntanten Heartbeat-/Guard-Pfade duerfen spaeter entfernt werden, ohne Autonomie zu brechen?

## Probe-Ergebnis / Gap-Analyse

### Aktiv und notwendig
- Systemd-Timer: `m7-auto-pickup`, `m7-plan-runner`, `openclaw-healthcheck`, `m7-mc-watchdog`, `m7-session-freeze-watcher`, `m7-stale-lock-cleaner`, `m7-worker-monitor`, `system-handbook-refresh`, `vault-sync`, `forge-heartbeat`, `researcher-run`, `launchpadlib-cache-clean`.
- Cron-Kern: `mc-ops-monitor`, `memory-size-guard`, `session-size-alert`, `script-integrity-check`, `openclaw sessions cleanup`, `rules-render`, `qmd update`, `qmd-pending-monitor`, `pr68846-patch-check`, `minions-pr-watch`, `cleanup`, `config-snapshot-to-vault`, `build-artifact-cleanup`, `cron-health-audit`, `canary-alert`, `session-janitor`, `cpu-runaway-guard`, `agents-md-size-check`, `session-size-guard`, `session-size-guard --log-only`, `qmd-native-embed-cron`, `mcp-qmd-reaper`, `vault-search-daily-checkpoint`, `mcp-taskboard-reaper`, `session-rotation-watchdog`, `per-tool-byte-meter`.

### Fehlend / zu schwach
- Heartbeat-Store ist nur fuer `main` frisch; die anderen Core-Agents sind im Store alt und damit down.
- Es gibt noch kein explizites first-heartbeat-Gate in den read-only Worker-Proof-Pfaden.
- Pickup-Proof erkennt claim-timeout, placeholder-run, active session locks und unclaimed pending-pickup, aber kein separates Zielbild fuer "claimed, no heartbeat yet" als eigene operative Stufe im Berichtspfad.

### Redundant / doppelt
- Heartbeat-Visualisierung existiert in zwei Pfaden (`HeartbeatMonitor` und `HeartbeatPanel`) mit unterschiedlichen Datenquellen und Zeitschwellen.
- Cron-Hygiene und Guarding laufen verteilt ueber mehrere Scheduler-Ebenen; das ist robust, aber schwerer auditierbar als ein konsolidierter M7-Cluster.

## Zielbild in einem Satz
- Atlas orchestriert; Forge haertet Infra/Worker-Gates; Lens bewertet Kosten/Qualitaet; Pixel reduziert UI-Reibung; Spark/James liefern kurze Spezialarbeit — und der Monitor muss diese Rollen, Heartbeats und Cron-Gates sauber trennen statt sie nur parallel zu pollen.
