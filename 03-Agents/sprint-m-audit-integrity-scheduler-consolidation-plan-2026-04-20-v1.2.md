---
title: Sprint-M — Audit-Integrity + Scheduler-Consolidation
sprint-id: M
version: 1.2 (post-Codex-re-review 2026-04-20 23:xx)
sprint-scope: Phase 0 + Phase 1 aus openclaw-cron-heartbeat-analysis-2026-04-20.md (v2)
author: Claude (Opus 4.7, 1M context)
date: 2026-04-20
status: DRAFT v1.2 — Atlas M0.A = APPROVE. Codex v1.1-review = APPROVE-WITH-MODS (3 finds: M6-contradiction, M7-OnFailure-missing-unit, M6-verify-weak). Alle 3 in v1.2 resolved. Lens (M0.B) pending gegen v1.2.
operatorLock: true
scope-lock: Plan-Doc-Frontmatter (R47)
total-effort-estimate: 17-24 h hands-on (Forge) + 24h post-sprint soak-phase for M7 (separated from sprint-close)
supersedes:
  - sprint-k-infra-hardening-plan-2026-04-19.md sections L2/L3/L4/L5 (Operator-Decision: Sprint-M supersedes these)
  - H10 L1 bleibt eigenständig in Sprint-K (nicht Teil Sprint-M)
live-baseline-2026-04-20-23:00-CEST:
  crontab_real_schedules: 46
  crontab_env_declarations: 4
  systemd_user_timers: 6
  openclaw_cron_enabled: 16
  total_schedules: 68
dependencies-upstream:
  - M0 Review-Gate (Atlas DONE, Codex DONE, Lens re-dispatch pending)
  - openclaw.json-Schema stable
  - MC + Gateway active
unblocks-downstream:
  - Phase 2 (GitOps)
  - Phase 3 (Observability/OTEL)
  - Phase 4 (Circuit-Breaker + Policy-Engine)
  - Sprint-N (M5b `--apply` der Registry-Reconciler)
rules-applied: R1, R4, R7, R8, R15, R27, R33, R34, R42, R44, R45, R46, R47, R49
related:
  - openclaw-cron-heartbeat-analysis-2026-04-20.md (v2)
  - codex-review-sprint-m-2026-04-20-2256.md (external Codex-Review)
  - sprint-k-infra-hardening-plan-2026-04-19.md (H10 L1 verbleibt dort; L2-L5 superseded hier)
  - workspace/HEARTBEAT.md §1.4 (Cron-Inventory — Re-Baseline in M0.D)
---

# Sprint-M — Audit-Integrity + Scheduler-Consolidation (v1.2)

## 📋 Changelog v1.1 → v1.2 (aktuell)

### Codex-Re-Review-Findings (3) applied

| Finding | Severity | v1.1 Problem | v1.2 Resolution |
|---|---|---|---|
| F1 | HIGH | M6 widersprüchlich: DoD sagt „read-only, keine crontab-Writes" — aber DoD-Punkt 5 nutzt `sed -i` auf crontab für 11 Memory-Lines. M6 ∥ M7 parallel = Race. | M6 **wirklich** read-only (nur Script-Build). Crontab-Mutation gezogen in **neuen M6b** der **sequenziell nach M7** läuft. |
| F2 | MED | M7 `OnFailure=alert-dispatcher@%i.service` — Unit existiert nicht im System, Plan erstellt sie nicht. | `OnFailure=` **gedroppt**. Alert-on-Failure läuft via Script-internen `alert-dispatcher.sh`-Call (existierendes Projekt-Pattern, siehe `mc-watchdog.sh`). `Persistent=true` bleibt erhalten (essentiell). |
| F3 | MED | M6-Verify `git -C ... diff` beweist crontab-Live-State nicht. | Verify-Protocol auf `crontab -l > before.txt` / `crontab -l > after.txt` + textueller `diff` umgestellt. |

### DAG v1.2 geändert

Wave 3 ist jetzt safe parallel (M6 read-only + M7 systemd-mig). Wave 4 ist NEU (M6b crontab-mutation). Wave 5 ist M8 (final). Siehe §Dispatch-Reihenfolge unten.

### Codex-v1.1-Verified als korrekt (bleibt unverändert)

- Live-Baseline 46/4/6/16 = 68 — bestätigt
- M4 Retarget auf `script-integrity-check.sh` + flock-konformer Canary — bestätigt
- M5-Split (M5a read-only, `openclaw cron edit` existiert für Sprint-N) — bestätigt
- 4 Codex-v1.0-Blocking-Mods bleiben resolved

