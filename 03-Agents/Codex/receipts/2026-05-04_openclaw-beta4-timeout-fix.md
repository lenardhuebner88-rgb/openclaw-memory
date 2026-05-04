# 2026-05-04 OpenClaw beta4 timeout fix receipt

## Scope

Goal: apply the OpenClaw timeout fix path for Atlas/Forge after the observed `codex app-server attempt timed out` failures on OpenClaw 2026.5.2.

## Baseline

- Host cwd: `/home/piet`
- Initial OpenClaw: `OpenClaw 2026.5.2 (8b2a6e5)`
- npm tags at start: `latest=2026.5.2`, `beta=2026.5.3-beta.4`
- Gateway before change: `active`, `/health` returned `{"ok":true,"status":"live"}`
- Active timeout setting: `agents.defaults.timeoutSeconds=300`
- Embedded-run timeout patch drop-in existed before upgrade:
  - `/home/piet/.config/systemd/user/openclaw-gateway.service.d/embedded-run-timeout-patch.conf`

## Backups

Primary backup directory:

- `/home/piet/.openclaw/backups/openclaw-beta4-upgrade-20260504T062526Z`

Important files captured:

- `openclaw.json`
- `openclaw-gateway.service.cat.txt`
- `embedded-run-timeout-patch.conf`
- `openclaw-version.before.txt`
- `npm-openclaw.before.json`
- plugin package and lockfile backups before plugin changes
- `installs.json` before registry reset/rebuild

## Changes Applied

1. Disabled the local embedded-run source patch drop-in before upgrade:
   - moved to `/home/piet/.config/systemd/user/openclaw-gateway.service.d/embedded-run-timeout-patch.conf.disabled-20260504T062526Z`

2. Upgraded OpenClaw core:
   - `openclaw@2026.5.3-beta.4`

3. Migrated beta4-incompatible config:
   - removed unsupported `agentRuntime.fallback` from `agents.defaults.agentRuntime`
   - removed unsupported `agentRuntime.fallback` from all 7 configured agents
   - applied consistently to:
     - `/home/piet/.openclaw/openclaw.json`
     - `/home/piet/.openclaw/openclaw.json.last-good`
     - `/home/piet/.openclaw/backups/openclaw-config-guard/openclaw.json.last-good`

4. Updated managed OpenClaw plugins:
   - `@openclaw/codex@2026.5.3-beta.4`
   - `@openclaw/discord@2026.5.3-beta.4`

5. Fixed beta4 plugin startup integration:
   - added runtime entry metadata to installed plugin manifests:
     - `@openclaw/codex/openclaw.plugin.json`: `runtimeExtensions=["./dist/index.js"]`
     - `@openclaw/discord/openclaw.plugin.json`: `runtimeExtensions=["./dist/index.js"]`, `runtimeSetupEntry="./dist/setup-entry.js"`
   - moved stale `/home/piet/.openclaw/plugins/installs.json` aside
   - rebuilt plugin registry with `openclaw doctor --fix --non-interactive`
   - installed `openclaw@2026.5.3-beta.4` into `/home/piet/.openclaw/npm` so managed plugins can resolve `openclaw/dist/plugin-sdk/...`

## Validation

Current package versions:

- `openclaw=2026.5.3-beta.4`
- `@openclaw/codex=2026.5.3-beta.4`
- `@openclaw/discord=2026.5.3-beta.4`
- managed plugin-root peer `openclaw=2026.5.3-beta.4`

Gateway and MC:

- `openclaw --version`: `OpenClaw 2026.5.3-beta.4 (c6c64e2)`
- `openclaw-gateway.service`: `active`
- `mission-control.service`: `active`
- `http://127.0.0.1:18789/health`: `{"ok":true,"status":"live"}`
- `http://127.0.0.1:3000/api/health`: `status=ok`

Config guard:

- `/usr/bin/python3 /home/piet/.openclaw/scripts/openclaw-config-validator.py`: `VALIDATION_OK`
- config-guard state hash equals current `openclaw.json` hash
- no remaining `agentRuntime.fallback` keys

Real canaries:

- Atlas/main:
  - command output file: `/tmp/openclaw-canary-main-20260504T064014Z.json`
  - runId: `761dc638-b9fc-493a-8ef4-a599b09bcdd4`
  - result: `status=ok`, `stopReason=stop`, `fallbackUsed=false`
  - model: `gpt-5.4-mini`
  - duration: `41853ms`
  - usage: `cacheRead=165248`, `total=166171`

- Forge/sre-expert:
  - command output file: `/tmp/openclaw-canary-forge-20260504T064108Z.json`
  - runId: `9678c835-ddf5-448a-b58c-6cad1ded824e`
  - result: `status=ok`, `stopReason=stop`, `fallbackUsed=false`
  - model: `gpt-5.3-codex`
  - duration: `15355ms`
  - usage: `cacheRead=6528`, `total=30075`

Post-canary log check since `2026-05-04 08:40:00 CEST`:

- no `codex app-server attempt timed out`
- no `FailoverError`
- no `fetch timeout reached`
- no `Gateway failed`
- no `Invalid config`
- no `ERR_MODULE_NOT_FOUND`
- no `model fallback decision`

## Notes

- The systemd unit description drop-in still says `OpenClaw Gateway (v2026.5.2)`, but the running binary and CLI report `2026.5.3-beta.4`.
- `apply-openclaw-response-hardening.py` still exits `1` during `ExecStartPre`, but it is prefixed with `-` and did not block startup. This is maintenance noise to clean separately.
- The first Atlas canary exposed `ERR_MODULE_NOT_FOUND` for plugin SDK resolution; this was fixed by adding the matching `openclaw@2026.5.3-beta.4` package to the managed plugin npm root.

## Rollback Anchor

Primary rollback materials are in:

- `/home/piet/.openclaw/backups/openclaw-beta4-upgrade-20260504T062526Z`

Minimum rollback would be:

```bash
npm install -g openclaw@2026.5.2
cp /home/piet/.openclaw/backups/openclaw-beta4-upgrade-20260504T062526Z/openclaw.json /home/piet/.openclaw/openclaw.json
systemctl --user daemon-reload
systemctl --user restart openclaw-gateway.service
```
