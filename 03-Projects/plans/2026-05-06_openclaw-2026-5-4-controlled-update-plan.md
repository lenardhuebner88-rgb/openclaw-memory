# OpenClaw 2026.5.4 Controlled Update Plan

Status: documented / not executed
Owner: Atlas
Date: 2026-05-06

## Current State

- Running OpenClaw: `2026.5.3-1`
- Target stable update: `2026.5.4`
- Do not use: `2026.5.5-beta.1`
- Gateway: systemd managed, reachable on `127.0.0.1:18789`
- Mission Control: reachable on `127.0.0.1:3000`
- MC health before update: `degraded` because of one known blocked/stale T15 task
- Board/Dispatch baseline before update:
  - board issueCount: `0`
  - dispatch consistencyIssues: `0`
- Known reason for T15 blocker: active runtime package lacks `tool-result-shadow`; 2026.5.4 package contains the relevant marker/components.

## Official Update Dry-Run

Command used:

```bash
openclaw update --tag 2026.5.4 --dry-run --json
```

Dry-run result summary:

- install kind: package
- mode: npm
- currentVersion: `2026.5.3-1`
- targetVersion: `2026.5.4`
- downgradeRisk: false
- restart: true
- planned actions:
  - Run global package manager update with spec `openclaw@2026.5.4`
  - Run plugin update sync after core update
  - Refresh shell completion cache if needed
  - Restart gateway service and run doctor checks

## Local Scripts / Drop-ins To Account For

Relevant scripts:

- `/home/piet/.openclaw/scripts/openclaw-config-guard.sh`
- `/home/piet/.openclaw/scripts/openclaw-config-validator.py`
- `/home/piet/.openclaw/scripts/gateway-port-guard.sh`
- `/home/piet/.openclaw/scripts/apply-mcp-recovery-patch.py`
- `/home/piet/.openclaw/scripts/apply-openclaw-response-hardening.py`
- `/home/piet/.openclaw/scripts/apply-embedded-lane-grace-patch.py`
- `/home/piet/.openclaw/scripts/atlas-orchestrator-budget-proof.mjs`
- `/home/piet/.openclaw/scripts/workspace-backup.py`
- `/home/piet/.openclaw/scripts/validate-models.py`
- `/home/piet/.openclaw/scripts/mc-pending-pickup-smoke.sh`
- `/home/piet/.openclaw/scripts/mc-watchdog.sh`
- `/home/piet/.openclaw/scripts/mission-control-reload.sh`

Active Gateway drop-in concerns:

- `OPENCLAW_TOOL_RESULT_SUMMARY_MODE=shadow`
- `NODE_OPTIONS=--max-old-space-size=4096`
- Memory caps: `MemoryHigh=5G`, `MemoryMax=6G`, `MemorySwapMax=2G`
- `gateway-port-guard.sh`
- `apply-mcp-recovery-patch.py`
- `apply-openclaw-response-hardening.py`
- `apply-embedded-lane-grace-patch.py`
- MCP child teardown
- Bonjour disabled
- output caps

## Go / No-Go Criteria

Go only if:

- no active operator-critical run is in progress
- no active worker besides the known blocked T15 condition
- short Gateway interruption is acceptable
- target remains stable `2026.5.4`
- dry-run still reports no downgrade risk

No-go if:

- Gateway/MC is already failing beyond the known T15 degraded state
- config validation fails
- dry-run target changes to beta/dev unexpectedly
- there is an active lock conflict or ambiguous worker/session state

## Pre-Update Backup

Create a timestamped backup directory, e.g.:

```bash
BACKUP="/home/piet/.openclaw/backups/openclaw-update-2026-5-4-$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$BACKUP"
cp -a /home/piet/.openclaw/openclaw.json "$BACKUP/openclaw.json"
systemctl --user cat openclaw-gateway > "$BACKUP/openclaw-gateway.systemd.txt"
cp -a /home/piet/.config/systemd/user/openclaw-gateway.service.d "$BACKUP/openclaw-gateway.service.d"
cp -a /home/piet/.openclaw/state/mission-control/data "$BACKUP/mission-control-data"
cp -a /home/piet/.npm-global/lib/node_modules/openclaw "$BACKUP/openclaw-package-2026.5.3-1"
openclaw status > "$BACKUP/openclaw-status.before.txt"
curl -fsS http://127.0.0.1:18789/health > "$BACKUP/gateway-health.before.json"
curl -fsS http://127.0.0.1:3000/api/health > "$BACKUP/mc-health.before.json"
curl -fsS 'http://127.0.0.1:3000/api/ops/worker-reconciler-proof?limit=20' > "$BACKUP/worker-proof.before.json"
curl -fsS 'http://127.0.0.1:3000/api/ops/pickup-proof?limit=20' > "$BACKUP/pickup-proof.before.json"
```

## Preflight Gates

Run before update:

```bash
openclaw update --tag 2026.5.4 --dry-run --json
/home/piet/.openclaw/scripts/openclaw-config-guard.sh
/home/piet/.openclaw/scripts/gateway-port-guard.sh
curl -fsS http://127.0.0.1:18789/health
curl -fsS http://127.0.0.1:3000/api/health
curl -fsS 'http://127.0.0.1:3000/api/ops/worker-reconciler-proof?limit=20'
curl -fsS 'http://127.0.0.1:3000/api/ops/pickup-proof?limit=20'
```

Expected before update:

- Gateway health reachable
- MC may be `degraded` only due to known T15 blocked/stale task
- board issueCount remains `0`
- dispatch consistencyIssues remains `0`
- worker/pickup proofs remain ok/pass

## Update Command

Preferred command:

```bash
openclaw update --tag 2026.5.4 --yes
```

Do not use:

- `openclaw update --channel beta`
- `openclaw update --tag 2026.5.5-beta.1`
- manual `npm update` bypassing OpenClaw updater

## Post-Update Gates

Immediately after update:

```bash
openclaw status
curl -fsS http://127.0.0.1:18789/health
curl -fsS http://127.0.0.1:3000/api/health
curl -fsS 'http://127.0.0.1:3000/api/ops/worker-reconciler-proof?limit=20'
curl -fsS 'http://127.0.0.1:3000/api/ops/pickup-proof?limit=20'
/home/piet/.openclaw/scripts/validate-models.py
node /home/piet/.openclaw/scripts/atlas-orchestrator-budget-proof.mjs
grep -R "tool-result-shadow" -n /home/piet/.npm-global/lib/node_modules/openclaw/dist | head -20
journalctl --user -u openclaw-gateway -n 200 --no-pager
```

Expected after update:

- `openclaw status` reports Gateway/app `2026.5.4`
- Gateway health reachable
- MC still no board/dispatch issues
- If MC remains degraded, it should still be only the known T15 blocked/stale state until T15 is rerun/closed
- `tool-result-shadow` marker exists in active package
- Gateway start patches do not fail fatally

## T15 Follow-Up

After update and health gates:

- rerun or re-dispatch the controlled shadow telemetry smoke
- prove `[tool-result-shadow]` emission with synthetic non-secret large tool result
- close or unblock T15 based on evidence
- then re-check MC health for full green

## Rollback Plan

If update fails or Gateway does not become healthy:

1. Save evidence:

```bash
journalctl --user -u openclaw-gateway -n 300 --no-pager
openclaw status
curl -fsS http://127.0.0.1:18789/health || true
```

2. Avoid blind repeated restarts.

3. Roll back package:

```bash
openclaw update --tag 2026.5.3-1 --yes
```

4. If package rollback is insufficient, restore from backup:

- `openclaw.json`
- `openclaw-gateway.service.d/`
- previous package tree if needed

5. Restart/verify Gateway once and rerun health gates.

## Recommendation

Proceed with the update only as a controlled maintenance step. The update is worth doing because it likely resolves the T15 runtime mismatch and includes relevant Gateway, tool-result, session, MCP, and channel fixes. The critical risk is interaction with local Gateway start patches, so backup and post-update verification are mandatory.
