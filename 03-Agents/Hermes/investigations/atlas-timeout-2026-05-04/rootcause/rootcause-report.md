# Atlas/Forge Codex App-Server Timeout Root Cause — 2026-05-04

## Scope

Requested items:
1. Broader timeout correlation across Atlas/Forge: model, session/cache size, tool-events yes/no, fallback success.
2. Clean test setup: route Atlas primary to `openai/gpt-5.4`.

## Change applied

- Config: `/home/piet/.openclaw/openclaw.json`
- Backup: `/home/piet/.openclaw/openclaw.json.bak-20260503T222735Z-atlas-primary-gpt54`
- Changed `agents.list[id=main].model.primary` from `openai/gpt-5.5` to `openai/gpt-5.4`.
- Cleaned duplicate fallback by removing `openai/gpt-5.4` from Atlas fallback chain.
- Effective Atlas model after restart:
  - primary: `openai/gpt-5.4`
  - fallbacks: `openai/gpt-5.4-mini`, `openai/gpt-5.3-codex`

## Live post-check

- `openclaw-gateway.service`: active/running, MainPID `395240`.
- `/health`: HTTP 200 `{ ok: true, status: live }`.
- Effective config endpoint confirms Atlas primary `openai/gpt-5.4`.
- Note: `apply-openclaw-response-hardening.py` returned status 1 in ExecStartPre but service continued and health is live. This is pre-existing patch-maintenance noise, not the timeout root cause.

## Root cause conclusion

The observed Atlas/Forge incidents are not caused by a Mission Control task mutation, Discord delivery action, or a specific OpenClaw tool call.

The immediate root cause is a Codex app-server assistant-turn timeout: the app-server stream/turn does not reach terminal completion before OpenClaw's per-attempt timeout/idle watchdog aborts it. OpenClaw then marks `promptError = "codex app-server attempt timed out"` and triggers model fallback.

The dominant trigger is long-lived Discord/Codex sessions with very large cached context plus partial assistant output. In the current 00:00 window, all failed attempts had already started producing assistant text and had **zero tool execution events** before timeout. That points to the Codex app-server/model runtime path, not an OpenClaw tool.

## Key evidence

### Code path

`/home/piet/.npm-global/lib/node_modules/openclaw/dist/run-attempt-CektiLYp.js`:

- Lines 3205-3209 create a hard timeout from `params.timeoutMs` and abort the run.
- Lines 1072-1075 set `promptError = "codex app-server attempt timed out"`.
- Lines 3223-3224 map timeout to final prompt error/source.

`/home/piet/.npm-global/lib/node_modules/openclaw/dist/pi-embedded-rWtLEwl7.js`:

- Lines 2687-2710 classify assistant timeout and choose fallback behavior.
- Lines 2817-2819 show the user-facing timeout branch when no payload/tool result is available.
- Lines 1433-1441 show our restart-persistent lane-timeout grace patch; this fixes the outer 330s lane kill, but not the inner app-server model timeout.

### Live journal correlation

Examples from `/home/piet/vault/03-Agents/Hermes/investigations/atlas-timeout-2026-05-04/rootcause/gateway-24h.log`:

- `23:50:52` Atlas: `from=openai/gpt-5.5 ... rawError=codex app-server attempt timed out`, then fallback to `openai/gpt-5.4-mini`, success at `23:51:52`.
- `00:01:25` Atlas: `from=openai/gpt-5.4-mini ... rawError=codex app-server attempt timed out`, then fallback to `openai/gpt-5.4`, success at `00:01:56`.
- `00:18:55` Forge: `from=openai/gpt-5.3-codex ... rawError=codex app-server attempt timed out`, then fallback to `openai/gpt-5.5`.
- `00:23:57` Forge: `from=openai/gpt-5.5 ... rawError=codex app-server attempt timed out`, fallback to `openai/gpt-5.4-mini`.

### Trajectory correlation — current sessions

Atlas session `c398bead-a362-46ca-a764-6502d305ff61`:

