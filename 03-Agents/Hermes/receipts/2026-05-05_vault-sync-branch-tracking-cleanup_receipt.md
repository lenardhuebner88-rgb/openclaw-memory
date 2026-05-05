# Receipt — vault-sync branch tracking cleanup

Date: 2026-05-05
Operator: Hermes, with Piet approval in Discord thread
Mode: approved metadata-only Git config cleanup

## Problem

Vault sync was functionally healthy after the secret-cleanup, but local branch tracking was misleading:

```text
branch.master.remote github
branch.master.merge refs/heads/main
```

while the actual operational push path and remote default are:

```text
Remote HEAD branch: master
vault-sync.service: git push github master
master pushes to master (up to date)
```

This caused `git status` to report:

```text
## master...github/main [ahead 970]
```

## Plan document

```text
/home/piet/vault/03-Agents/Hermes/plans/vault-sync-branch-tracking-cleanup-plan-2026-05-05.md
```

## Live pre-check

```text
github/master...master 0 0
github/main...master   0 970
Remote HEAD branch: master
Local branch configured for pull: master merges with remote main
Local ref configured for push: master pushes to master (up to date)
```

## Backup

```text
/home/piet/vault/.git/config.bak-vault-sync-branch-tracking-20260505T152417Z
```

## Change applied

Command:

```bash
git -C /home/piet/vault branch --set-upstream-to=github/master master
```

Exact metadata result:

```text
branch.master.remote github
branch.master.merge refs/heads/master
```

## Verification immediately after change

```text
## master...github/master
 M 03-Agents/OpenClaw/daily/2026-05-05.md
?? 03-Agents/Hermes/plans/vault-sync-branch-tracking-cleanup-plan-2026-05-05.md

github/master...master 0 0
```

The remaining modified/untracked files are normal Vault content/doc changes and not branch-tracking drift.

## Scope control

Not changed:

- no merge/rebase
- no force-push
- no GitHub repository/default-branch/rules changes
- no OpenClaw/Gateway/Mission Control restart
- no modification to `github/main`

## Rollback

Restore backed-up config:

```bash
cp /home/piet/vault/.git/config.bak-vault-sync-branch-tracking-20260505T152417Z /home/piet/vault/.git/config
```

Or restore old tracking explicitly:

```bash
git -C /home/piet/vault branch --set-upstream-to=github/main master
```
