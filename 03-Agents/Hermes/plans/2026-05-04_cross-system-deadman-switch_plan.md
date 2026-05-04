---
title: Cross-System Deadman Switch Plan
status: proposed
created: 2026-05-04T23:45:59+02:00
owner: Hermes
mutation_level: plan_only_no_runtime_changes
scope:
  - OpenClaw cron
  - Hermes cron
  - read-only health verification
approval_required_for:
  - creating scripts
  - creating/changing OpenClaw cron jobs
  - creating/changing Hermes cron jobs
  - service restarts
---

# Cross-System Deadman Switch Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task after Piet approval. Do not execute mutations from this plan without explicit approval in the current thread.

**Goal:** Build a low-noise mutual liveness guard where OpenClaw writes a heartbeat and Hermes verifies it, alerting only when either system appears unhealthy.

**Architecture:** OpenClaw owns deterministic health evidence generation; Hermes owns independent verification and alerting. Green path produces `NO_REPLY`; failure path posts one concise alert to Piet/Hermes origin or #alerts depending on approved delivery.

**Tech Stack:** Python 3.11 stdlib, OpenClaw Gateway cron, Hermes cron, local HTTP health endpoints, JSON files under `/home/piet/.openclaw/state/health/`.

---

## Background Evidence

- OpenClaw docs: cron persists jobs in `~/.openclaw/cron/jobs.json`; isolated jobs should use `sessionTarget=isolated`; green-path silent token `NO_REPLY` suppresses delivery.
- Hermes docs: cron scripts must live under `~/.hermes/scripts/`; external scripts should be wrapped from there.
- Local services observed live on 2026-05-04: `openclaw-gateway.service`, `mission-control.service`, `hermes-gateway.service`.

## Non-Goals

- No automatic restart.
- No automatic task creation.
- No YOLO/allowlist changes.
- No direct Discord token usage.
- No mutation outside named files/jobs.

## Proposed Runtime Flow

1. OpenClaw cron runs every 30 minutes and writes `/home/piet/.openclaw/state/health/openclaw-heartbeat.json`.
2. Hermes cron runs every 35 minutes and verifies heartbeat age plus direct service health.
3. If healthy, Hermes returns exactly `NO_REPLY`.
4. If unhealthy, Hermes returns a concise alert with evidence and recommended next action.

## Files

### Create

- `/home/piet/.openclaw/scripts/cross-system-heartbeat-write.py`
- `/home/piet/.hermes/scripts/verify-openclaw-heartbeat.py`

### Modify via CLI/API only after approval

- OpenClaw cron store: `/home/piet/.openclaw/cron/jobs.json`
- Hermes cron store: managed by `hermes cron create`

### Read-only inputs

- `http://127.0.0.1:18789/health`
- `http://127.0.0.1:3000/api/health`
- `http://127.0.0.1:3000/api/tasks/snapshot`
- `systemctl --user show hermes-gateway.service ...`

---

## Task 1: Create OpenClaw heartbeat writer

**Objective:** Deterministically write a fresh OpenClaw health heartbeat without LLM interpretation.

**Files:**
- Create: `/home/piet/.openclaw/scripts/cross-system-heartbeat-write.py`

**Implementation sketch:**

```python
#!/usr/bin/env python3
from __future__ import annotations
import json, time, urllib.request
from datetime import datetime, timezone
from pathlib import Path

OUT = Path('/home/piet/.openclaw/state/health/openclaw-heartbeat.json')

def get_json(url: str, timeout: float = 5.0):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return {'ok': 200 <= r.status < 300, 'http_status': r.status, 'body': json.loads(r.read().decode())}
    except Exception as exc:
        return {'ok': False, 'error': type(exc).__name__, 'detail': str(exc)[:240]}

now = datetime.now(timezone.utc)
heartbeat = {
    'schema': 1,
    'source': 'openclaw',
    'ts': now.isoformat(),
    'tsMs': int(time.time() * 1000),
    'openclawGateway': get_json('http://127.0.0.1:18789/health'),
    'missionControlHealth': get_json('http://127.0.0.1:3000/api/health'),
    'taskSnapshot': get_json('http://127.0.0.1:3000/api/tasks/snapshot'),
}
OUT.parent.mkdir(parents=True, exist_ok=True)
tmp = OUT.with_suffix('.json.tmp')
tmp.write_text(json.dumps(heartbeat, indent=2, sort_keys=True) + '\n')
tmp.replace(OUT)
print('OPENCLAW_HEARTBEAT_OK', OUT)
```

