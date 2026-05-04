# OpenClaw Beta4 Stabilization Plan

Stand: 2026-05-04 09:16 CEST
Owner: Codex
Scope: Atlas/Forge timeout stabilization after OpenClaw 2026.5.3-beta.4

Update: 2026-05-04 09:33 CEST - spaetere Claude-Korrekturen erneut gegen Live-Dateien, Bundle, Journal, npm und GitHub API geprueft.

## Executive Verdict

Ein einfacher Wechsel von Atlas auf `openai/gpt-5.3-codex` ist nicht die Loesung. Der Wechsel kann hoechstens eine kurzfristige Containment-Massnahme sein, weil `gpt-5.3-codex` im Live-Fallback einen konkreten Atlas-Turn gerettet hat.

Die primaere Stabilisierung muss die Ursache reduzieren, die in den Live-Daten jetzt besser belegt ist: Heartbeat- und Discord-Lane laufen im nativen Codex-App-Server-Pfad mit grossem Cache-Kontext in Konkurrenz. Der bisher staerkste Trigger ist der 06:49:59 UTC Heartbeat, der 6 Sekunden vor einem echten Discord-Operator-Turn startete. Der Operator-Turn timeoutete danach zweimal nach jeweils ca. 300s.

Die gepostete Claude/Atlas-Analyse ist in den Kernpunkten valide, aber zwei Punkte werden korrigiert:

- Heartbeat-Isolation nicht global ueber `agents.defaults` aktivieren. Zuerst nur `agents.list[id=main].heartbeat` setzen, damit wir Atlas isolieren und keine neuen Agent-Heartbeats nebenbei aktivieren.
- Minimax-Quelle ist inzwischen identifiziert: zwei aktivierte Cron-Payloads requesten `minimax/*`, nicht nur ein unklarer alter Payload-State.

## Verifizierte Live-Fakten

- `openclaw --version`: `OpenClaw 2026.5.3-beta.4 (c6c64e2)`.
- Gateway nach beta4 ist live.
- `agents.defaults.heartbeat`: nicht gesetzt.
- `agents.list[main].heartbeat`: nicht gesetzt.
- Atlas/main Routing: `openai/gpt-5.4 -> openai/gpt-5.4-mini -> openai/gpt-5.3-codex`.
- Forge/sre-expert Routing: `openai/gpt-5.3-codex -> openai/gpt-5.5 -> openai/gpt-5.4-mini -> openai/gpt-5.4`.
- Heartbeat-Schema in beta4 unterstuetzt `every`, `model`, `ackMaxChars`, `timeoutSeconds`, `lightContext`, `isolatedSession`, `skipWhenBusy`.
- Bundle implementiert `resolveIsolatedHeartbeatSessionKey()` und haengt `:heartbeat` an.
- `hasExplicitHeartbeatAgents(cfg)` existiert: sobald ein Agent explizit `heartbeat` hat, werden nur diese expliziten Heartbeat-Agenten scheduled. Das spricht gegen eine globale Defaults-Aenderung als ersten Schritt.
- `apply-openclaw-response-hardening.py` besteht aus drei Patch-Teilen: typing TTL, session-write-lock watchdog, session-store lock hold. Nur der store-lock Teil driftet hart in beta4.
- Rotation-Infrastruktur ist aktiv: `canary-session-rotation-watchdog.timer`, `canary-session-size-guard.timer`, `m7-auto-pickup.timer`.
- `auto-pickup.py` konsumiert `/tmp/atlas-rotation-signal.json`.
- Rotation-Watchdog misst aktuell Session-Dateigroesse bzw. `tokens_est`, nicht Modell-`cacheRead`. Deshalb loest `cacheRead=168k` keinen Rotation-Signal-Flow aus.
- Keine aktivierten `jobs.json` Jobs targeten `agentId=main`.
- Aktivierte Minimax-Cron-Quellen:
  - `5b6e3416-3164-4625-b04a-d806be4baeff`, `efficiency-auditor-heartbeat`, payload model `minimax/MiniMax-M2.7-highspeed`.
  - `0f9d0f2e-9839-4a14-ad18-cb75ff7f49c7`, `mc-pending-pickup-smoke-hourly`, payload model `minimax/MiniMax-M2.7`.
- Journal bestaetigt dieselben Minimax-Cron-Quellen nach beta4:
  - `09:00:01 CEST`, lane `session:agent:efficiency-auditor:cron:5b6e3416...`, requested `minimax/MiniMax-M2.7-highspeed`, error `Model provider minimax not found`.
  - `09:05:02 CEST`, lane `session:agent:system-bot:cron:0f9d0f2e...`, requested `minimax/MiniMax-M2.7`, error `Model provider minimax not found`.
