# OpenClaw Task Lifecycle

- 2026-04-26T22:01:35.164Z | FAILED | adfc0596-096a-4e0b-905d-ad232f79524b | [Forge][Image Generation] Expose/verify image_generate via Codex OAuth | worker=sre-expert | progress=- | summary=- | note=No progress for 24m (hard-threshold=20m). Auto-failed by worker-monitor.
- 2026-04-26T22:08:26.992Z | START | 2fe45813-247e-4a5d-87e3-d5e80d81506c | [Forge][Finalize] Verify Atlas image tool exposure | worker=sre-expert | progress=- | summary=-
- 2026-04-26T22:09:08.940Z | CHECKPOINT | 2fe45813-247e-4a5d-87e3-d5e80d81506c | [Forge][Finalize] Verify Atlas image tool exposure | worker=sre-expert | progress=- | summary=- | note=Verifikation fast abgeschlossen: Config enthält für Atlas korrekt `image` (und kein `image_generate`), Hot-Reload-Eintrag ist im Gateway-Log vorhanden, und Atlas-Session meldet `IMAGE_VISIBLE=yes`. Ich schreibe jetzt das terminale Ergebnis.
- 2026-04-26T22:09:28.653Z | DONE | 2fe45813-247e-4a5d-87e3-d5e80d81506c | [Forge][Finalize] Verify Atlas image tool exposure | worker=sre-expert | progress=- | summary=Atlas-Image-Tool-Finalisierung ist verifiziert: die korrigierte `image`-Freigabe ist in der Config vorhanden, Hot-Reload wurde protokolliert, und ein frischer Atlas-Tool-Surface-Check bestätigt `image` sichtbar.
- 2026-04-26T22:16:22.117Z | START | 337c2717-9b9e-4e98-88bd-c477e91e9160 | [Atlas][Autonomy] 9.5 Gate Sprint - 8 Slices | worker=main | progress=- | summary=-
- 2026-04-26T22:18:05.569Z | CHECKPOINT | 337c2717-9b9e-4e98-88bd-c477e91e9160 | [Atlas][Autonomy] 9.5 Gate Sprint - 8 Slices | worker=main | progress=80% | summary=-
- 2026-04-26T22:19:13.105Z | DONE | 337c2717-9b9e-4e98-88bd-c477e91e9160 | [Atlas][Autonomy] 9.5 Gate Sprint - 8 Slices | worker=main | progress=80% | summary=Atlas 9.5 Gate Sprint completed: A1/A2/A3/A5/A6 were green, A4/A7/A8 were yellow due reporting metadata and non-main heartbeat policy gaps. Final score 9.1/10; Discord transport worked, final live proofs are ok, and only two preview follow-up drafts were created with dispatchTarget set—no unsafe mutation or child dispatch occurred.
- 2026-04-26T22:23:41.406Z | START | 361355af-bd7b-4db2-a81b-c2665c6e444d | [Preview][Lens] Autonomy 9.5 Heartbeat Coverage policy follow-up | worker=efficiency-auditor | progress=- | summary=-
- 2026-04-26T22:24:23.785Z | START | 7e4a1073-94a6-40dc-85ec-616375971074 | [Preview][Forge] Autonomy 9.5 Reporting Metadata Gate follow-up | worker=sre-expert | progress=- | summary=-
- 2026-04-26T22:24:49.225Z | DONE | 361355af-bd7b-4db2-a81b-c2665c6e444d | [Preview][Lens] Autonomy 9.5 Heartbeat Coverage policy follow-up | worker=efficiency-auditor | progress=- | summary=Heartbeat-Coverage Policy: non-main Heartbeats dürfen 9.5/10 nicht hart blockieren, solange worker/pickup/health grün sind; sie bleiben aber gelber Residual-Risk. Empfehlung: 9.5 erlaubt mit dokumentiertem Waiver, 10/10 erst mit sauberer Non-Main-Coverage oder bewusster Scope-Reduktion.
- 2026-04-26T22:25:54.681Z | CHECKPOINT | 7e4a1073-94a6-40dc-85ec-616375971074 | [Preview][Forge] Autonomy 9.5 Reporting Metadata Gate follow-up | worker=sre-expert | progress=- | summary=- | note=Analyse abgeschlossen: Missing-Metadaten clustern in (a) historische Discord-401-Lifecycle-Report-Errors und (b) canceled-Tasks ohne terminalen Receipt-Pfad; ich schreibe jetzt die minimal reversible Empfehlung.
- 2026-04-26T22:26:53.963Z | DONE | 7e4a1073-94a6-40dc-85ec-616375971074 | [Preview][Forge] Autonomy 9.5 Reporting Metadata Gate follow-up | worker=sre-expert | progress=- | summary=A4-Metadaten-Lücke ist eingegrenzt: aktuelle Yellow-Signale kommen primär aus historischen Discord-401 Report-Errors (Status bereits gesetzt, finalReportSentAt fehlt) plus canceled-Datensätzen ohne terminalen Receipt-Pfad; kein Hinweis auf einen aktuellen Discord-Transportausfall.
- 2026-04-26T22:31:24.638Z | START | 7c2d2397-79d1-49cf-ad9d-e9dbd4a95659 | [Forge] Atlas Discord Tool Surface Baseline: dispatch + image | worker=sre-expert | progress=- | summary=-
- 2026-04-26T22:41:23.878Z | CHECKPOINT | 7c2d2397-79d1-49cf-ad9d-e9dbd4a95659 | [Forge] Atlas Discord Tool Surface Baseline: dispatch + image | worker=sre-expert | progress=- | summary=- | note=Zwischenstand: Root-Cause eingegrenzt — `agents.list.main.tools` greift für Discord-Surface nicht ausreichend; maßgeblich ist `tools.byProvider.discord`. Ich setze jetzt einen minimalen Provider-Scoped Allow für `image` (und teste optional Dispatch-Tool-Key), dann verifiziere ich die Atlas-Discord-Surface erneut.
- 2026-04-26T22:45:14.928Z | DONE | 7c2d2397-79d1-49cf-ad9d-e9dbd4a95659 | [Forge] Atlas Discord Tool Surface Baseline: dispatch + image | worker=sre-expert | progress=- | summary=PARTIAL: Policy-Pfad für Discord wurde eingegrenzt und minimal konfiguriert, aber Atlas-Discord zeigt weiterhin kein `image` und kein echtes Dispatch-Tool; zusätzlich blockiert ein aktueller sessions_send Gateway-Timeout die Live-Verifikation nach Reload.
- 2026-04-26T22:47:45.147Z | START | 1bacf4bb-5269-41b8-9774-67d7392bbd8e | [Forge] Fix localhost proof access for Atlas heartbeat control checks | worker=sre-expert | progress=- | summary=-
- 2026-04-26T22:48:53.452Z | CHECKPOINT | 1bacf4bb-5269-41b8-9774-67d7392bbd8e | [Forge] Fix localhost proof access for Atlas heartbeat control checks | worker=sre-expert | progress=- | summary=- | note=Root-Cause bestätigt: Problem liegt nicht an MC-Endpoint-Verfügbarkeit, sondern am Zugriffspfad (`web_fetch` blockt localhost/private-IP). Ich setze als engen Ersatz eine dokumentierte Truth-Order-Änderung in HEARTBEAT.md auf read-only `exec+curl`-Proof-Checks und verifiziere Tool-Surface/Endpoint-Erreichbarkeit ohne neue Broad-Tool-Freigaben.
- 2026-04-26T22:50:41.716Z | DONE | 1bacf4bb-5269-41b8-9774-67d7392bbd8e | [Forge] Fix localhost proof access for Atlas heartbeat control checks | worker=sre-expert | progress=- | summary=HEARTBEAT-Proof-Zugriff ist jetzt deterministisch dokumentiert: statt blockiertem web_fetch auf 127.0.0.1 nutzt Atlas read-only exec+curl für die drei Mission-Control Truth-Order-Endpunkte, ohne neue Broad-Tool-Freigaben.
- 2026-04-27T02:05:30.397Z | START | 4e0618d2-f453-4fa0-b483-8c57afc6a7c7 | [Nightly] Harden alerts API route with fail-soft error handling | worker=sre-expert | progress=- | summary=-
- 2026-04-27T02:06:34.090Z | CHECKPOINT | 4e0618d2-f453-4fa0-b483-8c57afc6a7c7 | [Nightly] Harden alerts API route with fail-soft error handling | worker=sre-expert | progress=- | summary=- | note=Implementierung steht: /api/alerts hat jetzt einen top-level fail-soft try/catch mit strukturiertem 500-JSON + no-store; Regressionstest für Unexpected-Failure und Ingress-Preserve ist hinzugefügt. Als Nächstes laufen tsc, Test, Build und Live-Verifikation.
- 2026-04-27T02:08:18.595Z | FAILED | 4e0618d2-f453-4fa0-b483-8c57afc6a7c7 | [Nightly] Harden alerts API route with fail-soft error handling | worker=sre-expert | progress=- | summary=- | note=Global TypeScript gate failed (npx tsc --noEmit, exit 1).
- 2026-04-27T06:06:30.214Z | START | 5455079a-cca8-4afa-baa8-d5f96e3f3fa1 | [Atlas][Stufe7] Reportingformat vereinheitlichen + Sprint-8 Prompt vorbereiten | worker=Atlas | progress=- | summary=-
- 2026-04-27T06:07:08.208Z | CHECKPOINT | 5455079a-cca8-4afa-baa8-d5f96e3f3fa1 | [Atlas][Stufe7] Reportingformat vereinheitlichen + Sprint-8 Prompt vorbereiten | worker=Atlas | progress=20% | summary=- | note=Task body read. Plan/doc/rules sources located; missing workspace scripts/rules-render.sh noted and will be handled by wrapper to canonical /home/piet/.openclaw/scripts/rules-render.sh.
- 2026-04-27T06:08:19.783Z | CHECKPOINT | 5455079a-cca8-4afa-baa8-d5f96e3f3fa1 | [Atlas][Stufe7] Reportingformat vereinheitlichen + Sprint-8 Prompt vorbereiten | worker=Atlas | progress=70% | summary=- | note=Stage-7 result-format KB and Sprint-7+8 prompt written to vault; R57 appended to memory/rules.jsonl; feedback_system_rules.md regenerated via workspace scripts/rules-render.sh wrapper.
- 2026-04-27T06:09:11.058Z | DONE | 5455079a-cca8-4afa-baa8-d5f96e3f3fa1 | [Atlas][Stufe7] Reportingformat vereinheitlichen + Sprint-8 Prompt vorbereiten | worker=main | progress=70% | summary=EXECUTION_STATUS
done — Task 5455079a-cca8-4afa-baa8-d5f96e3f3fa1 completed; terminal result receipt written with sprintOutcome and verified by GET.

