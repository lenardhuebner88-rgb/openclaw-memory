# Discord Agent Unresponsive - Atlas/Forge RCA

Datum: 2026-05-04
Zeitraum geprueft: ca. 14:33-16:37 CEST
Owner: Codex
Status: Stabilisierung ausgefuehrt, Post-Fix-Gates gruen

## Kurzfazit

Discord selbst war nicht der Ausfallpunkt. Die Mission-Control-Route `/api/discord/send` konnte erfolgreich in den Report-Channel `1495737862522405088` senden.

Das produktive Problem lag in den Agent-Discord-Lanes:

- Atlas/main Discord-Session war nach Timeout/Fallback auf einen alten Auto-Fallback-Pin gesetzt.
- Forge/sre-expert Discord-Session stand stale auf `running` >30 Minuten.
- Mission Control war gesund; die ueber Forge angelegten Tasks liefen durch, aber mehrere Agent-Ping-/Report-Checks timeouteten, weil die OpenClaw-Agent-Lanes selbst hingen.

## Live-Belege

### Services

- `openclaw-gateway.service`: active/running
- Gateway PID: `1035363`
- Gateway ActiveEnterTimestamp: `Mon 2026-05-04 14:59:23 CEST`
- Gateway `NRestarts=0`
- `mission-control.service`: active/running
- Mission Control `/api/health`: `ok`
- Mission Control `/api/board-consistency`: `ok`

### Discord-Route

Direkter Smoke nach `1495737862522405088`:

- Endpoint: `POST /api/discord/send`
- Ergebnis: `ok=true`
- Message ID: `1500868275557372108`

Interpretation: Discord-Token/Send-Route war nutzbar. Der Ausfall war kein genereller Discord-Send-Ausfall.

### Gateway-Timeouts letzte 2h

Relevante Events:

- 14:56 CEST Atlas Discord:
  - lane: `session:agent:main:discord:channel:1486480128576983070`
  - runId: `69ce46fa-7eab-48db-bb6b-bae4a40d00c7`
  - model: `openai/gpt-5.5`
  - error: `codex app-server attempt timed out`
  - duration: ca. `600765ms`
  - fallback: `openai/gpt-5.3-codex`, danach success
- 15:41 CEST Forge main:
  - lane: `session:agent:sre-expert:main`
  - runId: `04de0ecf-24e6-42da-a461-40843e39c1a3`
  - model: `openai/gpt-5.3-codex`
  - duration: ca. `1502169ms`
  - fallback: `openai/gpt-5.5`, danach success
- 15:56 CEST Atlas Discord:
  - lane: `session:agent:main:discord:channel:1486480128576983070`
  - runId: `90674feb-e561-4ebb-b3d1-dc6e2d681e62`
  - model: `openai/gpt-5.3-codex`
  - error: `codex app-server attempt timed out`
  - duration: ca. `600791ms`
  - fallback: `openai/gpt-5.4`, danach success
- 16:27 CEST Forge main:
  - lane: `session:agent:sre-expert:main`
  - runId: `2462de41-bdac-474c-9988-8ec8aef12ae0`
  - duration: ca. `1501661ms`

### Session-Store vor Fix

Atlas:

- sessionKey: `agent:main:discord:channel:1486480128576983070`
- sessionId: `29e5f70f-809f-442d-8f9c-0517500352f9`
- status: `timeout`
- model: `gpt-5.4`
- `modelOverride=gpt-5.4`
- `modelOverrideSource=auto`
- `providerOverride=openai`
- `cacheRead` ca. `196992`
- `totalTokens` ca. `198291`

Forge:

- sessionKey: `agent:sre-expert:discord:channel:1486480146524410028`
- sessionId: `8e22b3b4-bffa-4ca9-a5cc-a4aebf3fcab8`
- status: `running`
- age: >30 Minuten
- reason: `stale-running>30m`

### Forge/Atlas Tasks im Mission Control Board

Forge hatte mehrere Atlas-Hardening-Tasks angelegt und erledigt:

- `[P1] Atlas Discord Metadata Slimming + Dedupe`
- `[P1.1] Atlas Dedupe Perf Hardening`
- `[P1.2] Atlas Source Patch + Rebuild Verification`
- `[P1.3] Atlas E2E Live Verification`
- `[Live Audit] Mission Control Board`

Mission-Control-Sicht:

- Worker-Runs fuer diese Tasks: `succeeded`
- Board-Consistency: `ok`
- Open worker-runs nach Fix: `0`
- Open tasks nach Fix: `0`

Wichtiger Punkt: P1.3 meldete selbst, dass Stabilitaet noch nicht erreicht war:

- sample size: `59` real runs
- p50 latency: ca. `41.754s`
- p95 latency: ca. `324.706s`
- timeout runs: `3`
- cacheRead p50: `140160`
- cacheRead p95: `193920`

Die Tasks wurden also korrekt verarbeitet, aber die Produktionsstabilitaet war dadurch noch nicht nachhaltig geloest.

## Was falsch gelaufen ist

