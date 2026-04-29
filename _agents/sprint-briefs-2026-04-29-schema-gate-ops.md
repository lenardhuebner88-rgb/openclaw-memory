---
type: sprint-brief
date: 2026-04-29
status: in-progress
sprints: [S-SCHEMA-GATE-2, S-OPS-3]
owner: claude (autonomous, parallel-pass to Atlas V3 Hardening)
tags: [sprint-plan, r52, r53, r51-closure, jobs-json, delivery-routing]
---

# Sprint Briefs — S-SCHEMA-GATE-2 + S-OPS-3

## Context

Beide Sprints folgen direkt aus Round-4-Audit-Findings. **Atlas läuft parallel
V3 Hardening Gate 1** in MC-Source-Lane — diese zwei Sprints sind explizit
**out-of-band** und touchieren ausschließlich Scripts, Schema-Files, Vault-Docs.

**Strict scope-exclusions:**
- ❌ keine MC-Source-Edits (Atlas-Lane)
- ❌ kein Gateway-Restart
- ❌ keine direkten openclaw.json-Writes (runtime clobber-protection)
- ❌ keine model-routing-Änderungen
- ❌ kein V3-Dispatch

---

# Sprint S-SCHEMA-GATE-2: R52 + R51-Closure

**Owner:** claude (sre-expert role) | **Lens-Review:** post-deployment

## Goal

Schließe die strukturellen Schema-/Wipe-Drift-Lücken die heute (28.04. 15:29:54)
einen Crontab-Wipe ermöglichten und den R51-Validator nominell aber nicht voll
funktional ließen.

## Scope (3 Items)

### Item 1: R52 — Crontab Schema-Gate

**Pattern:** Pre-write diff-check + auto-rollback (analog R51 für openclaw.json).

**Deliverables:**
- `/home/piet/.openclaw/scripts/crontab-schema-gate.sh` — Wrapper-Script
- Daemon: monitors crontab via md5-hash polling (every minute)
- Detect-Patterns:
  - Line-count drop >50% (Wipe-Pattern wie 28.04.)
  - Total-bytes drop >50%
  - Loss of critical entries (memory-orchestrator, reapers, alerts)
- Action:
  - Backup current crontab to `/home/piet/.openclaw/backups/crontab-guard/<ts>.bak`
  - If schema-violation → restore from last-good backup
  - Discord-Alert via alert-dispatcher.sh
- Cron entry: `* * * * * flock -n /tmp/crontab-schema-gate.lock crontab-schema-gate.sh`

**Acceptance-Criteria:**
- AC1: Test with simulated wipe (1-line crontab) → auto-rollback to last-good
- AC2: Test with normal edit (1-line change) → accept + update last-good
- AC3: Test with critical-entry-loss (no memory-orchestrator) → alert + rollback
- AC4: Cron-entry runs every minute without lock-stampede
- AC5: Backup-rotation: keep last 24h of last-good snapshots

**Risk:** Low. Read-only scan + backup-based rollback. flock-protected.

### Item 2: openclaw.json Schema-Update + R51-jsonschema re-enable

**Background:** Schipped Schema (`/home/piet/.openclaw/schemas/openclaw.json.schema.json`)
sagt `model:string` und `runtime:enum`. Real runtime nutzt `model:object{primary,fallbacks}`.
R51-Validator hat schema-check deaktiviert (sonst rejected er live config).

**Deliverables:**
- Updated `openclaw.json.schema.json` reflecting real runtime shape:
  - `agents.list[*].model` als object mit primary/fallbacks
  - `runtime` field als optional (oder aus required entfernen)
  - `tools.exec` mit allowlist + safeBins
  - `models.providers.<name>.models[]` als string OR object
- `openclaw-config-validator.py` re-enable `jsonschema.validate` block
- Validator runs without errors against live config

**Acceptance-Criteria:**
- AC1: `python3 openclaw-config-validator.py` exits 0 against current config
- AC2: Schema rejects empty agents.list (validation_fail with code=2)
- AC3: Schema rejects bare `minimax/MiniMax` primary
- AC4: Schema accepts current production config

**Risk:** Low. Schema-File is static, no runtime impact. Validator check additive.

### Item 3: R53 — Vault-Frontmatter Schema-Gate

**Pattern:** Validate frontmatter consistency in vault docs (prevents
Index-Generator-Drift).

**Deliverables:**
- `/home/piet/.openclaw/scripts/vault-frontmatter-validator.py`
- Scans `/home/piet/vault/_agents/*.md` for required frontmatter:
  - `type` (one of: incident-report, sprint-brief, deployment-report, audit-report, decision-matrix, daily, rule-deployment)
  - `date` (ISO format)
  - `tags` (array)
- Reports drift in dedicated log
- Cron entry: `0 */6 * * * vault-frontmatter-validator.py`
- Discord-Alert if drift > N entries

**Acceptance-Criteria:**
- AC1: Scans all *.md files in /vault/_agents/ recursively
- AC2: Outputs JSON-formatted report with drift entries
- AC3: All today's docs (heute 7 deployed) pass validation
- AC4: Test with intentional drift → catches it

**Risk:** Very low. Read-only scan.

## Sprint Total Effort: 4-6h

---

# Sprint S-OPS-3: Operational Visibility

**Owner:** claude (sre-expert role) | **Atlas-Cleanup:** post-deployment

