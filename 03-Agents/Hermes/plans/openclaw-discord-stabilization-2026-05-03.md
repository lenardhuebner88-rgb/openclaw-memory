# OpenClaw Discord Stabilization Implementation Plan

> **For Hermes:** Execute this plan with `openclaw-operator` discipline. Use read-only evidence before each mutation. No YOLO/permanent allowlist changes. Stop on drift, failed backup, failed validation, failed post-check, or unclear service ownership.

**Goal:** Stabilize Piet's OpenClaw/Discord setup by upgrading from `openclaw@2026.4.29` to `openclaw@2026.5.2`, preserving the known-good model routing, and proving Discord/Gateway responsiveness with explicit quality gates.

**Architecture:** Treat `2026.5.2` as the primary remediation path because its changelog directly targets Gateway/agent hot paths, Discord startup/delivery edge cases, typing keepalive, reply startup blocking, sessions/list performance, pricing-fetch startup blocking, and plugin runtime caching. Keep `2026.4.23` only as a rollback target if `2026.5.2` fails gates. All changes are reversible via timestamped backups and npm version pinning.

**Tech Stack:** OpenClaw npm global install under `/home/piet/.npm-global`, Node `/home/piet/.openclaw/tools/node-v22.22.0/bin/node`, user systemd services `openclaw-gateway.service` and `openclaw-discord-bot.service`, config `/home/piet/.openclaw/openclaw.json`, validator `/home/piet/.openclaw/scripts/openclaw-config-validator.py`, vault SSoT `/home/piet/vault`.

---

## Known Live Facts at Plan Creation

- Current global package: `/home/piet/.npm-global/lib/node_modules/openclaw/package.json` = `2026.4.29`.
- Latest npm dist-tag: `openclaw@2026.5.2`.
- `2026.5.2` integrity: `sha512-Jz00jdV/yE0/RfAln0tVlEq1hX9DIZdc7NRZVQRpt98XINduqoua9uOc1Ty4GeYlg5c746Lhl5ZCe6A4rsOmng==`.
- Gateway service ExecStart currently points at `/home/piet/.npm-global/lib/node_modules/openclaw/dist/index.js gateway --port 18789`.
- CLI wrapper `/home/piet/bin/openclaw` points at `/home/piet/.npm-global/lib/node_modules/openclaw/dist/entry.js`.
- Gateway health currently reports `{"ok":true,"status":"live"}`.
- Active model route is intended to stay `openai/gpt-5.4-mini` via native Codex runtime / OpenAI-Codex OAuth profile.
- `openclaw version` and `openclaw commands list` can hang on `2026.4.29`; do not use them as sole preflight blockers.

---

## Quality Gates

### Gate A — Preflight Evidence Gate
Pass criteria:
- Current OpenClaw package version, npm latest, service units, config, validator, and recent logs captured.
- Config validator returns `VALIDATION_OK` before changes.
- Gateway health returns HTTP 200 with `ok=true` before changes.
- No active systemd crash-loop (`ActiveState=active`, `NRestarts` not rapidly increasing).

Fail action:
- Stop. Report live evidence and do not update.

### Gate B — Backup Gate
Pass criteria:
- Timestamped backups exist for:
  - `/home/piet/.openclaw/openclaw.json`
  - `/home/piet/.openclaw/scripts/openclaw-config-validator.py`
  - `/home/piet/.config/systemd/user/openclaw-gateway.service`
  - `/home/piet/.config/systemd/user/openclaw-discord-bot.service`
  - `/home/piet/bin/openclaw`
  - current global package metadata snapshot under `/home/piet/.openclaw/backups/`
- Backup manifest contains exact source paths and SHA256 checksums.

Fail action:
- Stop. Do not mutate.

### Gate C — Dry-Run Update Gate
Pass criteria:
- `openclaw update --tag 2026.5.2 --dry-run --json` completes or, if CLI hangs due known `2026.4.29` issue, npm-level dry-run confirms install plan without writing.
- No evidence of downgrade prompt or config incompatibility.

Fail action:
- Use direct npm update path only if dry-run failure is attributable to known CLI hang and npm package metadata is valid. Otherwise stop.

