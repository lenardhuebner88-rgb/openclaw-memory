# Atlas GPT-5.5 + Heartbeat Isolation Receipt

Timestamp: 2026-05-04 09:35 CEST
Owner: Codex

## Scope

Requested change: set Atlas/main to GPT 5.5 and work cleanly according to the stabilization plan.

Applied changes:

- `/home/piet/.openclaw/openclaw.json`
  - `agents.list[id=main].model.primary`: `openai/gpt-5.4` -> `openai/gpt-5.5`
  - `agents.list[id=main].model.fallbacks`: now `openai/gpt-5.3-codex`, `openai/gpt-5.4`, `openai/gpt-5.4-mini`
  - Added `agents.list[id=main].heartbeat`:
    - `every: 30m`
    - `isolatedSession: true`
    - `skipWhenBusy: true`
    - `lightContext: true`
    - `model: openai/gpt-5.4-mini`
    - `timeoutSeconds: 120`
    - `ackMaxChars: 80`
- `/home/piet/.openclaw/scripts/apply-openclaw-response-hardening.py`
  - Store-lock hold patch is now intentionally skipped for beta4 because the old store-lock anchors were removed.
  - Typing TTL and session-write-lock watchdog patches remain active.
- `/home/piet/.config/systemd/user/openclaw-gateway.service.d/description-version.conf`
  - Description updated from `v2026.5.2` to `v2026.5.3-beta.4`.

## Backup

- `/home/piet/.openclaw/openclaw.json.bak-20260504T072846Z-atlas-gpt55-heartbeat-isolation`

## Validation

Config validation:

- `python3 -m json.tool /home/piet/.openclaw/openclaw.json` passed.
- Atlas config after edit:
  - primary: `openai/gpt-5.5`
  - fallbacks: `openai/gpt-5.3-codex`, `openai/gpt-5.4`, `openai/gpt-5.4-mini`
  - heartbeat isolation block present.

Service validation:

- `systemctl --user daemon-reload` completed.
- `systemctl --user restart openclaw-gateway.service` completed.
- Service state after final restart:
  - active/running
  - PID `737681`
  - start timestamp `2026-05-04 09:32:24 CEST`
- Health:
  - `{"ok":true,"status":"live"}`
- Version:
  - `OpenClaw 2026.5.3-beta.4 (c6c64e2)`
- `openclaw agents list --json` shows:
  - `main`, name `Atlas`, model `openai/gpt-5.5`, default agent true.

ExecStartPre validation:

- `apply-openclaw-response-hardening.py` manual run returned `EXIT=0`.
- `py_compile` passed.
- Final restart logs show no `failed session-store lock hold patch`; only intentional line:
  - `skipped session-store lock hold patch: beta4 store-lock anchors removed`

Smoke note:

- A non-delivery `openclaw agent --agent main` CLI smoke was attempted.
- It is not valid as model-latency evidence because the CLI/Gateway path fell into a local embedded fallback and failed on local `openai/*` API-key auth.
- This does not invalidate the Discord/OAuth Gateway route. The effective agent list confirms Atlas/main is now routed to `openai/gpt-5.5`.

## Next Validation Window

Watch for 30-60 minutes:

- Heartbeat session key should become `agent:main:main:heartbeat`.
- If Atlas is busy during heartbeat time, journal should show busy-skip behavior instead of a parallel heartbeat run.
- Atlas Discord lane should have 0 fresh `codex app-server attempt timed out`.
- Normal Atlas Discord operator turns should respond under 60s.

Key commands:

```bash
openclaw agents list --json
curl -fsS http://127.0.0.1:18789/health
journalctl --user -u openclaw-gateway.service --since '2026-05-04 09:32:24 CEST' --no-pager | rg 'codex app-server attempt timed out|FailoverError|HEARTBEAT_SKIP_LANES_BUSY|heartbeat.*skipped|model fallback decision'
rg -n 'sessionKey.*heartbeat|timedOut|promptError|cacheRead|model.completed' /home/piet/.openclaw/agents/main/sessions/*.trajectory.jsonl
```

