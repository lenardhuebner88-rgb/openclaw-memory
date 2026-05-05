---
title: 04-Sprints Status Index
status: index
last_update: 2026-05-02
maintained_by: claude (manual until cron-sprint-index-generator deployed)
source_of_truth: true
purpose: Single canonical view of all sprint status. Newer than READMEs/AGENTS.md.
---

# 04-Sprints — Canonical Status Index

> **Read this first.** This file is the operator-facing source of truth for "what is open, what is done, what should I dispatch next".  
> The folders `planned/` `active/` `closed/` `superseded/` `reports/` are the storage; this file is the projection.  
> Whenever you close, supersede, or open a sprint, **update this index in the same commit**.

**Last full audit:** 2026-04-30 (post-update-2026.4.27).  
**Maintainer note:** Many files in `planned/` are stale — see §6 below. Trust this index, not the folder count.

---

## Open Sprints — by priority

### 🔥 P0 — Dispatch this week

| ID | Title | Owner | Estimate | Plan / Pointer | Why P0 |
|---|---|---|---|---|---|
| **EVE-1** | SystemPulse `/api/tasks` Poll Elimination | Forge (P) / Pixel (S) | 2-4 h | [planned/2026-04-24_evening-atlas-high-leverage-sprints.md §3 EVE-1](planned/2026-04-24_evening-atlas-high-leverage-sprints.md) | `/api/tasks` 1.85 MB × 15 s × 194 k requests. Highest live-perf lever. |
| **S-FOLLOWUP-1 AC-5** | GET /followup-stats Build + Deploy | Forge | 1 h + operator | [03-Agents/sprints/s-followup-1-final-closure-2026-04-29.md](../03-Agents/sprints/s-followup-1-final-closure-2026-04-29.md) | Route exists in source, prod returns 404. Needs `mc-restart-safe`. |
| **OPS-OAUTH-ANTHROPIC** | Anthropic OAuth re-auth | Operator | 5 min | [03-Agents/operator-actions-2026-04-29.md](../03-Agents/operator-actions-2026-04-29.md) | Token expired 2026-04-08 (19.5 d ago). Blocks Anthropic calls. Tracked also as Sprint-1 T6 (id f5f5a778). |
| **S1-T1..T6** | OpenClaw 4.27 Stab Sprint (6 drafts: RCA, Logrotate, Stale-Lock, utcnow, bundle-lsp, OAuth) | sre-expert / main(T6) | 8-12h | [reports/three-sprint-plan](reports/2026-04-30-openclaw-2026-4-27-three-sprint-plan.md) | T1+T6 sind P0; alle als operator-locked drafts angelegt 2026-04-30. |

### ⚠️ P1 — Next 1–2 weeks

| ID | Title | Owner | Estimate | Plan / Pointer | Notes |
|---|---|---|---|---|---|
| **EVE-2** | Metrics endpoint for archive/success/cycle | Forge | 4-6 h | [planned/2026-04-24_evening-atlas-high-leverage-sprints.md §3 EVE-2](planned/2026-04-24_evening-atlas-high-leverage-sprints.md) | Start only after EVE-1 green. Draft task `646c087e-…`. |
| **S-MC-T02** | MC Foundations Loading / Empty State | Pixel/Forge | ~6 h | [planned/2026-04-27_s-mc-t02-foundations-loading-empty.md](planned/2026-04-27_s-mc-t02-foundations-loading-empty.md) | T-Series follow-up to closed s-mc-t01. |
| **S-MC-T03** | Alert-Quality + Suppress-Rules | Forge | ~6 h | [planned/2026-04-27_s-mc-t03-alert-quality-suppress.md](planned/2026-04-27_s-mc-t03-alert-quality-suppress.md) | T-Series. |
| **S-MC-T04** | Konsistenz-Polish | Pixel | ~6 h | [planned/2026-04-27_s-mc-t04-konsistenz-polish.md](planned/2026-04-27_s-mc-t04-konsistenz-polish.md) | T-Series, can run after T02. |
| **S-FOLLOWUP-1 AC-1** | Receipt-v1.1 Adoption 35% → 80% | Atlas + worker prompts | 2-3 h | [03-Agents/sprints/s-followup-1-ea857017-ac1-v1.1-adoption-gap-2026-04-29.md](../03-Agents/sprints/s-followup-1-ea857017-ac1-v1.1-adoption-gap-2026-04-29.md) | Real adoption gap. May need target re-negotiation. |
| **CTX-LT-L1** | Context-Mgmt Long-Term Layer 1 (Tool-Schema-Deferral) | Forge | 6-8 h | [03-Agents/context-management-longterm-fix-2026-04-27.md](../03-Agents/context-management-longterm-fix-2026-04-27.md) | -90% toolsSchema-tokens. Highest token-saving lever. Review-pending → unblock. |

