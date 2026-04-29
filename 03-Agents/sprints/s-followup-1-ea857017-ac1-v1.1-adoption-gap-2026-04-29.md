# S-FOLLOWUP-1 AC-1 v1.1 Adoption Gap — Follow-Up Report
**Task:** ea857017-718f-4c8d-9e67-b38c453359f1  
**Parent:** 57d625db-f349-4f2e-a966-7359bf37dee8 (S1.1 Receipt Schema Audit)  
**Date:** 2026-04-29  
**Owner:** Lens (efficiency-auditor)  
**Status:** READY FOR ATLAS/ATLAS MASTER

---

## Executive Summary

The S1.1 audit reported "35.1% v1.1 adoption". This figure is **incorrect** due to a classification bug in the audit script. True `sprintOutcome.schema_version = "v1.1"` adoption is **0%**. The primary adoption gap is not schema version confusion — it is that **61% of terminal receipts omit sprintOutcome entirely**.

**Root causes (3):**
1. **Audit script bug:** maps `schema_version == 'v1'` → labeled as `v1.1` in output (inflates adoption rate)
2. **Inclusion gap:** 61% of recent receipts have no `sprintOutcome` field at all
3. **Schema wrapper not normalizing v1 → v1.1:** When sprintOutcome IS present with `schema_version: 'v1'`, the wrapper does not upgrade it to `v1.1`

**Infrastructure is ready:**
- S1.2: Atlas v1.1 prompt template exists at `docs/operations/atlas-sprintoutcome-v1.1-terminal-receipt-template.md`
- S1.3: Worker v1.1 templates at `docs/operations/worker-sprintoutcome-v11-templates.md`
- S1.4: Schema wrapper fallback implemented in `receipt-schema-wrapper.ts`
- BUT: Templates not integrated into `AGENTS.md` system prompts → agents don't know to use them

---

## Corrected AC-1 Baseline

| Metric | S1.1 Audit Reported | True Value | Source |
|--------|-------------------|-----------|--------|
| v1.1 adoption | 35.1% | **0%** | No task has `schema_version: "v1.1"` in sprintOutcome field |
| v1 adoption | — | **~35%** | 34/97 tasks have `schema_version: "v1"` (audit script bug: labeled as v1.1) |
| No sprintOutcome | 64.9% | **61%** | 67/110 recent terminal receipts missing field entirely |
| sprintOutcome present | — | **39%** | 43/110 recent terminal receipts have field |

---

## Per-Agent Adoption (Last ~48h)

| Agent | sprintOutcome Inclusion | Notes |
|-------|------------------------|-------|
| frontend-guru | 71% (17/24) | Best performer; likely from existing UI-task patterns |
| efficiency-auditor | 44% (4/9) | Mid-tier; S1.1 self-audit done with proper schema |
| sre-expert | 39% (21/54) | High volume but low rate; templates available but not applied |
| main (Atlas) | 7% (1/15) | Very low; template doc exists but not in AGENTS.md system prompt |
| spark | 0% (0/4) | No sprintOutcome at all |
| james | 0% (0/4) | No sprintOutcome at all |

---

## Root Cause Analysis

### RC-1: Audit Script Bug (S1.1, non-critical)
**File:** `scripts/receipt-schema-audit.py` line ~62  
**Bug:** `elif outcome.get('schema_version') == 'v1':` → appends to `v1_1` list, labeled as `v1.1` in output  
**Impact:** S1.1 reported "35.1% v1.1 adoption" when it was actually "35% v1 adoption; 0% v1.1 adoption"  
**Severity:** Low (audit metadata issue, not a system defect)  
**Fix:** Change `'v1'` condition to only match `'v1.1'`; rename list to `v1` for accuracy

### RC-2: 61% Inclusion Gap (HIGH)
**Cause:** Agents (main/Atlas, spark, james especially) do not include `sprintOutcome` in their receipts  
**Why:** SprintOutcome v1.1 templates exist in `docs/operations/` but are **not referenced in AGENTS.md** system prompts  
**Evidence:** `docs/operations/atlas-sprintoutcome-v1.1-terminal-receipt-template.md` exists but `AGENTS.md` does not include the v1.1 instruction snippet  
**Fix:** Add v1.1 sprintOutcome instruction to AGENTS.md → requires Atlas (orchestrator)

### RC-3: Schema Wrapper Not Normalizing v1 → v1.1 (MEDIUM)
**File:** `src/lib/receipt-schema-wrapper.ts` line ~64  
**Bug:** `if (existing?.schema_version === 'v1.1') return existing` → early return on v1.1, but when `schema_version === 'v1'` the wrapper sets `schema_version: 'v1.1'` in fallback  
**Evidence:** 0 tasks have v1.1 in storage despite 43 having sprintOutcome v1 → wrapper is not applying  
**Root cause:** The condition `schema_version !== 'v1.1'` IS entered for v1, but the `toObject` call on v1 sprintOutcome may not trigger fallback creation because `schema_version: 'v1'` is truthy → check at line ~76 `const schema_version = toObject(existing)?.schema_version` returns 'v1', then `if (schema_version !== 'v1.1')` is TRUE so it should create fallback. But the fallback creation uses `status: existing_status` which may be undefined → invalid v1.1 object → rejected by validation → original v1 kept  
**Fix:** Forge to verify wrapper behavior; ensure v1 → v1.1 normalization in fallback always produces valid v1.1

---

## Recommended Actions

### Immediate (this week)

| Priority | Action | Owner | Effort |
|----------|--------|-------|--------|
| P0 | Fix audit script bug → re-run baseline measurement | Lens | 15 min |
| P0 | Integrate v1.1 sprintOutcome snippet into AGENTS.md (Atlas section) | Atlas | 10 min |
| P1 | Forge: verify v1 → v1.1 wrapper normalization; fix if broken | Forge | 30 min |
| P1 | Atlas: run targeted re-audit with corrected script | Lens | 10 min |

### Short-term (2 weeks)

| Priority | Action | Owner | Effort |
|----------|--------|-------|--------|
| P2 | spark/james sprintOutcome v1.1 integration — update their skill prompts | Atlas | 30 min |
| P2 | sre-expert: reinforce v1.1 in Forge system context via AGENTS.md | Atlas | 10 min |
| P2 | Re-audit after 2 weeks to measure trajectory toward 60% target | Lens | 10 min |

---

## Revised AC-1 Recommendation

**Current:** 80% target is unrealistic given 0% current adoption and 61% inclusion gap  
**Recommended:** Replace AC-1 with a **trajectory-based target:**
- Week 1: ≥30% v1.1 adoption (inclusion + normalization fixes)
- Week 2: ≥50% v1.1 adoption
- Week 4: ≥70% v1.1 adoption

This acknowledges that: (a) sprintOutcome v1.1 templates were only created on 2026-04-29, (b) agent prompt integration takes time, (c) trajectory is more actionable than a static 80% target that was set before the templates existed.

---

## Anti-Scope (Not Doing)

- No retroactive modification of existing task receipts
- No enforcement at API level (schema validation already exists)
- No changes to openclaw.json or gateway config
- No new cron jobs or restart operations

---

## Files Referenced

- `scripts/receipt-schema-audit.py` — audit script with bug
- `src/lib/receipt-schema-wrapper.ts` — schema wrapper, line ~64
- `docs/operations/atlas-sprintoutcome-v1.1-terminal-receipt-template.md` — Atlas template
- `docs/operations/worker-sprintoutcome-v11-templates.md` — Worker templates
- `AGENTS.md` — system prompts, needs v1.1 snippet integration