### Gate D — Install Gate
Pass criteria:
- `openclaw@2026.5.2` installed globally under `/home/piet/.npm-global`.
- `package.json` after install reads `2026.5.2`.
- CLI wrapper still points to the global install and Node v22.22.0.
- `npm ls -g openclaw --depth=0` reports `openclaw@2026.5.2`.

Fail action:
- Roll back npm global package to `openclaw@2026.4.29` or backup package snapshot if npm rollback fails.

### Gate E — Config/Validator Gate
Pass criteria:
- `/home/piet/.openclaw/openclaw.json` still contains:
  - `channels.discord.streaming.mode = partial`
  - `agents.defaults.model.primary = openai/gpt-5.4-mini`
  - `agents.list[system-bot].model.primary = openai/gpt-5.4-mini`
  - no `minimax/*` in active default/system-bot fallback routes
- Validator returns `VALIDATION_OK`.
- Config-Guard log shows no rollback after update.

Fail action:
- Restore config backup and/or reapply validator-compatible model routing, then validate. If still failing, roll back package.

### Gate F — Restart/Readiness Gate
Pass criteria:
- `systemctl --user restart openclaw-gateway.service` completes.
- Gateway health returns `ok=true` within 90 seconds.
- Journal contains ready signal and no fatal plugin/config errors.
- `openclaw-gateway.service` remains active after 120 seconds.

Fail action:
- Collect `journalctl --user -u openclaw-gateway.service -n 200`.
- Roll back to `2026.4.29` unless failure is a small, obvious config compatibility issue with safe patch.

### Gate G — Model/Agent Gate
Pass criteria:
- `openclaw agent --agent system-bot --message 'Smoketest: Antworte exakt mit OK.' --json` succeeds.
- Winner is `openai/gpt-5.4-mini` or approved fallback `openai/gpt-5.4`/`openai/gpt-5.5`.
- No `minimax not found`, `openrouter provider not found`, `fetch-timeout`, or `FailoverError` in post-update logs.

Fail action:
- Preserve logs and result JSON; inspect provider resolution before further config changes.

### Gate H — Discord UX Gate
Pass criteria:
- Discord bot service remains active.
- Gateway Discord logs show startup/connected/ready, not reconnect loops.
- In Discord, a test prompt shows visible typing/partial feedback or final reply without silent stall.
- No new `InteractionEventListener timeout`, `listener timeout`, `Discord gateway unresponsive`, or stuck `processing` indicators in logs.

Fail action:
- Inspect Discord channel/account status and recent Gateway logs; do not broadly restart both services unless evidence points to Discord transport state.

### Gate I — 10-Minute Soak Gate
Pass criteria:
- 20 health iterations over 10 minutes: all HTTP 200 and `ok=true`.
- Error count zero for critical patterns:
  - `minimax not found`
  - `Model provider openrouter not found`
  - `fetch-timeout`
  - `FailoverError`
  - `InteractionEventListener`
  - `listener timeout`
  - `unhandledRejection`
  - `fatal`
- `eventLoopDelayMaxMs` not repeatedly above 6000ms under idle/light load. One isolated warning is acceptable if no user-visible stall.
- `openclaw version` or `openclaw update status --json` no longer hangs; if still hanging, classify as residual CLI bug, not service failure, only if Gateway/Discord gates pass.

Fail action:
- Keep system on updated version only if user-facing Discord is improved and failures are non-critical; otherwise execute rollback.

---

## Rollback Strategy

Primary rollback target: `openclaw@2026.4.29`.

Secondary rollback target: `openclaw@2026.4.23`, only if:
- `2026.5.2` fails critical gates, and
- `2026.4.29` remains known-bad for Discord latency, and
- config compatibility with `2026.4.23` has been checked.

Rollback gates:
- Install target version.
- Restore config/validator backups if needed.
- Restart Gateway.
- Re-run Gates E, F, G, I.

Rollback command candidates:
```bash
npm install -g openclaw@2026.4.29 --prefix /home/piet/.npm-global
# or, only if explicitly selected:
npm install -g openclaw@2026.4.23 --prefix /home/piet/.npm-global
systemctl --user daemon-reload
systemctl --user restart openclaw-gateway.service
```

---

## Execution Tasks

### Task 1: Capture preflight snapshot

**Objective:** Establish exact current state before mutation.

