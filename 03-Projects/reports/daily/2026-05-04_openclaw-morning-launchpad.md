# OpenClaw Morning Launchpad — 2026-05-04

Generated: `2026-05-04T20:33:29+00:00`
Window: last `12h`

## GO/NO-GO: YELLOW

Recommended mode: **Produktiv starten mit Beobachtung**

## System Ampel

- **Gateway**: GREEN
- **Mission Control**: GREEN
- **Board**: GREEN
- **Worker Lifecycle**: GREEN
- **Cron**: YELLOW
- **Timers**: GREEN
- **Logs**: YELLOW
- **Atlas**: YELLOW
- **Forge**: GREEN
- **Spark**: GREEN
- **Lens**: GREEN
- **Pixel**: GREEN
- **James**: GREEN
- **System Bot**: GREEN

## Agenten
- **Atlas** (`main`): YELLOW | primary=`openai-codex/gpt-5.5` | runtime=`pi` | sessionStatus=`done` model=`gpt-5.5` cacheRead=`36352` total=`37848` | reasons=historical gateway fallback/timeout signals in window
- **Forge** (`sre-expert`): GREEN | primary=`openai-codex/gpt-5.3-codex` | runtime=`pi` | sessionStatus=`done` model=`gpt-5.3-codex` cacheRead=`23040` total=`25566` | reasons=none
- **Spark** (`spark`): GREEN | primary=`openai-codex/gpt-5.3-codex` | runtime=`pi` | sessionStatus=`n/a` model=`n/a` cacheRead=`n/a` total=`n/a` | reasons=none
- **Lens** (`efficiency-auditor`): GREEN | primary=`minimax/MiniMax-M2.7-highspeed` | runtime=`pi` | sessionStatus=`n/a` model=`n/a` cacheRead=`n/a` total=`n/a` | reasons=none
- **Pixel** (`frontend-guru`): GREEN | primary=`openai-codex/gpt-5.5` | runtime=`pi` | sessionStatus=`n/a` model=`n/a` cacheRead=`n/a` total=`n/a` | reasons=none
- **James** (`james`): GREEN | primary=`openai-codex/gpt-5.5` | runtime=`pi` | sessionStatus=`n/a` model=`n/a` cacheRead=`n/a` total=`n/a` | reasons=none
- **System Bot** (`system-bot`): GREEN | primary=`openai-codex/gpt-5.5` | runtime=`pi` | sessionStatus=`None` model=`None` cacheRead=`None` total=`None` | reasons=none

## Mission Control

- openTasks: `0`
- inProgress: `0`
- pendingPickup: `0`
- staleOpenTasks: `0`
- orphanedDispatches: `0`
- raw open tasks from file: `0`
- open worker-runs: `0`

## Guards / Cron / Timers / Logs

- Session guard: rotationNeeded=`0` staleRunning=`0` loadErrors=`0`
- Failed user units: `0`
- Required timers: `{"openclaw-morning-launchpad.timer": true, "atlas-autonomy-review-tick.timer": true, "canary-openclaw-discord-session-stability-guard.timer": true, "gateway-memory-monitor.timer": true}`
- Enabled cron jobs: `14`
- Cron state errors: `8`
- Cron model allowlist misses: `0`
- Gateway log signals: `{"timeouts": 92, "failover": 28, "candidateFailed": 70, "candidateSucceeded": 12, "commandLaneTimeout": 2, "status408": 0, "clientClosed": 3, "discordAckTimeout": 6, "atlasLane": 27, "forgeLane": 17}`

## Nächste Schritte

- Atlas ist für normale Arbeit nutzbar; historische Logsignale nur beobachten.
- Keine aggressiven Stresstests oder mehrstündigen Autonomie-Runs starten, bis Cron/Log-YELLOW sauber ist.
- Nach Restart, längerer Atlas-Arbeit oder neuen Timeouts Launchpad erneut ausführen.

## Copy-Paste Prompts

- `Atlas: Plane den heutigen Arbeitstag anhand Mission Control. Keine Reparaturen, nur Priorisierung und klare nächste Schritte.`
- `Forge: Bearbeite nur Backend/RCA-Aufgaben mit klarem Scope und Receipt. Keine breiten Refactors ohne Gate.`
- `Spark: Übernimm kleine, schnelle Codefixes mit Testnachweis. Keine Gateway-/Runtime-Config anfassen.`
- `Lens: Prüfe Kosten, Cron-Noise und Monitoring nur read-only, außer ein Fix ist explizit freigegeben.`
- `Pixel: UI-Aufgaben nur mit Screenshot-/Build-Gate und ohne Mission-Control-Datenmutation.`

## Cron Errors

- `daily-cost-report`: cron payload.model 'openai-codex/gpt-5.4-mini' rejected by agents.defaults.models allowlist: openai-codex/gpt-5.4-mini
- `morning-brief`: cron payload.model 'openai-codex/gpt-5.4-mini' rejected by agents.defaults.models allowlist: openai-codex/gpt-5.4-mini
- `nightly-self-improvement`: cron payload.model 'openai-codex/gpt-5.4' rejected by agents.defaults.models allowlist: openai-codex/gpt-5.4
- `efficiency-auditor-heartbeat`: cron: job execution timed out
- `session-cleanup-local`: cron payload.model 'openai-codex/gpt-5.4-mini' rejected by agents.defaults.models allowlist: openai-codex/gpt-5.4-mini
