# Cost-Anomaly Deep-Dive — 2026-04-19
**Agent:** Lens (efficiency-auditor)
**Task:** Sprint-A/A1 Sub-Task — Cost-Anomaly Deep-Dive
**Status:** COMPLETE

---

## 1. Anomaly Identification

**Provider:** MiniMax (prepaid pool, EUR 40/month)
**Model:** `MiniMax-M2.7-highspeed` (and `MiniMax-M2.7`)
**Agents in scope:** `main` (Atlas) + `efficiency-auditor` (Lens) — hardcoded in `MINIMAX_AGENTS` in `costs-data.ts:619`
**Primary anomaly metric:** TPM rate limit + cash pool dual overrun

### Dual Overrun Confirmed by Efficiency-Auditor Task f225df08 (2026-04-18):
| Metric | Value | Limit | Overrun |
|---|---|---|---|
| **TPM Rate** | 55M tokens | 20M TPM | **275%** (rate-limit throttling) |
| **Cash Pool** | EUR 72.46 | EUR 40/mo | **181%** (EUR +32.46 actual overspend) |

**Source of `usedCost`:** `loadAgentSessionUsage()` in `costs-data.ts` reads session JSONL files from `~/.openclaw/agents/{main,efficiency-auditor}/sessions/`. The cost field reflects actual MiniMax API response costs, not a theoretical calculation.

**"$362/$3" reference in Sprint Plan:** The $362 figure in the plan likely refers to an accumulated implied cost (e.g., 55M tokens × MiniMax rate) or a 30-day accumulated figure. The $3 is the pay-per-use daily budget. The primary actionable signal is the MiniMax prepaid pool overrun (EUR 72.46 vs EUR 40), not the implied-token-cost figure.

---

## 2. Classification

**Type: Real spend regression — not noise, not config ambiguity.**

- **Not noise:** The 181% pool overrun is a confirmed cash overspend (EUR 72.46 billed against EUR 40 pool). This is real money beyond the prepaid allocation.
- **Not config/routing issue per se:** The routing to MiniMax is intentional (it's the fallback model). The problem is volume — too many tokens routed through MiniMax.
- **Root cause:** High token-volume sessions in `main` and `efficiency-auditor` agents consuming MiniMax at 2.75× the monthly TPM rate. Likely driven by large-context bootstrap operations, QMD embedding, or multi-agent orchestration loops.

---

## 3. Recommended Action: FIX/FLIP

**Action: Account/Provider follow-up (MiniMax prepaid pool)**

**Rationale:**
The pool is already 181% exhausted mid-month (April 19). At current burn rate (EUR 72.46 in ~19 days = ~EUR 3.8/day), the pool will be empty within days. No automatic Discord alert is firing for the cash overrun — only the TPM rate alert fires (`268%`-style text).

**Specific steps (for Operator/Forge to execute):**
1. **Immediate:** Check if MiniMax pool has auto-recharge or what happens at exhaustion (hard block? throttle?)
2. **Short-term (1-2 days):** Reduce MiniMax token volume — ensure `main` agent uses GPT-5.4 flatrate as primary, not MiniMax. MiniMax should only be the true fallback.
3. **Monitoring:** Ensure `cost-alert-dispatcher.py` (already in integrity-check) fires a Discord alert specifically for **pool-exhaustion forecast** (not just TPM alert) so the operator gets 24-48h warning before pool empties.
4. **Next month:** Consider increasing pool size OR enforce tighter MiniMax routing rules.

**What NOT to do (constraints respected):**
- No openclaw.json writes from this analysis
- No broad refactors

---

## 4. Evidence Sources
- `src/lib/costs-data.ts:619-625` — MINIMAX_AGENTS and MINIMAX_LIMITS constants
- `src/lib/costs-data.ts:768-833` — `getMiniMaxUsage()` and subscription status logic
- Log: `logs/auto-pickup-runs/f225df08__efficiency-auditor__1776444361.log` — efficiency-auditor Phase 1 result showing EUR 72.46 / 181% pool
- `src/lib/cost-telemetry.ts` — telemetry write path (cost-events.jsonl is stale since 2026-03-27, but session-based cost reading is live)
- `vault/03-Agents/atlas-costs-cockpit-v2.md` — full billing mode analysis (confirmed MiniMax is PREPAID mode)

---

## 5. Sprint-A Recommendation

**Sub-A1 (this task) is DONE.** Decision documented above.

For Sprint-A completion: Forge should execute the FIX/FLIP action (check pool exhaustion policy + ensure Discord alert for cash overrun specifically). This is a real regression requiring provider follow-up, not a muteable noise event.

**Next pointer for Atlas/Sprint-A result receipt:**
- Root cause: MiniMax `MiniMax-M2.7-highspeed` in `main` + `efficiency-auditor` sessions — real cash overrun (EUR 72 vs EUR 40 pool, 181%)
- Confounding factor: TPM metric (275%) is displayed but pool cash metric is the actionable one
- Required action: Pool exhaustion policy check + Discord alert for cash overrun forecast
