---
title: Sprint-M — Audit-Integrity + Scheduler-Consolidation
sprint-id: M
sprint-scope: Phase 0 + Phase 1 aus openclaw-cron-heartbeat-analysis-2026-04-20.md (v2)
author: Claude (Opus 4.7, 1M context)
date: 2026-04-20
status: DRAFT — **BLOCKED by M0 Review-Gate** — requires Atlas + Lens sign-off before dispatch
operatorLock: true
scope-lock: Plan-Doc-Frontmatter (R47) — neue Task-IDs für identischen Scope sind NICHT autorisiert
total-effort-estimate: 16-22 h (Forge + Lens + Atlas-Orchestration)
dependencies-upstream:
  - Plan-Review-Gate M0 erfolgreich
  - openclaw.json-Schema stable (keine pending H2/H5 Rollbacks)
  - MC + Gateway active (curl /api/health = 200)
unblocks-downstream:
  - Phase 2 (GitOps)
  - Phase 3 (Observability/OTEL)
  - Phase 4 (Circuit-Breaker + Policy-Engine)
rules-applied: R1, R4, R7, R8, R15, R33, R42, R44, R45, R46, R47, R49
related:
  - openclaw-cron-heartbeat-analysis-2026-04-20.md (v2, Source-of-Truth)
  - memory/sprint_k_infra_hardening_plan.md (H10-Scope wird teilweise ersetzt durch M3-M5)
  - workspace/HEARTBEAT.md (Cron-Inventory §1.4)
---

# Sprint-M — Audit-Integrity + Scheduler-Consolidation

**Purpose:** Zuerst den kaputten Health-Checker reparieren (damit alle weiteren Defense-Layer auf vertrauenswürdige Signale aufbauen), dann die 3-Scheduler-Fragmentierung durch eine Registry-basierte Single-Source-of-Truth ersetzen.

**Why NOW:** cron-health-audit.sh erzeugt systematische False-Positives (siehe Analyse §1.6) — jede weitere Optimierung des Stacks basiert auf unzuverlässigen Signalen. Audit-Fix ist damit **Voraussetzung** für Phase 2+, nicht parallel.

---

## 🛑 M0 · Review-Gate (BLOCKING — vor jedem anderen Dispatch)

Zweck: Zwei unabhängige Reviewer-Perspektiven **vor** Ressourcen-Einsatz. Atlas prüft Scope/Risiko/Abhängigkeiten, Lens prüft Kosten/Over-Engineering/Waste. Operator konsolidiert und gibt frei.

### M0.A · Atlas-Review (main-Orchestrator)

**Dispatch-Method:** Manual — **NICHT** via auto-pickup (R37: Atlas-Orchestrator-Tasks nicht via Auto-Pickup). Operator triggert Atlas-Session mit Trigger-Phrase:

> "Atlas — Sprint-M Plan-Review. Lies `sprint-m-audit-integrity-scheduler-consolidation-plan-2026-04-20.md` und die Source-Analyse `openclaw-cron-heartbeat-analysis-2026-04-20.md` v2. Poste Review-Receipt als Task."

**Atlas-Review-Scope (mandatory):**

1. **Scope-Check:** Sind M1-M8 vollständig? Fehlt etwas aus v2-Analyse Phase 0+1? Ist etwas redundant zu Sprint-K H10 (L2/L3/L4/L5)?
2. **Dependency-Check:** Läuft M3 (Registry) **vor** M4 (Reconciler)? Kann M5 (Memory-Orchestrator) parallel zu M6 (systemd-Migration) laufen? Gibt es hidden coupling?
3. **Risk-Check:** Welche Tasks haben MC-Restart-Impact (R46 Deploy-Serialization)? Welche können `openclaw.json` triggern (R4)? Welche berühren aktive Defense-Crons?
4. **Rule-Compliance:** Verletzt der Plan aktive Rules R1-R50? (Besonders R4 Config-NIE, R15 Deploy-Atomar, R42 Verify-Contract, R46 Parallel-Deploy-Serialization.)
5. **Timing:** Sind 16-22 h realistisch? Wo könnten Stunden explodieren?

**Receipt-Format (Atlas postet auf Board als neue Task `m0-atlas-review`):**

