---
type: sprint-brief
date: 2026-04-29
status: pending-go
sprint_id: S-FOLLOWUP-1
title: "Follow-Up Autonomy Recovery + E2E Test Suite"
owner: claude (or Atlas/Forge per-item)
effort: 2-3 days
discord_announcement: "msg 1499084964858429510 (ch 1495737862522405088)"
related:
  - "[[autonomy-audit-2-agent-2026-04-29]]"
  - "[[stabilization-2026-04-29-full]]"
tags: [sprint-brief, followup, autonomy, e2e-tests, receipt-materializer, autonomy-self-healing]
---

# Sprint S-FOLLOWUP-1 — Follow-Up Autonomy Recovery + E2E

## IST-Analyse

**Was vorhanden ist:**
- `receipt-materializer.ts` (438 Zeilen) — schemagated bei `schema_version: 'v1.1'`, MAX_2-followups, decisionKey-dedup, approval-class-driven gates
- `autonomy-self-healing.ts` (432 Zeilen) — risk-tiers A0-A5, policy-decisions, taskCandidates
- `AUTONOMY_MATERIALIZER=on` ✅ aktiv (systemd drop-in `autonomy-materializer.conf`)
- API-Endpoints: `/autonomy-approve`, `/autonomy-reject`, `/recover`, `/recovery-action`, `/bulk`, `/admin-close`
- Owner-Inference via Regex (pixel/forge/lens/james/spark/main)

**Was NICHT funktioniert (gemessen):**
- 🔻 Nur **24 auto-Tasks in 19 Tagen** = 0.06/Stunde (von 738 total = 3.3%)
- 🔻 autonomy-self-healing hat **3 LIVE findings** RIGHT NOW (cost:flatrate-rate-spike + 2 mehr) → bleibt in `mode=dry-run, readOnly=true`
- 🔻 Schema-v1.1-Adoption nicht messbar (kein Receipt-Storage gefunden in `data/`)
- 🔻 Owner-Inference ist naive Regex → fehleranfällig
- 🔻 7 von 24 atlas-autonomy-tasks ended `canceled` (29%) → noisy generation

**Root Cause:** Atlas + Worker-Agents emittieren ihre Sprint-Outcomes selten als `v1.1 schema_version` mit `next_actions[]`-Array. → receipt-materializer triggert nicht. + autonomy-self-healing ist by-design dry-run-only.

## SOLL-Zustand

1. **≥80% aller Atlas/Worker terminal-receipts emittieren v1.1 schema** mit `next_actions[]`
2. **autonomy-self-healing live-mode** für `A0` (info) und `A1` (propose-readonly) Risk-Tiers
3. **Owner-Inference 2-stufig:** Regex-fallback + agent-skill-mapping per task-class
4. **Discord-Approval-Flow:** atlas-autonomy drafts posten in Channel mit ✅/❌ buttons
5. **E2E-Test-Suite** mit 6 Use-Cases als CI-Gate
6. **Dashboard:** follow-up-conversion-rate + accept-rate sichtbar in MC-UI

## Sprint-Plan (10 Items, Step-by-Step)

### Phase 1 — Foundation + Measurement (Tag 1, 6h)

**S1.1 Receipt-Schema-Audit (1h)** [READ-ONLY]
- File: `scripts/receipt-schema-audit.py` (NEW)
- Scans last 48h agent trajectory.jsonl for terminal-receipts
- Reports: % v1.1 / % v0 / % no-schema, per-agent breakdown
- Output: `/workspace/state/receipt-schema-audit.json`
- AC: baseline-metrics für sprint-tracking

**S1.2 Atlas Prompt-Template v1.1 (1.5h)** [SCRIPT-ONLY]
- File: `vault/skills/sprint-outcome/SKILL.md` (UPDATE oder NEW)
- Definiert v1.1-Schema explizit: schema_version, status, next_actions[]
- Template einbinden in Atlas-Master-Prompt-Skill
- AC: atlas-master-heartbeat (1h-cycle) emittiert v1.1 messbar in Atlas-trajectory

