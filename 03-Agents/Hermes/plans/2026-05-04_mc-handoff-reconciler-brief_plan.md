---
title: Mission Control Handoff Reconciler and Hermes Brief Plan
status: proposed
created: 2026-05-04T23:45:59+02:00
owner: Hermes
mutation_level: plan_only_no_runtime_changes
scope:
  - Mission Control read-only hygiene report
  - Hermes review brief
approval_required_for:
  - creating scripts
  - creating/changing OpenClaw cron jobs
  - creating/changing Hermes cron jobs
---

# Mission Control Handoff Reconciler + Hermes Brief Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task after Piet approval. Do not execute mutations from this plan without explicit approval in the current thread.

**Goal:** Surface actionable Mission Control backlog and handoff hygiene issues twice daily without automatically changing tasks.

**Architecture:** OpenClaw generates a deterministic read-only JSON report from Mission Control task APIs and local state. Hermes turns the report into a concise human-facing brief with top actions and explicit `No mutation performed` footer.

**Tech Stack:** Python 3.11 stdlib, Mission Control local REST API, OpenClaw cron, Hermes cron, JSON under `/home/piet/.openclaw/state/reports/`.

---

## Background Evidence

- Mission Control snapshot on 2026-05-04: `total=1002`, `open=213`, `done=789`, `staleInProgress=0`.
- Open tasks can be stale even when `staleInProgress=0`: e.g. no owner, no recent receipt, duplicated task, pending pickup not progressing.
- Piet wants operationally useful automation, not generic health noise.

## Non-Goals

- No automatic task close/archive/assign.
- No automatic dispatch/retry.
- No Atlas WIP mutation.
- No task creation.
- No direct Discord API calls outside approved cron delivery.

## Proposed Runtime Flow

1. OpenClaw cron runs 11:30 and 17:30 Europe/Berlin and writes `mc-handoff-reconciler-latest.json`.
2. Hermes cron runs 11:40 and 17:40, reads report, emits concise brief only when actionable issues exist.
3. If no issues: `NO_REPLY`.
4. If issues: top 5 suggested human actions, no mutation.

## Files

### Create

- `/home/piet/.openclaw/scripts/mc-handoff-reconciler.py`
- `/home/piet/.hermes/scripts/hermes-mc-handoff-brief.py`

### Read-only inputs

- `http://127.0.0.1:3000/api/tasks/snapshot`
- `http://127.0.0.1:3000/api/tasks` if available
- local Mission Control data fallback under `/home/piet/.openclaw/state/mission-control/data`
- `/home/piet/.openclaw/cron/jobs-state.json` optional context

---

## Task 1: Discover Mission Control task list endpoint safely

**Objective:** Determine the read-only endpoint for task listing without broad scans.

**Commands:**

```bash
curl -s -o /tmp/mc_tasks_snapshot.json -w '%{http_code}\n' http://127.0.0.1:3000/api/tasks/snapshot
curl -s -o /tmp/mc_tasks_list.json -w '%{http_code}\n' 'http://127.0.0.1:3000/api/tasks?limit=500'
```

**Pass:** snapshot returns 200; task list either returns JSON 200 or plan falls back to local data path.

**No mutation.**

---

## Task 2: Create OpenClaw reconciler script

**Objective:** Produce a deterministic JSON report of backlog/handoff hygiene issues.

**Files:**
- Create: `/home/piet/.openclaw/scripts/mc-handoff-reconciler.py`

**Implementation sketch:**