```
VERDICT: APPROVE | APPROVE_WITH_MODS | REJECT
Scope-OK: Y/N (notes)
Deps-OK: Y/N (notes)
Risks: <liste>
Rule-Violations: <liste oder "none">
Timing-Assessment: <notes>
Required-Mods-for-Approval: <liste; empty if APPROVE>
```

**DoD M0.A:** Atlas-Receipt auf Board mit explizitem VERDICT-Feld.

### M0.B · Lens-Review (efficiency-auditor)

**Dispatch-Method:** Standard Board-Task (Lens akzeptiert via auto-pickup). Label: `[Sprint-M-Review]`. `operatorLock: false` (Lens darf eigenständig akzeptieren).

**Lens-Review-Scope (mandatory):**

1. **Cost-Check:** Total Token-Budget für Sprint-M realistisch? Forge-Subagent-Cost-Estimate pro Task?
2. **Waste-Check:** Sind Tasks überdimensioniert? Z.B. ist ein vollwertiger `cron-reconciler.py` nötig oder reicht ein einfacher bash-Loop?
3. **Over-Engineering:** Brauchen wir `cron-registry.yaml` als YAML, oder tut es eine `.openclaw/cron/registry.jsonl`? YAML zwingt neue Parser-Dep.
4. **Reuse-Check:** Welche Scripts existieren bereits und könnten wiederverwendet werden? (Z.B. `rules-md-to-jsonl.py` als Parser-Template?)
5. **Simplification-Potential:** Gibt es Tasks, die als 1-zeiliger `sed`/`crontab`-Edit statt als volles Sprint-Sub laufen könnten?

**Receipt-Format (Lens postet als `m0-lens-review`):**

```
VERDICT: APPROVE | SIMPLIFY | REJECT
Token-Budget-Estimate: <hrs * $rate> (breakdown)
Over-Engineered-Tasks: <liste mit Alternative>
Reuse-Opportunities: <liste>
Simplification-Proposals: <liste>
Total-Effort-Revised: <hrs>
```

**DoD M0.B:** Lens-Receipt auf Board mit VERDICT.

### M0.C · Operator-Consolidation (Human-Gate)

Operator liest beide Reviews und entscheidet:

- **Beide APPROVE** → Operator setzt `m0-approved: true` auf Plan-Doc-Frontmatter + triggert M1-Dispatch.
- **Mindestens ein APPROVE_WITH_MODS oder SIMPLIFY** → Operator editiert Plan, bumpt Version, re-review (M0.A + M0.B erneut) ODER accept mods directly und gehe zu Dispatch.
- **Mindestens ein REJECT** → Plan zurück in DRAFT, Scope-Revision nötig.

**DoD M0.C:** `m0-approved: true` im Frontmatter dieses Docs + kurzer Decision-Log in §5.

**Time-Box:** M0 soll nicht länger als 45 min (Atlas ~15 min, Lens ~15 min, Operator ~15 min).

---

## Sprint-M Sub-Tasks (erst ab M0-APPROVED)

### Phase M.1 — Audit-Repair (P0, Scope Analyse §4.2)

#### M1 · `cron-health-audit.sh` Regex + False-Positive-Fix

**Agent:** Forge (sre-expert)  
**Effort:** 2-3 h  
**Depends on:** —

**Problem:** Case-insensitive `grep 'error|fail'` matcht Normal-Status-Felder wie `auto-failed=0`, `stalled-hard-failed=0` in worker-monitor.log → 1145 false-positives pro 5000 Zeilen.

**DoD:**
1. Script nutzt striktes Regex: `grep -E '^\S+ (ERROR|FATAL|CRITICAL|ALERT)' ` oder JSON-Log-Parser mit `jq 'select(.severity>="error")'`.
2. Gegentest gegen worker-monitor.log: legitimate-errors vs false-positives = ≥95% Precision.
3. Unit-Test-File `tests/cron-health-audit.test.sh` mit 2 synthetischen Logs (clean + dirty), Erwartung per Fixture dokumentiert.
4. Audit-Run in CI (script-integrity-check invokes it) dann grün.
5. Backup `cron-health-audit.sh.bak-m1-2026-04-20` vor Edit (R8).

**Dispatch-Prompt:**