### 🟢 P2 — Later

| ID | Title | Owner | Estimate | Plan / Pointer | Notes |
|---|---|---|---|---|---|
| **EVE-3** | `/api/costs` + `/api/ops/runtime-soak-proof` perf cut | Spark RCA → Forge | 4-8 h | [planned/2026-04-24_evening-atlas-high-leverage-sprints.md §3 EVE-3](planned/2026-04-24_evening-atlas-high-leverage-sprints.md) | 1516 ms / 2093 ms avg. RCA first. |
| **CTX-LT-L4** | Worker Memory-Tool MVP | Forge | 8-12 h | [03-Agents/james-worker-memory-tool-mvp-2026-04-27.md](../03-Agents/james-worker-memory-tool-mvp-2026-04-27.md) | Spec liegt vor (James). |
| **OPS-OPENROUTER** | OpenRouter Account Top-Up | Operator | 5 min | [03-Agents/operator-actions-2026-04-29.md](../03-Agents/operator-actions-2026-04-29.md) | Backstop `billing-alert-watch.sh` live. |
| **OPS-NETWORK-BIND** | Loopback-Bind Gateway/Jaeger/OTLP | Operator + Forge | 1-2 h | [03-Agents/operator-actions-2026-04-29.md](../03-Agents/operator-actions-2026-04-29.md) | Needs gateway-restart window. |
| **R49-DRIFT-RCA** | task_not_found warnings for `9f07d91b…` `abc44fbd…` | Atlas / sre-expert | 1-2 h | (no plan-doc yet) | Recurring R49 violations 2026-04-29 13:21+ — possible hallucination drift. |
| **VAULT-CLEANUP-PHASE-B** | Move 12 superseded plans + finalize Sprint-K close | Operator + script | 1-2 h | This file §6 | Hygiene; unblocks future Atlas-dispatches. |

### ⏸️ Deferred / Contingency — only if regression

| ID | Title | Trigger to start |
|---|---|---|
| **EVE-4** | Auto-Pickup API-unreachable hardening | New worker-proof / pickup degradation |
| **s-ctx-p0** (`planned/s-ctx-p0-2026-04-22.md`) | Context proof tightening | Live context-overflow incident |
| **s-infra** (`planned/s-infra-2026-04-22.md`) | Generic infra | Recut against current state first |
| **s-integ-w1** (`planned/s-integ-w1-2026-04-22.md`) | Integration Week-1 | Operator/Desktop integration decision |

---

## Partially closed — needs verification

| ID | What's done | What's left | Pointer |
|---|---|---|---|
| **S-FOLLOWUP-1** Closure | S1–S4 infra implemented; AC-9 PASS, AC-4 PASS | 3 FAIL (AC-1, AC-6, AC-7) + 4 PARTIAL — see P0/P1 above | [03-Agents/sprints/s-followup-1-final-closure-2026-04-29.md](../03-Agents/sprints/s-followup-1-final-closure-2026-04-29.md) |
| **Sprint-K Infra-Hardening** | H9, H11, H12, H13 reports in `/reports/` | H10 status unclear; Plan-Doc not moved out of `/planned/` | [reports/sprint-k-h9-…](reports/sprint-k-h9-contrast-audit-report-2026-04-20.md) [H11](reports/sprint-k-h11-session-lock-governance-report-2026-04-20.md) [H12](reports/sprint-k-h12-board-state-machine-fix-report-2026-04-20.md) [H13](reports/sprint-k-h13-defense-layers-report-2026-04-20.md) |
| **Sprint-L Memory-KB** | L1-L6-Lite MVPs all live | L1 Deep LLM-Synthesis (gpt-5.4-mini migration) in nightly phase | [planned/sprint-l-memory-kb-compilation-plan-2026-04-19.md](planned/sprint-l-memory-kb-compilation-plan-2026-04-19.md) — likely to be marked superseded |
| **Sprint-M v1.2.1 Audit-Integrity** | M1-M7, M5a, Wave-2 done (per MCP sprint_status) | M0.B Lens-Plan-Review failed ×2 — needs RCA or accepted-failure note | [reports/sprint-m-session-closeout-and-forge-verification-2026-04-21.md](reports/sprint-m-session-closeout-and-forge-verification-2026-04-21.md) |

