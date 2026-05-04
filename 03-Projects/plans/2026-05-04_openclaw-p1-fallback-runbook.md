# OpenClaw P1 Fallback Runbook

Date: 2026-05-04
Owner: Atlas
Related tasks:
- `c79041bd-9f47-452a-b2f2-2969f773e1ce` `[P1] Atlas Discord Metadata Slimming + Dedupe`
- `e97a5df5-c00d-43cb-ac05-76d823af4d92` `[P1.1] Atlas Dedupe Perf Hardening`

## Purpose

Provide a clean fallback path if P1/P1.1 improves prompt size but causes unacceptable live regressions in Atlas/Discord runtime behavior.

## Current change set

Runtime file touched by P1:
- `/home/piet/.openclaw/npm/node_modules/openclaw/dist/get-reply-BQ4hxDzS.js`

Observed P1 result:
- Metadata payload: `803 B -> 425 B` (`-47.07%`)
- Media note payload: `861 B -> 647 B` (`-24.85%`)
- Prompt-size proxy: `1664 B -> 1072 B` (`-35.58%`)
- Local render microbench: `55.43 ms -> 290.89 ms` (`+424.79%`)

Config backup already present:
- `/home/piet/.openclaw/backups/openclaw-json/openclaw.json.bak-20260504-thinking-defaults-124623`

## Fallback triggers

Fallback is justified if one or more of these become true after P1/P1.1 rollout:

1. Atlas Discord p95 latency regresses materially and stays elevated across repeated checks.
2. Attachment-heavy chats show visible responsiveness degradation.
3. Edge-context loss appears in live behavior because metadata slimming removed fields that are operationally needed.
4. Duplicate suppression causes confusing references without enough first-message context.
5. Gateway CPU cost from the local string-builder path outweighs the prompt-byte reduction in real traffic.

## Fallback levels

### Level 1: Keep metadata slimming, disable dedupe path

Use this if prompt reduction is good but the dedupe cache/reference path is the regression source.

Expected effect:
- Preserve most metadata savings.
- Remove fingerprint/cache overhead and `ref:<fingerprint>` behavior.

### Level 2: Revert to pre-P1 runtime behavior

Use this if live behavior is unstable or semantically degraded.

Expected effect:
- Restore original metadata/media formatting behavior.
- Lose the P1 prompt-size win until a safer redesign is ready.

## Safe execution steps

1. Snapshot current runtime file before any revert.
2. Apply the smallest possible rollback:
   - first prefer Level 1
   - use Level 2 only if Level 1 is insufficient
3. Restart Gateway.
4. Re-run the same verification matrix.
5. Confirm live health before calling the rollback complete.

## Verification after fallback

Run these checks after any fallback:

1. `openclaw gateway health`
2. Atlas/Forge config sanity:
   - `jq -r '.agents.list[] | select(.id=="main" or .id=="sre-expert") | [.id,.thinkingDefault,.reasoningDefault,.fastModeDefault] | @tsv' /home/piet/.openclaw/openclaw.json`
3. Mission Control health:
   - `curl -sS http://127.0.0.1:3000/api/health`
4. Repeat the same Atlas test matrix used for P1:
   - metadata payload
   - media note payload
   - prompt-size proxy
   - local render microbench
5. Confirm no new dispatch/receipt anomaly:
   - `orphanedDispatches=0`
   - `pendingPickup=0` after idle period

## Decision rule

- If prompt-size win remains and p95 latency normalizes after Level 1, keep Level 1 and continue with bounded-cache hardening later.
- If semantics or latency are still bad after Level 1, execute Level 2 and re-open redesign as a new task.
- Do not change model chain, `fastMode`, or Atlas/Forge thinking defaults as part of this fallback. Those are separate controls.

## Notes for operators

- The P1 risk is not data loss; it is runtime quality/performance tradeoff.
- The most likely emergency move is partial rollback of dedupe logic, not a full system rollback.
- Keep the rollback narrow. Avoid mixing runtime fallback with unrelated config tuning.
