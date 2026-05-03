# Receipt — Atlas primary gpt-5.4 test route

Date: 2026-05-04 00:28 CEST

## Approval

Piet requested: "Setzte sauber 1 und 2 auf und finde den rootcause".

## Files changed

- `/home/piet/.openclaw/openclaw.json`

## Backup

- `/home/piet/.openclaw/openclaw.json.bak-20260503T222735Z-atlas-primary-gpt54`

## Diff summary

Atlas (`agents.list[id=main]`):

- `model.primary`: `openai/gpt-5.5` → `openai/gpt-5.4`
- `model.fallbacks`: removed duplicate `openai/gpt-5.4` after making it primary
- final fallbacks: `openai/gpt-5.4-mini`, `openai/gpt-5.3-codex`

## Restart

Command run:

```bash
systemctl --user restart openclaw-gateway.service
```

## Post-check

- `openclaw-gateway.service`: active/running, MainPID `395240`
- `/health`: HTTP 200 `{ "ok": true, "status": "live" }`
- Effective config redacted endpoint confirms Atlas primary `openai/gpt-5.4`.

Note: first immediate curl raced startup and failed before HTTP server bound; subsequent MCP health check succeeded.

## Rollback

```bash
cp /home/piet/.openclaw/openclaw.json.bak-20260503T222735Z-atlas-primary-gpt54 /home/piet/.openclaw/openclaw.json
systemctl --user restart openclaw-gateway.service
```

## Related investigation artifact

- `/home/piet/vault/03-Agents/Hermes/investigations/atlas-timeout-2026-05-04/rootcause/rootcause-report.md`
