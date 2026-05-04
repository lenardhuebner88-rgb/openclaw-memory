---
title: Nightly Incident Distiller to Hermes Learning Packet Plan
status: proposed
created: 2026-05-04T23:45:59+02:00
owner: Hermes
mutation_level: plan_only_no_runtime_changes
scope:
  - OpenClaw read-only incident evidence collection
  - Hermes pending learning packet generation
approval_required_for:
  - creating scripts
  - creating/changing OpenClaw cron jobs
  - creating/changing Hermes cron jobs
---

# Nightly Incident Distiller → Hermes Learning Packet Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task after Piet approval. Do not execute mutations from this plan without explicit approval in the current thread.

**Goal:** Turn overnight OpenClaw runtime evidence into a reviewable Hermes learning packet without automatically changing memory, skills, configs, or tasks.

**Architecture:** OpenClaw produces a deterministic JSON evidence pack from logs/Mission Control/session state. Hermes reads that pack and writes a Markdown `pending_validation` learning packet in the canonical vault for human review.

**Tech Stack:** Python 3.11 stdlib, journalctl, local Mission Control/OpenClaw HTTP endpoints, Hermes cron, OpenClaw cron, canonical vault `/home/piet/vault`.

---

## Background Evidence

- Piet routinely asks for night-log timeout analysis.
- Hermes governance requires lessons to go through `/home/piet/vault/03-Agents/Hermes/learning-packets/` and not be stuffed directly into memory.
- OpenClaw docs recommend cron run history and failure state as durable evidence.

## Non-Goals

- No automatic memory writes.
- No automatic skill patches.
- No automatic task creation.
- No config edits/restarts.
- No raw secret/token capture.

## Proposed Runtime Flow

1. OpenClaw cron runs at 05:30 Europe/Berlin and writes JSON evidence under `/home/piet/.openclaw/state/reports/`.
2. Hermes cron runs at 06:00, reads the latest JSON, writes Markdown packet to `/home/piet/vault/03-Agents/Hermes/learning-packets/pending/`.
3. Hermes returns a concise summary and link/path. No durable memory change happens automatically.

## Files

### Create

- `/home/piet/.openclaw/scripts/nightly-incident-evidence-pack.py`
- `/home/piet/.hermes/scripts/hermes-nightly-learning-packet.py`
- Output dir: `/home/piet/.openclaw/state/reports/`
- Output dir: `/home/piet/vault/03-Agents/Hermes/learning-packets/pending/`

### Read-only inputs

- `journalctl --user -u openclaw-gateway.service --since '24 hours ago'`
- `/home/piet/.openclaw/cron/jobs-state.json`
- `/home/piet/.openclaw/cron/jobs.json`
- `http://127.0.0.1:3000/api/tasks/snapshot`
- `http://127.0.0.1:18789/health`

---

## Task 1: Create OpenClaw evidence pack script

**Objective:** Collect minimal structured overnight evidence without LLM interpretation.

**Files:**
- Create: `/home/piet/.openclaw/scripts/nightly-incident-evidence-pack.py`

**Implementation sketch:**

