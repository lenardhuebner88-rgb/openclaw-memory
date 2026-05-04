# OpenClaw/Mission-Control Stabilization Final Report — 2026-05-04

Canonical location decision: this report is under `/home/piet/vault/03-Projects/plans/` because the stabilization covered OpenClaw runtime, Mission Control board state, cron, timers, guards, sessions, and operator procedure across agents. Agent receipts remain evidence sources; this file is the operator/system SSOT.

Live check time: 2026-05-04 around 13:17 CEST.

## Executive Verdict

- Overall: YELLOW, stable post-fix with one active high-cache Atlas session and one unrelated failed legacy watchdog unit.
- Gateway: GREEN.
- Atlas/main: YELLOW, active/running and no overrides, but current Discord session is over cache/token thresholds.
- Forge/sre-expert: GREEN, stale Discord session key rotated and no current Forge Discord session remains.
- Session Store: YELLOW, guard dry-run has only the active Atlas high-cache candidate.
- Timers/Guards: YELLOW, canary timers active; `m7-mc-watchdog.service` remains failed from prior state.
- Cronjobs: GREEN, enabled `minimax/*` payload refs are now `0`.
- Mission Control Board: GREEN, health and board consistency OK, open tasks and open worker-runs `0`.
- Logs since restart: GREEN, no post-restart timeout/fallback/minimax provider signatures.

## Timeline

- 2026-05-04 early: Hermes/Codex investigation identified embedded-run timeout persistence and Atlas timeout behavior. Historical timeout events before the later restart are evidence, not current post-fix failures.
- 2026-05-04 12:09:24 CEST: OpenClaw beta.4 Gateway restarted after approved timeout/lane-grace stability changes.
- Timeout budget and lane grace:
  - `agents.defaults.timeoutSeconds` set to `600`.
  - Embedded lane timeout grace patched to 10 minutes.
  - systemd user drop-in added for restart persistence.
- Atlas stale pin cleanup:
  - Old Atlas Discord fallback/session override pin removed.
  - `.jsonl` history preserved.
- All-agent session guard:
  - All-agent Discord stability guard implemented and tested.
  - Scoped mode added for exact `--only-session-key` cleanup.
- Forge scoped cleanup:
  - Removed stale Forge Discord key `agent:sre-expert:discord:channel:1486480146524410028`.
- Minimax cron fix:
  - Two enabled Minimax cron payload models changed to OpenAI/Codex model to avoid provider-not-found noise.
- Mission Control lifecycle canaries:
  - Worker lifecycle canary passed: task `c7dcb8b2-def2-4ed3-841d-ca9c9defb92b`, run `72fd1cb6-bd78-4fe1-9f6f-ae5985c6d9b1`.
  - Draft-to-done E2E board-state canary passed: task `9c2cd146-e4e3-4f69-a562-125784a628cb`, run `4f51fd44-9103-41b0-bc65-ad55e40fbdea`.

## Root Cause Status

- H1 Heartbeat/Discord race: mitigated/observing. No post-restart timeout/fallback signatures.
- H2 stale modelOverride/session pin: mitigated. Atlas stale override pin and Forge stale running key were removed; current Atlas has no overrides.
- H3 timeout budget/lane cap: mitigated. Runtime timeout is 600s and lane grace is 10 minutes.
- H4 minimax cron noise: mitigated. Enabled cron payload refs to `minimax/*` are `0`; pre-restart provider-not-found events are historical.
- H5 Mission Control worker lifecycle: verified. Live worker lifecycle and full draft-to-done board-state canaries passed.
- H6 high cache / long Discord session context: active risk. Current Atlas Discord session is running with `cacheRead=202624`, `totalTokens=205008`; do not rotate while active/recent.

## Changes Made

- OpenClaw config timeout:
  - File: `/home/piet/.openclaw/openclaw.json`
  - Change: `agents.defaults.timeoutSeconds` to `600`.
  - Backup: `/home/piet/.openclaw/openclaw.json.bak-20260504T100703Z-global-timeout600-stability`
  - Rollback: restore backup and restart Gateway only with operator approval.

- Embedded lane grace:
  - Script: `/home/piet/.openclaw/scripts/apply-embedded-lane-grace-patch.py`
  - Drop-in: `/home/piet/.config/systemd/user/openclaw-gateway.service.d/embedded-lane-grace-patch.conf`
  - Bundle backup: `/home/piet/backups/openclaw-embedded-lane-grace-patch/pi-embedded-D-LaArit.js.bak-lane-grace-20260504T100705Z`
  - Rollback: restore bundle backup and remove drop-in, then daemon-reload/restart with approval.