---

## 📋 Changelog v1.0 → v1.1 (Historie)

### Blocking Codex-Mods applied

| Mod | v1.0 Problem | v1.1 Resolution |
|---|---|---|
| 1 | M0.A Scope-Check referenzierte falsche Task-Numbers (M4=Reconciler, M5=Memory); tatsächlich M5=Reconciler, M6=Memory, M7=systemd | Task-Numbers in M0.A §2 Deps-Check korrigiert + Atlas' Review hat das bereits mit korrektem Mapping beantwortet |
| 2 | M4 zielte auf `cron-health-audit.sh` ENV-Check, aber False-Positives entstehen in `script-integrity-check.sh:119-144` | M4 retargetet auf `script-integrity-check.sh`; `cron-health-audit.sh` nur noch für regex-strictness (M1) |
| 3 | M5 referenzierte nicht-existentes `openclaw cron set` (CLI kennt nur add/edit/enable/disable/rm/run/runs/status) | **M5 split in M5a (read-only diff + validator) in Sprint-M** + **M5b (`--apply` mit `openclaw cron edit/add`) in Sprint-N** — Operator-Decision zu Codex-Frage 1 |
| 4 | Canary-Cron (M4) ohne flock; R33-Verletzung | Canary-Cron bekommt `flock -n /tmp/canary-alert.lock` |

### Additional Codex-Findings applied

- **Live-Count-Re-Baseline:** v2 sagte 66, Codex sagte 67, live-verifiziert sind **68** (46 crontab + 6 systemd + 16 openclaw-cron). Added as **M0.D pre-step** (runs before M3).
- **DAG M6-Contradiction** (header "parallel zu M5" vs DAG "nach M5"): aufgelöst via Atlas-Clarification — M6 liest NUR Registry, macht keine Crontab-Writes, daher M6 ∥ M7 nach M5.
- **Backup-Name-Collisions:** `.bak-m{N}-YYYY-MM-DD` nicht unique bei Retry → upgraded auf `.bak-m{N}-YYYYMMDD-HHMMSS`.
- **M7 Persistent=true + OnFailure=** explicit in DoD (war in H10 erwähnt, in v1.0 gedroppt).
- **24h-Soak** aus Sprint-M-Close rausgezogen → **§Soak-Phase (post-sprint)**.
- **DoD-Falsifiability:** „first canary received" / "all 66 lastRun populated" durch konkrete Checks mit Exit-Code ersetzt.
- **v2-Analyse §47 Fehler:** „openclaw-cron jobs haben lastRun: null" — Codex verifizierte live `lastRunAtMs != null`. Wird in nächster v3 der Analyse korrigiert. Keine Auswirkung auf Sprint-M.

### Atlas-Mod applied

- M6 DoD ergänzt: **„M6 liest nur Registry, keine konkurrierenden Crontab-Writes"** (sichert M6 ∥ M7 Parallelisierbarkeit).

### Operator-Decisions (zu Codex' 3 Fragen)

1. **M5 read-only in Sprint-M, `--apply` in Sprint-N** — minimiert R-M-1 auf ~0, separiert apply-Risk in eigenes review-gate.
2. **Sprint-M supersediert H10 L2-L5**, H10 L1 bleibt in Sprint-K. H10-Plan-Frontmatter wird mit `superseded-by: sprint-m-...-v1.1.md` ergänzt (post-Sprint-M).
3. **Registry-Baseline = 68** (46 real crontab + 6 systemd + 16 openclaw-cron). ENV-declarations (4) werden separat kategorisiert, nicht als Schedule.

### New Risks (Codex D9)

- R-M-6: Crontab-Write-Races M4/M5/M6 → Serialization via sequenced waves.
- R-M-7: M7 Double-Fire-Window (timers enabled while old cron lines still live) → Disable cron BEFORE enabling timer.
- R-M-8: Registry Stale-Seed → M0.D Pre-Baseline-Step.

---

## 🛑 M0 · Review-Gate (BLOCKING)

### M0.A · Atlas-Review — ✅ **APPROVE** (abgeschlossen 2026-04-20 22:xx UTC)

Atlas-Review-Verdict: **APPROVE** mit einer DoD-Clarification für M6 (übernommen unten).

Atlas-Required-Mod (in v1.1 übernommen): M6-DoD ergänzen um *„liest nur Registry, keine konkurrierenden Crontab-Writes"* — sichert M6 ∥ M7 ab.

