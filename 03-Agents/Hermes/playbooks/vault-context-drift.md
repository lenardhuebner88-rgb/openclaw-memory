---
title: Hermes Playbook - Vault Context Drift
status: active
created: 2026-05-02
owner: Piet
scope: read-only-diagnosis
---

# Hermes Playbook - Vault Context Drift

Use this when Hermes, OpenClaw, Mission Control, or an operator suspects the wrong vault path, stale planning context, wrong KB path, or outdated memory-derived claims.

## Ground Truth

- Canonical active vault: `/home/piet/vault`
- Agent planning SSoT: `/home/piet/vault/03-Agents/`
- Vault index: `/home/piet/vault/03-Agents/_VAULT-INDEX.md`
- Sprint index SSoT: `/home/piet/vault/04-Sprints/INDEX.md`
- KB compiler output: `/home/piet/vault/10-KB/`
- OpenClaw memory bulk: `/home/piet/.openclaw/workspace/memory/`
- Mirror/reference only: `/home/piet/.openclaw/workspace/vault`
- Wrong-vault trap: `/home/piet/Vault`

## Allowed Without Approval

Read-only checks:

```bash
test -d /home/piet/vault && echo "active_vault=present"
test -d /home/piet/Vault && echo "wrong_case_vault=present" || echo "wrong_case_vault=absent"
test -f /home/piet/vault/03-Agents/_VAULT-INDEX.md && head -20 /home/piet/vault/03-Agents/_VAULT-INDEX.md
test -f /home/piet/vault/04-Sprints/INDEX.md && head -40 /home/piet/vault/04-Sprints/INDEX.md
find /home/piet/vault/03-Agents/Hermes -maxdepth 2 -type f | sort
test -d /home/piet/vault/10-KB && echo "kb=10-KB-present"
test -d /home/piet/vault/03-Agents/kb && echo "legacy_kb_path=present" || echo "legacy_kb_path=absent"
test -d /home/piet/.openclaw/workspace/vault && echo "mirror=present"
test -d /home/piet/.openclaw/workspace/memory && echo "openclaw_memory=present"
```

Optional timestamp checks:

```bash
stat -c "%y %n" /home/piet/vault/03-Agents/Hermes/working-context.md /home/piet/vault/03-Agents/Hermes/system-overview.md
find /home/piet/vault/01-Daily -maxdepth 1 -type f 2>/dev/null | sort | tail -5
```

## Report Shape

```text
Problem: suspected vault/context drift
Evidence: exact paths and timestamps checked
Risk: what would go wrong if stale context is used
Next Action: use confirmed path, or ask Piet if live evidence conflicts
```

## Stop Conditions

- `/home/piet/vault` is missing.
- `_VAULT-INDEX.md` and `04-Sprints/INDEX.md` conflict with each other.
- Current session evidence conflicts with Hermes working context.
- A proposed fix would write to `/home/piet/Vault` or the mirror path.

Do not edit or sync vaults during this playbook unless Piet explicitly asks.