RESULT_SUMMARY
Created the canonical Stage-7 Atlas reporting format and the official Sprint-7+8 prompt. Added R57 to memory/rules.jsonl, regenerated feedback_system_rules.md through scripts/rules-render.sh, and added a workspace wrapper for the renderer path referenced by the task. No worker fanout was dispatched because the task anti-scope forbids Sprint-8 fanout; this was a bounded Atlas-owned documentation/rules mutation.

FILES_CHANGED
- /home/piet/vault/03-Agents/kb/atlas-result-format.md
- /home/piet/vault/03-Agents/kb/atlas-sprint-7-8-prompt.md
- /home/piet/.openclaw/workspace/memory/rules.jsonl
- /home/piet/.openclaw/workspace/feedback_system_rules.md
- /home/piet/.openclaw/workspace/scripts/rules-render.sh

VALIDATION
- JSONL parsed successfully; last rule is R57.
- atlas-result-format.md contains all five canonical fields: EXECUTION_STATUS, RESULT_SUMMARY, GATES, FOLLOW_UPS, OPERATOR_DECISIONS.
- feedback_system_rules.md contains rendered R57 and reports 56 rules.
- /home/piet/.openclaw/workspace/scripts/rules-render.sh executed successfully.
- Workspace commit: d77013ba. Vault commit: 93cfcc1.

