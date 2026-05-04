---
title: OpenClaw Cron Model-Allowlist and Agent Retarget Plan
status: proposed
created: 2026-05-04
owner: Hermes
mutation_level: plan_only_no_runtime_changes
scope:
  - /home/piet/.openclaw/openclaw.json
  - /home/piet/.openclaw/cron/jobs.json
  - /home/piet/.openclaw/cron/jobs-state.json
for_atlas:
  status: needs_piet_approval
  affected_agents: [system-bot, sre-expert, efficiency-auditor, worker]
  affected_files:
    - /home/piet/.openclaw/openclaw.json
    - /home/piet/.openclaw/cron/jobs.json
  recommended_next_action: "Fix cron payload.model allowlist first; only retarget worker drift after that. Do not blanket-retarget all cronjobs to system-bot."
  risk: "Cron model preflight failures continue until agents.defaults.models or payload.model usage is corrected. Blanket agent retargeting would not fix the current failure and may erase useful role separation."
  evidence_files:
    - /home/piet/.openclaw/cron/jobs.json
    - /home/piet/.openclaw/cron/jobs-state.json
    - /home/piet/.openclaw/cron/runs/learnings-to-tasks-001.jsonl
---

# OpenClaw Cron Model-Allowlist and Agent Retarget Plan

> **For Hermes:** This is a plan-only document. Do not mutate OpenClaw config, cron jobs, services, or sessions without Piet's explicit approval in the current thread.

## Goal

Restore scheduled OpenClaw cron reliability by fixing the cron `payload.model` allowlist failure, while preserving useful agent ownership boundaries and only retargeting jobs where live config shows drift.

## Recommendation

Do **not** blanket-retarget all cron jobs to `system-bot`.

Concrete recommended path:

1. **Phase 1 — Fix model allowlist class bug** by adding all cron-used explicit `openai-codex/*` model refs to `agents.defaults.models` in `/home/piet/.openclaw/openclaw.json`.
2. **Phase 2 — Leave most agent ownership as-is** because many failed jobs already run on `system-bot`, and SRE/Lens jobs have role-specific intent.
3. **Phase 3 — Clean one likely drift case**: retarget `memory-sqlite-vacuum-weekly` from non-existent `worker` to `system-bot`, or recreate/define `worker` if Piet intentionally wants a worker agent.
4. **Phase 4 — Focused verification** with one manual cron smoke for `learnings-to-tasks` and one high-frequency/no-delivery smoke such as `mc-pending-pickup-smoke-hourly`.

## Live Evidence Snapshot

Collected read-only on 2026-05-04.

### Current cron allowlist

`agents.defaults.models` currently allows only:

- `minimax/MiniMax-M2.7`
- `minimax/MiniMax-M2.7-highspeed`
- `openai/gpt-image-2`
- `openrouter/auto`

### Enabled cron jobs with disallowed explicit `payload.model`

All listed jobs are enabled and currently use a `payload.model` that is not present in `agents.defaults.models`:

| Job | Agent | payload.model |
|---|---|---|
| `daily-cost-report` | `system-bot` | `openai-codex/gpt-5.4-mini` |
| `morning-brief` | `system-bot` | `openai-codex/gpt-5.4-mini` |
| `nightly-self-improvement` | `system-bot` | `openai-codex/gpt-5.4` |
| `efficiency-auditor-heartbeat` | `efficiency-auditor` | `openai-codex/gpt-5.4-mini` |
| `session-cleanup-local` | `sre-expert` | `openai-codex/gpt-5.4-mini` |
| `evening-debrief` | `system-bot` | `openai-codex/gpt-5.4` |
| `Security-Weekly-Audit` | `sre-expert` | `openai-codex/gpt-5.3-codex` |
| `validate-models` | `system-bot` | `openai-codex/gpt-5.4-mini` |
| `learnings-to-tasks` | `system-bot` | `openai-codex/gpt-5.4-mini` |
| `memory-rem-backfill` | `system-bot` | `openai-codex/gpt-5.4-mini` |
| `memory-sqlite-vacuum-weekly` | `worker` | `openai-codex/gpt-5.4-mini` |
| `mc-pending-pickup-smoke-hourly` | `system-bot` | `openai-codex/gpt-5.4-mini` |
| `midday-brief` | `system-bot` | `openai-codex/gpt-5.4-mini` |
| `daily-ops-digest` | `system-bot` | `openai-codex/gpt-5.4-mini` |

### Enabled cron jobs not on `system-bot`