## Goal

Heile drei operative Lücken die Monitoring-Visibility + Alert-Routing einschränken:
jobs.json `last_run=null`, sre-expert-Cron channel-routing-bug, R48 stale-tasks-Backlog.
Plus: Docstring-Coverage für 5 critical scripts.

## Scope (4 Items)

### Item 1: jobs.json last_run External Tracker

**Background:** Alle 25 openclaw-internal jobs zeigen `last_run=null` trotz
sichtbarer runs in `/cron/runs/*.jsonl`. openclaw-runtime persistiert nicht.
Direkter Code-Fix wäre Runtime-Patch — risky.

**Approach:** Externer Tracker-Script aggregiert aus `/cron/runs/*.jsonl` und
schreibt `/home/piet/.openclaw/cron/runs-tracker.jsonl` (alternative Quelle für
Monitoring).

**Deliverables:**
- `/home/piet/.openclaw/scripts/cron-runs-tracker.py`
- Reads all `/cron/runs/*.jsonl` files
- For each unique jobId: latest ts, status, duration, model, provider
- Writes consolidated state to `/cron/runs-tracker.jsonl`
- Cron entry: `*/5 * * * * cron-runs-tracker.py`

**Acceptance-Criteria:**
- AC1: Tracker scans alle 30+ run-files
- AC2: Output enthält für jeden bekannten jobId: last_run_ts, last_status, last_duration_ms
- AC3: Idempotent (re-run same data produces same output)
- AC4: Output usable for r48-board-hygiene + cron-health-audit

**Risk:** Very low. Read-only aggregation.

### Item 2: delivery.channel Routing-Fix

**Background:** sre-expert cron-jobs schlagen 5/7 mal fehl mit
`Channel is required when multiple channels are configured: discord, telegram`.
Cron-runs erfolgreich (`status=ok`), aber delivery silent failure.

**Investigation:**
- Wo wird `delivery.channel` gelesen?
- Welcher Default ist sinnvoll für sre-expert (discord channel-id?)
- Gibt es Per-Cron-Override-Mechanismus in jobs.json?

**Deliverables:**
- Investigation findings dokumentiert
- Falls Fix in script-only: Patch deployen
- Falls Fix nur via jobs.json-Edit (runtime-clobbered): operator-action documentation

**Acceptance-Criteria:**
- AC1: Root cause klar identifiziert
- AC2: Either fix deployed OR operator-action documented with exact steps
- AC3: After fix, sre-expert delivery success rate >90% in next hour

**Risk:** Medium. Could touch openclaw runtime config (clobber-risk) — fall back to docs-only.

### Item 3: R48 Stale-Tasks Approach

**Background:** 35 task-status=`failed` seit 22.04. State-machine forbids
`failed→canceled`. Mass-close via API blocked.

**Approach:** 3 sub-options to explore:
- A: Look for an admin-close API path (Atlas hat es 12:48 demonstriert für
  status=`assigned`)
- B: Investigate `executionState` or `dispatchState` mutation paths
- C: Document as operator-action (Forge-Sprint)

**Deliverables:**
- Investigation: read /api/tasks/*/route.ts to find admin-close path
- If found: mass-execute on 15 very_old tasks (>7d)
- If not found: clean operator-handoff doc with each task's age + agent + title

**Acceptance-Criteria:**
- AC1: Either 15 stale tasks closed via canonical API path
- AC2: OR clear documentation why API doesn't support + operator-recommendation

**Risk:** Low. Read-only investigation; mutation only via canonical API.

### Item 4: Docstring + Vault-Operator-Doc-Coverage

**Background:** Round-4 added 2 docstrings (cost-alert-dispatcher,
session-size-guard). Audit-2 had identified 5 missing — re-verify the others
(auto-pickup, mc-critical-alert, r49-claim-validator) and add if missing.
Plus: vault-doc for openclaw-config-validator.py (R51-Implementation, dünn dokumentiert).

**Deliverables:**
- Docstring-coverage check on all 13 critical scripts
- Add missing docstrings (text-only edits)
- Vault-doc: `/vault/_agents/r51-validator-operator-doc.md` (How to use, Failure-modes, Test patterns)

**Acceptance-Criteria:**
- AC1: All 13 critical scripts have ≥5-line docstring with Purpose/Schedule/Failure
- AC2: R51-Operator-Doc deployed in vault
- AC3: py_compile / bash -n pass for all edited scripts

**Risk:** Very low. Text-only.

## Sprint Total Effort: 3-4h

---

# Combined Execution Plan

**Order (parallelizable where independent):**

1. **First:** Sprint-Briefs Vault-Doc (this file)
2. **R52** Crontab-Schema-Gate (independent, deliver first)
3. **Schema-Update** for openclaw.json (parallel-able with R52)
4. **R51-Closure** validator (depends on Schema-Update)
5. **R53** Vault-Frontmatter (independent)
6. **jobs.json last_run tracker** (independent)
7. **delivery.channel** investigation + fix
8. **R48** investigation + action
9. **Docstrings** verify + add
10. **Closure**: Vault-Doc + Discord Report

**Total estimated effort:** 7-10h

**Blast-radius mitigation:**
- All deliverables are scripts or schema-files (no runtime mutation)
- Each deliverable backed up before deploy
- Test against current state before activating cron
- flock + atomic writes throughout