**Verify:**

```bash
python3 /home/piet/.openclaw/scripts/cross-system-heartbeat-write.py
python3 -m json.tool /home/piet/.openclaw/state/health/openclaw-heartbeat.json >/dev/null
```

Expected: `OPENCLAW_HEARTBEAT_OK` and valid JSON.

---

## Task 2: Create Hermes verifier script

**Objective:** Verify OpenClaw heartbeat freshness and Hermes service health, returning `NO_REPLY` on green path.

**Files:**
- Create: `/home/piet/.hermes/scripts/verify-openclaw-heartbeat.py`

**Implementation sketch:**

```python
#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess, time, urllib.request
from pathlib import Path

HEARTBEAT = Path('/home/piet/.openclaw/state/health/openclaw-heartbeat.json')
MAX_AGE_SEC = 45 * 60

def get_json(url: str, timeout: float = 5.0):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return {'ok': 200 <= r.status < 300, 'http_status': r.status}
    except Exception as exc:
        return {'ok': False, 'error': type(exc).__name__, 'detail': str(exc)[:160]}

def systemd_state(unit: str):
    p = subprocess.run(['systemctl','--user','show',unit,'--property=ActiveState,SubState,MainPID,Result','--no-pager'], text=True, capture_output=True, timeout=8)
    fields = dict(line.split('=',1) for line in p.stdout.splitlines() if '=' in line)
    return {'ok': fields.get('ActiveState') == 'active', **fields}

issues = []
if not HEARTBEAT.exists():
    issues.append(f'missing heartbeat file: {HEARTBEAT}')
    age = None
else:
    data = json.loads(HEARTBEAT.read_text())
    age = int(time.time() - (data.get('tsMs', 0) / 1000))
    if age > MAX_AGE_SEC:
        issues.append(f'OpenClaw heartbeat stale: ageSec={age}')
    for key in ['openclawGateway','missionControlHealth']:
        if not (data.get(key) or {}).get('ok'):
            issues.append(f'heartbeat reports {key} unhealthy: {data.get(key)}')

live = {
  'openclawGatewayNow': get_json('http://127.0.0.1:18789/health'),
  'missionControlNow': get_json('http://127.0.0.1:3000/api/health'),
  'hermesGatewayService': systemd_state('hermes-gateway.service'),
}
for key, val in live.items():
    if not val.get('ok'):
        issues.append(f'{key} unhealthy: {val}')

if not issues:
    print('NO_REPLY')
else:
    print('🔴 Cross-System Deadman Alert')
    print('')
    for issue in issues[:8]:
        print(f'- {issue}')
    print('')
    print('Next Action: read-only inspect OpenClaw/Hermes service status and recent logs; no automatic restart performed.')
```

**Verify:**

```bash
python3 /home/piet/.hermes/scripts/verify-openclaw-heartbeat.py
```

Expected healthy path: `NO_REPLY`.

---

## Task 3: Create OpenClaw cron job

**Objective:** Schedule the heartbeat writer via OpenClaw, isolated and silent.

**Files:**
- Modify through OpenClaw CLI: `/home/piet/.openclaw/cron/jobs.json`

**Command after approval:**

```bash
/home/piet/bin/openclaw cron add \
  --name cross-system-openclaw-heartbeat \
  --cron '*/30 * * * *' \
  --tz Europe/Berlin \
  --agent system-bot \
  --session isolated \
  --message 'RUN: python3 /home/piet/.openclaw/scripts/cross-system-heartbeat-write.py
If output starts with OPENCLAW_HEARTBEAT_OK, reply exactly NO_REPLY.
If command fails, reply with first 10 lines of stdout/stderr.
STOP.' \
  --model openai-codex/gpt-5.4-mini \
  --no-deliver
```