NEXT_STEP
Use /home/piet/vault/03-Agents/kb/atlas-sprint-7-8-prompt.md as the gated prompt for Stage 8 after operator approval.
- 2026-04-27T06:09:55.292Z | START | 1db3aa49-3e30-4db4-a086-06a747259b4a | [Follow-up][Lens] Materializer sequential dispatch policy review | worker=efficiency-auditor | progress=- | summary=-
- 2026-04-27T06:11:07.221Z | DONE | 1db3aa49-3e30-4db4-a086-06a747259b4a | [Follow-up][Lens] Materializer sequential dispatch policy review | worker=efficiency-auditor | progress=- | summary=Materializer-Policy Review: direkte Dispatch-Automation nur sequentiell, max 1 aktiver Child-Dispatch und max 2 offene materialisierte Children; bei health!=ok oder worker/pickup Findings nur Preview/Assigned, kein Auto-Dispatch. Operator-Go fuer direct dispatch bleibt offen.
- 2026-04-27T06:11:20.633Z | START | 29307251-d2bc-4b1b-ac78-f046b8442329 | [P1][Forge] Migration-Beschluss: m7-Kernel-Timer vs Legacy-Crons | worker=atlas | progress=- | summary=-
- 2026-04-27T06:12:16.800Z | CHECKPOINT | 29307251-d2bc-4b1b-ac78-f046b8442329 | [P1][Forge] Migration-Beschluss: m7-Kernel-Timer vs Legacy-Crons | worker=atlas | progress=65% | summary=- | note=Live-Inventar erhoben: aktive m7-Timer/Services und aktueller Crontab verglichen; ich formuliere jetzt Overlap-Cluster, Optionen/Risiken und die empfohlene Migrationsreihenfolge.
- 2026-04-27T06:13:12.587Z | DONE | 29307251-d2bc-4b1b-ac78-f046b8442329 | [P1][Forge] Migration-Beschluss: m7-Kernel-Timer vs Legacy-Crons | worker=sre-expert | progress=65% | summary=EXECUTION_STATUS: done
RESULT_SUMMARY: Read-only decision brief erstellt. Live-Inventar zeigt: m7-Kernjobs laufen bereits als systemd-Timer (1m/2m/5m); entsprechende Legacy-Cron-Einträge für diese Kernjobs sind nicht mehr in crontab aktiv. Verbleibende Cron-Jobs bilden separate Guard-/Maintenance-Schicht mit partieller Funktionsnähe (v. a. Session- und Monitoring-Bereich).
OVERLAP_CLUSTERS:
1) CORE-M7-MIGRATED: auto-pickup, plan-runner, mc-watchdog, worker-monitor, stale-lock-cleaner, session-freeze-watcher -> aktiv als m7-*.timer/service; kein identischer aktiver Crontab-Duplikatlauf sichtbar.
2) SESSION-GUARD-ADJACENT: m7-session-freeze-watcher (Task/Session-Stall-Erkennung) vs Cron-Guards session-rotation-watchdog (*/2), session-size-guard (* und */5), session-janitor (*/30) -> ähnliche Risikodomäne (Session-Gesundheit), aber unterschiedliche Trigger/KPIs.
3) PLATFORM-MONITORING-ADJACENT: m7-mc-watchdog (2m Service-Liveness-Heal) vs Cron mc-ops-monitor (stündlich Health/Ops-Checks) -> kein 1:1-Duplikat, aber teilweise überlappende Beobachtungsziele.
OPTIONS_AND_RISKS:
A) Hybrid stabil lassen (m7-Kern via Timer, übrige Guards weiter Cron): geringstes Sofortrisiko, aber höhere Betriebs-Komplexität (2 Scheduler-Welten).
B) Domänenweise Konsolidierung in systemd (zuerst Session-Guards, dann Monitoring): mittleres Risiko, reduziert Drift/Debug-Aufwand; benötigt klare Unit-Hardening/Alert-Routing-Validierung.
C) Big-bang Vollmigration aller Cron-Guards: höchstes Risiko (Blind Spots/Timing-Regressionen), nicht empfohlen.
RECOMMENDED_ORDER:
1. Keine Änderung an CORE-M7-MIGRATED (bereits sauber timer-basiert).
2. Session-Guard-Cluster zuerst konsolidieren (rotation/size/janitor/freeze) mit Canary-Phase und Dual-Run-Fenster.
3. Danach Monitoring-Cluster (mc-ops-monitor + verwandte Checks) in Timer überführen, erst dann Legacy-Crons abbauen.
4. Pro Cluster: vor Abschaltung eines Cron-Jobs immer 7 Tage Nachweis (keine verschlechterten Health-/Pickup-Proofs).
OPERATOR_DECISION_REQUEST: Bitte Option B freigeben (domänenweise Migration mit Canary + Nachweisfenster) oder explizit Hybrid-Dauerbetrieb bestätigen. Es wurden keine Runtime-Änderungen durchgeführt.
- 2026-04-27T06:21:13.791Z | START | 283bab6b-650e-4507-a7a1-0a35a33c8ef0 | [P1][Forge] Option B: Session-Guard Cron→systemd Canary vorbereiten | worker=atlas | progress=- | summary=-
- 2026-04-27T06:22:03.895Z | CHECKPOINT | 283bab6b-650e-4507-a7a1-0a35a33c8ef0 | [P1][Forge] Option B: Session-Guard Cron→systemd Canary vorbereiten | worker=atlas | progress=45% | summary=- | note=Legacy-Session-Guard-Crons und Zielscripte sind inventarisiert. Ich erstelle jetzt canary-sichere systemd-Units (ohne Cron-Abschaltung) plus Rollback- und 7-Tage-Proof-Plan.
- 2026-04-27T06:24:01.492Z | DONE | 283bab6b-650e-4507-a7a1-0a35a33c8ef0 | [P1][Forge] Option B: Session-Guard Cron→systemd Canary vorbereiten | worker=sre-expert | progress=45% | summary=EXECUTION_STATUS: done
RESULT_SUMMARY: Option-B Session-Guard Canary wurde live vorbereitet und aktiviert, ohne Legacy-Cron zu entfernen: drei neue user-level canary timer/services laufen parallel in safe mode (rotation-watchdog dry-run, size-guard --log-only, janitor dry-run scanner). Zusätzlich wurde ein neuer Dry-Run-Scanner für janitor erstellt, damit die janitor-Migration risikominimiert beobachtbar ist.
FILES_CHANGED:
- /home/piet/.config/systemd/user/canary-session-rotation-watchdog.service
- /home/piet/.config/systemd/user/canary-session-rotation-watchdog.timer
- /home/piet/.config/systemd/user/canary-session-size-guard.service
- /home/piet/.config/systemd/user/canary-session-size-guard.timer
- /home/piet/.config/systemd/user/canary-session-janitor.service
- /home/piet/.config/systemd/user/canary-session-janitor.timer
- /home/piet/.openclaw/workspace/scripts/session-janitor-canary.py
CANARY_UNITS_OR_RUNBOOK:
- canary-session-rotation-watchdog.timer: OnBootSec=3min, OnUnitActiveSec=10min, Unit=canary-session-rotation-watchdog.service (dry-run, ohne --live).
- canary-session-size-guard.timer: OnBootSec=4min, OnUnitActiveSec=10min, Unit=canary-session-size-guard.service (--log-only).
- canary-session-janitor.timer: OnBootSec=5min, OnUnitActiveSec=30min, Unit=canary-session-janitor.service (session-janitor-canary.py ohne Datei-Moves).
- Legacy cron blieb unverändert aktiv: session-rotation-watchdog (*/2), session-size-guard (*/5 + * log-only), session-janitor (*/30).
VALIDATION:
- Inventory: crontab-Zeilen für alle 3 Zieljobs bestätigt.
- Unit syntax: systemd-analyze --user verify (nur bestehende fremde vault-sync warnings, keine Fehler in neuen canary units).
- Activation: systemctl --user enable --now für alle 3 canary timer erfolgreich.
- First execution: alle 3 canary services direkt erfolgreich mit status=0/SUCCESS ausgelaufen.
- Scheduler evidence: list-timers zeigt nächste Läufe (rotation/size 10min, janitor 30min).
ROLLBACK:
1) systemctl --user disable --now canary-session-rotation-watchdog.timer canary-session-size-guard.timer canary-session-janitor.timer
2) rm /home/piet/.config/systemd/user/canary-session-{rotation-watchdog,size-guard,janitor}.service /home/piet/.config/systemd/user/canary-session-{rotation-watchdog,size-guard,janitor}.timer
3) optional rm /home/piet/.openclaw/workspace/scripts/session-janitor-canary.py
4) systemctl --user daemon-reload
5) verify: keine canary-session-* timer in list-timers
SEVEN_DAY_PROOF_PLAN:
- Täglich (7 Tage): /api/health, /api/ops/pickup-proof?limit=20, /api/ops/worker-reconciler-proof?limit=20 prüfen und Snapshot speichern.
- Canary logs täglich prüfen:
  - /home/piet/.openclaw/workspace/logs/canary-session-rotation-watchdog.log
  - /home/piet/.openclaw/workspace/logs/canary-session-size-guard.log
  - /home/piet/.openclaw/workspace/logs/canary-session-janitor.log
