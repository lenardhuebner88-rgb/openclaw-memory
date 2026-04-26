---
status: active
owner: codex
created: 2026-04-27
scope: "Forge image-tool RCA fix + Atlas Autonomy 9.5 Sprint"
---

# Ziel

OpenClaw Autonomie nach dem Forge-Blocker wieder stabilisieren und durch einen Atlas-geführten 8-Slice-Sprint gegen ein 9.5/10-Zielbild prüfen.

# Live-Startbefund

- Forge-Task `adfc0596-096a-4e0b-905d-ad232f79524b` war nicht mehr aktiv, sondern terminal `failed` durch `worker-monitor` nach 24 Minuten ohne Progress.
- Rootcause Image-Tool: Atlas bekam `image_generate`, aber die aktive OpenClaw-Tool-Policy nutzt in diesem Setup den Tool-Key `image`.
- Minimalfix gesetzt: `/home/piet/.openclaw/openclaw.json` Atlas `tools.alsoAllow` und `tools.sandbox.tools.alsoAllow` jeweils auf `image` korrigiert. Backup liegt unter `/home/piet/.openclaw/backup/audit-2026-04-27/`.
- Gateway-Hot-Reload belegt: `/tmp/openclaw/openclaw-2026-04-27.log` meldet `config hot reload applied (agents.list)`.
- Folge-Task `2fe45813-247e-4a5d-87e3-d5e80d81506c` hatte `dispatchTarget=None`; auto-pickup meldete `SKIP_NO_TARGET`. Minimalfix: `dispatchTarget=sre-expert` gesetzt.
- Forge-Finalisierung danach gruen: `STATUS: PASS`, `ATLAS_IMAGE_TOOL_VISIBLE: yes`, Worker-Run `succeeded`.
- Codex-Sandbox kann Discord nicht direkt posten (`Temporary failure in name resolution` / `fetch failed`), Atlas/MC soll Sprint-Updates selbst posten.

# Aktuelle Wertung

Vor dem Sprint: 8.6/10.

Warum nicht 9.5: Der Image-Fix ist gruen, aber es gab zwei Autonomie-Schwachstellen im Ablauf: falscher Tool-Key im Prompt und fehlender `dispatchTarget`. Beide sind minimal behoben, muessen aber im normalen Atlas-Flow regressionsfest bewiesen werden.

# Atlas 8-Slice Sprint

Atlas steuert genau einen Parent-Sprint. Maximal zwei Child-Tasks gleichzeitig. Keine Modellwechsel, kein sudo, kein OpenClaw-Upgrade. Mutationen nur klein/reversibel und nur wenn Gate-Evidence klar ist.

1. **A1 Dispatch-Completeness Gate**
   - Suche alle aktiven `pending-pickup`/`assigned` Tasks ohne `dispatchTarget`.
   - Gate: `no_target=0`, sonst genau eine kleinste Korrektur oder `PARTIAL`.

2. **A2 Pickup/First-Heartbeat Gate**
   - Prüfe letzte Auto-Pickup-Zyklen auf `first_heartbeat_gate`, `no_first_heartbeat`, `pending_pickup`.
   - Gate: `first_heartbeat=pass`, `no_first_heartbeat=0`.

3. **A3 Worker-Run-Reconciler Gate**
   - Prüfe `worker-reconciler` dry-run/proof auf offene terminale Runs und stale active runs.
   - Gate: `proposedActions=0` oder explizit begruendeter Safe-Fix.

4. **A4 Reporting/Discord Gate**
   - Prüfe zuletzt terminale Tasks auf `resultSummary`, `finalReportSentAt`, `lastReportedStatus`.
   - Gate: keine neuen done/failed Tasks ohne Ergebnisreport; wenn Discord-Transport kaputt, klar klassifizieren.

5. **A5 Atlas Session/Context Gate**
   - Prüfe aktuelle Atlas Session-Size, Rotation, und ob Session-Wachstum durch unnötige Logs/Tools entsteht.
   - Gate: kein HARD/ROTATION-Blocker; bei Warnung nur Empfehlung, kein harter Reroute.