**Verify:**

```bash
/home/piet/bin/openclaw cron list | grep -F cross-system-openclaw-heartbeat
/home/piet/bin/openclaw cron run <job-id>
/home/piet/bin/openclaw cron runs --id <job-id> --limit 3
```

Expected: run status `ok`, output `NO_REPLY`, heartbeat JSON updated.

---

## Task 4: Create Hermes cron job

**Objective:** Schedule independent verification from Hermes.

**Files:**
- Modify through Hermes CLI: `~/.hermes/cron` managed store

**Command after approval:**

```bash
hermes cron create '*/35 * * * *' \
  --name 'Verify OpenClaw Heartbeat' \
  --script verify-openclaw-heartbeat.py \
  --deliver origin
```

If CLI syntax differs, use `hermes cron create` interactively and set:

- schedule: `*/35 * * * *`
- script: `verify-openclaw-heartbeat.py`
- delivery: `origin`

**Verify:**

```bash
hermes cron list --all
hermes cron run <job-id>
```

Expected: no Discord noise on `NO_REPLY`; alert only on injected stale heartbeat test.

---

## Task 5: Failure-mode smoke tests

**Objective:** Prove alerting works without breaking production state.

**Steps:**

1. Backup heartbeat file:

```bash
cp /home/piet/.openclaw/state/health/openclaw-heartbeat.json /tmp/openclaw-heartbeat.json.bak
```

2. Temporarily write stale copy with `tsMs=0`.
3. Run Hermes verifier.
4. Restore backup immediately.

**Pass:** Verifier prints `Cross-System Deadman Alert` for stale file, then returns `NO_REPLY` after restore.

---

## Rollback

```bash
# Remove/disable OpenClaw cron job
/home/piet/bin/openclaw cron edit <job-id> --disable

# Remove/disable Hermes cron job
hermes cron pause <job-id>

# Keep scripts for forensic reuse, or remove after explicit approval
```

## Subagent Verification Addendum — Required Fixes Before Execution

A read-only Hermes subagent reviewed this plan after creation. Implementation must incorporate these corrections:

1. **Hermes CLI syntax:** use `--deliver origin`, not `--delivery origin`.
2. **OpenClaw execution semantics:** OpenClaw cron is script-first but still LLM-mediated unless migrated to a systemd/OpenClaw systemjob. Do not call it fully deterministic in receipts.
3. **Model override:** remove explicit `--model openai-codex/gpt-5.4-mini` unless a just-in-time preflight proves it is allowed and healthy. Safer default: inherit `system-bot` defaults.
4. **Failure alerting:** because OpenClaw green path uses `--no-deliver`, configure an explicit failure alert to #alerts (`1491148986109661334`) or add Hermes stale-heartbeat detection as the primary alert path.
5. **Hermes prompt contract:** Hermes cron must explicitly say: if script output is exactly `NO_REPLY`, reply exactly `NO_REPLY`; otherwise return script output unchanged; do not mutate.
6. **Safe negative smoke:** do not mutate the production heartbeat file during stale tests unless the Hermes verifier cron is paused; preferred approach is a verifier `--heartbeat-path` test override.
7. **Data minimization:** heartbeat JSON should store health booleans/totals/truncated errors, not full task snapshot bodies.
8. **Pre-change snapshots:** before creating jobs, save OpenClaw cron jobs/state backups and `hermes cron list --all` output.

## Acceptance Criteria

- OpenClaw heartbeat file updates every 30 minutes.
- Hermes verifier sees heartbeat freshness and service health.
- Green path is silent.
- Failure path produces one concise alert with evidence.
- Subagent addendum corrections are reflected in the final implementation receipt.
- No restarts, config edits, task mutations, or auto-remediation occur.