### M0.B · Lens-Review — ⏳ **re-dispatch nach v1.1 Upload**

Lens-v1.0-Task `f6e9a647-a91d-47c2-b644-b19e69e2fc29` ist `canceled` (Codex hat v1.0 mit blocking-mods zurückgewiesen; Re-Review gegen v1.0 wäre verschwendet). Re-Dispatch gegen v1.1 erfolgt nach Upload nach Vault.

### M0.C · Codex-Review — ✅ **APPROVE-WITH-MODS** (abgeschlossen 2026-04-20 22:56)

Ergebnis: `/home/piet/vault/03-Agents/codex-review-sprint-m-2026-04-20-2256.md`. 4 blocking mods + 3 operator-questions alle resolved in diesem v1.1.

### M0.D · Re-Baseline Live Counts (NEW — Pre-M3 Step)

**Before M3 seeds the registry:** Operator (oder Forge via cron-one-shot) re-baseline live:

```sh
crontab -l | grep -v '^#' | grep -v '^$' | grep -v '^[A-Z_][A-Z_0-9]*=' | wc -l  # expect 46
crontab -l | grep -E '^[A-Z_][A-Z_0-9]*=' | wc -l                                  # expect 4
systemctl --user list-timers --all --no-pager | grep -c '\.timer'                   # expect 6
jq '[.jobs[] | select(.enabled==true)] | length' /home/piet/.openclaw/cron/jobs.json  # expect 16
```

**DoD M0.D:** Counts fresh documented als Vault-File `cron-baseline-<YYYYMMDD-HHMMSS>.json`. Wenn Zahlen driften von obigen Expectations → STOP, Analyse-v3 update nötig.

### M0.E · Operator-Consolidation

- Atlas APPROVE ✅
- Codex APPROVE-WITH-MODS → v1.1 mit mods ✅
- Lens APPROVE pending → nach Upload

**Dispatch-Unblock-Condition:** Lens-APPROVE gegen v1.1 erhalten → `m0-approved: true` in Frontmatter → Dispatch-Wave 1.

---

## Sprint-M Sub-Tasks

### Phase M.1 — Audit-Repair

#### M1 · `cron-health-audit.sh` Regex-Fix

**Agent:** Forge · **Effort:** 2-3h · **Depends on:** —

**Scope (v1.1 geändert):** Nur noch Regex-Strictness in `cron-health-audit.sh`. ENV-Cross-Check umgezogen zu M4 (→ `script-integrity-check.sh`).

**Problem:** Case-insensitive `grep 'error|fail'` matcht `auto-failed=0`, `stalled-hard-failed=0` in Normal-Status-Zeilen → v1-Analyse zählte 5192 errors wo <50 legitim waren.

**DoD (falsifizierbar):**
1. Regex-Strictness: `grep -E '^\S+ (ERROR|FATAL|CRITICAL|ALERT)'` oder JSON-Log-Parser mit `jq 'select(.severity>="error")'`.
2. Unit-Test-Fixtures `/home/piet/.openclaw/scripts/tests/cron-health-audit/clean.log` + `dirty.log` mit Expected-Output (exit-code + grep-counts).
3. Test-Run: `bash tests/cron-health-audit.test.sh` exit=0.
4. Regression-Check: `tail -1000 ~/.openclaw/workspace/scripts/worker-monitor.log | /home/piet/.openclaw/scripts/cron-health-audit.sh --test-stdin` gibt **≤ 5 error-matches** (vorher: >1000).
5. Backup `cron-health-audit.sh.bak-m1-$(date +%Y%m%d-%H%M%S)` vor Edit.

**Dispatch-Prompt:**
```
Task [Sprint-M v1.1 M1] cron-health-audit.sh Regex-Strict.
Read: scripts/cron-health-audit.sh + workspace/scripts/worker-monitor.log.
Fix: strict severity-regex. Add tests/cron-health-audit/ fixtures.
DoD: see plan v1.1 M1. R8: timestamped backup first.
R42 Verify: regression-tail-check returns ≤5 matches.
```

#### M2 · Audit liest Cron-Registry (stateful Pfad-Resolution)

**Agent:** Forge · **Effort:** 2-3h · **Depends on:** M1 + M3

**Scope:** Remove hardcoded log-paths. Audit-Tool iteriert `registry.jsonl`, resolved `logfile`/`schedule` dynamisch, berechnet expected-mtime-age aus Schedule-Kadenz.