| Job | Current agent | Assessment |
|---|---|---|
| `efficiency-auditor-heartbeat` | `efficiency-auditor` | Keep on Lens unless Piet wants all cost enforcement centralized; workload is role-specific. |
| `session-cleanup-local` | `sre-expert` | Keep on Forge/SRE; workload mutates session files and is maintenance-oriented. |
| `Security-Weekly-Audit` | `sre-expert` | Keep on Forge/SRE; security audit is SRE-oriented. |
| `memory-sqlite-vacuum-weekly` | `worker` | Drift candidate: `worker` is not in active `agents.list`; retarget to `system-bot` unless `worker` should be restored. |

### Key conclusion

The current failure class is independent of `agentId`. Many failing jobs already run on `system-bot`; therefore agent retargeting is not the primary fix.

## Phase 0 — Approval Gate

Before implementation, state and obtain approval for:

```text
Live evidence: enabled cron jobs fail because payload.model refs are not present under agents.defaults.models.
Exact files:
- /home/piet/.openclaw/openclaw.json
- /home/piet/.openclaw/cron/jobs.json only if doing Phase 3 retarget
Exact key/path:
- agents.defaults.models
- cron.jobs[id=memory-sqlite-vacuum-weekly].agentId/sessionKey only if approved
Timestamped backup path:
- /home/piet/.openclaw/openclaw.json.bak-<UTC>
- /home/piet/.openclaw/cron/jobs.json.bak-<UTC> only if Phase 3 retarget is applied
Restart needed: likely yes for OpenClaw Gateway to reload config/cron definitions; command: systemctl --user restart openclaw-gateway.service
Expected post-check:
- JSON parse passes
- /health returns live
- cron manual smoke no longer fails at payload.model allowlist
```

Stop if Piet approves only analysis or only a subset.

## Phase 1 — Fix `agents.defaults.models` allowlist

### Objective

Make existing explicit cron `payload.model` values pass the cron preflight.

### File

- Modify: `/home/piet/.openclaw/openclaw.json`

### Intended JSON change

Add these keys under `agents.defaults.models` if absent:

```json
{
  "openai-codex/gpt-5.4-mini": {},
  "openai-codex/gpt-5.4": {},
  "openai-codex/gpt-5.3-codex": {},
  "openai-codex/gpt-5.5": {}
}
```

Rationale:

- `gpt-5.4-mini`, `gpt-5.4`, and `gpt-5.3-codex` are directly used by enabled cron jobs.
- `gpt-5.5` is active in system defaults and system-bot primary; including it prevents the same gate if a future cron adopts the default explicit model.

### Verification before restart

Run a read-only parser after edit:

```bash
python3 -m json.tool /home/piet/.openclaw/openclaw.json >/dev/null
python3 - <<'PY'
import json
cfg=json.load(open('/home/piet/.openclaw/openclaw.json'))
allowed=set((cfg.get('agents',{}).get('defaults',{}).get('models') or {}).keys())
needed={
  'openai-codex/gpt-5.4-mini',
  'openai-codex/gpt-5.4',
  'openai-codex/gpt-5.3-codex',
  'openai-codex/gpt-5.5',
}
print('missing=', sorted(needed-allowed))
PY
```

Expected:

```text
missing= []
```

## Phase 2 — Do not blanket-retarget role-specific jobs

### Objective

Preserve agent ownership where it carries operational meaning.

### Keep as-is

- `efficiency-auditor-heartbeat` on `efficiency-auditor`
  - Reason: cost enforcement/audit belongs to Lens semantics.
- `session-cleanup-local` on `sre-expert`
  - Reason: session-store cleanup is SRE/maintenance work.
- `Security-Weekly-Audit` on `sre-expert`
  - Reason: security audit is SRE work.

### Why not retarget all to system-bot

- It would not fix allowlist failures.
- It increases system-bot blast radius and transcript/state coupling.
- It removes useful routing/ownership signals in logs and future RCA.

## Phase 3 — Optional drift cleanup: `memory-sqlite-vacuum-weekly`

### Objective

Remove the active cron dependency on `agentId=worker`, because active OpenClaw config currently has no `worker` agent in `agents.list`.

### File

- Modify: `/home/piet/.openclaw/cron/jobs.json`

### Intended change option A — recommended

Retarget only this job:

```json
{
  "id": "af681204-978f-46cf-b793-a50376580291",
  "name": "memory-sqlite-vacuum-weekly",
  "agentId": "system-bot",
  "sessionKey": "agent:system-bot:cron:memory-sqlite-vacuum-weekly:run"
}
```