- Drift prüfen: Cron + canary dürfen keine Fehlerspitzen/lock-contention erzeugen.
- Nach 7 stabilen Tagen: erst dann separater Änderungs-Task zur schrittweisen Cron-Reduktion je Job.
NEXT_OPERATOR_DECISION:
Freigabe für Phase 2 erbeten: Soll nach 7 Tagen zuerst session-rotation-watchdog Cron (*/2) auf timer-only umgestellt werden, oder zuerst session-size-guard Cron-Paar? Empfehlung: zuerst rotation-watchdog, dann size-guard, janitor zuletzt.
- 2026-04-27T06:33:43.884Z | START | b53ac84b-9c62-4577-83e8-29a5c234f8ea | [P0][Forge] OpenClaw 2026.4.25 Update Readiness + Dry-run + Go/No-Go | worker=atlas | progress=- | summary=-
- 2026-04-27T06:34:23.953Z | CHECKPOINT | b53ac84b-9c62-4577-83e8-29a5c234f8ea | [P0][Forge] OpenClaw 2026.4.25 Update Readiness + Dry-run + Go/No-Go | worker=atlas | progress=55% | summary=- | note=Update-Status, Dry-Run und Doctor wurden ausgeführt; ich ermittle jetzt Board-Quiet-Status, Backup-Nachweise und formuliere Go/No-Go mit Runbook/Rollback.
- 2026-04-27T06:36:43.196Z | DONE | b53ac84b-9c62-4577-83e8-29a5c234f8ea | [P0][Forge] OpenClaw 2026.4.25 Update Readiness + Dry-run + Go/No-Go | worker=sre-expert | progress=55% | summary=EXECUTION_STATUS: done
RESULT_SUMMARY: Update-Readiness und Dry-Run wurden vollständig durchgeführt. Für stabile Schiene ist 2026.4.24 verfügbar; für 2026.4.25 ist nur Beta (2026.4.25-beta.10) nachweisbar. Empfehlung: aktuell NO-GO für Pre-release-Upgrade, bis QMD/Toolbridge-Basiszustand wieder grün ist und ein separater Go-Task freigegeben wird.
CURRENT_STATE:
- Installiert: OpenClaw 2026.4.22 (openclaw --version), Node v22.22.0.
- Install-Typ: package (pnpm), Channel effektiv: stable.
- update status --json: latest stable 2026.4.24 verfügbar.
- Registry dist-tags: latest=2026.4.24, beta=2026.4.25-beta.10.
- Board quiet vor künftigem Update: pending-pickup_excl_current=0, in-progress_excl_current=0.
- Doctor (non-interactive): completed; Security-Warnungen vorhanden (u.a. Gateway bind lan, exec security full).
- QMD status: Not connected (aktueller Toolbridge-/MCP-Risikofaktor).
DRY_RUN_FINDINGS:
1) openclaw update status --json
   - installKind=package, packageManager=pnpm, effectiveChannel=stable
   - currentVersion=2026.4.22, latestVersion(stable)=2026.4.24