```python
#!/usr/bin/env python3
from __future__ import annotations
import json, re, subprocess, urllib.request
from datetime import datetime, timezone
from pathlib import Path

OUT_DIR = Path('/home/piet/.openclaw/state/reports')
JOBS = Path('/home/piet/.openclaw/cron/jobs.json')
STATE = Path('/home/piet/.openclaw/cron/jobs-state.json')
WINDOW = '24 hours ago'
PATTERNS = {
  'codex_timeout': re.compile(r'LLM request timed out|timed out', re.I),
  'candidate_failed': re.compile(r'candidate_failed|candidate failed|failover', re.I),
  'allowlist_rejection': re.compile(r'payload\.model .* rejected by agents\.defaults\.models allowlist', re.I),
  'provider_not_found': re.compile(r'provider.*not found|provider_not_found', re.I),
  'discord_delivery_error': re.compile(r'discord.*(failed|error|429|401)', re.I),
}

def get_json(url):
    try:
        with urllib.request.urlopen(url, timeout=8) as r:
            return {'ok': 200 <= r.status < 300, 'http_status': r.status, 'body': json.loads(r.read().decode())}
    except Exception as exc:
        return {'ok': False, 'error': type(exc).__name__, 'detail': str(exc)[:240]}

def journal_lines():
    p = subprocess.run(['journalctl','--user','-u','openclaw-gateway.service','--since',WINDOW,'--no-pager'], text=True, capture_output=True, timeout=30)
    return p.stdout.splitlines()[-5000:]

lines = journal_lines()
counts = {k: 0 for k in PATTERNS}
samples = {k: [] for k in PATTERNS}
for line in lines:
    for k, pat in PATTERNS.items():
        if pat.search(line):
            counts[k] += 1
            if len(samples[k]) < 8:
                samples[k].append(line[-500:])

jobs = json.loads(JOBS.read_text()) if JOBS.exists() else {'jobs': []}
state = json.loads(STATE.read_text()) if STATE.exists() else {'jobs': {}}
cron_errors = []
for job in jobs.get('jobs', []):
    st = (state.get('jobs', {}).get(job.get('id'), {}) or {}).get('state', {})
    if st.get('lastStatus') == 'error' or st.get('consecutiveErrors', 0) > 0:
        cron_errors.append({
          'id': job.get('id'), 'name': job.get('name'), 'agentId': job.get('agentId'),
          'lastStatus': st.get('lastStatus'), 'consecutiveErrors': st.get('consecutiveErrors'),
          'lastError': st.get('lastError'), 'nextRunAtMs': st.get('nextRunAtMs')
        })

now = datetime.now(timezone.utc)
report = {
  'schema': 1,
  'kind': 'nightly-incident-evidence-pack',
  'generatedAt': now.isoformat(),
  'window': '24h',
  'journal': {'lineCount': len(lines), 'counts': counts, 'samples': samples},
  'cronErrors': cron_errors,
  'openclawHealth': get_json('http://127.0.0.1:18789/health'),
  'taskSnapshot': get_json('http://127.0.0.1:3000/api/tasks/snapshot'),
}
OUT_DIR.mkdir(parents=True, exist_ok=True)
out = OUT_DIR / f'nightly-incident-evidence-{now.date().isoformat()}.json'
out.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
latest = OUT_DIR / 'nightly-incident-evidence-latest.json'
latest.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
print('NIGHTLY_EVIDENCE_PACK_OK', out)
```

**Verify:**

```bash
python3 /home/piet/.openclaw/scripts/nightly-incident-evidence-pack.py
python3 -m json.tool /home/piet/.openclaw/state/reports/nightly-incident-evidence-latest.json >/dev/null
```

Expected: JSON with `journal.counts`, `cronErrors`, `taskSnapshot`.

---

## Task 2: Create Hermes learning packet writer

**Objective:** Convert latest evidence JSON into a pending Markdown packet in the canonical vault.

**Files:**
- Create: `/home/piet/.hermes/scripts/hermes-nightly-learning-packet.py`

**Implementation sketch:**

```python
#!/usr/bin/env python3
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path

SRC = Path('/home/piet/.openclaw/state/reports/nightly-incident-evidence-latest.json')
OUT_DIR = Path('/home/piet/vault/03-Agents/Hermes/learning-packets/pending')

def bullet_counts(counts):
    return '\n'.join(f'- `{k}`: {v}' for k, v in sorted(counts.items()) if v) or '- none'

def top_cron_errors(errors):
    if not errors:
        return '- none'
    lines = []
    for e in errors[:15]:
        lines.append(f"- `{e.get('name')}` agent=`{e.get('agentId')}` consecutiveErrors=`{e.get('consecutiveErrors')}` error=`{e.get('lastError')}`")
    return '\n'.join(lines)

if not SRC.exists():
    raise SystemExit(f'ERROR: missing evidence pack: {SRC}')
report = json.loads(SRC.read_text())
now = datetime.now(timezone.utc)
date = now.date().isoformat()
out = OUT_DIR / f'{date}-openclaw-nightly.md'
OUT_DIR.mkdir(parents=True, exist_ok=True)
content = f'''---
status: pending_validation
source: openclaw-nightly-evidence-pack
created: {now.isoformat()}
mutation: none
evidence: {SRC}
---

# Nightly OpenClaw Incident Learning Packet — {date}

## Facts

- Evidence window: `{report.get('window')}`
- OpenClaw health ok: `{(report.get('openclawHealth') or {}).get('ok')}`
- Task snapshot: `{(((report.get('taskSnapshot') or {}).get('body') or {}).get('totals'))}`

## Journal Counts

{bullet_counts((report.get('journal') or {}).get('counts') or {})}

## Cron Errors

{top_cron_errors(report.get('cronErrors') or [])}

## Hypotheses

- Fill during human/Hermes review. Do not promote to memory automatically.

## Reusable Lesson Candidate

- Candidate skill/memory updates require explicit review.

## Should become Hermes memory?

- Proposed: `no` until Piet/Hermes validates the packet.

## Should patch a skill?

- Proposed: `none` unless a repeated operational pattern is confirmed.

## Next Action

- Review this packet; if facts reveal a repeated fix pattern, patch the relevant skill with explicit approval.
'''
out.write_text(content)
print('HERMES_LEARNING_PACKET_OK', out)
```

