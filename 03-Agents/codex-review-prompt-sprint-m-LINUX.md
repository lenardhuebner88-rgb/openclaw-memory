# Codex-Review-Prompt (Linux/Homeserver-Variante)

> Für Codex-Terminal direkt auf dem Homeserver. CWD muss `/home/piet/vault/03-Agents/` sein (dort liegen die 3 MD-Files).

---

## Start-Sequenz

```sh
ssh homeserver
cd /home/piet/vault/03-Agents
ls -la openclaw-cron-heartbeat-analysis-2026-04-20.md sprint-m-audit-integrity-scheduler-consolidation-plan-2026-04-20.md
codex
```

Nach dem Start → folgenden Prompt paste:

---

## Prompt (copy-paste ab hier)

```
ROLE: You are a senior SRE/Infra reviewer specializing in multi-agent orchestration
platforms. You have no prior context about this project — everything you need is in
the two docs referenced below. Do NOT trust the plan's claims at face value; verify
them against the live system you already have shell access to.

GOAL: Produce an independent, adversarial review of Sprint-M (an infrastructure
consolidation sprint for an OpenClaw-based Mission-Control deployment). Output an
explicit APPROVE / APPROVE-WITH-MODS / REJECT verdict with a prioritized issue-list
and concrete rewrite suggestions where needed.

PRIMARY INPUTS (read these fully before anything else — same directory as CWD):
  1. Source analysis v2:
     ./openclaw-cron-heartbeat-analysis-2026-04-20.md
  2. Sprint plan under review:
     ./sprint-m-audit-integrity-scheduler-consolidation-plan-2026-04-20.md

LIVE SYSTEM ACCESS (you are already on the target homeserver — run commands directly):
  Key paths:
    /home/piet/.openclaw/scripts/                (~53 active scripts)
    /home/piet/.openclaw/workspace/scripts/      (~42 active scripts)
    /home/piet/.openclaw/workspace/HEARTBEAT.md  (state-machine + cron-inventory)
    /home/piet/.openclaw/workspace/AGENTS.md     (agent roles + rules preamble)
    /home/piet/.openclaw/cron/jobs.json          (openclaw-cron plugin, 16 jobs)
    /home/piet/.openclaw/openclaw.json           (main config — do NOT edit, schema-strict)
    ~/.config/systemd/user/                       (systemd user units)
    ~/.openclaw/workspace/logs/                   (43 log files)
    /tmp/*.log                                    (69 cron quick-logs)

  Useful commands (run freely):
    crontab -l | grep -v '^#' | grep -v '^$'
    systemctl --user list-timers --no-pager
    jq '.jobs[]' /home/piet/.openclaw/cron/jobs.json
    curl -s http://localhost:3000/api/health
    tail -50 ~/.openclaw/workspace/logs/<any>.log

  Semantic search (if you need to find things in the codebase/docs):
    qmd search "<query>"              # BM25 across vault+workspace+mc-src
    qmd query "<concept>"             # hybrid + rerank
    qmd get <path>                    # read a specific file

REVIEW DIMENSIONS (all mandatory):

  D1. CLAIM-VERIFICATION
      The v2 analysis §8 lists 7 v1-errors it corrected. Spot-check ≥3 of
      those corrections against live state. Flag any correction that is
      itself still wrong.
      Example: v2 claims "44 crontab entries" — run `crontab -l | grep -v '^#' | grep -v '^$' | wc -l`.
      v2 claims ".openclaw is NOT a git repo" — run `cd ~/.openclaw && git status`.

  D2. SCOPE COMPLETENESS
      Does Sprint-M cover Phase 0 + Phase 1 from the v2 roadmap completely?
      Is anything from the v2 gap-list (G0-G13) silently omitted?
      Is anything added that wasn't in the source analysis (scope creep)?

  D3. DEPENDENCY GRAPH
      Plan claims Wave 1 = M1+M3 parallel, Wave 2 = M2+M4+M5, etc. Walk
      each edge: hidden ordering constraint? Can M2 truly run without M5
      being live? Can M6 proceed before M7 under concurrency constraints?

  D4. DoD QUALITY
      For each M1-M8: are DoD-criteria testable + falsifiable, or vague
      ("works correctly")? Does each task have a verify-command Forge
      can execute and that produces binary pass/fail?

  D5. ROLLBACK INTEGRITY
      Plan claims per-task isolated rollback. Stress-test: M5 succeeds,
      M7 fails mid-migration at 2am. Can operator restore without manual
      surgery? Are .bak-* names unique enough to avoid collision?

  D6. RULE-COMPLIANCE (R1-R50)
      Plan invokes R1/R4/R7/R8/R15/R33/R42/R44/R45/R46/R47/R49.
      Read /home/piet/.openclaw/workspace/memory/rules.jsonl (or
      feedback_system_rules.md in memory) and check:
      Does any step violate a rule it doesn't invoke?
      Of particular concern: R27 (Legacy-Task after Root-Cause-Fix —
      does M7 need legacy-cleanup after systemd-migration?) and R34
      (Bootstrap-Limit — do Forge-Tasks here require oversized
      MEMORY.md bootstrap?).

  D7. COST / OVER-ENGINEERING
      16-22h claimed. Your independent per-sub estimate? Identify 1-3
      tasks that could be ≥30% smaller (simpler approach, reuse of
      existing scripts, merge two subs into one). Flag resume-padding.

  D8. INDUSTRY-BEST-PRACTICE DELTA
      Compare against: Temporal activity-heartbeats, K8s operator
      reconcile loops, systemd.timer vs cron tradeoffs, OpenTelemetry
      instrumentation patterns. Aligned / ahead / behind? Name one
      concrete pattern that would strengthen Sprint-M if added.

  D9. RISK BLINDSPOTS
      Plan lists 5 risks (R-M-1..R-M-5). What's missing? E.g. crontab-
      write races with the running cron-daemon? openclaw-config-guard-
      cron blocking reconciler writes? systemd-user-bus timing?

  D10. REVIEW-GATE DESIGN (M0)
       Atlas + Lens receipt-format unambiguous? Can operator combine
       two verdicts without loss of information? Propose a concrete
       decision-matrix (e.g., "both APPROVE → go; any REJECT → halt;
       Atlas APPROVE_WITH_MODS + Lens SIMPLIFY → merge mods then
       re-review").

VERIFICATION PROTOCOL:
  - Factual claim about live system → run the command, quote output.
  - Respect R1 (Verify-After-Write): every assertion has cmd-output or
    file:line reference.
  - Use `qmd` for concept-search before brute-force file-reads to save
    context window.

OUTPUT FORMAT (strict — goes into the operator's M0 review-gate):

  # Codex Independent Review — Sprint-M (2026-04-20)

  ## Verdict
  APPROVE | APPROVE-WITH-MODS | REJECT

  ## Summary (≤ 150 words)

  ## Findings by Dimension
  ### D1 Claim-Verification
  ### D2 Scope-Completeness
  ### D3 Dependency-Graph
  ### D4 DoD-Quality
  ### D5 Rollback-Integrity
  ### D6 Rule-Compliance
  ### D7 Cost / Over-Engineering
  ### D8 Industry-Delta
  ### D9 Risk-Blindspots
  ### D10 Review-Gate-Design

  ## Required Modifications (if APPROVE-WITH-MODS)
  1. [task-ID] — [change] — [why]

  ## Optional Improvements

  ## Revised Effort Estimate
  Plan claims 16-22h. My estimate: X-Yh (per-sub breakdown).

  ## Top-3 Risks I'd Add

  ## Questions for Operator

SAVE OUTPUT:
  After completing, save the review to:
    /home/piet/vault/03-Agents/codex-review-sprint-m-<YYYY-MM-DD-HHMM>.md
  So Atlas and the operator can read it in the M0-Review-Gate step.

CONSTRAINTS:
  - Do NOT rewrite architecture — harden, not redesign.
  - Do NOT add new languages / schedulers beyond systemd/crontab/openclaw-cron.
  - Do NOT sugarcoat.
  - Do NOT exceed 2500 words.

TIME-BOX: 20-30 min real tool-use.
  - 5 min: read both docs
  - 10 min: live-verification commands
  - 10 min: draft output
  - 5 min: self-check + save

START:
  1. Read ./openclaw-cron-heartbeat-analysis-2026-04-20.md
  2. Read ./sprint-m-audit-integrity-scheduler-consolidation-plan-2026-04-20.md
  3. Sanity-check: `date -u; crontab -l | grep -v '^#' | grep -v '^$' | wc -l; systemctl --user list-timers --no-pager | tail -3; curl -sS http://localhost:3000/api/health | head -c 200`
  4. Proceed through D1-D10.
```

---

## Nach der Review

Die Datei liegt dann unter `/home/piet/vault/03-Agents/codex-review-sprint-m-<timestamp>.md`.

Abrufen zum Lesen:

```sh
ssh homeserver "ls -lt /home/piet/vault/03-Agents/codex-review-sprint-m-*.md | head -1"
ssh homeserver "cat /home/piet/vault/03-Agents/codex-review-sprint-m-<timestamp>.md"
```

Der vault-sync-Timer (`*/30min`) synct außerdem automatisch — die Review taucht zeitnah auch im lokalen Vault-Mirror auf.