**DoD (falsifizierbar):**
1. `cron-health-audit.sh` hat 0 hardcoded log-paths (grep `/home/piet/` in script = nur registry-path).
2. Gegen M3-Registry-Seed: 0 false-positives bei bekannten Clean-State.
3. Silent-ok-Schedules (z.B. build-artifact-cleanup weekly ohne stdout) werden korrekt NICHT als missing-log gemeldet.
4. Rollback via `.bak-m2-$(date +%Y%m%d-%H%M%S)`.

#### M3 · `cron/registry.jsonl` Schema + Initial-Population

**Agent:** Forge · **Effort:** 3-4h · **Depends on:** M0.D (Pre-Baseline)

**Scope:** Single-Source-of-Truth für alle 68 aktiven Schedules + 4 ENV-declarations (separate Kategorie).

**Reuse-Opportunity (Lens-Area):** `rules-md-to-jsonl.py` als Parser-Template.

**DoD (falsifizierbar):**
1. Schema-Datei `~/.openclaw/cron/registry.schema.json` als JSON-Schema.
2. `~/.openclaw/cron/registry.jsonl` mit **68 schedule-entries** + separate `~/.openclaw/cron/env-declarations.jsonl` mit **4 entries**.
3. `cron/registry-validate.py`: Schema-OK, 0 duplicate-names, 0 missing script-paths, count assertions (46/6/16).
4. `registry-validate.py` exit=0 erforderlich VOR M5-Dispatch.
5. Integrity-sanity: Zweiter Run von `registry-validate.py` mit gleichem File: identisches exit=0 (idempotent).

**Dispatch-Prompt:**
```
Task [Sprint-M v1.1 M3] cron-registry.jsonl + validate.
Read: v2-analysis §4.3 + HEARTBEAT.md §1.4 + M0.D baseline-json.
Populate registry.jsonl from crontab/systemd-list-timers/openclaw-cron
jobs.json. 68 entries expected (46+6+16); separate env-declarations.jsonl.
Reuse rules-md-to-jsonl.py pattern. DoD: registry-validate.py exit=0.
R42 Verify: diff counts against M0.D-baseline.
```

#### M4 · ENV-Cross-Check in `script-integrity-check.sh` + Schedule-Up + Canary-with-flock

**Agent:** Forge · **Effort:** 1.5-2h · **Depends on:** M1 + M3

**Scope (v1.1 geändert):** ENV-check zieht um von `cron-health-audit.sh` (falsche Quelle) zu **`script-integrity-check.sh:119-144`** (tatsächliche ENV_MISSING-Source). Plus Schedule-Up + Canary.

**DoD (falsifizierbar):**
1. **ENV-Cross-Check:** `script-integrity-check.sh` prüft jede in `env_required`-Feld der Registry deklarierte ENV gegen `grep -rln "\$ENVNAME" ~/.openclaw/scripts/ ~/.openclaw/workspace/scripts/`. Keine false-positives für ungenutzte ENVs.
2. **Schedule-Up:** `0 9 * * 1` (weekly) → `*/30 * * * *` in crontab. Verify: nach 30 min neue mtime auf `/tmp/cron-health-audit.log`.
3. **Canary-Cron mit flock (R33-konform):**
   ```
   0 */6 * * * flock -n /tmp/canary-alert.lock /home/piet/.openclaw/scripts/alert-dispatcher.sh canary info "canary-ok"
   ```
4. **Verify:** Innerhalb 6h ein `canary-ok` in #alerts; innerhalb 30min fresh audit-run.
5. Backup crontab vor Edit: `crontab -l > /home/piet/.openclaw/cron/crontab.bak-m4-$(date +%Y%m%d-%H%M%S)`.

### Phase M.2 — Scheduler-Consolidation

#### M5a · `cron-reconciler.py` READ-ONLY diff + validator (Sprint-M)

**Agent:** Forge · **Effort:** 2-3h · **Depends on:** M3

**Scope (v1.1 geändert — split from full reconciler):**

**NUR** read-only Diff-Detection + Validator. **KEIN** `--apply`. Kein `openclaw cron set` (existiert nicht). Apply-Capability → Sprint-N M5b (separate review-gate).

**Reuse-Opportunity:** `self-optimizer.py` dry-run-pattern als Template.