---

## Hermes Sprint Lane — active peer integration

Hermes is active since 2026-05-02 as an operator-facing peer agent for OpenClaw/Homeserver support. Phase 1 keeps Hermes mostly read-only and approval-gated; Phase 2/3 can expand into task support, lesson writing, and memory contribution after explicit operator gates.

| ID | Status | Owner | Pointer | Outcome / Next Gate |
|---|---|---|---|---|
| **H-2** | done | Codex/Hermes | [../03-Agents/Hermes/sprint-h2-operator-companion-2026-05-02.md](../03-Agents/Hermes/sprint-h2-operator-companion-2026-05-02.md) + [receipt](../03-Agents/Hermes/sprint-h2-receipt-2026-05-02.md) | Operator companion, `mc-readonly`, QMD stdio path, first Discord E2E. |
| **H-3** | done | Codex/Hermes | [../03-Agents/Hermes/sprint-h3-discord-live-openclaw-readonly-2026-05-02.md](../03-Agents/Hermes/sprint-h3-discord-live-openclaw-readonly-2026-05-02.md) + [receipt](../03-Agents/Hermes/sprint-h3-receipt-2026-05-02.md) | `openclaw-readonly` MCP, model status, break-glass runbooks, Discord live checks. |
| **H-4** | done | Codex/Hermes | [../03-Agents/Hermes/plans/sprint-h4-hermes-operator-optimization-2026-05-02.md](../03-Agents/Hermes/plans/sprint-h4-hermes-operator-optimization-2026-05-02.md) + [receipt](../03-Agents/Hermes/sprint-h4-receipt-2026-05-02.md) | PII redaction, stage-1 systemd hardening, slash-sync throttle, tool-surface tightening. |
| **H-5** | done | Codex/Hermes | [../03-Agents/Hermes/sprint-h4-receipt-2026-05-02.md](../03-Agents/Hermes/sprint-h4-receipt-2026-05-02.md) | Operating check and MCP E2E after H-4; no active 429 loop observed. |
| **H-6** | done | Codex | [../03-Agents/Hermes/sprint-h6-receipt-2026-05-02.md](../03-Agents/Hermes/sprint-h6-receipt-2026-05-02.md) | Vault documentation optimized for active peer trajectory. |
| **H-7** | partial-pass | Hermes/Codex | [../03-Agents/Hermes/plans/sprint-h7-phase2-lesson-loop-2026-05-02.md](../03-Agents/Hermes/plans/sprint-h7-phase2-lesson-loop-2026-05-02.md) + [receipt](../03-Agents/Hermes/sprint-h7-receipt-2026-05-02.md) | Lessons loop alpha: schema, pending validation, static eval gate, manual extractor first; cron not active. |
| **H-8** | planned | Hermes/OpenClaw | `TBD` | Controlled task participation pilot after explicit operator approval and receipt gates. |

---

## Recently closed (last 30 days, in `/closed/` or with closure-doc)