### Intended change option B — alternative

Leave cron unchanged and restore/define a real `worker` agent in OpenClaw config.

Use this only if Piet wants a dedicated worker agent. This is broader than needed for the current incident.

### Recommendation

Use option A unless there is a known reason to keep `worker`.

## Phase 4 — Gateway reload/restart gate

### Objective

Activate config/cron changes cleanly.

### Command

Only after approval:

```bash
systemctl --user restart openclaw-gateway.service
```

### Expected post-check

```bash
systemctl --user status openclaw-gateway.service --no-pager
curl -s --max-time 5 http://127.0.0.1:18789/health
journalctl --user -u openclaw-gateway.service --since "2 minutes ago" --no-pager \
  | grep -Ei 'ready|error|failed|payload.model|provider.*not found|timed out'
```

Expected:

- service active
- `/health` returns `ok/live`
- no new startup-critical config errors

## Phase 5 — Focused cron smoke verification

### Smoke 1: current incident job

```bash
/home/piet/bin/openclaw cron run learnings-to-tasks-001
/home/piet/bin/openclaw cron runs --id learnings-to-tasks-001 --limit 5
```

Pass condition:

- No `payload.model ... rejected by agents.defaults.models allowlist`.
- If the script itself later reports Ollama/MiniMax/Discord/task API issues, classify those separately; they are not the preflight allowlist issue.

### Smoke 2: high-frequency/no-delivery job

```bash
/home/piet/bin/openclaw cron run 0f9d0f2e-9839-4a14-ad18-cb75ff7f49c7
/home/piet/bin/openclaw cron runs --id 0f9d0f2e-9839-4a14-ad18-cb75ff7f49c7 --limit 5
```

Pass condition:

- No allowlist error.
- Expected summary is `SMOKE_OK` or a real Mission Control smoke result.

## Phase 6 — Post-fix monitoring

After the next morning cycle, inspect:

```bash
python3 - <<'PY'
import json, datetime
st=json.load(open('/home/piet/.openclaw/cron/jobs-state.json')).get('jobs',{})
for jid in ['learnings-to-tasks-001','881bd75e-191e-4f1e-b605-b9f8ec95795a','8f69541c-6add-4da2-960c-d34f36f51eac']:
    s=st.get(jid,{}).get('state',{})
    print(jid, s.get('lastStatus'), s.get('consecutiveErrors'), s.get('lastError'))
PY
```

Expected:

- Allowlist errors disappear.
- Any remaining errors are job-specific and should be triaged separately.

## Rollback Plan

If post-check fails:

1. Restore backup:

```bash
cp /home/piet/.openclaw/openclaw.json.bak-<UTC> /home/piet/.openclaw/openclaw.json
```

2. If cron jobs were edited:

```bash
cp /home/piet/.openclaw/cron/jobs.json.bak-<UTC> /home/piet/.openclaw/cron/jobs.json
```

3. Restart gateway with approval if rollback requires activation:

```bash
systemctl --user restart openclaw-gateway.service
```

4. Verify `/health` and recent journal.

## Final Decision Matrix

| Decision | Recommendation |
|---|---|
| Fix current learnings-to-tasks failure | Add cron-used `openai-codex/*` refs to `agents.defaults.models`. |
| Retarget all jobs to system-bot | No. Does not fix the current failure and weakens role separation. |
| Retarget `memory-sqlite-vacuum-weekly` | Yes, likely, because `worker` is not an active configured agent. |
| Keep SRE jobs on Forge | Yes. `session-cleanup-local` and `Security-Weekly-Audit` are SRE work. |
| Keep Lens cost job on Lens | Yes, unless Piet wants central system-bot ownership for all cost controls. |
| Remove all `payload.model` values instead | Viable alternative, but less explicit and may increase reliance on agent defaults. |

## Exact approval request for implementation

If Piet wants Hermes to implement this plan, request approval for this bounded mutation:

```text
Approve Phase 1 + optional Phase 3A:
- Backup /home/piet/.openclaw/openclaw.json
- Add openai-codex/gpt-5.4-mini, gpt-5.4, gpt-5.3-codex, gpt-5.5 under agents.defaults.models
- Optionally backup /home/piet/.openclaw/cron/jobs.json and retarget only memory-sqlite-vacuum-weekly worker -> system-bot
- Restart openclaw-gateway.service
- Run focused cron smokes for learnings-to-tasks and mc-pending-pickup-smoke-hourly
```