- Session guard scripts:
  - Script: `/home/piet/.openclaw/scripts/openclaw-discord-session-stability-guard.py`
  - Tests: `/home/piet/.openclaw/scripts/tests/test_openclaw_discord_session_stability_guard.py`
  - Behavior: dry-run by default; live requires `--live`; scoped cleanup via `--only-session-key`.

- Fallback watcher scripts/timers:
  - Script: `/home/piet/.openclaw/scripts/openclaw-discord-fallback-chain-watch.py`
  - Script: `/home/piet/.openclaw/scripts/atlas-discord-fallback-chain-watch.py`
  - Timers: `canary-atlas-discord-fallback-chain-watch.timer`, `canary-openclaw-discord-fallback-chain-watch.timer`.

- Forge session cleanup:
  - Removed session key: `agent:sre-expert:discord:channel:1486480146524410028`
  - Removed sessionId: `d62fb49b-74ec-49f7-a8a5-64db96bee16e`
  - Backup: `/home/piet/.openclaw/agents/sre-expert/sessions/sessions.json.bak-20260504T103538Z-openclaw-discord-session-stability-guard`
  - Rollback: restore that `sessions.json` backup if needed.

- Cron Minimax risk fix:
  - File: `/home/piet/.openclaw/cron/jobs.json`
  - Backup: `/home/piet/.openclaw/cron/jobs.json.bak-20260504T104937Z-minimax-cron-fix`
  - Changed:
    - `efficiency-auditor-heartbeat`: `minimax/MiniMax-M2.7-highspeed` -> `openai-codex/gpt-5.4-mini`
    - `mc-pending-pickup-smoke-hourly`: `minimax/MiniMax-M2.7` -> `openai-codex/gpt-5.4-mini`
  - Rollback: restore jobs backup.

- Mission Control canaries:
  - Worker lifecycle canary backups:
    - `/home/piet/.openclaw/state/mission-control/data/tasks.json.bak-20260504T110005Z-mc-canary-worker-lifecycle-live`
    - `/home/piet/.openclaw/state/mission-control/data/worker-runs.json.bak-20260504T110005Z-mc-canary-worker-lifecycle-live`
    - `/home/piet/.openclaw/state/mission-control/data/board-events.json.bak-20260504T110005Z-mc-canary-worker-lifecycle-live`
    - `/home/piet/.openclaw/state/mission-control/data/board-events.jsonl.bak-20260504T110005Z-mc-canary-worker-lifecycle-live`
  - Draft-to-done E2E canary backups:
    - `/home/piet/.openclaw/state/mission-control/data/tasks.json.bak-20260504T110757Z-mc-e2e-draft-to-done-canary`
    - `/home/piet/.openclaw/state/mission-control/data/worker-runs.json.bak-20260504T110757Z-mc-e2e-draft-to-done-canary`
    - `/home/piet/.openclaw/state/mission-control/data/board-events.json.bak-20260504T110757Z-mc-e2e-draft-to-done-canary`
    - `/home/piet/.openclaw/state/mission-control/data/board-events.jsonl.bak-20260504T110757Z-mc-e2e-draft-to-done-canary`
  - Rollback: restore corresponding data backups only if operator intentionally wants to remove canary artifacts.

## Validation Gates Passed

- Gateway health: `{"ok":true,"status":"live"}`.
- Gateway uptime: `Mon 2026-05-04 12:09:24 CEST`.
- Gateway `NRestarts=0`.
- Post-restart Gateway journal: no matches for `FailoverError`, `codex app-server attempt timed out`, `CommandLaneTaskTimeout`, `candidate_failed`, `status 408`, or `Model provider minimax not found`.
- Guard dry-run: only active Atlas high-cache candidate; no load errors.
- Cron minimax refs: enabled `minimax/*` payload refs `0`.
- Mission Control `/api/health`: OK, open tasks `0`, orphaned dispatches `0`.
- Mission Control `/api/board-consistency`: OK.
- Worker lifecycle canary: GREEN core path.
- Draft-to-done E2E canary: GREEN core path, YELLOW only for ingress nuance and unrelated concurrent events.

## Current Live State