- GitHub Issue `openclaw/openclaw#76307` ist real und geschlossen; der Report beschreibt Stream-Abbrueche/Fetch-Timeouts bei langen Outputs.
- GitHub Issue `openclaw/openclaw#66561` ist real und offen; Rollback auf `openai-codex/*` ist deshalb nicht die bevorzugte Stabilisierung.
- GitHub Release-API: `v2026.5.3-beta.3` liefert HTTP 200; `v2026.5.3-beta.4` liefert HTTP 404. Deshalb ist beta3 die belastbare GitHub-Release-Notes-Quelle fuer den Stream-Fix; beta4 ist ueber npm belegt (`dist-tags.beta=2026.5.3-beta.4`, publish time `2026-05-04T04:08:47Z`).

## Bewertung der spaeteren Claude-Korrekturen

Angenommen:

- `skipWhenBusy` gehoert in Phase 1. Es war bereits im Plan enthalten und ist im Bundle belegt.
- Phase-1-Validation soll neben `:heartbeat` auch Busy-Skip Events beobachten.
- beta4 nicht als GitHub-Fix-Doku verwenden. Fix-Doku bleibt beta3; beta4 Installation wird ueber npm belegt.

Abgelehnt bzw. korrigiert:

- Die Aussage `jobs.json filter by minimax in payload -> 0 Treffer` ist gegen den aktuellen Live-Stand falsch. `jobs.json` enthaelt zwei aktivierte Minimax-Payloads, und das Journal korreliert exakt mit diesen IDs.
- Phase 4 ist deshalb nicht bei "Quelle unbekannt" blockiert. Ungeklaert ist nur, warum der Codex-App-Server den konfigurierten Provider `minimax` trotz OpenClaw-Config ablehnt.

## Entscheidende Live-Timeline

### Erfolgreiche Discord-Turns vor Heartbeat-Overlap

- `2026-05-04T06:47:19Z` Atlas Discord, `gpt-5.4`, success `06:47:27Z`, `cacheRead=6528`, `total=61943`.
- `2026-05-04T06:47:41Z` Atlas Discord, `gpt-5.4`, success `06:48:23Z`, `cacheRead=64896`, `total=69268`.

### Heartbeat-Overlap und Timeout-Kaskade

- `2026-05-04T06:49:59Z` Heartbeat startet auf `sessionKey=agent:main:main`, `gpt-5.4-mini`.
- `2026-05-04T06:50:05Z` echter Atlas Discord-Turn startet auf `agent:main:discord:channel:1486480128576983070`, `gpt-5.4`.
- Heartbeat endet `06:50:32Z` erfolgreich, aber mit `cacheRead=168320`, `total=174816`.
- Discord-Turn timeoutet `06:55:05Z`, `codex app-server attempt timed out`, `cacheRead=85376`, `total=86017`.
- Fallback `gpt-5.4-mini` timeoutet `07:00:07Z`, `cacheRead=89472`, `total=92405`.
- Fallback `gpt-5.3-codex` succeeded `07:02:34Z`, `cacheRead=104320`, `total=105602`.

### Interpretation

Die beste aktuelle Hypothese ist nicht mehr "gpt-5.4 ist schlecht, gpt-5.3-codex ist gut", sondern:

- Native Codex-App-Server-Lane wird bei grossen Cache-Kontexten und parallelem Heartbeat/User-Turn instabil.
- `gpt-5.3-codex` war in diesem Fall robust genug, um den Turn zu retten, ist aber nicht der eigentliche Root-Fix.
- Heartbeat-Isolation ist der kleinste Fix mit hohem Impact, weil sie genau den belegten Overlap trennt.

## Stabilisierung in Phasen

### Phase 0 - Read-only Baseline

Status: erledigt.

Gate:

- beta4 live bestaetigt.
- Heartbeat-Isolation im Bundle bestaetigt.
- Heartbeat/Discord-Overlap belegt.
- Rotation-Infra aktiv, aber cacheRead-blind.
- Minimax-Cron-Quellen identifiziert.

Stopper: keiner.

### Phase 1 - Primary Fix: Atlas Heartbeat Isolieren

Ziel: Heartbeat-Lane von Atlas Operator-/Discord-Lane trennen.

Change:

- Backup von `/home/piet/.openclaw/openclaw.json`.
- Nicht `agents.defaults.heartbeat` setzen.
- Nur in `agents.list[id=main]` setzen:

```json
"heartbeat": {
  "every": "30m",
  "isolatedSession": true,
  "lightContext": true,
  "model": "openai/gpt-5.4-mini",
  "timeoutSeconds": 120,
  "ackMaxChars": 80,
  "skipWhenBusy": true
}
```

Warum diese Felder:

- `isolatedSession:true`: erzeugt `agent:main:main:heartbeat`, trennt Store/Lane vom Operator-Kontext.
- `lightContext:true`: beta4 unterstuetzt es; reduziert Bootstrap-Kontext fuer Heartbeats.
- `model:gpt-5.4-mini`: Heartbeat ist Light-Lane, nicht Reasoning-Task.
- `timeoutSeconds:120`: Heartbeat darf schnell failen; 300s Blockade ist fuer Health-Wake nicht akzeptabel.
- `ackMaxChars:80`: kapselt HEARTBEAT_OK/Tool-Ack.
- `skipWhenBusy:true`: reduziert Konkurrenz, wenn Atlas gerade arbeitet.

Validation nach Restart:

- JSON valid.
- Gateway health live.
- Naechster Heartbeat erzeugt `sessionKey=agent:main:main:heartbeat`.
- Wenn Atlas/Discord-Lane waehrend eines geplanten Heartbeats busy ist, soll ein Busy-Skip Event sichtbar werden, z. B. `HEARTBEAT_SKIP_LANES_BUSY`.
- Echte Atlas Discord-Turns laufen parallel oder kurz nach Heartbeat ohne `codex app-server attempt timed out`.
- 2-3h Beobachtung: 0 Timeouts auf `session:agent:main:discord:*`.

Rollback:

- Backup zurueckkopieren.
- `systemctl --user restart openclaw-gateway.service`.

### Phase 2 - Restart-Hygiene: Response-Hardening Script Splitten

Ziel: Keine ExecStartPre-FAILUREs mehr durch tote beta4-Anker.

Change:

- In `/home/piet/.openclaw/scripts/apply-openclaw-response-hardening.py` den `patch_store_lock_hold()`-Block in `main()` beta4-sicher deaktivieren oder als no-op markieren.
- Typing-TTL und `session-write-lock` 1s Watchdog bleiben aktiv.
- Kommentar in das Script: store-lock symbols removed in beta4; keep disabled unless re-anchored.

Validation:

```bash
python3 /home/piet/.openclaw/scripts/apply-openclaw-response-hardening.py; echo EXIT=$?
```

Erwartung:

- exit 0.
- Keine `failed session-store lock hold patch` Zeile.
- Nach naechstem Gateway-Restart keine ExecStartPre FAILURE durch dieses Script.

### Phase 3 - Context/Rotation Guard fuer cacheRead

Ziel: Rotation nicht nur anhand Session-Dateigroesse, sondern anhand realer Modell-Cache-Nutzung triggern.

Problem:

- `memory-budget.log` meldet bei Atlas nur 4-6 Prozent, waehrend Trajectories `cacheRead=168k` zeigen.
- Der aktuelle Rotation-Watchdog sieht die tatsaechliche Modelllast nicht.

Plan:

- Separaten read-only `trajectory-cache-watch` bauen oder Rotation-Watchdog erweitern.
- Quelle: neueste `.trajectory.jsonl` pro Agent.
- Felder: `usage.cacheRead`, `usage.total`, `timedOut`, `sessionKey`, `runId`, `model`.
- Warnung bei `cacheRead >= 80000`.
- Rotation-Signal oder Operator-Alert bei `cacheRead >= 150000` plus laufender Discord/Operator-Hotpath.

Validation:

- Bei bestehender `cacheRead=168k` Historie erkennt der neue Check die Ueberschreitung.
- Keine Rotation ohne Signal/Schwellwert.
- Auto-pickup konsumiert Signal weiterhin ueber `/tmp/atlas-rotation-signal.json`.

### Phase 4 - Minimax Cron Noise Separat Bereinigen

Ziel: `Model provider minimax not found` aus Cron-Laeufen entfernen, ohne Atlas-RCA zu vermischen.

Live-Quelle:

- `efficiency-auditor-heartbeat` requestet `minimax/MiniMax-M2.7-highspeed`.
- `mc-pending-pickup-smoke-hourly` requestet `minimax/MiniMax-M2.7`.

Offene Frage:

- Warum akzeptiert der native Codex-App-Server `minimax/*` in Cron-Agent-Turns nicht, obwohl `openclaw.json` Minimax-Auth und Modell-Definitionen enthaelt.

Empfohlene kleine Massnahme nach read-only Gegencheck:

- Beide Cron-Payloads temporaer auf `openai/gpt-5.4-mini` setzen, falls diese Jobs nicht explizit Minimax testen sollen.
- Minimax-Provider-Mapping danach als eigenes Thema pruefen.

Nicht tun:

- Minimax Plugin blind entfernen; Live-Main-Smokes konnten Minimax-Modell-IDs teilweise erfolgreich ausfuehren.

Validation:

- Naechster 09:00/Hourly Cron erzeugt keine `Model provider minimax not found`.

### Phase 5 - Inaktive Heartbeats Nur Nach Phase 1

Ziel: Token- und Noise-Reduktion.

