---
type: rule-deployment
status: live
deployed: 2026-04-29
rule_id: R51
tags: [governance, schema-gate, openclaw-config, defensive-programming]
supersedes_pattern: openclaw-config-guard-v1
related:
  - "[[stabilization-2026-04-29-full]]"
  - "[[feedback_system_rules]]"
---

# R51 — Schema-Gate für openclaw.json Writes

## Purpose

Verhindert das **Round-2-Audit P0-3 Pattern**: openclaw-config-guard akzeptierte
**28 schema-violating mutations** in 9 Tagen als VALID, weil der einzige Check
ein `grep "Config invalid"` auf doctor-output war.

R51 fügt eine **Pre-Acceptance-Validation-Stufe** hinzu, die structural + invariant
checks macht, BEVOR doctor's string-match greift.

## Files

| Path | Role |
|---|---|
| `/home/piet/.openclaw/scripts/openclaw-config-validator.py` | NEW: structural + invariant validator |
| `/home/piet/.openclaw/scripts/openclaw-config-guard.sh` | UPDATED: ruft validator vor doctor |
| `/home/piet/.openclaw/backups/openclaw-config-guard/openclaw.json.last-good` | Auto-rollback target |
| `/tmp/openclaw-config-guard-validator.log` | Validator decision log |

## Validation Layers (in order)

1. **Existence + size** — file must exist, ≥5KB
2. **Size-shrink** — reject if shrunk >50% vs last-good (catches wipe-attempts)
3. **JSON parse** — must be valid JSON
4. ~~Schema validation~~ — DISABLED 2026-04-29 (shipped schema is outdated:
   sagt `model:string`, runtime ist `model:object`. Re-enable after schema-update sprint.)
5. **Invariants:**
   - `agents.list` ≥ 3 entries (we have 6)
   - Each agent: `id` + `model.primary` (string) + valid slug format `^[a-z][a-z0-9-]*\/[A-Za-z0-9._\/-]+$`
   - Each `model.fallbacks` entry: same slug format
   - `spark.primary` MUST start with `openai-codex/` (operator-policy)
   - `agents.defaults.model.primary` valid slug
   - `openrouter/auto` MUST be LAST in any fallback chain that contains it
6. **Legacy doctor string-check** (kept as second-line)

## Action on Failure

```
VALIDATOR_FAIL → Auto-rollback to LAST_GOOD
              → Update STATE_FILE with rolled-back hash
              → Discord alert via alert-dispatcher.sh
              → Exit 0 (don't break cron)
```

## Test Results

Tested against live config 2026-04-29 12:35 UTC:

```
INFO schema_check_skipped reason=outdated_schema (model:string vs runtime:object)
VALIDATION_OK size=32489 agents=6 ts=2026-04-29T10:35:10Z
VALIDATOR_EXIT=0
```

Guard run with cleared state:
```
2026-04-29T10:35:10Z INIT hash=604e793a2ce3118b47b78051569cf39f
GUARD_EXIT=0
```

Last-good written, state-file synced. ✅

## Known Limitations

1. **Schema validation skipped** until `openclaw.json.schema.json` is brought
   in sync with current runtime (`model` is object, not string).
2. **Crontab is NOT covered** by R51 — separate scope. Crontab-Wipe-Pattern
   (28.04. 15:29:54) needs analogue R52 candidate (pre-write diff-check on
   `crontab -l` output before applying).
3. **Validator runs every minute** (config-guard cron `* * * * *`) — minimal
   overhead but adds ~50ms per cycle. Acceptable.

## Future Hardening Candidates

- **R52 Crontab-Schema-Gate** — analog für crontab-Writes (catch wipe early)
- **R53 Vault-Schema-Gate** — analog für `/vault/03-Agents/_VAULT-INDEX.md`
- **Schema sync** — bring `openclaw.json.schema.json` in sync mit runtime,
  re-enable jsonschema-Check
- **Pre-write hooks** — instead of post-write rollback, intercept `openclaw config edit`
  itself with validation
