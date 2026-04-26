---
status: implemented
created: 2026-04-26T17:58Z
owner: codex
scope: atlas-runtime-kernel
---

# Atlas Kernel v1 Durable Patch Report

## Ergebnis

Atlas' Runtime-Kernel ist jetzt deutlich kleiner und der manuelle `dist`-Patch ist reproduzierbar.

## Geaendert

- `/home/piet/.openclaw/workspace/HEARTBEAT.md`
  - vorher: 18,987 Bytes
  - nachher: 3,349 Bytes
  - Inhalt: aktiver Heartbeat-/Truth-/Stop-Kernel statt langer historischer Regelkoerper.
- `/home/piet/.openclaw/workspace/MEMORY.md`
  - vorher: 29,063 Bytes
  - nachher: 2,370 Bytes
  - Inhalt: Retrieval-Index und Pointer statt eingebetteter Langzeit-Zusammenfassungen.
- `/home/piet/.openclaw/scripts/atlas-orchestrator-runtime-patch.mjs`
  - read-only Verify Default
  - `--apply` kopiert den bekannten gepatchten Runtime-Build wieder ein, falls ein npm/global package overwrite den Patch entfernt.

## Backups

- `/home/piet/.openclaw/backup/atlas-kernel-v1-20260426/HEARTBEAT.md.bak`
- `/home/piet/.openclaw/backup/atlas-kernel-v1-20260426/MEMORY.md.bak`
- `/home/piet/.openclaw/backup/atlas-kernel-v1-20260426/selection-DGLE6AvW.js.current`

## Verifikation

- `openclaw config validate`: ok
- `atlas-orchestrator-runtime-patch.mjs --apply`: ok, Patch bereits vorhanden
- Atlas Smoke:
  - Session: `e6c23575-9d28-4cba-b5e9-98e240c4f605`
  - Antwort: `ATLAS_KERNEL_V1_OK`
  - Dauer: 2.86s
  - Prompt Tokens: 16,361
  - System-Prompt chars: 52,893
- Budget Proof:
  - `status=ok`
  - latest trajectory bytes: 10,540
  - max trace metadata bytes: 3,278
  - max context compiled bytes: 1,543
  - max tools bytes: 17,055
  - findings: `[]`
- Mission Control:
  - `/api/health`: ok
  - `/api/ops/pickup-proof?limit=20`: ok nach DispatchTarget-Fix fuer Task `76a89795...`
  - `/api/ops/worker-reconciler-proof?limit=20`: ok, `criticalIssues=0`
  - `mission-control.service`: active
  - `openclaw-gateway.service`: active

## Zusaetzlicher Minimal-Fix

Beim Gate fiel ein neuer Task auf:

- Task: `76a89795-87f0-4d3c-98db-11f38a8171d5`
- Problem: `assigned_agent=sre-expert`, aber kein `dispatchTarget`; Auto-Pickup meldete `SKIP_NO_TARGET`.
- Fix: nur `dispatchTarget=sre-expert` und `workerLabel=sre-expert` gesetzt.
- Ergebnis: Auto-Pickup hat sauber uebernommen; Task ist `in-progress`, Worker-Run offen, Heartbeat frisch.

## Rest-Risiken

- Atlas Discord Smoke nutzt aktuell `gpt-5.4-mini`. Das kann fuer Heartbeat guenstig sein, sollte aber fuer echte Orchestrierung explizit von GPT-5.5-Routing getrennt werden.
- `systemPrompt.chars=52,893` ist besser, aber noch nicht ideal. Groesste naechste Hebel: `AGENTS.md`, Skill-Prompt-Liste und Tool-Schema.
- `dist`-Patch bleibt ein Runtime-Patch. Das neue Script macht ihn reproduzierbar, ersetzt aber keinen Upstream-Fix.

## Rollback

```bash
cp /home/piet/.openclaw/backup/atlas-kernel-v1-20260426/HEARTBEAT.md.bak /home/piet/.openclaw/workspace/HEARTBEAT.md
cp /home/piet/.openclaw/backup/atlas-kernel-v1-20260426/MEMORY.md.bak /home/piet/.openclaw/workspace/MEMORY.md
cp /home/piet/.openclaw/backup/atlas-kernel-v1-20260426/selection-DGLE6AvW.js.current /home/piet/.npm-global/lib/node_modules/openclaw/dist/selection-DGLE6AvW.js
systemctl --user restart openclaw-gateway.service
```
