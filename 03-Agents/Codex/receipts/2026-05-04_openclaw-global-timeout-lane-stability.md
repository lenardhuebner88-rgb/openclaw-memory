# 2026-05-04 OpenClaw Global Timeout/Lane Stability

## Ziel

Stabilitaet vor Kosten: nicht nur Atlas/main, sondern alle OpenClaw Agents sollen mehr Runtime-Budget bekommen, damit Fallback/Recovery nicht vom lokalen 300s + 30s Lane-Cap abgeschnitten wird.

## Durchgefuehrt

- `/home/piet/.openclaw/openclaw.json`
  - Backup: `/home/piet/.openclaw/openclaw.json.bak-20260504T100703Z-global-timeout600-stability`
  - `agents.defaults.timeoutSeconds`: `300` -> `600`
  - Keine per-agent Timeout-Overrides vorhanden.

- Neuer schmaler beta.4-kompatibler Patch:
  - Script: `/home/piet/.openclaw/scripts/apply-embedded-lane-grace-patch.py`
  - Drop-in: `/home/piet/.config/systemd/user/openclaw-gateway.service.d/embedded-lane-grace-patch.conf`
  - Scope: nur `EMBEDDED_RUN_LANE_TIMEOUT_GRACE_MS` von 30s auf 10min.
  - Bewusst nicht gepatcht: diagnostic `allowActiveAbort`, damit beta.4 Upstream abort-drain nicht ausgehebelt wird.
  - Bundle-Backup: `/home/piet/backups/openclaw-embedded-lane-grace-patch/pi-embedded-D-LaArit.js.bak-lane-grace-20260504T100705Z`

- Gateway-Restart auf User-Freigabe:
  - Vorher PID: `838452`
  - Nachher PID: `882905`
  - Restart-Zeit: `2026-05-04 12:09:24 CEST`
  - `/health`: `{"ok":true,"status":"live"}`

- Atlas stale fallback pin entfernt:
  - Backup: `/home/piet/.openclaw/agents/main/sessions/sessions.json.bak-20260504T101034Z-manual-stale-atlas-discord-pin-reset`
  - Entfernt nur Session-Key: `agent:main:discord:channel:1486480128576983070`
  - Entfernte Werte: `modelOverride=gpt-5.3-codex`, `modelOverrideSource=auto`, `providerOverride=openai`
  - Keine `.jsonl` History geloescht.

- Breites Discord-Fallback-Chain Monitoring fuer alle Agents:
  - Script: `/home/piet/.openclaw/scripts/openclaw-discord-fallback-chain-watch.py`
  - Service: `/home/piet/.config/systemd/user/canary-openclaw-discord-fallback-chain-watch.service`
  - Timer: `/home/piet/.config/systemd/user/canary-openclaw-discord-fallback-chain-watch.timer`
  - State: `/home/piet/.openclaw/workspace/logs/openclaw-discord-fallback-chain-watch.state.json`
  - Log: `/home/piet/.openclaw/workspace/logs/openclaw-discord-fallback-chain-watch.log`
  - Timer: alle 2 Minuten.

## Validierung

- `openclaw config validate`: valid.
- Gateway: `active`.
- Gateway health: live.
- ExecStartPre beim Restart:
  - `apply-embedded-lane-grace-patch.py`: `already-patched embedded-lane-grace`
  - MCP recovery: marker already present.
  - response hardening: bekannte beta.4 store-lock anchor drift nur als skip, kein Startup-Fail.
- Aktiver Bundle-Wert:
  - `const EMBEDDED_RUN_LANE_TIMEOUT_GRACE_MS = 10 * 60 * 1e3;`
- Fallback-Logs seit Restart:
  - Keine neuen `codex app-server attempt timed out`
  - Keine neuen `FailoverError`
  - Keine neuen `CommandLaneTaskTimeout`
  - Keine neuen `status 408`
- Timer:
  - `canary-atlas-discord-fallback-chain-watch.timer` aktiv.
  - `canary-openclaw-discord-fallback-chain-watch.timer` aktiv.

## Restbefunde

- `sre-expert` hat noch einen alten Session-Store-Eintrag:
  - `agent:sre-expert:discord:channel:1486480146524410028`
  - `status=running`
  - `updatedAt=2026-05-04T06:55:53Z`
  - Keine model/provider Overrides.
  - Empfehlung: separat per read-only Guard bewerten, nicht blind loeschen.

## Rollback

```bash
cp /home/piet/.openclaw/openclaw.json.bak-20260504T100703Z-global-timeout600-stability /home/piet/.openclaw/openclaw.json
cp /home/piet/backups/openclaw-embedded-lane-grace-patch/pi-embedded-D-LaArit.js.bak-lane-grace-20260504T100705Z /home/piet/.npm-global/lib/node_modules/openclaw/dist/pi-embedded-D-LaArit.js
rm -f /home/piet/.config/systemd/user/openclaw-gateway.service.d/embedded-lane-grace-patch.conf
systemctl --user daemon-reload
systemctl --user restart openclaw-gateway.service
```

Atlas session reset rollback, falls noetig:

```bash
cp /home/piet/.openclaw/agents/main/sessions/sessions.json.bak-20260504T101034Z-manual-stale-atlas-discord-pin-reset /home/piet/.openclaw/agents/main/sessions/sessions.json
systemctl --user restart openclaw-gateway.service
```

## Naechster Schritt

Einen echten Atlas Discord Turn ausloesen und danach pruefen:

- completed model ist wieder `openai/gpt-5.5`
- kein `modelOverrideSource=auto`
- kein `FailoverError`
- kein `codex app-server attempt timed out`
- Dauer bleibt unter neuem 600s Budget oder faellt sauber in Fallback ohne Lane-Abbruch.