```python
#!/usr/bin/env python3
from __future__ import annotations
import json, time, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path

OUT_DIR = Path('/home/piet/.openclaw/state/reports')
MAX_TASKS = 500
STALE_OPEN_DAYS = 14
RECEIPT_STALE_HOURS = 18

def get_json(url):
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            return {'ok': 200 <= r.status < 300, 'http_status': r.status, 'body': json.loads(r.read().decode())}
    except Exception as exc:
        return {'ok': False, 'error': type(exc).__name__, 'detail': str(exc)[:240]}

def parse_ms(task, *keys):
    for key in keys:
        val = task.get(key)
        if isinstance(val, (int, float)):
            return int(val)
    return None

def task_list():
    # Adjust endpoint if local MC uses a different list path.
    url = f'http://127.0.0.1:3000/api/tasks?{urllib.parse.urlencode({"limit": MAX_TASKS})}'
    res = get_json(url)
    if not res.get('ok'):
        return res, []
    body = res.get('body')
    if isinstance(body, list):
        return res, body
    if isinstance(body, dict):
        return res, body.get('tasks') or body.get('items') or []
    return res, []

now_ms = int(time.time() * 1000)
list_res, tasks = task_list()
issues = []
agent_wip = {}
seen_titles = {}
for t in tasks:
    status = str(t.get('status') or '').lower()
    title = str(t.get('title') or '').strip()
    owner = t.get('agentId') or t.get('assignee') or t.get('owner')
    updated = parse_ms(t, 'updatedAtMs', 'updated_at_ms', 'updatedAt')
    created = parse_ms(t, 'createdAtMs', 'created_at_ms', 'createdAt')
    age_days = None if not created else round((now_ms-created)/86400000, 1)
    idle_hours = None if not updated else round((now_ms-updated)/3600000, 1)

    if status in {'open','todo','draft','queued','assigned','pending','in_progress'}:
        if owner:
            agent_wip[owner] = agent_wip.get(owner, 0) + 1
        if not owner:
            issues.append({'kind':'open_no_owner','id':t.get('id'),'title':title,'status':status,'ageDays':age_days})
        if age_days is not None and age_days > STALE_OPEN_DAYS:
            issues.append({'kind':'old_open_task','id':t.get('id'),'title':title,'status':status,'ageDays':age_days,'owner':owner})
        if idle_hours is not None and idle_hours > RECEIPT_STALE_HOURS and status in {'assigned','in_progress','pending'}:
            issues.append({'kind':'handoff_idle','id':t.get('id'),'title':title,'status':status,'idleHours':idle_hours,'owner':owner})

    key = title.lower()[:120]
    if key:
        seen_titles.setdefault(key, []).append(t.get('id'))

for title_key, ids in seen_titles.items():
    if len(ids) > 1:
        issues.append({'kind':'possible_duplicate_title','titleKey':title_key,'ids':ids[:8],'count':len(ids)})

snapshot = get_json('http://127.0.0.1:3000/api/tasks/snapshot')
now = datetime.now(timezone.utc)
report = {
  'schema': 1,
  'kind': 'mc-handoff-reconciler',
  'generatedAt': now.isoformat(),
  'taskListOk': list_res.get('ok'),
  'taskListStatus': list_res.get('http_status') or list_res.get('error'),
  'taskCountLoaded': len(tasks),
  'snapshot': snapshot,
  'agentWip': agent_wip,
  'issues': issues[:100],
  'issueCounts': {k: sum(1 for i in issues if i.get('kind') == k) for k in sorted({i.get('kind') for i in issues})},
}
OUT_DIR.mkdir(parents=True, exist_ok=True)
out = OUT_DIR / f'mc-handoff-reconciler-{now.date().isoformat()}.json'
out.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
(OUT_DIR / 'mc-handoff-reconciler-latest.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
print('MC_HANDOFF_RECONCILER_OK', out, 'issues=', len(issues))
```

**Verify:**

```bash
python3 /home/piet/.openclaw/scripts/mc-handoff-reconciler.py
python3 -m json.tool /home/piet/.openclaw/state/reports/mc-handoff-reconciler-latest.json >/dev/null
```

Expected: JSON report with `issueCounts`, `agentWip`, `taskCountLoaded`.

---

## Task 3: Create Hermes handoff brief script

**Objective:** Convert JSON issues into a concise operator brief; remain silent if there are no actionable findings.

**Files:**
- Create: `/home/piet/.hermes/scripts/hermes-mc-handoff-brief.py`

**Implementation sketch:**