```
Task [Sprint-M M1] `cron-health-audit.sh` Regex-Fix.
Read: scripts/cron-health-audit.sh + workspace/scripts/worker-monitor.log.
Problem: grep-Pattern 'error|fail' case-insensitive matcht 'auto-failed=0' etc.
Fix: strict severity-regex oder JSON-mode. Add tests/ dir.
DoD: siehe plan M1. Receipt=accepted within 60s, progress every 5min.
R8: .bak-m1-2026-04-20 backup first. R42 Verify-Contract: after fix,
tail -1000 worker-monitor.log | ./cron-health-audit.sh --test must return
<= 5 errors (not 5192).
```

#### M2 · Audit liest Cron-Registry statt hardcoded Paths

**Agent:** Forge  
**Effort:** 2 h  
**Depends on:** M3 (Registry Schema existiert)

**Problem:** Audit-Script hat Log-Pfade hartkodiert → prüft `auto-pickup-cron.log` (cron-stdout) statt `auto-pickup.log` (Script-eigener Log).

**DoD:**
1. Audit liest `~/.openclaw/cron/registry.jsonl` (aus M3) und löst `logfile` + `schedule` pro Cron dynamisch.
2. Missing-Log-Check unterscheidet: Schedule erwartet Output (z.B. hourly) vs Schedule silent-by-default (z.B. weekly script ohne stdout).
3. Stale-Threshold = `expected_interval * 2` aus Registry, nicht mehr 2× hardcoded.
4. Audit-Run produziert 0 false-positives gegen bekannten Clean-State.

**Dispatch-Prompt:**

```
Task [Sprint-M M2] Audit reads Registry.
Depends on M3. Read: scripts/cron-health-audit.sh + cron/registry.jsonl (from M3).
Refactor: remove hardcoded log-paths, iterate registry entries.
DoD: 0 false-positives in clean state. R42 Verify: run audit, diff with
manual log-ls; match.
```

#### M3 · `cron/registry.jsonl` Schema + Initial-Population

**Agent:** Forge  
**Effort:** 3-4 h  
**Depends on:** —

**Scope:** Single-Source-of-Truth für alle 66 aktiven Schedules (44 crontab + 6 systemd-timer + 16 openclaw-cron).

**DoD:**
1. Schema (JSON-Line per Entry):
   ```json
   {"name":"auto-pickup","scheduler":"crontab","schedule":"* * * * *",
    "command":"flock -n /tmp/... /home/piet/.openclaw/scripts/auto-pickup.py",
    "script_path":"/home/piet/.openclaw/scripts/auto-pickup.py",
    "logfile":"/home/piet/.openclaw/workspace/logs/auto-pickup.log",
    "stdout_log":"/home/piet/.openclaw/workspace/logs/auto-pickup-cron.log",
    "tier":"T1","category":"Auto-Execution",
    "expected_output":"hourly","silent_ok":false,
    "depends_on":[],"alert_on_failure":true,
    "env_required":["AUTO_PICKUP_ENABLED","AUTO_PICKUP_WEBHOOK_URL"],
    "owner":"sre-expert"}
   ```
2. Initial-Population aus Live-State:
   - `crontab -l` → 44 entries
   - `systemctl --user list-timers` → 6 entries
   - `jq '.jobs[]' ~/.openclaw/cron/jobs.json` → 16 entries
3. Validator-Script `cron/registry-validate.py`: checkt Schema, Duplicate-Names, Script-Existence.
4. Datei unter Versionskontrolle (via Phase-2-Git-Init oder zumindest manuell commitiert in Vault).

**Dispatch-Prompt:**

```
Task [Sprint-M M3] cron-registry.jsonl Schema + Population.
Read: v2-analysis §4.3 (Registry design). HEARTBEAT.md §1 Cron-Inventory.
Create /home/piet/.openclaw/cron/registry.jsonl with 66 entries
(44 crontab + 6 systemd + 16 openclaw-cron).
Use jq, crontab -l, systemctl --user list-timers as inputs.
DoD: registry-validate.py exit=0, count=66.
```

#### M4 · ENV-Check-Fix + Schedule */30min + Canary

**Agent:** Forge  
**Effort:** 1.5 h  
**Depends on:** M1, M2

**Scope bundle:** 3 kleine Fixes.