- OpenClaw version: `OpenClaw 2026.5.3-beta.4 (c6c64e2)`.
- Gateway:
  - `MainPID=882905`
  - `SubState=running`
  - `NRestarts=0`
  - `ActiveEnterTimestamp=Mon 2026-05-04 12:09:24 CEST`
- Mission Control:
  - `/api/health`: OK
  - `/api/board-consistency`: OK
  - `totalTasks=966`
  - `openTasks=0`
  - `pendingPickup=0`
  - `inProgress=0`
  - `orphanedDispatches=0`
- Atlas current Discord session:
  - sessionKey: `agent:main:discord:channel:1486480128576983070`
  - sessionId: `29e5f70f-809f-442d-8f9c-0517500352f9`
  - status: `running`
  - model: `gpt-5.5`
  - overrides: none
  - cacheRead/totalTokens: `202624` / `205008`
  - age at live check: about `58s`
- Forge state:
  - stale Discord key removed.
  - no current Forge Discord session in guard dry-run.
- Enabled timers:
  - Atlas and all-agent fallback-chain timers active.
  - session guard / janitor / rotation / size timers active.
- Cron risks:
  - enabled cronjobs: `14`
  - enabled `minimax/*` payload refs: `0`
- Known remaining failed unit:
  - `m7-mc-watchdog.service` failed, pre-existing legacy signal; not a current Mission Control board failure.

## Remaining Risks

- Atlas high cache can recur while the same Discord thread stays active.
- Watcher historical logs before `2026-05-04 12:09:24 CEST` can cause false RED/YELLOW if checks are not time-windowed.
- OpenClaw beta.4 upstream behavior can still shift bundle anchors; keep patch scripts compile-checked after updates.
- Active sessions must not be rotated until idle/recent safety gate is satisfied.
- `m7-mc-watchdog.service` remains a legacy failed unit and should be repaired separately if it is still part of desired ops coverage.

## Next Safe Operating Procedure

- Let Atlas finish the active Discord turn.
- If Atlas is idle for more than 10 minutes and cache remains high, rotate only `agent:main:discord:channel:1486480128576983070` using scoped guard/live procedure.
- Continue 24h observation.
- Do not change config again unless post-restart logs show real failures.
- Treat historical pre-restart timeout/fallback/minimax events as historical evidence, not current incidents.

## Evidence Appendix

Source receipts:
- `/home/piet/vault/03-Agents/Codex/receipts/2026-05-04_openclaw-global-timeout-lane-stability.md`
- `/home/piet/vault/03-Agents/Codex/receipts/2026-05-04_openclaw-all-agent-session-stability-guard.md`
- `/home/piet/vault/03-Agents/Codex/receipts/2026-05-04_forge-scoped-stale-session-rotation.md`
- `/home/piet/vault/03-Agents/Codex/receipts/2026-05-04_openclaw-beta4-post-gate-stability-check.md`
- `/home/piet/vault/03-Agents/Codex/receipts/2026-05-04_mission-control-live-worker-lifecycle-canary.md`
- `/home/piet/vault/03-Agents/Codex/receipts/2026-05-04_mission-control-e2e-draft-to-done-canary.md`
- `/home/piet/vault/03-Agents/Hermes/receipts/2026-05-04_embedded-run-persistence-and-atlas-timeout.md`
- `/home/piet/vault/03-Agents/Hermes/investigations/atlas-timeout-2026-05-04/`

Mission Control canary IDs:
- Worker lifecycle taskId: `c7dcb8b2-def2-4ed3-841d-ca9c9defb92b`
- Worker lifecycle runId: `72fd1cb6-bd78-4fe1-9f6f-ae5985c6d9b1`
- Draft-to-done taskId: `9c2cd146-e4e3-4f69-a562-125784a628cb`
- Draft-to-done runId: `4f51fd44-9103-41b0-bc65-ad55e40fbdea`

Validation commands used read-only for this final report:
- `openclaw --version`
- `systemctl --user show openclaw-gateway.service -p ActiveEnterTimestamp -p NRestarts -p MainPID -p SubState --no-pager`
- `curl -fsS http://127.0.0.1:18789/health`
- `curl -fsS http://127.0.0.1:3000/api/health`
- `curl -fsS http://127.0.0.1:3000/api/board-consistency`
- `python3 /home/piet/.openclaw/scripts/openclaw-discord-session-stability-guard.py`
- `journalctl --user-unit openclaw-gateway.service --since '2026-05-04 12:09:24'`