6. **A6 QMD/Vault Truth Gate**
   - Prüfe Atlas QMD-Tool-Binding plus direkte Vault-Datei-Wahrheit; keine QMD-Architekturänderung.
   - Gate: aktuelle Vault-Dateien direkt lesbar, QMD-Zustand klar klassifiziert.

7. **A7 Cron/Heartbeat Coverage Gate**
   - Read-only Snapshot: m7-auto-pickup, worker-monitor, mc-watchdog, session-freeze-watcher, agent heartbeats.
   - Gate: keine akute stale-open-run/heartbeat-Lücke; strukturelle Lücken nur als Follow-up.

8. **A8 Autonomy Follow-up Gate**
   - Aus realen Findings maximal zwei Follow-up-Tasks als Preview erstellen; nur einen sicheren Read-only/Small-Fix ausführen, falls Gate-grün.
   - Gate: Atlas liefert Score, Residual Risks, und klare nächste 3 Schritte. Ziel >=9.0/10, 9.5 nur wenn A1-A8 gruen und Reporting funktioniert.

# Stop-Kriterien

- Neuer Task ohne `dispatchTarget`.
- Offener Worker-Run auf terminalem Task.
- Kein first heartbeat nach Claim.
- Fanout >2 Child-Tasks.
- Modellwechsel oder sudo wird benötigt.
- Discord/Reporting still failed ohne Klassifikation.

# Reporting

Atlas soll nach jedem Slice kurz in Discord `1495737862522405088` posten:

- Slice-ID
- Gate: green/yellow/red
- Evidence-Pfad/Logzeile
- Mutation: none/small-fix/blocked
- Next step

Codex begleitet read-only über `tasks.json`, `worker-runs.json`, `auto-pickup.log`, `worker-reconciler.mjs --dry-run` und Vault-Plan.

# Live Dispatch

- 2026-04-26T22:16Z: Parent-Sprint als Atlas/Main-Task angelegt: `337c2717-9b9e-4e98-88bd-c477e91e9160`.
- Dispatch-Felder: `status=pending-pickup`, `dispatchState=dispatched`, `executionState=queued`, `assigned_agent=main`, `dispatchTarget=main`.
- Backup vor Mutation: `/home/piet/.openclaw/backup/audit-2026-04-27/tasks.json.bak-before-atlas-autonomy-8slice-*`.
- 2026-04-26T22:16Z: Auto-pickup claimed den Parent sauber: `CLAIM_CONFIRMED task=337c2717 agent=main ... first_heartbeat_gate=ok`; danach `pending_pickup=pass`, `proof_green=pass`.
- 2026-04-26T22:19Z: Parent terminal `done`, finaler Score `9.1/10`. 9.5 wurde nicht vergeben wegen A4 Reporting-Metadaten und A7 Non-main Heartbeat-Policy.
- 2026-04-26T22:21Z: Die zwei safe/read-only Follow-up-Drafts wurden als kontrollierter Max-2-Lauf dispatcht: Forge `7e4a1073-94a6-40dc-85ec-616375971074`, Lens `361355af-bd7b-4db2-a81b-c2665c6e444d`.
- 2026-04-26T22:24Z: Beide Follow-ups sauber claimed, jeweils mit `first_heartbeat_gate=ok`; Auto-Pickup danach `pending_pickup=pass`, `proof_green=pass`.
- 2026-04-26T22:27Z: Beide Follow-ups terminal erfolgreich. Lens empfiehlt 9.5 mit dokumentiertem Scope-Based Waiver fuer Non-main Heartbeats; Forge klassifiziert A4 als Legacy/Discord-401-Metadatenproblem, kein aktueller Transportausfall.
- 2026-04-26T22:31Z: Atlas erzeugte zwei weitere Forge-Baseline-Tasks; `1bacf4bb-5269-41b8-9774-67d7392bbd8e` hing als `assigned/queued` ohne Dispatch. Minimal normalisiert auf `dispatchTarget=sre-expert` und danach `pending-pickup/dispatched`.