| Date | Sprint | Pointer |
|---|---|---|
| 2026-05-01 | S1 Follow-up Pipeline | [closed/2026-05-01_s1-followup-pipeline.md](closed/2026-05-01_s1-followup-pipeline.md) |
| 2026-05-01 | S2 Session / Context Stability | [closed/2026-05-01_s2-session-context-stability.md](closed/2026-05-01_s2-session-context-stability.md) |
| 2026-05-01 | S3 Operator Awareness Loop | [closed/2026-05-01_s3-operator-awareness-loop.md](closed/2026-05-01_s3-operator-awareness-loop.md) |
| 2026-04-30 | OpenClaw 2026.4.27 Update + Audit | [reports/2026-04-30-openclaw-2026-4-27-update-report.md](reports/2026-04-30-openclaw-2026-4-27-update-report.md) + [post-update-audit](reports/2026-04-30-openclaw-2026-4-27-post-update-audit.md) + [three-sprint-plan](reports/2026-04-30-openclaw-2026-4-27-three-sprint-plan.md) (Server: ~/.openclaw/workspace/memory/) |
| 2026-04-29 | Stabilization 2026-04-29 (Crontab-restore + R51 Schema-Gate) | [../03-Agents/stabilization-2026-04-29-full.md](../03-Agents/stabilization-2026-04-29-full.md) |
| 2026-04-27 | MCP-Hardening Sprint (P0.2 + Reaper + alert-dispatcher + 2026.4.24 upgrade) | [2026-04-27-mcp-hardening-sprint.md](2026-04-27-mcp-hardening-sprint.md) |
| 2026-04-27 | S-MC-T01 Critical-Bug-Triage | [closed/s-mc-t01-2026-04-27.md](closed/s-mc-t01-2026-04-27.md) (+ `.DONE` marker in planned/) |
| 2026-04-22 | Sprint-N Lifecycle Stability | [reports/sprint-n-sprint-o-closure-2026-04-20.md](reports/sprint-n-sprint-o-closure-2026-04-20.md) + [reports/sprint-n-e2e-stabilization-2026-04-22.md](reports/sprint-n-e2e-stabilization-2026-04-22.md) |
| 2026-04-22 | Sprint-O lastReportedStatus + QMD-Minimization | [reports/sprint-o-qmd-minimization-2026-04-22.md](reports/sprint-o-qmd-minimization-2026-04-22.md) |
| 2026-04-22 | Sprint-M Audit-Integrity Final-Close | [closed/sprint-m-final-close-2026-04-22.md](closed/sprint-m-final-close-2026-04-22.md) |
| 2026-04-22 | S-Health Final-Close + Board-Cleanup | [closed/s-health-final-close-2026-04-22.md](closed/s-health-final-close-2026-04-22.md) |
| 2026-04-22 | S-FND / S-GOV / S-UX / S-RPT / S-RELIAB-P0 | `closed/s-fnd-2026-04-22.md` + 4 weitere |
| 2026-04-20 | Sprint-K H9/H11/H12/H13 (sub-tickets) | reports/ |
| 2026-04-19 | Sprint-1, 2/3, ABC, D, E, F/G/H, I, J5 | reports/ |

---

## Cleanup-backlog — Vault hygiene

### Stale plans to move from `/planned/` to `/superseded/`

Authority: `planned/2026-04-24_evening-atlas-high-leverage-sprints.md` §2.1 "Vault Plans To Treat As Superseded/Stale" + post-2026-04-29 audit.