**S1.3 Worker-Agents Prompt-Templates v1.1 (1.5h)** [SCRIPT-ONLY]
- Update für: forge, pixel, lens, james, spark
- AC: alle Worker-Agents emittieren v1.1 bei `EXECUTION_STATUS=done|partial|failed`

**S1.4 Receipt-Schema-Wrapper (2h)** [SCRIPT-ONLY]
- File: `mission-control/src/lib/receipt-schema-wrapper.ts` (NEW)
- Wenn agent-result kein v1.1 → synthesize v1.1 aus textual `Follow-up:` / `Recommendation:` Patterns
- Fallback owner via Regex (existing `inferOwnerFromText`)
- AC: backwards-compat für bestehende v0-Patterns

### Phase 2 — Activation + Gate-Tuning (Tag 2 vormittag, 4h)

**S2.1 autonomy-self-healing live-mode für A0/A1 (1.5h)** [SCRIPT-ONLY, REVERSIBLE]
- File: `mission-control/src/lib/autonomy-self-healing.ts` (UPDATE)
- Add: `MODE=enforce` env-flag (default `dry-run` for backwards-compat)
- Wenn `MODE=enforce` AND `riskTier in [A0, A1]` → `readOnly=false`, create draft-task
- AC: 3 LIVE findings (cost:flatrate-rate-spike etc) werden zu drafts mit `operatorLock=true`

**S2.2 Owner-Inference 2-stufig (1.5h)** [SCRIPT-ONLY]
- File: `mission-control/src/lib/receipt-materializer.ts` (UPDATE Zeile 116-165)
- Stufe 1: existing Regex-inferOwnerFromText
- Stufe 2: `task-class → agent-skill`-mapping (z.B. ui-bug → frontend-guru, perf-issue → efficiency-auditor)
- AC: <5% Owner-Mismatch in next 24h auto-tasks

**S2.3 Discord-Approval-Flow Integration (1h)** [SCRIPT-ONLY]
- File: `scripts/discord-followup-approval-bridge.py` (NEW)
- Cron: `*/5 * * * *` — finds drafts mit `lockReason='atlas-autonomy-awaiting-approval'`, postet zu Channel mit Embed (title/owner/risk/decisionKey) + reaction-buttons (✅ approve / ❌ reject)
- Bot-handler ruft existing `/api/tasks/[id]/autonomy-approve` oder `/autonomy-reject` API
- AC: end-to-end flow draft → discord-prompt → operator-click → assigned

### Phase 3 — E2E Test Suite (Tag 2 nachmittag, 4h)

**S3.1 E2E Test Use-Cases (3h)** [SCRIPT-ONLY]

File: `mission-control/tests/e2e/followup-autonomy.test.ts` (NEW)

**UC1 — Happy Path:** Atlas emittiert v1.1 receipt mit 2 next_actions (`safe-read-only` + `gated-mutation`)
- ✅ 2 tasks created
- ✅ #1: status=`assigned` (safe-read-only)
- ✅ #2: status=`draft`, operatorLock=true (gated-mutation)
- ✅ decisionKey-dedup verhindert duplicate

**UC2 — Schema-v0-Fallback:** Agent emittiert v0 ohne next_actions
- ✅ Fallback: receipt-schema-wrapper synthesiert v1.1
- ✅ Mind. 1 follow-up via FOLLOWUP_SIGNAL_PATTERNS regex

**UC3 — autonomy-self-healing A1-finding:** cost-anomaly mit risk_tier=A1
- ✅ create-draft-task mit `operatorLock=true` und `policyDecision='draft-only'`
- ✅ assignedAgent=`efficiency-auditor` (von buildTaskCandidate)

**UC4 — Operator-Approval-Flow:** Operator clickt ✅
- ✅ `/autonomy-approve` API patcht status=`assigned`, dispatchState=`queued`
- ✅ auto-pickup spawnt worker (via existing dispatch-flow)
- ✅ Telemetry-Event `task.followup.approved`

**UC5 — Duplicate-Block:** 2× identical decisionKey
- ✅ 1. Task created
- ✅ 2. wird `skipped: duplicate-decisionKey`