**DoD (falsifizierbar):**
1. `cron-reconciler.py --dry-run` (einzige Mode in v1.1) zeigt strukturierten Diff (JSON-Lines): Registry vs Live-State pro Scheduler.
2. Drift-Classifier: `missing_in_registry`, `missing_in_live`, `schedule_mismatch`, `command_mismatch`, `scheduler_mismatch`.
3. Test-Run gegen bekannten Drift (z.B. eine crontab-Line entfernen): Reconciler meldet `missing_in_live` mit Path+Schedule.
4. Test-Run gegen Clean-State: `ok=true, drift=[]`.
5. Exit-Code: 0 = clean, 1 = drift, 2 = error.
6. **NO apply-mode** — wenn `--apply` als Argument kommt: exit 3 mit Message *"apply deferred to Sprint-N M5b"*.

**Dispatch-Prompt:**
```
Task [Sprint-M v1.1 M5a] cron-reconciler.py READ-ONLY.
Depends on M3. Read registry.jsonl + live scheduler states.
Build dry-run/diff-only reconciler. NO --apply. NO openclaw-cron-set.
Reuse self-optimizer.py dry-run pattern.
DoD: clean-state = exit 0, drift-injection = exit 1 with structured output.
R42 Verify: apply-arg rejected with exit 3.
```

#### M6 · Memory-Orchestrator Script (v1.2: WIRKLICH read-only)

**Agent:** Forge · **Effort:** 2-3h · **Depends on:** M3 (Registry-READ)

**Scope (v1.2):** Nur **Script-Erstellung + Testing**. KEINE crontab-Mutation. KEINE systemd-Mutation. Crontab-Mutation wurde in **M6b** ausgelagert (sequenziell nach M7, verhindert Wave-3-Race).

**Reuse:** H10-Layer-2-shape aus `sprint-k-infra-hardening-plan-2026-04-19.md:197-211` (`memory-maintenance-suite.sh` Konzept).

**DoD (v1.2 falsifizierbar, wirklich read-only):**
1. `memory-orchestrator.py <phase>` erstellt unter `/home/piet/.openclaw/workspace/scripts/memory-orchestrator.py`. Phases: hourly, nightly, weekly, quarterly.
2. DAG explizit im Code: `qmd-update → kb-compiler → graph-edge-builder → dashboard-generator`.
3. Lock pro Phase: `/tmp/memory-orchestrator-<phase>.lock` via `flock` (R33).
4. **Dry-Run-Validation:** Manueller Run `memory-orchestrator.py nightly --dry-run` reproduziert semantisch die bisherigen 11 Einzelläufe (keine State-Mutation bei `--dry-run`).
5. **No-Touch-Verify (v1.2 neu):** `crontab -l > /tmp/crontab-m6-before.txt` **vor** M6-Deploy; `crontab -l > /tmp/crontab-m6-after.txt` **nach** M6-Deploy; `diff /tmp/crontab-m6-before.txt /tmp/crontab-m6-after.txt` **muss leer sein** (exit 0). Analog für `systemctl --user list-timers --all --no-pager`.
6. Script-Permissions: `chmod +x`. Script-integrity-check nimmt es auf.
7. Kein neuer crontab-Eintrag in M6 — das passiert in M6b.

#### M6b · Memory-Orchestrator Crontab-Mutation (NEU v1.2)

**Agent:** Forge · **Effort:** 30-45 min · **Depends on:** M6 (Script ready) + M7 (systemd-Migration abgeschlossen, damit M6b allein crontab-Writer ist)

**Scope:** Die 11 Memory-Cron-Lines in crontab auskommentieren, 4 Orchestrator-Cron-Lines hinzufügen, Registry aktualisieren.

**Warum sequenziell nach M7?** Wenn M6b parallel zu M7 liefe, wären zwei Prozesse gleichzeitig crontab-Writer → Race (Codex-Finding F1 + R-M-6 Mitigation).

**DoD (falsifizierbar):**
1. `crontab -l > /home/piet/.openclaw/cron/crontab.bak-m6b-$(date +%Y%m%d-%H%M%S)` (Rollback-Base).
2. `crontab -l > /tmp/crontab-m6b-before.txt`.
3. Mutation-Script `scripts/memory-cron-migrate.sh` (ad-hoc, nicht persistent): kommentiert die 11 Memory-Cron-Zeilen (qmd-update, kb-compiler, graph-edge-builder, kb-synth, retrieval-feedback, dashboard-generator, daily-reflection, importance-recalc, memory-layer-sweep, sqlite-vacuum, sqlite-maintenance) mit Präfix `# [Sprint-M M6b] superseded by memory-orchestrator `. Fügt 4 neue Zeilen hinzu für hourly/nightly/weekly/quarterly Orchestrator-Phases mit `flock`.
4. `crontab -l > /tmp/crontab-m6b-after.txt`.
5. `diff /tmp/crontab-m6b-before.txt /tmp/crontab-m6b-after.txt | grep -c '^[<>]'` = exakt **15 Änderungen** (11 auskommentiert + 4 hinzugefügt), keine anderen.
6. Registry (M3) update: 11 Einträge markiert mit `consolidated_into: memory-orchestrator`, 4 neue Einträge angelegt. `registry-validate.py` exit=0.
7. Post-deploy-Live-Test: Nach nächster `*/hour`-Marke existiert Eintrag im `memory-orchestrator` Log. Wenn nicht → Rollback via `crontab <bak-file>`.