Wichtig:

- Aktuell gibt es keine expliziten Heartbeat-Keys auf den Agenten.
- Sobald wir `main.heartbeat` explizit setzen, scheduled OpenClaw laut Bundle nur explizite Heartbeat-Agenten.
- Deshalb nicht sofort breit `heartbeat: { every: "disabled" }` auf viele Agenten schreiben; erst pruefen, was Phase 1 bewirkt.

Nach Phase-1-Validierung:

- Falls andere Agenten weiter automatisch heartbeaten, gezielt deaktivieren.
- Kandidaten: `frontend-guru`, `spark`, `james`, `efficiency-auditor`.

### Phase 6 - m7-mc-watchdog Separat

Ziel: MC-Defense-Layer reparieren, aber nicht mit Atlas/Forge Timeout-RCA vermischen.

Plan:

- Logs vom 2026-04-30 Crash lesen.
- `reset-failed` erst nach Diagnose.
- Manuell `/home/piet/.openclaw/scripts/mc-watchdog.sh` testen.
- Nur wenn manuell sauber: Service reaktivieren.

## Erfolgsdefinition

24h nach Phase 1+2:

- 0 `codex app-server attempt timed out` auf `session:agent:main:discord:*`.
- 0 `FailoverError: LLM request timed out` fuer Atlas Operator-Turns.
- Heartbeat-Trajectories laufen unter `agent:main:main:heartbeat`.
- Busy-Overlap wird durch `skipWhenBusy` sichtbar verhindert: bei belegter Atlas-Lane erscheinen Busy-Skip Events statt paralleler Heartbeat-LLM-Turns.
- Heartbeats bleiben kurz und leicht: `timeoutSeconds=120`, `ackMaxChars=80`, `lightContext=true`.
- Atlas Operator-Turns antworten in normalen Discord-Use-Cases konsistent unter 60s.
- Service-Uptime bleibt mindestens 12h ohne ungeplanten Restart.
- `apply-openclaw-response-hardening.py` exit 0.
- Gateway-Restarts ohne ExecStartPre FAILURE.
- `openclaw --version` bleibt `2026.5.3-beta.4`.
- Gateway `/health` bleibt live.

## Stop Conditions

Sofort stoppen und neu analysieren, wenn:

- nach Phase 1 weiterhin ein Atlas Discord-Turn nach Heartbeat-Overlap timeoutet,
- Heartbeat-Isolation keine `:heartbeat` Session erzeugt,
- JSON-Validation fehlschlaegt,
- Gateway nicht live kommt,
- neue `ERR_MODULE_NOT_FOUND` nach stabilem Start auftauchen,
- Rotation-Signal automatische Endlosschleifen erzeugt.

## Empfohlene Reihenfolge

1. Phase 1 umsetzen: `main.heartbeat` isoliert konfigurieren.
2. Restart und 30-60 Minuten warten, bis ein echter Heartbeat sichtbar ist.
3. Atlas weiter real arbeiten lassen und parallel Logs/Trajectories beobachten.
4. Phase 2 Script-Hygiene umsetzen, falls Phase 1 Restart sauber war oder beim naechsten Restart wieder ExecStartPre Failure sichtbar wird.
5. Phase 3 cacheRead-Watch planen/implementieren.
6. Phase 4 Minimax Cron Noise separat fixen.
7. Phase 6 MC-Watchdog erst danach.

## Monitoring Commands

```bash
openclaw --version
curl -fsS http://127.0.0.1:18789/health
systemctl --user show openclaw-gateway.service -p ActiveState -p SubState -p ExecMainStartTimestamp -p ExecMainPID -p NRestarts -p MemoryCurrent -p TasksCurrent --value
journalctl --user -u openclaw-gateway.service --since '2026-05-04 08:40:00' --no-pager | rg 'codex app-server attempt timed out|FailoverError|fetch timeout reached|ERR_MODULE_NOT_FOUND|Model provider minimax not found|model fallback decision'
journalctl --user -u openclaw-gateway.service --since '1 hour ago' --no-pager | rg 'HEARTBEAT_SKIP_LANES_BUSY|heartbeat.*skipped|lanes_busy|skipWhenBusy'
rg -n 'sessionKey.*heartbeat|timedOut|promptError|cacheRead|model.completed' /home/piet/.openclaw/agents/main/sessions/*.trajectory.jsonl
```

## Durable Artifacts

- Fix receipt: `/home/piet/vault/03-Agents/Codex/receipts/2026-05-04_openclaw-beta4-timeout-fix.md`
- Upgrade backup: `/home/piet/.openclaw/backups/openclaw-beta4-upgrade-20260504T062526Z`
- Current plan: `/home/piet/vault/03-Agents/Codex/plans/2026-05-04_openclaw-beta4-stabilization-plan.md`