**DoD:**
1. **ENV-Cross-Check:** Audit-Script prüft jede ENV gegen `grep -rln "\$ENVNAME" ~/.openclaw/scripts/ ~/.openclaw/workspace/scripts/`. Wenn Script die ENV nicht referenziert → kein ENV_MISSING-Alert.
2. **Cron-Schedule:** `0 9 * * 1` → `*/30 * * * *` in crontab (via `crontab -l | sed`).
3. **Canary-Cron:** Neue Zeile `0 */6 * * * /home/piet/.openclaw/scripts/alert-dispatcher.sh canary info "canary-ok"`. Discord channel #alerts erhält alle 6h eine Canary-Message. Dedup-Lock nicht nötig (gewollt).

**Dispatch-Prompt:**

```
Task [Sprint-M M4] ENV-Fix + Schedule-Up + Canary.
3 Fixes: (a) cron-health-audit ENV-check cross-references scripts,
(b) audit schedule */30min, (c) canary-alert every 6h.
DoD all 3 deployed, first canary received on #alerts.
R42 verify: after 30min, fresh audit-log exists and shows ok-state.
```

### Phase M.2 — Scheduler-Consolidation (P0)

#### M5 · `cron-reconciler.py` (Registry → Scheduler Writer)

**Agent:** Forge  
**Effort:** 4-6 h  
**Depends on:** M3

**Scope:** Nimmt Registry als Input, appliziert auf tatsächliche Scheduler. Idempotent (dry-run default).

**DoD:**
1. `cron-reconciler.py --dry-run` (default) zeigt Diff: Registry vs Live-State.
2. `cron-reconciler.py --apply` schreibt:
   - crontab-Entries via `crontab -l | grep -v <tag> ; echo new >> ...` mit Managed-Tag-Marker `# MANAGED-BY-RECONCILER`.
   - systemd user-timer Units in `~/.config/systemd/user/<name>.timer` + `.service`.
   - openclaw-cron-Plugin Jobs via `openclaw cron set <name> ...`.
3. Backup vor jedem Apply: `crontab -l > .bak-reconciler-<ts>`.
4. Error-Handling: Wenn Registry-Entry invalid → skip + log, nicht abort.
5. Re-running with no changes: exit 0, „no drift".

**Dispatch-Prompt:**

```
Task [Sprint-M M5] cron-reconciler.py.
Depends on M3. Read: registry.jsonl schema.
Build reconciler that applies registry to crontab + systemd-timers +
openclaw-cron. Dry-run default. Managed-tag-marker in crontab.
DoD: idempotent; second apply = no-op. Backup before apply.
R42 Verify: after apply, crontab -l | diff against registry = empty.
```

#### M6 · Memory-Crons → 1 Orchestrator

**Agent:** Forge  
**Effort:** 2-3 h  
**Depends on:** M3 (registry), can run parallel to M5

**Scope:** Die 11 Memory-Crons (qmd-update, kb-compiler, graph-edge-builder, dreaming, importance-recalc, retrieval-feedback-loop, memory-dashboard-generator, daily-reflection-cron, sqlite-maintenance, memory-layer-sweep, REM-backfill) als **eine** `memory-orchestrator.py` mit expliziter DAG + Lock.

**DoD:**
1. `memory-orchestrator.py <phase>` — Phases: `hourly`, `nightly`, `weekly`, `quarterly`.
2. DAG-Reihenfolge (explizit): `qmd-update → kb-compiler → graph-edge-builder → dashboard-generator`.
3. Lock pro Phase: `/tmp/memory-orchestrator-<phase>.lock`.
4. Registry (M3) wird entsprechend aktualisiert: 11 Einträge werden zu 4 Orchestrator-Einträge.
5. Alte 11 Cron-Entries in crontab auskommentiert (nicht gelöscht — R8-Rollback).
6. Dry-Run first: 1× Manual nightly-Run verifiziert alle 11 Sub-Steps OK.

**Dispatch-Prompt:**

```
Task [Sprint-M M6] memory-orchestrator.py.
Consolidate 11 Memory-Crons into 1 script with phase-argument + DAG.
DoD: nightly-phase dry-run reproduces current output of 11 individual
crons. Crontab shrinks from 11 to 4 memory-lines.
R42 Verify: diff qmd-index-before-after, kb-compiler-output-before-after
= semantic-identical.
```

#### M7 · Top-5 Kernel-Crons → systemd-timer Migration

**Agent:** Forge  
**Effort:** 2-3 h  
**Depends on:** M5 (reconciler needs to handle both scheduler-types)

