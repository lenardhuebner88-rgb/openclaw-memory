# Receipt — vault-sync secret-cleanup and push observability fix

Date: 2026-05-05
Operator: Hermes, with Piet approval in Discord thread
Mode: approved mutation / focused recovery

## Problem
`vault-sync.service` created local commits but GitHub rejected push with:

```text
! [remote rejected] master -> master (push declined due to repository rule violations)
```

Live inspection found the likely push-protection trigger in the unpublished diff:

```text
08-Backups/openclaw-config-backups/2026-05-05/openclaw.json openai_key=2 generic_api_key_assignment=10
```

The service also hid push failures because `git push ... | tail -3` returned `tail`'s exit code.

## Plan document

```text
/home/piet/vault/03-Agents/Hermes/vault-sync-secret-cleanup-plan-2026-05-05.md
```

## Backups

```text
Git backup branch: backup/vault-sync-pre-secret-cleanup-20260505T145835Z
Git bundle: /home/piet/vault/.git/vault-sync-pre-secret-cleanup-20260505T145835Z.bundle
Service backup: /home/piet/.config/systemd/user/vault-sync.service.bak-20260505T145835Z
```

## Changes applied

### Vault git history/local state

- Temporarily stopped `vault-sync.timer`.
- Rebased/rebuilt unpublished local state onto last accepted `github/master` via `git reset --soft github/master`.
- Removed `08-Backups/openclaw-config-backups/` from Git index while leaving local files on disk.
- Added `.gitignore` entry:

```gitignore
# Local OpenClaw config/script backups may contain secrets and must stay local-only
08-Backups/openclaw-config-backups/
```

- Created cleaned commit:

```text
537a37d chore(vault): sync cleaned local state without config backups
```

### vault-sync.service

Replaced the fragile one-liner with pipefail-safe execution:

```bash
set -euo pipefail
cd /home/piet/vault
git add -A
git diff --cached --quiet || git commit -m "auto-sync: $(date +%Y-%m-%d\ %H:%M)"
git push github master
```

This makes future push rejection visible as a systemd failure.

## Verification snapshot before final service-run

- Backup dir staged additions/modifications: `0`.
- Staged secret-like scan before cleaned commit: `0` hits across non-deleted staged files.
- GitHub remote `refs/heads/master` observed at cleaned commit:

```text
537a37de81e5146fe647b90f6091d1c4b44b6982 refs/heads/master
```

## Rollback

- Git state rollback:

```bash
git -C /home/piet/vault reset --hard backup/vault-sync-pre-secret-cleanup-20260505T145835Z
```

- Or recover from bundle:

```bash
git -C /home/piet/vault fetch /home/piet/vault/.git/vault-sync-pre-secret-cleanup-20260505T145835Z.bundle master:restore/vault-sync-pre-secret-cleanup
```

- Service rollback:

```bash
cp /home/piet/.config/systemd/user/vault-sync.service.bak-20260505T145835Z /home/piet/.config/systemd/user/vault-sync.service
systemctl --user daemon-reload
```