**Rollback M6b:**
```sh
crontab /home/piet/.openclaw/cron/crontab.bak-m6b-<ts>
# + registry: 11 entries revert, 4 orchestrator-entries remove
```

#### M7 · Top-5 Kernel-Crons → systemd-timer Migration

**Agent:** Forge · **Effort:** 3-4h hands-on + **24h soak phase post-sprint** · **Depends on:** M5a (drift-visibility)

**Scope:** `auto-pickup`, `mc-watchdog`, `worker-monitor`, `session-freeze-watcher`, `stale-lock-cleaner` → systemd-user-timer.

**DoD (v1.2 geschärft, OnFailure= gedroppt):**
1. 5× `.timer` + `.service` units in `~/.config/systemd/user/`.
2. Jede Service-Unit: `Restart=on-failure`, `RestartSec=30`, `StartLimitBurst=5`.
3. Jede Timer-Unit: **`Persistent=true`** (missed-run recovery, Codex D8 + H10-L3). *(v1.2: `OnFailure=alert-dispatcher@%i.service` gedroppt — Template-Unit existiert nicht und Alert-on-Failure läuft bereits script-intern via `alert-dispatcher.sh` wie bei `mc-watchdog.sh`.)*
4. **Alert-Pipeline-Compat:** Jedes Script muss am Ende prüfen `if [[ $? -ne 0 ]]; then alert-dispatcher.sh <name> error "<msg>"; fi`. Falls ein Script das noch nicht tut → kurzer Wrapper in M7 nachziehen.
5. **Cutover-Safety (R-M-7 Mitigation):** Pro Cron:
   - Schritt 1: Kommentiere crontab-Line aus (R8 backup, timestamped).
   - Schritt 2: `systemctl --user daemon-reload && systemctl --user enable --now <name>.timer`.
   - Schritt 3: Warte 2× expected-interval; prüfe journalctl zeigt runs.
   - **KEIN überlappendes Enable** — cron muss OFF sein bevor timer ON ist.
6. Rollback-Script `systemd-migration-rollback.sh`: `systemctl --user disable --now <name>.timer` + `sed -i` uncomment + registry rollback-pointer.
7. Registry (M3) Updated: `scheduler` Feld crontab → systemd-timer.
8. **24h-Soak explicitly POST-SPRINT** (→ siehe §Soak-Phase); Sprint-M schließt nicht bevor Soak startet.

#### M8 · Cron-Audit-Final-Run + Baseline-Seed + Endreport

**Agent:** Forge + Atlas (verify) · **Effort:** 1-2h · **Depends on:** M1-M7 done

**DoD (falsifizierbar):**
1. `cron-health-audit.sh` fresh-run: **0 false-positive error-alarms**, **0 unexpected missing-log-alarms** (expected silent-ok schedules filtered).
2. Registry-diff-reconcile (M5a dry-run): `ok=true, drift=[]`.
3. Baseline-File `~/.openclaw/workspace/memory/cron-audit-baseline-$(date +%Y%m%d).json` mit Registry-Snapshot + Audit-Output gespeichert.
4. **NICHT-DoD (postponed to soak-phase):** ~~all 68 registry entries have lastRun populated~~ (daily/weekly schedules brauchen bis zu 7 Tagen).
5. Atlas postet Endreport-Task `[Sprint-M] Endreport` mit Before/After-Matrix. R49: inline-verify jede SHA/Session-ID.
6. Discord `#execution-reports` erhält Sprint-M-Completion-Message.

---

## §Soak-Phase (post-sprint, 24-72h)

**Scope:** Post-M8 Observation-Period.