2) openclaw update --dry-run --json
   - targetVersion=2026.4.24
   - erwartete Aktionen: package update, plugin sync, completion refresh, gateway restart + doctor checks
3) openclaw update --dry-run --json --tag 2026.4.25-beta.10
   - targetVersion=2026.4.25-beta.10 (pre-release path bestätigbar)
4) openclaw doctor --non-interactive
   - erfolgreich abgeschlossen; keine fatalen Stopper, aber Sicherheits-/Härtungshinweise
RISK_MATRIX:
- Gateway/Restart-Risiko: mittel (Updatepfad beinhaltet Gateway-Restart; aktiver Betrieb kann kurz unterbrochen werden).
- Toolbridge/QMD-Risiko: hoch (QMD aktuell nicht verbunden; Baseline nicht grün).
- Taskboard MCP-Risiko: niedrig-mittel (taskboard stats erreichbar, aber Post-Update trotzdem Pflichtcheck).
- Plugin-Registry/Sync-Risiko: mittel (Dry-run zeigt plugin update sync als festen Schritt).
- Config-Migration-Risiko: niedrig-mittel (doctor läuft, aber Pre-release erhöht Migrationsunsicherheit).
- Active Sessions-Risiko: mittel (mehrere aktive Sessions sichtbar; Restart-Fenster koordinieren).
- Runtime/Node-Risiko: niedrig (Node v22.22.0 kompatibel erscheinend).
BACKUP_CHECKLIST:
- ✅ /home/piet/.openclaw/openclaw.json vorhanden
- ✅ /home/piet/.openclaw/workspace vorhanden (4.6G)
- ✅ Session-State: /home/piet/.openclaw/agents/main/sessions/sessions.json vorhanden (381M dir)
- ✅ Task-State: mission-control/data/tasks.json + worker-runs.json vorhanden
- ✅ Konfig-Backups vorhanden: /home/piet/vault/08-Backups/openclaw-config-backups/2026-04-27 (und Vortage)
- Empfehlung vor Go-Task: zusätzlich on-demand Snapshot von openclaw.json + sessions + tasks.json unmittelbar vor Updatezeitpunkt erstellen.
IMPLEMENTATION_RUNBOOK:
1) Pre-Go Gates (im separaten Go-Task):
   a) Board quiet bestätigen (kein pending-pickup/in-progress außer Wartungstask)
   b) QMD/Toolbridge connectivity grün
   c) frischer pre-update Snapshot (config/sessions/tasks)
