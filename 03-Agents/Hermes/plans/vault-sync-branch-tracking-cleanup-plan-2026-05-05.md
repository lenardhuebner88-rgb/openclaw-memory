---
title: Vault Sync Branch Tracking Cleanup Plan
date: 2026-05-05
status: proposed
mutation_level: planned_git_config_change_only
affected_files:
  - /home/piet/vault/.git/config
  - /home/piet/.config/systemd/user/vault-sync.service
for_atlas:
  status: needs_piet_approval
  affected_agents: []
  affected_files:
    - /home/piet/vault/.git/config
    - /home/piet/.config/systemd/user/vault-sync.service
  recommended_next_action: "If Piet approves, align local master tracking to github/master and verify vault-sync still pushes cleanly."
  risk: "Low if limited to branch tracking; do not merge/rebase main into master in this step."
  evidence_files:
    - /home/piet/vault/03-Agents/Hermes/receipts/2026-05-05_vault-sync-secret-cleanup_receipt.md
---

# Vault Sync Branch Tracking Cleanup Plan — 2026-05-05

## Problem

After the vault-sync secret cleanup, the actual Git push path is healthy, but local branch tracking is misleading:

```text
Local branch configured for 'git pull': master merges with remote main
Local ref configured for 'git push': master pushes to master (up to date)
```

Live evidence at planning time:

```text
remote.github.url git@github.com:lenardhuebner88-rgb/openclaw-memory.git
remote.github.fetch +refs/heads/*:refs/remotes/github/*
branch.master.remote github
branch.master.merge refs/heads/main
Remote HEAD branch: master
master vs github/master: 0 0
master vs github/main:   0 970
```

Current visible symptom:

```text
## master...github/main [ahead 970]
```

This makes operators and agents think the Vault is massively ahead of its upstream, even though the service push target `github/master` is in sync.

## Goal

Make branch tracking reflect the real operational path:

```text
local master tracks github/master
vault-sync.service pushes github master
Git status no longer reports github/main ahead drift
```

## Non-goals

- Do not merge, rebase, delete, or rewrite `github/main`.
- Do not change GitHub default branch or repository rules.
- Do not force-push.
- Do not alter Vault content except a receipt if implementation is approved.
- Do not restart OpenClaw/Gateway/Mission Control.

## Recommended fix

Set local `master` upstream to `github/master`:

```bash
git -C /home/piet/vault branch --set-upstream-to=github/master master
```

Equivalent exact config mutation:

```ini
[branch "master"]
  remote = github
  merge = refs/heads/master
```

Rationale:

- `github` remote HEAD is `master`.
- `vault-sync.service` already pushes `git push github master`.
- `master` and `github/master` are currently equal.
- Changing upstream is metadata-only; no working-tree or commit history mutation is required.

## Step-by-step implementation plan

### 1. Pre-check live state

```bash
cd /home/piet/vault
git status --short --branch
git config --get-regexp '^(branch\.master\.|remote\.github\.)'
git remote show github
git rev-list --left-right --count github/master...master
git rev-list --left-right --count github/main...master
systemctl --user status vault-sync.service --no-pager
systemctl --user list-timers 'vault-sync.timer' --all --no-pager
```

Expected before-change evidence:

```text
branch.master.merge refs/heads/main
master vs github/master: 0 0
Remote HEAD branch: master
```

Stop if `master vs github/master` is not `0 0`; that would mean new divergence and the safe metadata-only assumption no longer holds.

### 2. Backup Git config

```bash
ts=$(date -u +%Y%m%dT%H%M%SZ)
cp /home/piet/vault/.git/config /home/piet/vault/.git/config.bak-vault-sync-branch-tracking-$ts
```

Stop if backup fails.

### 3. Apply metadata-only upstream fix

Preferred:

```bash
git -C /home/piet/vault branch --set-upstream-to=github/master master
```

This edits only `/home/piet/vault/.git/config`.

### 4. Verify branch tracking

```bash
cd /home/piet/vault
git config --get branch.master.remote
git config --get branch.master.merge
git status --short --branch
git remote show github
```

Expected post-check:

```text
branch.master.remote = github
branch.master.merge = refs/heads/master
## master...github/master
```

If there are local Vault modifications, `git status` may still list changed files, but it should no longer say `github/main [ahead 970]`.

### 5. Verify vault-sync still uses intended push path

Read-only service check:

```bash
systemd-analyze --user verify /home/piet/.config/systemd/user/vault-sync.service /home/piet/.config/systemd/user/vault-sync.timer
systemctl --user list-timers 'vault-sync.timer' --all --no-pager
```

Optional focused live run, only if Piet wants immediate end-to-end proof instead of waiting for the next timer:

```bash
systemctl --user start vault-sync.service
systemctl --user show vault-sync.service -p Result -p ExecMainStatus -p ExecMainCode --no-pager
git -C /home/piet/vault status --short --branch
GIT_SSH_COMMAND='ssh -i /home/piet/.ssh/id_github -o StrictHostKeyChecking=accept-new' \
  git -C /home/piet/vault ls-remote github refs/heads/master
```

Expected:

```text
Result=success
ExecMainStatus=0
remote refs/heads/master equals local master or advances to the new receipt commit
```

### 6. Receipt

If implemented, write receipt:

```text
/home/piet/vault/03-Agents/Hermes/receipts/2026-05-05_vault-sync-branch-tracking-cleanup_receipt.md
```

Receipt should include:

- backup path for `.git/config`
- before/after `branch.master.merge`
- `git status --short --branch` before/after
- service/timer verification
- rollback command

## Rollback

Restore backed-up config:

```bash
cp /home/piet/vault/.git/config.bak-vault-sync-branch-tracking-<timestamp> /home/piet/vault/.git/config
```

Or explicitly restore old tracking:

```bash
git -C /home/piet/vault branch --set-upstream-to=github/main master
```

Rollback should not affect commits or working-tree files.

## Risk assessment

Low risk if constrained to `branch.master.merge` metadata.

Main risk is scope creep: resolving the historical `main` vs `master` branch split is a separate repository-governance decision and should not be combined with this hygiene fix.

## Recommendation

Proceed with the metadata-only fix: set local `master` upstream to `github/master`, verify status and vault-sync, and document a receipt. Do not touch `github/main` in this step.