**Scope:** `auto-pickup`, `mc-watchdog`, `worker-monitor`, `session-freeze-watcher`, `stale-lock-cleaner` — die Tier-1-Kernel-Crons — auf systemd-user-timer migrieren. Grund: systemd `Restart=on-failure`, besseres Logging (`journalctl`), `StartLimitBurst` gegen Runaway.

**DoD:**
1. 5 `.timer` + 5 `.service` Units in `~/.config/systemd/user/`.
2. Jede Service-Unit mit `Restart=on-failure`, `RestartSec=30`, `StartLimitBurst=5`.
3. `systemctl --user enable --now <name>.timer` für alle 5.
4. Crontab-Entries für die 5 auskommentiert (nicht deleted).
5. Registry (M3) aktualisiert: `scheduler` Feld von `crontab` → `systemd-timer`.
6. Rollback-Script `systemd-migration-rollback.sh` bereit: deaktiviert timer, reactiviert crontab-lines.
7. 24h-Soak-Test: nach 24h `journalctl --user -u auto-pickup.service` zeigt ≥ 1400 starts (≈ 1/min).

**Dispatch-Prompt:**

```
Task [Sprint-M M7] Kernel-Crons → systemd-timer migration.
Migrate 5 Tier-1 crons: auto-pickup, mc-watchdog, worker-monitor,
session-freeze-watcher, stale-lock-cleaner.
DoD: all 5 running as systemd-timer, crontab-lines commented out,
rollback-script ready, registry updated.
R42 Verify: after 15min, journalctl --user -u auto-pickup.service shows
≥14 starts (1/min).
```

#### M8 · Cron-Audit-Final-Run + Dashboard-Seed

**Agent:** Forge + Atlas (verify)  
**Effort:** 1 h  
**Depends on:** M1-M7 all done

**Scope:** Abschluss-Run der reparierten Audit-Pipeline. Atlas verifiziert.

**DoD:**
1. `cron-health-audit.sh` Run zeigt: **0 false-positive errors**, **0 missing-logs** (die 4 von v1 sind entweder behoben oder als `silent_ok:true` in Registry markiert), **0 stale-alarms** (Registry-kadenz-basiert).
2. Seed-File `~/.openclaw/workspace/memory/cron-audit-baseline-2026-04-2X.json` als Referenz für Drift-Detection.
3. Atlas postet Sprint-M-Endreport (Board-Task `m-endreport`) mit Before/After-Matrix.
4. Alle 66 Registry-Einträge `lastRun` + `lastStatus` populated.
5. Discord `#execution-reports` erhält Sprint-M-Completion-Message.

**Dispatch-Prompt (an Atlas):**

```
Atlas: Sprint-M finalization. Read M1-M7 results.
Run fresh cron-health-audit.sh. Verify: 0 false-positives, 0 missing,
0 stale. Seed baseline-file. Post endreport.
R49: every claimed commit/ID inline-verify before reporting.
```

---

## Dispatch-Reihenfolge (DAG)

```
M0 (Review-Gate, BLOCKING)
    │
    ├─→ M3 (Registry) ───┬─→ M2 (Audit uses Registry)
    │                     ├─→ M5 (Reconciler)
    │                     └─→ M6 (Memory-Orch) ─┐
    ├─→ M1 (Regex-Fix) ──→ M4 (ENV+Sched+Canary)│
    │                                             │
    │                     M5 ─→ M7 (systemd-mig) ─┤
    │                                             ▼
    └─→ all-done ────────────────────────────── M8 (Audit-Final)
```

**Parallelisierbar (nach M0-Approval):**

- **Wave 1:** M1 + M3 (unabhängig)
- **Wave 2:** M2 + M4 (nach M1+M3) und M5 (nach M3)
- **Wave 3:** M6 + M7 (nach M5)
- **Wave 4:** M8 (nach alle vorherigen)

**R46 Parallel-Deploy-Serialization:** M7 berührt systemd-user — kein MC-Restart. M1-M6 berühren keine MC-Routes. Kein Deploy-Race-Risiko. MC-Restart ausschließlich falls Registry-Changes eine MC-Route brauchen (aktuell nein).

---

## Risiken & Mitigations

