# OpenClaw Update Audit — 2026-05-06

Scope: Read-only audit after OpenClaw update to `2026.5.4`, including live system components, update completeness, disk growth, and weak spots. No restarts, config edits, installs, cleanup, task creation, or cron changes were performed.

## Executive Verdict

**Problem:** The update was real, but not all OpenClaw-adjacent components are version-coherent.

**Evidence:**
- `/home/piet/bin/openclaw --version` reports `OpenClaw 2026.5.4 (325df3e)`.
- `openclaw-gateway.service` runs `/home/piet/.npm-global/lib/node_modules/openclaw/dist/index.js gateway --port 18789` with Node `v22.22.0` and `OPENCLAW_SERVICE_VERSION=2026.5.4`.
- Gateway `/health`: `{"ok":true,"status":"live"}`.
- Mission Control endpoints all returned HTTP `200`, but `/api/health` is `degraded` due to execution/task state.
- OpenClaw plugin inventory shows bundled plugins loaded at `2026.5.4`, but external Discord plugin is still `@openclaw/discord@2026.5.3`; external Codex plugin is `@openclaw/codex@2026.5.3` and disabled.
- Root filesystem: `98G`, `81G` used, `13G` free, `87%` full.

**Risk:** This is not a fake/shiny update for the active Gateway core, but there is operational drift: external plugin lag, stale systemd description, old OpenClaw package copies, high disk pressure, and Mission Control/monitoring debt.

**Next Action:** Do not delete or change anything blindly. First decide whether to run a controlled plugin-sync/cleanup window with backups and post-checks.

---

## System Components — Live State

| Component | Live evidence | Status | Notes |
|---|---:|---|---|
| Host | `huebners`, time `2026-05-06T07:59:37+02:00` | OK | Linux host; root LV at `87%` used. |
| OpenClaw CLI/Core | `OpenClaw 2026.5.4 (325df3e)` | OK | Active CLI path is `/home/piet/bin/openclaw`; service points to global package. |
| OpenClaw Gateway | systemd `active/running`, PID `2572457`, memory ~650-708 MB | OK with warnings | `/health` live; recent startup had Discord fetch-timeout/event-loop warning during settle. |
| Mission Control | systemd `active/running`, PID `2352137`, memory ~227 MB | Degraded | API up, but `/api/health` reports execution degraded: 1 stale/blocked open task, recoveryLoad 1. |
| QMD HTTP MCP | systemd `active/running`, PID `2572498`, memory ~60 MB | OK with lifecycle debt | `/health` OK; `NRestarts=4203` is high and should be investigated separately. |
| QMD index | `/home/piet/.cache/qmd/index.sqlite` `459.0 MB`; 2270 docs, 88780 vectors, 20 pending | OK | Updated minutes before audit; large recent disk writer. |
| Gateway watchdog | `gateway-memory-monitor.timer` active; 2-min cadence | OK | Recent logs: Discord watchdog `connected=True`, runtime signal back to `ok`. |
| Legacy Discord bot | `openclaw-discord-bot.service` inactive/dead | OK | Expected when Gateway Discord is SSoT. |
| Hermes | `.hermes` present; this report produced by Hermes | OK | Hermes not part of OpenClaw runtime path. |

---

## Was the Update Real?

### Confirmed Real

- Active CLI: `OpenClaw 2026.5.4 (325df3e)`.
- Active service `ExecStart`: `/home/piet/.openclaw/tools/node-v22.22.0/bin/node /home/piet/.npm-global/lib/node_modules/openclaw/dist/index.js gateway --port 18789`.
- Global package: `/home/piet/.npm-global/lib/node_modules/openclaw/package.json` = `2026.5.4`.
- Gateway service env includes `OPENCLAW_SERVICE_VERSION=2026.5.4`.
- Post-update gate log `/home/piet/.openclaw/backups/openclaw-update-2026-5-4-20260506T052705Z/post-gates-20260506T054907Z.log` recorded `package 2026.5.4`, Gateway reachable, Gateway self app `2026.5.4`, service running PID `2572457`.

### Not Fully Coherent

- `/home/piet/.openclaw/npm/node_modules/openclaw/package.json` = `2026.5.3`.
- `/home/piet/.openclaw/npm/node_modules/@openclaw/discord/package.json` = `2026.5.3` and **loaded**.
- `/home/piet/.openclaw/npm/node_modules/@openclaw/codex/package.json` = `2026.5.3` and **disabled**.
- `openclaw plugins list --json` reports:
  - `discord`: version `2026.5.3`, origin `global`, status `loaded`, source `/home/piet/.openclaw/npm/node_modules/@openclaw/discord/dist/index.js`.
  - `codex`: version `2026.5.3`, origin `global`, status `disabled`.
  - Bundled `deepseek`, `memory-core`, `minimax`, `ollama`, `openai`, `openrouter`, `telegram`, `xiaomi`: version `2026.5.4`, status `loaded`.