```python
#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

SRC = Path('/home/piet/.openclaw/state/reports/mc-handoff-reconciler-latest.json')
if not SRC.exists():
    raise SystemExit(f'ERROR: missing report: {SRC}')
r = json.loads(SRC.read_text())
issues = r.get('issues') or []
if not issues:
    print('NO_REPLY')
    raise SystemExit(0)

priority = {'handoff_idle': 1, 'open_no_owner': 2, 'old_open_task': 3, 'possible_duplicate_title': 4}
issues = sorted(issues, key=lambda x: priority.get(x.get('kind'), 99))[:5]
print('MISSION CONTROL HANDOFF BRIEF')
print('')
print(f"Generated: {r.get('generatedAt')}")
print(f"Loaded tasks: {r.get('taskCountLoaded')} | Issue counts: {r.get('issueCounts')}")
print('')
print('Top actionable items:')
for idx, i in enumerate(issues, 1):
    print(f"{idx}. {i.get('kind')}: {i.get('title') or i.get('titleKey')} id={i.get('id') or i.get('ids')} owner={i.get('owner')} ageDays={i.get('ageDays')} idleHours={i.get('idleHours')}")
print('')
print(f"Agent WIP: {r.get('agentWip')}")
print('')
print('Suggested action: Review/merge/archive manually in Mission Control. No mutation performed.')
```

**Verify:**

```bash
python3 /home/piet/.hermes/scripts/hermes-mc-handoff-brief.py
```

Expected: `NO_REPLY` if no issues, otherwise concise brief.

---

## Task 4: Create OpenClaw reconciler cron

**Objective:** Schedule read-only report generation twice daily.

**Command after approval:**

```bash
/home/piet/bin/openclaw cron add \
  --name mc-handoff-reconciler \
  --cron '30 11,17 * * *' \
  --tz Europe/Berlin \
  --agent system-bot \
  --session isolated \
  --message 'RUN: python3 /home/piet/.openclaw/scripts/mc-handoff-reconciler.py
If output starts with MC_HANDOFF_RECONCILER_OK, reply exactly NO_REPLY.
If command fails, reply with first 20 lines of stdout/stderr.
STOP.' \
  --model openai-codex/gpt-5.4-mini \
  --no-deliver
```

**Verify:**

```bash
/home/piet/bin/openclaw cron run <job-id>
/home/piet/bin/openclaw cron runs --id <job-id> --limit 3
```

Expected: report JSON written, cron `ok`, no delivery on green path.

---

## Task 5: Create Hermes brief cron

**Objective:** Schedule the human-facing brief after report generation.

**Command after approval:**

```bash
hermes cron create '40 11,17 * * *' \
  --name 'Hermes MC Handoff Brief' \
  --script hermes-mc-handoff-brief.py \
  --deliver origin
```

**Verify:**

```bash
hermes cron list --all
hermes cron run <job-id>
```

Expected: origin receives brief only if issues exist.

---

## Rollback

```bash
/home/piet/bin/openclaw cron edit <openclaw-job-id> --disable
hermes cron pause <hermes-job-id>
```

Scripts can remain inert for manual diagnostics, or be removed after explicit approval.

## Subagent Verification Addendum — Required Fixes Before Execution

A read-only Hermes subagent reviewed this plan after creation. Implementation must incorporate these corrections:

1. **Hermes CLI syntax:** use `--deliver origin`, not `--delivery origin`.
2. **Hermes prompt contract:** if script output is exactly `NO_REPLY`, reply exactly `NO_REPLY`; otherwise return the brief unchanged; do not mutate tasks/OpenClaw/Hermes/configs/crons/services.
3. **OpenClaw execution semantics:** report generation scheduled through OpenClaw cron is script-first but LLM-mediated unless migrated to a systemjob.
4. **Mission Control fallback:** implement real local-data fallback with shape validation, or remove fallback claim.
5. **Task load cap:** cap loaded tasks after API response even if `/api/tasks?limit=` is ignored.
6. **Timestamp parsing:** parse numeric ms and ISO strings; prefer `lastActivityAt` for idle/handoff detection.
7. **Duplicate noise:** restrict duplicate detection to active/non-terminal tasks.
8. **Model override:** remove explicit `--model openai-codex/gpt-5.4-mini` unless a just-in-time preflight proves allowlist/runtime health. Safer default: inherit defaults.
9. **Timeout/failure alert:** set OpenClaw `timeoutSeconds≈120` and configure failure alert/cooldown to #alerts (`1491148986109661334`) or add Hermes stale/missing report detection.
10. **Verification writes:** manual script verification writes report files; treat that as an approved mutation during implementation.

## Acceptance Criteria

- Twice-daily report detects taskboard/handoff hygiene issues.
- Hermes brief is concise and action-oriented.
- Green path is silent.
- Subagent addendum corrections are reflected in the final implementation receipt.
- No task mutations, dispatches, retries, closes, archives, or assignments occur.