**Commands:**
```bash
TS=$(date +%Y%m%d-%H%M%S)
mkdir -p /home/piet/.openclaw/backups/HERMES-openclaw-20260503-stabilization-$TS
node -e "const p=require('/home/piet/.npm-global/lib/node_modules/openclaw/package.json'); console.log(JSON.stringify({name:p.name,version:p.version},null,2))"
npm view openclaw version dist-tags --json
systemctl --user show openclaw-gateway.service openclaw-discord-bot.service -p ActiveState -p SubState -p MainPID -p NRestarts -p ExecMainStatus -p MemoryCurrent
curl -fsS http://127.0.0.1:18789/health
python3 /home/piet/.openclaw/scripts/openclaw-config-validator.py
journalctl --user -u openclaw-gateway.service -u openclaw-discord-bot.service --since '30 min ago' --no-pager | tail -n 200
```

**Expected:** Current version `2026.4.29`, latest `2026.5.2`, services active, health live, validator OK.

---

### Task 2: Create backup manifest

**Objective:** Make rollback possible before touching package/config/services.

**Commands:**
```bash
TS=$(date +%Y%m%d-%H%M%S)
B=/home/piet/.openclaw/backups/HERMES-openclaw-20260503-stabilization-$TS
mkdir -p "$B"
cp -a /home/piet/.openclaw/openclaw.json "$B/openclaw.json"
cp -a /home/piet/.openclaw/scripts/openclaw-config-validator.py "$B/openclaw-config-validator.py"
cp -a /home/piet/.config/systemd/user/openclaw-gateway.service "$B/openclaw-gateway.service"
cp -a /home/piet/.config/systemd/user/openclaw-discord-bot.service "$B/openclaw-discord-bot.service"
cp -a /home/piet/bin/openclaw "$B/openclaw-wrapper"
node -e "const p=require('/home/piet/.npm-global/lib/node_modules/openclaw/package.json'); console.log(JSON.stringify(p,null,2))" > "$B/openclaw-package-before.json"
sha256sum "$B"/* > "$B/SHA256SUMS"
printf '%s\n' "$B" > /home/piet/.openclaw/backups/HERMES-openclaw-20260503-stabilization-LATEST
```

**Expected:** Backup dir exists and `sha256sum -c SHA256SUMS` passes.

---

### Task 3: Run update dry-run

**Objective:** Prefer OpenClaw's own updater if responsive.

**Commands:**
```bash
timeout 180 openclaw update --tag 2026.5.2 --dry-run --json
```

**Expected:** JSON preview and no writes. If it hangs like `openclaw version`, document and use npm direct install path.

---

### Task 4: Install `openclaw@2026.5.2`

**Objective:** Upgrade package without changing config semantics.

**Preferred command:**
```bash
timeout 1800 openclaw update --tag 2026.5.2 --yes --no-restart --json
```

**Fallback command if updater hangs:**
```bash
npm install -g openclaw@2026.5.2 --prefix /home/piet/.npm-global
```

**Verification:**
```bash
node -e "const p=require('/home/piet/.npm-global/lib/node_modules/openclaw/package.json'); console.log(p.version)"
npm ls -g openclaw --depth=0 --prefix /home/piet/.npm-global
```

**Expected:** `2026.5.2`.

---

### Task 5: Validate config and preserve routing

**Objective:** Ensure update did not undo stable model routing.

**Commands:**
```bash
python3 /home/piet/.openclaw/scripts/openclaw-config-validator.py
python3 - <<'PY'
import json
p='/home/piet/.openclaw/openclaw.json'
d=json.load(open(p))
print('streaming=', d.get('channels',{}).get('discord',{}).get('streaming',{}).get('mode'))
print('default.primary=', d.get('agents',{}).get('defaults',{}).get('model',{}).get('primary'))
for a in d.get('agents',{}).get('list',[]):
    if a.get('id')=='system-bot':
        print('system-bot.primary=', a.get('model',{}).get('primary'))
        print('system-bot.fallbacks=', a.get('model',{}).get('fallbacks'))
PY
```

**Expected:** Validator OK, streaming `partial`, primary `openai/gpt-5.4-mini`.

---

### Task 6: Restart Gateway and verify readiness

**Objective:** Load the new package in the managed service.