- systemd drop-in `/home/piet/.config/systemd/user/openclaw-gateway.service.d/description-version.conf` still says `OpenClaw Gateway (v2026.5.3-1)`, while the base unit/env says `2026.5.4`.

**Interpretation:** Core/Gateway update succeeded. External plugin/package ecosystem was only partially advanced. This is the main “shine-update” risk.

---

## Disk Growth Analysis

### Current Disk Pressure

`df -h /`:

```text
Filesystem                         Size  Used Avail Use% Mounted on
/dev/mapper/ubuntu--vg-ubuntu--lv   98G   81G   13G  87% /
```

### Most Relevant Recent Growth Since ~07:40

| Size | Timestamp | Path | Interpretation |
|---:|---|---|---|
| `459.0 MB` | 07:46:50 | `/home/piet/.cache/qmd/index.sqlite` | QMD index rewrite/update; very close to the observed ~500 MB growth. |
| `362.2 MB` total | 07:46 | `/home/piet/.npm-global/lib/node_modules/openclaw` | New active OpenClaw 2026.5.4 global package tree. |
| `629 MB` total | 05:27-05:49 | `/home/piet/.openclaw/backups/openclaw-update-2026-5-4-20260506T052705Z` | Update rollback/backup bundle. Codex subagent saw ~471 MB old package + ~158 MB MC data inside. |
| `64.4 MB` | 07:53:10 | `/home/piet/.openclaw/agents/main/qmd/xdg-cache/qmd/index.sqlite` | Agent-local QMD cache. |
| `14.6 MB` | 08:00 | `/home/piet/.openclaw/workspace/memory/session-health.log` | Normal log growth, but needs rotation watch. |
| `8.2 MB` | 07:58 | `/home/piet/.openclaw/workspace/scripts/worker-monitor.log` | Log growth. |
| `7.2 MB` + `5.1 MB` | 08:00 | Mission Control board event files | State/log growth. |

### Large Persistent Footprint

| Root | Size | Notes |
|---|---:|---|
| `/home/piet/.openclaw` | `18.4 GB` measured file total | Main OpenClaw state. |
| `/home/piet/.openclaw/workspace` | `8.7 GB` | Includes Mission Control and many build artifacts. |
| `/home/piet/.openclaw/agents` | `4.1 GB` | Agent state; main agent alone ~2.7 GB per subagent check. |
| `/home/piet/.openclaw/backups` | `1.3 GB` | Includes current update backup. |
| `/home/piet/.openclaw/memory` | `1.25 GB` | SQLite memory DBs; `main.sqlite` 409.8 MB. |
| `/home/piet/.cache/qmd` | `2.6 GB` | QMD cache; current root index 459 MB. |
| `/home/piet/.hermes` | `1.8 GB` | Hermes local state; not caused by OpenClaw update. |
| Mission Control `.next*` copies | many `390-474 MB` dirs | Old isolated/debug builds are a major cleanup candidate. |

**Interpretation:** The observed ~500 MB growth is most plausibly **QMD index rewrite (`459 MB`) plus update/package churn**, not a clear failed update. However, the update also created a large rollback backup and the system is already at 87% disk usage.

---

## Runtime / Health Findings

### Good Signals

- Gateway `/health` live.
- Gateway systemd active/running; no failed user units.
- `mc_openclaw_model_runtime_failures?window=2h` returned no model-runtime failure events.
- Session health over 360 min: 11 sessions, `suspectedStuck=0`, `withErrors=0`.
- Gateway watchdog after update reports Discord `connected=True`; latest snapshot showed WS heartbeat.
- Mission Control endpoint status: all checked endpoints HTTP `200`.
- Alerts endpoint: `activeCount=0`.

### Warning Signals

- Mission Control `/api/health` reports `status=degraded`, execution degraded: stale/blocked open task and `recoveryLoad=1`.
- `/api/tasks/snapshot` reported `open=239`, while `/api/health` focused metrics reported `openTasks=1`; likely different definitions/views, but worth reconciling to avoid false “all clear”.
- `/api/monitoring` summary counts: `green=14`, `yellow=3`, `red=32`. Some red entries may be stale cron-monitoring expectations, but the number is high.
- Gateway startup window after update showed:
  - Discord `/users/@me` fetch-timeout after 2500 ms / event-loop delay.
  - Many `ws closed before connect ... code=1008 reason=connect failed` during startup/settle.
  - One `event_loop_delay` liveness warning.
  - Later watchdog returned to `runtime_signal=ok` and Discord connected.
- `openclaw model-status` via readonly MCP timed out after 12s; direct `openclaw model-status` in subagent completed in ~13.4s. This is a latency warning for diagnostics, not necessarily runtime failure.
- OpenAI direct provider auth is missing; current route relies on `openai-codex` OAuth, expiring in about 14h per subagent output.

---

## Configuration / Routing Findings

Direct config parse `/home/piet/.openclaw/openclaw.json`:

- Defaults runtime: `{ "id": "pi" }`.
- Defaults primary: `openai-codex/gpt-5.5`.
- Default fallbacks include `minimax/MiniMax-M2.7-highspeed`, `openai-codex/gpt-5.3-codex`, `minimax/MiniMax-M2.7`, `openai-codex/gpt-5.4`, `openai-codex/gpt-5.4-mini`.
- `plugins.allow`: `minimax`, `discord`, `openrouter`, `openai`, `ollama`, `deepseek`, `memory-core`, `telegram`, `xiaomi`.
- Effective config redacted confirms all named agents are now `agentRuntime.id=pi`.

**Risk:** This differs from older known-good native Codex-runtime guidance. It may be intentional after the update, but it means the current system depends on PI/openai-codex routing and external Discord plugin `2026.5.3`. Treat model/routing changes as deliberate only if an operator change note confirms them.

---

## Weak Spots / Schwachstellen

1. **External Discord plugin version drift**
   - Active Gateway core is `2026.5.4`; loaded Discord plugin is `2026.5.3` from `/home/piet/.openclaw/npm`.
   - Risk: 2026.5.4 Discord/plugin fixes may not be active.

2. **Stale systemd description**
   - Drop-in still says `OpenClaw Gateway (v2026.5.3-1)`.
   - Risk: human/operator diagnostics can misread version state.

3. **High disk usage**
   - Root at `87%`, only `13G` free.
   - Update backup, QMD cache, `.next*` build copies, agent/session state, and memory DBs are all significant.

4. **Mission Control degraded / monitoring red count**
   - MC is up, but health is not green.
   - Monitoring reports 32 red cron checks; needs triage before declaring the update fully operational.

5. **QMD service restart debt**
   - `qmd-mcp-http.service` active, but `NRestarts=4203`.
   - Risk: service works now, but restart count indicates recurring lifecycle instability or historical crash-looping.

6. **OAuth expiry / auth path risk**
   - Subagent saw `openai-codex` OAuth expiring in ~14h and missing direct `openai` auth.
   - Risk: Atlas/main may degrade when OAuth expires unless refresh path is healthy.

7. **Old package copies / rollback artifacts**
   - `.openclaw/npm/openclaw@2026.5.3`, `.openclaw/lib` older package state, and large backups remain.
   - Risk: path confusion and disk pressure; not immediate failure while service path is global 2026.5.4.

8. **Startup settle warnings after update**
   - Discord fetch-timeout/event-loop delay appeared during startup; watchdog later recovered.
   - Risk: not a current outage, but should be watched after the next restart/update.

---

## Recommended Next Actions — No Mutations Done Yet

1. **Plugin coherence gate**
   - Verify whether `@openclaw/discord@2026.5.4` and `@openclaw/codex@2026.5.4` are available and expected.
   - If yes, plan a controlled external-plugin update with backup and Gateway post-check.

2. **Disk cleanup plan, not immediate deletion**
   - Candidate cleanup classes after 24-48h stable operation:
     - old update backup generations,
     - obsolete Mission Control `.next-hermes-*` / debug build copies,
     - old OpenClaw package copies not on active service path,
     - rotated logs and archived sessions.
   - Require exact keep/delete list and rollback decision before deletion.

3. **Mission Control degraded triage**
   - Reconcile `/api/health` open task count vs `/api/tasks/snapshot` open count.
   - Triage the single stale/blocked execution item and the 32 red monitoring entries.

4. **QMD restart-count RCA**
   - Inspect `qmd-mcp-http.service` journal over 24h/7d and classify whether restarts are historical or ongoing.

5. **Auth refresh check**
   - Confirm `openai-codex` OAuth refresh status before the ~14h expiry window.

6. **Cosmetic but useful systemd cleanup**
   - Update/remove stale `description-version.conf` in a low-risk maintenance window.

---

## Subagent Consolidation

A Codex read-only audit subagent was spawned and completed. It corroborated:

- Update is real for active CLI/Gateway path.
- Version drift exists in external/global plugin paths, especially Discord `2026.5.3` loaded under OpenClaw core `2026.5.4`.
- Disk growth is plausibly explained by update backup/package tree plus QMD/cache activity.
- Stale systemd description is diagnostic drift.
- Main disk pressure is broader than the update: Mission Control `.next*` copies, OpenClaw workspace/agents/backups/memory, and QMD cache.

---

## Evidence Files / Commands Referenced

- `/home/piet/.openclaw/backups/openclaw-update-2026-5-4-20260506T052705Z/post-gates-20260506T054907Z.log`
- `/home/piet/.openclaw/openclaw.json`
- `/home/piet/.config/systemd/user/openclaw-gateway.service`
- `/home/piet/.config/systemd/user/openclaw-gateway.service.d/description-version.conf`
- `/home/piet/.cache/qmd/index.sqlite`
- `/home/piet/.npm-global/lib/node_modules/openclaw/package.json`
- `/home/piet/.openclaw/npm/node_modules/@openclaw/discord/package.json`
- `/home/piet/.openclaw/npm/node_modules/@openclaw/codex/package.json`

End of read-only audit.