**Abläufe:**
- 24h: M7 journalctl-check — jeder Kernel-Cron hat ≥ erwartete Starts.
- 48h: Registry-Drift-Check — `cron-reconciler.py --dry-run` mit exit=0.
- 72h: Audit-Run-Qualität — `cron-health-audit.sh` konsistent 0 false-positives.

**Sprint-M-Close-Trigger:** Nach 72h erfolgreichem Soak → Sprint-M formal closed, Sprint-N (M5b apply-capability) dispatchable.

**Soak-Failure-Mitigation:** Rollback-Script aus M7 nutzen; Sprint-M-Status auf REGRESSION; post-mortem vor Retry.

---

## Dispatch-Reihenfolge (DAG v1.2)

```
M0.D (Re-Baseline) ─┐
                    │
M0 (Atlas+Codex+Lens APPROVED)
    │
    ├─→ M3 (Registry) ──┬→ M2 (Audit uses Registry) ───────┐
    │                    ├→ M5a (Reconciler read-only)     │
    │                    └→ M6 (Memory-Orch SCRIPT only) ──┤
    ├─→ M1 (Regex-Fix) ─→ M4 (script-integrity + flock)  │
    │                                                      │
    │                    M5a → M7 (systemd-mig, cutover) ──┤
    │                                                       │
    │                                   M6 + M7 done ──→ M6b (crontab-mutate)
    │                                                        │
    └─→ all-done ──────────────────────────────────────── M8 (Final-Audit)
                                                             │
                                                             ▼
                                                    §Soak-Phase (24-72h)
                                                             │
                                                             ▼
                                                    Sprint-M CLOSED
                                                             │
                                                             ▼
                                                    Sprint-N (M5b apply)
```

**Waves (v1.2 angepasst — M6b neu, verhindert Wave-3-Race):**

- **Wave 0:** M0.D (5 min, baseline re-capture) — blocks M3
- **Wave 1:** M1 + M3 (parallel)
- **Wave 2:** M2 (nach M1+M3) + M4 (nach M1+M3) + M5a (nach M3)
- **Wave 3:** M6 read-only script-build (nach M3) **parallel zu** M7 systemd-migration (nach M5a) — **safe** weil M6 jetzt wirklich read-only ist
- **Wave 4 NEU:** M6b crontab-mutation für Memory-Orchestrator — **sequenziell nach M7** (damit M6b alleiniger crontab-Writer ist, kein Race)
- **Wave 5:** M8 (nach allen vorher)
- **Post-sprint:** Soak-Phase → Sprint-N unlocked

**R46-Compliance:** Kein Wave hat MC-Restart-Impact. M7 touched nur `systemd --user`. M6b touched nur crontab (ohne M7-Overlap). Keine Race.

**R-M-6 Mitigation (crontab-Writer-Serialization):** Crontab wird in v1.2 nur noch zu **3 separaten Zeitpunkten** geschrieben — nie überlappend:
- **M4 (Wave 2):** 1 Schedule-Change + 1 Canary-Line hinzu.
- **M7 (Wave 3):** 5 Kernel-Lines auskommentiert (cutover-protocol).
- **M6b (Wave 4):** 11 Memory-Lines auskommentiert + 4 Orchestrator-Lines hinzu.

M6 selbst (Wave 3) berührt crontab NICHT mehr.

---

## Risiken & Mitigations (v1.1)

| # | Risk | Severity | Mitigation |
|---|---|---|---|
| R-M-1 | M5a-Reconciler zerstört crontab | ELIMINATED | read-only in v1.1 — apply erst Sprint-N |
| R-M-2 | M7 systemd-mig bringt auto-pickup offline | MED | Cutover-Protocol (cron-off BEFORE timer-on), rollback-script, ≤10min Lücke |
| R-M-3 | M6 Memory-Orchestrator ändert qmd-State | MED | Dry-run full nightly, Atlas qmd-query-parity check |
| R-M-4 | M3 Registry misses a cron | LOW | M0.D re-baseline + validator exit=0 required |
| R-M-5 | M4 Canary macht #alerts noisy | LOW | 6h-Frequenz acceptable |
| **R-M-6** | M4/M6/M7 Crontab-Write-Races (NEU v1.1) | MED | Wave-Serialization (M4 Wave-2, M6+M7 Wave-3, not mixed) |
| **R-M-7** | M7 Double-Fire-Window während Cutover (NEU v1.1) | HIGH | Cutover-Protocol Schritt 1 (cron OFF) vor Schritt 2 (timer ON); kein Overlap |
| **R-M-8** | Registry Stale-Seed bei M3 (NEU v1.1) | MED | M0.D Pre-Baseline-Step |