**UC6 — Quality-Gate-Limit:** 3 next_actions im receipt
- ✅ #1+#2 created
- ✅ #3 wird `skipped: subtask-limit-exceeded` (MAX_MATERIALIZED_NEXT_ACTIONS=2)

**S3.2 Test-Fixtures + Mock-Agents (1h)** [SCRIPT-ONLY]
- File: `mission-control/tests/e2e/fixtures/agent-results.fixture.ts`
- 6 fixture-receipts (1 per UC)
- Mock /api/tasks responses + autonomy-self-healing-data
- AC: `npm test e2e/followup-autonomy.test.ts` → 6/6 PASS

### Phase 4 — Observability + Closure (Tag 3 vormittag, 2h)

**S4.1 Follow-Up-Dashboard (1h)** [SCRIPT-ONLY]
- File: `mission-control/src/app/api/followup-stats/route.ts` (NEW READ-ONLY)
- Returns: 24h-stats per autoSource (`atlas-autonomy`, `signal-followup`)
- Counts: created, draft, assigned, completed, canceled, accept-rate
- AC: GET endpoint returns 200 mit JSON-payload

**S4.2 Sprint-Closure-Doc + Discord-Report (1h)** [SCRIPT-ONLY]
- Vault: `_agents/sprint-closure-followup-1-YYYY-MM-DD.md`
- Discord: per-AC verification + before/after metrics

## Acceptance-Criteria Sprint-Total

- [ ] **AC-1:** ≥80% Atlas/Worker terminal-receipts emittieren v1.1 (gemessen via S1.1)
- [ ] **AC-2:** autonomy-self-healing erzeugt drafts für ≥1 A0/A1-finding pro 24h
- [ ] **AC-3:** Discord-Approval-Flow end-to-end funktional (UC4 PASS)
- [ ] **AC-4:** E2E-Test-Suite 6/6 UC PASS
- [ ] **AC-5:** Dashboard-Endpoint GET /followup-stats liefert valide JSON
- [ ] **AC-6:** Sprint-Verlauf: ≥10× new auto-tasks erstellt (vs. 24 in 19d Vergangenheit)
- [ ] **AC-7:** Cancel-Rate <20% (heute 29% von 24 atlas-autonomy-tasks)
- [ ] **AC-8:** Owner-Mismatch <5% (manual review von 10 random auto-tasks)
- [ ] **AC-9:** Reversibel: `MODE=dry-run` env rollback in <60s
- [ ] **AC-10:** Vault-Doc + Discord-Report deployed

## Strict Scope-Constraints

- ❌ kein Atlas/Worker-Lane (außer prompt-template-update)
- ❌ kein openclaw.json edit (clobber-protection)
- ❌ kein Gateway-Restart (außer **eine** controlled MC-restart für autonomy-self-healing live-mode S2.1)
- ❌ kein modelrouting/cron-config (außer 1× neue cron in S2.3 für Discord-bridge)
- ✅ alles über existing API-Endpoints + Script-Edits
- ✅ feature-flag MODE=enforce, default off → reversibel

## Recommended Owners

- **Atlas (orchestrator):** S1.2 prompt-template + S2.3 Discord-bridge dispatch
- **Forge (sre-expert):** S1.4 wrapper + S2.1 self-healing-mode + S4.1 dashboard
- **Pixel (frontend-guru):** S2.2 owner-inference enhancement
- **Lens (efficiency-auditor):** S1.1 schema-audit + final-review
- **claude (parallel-pass):** S3.1+S3.2 E2E-test-suite (least context-bound)

## Effort + Risk

- **Total:** 2-3 Tage (16-20h)
- **Risk:** LOW-MED (alle Änderungen reversibel via feature-flags + git-revert)
- **Blast-Radius:** isoliert (autonomy-Pfad, kein dispatch-direct-modification)

## Status

**PENDING-GO** — Discord-Announcement gepostet (msg 1499084964858429510). Ready für Operator-GO oder Atlas-Sprint-Dispatch.