| UTC ts | run | model | result | usage input/output/cache/total | tool events before complete | partial assistant text |
|---|---|---|---|---:|---:|---|
| 21:50:52 | `f1d3c6b9` | `gpt-5.5` | timeout | 12162 / 449 / 27520 / 40131 | 0 | "Die API ist erreichbar; das Board liefert live 960 Tasks..." |
| 21:51:52 | `f1d3c6b9` | `gpt-5.4-mini` | success | 934 / 1007 / 54144 / 56085 | 0 | draft task analysis completed |
| 22:01:25 | `a362c84a` | `gpt-5.4-mini` | timeout | 3354 / 893 / 73088 / 77335 | 0 | "Ich schreibe die vier Dubletten jetzt..." |
| 22:01:56 | `a362c84a` | `gpt-5.4` | success | 1279 / 233 / 84352 / 85864 | 0 | four draft duplicates canceled |
| 22:19:56 | `1b493e1a` | `gpt-5.4` | timeout | 99944 / 556 / 25472 / 125972 | 2 prior context tool events | timeout while summarizing investigation |
| 22:21:13 | `1b493e1a` | `gpt-5.4-mini` | success | 310 / 2029 / 154496 / 156835 | 2 prior context tool events | RCA summary completed |

Forge session `c34c01e4-6f69-4a78-81a5-37bc27b22029`:

| UTC ts | run | model | result | usage input/output/cache/total | tool events before complete | partial assistant text |
|---|---|---|---|---:|---:|---|
| 22:18:55 | `225824eb` | `gpt-5.3-codex` | timeout | 2828 / 403 / 150912 / 154143 | 0 | "Ich setze es jetzt in zwei Schritten um..." |
| 22:23:57 | `225824eb` | `gpt-5.5` | timeout | 655 / 223 / 168832 / 169710 | 0 | "Ich bearbeite jetzt zwei Dateien im MC-Code..." |

### Broader 24h counts

From generated artifacts:

- `journal-timeout-events.json`: 32 `codex_timeout` entries in the broader journal window, across `gpt-5.5`, `gpt-5.4-mini`, `gpt-5.3-codex`, and some legacy `openai-codex/*` refs.
- Current 30m Mission Control summary: 8 `codex_app_server_timeout`, 8 `failover_error`, 10 diagnostic lane/stuck-session observations.
- Trajectory global historical scan is noisy because it includes old sessions, but confirms timeouts are cross-model, not one model-only.

## Interpretation

Facts:

1. The failed attempts are assistant/model attempts, not OpenClaw tool executions.
2. The failure string is generated by OpenClaw's Codex app-server attempt watchdog, after the Codex app-server turn fails to complete.
3. The same auth profile appears on all OpenAI Codex-backed attempts (`sha256:195d...`) and logs repeatedly show `Profile openai-codex:lenardhuebner88@gmail.com timed out. Trying next account...`.
4. OAuth status currently reads `ok`, remaining ~251M ms, so this is not simple token expiry at post-check time.
5. Long cached contexts are strongly correlated in the current incidents: 73k-169k cache-read tokens on the most relevant Atlas/Forge timeout attempts.
6. `gpt-5.4` is not immune, but in the original Atlas action it was the fast successful fallback after `gpt-5.4-mini` timed out.

Hypothesis with highest support:

- Codex app-server/model runtime stalls under long Discord session context and partial streaming, before terminal completion. OpenClaw correctly aborts/fails over after watchdog expiry. This is runtime/provider behavior exposed by OpenClaw's Codex harness, not a Mission Control action bug.

Secondary contributors:

- Huge cached session context increases risk.
- The prior 330s outer lane-timeout bug masked/reinforced the failure; that part is already patched with 10min grace.
- Atlas had primary `gpt-5.5`, which showed repeated timeouts. Routing Atlas primary to `gpt-5.4` is a clean mitigation/test, not a proof that `gpt-5.4` can never timeout.

## Next verification

Run one long Atlas Discord turn after the route change and compare:

- model selected: should be `openai/gpt-5.4`
- whether tool events occur
- usage/cacheRead
- duration to `model.completed`
- fallback needed yes/no

Rollback if worse:

```bash
cp /home/piet/.openclaw/openclaw.json.bak-20260503T222735Z-atlas-primary-gpt54 /home/piet/.openclaw/openclaw.json
systemctl --user restart openclaw-gateway.service
```