---

## Success-Kriterien (Sprint-M v1.1)

**Sprint-M-CLOSE nach M8 (before soak):**
- [ ] M0.D Baseline-File committed
- [ ] `cron-health-audit.sh` Regression-Test: ≤5 matches (vorher ≥1000)
- [ ] Audit-Schedule `*/30min` live; fresh log < 30min mtime
- [ ] `registry.jsonl` = 68 entries + `env-declarations.jsonl` = 4 entries, validator exit=0
- [ ] `cron-reconciler.py --dry-run` exit=0 auf Clean-State
- [ ] `--apply` arg rejected with exit 3
- [ ] **M6:** `memory-orchestrator.py` exists, `--dry-run nightly` läuft; crontab-before/after-diff = leer (M6 truly read-only)
- [ ] **M6b:** 11 Memory-Crons kommentiert, 4 Orchestrator-Einträge aktiv, post-deploy-live-test fired successfully
- [ ] 5 Kernel-Crons disabled in crontab, active als systemd-timer mit `Persistent=true`
- [ ] Canary-Alert live with flock, ≥1 `canary-ok` in #alerts
- [ ] 0 reale Production-Incidents während Sprint-Execution
- [ ] Endreport auf Discord

**Sprint-M-TRULY-DONE nach Soak (72h post-M8):**
- [ ] 5 systemd-timer: journalctl ≥ expected runs
- [ ] Reconciler-dry-run über 3 Tage: drift=[]
- [ ] Audit-run konsistent clean
- [ ] Sprint-N dispatchable

---

## Rollback-Plan (pro Task isoliert, timestamp-unique)

Alle Backups mit `$(date +%Y%m%d-%H%M%S)` suffix:

- **M1:** `cp scripts/.archive-pre-sprint-m-2026-04-20/cron-health-audit.sh.bak-pre-sprint-m scripts/cron-health-audit.sh`
- **M2:** restore `.bak-m2-<ts>` aus M2-Deploy
- **M3:** `rm registry.jsonl env-declarations.jsonl` + revalidate live
- **M4:** `crontab /home/piet/.openclaw/cron/crontab.bak-m4-<ts>`
- **M5a:** `rm cron-reconciler.py` (no state-mutations in read-only mode)
- **M6:** `rm memory-orchestrator.py` (read-only, no crontab-state to revert)
- **M6b:** `crontab /home/piet/.openclaw/cron/crontab.bak-m6b-<ts>` + registry-revert
- **M7:** `systemd-migration-rollback.sh` — disable timers + uncomment crontab + registry-revert
- **M8:** N/A (read-only report)

**Global fallback:** crontab.bak-pre-sprint-m-2026-04-20 (schon erstellt 22:50 UTC) als Ultimate-Restore.

---

## Decision-Log (v1.1)

| Datum UTC | Reviewer | Verdict | Mods | Status |
|---|---|---|---|---|
| 2026-04-20 22:56 | Codex (v1.0) | APPROVE-WITH-MODS | 4 blocking + 3 questions | Resolved in v1.1 |
| 2026-04-20 ~22:xx | Atlas (v1.0) | APPROVE | M6-DoD-Clarification | Integrated in v1.1 |
| 2026-04-20 23:xx | Codex (v1.1 re-review) | APPROVE-WITH-MODS | 3 findings (M6-contradiction, M7-OnFailure-unit-missing, M6-verify-weak) | Resolved in v1.2 |
| 2026-04-20 23:xx | Lens (pending) | — | — | Re-dispatch gegen v1.2 |
| TBD | Operator (v1.2 consolidation) | — | — | nach Lens-APPROVE |

---

## Trigger-Phrases (post Lens-APPROVE)

- **„Atlas — dispatch Sprint-M v1.2 Phase M.1 Wave 1"** → M0.D (5min) + M1 + M3 parallel
- **„Atlas — dispatch Sprint-M v1.2 Wave 2"** → M2 + M4 + M5a
- **„Atlas — dispatch Sprint-M v1.2 Wave 3"** → M6 (read-only script) + M7 (systemd-mig)
- **„Atlas — dispatch Sprint-M v1.2 Wave 4"** → M6b (crontab-mutation Memory-Orch)
- **„Atlas — finalize Sprint-M v1.2"** → M8 + Endreport + Soak-Trigger

---

**v1.2 Ende.** Status: READY-FOR-LENS-REVIEW against this revised document (incorporating Codex v1.1-re-review findings).