**Verify:**

```bash
python3 /home/piet/.hermes/scripts/hermes-nightly-learning-packet.py
readlink -f /home/piet/vault/03-Agents/Hermes/learning-packets/pending/*openclaw-nightly.md
```

Expected: Markdown packet with `pending_validation` and no memory/skill mutation.

---

## Task 3: Create OpenClaw evidence cron

**Objective:** Schedule nightly evidence pack generation.

**Command after approval:**

```bash
/home/piet/bin/openclaw cron add \
  --name nightly-incident-evidence-pack \
  --cron '30 5 * * *' \
  --tz Europe/Berlin \
  --agent system-bot \
  --session isolated \
  --message 'RUN: python3 /home/piet/.openclaw/scripts/nightly-incident-evidence-pack.py
If output starts with NIGHTLY_EVIDENCE_PACK_OK, reply exactly NO_REPLY.
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

Expected: run `ok`, evidence JSON written, no Discord output.

---

## Task 4: Create Hermes learning packet cron

**Objective:** Schedule conversion after evidence generation.

**Command after approval:**

```bash
hermes cron create '0 6 * * *' \
  --name 'Hermes Nightly Learning Packet' \
  --script hermes-nightly-learning-packet.py \
  --deliver origin
```

**Verify:**

```bash
hermes cron list --all
hermes cron run <job-id>
```

Expected: packet path printed to origin; no tasks/memory/skills changed.

---

## Rollback

```bash
/home/piet/bin/openclaw cron edit <openclaw-job-id> --disable
hermes cron pause <hermes-job-id>
```

Generated packets are review artifacts; remove only after explicit approval.

## Subagent Verification Addendum — Required Fixes Before Execution

A read-only Hermes subagent reviewed this plan after creation. Implementation must incorporate these corrections:

1. **Hermes CLI syntax:** use `--deliver origin`, not `--delivery origin`.
2. **Hermes prompt contract:** packet cron must explicitly forbid memory writes, skill patches, task creation, config edits, and restarts; if output is exactly `NO_REPLY`, reply exactly `NO_REPLY`.
3. **OpenClaw execution semantics:** evidence generation scheduled through OpenClaw cron is script-first but LLM-mediated unless migrated to a systemjob.
4. **Model override:** remove explicit `--model openai-codex/gpt-5.4-mini` unless a just-in-time preflight proves allowlist/runtime health. Safer default: inherit defaults.
5. **Timeout/failure alert:** set OpenClaw `timeoutSeconds≈120` and configure failure alert/cooldown to #alerts (`1491148986109661334`) or add Hermes stale/missing evidence detection.
6. **Redaction/minimization:** redact journal samples and store counts/IDs/timestamps/truncated errors, not full raw lines or full task snapshots.
7. **Cron run evidence:** include `/home/piet/.openclaw/cron/runs/*.jsonl` where available, not only `jobs-state.json`.
8. **Evidence scope:** include model-runtime failures, session health/stuck sessions, fallback summaries, and cron payload.model allowlist drift if available through read-only endpoints/scripts.
9. **Learning path:** packets remain pending review artifacts; validated lessons may later move/copy to `/home/piet/vault/03-Agents/Hermes/lessons/` after review.

## Acceptance Criteria

- Evidence pack JSON is generated nightly.
- Hermes packet is generated from JSON into canonical vault.
- Packet status is `pending_validation`.
- Subagent addendum corrections are reflected in the final implementation receipt.
- No automatic memory, skill, task, config, restart, or dispatch occurs.