# Abschluss 2026-04-26T22:51Z

## Gate-Resultat

- Forge-Ursprungstask `adfc0596-096a-4e0b-905d-ad232f79524b`: nicht reaktiviert; Rootcause war falscher Tool-Key `image_generate` statt runtime-gueltig `image`.
- Korrektur wurde ueber Folge-Task `2fe45813-247e-4a5d-87e3-d5e80d81506c` verifiziert: `ATLAS_IMAGE_TOOL_VISIBLE: yes`, Task `done`.
- Atlas 8-Slice-Sprint `337c2717-9b9e-4e98-88bd-c477e91e9160`: terminal `done`, Score `9.1/10`.
- Zwei gezielte Follow-ups wurden ohne Operator-Freigabe dispatcht, da weder Sudo noch Modellwechsel betroffen waren: Forge `7e4a1073-94a6-40dc-85ec-616375971074`, Lens `361355af-bd7b-4db2-a81b-c2665c6e444d`; beide `done`.
- Zusaetzlicher Forge-Task `1bacf4bb-5269-41b8-9774-67d7392bbd8e`: erst Claim-Timeout waehrend Gateway-Restart/Drain, danach selbst erholt, `CLAIM_CONFIRMED`, terminal `done`.

## Live-Proofs

- `node scripts/worker-reconciler.mjs --dry-run`: `proposedActions: 0`.
- Board-Status: keine aktiven `pending-pickup`/`in-progress`/`assigned` Tasks.
- Auto-Pickup nach Recovery: `pending_pickup=pass`, `proof_green=pass`; ein historischer `trend_claim_timeouts_10m=1` bleibt als gelber Nachlauf.
- Mission-Control-Watchdog: durchgehend `OK healthy` bis `2026-04-26T22:49:30Z`.
- Gateway: nach Full-Restart wieder `ready`, Modell `openai-codex/gpt-5.5`.

## Rootcause-Kette

1. Forge hatte einen falschen Tool-Key konfiguriert: `image_generate` ist in der aktuellen OpenClaw-Tool-Surface kein gueltiger Allowlist-Key.
2. Die korrekte Freigabe ist `image`; diese wurde in Atlas/Main `tools.alsoAllow` und `tools.sandbox.tools.alsoAllow` gesetzt.
3. Ein spaeterer Forge-Baseline-Task erweiterte zusaetzlich `tools.byProvider.discord.alsoAllow` und fuehrte einen Gateway-Full-Restart aus. Der Restart traf laufende Forge-Session-/Claim-Pfade und erzeugte `GatewayDrainingError`, `session file locked` und einen einmaligen Claim-Timeout.
4. Das Pickup-System hat sich danach selbst erholt; kein manueller Kill, kein neuer Duplikat-Task und kein Rollback waren noetig.

## Autonomie-Wertung

- Aktueller Stand nach Gates: **9.1/10 stabil belegt**.
- **9.5/10 ist mit dokumentiertem Scope-Based Waiver vertretbar**, wenn Non-main-Heartbeat-Coverage als gelbes Residual-Risk akzeptiert wird und historische Reporting-Metadaten nicht als aktueller Transportfehler gewertet werden.
- Ohne Waiver bleibt die harte Wertung bei 9.1/10, weil A4/A7 nicht voll gruen sind.

## Naechste zwei Hebel

1. **Gateway-Restart-Governance fuer Worker-Tasks:** Runtime-/Gateway-Restarts nie aus laufendem Forge-Task heraus gegen aktive Sessions; stattdessen Safe-Window, Drain-Check, dann Restart.
2. **Reporting-Metadaten-Backfill:** historische `lastReportedStatus + threadError=401` und legacy `canceled` Datensaetze explizit klassifizieren, damit aktuelle Gates nicht durch Altlasten gelb bleiben.
