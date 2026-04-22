# Sprint-M / Plan v1.2 — Session Handover — 2026-04-21

## Final Status Before Session Reset

Sprint-M remains `READY-WITH-KNOWN-GAPS`.

What is already settled:

- `registry.jsonl` was normalized enough for `registry-validate.py` to pass.
- `mc-critical-alert` is no longer a `B` gap. Live verification showed:
  - cron fires in the expected cadence
  - script exits cleanly
  - statefile is healthy
  - real alert deliveries succeeded with HTTP 204
- `memory-orchestrator.py` root cause was identified and minimally fixed:
  - the cron wrapper already held the phase lock
  - the Python script tried to lock the same path again
  - result was self-blocking on wrapped runs
  - internal re-lock was removed
  - wrapped dry-runs are now green again

## Current Live Constraint

There is an active parallel QMD scheduler proof being run by Claude bot.

Known live state:

- live crontab contains `15,45 * * * * /home/piet/.openclaw/scripts/qmd-native-embed-cron.sh`
- manual trigger of `qmd-native-embed` completed successfully
- Claude bot is monitoring the next cycles to prove the scheduler actually fires at `:15` and `:45`

Operational rule until that soak is finished:

- no more writes to
  - user crontab
  - `/home/piet/.openclaw/cron/registry.jsonl`
  - `/home/piet/.openclaw/scripts/qmd-native-embed-cron.sh`
  - `/home/piet/.openclaw/scripts/qmd-pending-monitor.sh`

Reason:

- the current bottleneck is evidence, not implementation
- changing the path while the 2h proof is running would invalidate the result

## Current Open Contract Gap

The remaining scheduler contract issue before continuing Plan v1.2 is:

- live `cron-reconciler.py --dry-run` is **not** green
- current drift is exactly one item:
  - `missing_in_registry`
  - live schedule `15,45 * * * *`
  - live command `/home/piet/.openclaw/scripts/qmd-native-embed-cron.sh`

So the next normalization task after the soak is not broad audit work. It is specifically:

1. decide whether `qmd-native-embed` is now part of the canonical active cron set
2. if yes, model it in `registry.jsonl`
3. if no, remove the live cron deliberately
4. rerun validator + reconciler

## Memory-Orchestrator Status

Current state:

- file: `/home/piet/.openclaw/workspace/scripts/memory-orchestrator.py`
- wrapped `hourly --dry-run`: green
- wrapped `nightly --dry-run`: green
- real hourly live-fire: still pending

Important note:

- the file is runtime-correct but still untracked in git
- this is repository hygiene debt, not an immediate runtime blocker

## Recommended Next Order

1. Let Claude bot finish the `qmd-native-embed` soak proof.
2. Normalize the `qmd-native-embed` registry drift.
3. Rerun:
   - `python3 /home/piet/.openclaw/cron/registry-validate.py`
   - `python3 /home/piet/.openclaw/cron/cron-reconciler.py --dry-run`
4. Verify one real `memory-orchestrator hourly` live-fire.
5. Only then continue the next Plan v1.2 work package.

## Start Prompt For Atlas

```text
Atlas — Session-Neustart mit engem Scope.

Lies zuerst:
- /home/piet/vault/03-Agents/sprint-m-v1.2-session-handover-2026-04-21.md
- /home/piet/vault/03-Agents/sprint-m-followup-status-2026-04-21.md

Wichtige Arbeitsregel:
- Kein Broad Review.
- Kein Reopening von Sprint-M.
- Keine Writes an QMD-Scheduler-Pfaden, solange der laufende 2h-Soak von Claude bot nicht abgeschlossen ist.

Nach dem Soak ist dein erster Job:
1. qmd-native-embed gegen registry.jsonl normalisieren
2. registry-validate.py + cron-reconciler.py --dry-run erneut prüfen
3. danach memory-orchestrator hourly live-fire verifizieren

Erwarte Fokus, keine Nebenbaustellen.
```
