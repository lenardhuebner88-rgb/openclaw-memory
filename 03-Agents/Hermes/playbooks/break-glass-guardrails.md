---
title: Break-glass Guardrails
created: 2026-05-03T18:14Z
agent: Hermes
status: active_guardrail_doc
scope: openclaw-break-glass
mutation_level: documentation_only
---

# Break-glass Guardrails

This playbook defines the approval gate for Hermes when Piet explicitly asks for emergency debugging/recovery or asks Hermes to perform bounded OpenClaw operations.

## Default Boundary

Hermes is read-only first.

Allowed without mutation approval:

```text
MCP read-only health/status/log/session checks
focused file reads in /home/piet/vault and redacted/targeted config reads
journal exact-window reads
PERN incident report
```

Not allowed without explicit Piet approval:

```text
service restarts
config edits
task/cron/agent creation
plugin install/update/deploy
Discord command sync/clear
permanent command allowlist changes
YOLO mode
token rotation or token replacement
```

## Restart Gate

Before any restart, Hermes must state:

```text
Live evidence showing why restart is needed
Exact service
Exact command
Expected post-check
Scope/risk
```

Then wait for Piet approval in the current Discord thread.

### Approved-shape restart commands

Only if specifically approved:

```bash
systemctl --user restart openclaw-gateway.service
systemctl --user restart mission-control.service
systemctl --user restart openclaw-discord-bot.service
```

Use the narrowest service that matches the evidence.

### Post-check

```bash
systemctl --user status <service> --no-pager
curl -s --max-time 5 http://127.0.0.1:18789/health    # for OpenClaw gateway
journalctl --user -u <service> --since "2 minutes ago" --no-pager \
  | grep -Ei 'ready|error|failed|timeout|provider.*not found'
```

For user-visible Discord incidents, require an E2E signal where possible; `/health` alone is not enough.

## Config Edit Gate

Before editing config, Hermes must state:

```text
Live evidence showing why the edit is needed
Exact file
Exact key/path
Timestamped backup path
Intended diff
Whether restart is needed
Focused post-check
```

Then wait for Piet approval in the current Discord thread.

### Canonical config file

```text
/home/piet/.openclaw/openclaw.json
```

### Backup pattern

```bash
ts=$(date -u +%Y%m%dT%H%M%SZ)
cp /home/piet/.openclaw/openclaw.json /home/piet/.openclaw/openclaw.json.bak-$ts
```

Stop immediately if backup fails.

### Edit pattern

Use targeted JSON parsing/writing. Do not use broad sed/string replacement for JSON migrations.

```bash
python3 - <<'PY'
import json
p='/home/piet/.openclaw/openclaw.json'
d=json.load(open(p))
# targeted edit here
with open(p,'w') as f:
    json.dump(d, f, indent=2)
    f.write('\n')
PY
```

### Verify before restart

```bash
python3 -m json.tool /home/piet/.openclaw/openclaw.json >/dev/null
python3 - <<'PY'
import json
p='/home/piet/.openclaw/openclaw.json'
d=json.load(open(p))
# print exact edited keys only
PY
```

## Stop Conditions

Stop and report if:

```text
backup failed
JSON parse failed
target key/path differs from expected
service ownership unclear
restart fails
post-check shows new critical errors
scope expands beyond approval
```

## Receipt Requirement

After approved mutation, write a receipt under:

```text
/home/piet/vault/03-Agents/Hermes/receipts/YYYY-MM-DD_<topic>_receipt.md
```

Include:

```text
operator approval phrase/time
live pre-evidence
backup path
exact diff summary
commands run
post-check evidence
rollback note
remaining risk
for_atlas block
```

## Never

- Never expose tokens in Discord, logs, or vault docs.
- Never replace Hermes tokens with Piet/OpenClaw tokens.
- Never enable YOLO mode unless Piet explicitly asks for YOLO by name.
- Never create persistent automation as a side-effect of incident recovery.
- Never use `/home/piet/Vault` or `/home/piet/.openclaw/workspace/vault` as the canonical vault.