| # | Risk | Severity | Mitigation |
|---|---|---|---|
| R-M-1 | cron-reconciler (M5) schreibt fehlerhafte crontab, alle Crons tot | HIGH | Backup vor jedem Apply; dry-run default; 1× manuell verifizierter apply vor auto-apply |
| R-M-2 | systemd-timer migration (M7) bringt Auto-Pickup temporär offline → Board freezet | MED | Migration im 10-min-Fenster; rollback-script ready; manual `auto-pickup.py` während migration |
| R-M-3 | Memory-Orchestrator (M6) ändert qmd-Collections-State → agents verlieren Memory-Context | MED | Dry-run full nightly cycle before switchover; Atlas verifiziert qmd-query-parity |
| R-M-4 | Registry (M3) fehlt einen Cron → Reconciler löscht ihn | LOW | Validator exit=0 required before M5-apply; operator-diff-review |
| R-M-5 | M4 Canary-Alert macht #alerts noisy | LOW | 6h-Frequenz; Discord-thread Silence nach 1 Tag optional |

---

## Success-Kriterien (Sprint-M)

Nach M8 erfüllt:

- [ ] `cron-health-audit.sh` produziert < 5 false-positives/Woche (Baseline heute: ≥5k)
- [ ] Audit-Schedule ist `*/30min` (heute: weekly)
- [ ] `cron/registry.jsonl` existiert mit 66 Entries, Validator exit=0
- [ ] `cron-reconciler.py` idempotent-apply funktioniert
- [ ] 11 Memory-Crons → 4 Orchestrator-Phasen migriert
- [ ] 5 Kernel-Crons auf systemd-timer, 24h soak-test überstanden
- [ ] Canary-Alert-Pipeline live
- [ ] 0 reale Production-Incidents während Sprint-M-Execution
- [ ] Baseline-File für Drift-Detection seeded
- [ ] Sprint-M-Endreport auf #execution-reports

---

## Rollback-Plan (global)

Falls zu irgendeinem Zeitpunkt im Sprint-M eine kritische Regression auftritt:

1. **M1-M4 (Audit-Tool-Fixes):** Restore aus `.bak-m*-2026-04-20` — Audit-Tool zurück auf alten Zustand (buggy but known).
2. **M5 (Reconciler):** `crontab < ~/.openclaw/cron/crontab.bak-reconciler-<ts>` — crontab zurück.
3. **M6 (Memory-Orchestrator):** Crontab-Kommentare entfernen, alte 11 Memory-Cron-Lines reaktivieren; Orchestrator-Script-Lines disabled.
4. **M7 (systemd-Migration):** `systemd-migration-rollback.sh` — disabled timers, re-enabled crontab-lines.
5. **Notfall:** Alles via `openclaw doctor --fix` (letzter Schritt) — greift nur wenn openclaw.json-Schema drift.

Rollback ist pro-Task isoliert — kein Bundle-Rollback nötig da DAG-Ordering Einzelrollbacks zulässt.

---

## 5 · Decision-Log (wird während M0 gefüllt)

| Datum UTC | Reviewer | Verdict | Mods | Operator-Action |
|---|---|---|---|---|
| TBD | Atlas | — | — | — |
| TBD | Lens | — | — | — |
| TBD | Operator | — | — | — |

---

## 6 · Anhang — Trigger-Phrases

Nach Operator-Freigabe M0.C:

- **„Atlas — dispatch Sprint-M Phase M.1"** → M1 + M3 (Wave 1)
- **„Atlas — dispatch Sprint-M Phase M.2"** → M2 + M4 + M5 (Wave 2)
- **„Atlas — dispatch Sprint-M Phase M.3"** → M6 + M7 (Wave 3)
- **„Atlas — finalize Sprint-M"** → M8 + Endreport

Bei Abweichung vom Plan (neue Task-IDs für identischen Scope): **R47-Violation**. Plan-Frontmatter `scope-lock: Plan-Doc-Frontmatter` ist bindend.

---

## 7 · Related Docs

- `openclaw-cron-heartbeat-analysis-2026-04-20.md` (v2) — Source-of-Truth
- `workspace/HEARTBEAT.md` §1 Cron-Inventory — Kategorisierung
- `memory/sprint_k_infra_hardening_plan.md` — H10-Überlapp (H10 L2/L3/L4/L5 wird durch M5/M6/M7/M8 ersetzt; H10 L1 bleibt separat)
- `feedback_system_rules.md` — R1/R4/R7/R8/R15/R33/R42/R44/R45/R46/R47/R49 (invoked)

---

**Plan-Ende. Status bis M0-Approval: DRAFT / BLOCKED. Nach Approval: RUNNING.**