1. Die Forge-Tasks haben echte Verbesserungen eingebracht, aber die Live-E2E-Verifikation zeigte weiterhin hohe Latenz und Timeout-Ausreisser.
2. Atlas lief danach weiter in derselben lang gewachsenen Discord-Session.
3. Der Timeout/Fallback-Mechanismus persistierte einen `modelOverrideSource=auto` und `providerOverride`.
4. Damit wurde `openclaw.json` nicht mehr effektiv fuer die bestehende Atlas-Discord-Session: die Session war auf den Fallback-Zustand gepinnt.
5. Forge hatte parallel eine stale Discord-Session auf `running`, was weitere Antworten blockieren oder verwirren konnte.
6. Mission-Control-Reporting selbst war nicht kaputt; Agent-Ping-/Report-Schritte liefen teilweise in Agent-Timeouts.

## Fix ausgefuehrt

Scoped Rotation nur der betroffenen Discord-Session-Keys:

### Atlas/main

Command:

```bash
python3 /home/piet/.openclaw/scripts/openclaw-discord-session-stability-guard.py --live --only-session-key 'agent:main:discord:channel:1486480128576983070'
```

Ergebnis:

- rotiert: ja
- Backup: `/home/piet/.openclaw/agents/main/sessions/sessions.json.bak-20260504T143640Z-openclaw-discord-session-stability-guard`
- JSONL History geloescht: nein
- Gateway-Restart: nein

### Forge/sre-expert

Command:

```bash
python3 /home/piet/.openclaw/scripts/openclaw-discord-session-stability-guard.py --live --only-session-key 'agent:sre-expert:discord:channel:1486480146524410028'
```

Ergebnis:

- rotiert: ja
- Backup: `/home/piet/.openclaw/agents/sre-expert/sessions/sessions.json.bak-20260504T143652Z-openclaw-discord-session-stability-guard`
- JSONL History geloescht: nein
- Gateway-Restart: nein

## Post-Fix-Gates

- Guard dry-run: `ok=true`
- `rotationNeeded=0`
- `staleRunning=0`
- `loadErrors=0`
- `wouldRotateSessionKeys=[]`
- Gateway: active/running, `NRestarts=0`
- Mission Control `/api/health`: `ok`
- Mission Control `/api/board-consistency`: `ok`
- Neue Gateway-Logs seit Rotation: keine neuen Timeout-/Fallback-Events, nur QMD init fuer sre-expert

## Nachzügler nach erstem Fix

Beim finalen Sanity-Check trat ein erwarteter Race-Fall auf: Ein bereits laufender Atlas-Wait schrieb nach der ersten Rotation die alte Atlas-Session erneut in `sessions.json`.

Beleg:

- Zeitpunkt: ca. 16:37 CEST
- lane: `session:agent:main:discord:channel:1486480128576983070`
- Ergebnis: `candidate_succeeded requested=openai/gpt-5.4 candidate=openai/gpt-5.3-codex`
- Session danach wieder sichtbar mit:
  - `modelOverrideSource=auto`
  - `providerOverride=openai`
  - `cacheRead` ca. `182144`
  - `totalTokens` ca. `199869`
  - status: `done`

Da der Turn danach nicht mehr aktiv war, wurde Atlas ein zweites Mal scoped rotiert:

```bash
python3 /home/piet/.openclaw/scripts/openclaw-discord-session-stability-guard.py --live --only-session-key 'agent:main:discord:channel:1486480128576983070'
```

Ergebnis:

- rotiert: ja
- Backup: `/home/piet/.openclaw/agents/main/sessions/sessions.json.bak-20260504T143845Z-openclaw-discord-session-stability-guard`
- JSONL History geloescht: nein
- Gateway-Restart: nein

Finaler Check danach:

- Guard dry-run: `ok=true`
- `rotationNeeded=0`
- aktive Discord-Sessions im 30-Minuten-Fenster: `0`
- neue Gateway-Logs seit zweiter Rotation: keine Eintraege
- Mission Control `/api/health`: `ok`

## Root Cause Status

- H1 Discord-Send-Route defekt: widerlegt.
- H2 Mission-Control-Board/Worker-Lifecycle defekt: widerlegt fuer diesen Incident.
- H3 Atlas/Forge Agent-Lanes durch Timeouts und stale sessions blockiert: bestaetigt.
- H4 Hoher Context/cacheRead verursacht Timeout-Risiko: weiterhin bestaetigt.
- H5 Compaction loest Session-Pins nicht: bestaetigt.

## Naechste Schritte

1. Atlas und Forge sollen die naechste echte Discord-Nachricht in einer neuen Session starten.
2. Direkt danach pruefen:
   - keine `modelOverrideSource=auto`
   - keine `providerOverride`
   - Atlas requested/completed wieder auf gewuenschtem primary model
   - `cacheRead` niedrig
3. Den Context-Growth-Sprint weiterfuehren:
   - Discord Prompt-Metadata Slimming validieren
   - Attachment/Textdump-Dedupe live messen
   - Low-watermark Compaction/Rotation nach Run-Ende automatisieren
4. Fallback-/Timeout-Watcher weiterlaufen lassen; ab >=2 Events/10 Minuten eskalieren.