| Current path | Reason | Action |
|---|---|---|
| `planned/sprint-h-board-analytics-plan-2026-04-19.md` | `/api/analytics` exists, scope changed | mv → `superseded/`, add `superseded_by: 2026-04-24_evening-atlas-high-leverage-sprints.md` |
| `planned/sprint-i-mobile-polish-plan-2026-04-19.md` | "too broad until payload/perf path is cleaner" | mv → `superseded/` |
| `planned/sprint-j-cascade-postmortem-plan-2026-04-19.md` | governance lessons absorbed into R47/R50 | mv → `superseded/` |
| `planned/sprint-k-infra-hardening-plan-2026-04-19.md` | partially superseded; sub-tickets H9/H11/H12/H13 closed via reports | mv → `superseded/` + write `closed/sprint-k-final-close-2026-04-29.md` linking the four reports |
| `planned/sprint-l-memory-kb-compilation-plan-2026-04-19.md` | MVPs live, Deep in nightly — current state observable | mv → `superseded/` (Deep tracked separately) |
| `planned/sprint-m-audit-integrity-scheduler-consolidation-plan-2026-04-20-v1.2.1.md` | "materially superseded by recent cron/heartbeat reports" | mv → `superseded/` (closed/sprint-m-final-close already exists) |
| `planned/sprint-reporting-next-action-hardening-plan-2026-04-21.md` | "likely superseded by closed S-RPT" | verify → mv → `superseded/` |
| `planned/2026-04-24_mc-audit-p4-followup-plan.md` | P4.1-P4.3 done | mv → `superseded/` |
| `planned/2026-04-24_mc-orchestrated-audit-gate.md` | done via MC-Task `30c36874-…`, report exists | mv → `closed/` (it's done, not superseded) |
| `planned/s-mc-alerts-dashboard-audit-2026-04-23.md` | superseded by later MC audit + P4 work | mv → `superseded/` |
| `planned/s-ctx-p0-2026-04-22.md` | superseded by `03-Agents/context-management-longterm-fix-2026-04-27.md` | mv → `superseded/` with explicit pointer |
| `planned/s-infra-2026-04-22.md` | "needs recut against current worker-proof green state" | mv → `superseded/` |

After these moves, `/planned/` should contain only: EVE-1/2/3/4 (live in `2026-04-24_evening-atlas-high-leverage-sprints.md`), the three `2026-04-27_s-mc-t02/t03/t04` plans, and `2026-04-27_mc-ui-audit-claude-design-prep.md`.

### Failed-marker cleanup in MCP `sprint_status`

These parent-tasks return `failed=1` despite all sub-workstreams `done=1`. Closure-task to do:

- **Sprint-N** — sub-WS A/B/C/D/E + 2 E2E tests all done; parent `failed`. Set parent → done with pointer to closure-report.
- **Sprint-O** — Workstream 1+2 done; parent `failed`. Same fix.
- **[Sprint-M v1.2.1 M0.B] Lens Plan-Review** — failed ×2. Either accept-with-reason or attach RCA.
- **"[Atlas][Stufe7] Reportingformat vereinheitlichen + Sprint-8 Prompt vorbereiten"** — failed, no follow-up doc. Investigate or close.

### Missing or wrong references

- `MEMORY.md:19` (lokale Claude-memory) referenziert `/home/piet/vault/03-Agents/_VAULT-INDEX.md` — diese Datei wurde **heute** angelegt (siehe `../03-Agents/_VAULT-INDEX.md`). Pointer ist jetzt valide.
- Pre-2026-04-19 sprint-pfade in lokaler Memory zeigen auf `/03-Agents/` statt `/04-Sprints/planned/` (Folder-Re-Org war später). Memory-Update separat.

---

## Maintenance

This index is currently **manually maintained**. To keep it honest:

- **Whenever you close a sprint:** move file to `closed/`, update §"Recently closed" table, remove from §"Open Sprints by priority".
- **Whenever you open a sprint:** add row in P0/P1/P2 table with plan-pointer + estimate + owner.
- **Whenever you supersede:** move file to `superseded/`, add `superseded_by:` frontmatter, log in §"Cleanup-backlog".
- **Quarterly:** verify §"Recently closed" against `closed/` directory listing — drop entries older than 90 days.

**Future automation candidate** (P2 backlog): `cron-sprint-index-generator.py` reads frontmatter from all sprint files and regenerates this file. Pattern parallels `memory-dashboard-generator` (cron `30 4 * * *`).

### 🆕 2026-05-05 — S-Context (Session/Context next level)

| ID | Title | Owner | Estimate | Tasks | Why |
|---|---|---|---|---|---|
| **S-Context** | Session/Context Management auf nächste Stufe | Atlas | TBD | T1-T4 dispatched | QMD-Sync tot, Bootstrap-Budget überschritten, 186 Archive |

**Task IDs:**
- T1 (Forge): `a633ff1e-c2b6-4029-9e37-3e88d32a2770` — QMD OnSessionStart Sync
- T2 (Atlas): `b0da1870-18f5-4b12-844a-55c99bcb1f8d` — Bootstrap 16KB Budget
- T3 (Forge): `4ed8145f-1a3b-47f9-abde-21df7e3dfa07` — L2 Auto-Sweep
- T4 (Forge): `91756557-d3c2-4384-8a0b-cc15f965c9f0` — maxActiveTranscriptBytes 1MB

**Plan:** `04-Sprints/planned/2026-05-05_s-context-next-level.md`