**Commands:**
```bash
systemctl --user daemon-reload
systemctl --user restart openclaw-gateway.service
for i in $(seq 1 90); do
  if curl -fsS http://127.0.0.1:18789/health | grep -q '"ok":true'; then echo READY; break; fi
  sleep 1
done
systemctl --user show openclaw-gateway.service -p ActiveState -p SubState -p MainPID -p NRestarts -p ExecMainStatus -p MemoryCurrent
journalctl --user -u openclaw-gateway.service --since '5 min ago' --no-pager | tail -n 200
```

**Expected:** READY within 90s, service active, no fatal config/plugin error.

---

### Task 7: Verify Discord service and Gateway channel state

**Objective:** Confirm Discord transport did not regress.

**Commands:**
```bash
systemctl --user show openclaw-discord-bot.service -p ActiveState -p SubState -p MainPID -p NRestarts -p ExecMainStatus -p MemoryCurrent
journalctl --user -u openclaw-gateway.service -u openclaw-discord-bot.service --since '10 min ago' --no-pager | egrep -i 'discord|gateway|ready|connected|error|warn|timeout|interaction|typing|listener' | tail -n 200
```

**Expected:** Discord bot active; no reconnect loop or listener timeout.

---

### Task 8: Run system-bot model smoketest

**Objective:** Prove model routing and agent runtime still work.

**Command:**
```bash
timeout 180 openclaw agent --agent system-bot --message 'Smoketest: Antworte exakt mit OK.' --json | tee /tmp/openclaw-system-bot-smoketest-20260503.json
```

**Expected:** `ok`/completed, text `OK`, winner `openai/gpt-5.4-mini` or approved OpenAI fallback, no provider-not-found.

---

### Task 9: Run 10-minute soak

**Objective:** Prove stability under light repeated health checks.

**Command:**
```bash
START=$(date --iso-8601=seconds)
for i in $(seq 1 20); do
  printf '%02d %s ' "$i" "$(date +%H:%M:%S)"
  curl -fsS http://127.0.0.1:18789/health || true
  echo
  sleep 30
done
END=$(date --iso-8601=seconds)
echo "START=$START END=$END"
journalctl --user -u openclaw-gateway.service -u openclaw-discord-bot.service --since "$START" --until "$END" --no-pager | egrep -i 'minimax not found|provider openrouter not found|fetch-timeout|FailoverError|InteractionEventListener|listener timeout|unhandledRejection|fatal|eventLoopDelayMaxMs|error' || true
```

**Expected:** 20/20 health OK, zero critical errors, no repeated high event-loop warnings.

---

### Task 10: Operator Discord UX test

**Objective:** Validate the user-visible issue from the actual Discord surface.

**Procedure:**
1. Piet sends a short test prompt to the OpenClaw Discord bot/channel.
2. Observe whether typing/partial response appears quickly.
3. Capture timestamp and final latency.
4. Check logs for corresponding run.

**Pass:** visible progress and final reply; no silent 60s+ wait; no stuck processing.

---

### Task 11: Final report and cleanup

**Objective:** Leave system documented and rollback-ready.

**Actions:**
- Record final version, health, service PIDs, smoke result, soak result, critical log count.
- Keep backup path in report.
- If all gates pass, no rollback.
- If critical gate fails, execute rollback plan and report both failure evidence and rollback verification.

---

## Decision Matrix

| Result | Action |
|---|---|
| `2026.5.2` passes all gates | Keep `2026.5.2`; monitor event-loop delay only. |
| `2026.5.2` passes service gates but CLI still hangs | Keep `2026.5.2`; classify CLI as residual issue and investigate separately. |
| `2026.5.2` fails config/validator | Restore config/validator backups; retry once; if still failing, roll back `2026.4.29`. |
| `2026.5.2` fails Gateway readiness | Roll back `2026.4.29`; only consider `2026.4.23` if `2026.4.29` remains unstable. |
| `2026.5.2` fails Discord UX but Gateway/model stable | Inspect Discord channel/plugin state before package rollback; do not broad-remediate blindly. |

---

## Explicit Non-Goals

- Do not change Discord tokens.
- Do not enable YOLO mode.
- Do not add permanent command allowlists.
- Do not migrate vault SSoT away from `/home/piet/vault`.
- Do not change model routing away from `openai/gpt-5.4-mini` unless a gate failure proves it is needed.
- Do not roll back to `2026.4.23` before trying the official latest `2026.5.2` path.