2) Stable-Pfad (bevorzugt):
   - openclaw update --dry-run --json
   - openclaw update --yes --json
3) Pre-release-Pfad (nur explizit freigegeben):
   - openclaw update --dry-run --json --tag 2026.4.25-beta.10
   - openclaw update --yes --json --tag 2026.4.25-beta.10
4) Keine weiteren Mutationen parallel (kein cron/gateway/config/model-routing change außerhalb Updatepfad).
POST_UPDATE_VERIFY:
- openclaw --version entspricht Zielversion
- openclaw doctor --non-interactive erfolgreich
- openclaw status zeigt Gateway/Channels gesund
- /api/health ok
- /api/ops/pickup-proof?limit=20 ok
- /api/ops/worker-reconciler-proof?limit=20 ok
- qmd__status != Not connected
- taskboard stats abrufbar
ROLLBACK_CRITERIA:
Rollback/Abort wenn eines zutrifft:
- doctor liefert harte Fehler nach Update
- Gateway/Health bleibt degraded/down über vereinbartes Wartungsfenster
- QMD/Toolbridge oder Taskboard MCP bleibt nach Update nicht funktionsfähig
- kritische Session-/Dispatch-Proofs zeigen Regressionsmuster
Rollback-Aktion (separater Notfalltask): Rückkehr auf stabilen bekannten Stand (mindestens 2026.4.24; falls nötig 2026.4.22) via explizitem --tag + danach doctor/status/proofs.
GO_NO_GO_RECOMMENDATION:
NO-GO für sofortiges Upgrade auf 2026.4.25-beta.10 in der aktuellen Lage.
CONDITIONAL GO für separates, explizit freigegebenes Update-Fenster, sobald QMD/Toolbridge wieder grün ist und Pre-Go-Backups unmittelbar vor Ausführung bestätigt sind. Wenn kein Pre-release-Zwang besteht: zuerst stable 2026.4.24 bevorzugen.
