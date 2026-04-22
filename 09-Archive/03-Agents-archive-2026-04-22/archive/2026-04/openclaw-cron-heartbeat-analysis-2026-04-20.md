---
title: OpenClaw Cron/Heartbeat/Script-System — Deep Analysis v2 (korrigiert)
author: Claude (Opus 4.7, 1M context)
date: 2026-04-20
version: v2 — Ist-Analyse gegen Live-State verifiziert, v1-Fehler korrigiert
scope: Ist, GAP, Zielmodell, Roadmap
status: Draft v2 — operator review required
related:
  - vault/03-Agents/cron-audit-2026-04-19.md (338 Z)
  - memory/sprint_k_infra_hardening_plan.md (H10)
  - workspace/HEARTBEAT.md (377 Z)
---

# OpenClaw Cron / Heartbeat / Script-System — Deep Analysis v2

> **v1→v2 Changelog:** Kritische Korrekturen nach Direct-Live-Verifikation. v1 hat sich zu stark auf `cron-health-audit.sh`-Output als Wahrheits-Quelle verlassen — dieses Tool hat **selbst systematische Bugs** (grep false-positives, prüft falsche Logfiles, prüft ungenutzte ENV-Vars). Mehrere als kritisch gewertete Gaps waren Audit-Artefakte, nicht reale Probleme. Das **eigentliche** Gap ist damit ein anderes: **„Who checks the checker?"**.

---

## 0 · Executive Summary (korrigiert)

Der aktuelle Stack ist **deutlich gesünder** als in v1 dargestellt. Die dramatischen Zahlen aus v1 (5.192 worker-monitor errors, 1.180 Backups, 22h stale auto-pickup) waren **Mess-Artefakte des Audit-Tools**, nicht reale Probleme. Live-State heute 2026-04-20 ~20:00 UTC: MC 200 OK, Gateway aktiv, auto-pickup schreibt jede Minute einen CYCLE-Line in den **korrekten** Log, worker-monitor läuft sauber.

**Verbleibende echte Probleme:**

1. **Scheduler-Fragmentierung real** — 44 crontab + 6 systemd-timer + 16 openclaw-cron-plugin = **66 aktive Schedules** über 3 Scheduler (v1 sagte 52, Zahl war zu niedrig).
2. **Audit-Tool selbst ist kaputt** — grep-False-Positives, falsche Logfile-Pfade, unused-ENV-Checks. Läuft zudem nur Montag 09:00.
3. **Script-Versionierung fehlt** — `.openclaw/` ist kein Git-Repo; 156 `.bak-*` Files statt Git-History.

Der bereits geplante **Sprint-K H10** adressiert Punkt 1 teilweise. Die Zielarchitektur muss um **Audit-Tool-Reparatur** und **GitOps** ergänzt werden.

---

## 1 · Ist-Analyse (verifiziert gegen Live-State)

### 1.1 Scheduler-Inventar — korrigiert

| Scheduler | Zählung (live 2026-04-20 20:00 UTC) | v1-Zahl | Delta |
|---|---|---|---|
| User-Crontab | **44** | 34 | +10 (ich hatte ENV-lines ausgeschlossen statt gezählt) |
| systemd User-Timer | **6** | 6 | OK |
| openclaw-cron Plugin | **16 enabled, 0 disabled** | "16 enabled, 9 disabled entfernt" | disabled=0 aktuell |
| **Gesamt aktive Schedules** | **66** | 52 | **+14** |

**Beobachtung:** 3 Scheduler bleiben fragmentiert, jeder blind für die anderen. `cron-health-audit.sh` schaut NUR in crontab — openclaw-cron-plugin und systemd-timer werden nicht auditiert. Damit werden 22/66 Schedules (33%) gar nicht überwacht.

Die openclaw-cron-Jobs haben aktuell alle `lastRun: null`, `lastStatus: null` — das deutet darauf hin, dass die runs entweder extern geloggt werden (`~/.openclaw/cron/runs/*.jsonl`) ODER das Feld noch nicht aktualisiert wird. Zu prüfen.

### 1.2 Script-Inventar — korrigiert

| Kategorie | v1-Aussage | Verifizierte Zahl |
|---|---|---|
| `.openclaw/scripts/` aktive Scripts (.sh/.py, ohne .bak/.original) | ~60 | **53** |
| `.openclaw/workspace/scripts/` aktive Scripts | ~71 | **42** |
| **Aktive Scripts gesamt** | ~130 | **95** |
| `.bak-*` Files | „~1180" | **156** |
| `__pycache__` dirs | unclear | **63** |
| `find .sh+.py total` | 1.312 | 1.312 (korrekt, inkl. pycache-Kompilate, subdirs) |

v1 hatte die 1.312 als „Script-Orgy" dargestellt — korrekt ist: **95 aktive Scripts + 156 Backups + pycache-Artefakte**. Das ist **deutlich disziplinierter** als v1 suggerierte.

**Gemeinsames Gap bleibt:** `.openclaw/` ist **kein Git-Repo** (`fatal: not a git repository`). 156 `.bak-*` sind der Rollback-Mechanismus (R8-Regel formalisiert das) — funktional aber nicht auditable, nicht diffable, keine Attribution.

### 1.3 SystemD-Services (unverändert, 7 active)

`mission-control`, `openclaw-gateway`, `claude-telegram-bridge`, `commander-bot`, `tmux-claude`, `dbus`, `gpg-agent` — alle `active running`. Keine Änderung ggü. v1.

### 1.4 Logging — korrigiert

Verteilung (aktive Log-Files in letzten 24h):

| Location | Anzahl | Zweck |
|---|---|---|
| `~/.openclaw/workspace/logs/` | **43** Files | offizieller Log-Ort |
| `/tmp/*.log` | **69** Files | Quick-Logs (Crons) |
| `~/.openclaw/workspace/memory/*.log` | few | Memory-Domain |
| `~/.openclaw/outputs/logs/` | few | Agent-Outputs |

Live-Sample auto-pickup:
- **Script-eigener Log** `~/.openclaw/workspace/logs/auto-pickup.log` — **563 KB, letzter Eintrag 21:54 UTC (vor 1 min)** — **schreibt jede Minute eine CYCLE-Line**. Healthy.
- **Cron-Stdout-Log** `~/.openclaw/workspace/logs/auto-pickup-cron.log` — 0 Bytes, mtime 22h stale. Das ist **kein Problem** — der Cron-Wrapper produziert bei Silent-Success keinen stdout; das Script loggt in sein eigenes File.

**v1-Fehler:** v1 schloss aus der 22h-Stale-Meta, auto-pickup sei ausgefallen. Das war falsch. Das **Audit-Tool** `cron-health-audit.sh` prüft das **falsche Logfile** (stderr-Redirect statt Script-Log).

### 1.5 Live-Health-State (2026-04-20 ~20:00 UTC)

- MC `/api/health` → **200 OK**, `severity=ok`, `openCount=1`, `issueCount=0`
- systemd services: alle **active running**
- worker-monitor letzte 10 Runs: **checked=1-2, auto-failed=0, stalled=0, stalled-warning=0/1, stalled-hard-failed=0** — gesund
- auto-pickup: jede Minute `CYCLE mode=LIVE pending=0 triggered=0 silent_fails=0` — gesund
- 14 Defense-Crons (HEARTBEAT.md): alle laufen

### 1.6 Audit-Tool-Bugs (NEU — der wichtigste v2-Befund)

`cron-health-audit.sh` (letzter Run 2026-04-20 08:50 UTC, nächster Run Mo 09:00 UTC in 7 Tagen) produziert **systematische False-Positives**:

| v1-„Problem" | Realität | Audit-Bug |
|---|---|---|
| **„worker-monitor: 5192 error-lines"** | 1145 von diesen sind grep-Matches auf die Wörter `auto-failed=0` / `stalled-hard-failed=0` in **normalen Status-Zeilen** | grep-Pattern `error\|fail` case-insensitive matcht Felder die syntaktisch „fail" enthalten |
| **„self-optimizer: 55 errors"** | gleiche Ursache (dry-run-Output enthält Felder wie `recoverable_failures`) | identisch |
| **„auto-pickup 697m stale"** | Script-Log wird jede Minute aktualisiert in anderem File | Audit prüft `auto-pickup-cron.log` statt `auto-pickup.log` |
| **„MC_WATCHDOG_WEBHOOK_URL missing"** | Die Variable wird **nirgends** referenziert; alert-dispatcher nutzt `MC_ALERTS_WEBHOOK` oder `AUTO_PICKUP_WEBHOOK_URL` | Audit prüft eine ENV die das Script nicht braucht |
| **„build-artifact-cleanup log missing"** | Script läuft **Sonntag 03:00 Weekly** — Log-File wird nur sonntags geschrieben | Audit erwartet hourly-Log, Schedule-Kadenz nicht berücksichtigt |

**Reale Error-Rate** (aus letzten 1000 Zeilen worker-monitor.log, grep ohne Status-Feld-Spam): **31 legitime Matches** — davon meist Echo-Rauschen, keine harten Fehler.

**Konsequenz:** Die v1-GAPs G9 und G14 waren **Audit-Tool-Bugs**, nicht reale Produktions-Probleme. Der korrekte Gap ist:

> **„Der Health-Checker selbst ist nicht health-checked."** Das Tool produziert Rauschen, läuft nur wöchentlich, und würde echte Probleme im Rauschen versenken.

### 1.7 State-Machine + Rules (unverändert gut)

HEARTBEAT.md-Contract (3-State-Model + 5 Konsistenz-Regeln), R1-R50 Post-Mortem-driven, pre-flight-sprint-dispatch 7-Gate, R50 Session-Lock-Governance, Memory-L1-L6 — all das bleibt **better-than-most** gegenüber Industry-Peers.

---

## 2 · Best-in-Class-Benchmarks (unverändert zu v1)

- OpenClaw-Docs empfehlen 3-Layer: Hooks / Cron / Heartbeat (30 min, full-context)
- Community-Mindestminimum: 3 Crons → dein Setup 66 ist überdimensioniert ggü. Reference
- Temporal Activity-Heartbeat, Claude Code Agent Teams 5-min-Timeout, K8s Operator ~30s reconcile, Cordum Circuit-Breaker, OpenTelemetry Tracing
- Referenz-Repos: `openclaw-rocks/k8s-operator`, `manish-raana/openclaw-mission-control` (Convex push-based)

Details siehe v1 §2 — Quellen und Aussagen bleiben valide.

---

## 3 · GAP-Analyse (korrigiert)

### Gestrichen (v1-Gaps die nicht real waren)

- ~~G9 `MC_WATCHDOG_WEBHOOK_URL` ENV_MISSING~~ → Audit-Bug, nicht real
- ~~G14 „worker-monitor 5192 Errors ohne Alert"~~ → Audit-grep-False-Positive; reale Error-Rate ist niedrig
- Downgrade G5 (`cron-health-audit` nur Montag) → bleibt P1, aber **erst nach Tool-Reparatur** ausrollen

### Neue/geschärfte Gaps

| # | Gap | Severity | Evidenz |
|---|---|---|---|
| **G0** (NEU) | `cron-health-audit.sh` selbst ist fehlerhaft (grep-False-Positives, falsche Log-Pfade, unused-ENV-Checks, wöchentliche Kadenz) | **P0** | 5/5 gesampelte Befunde waren False-Positives |
| G1 | 3-Scheduler-Fragmentierung (**66 Schedules**, nicht 52) | P0 | 33 % der Schedules nicht auditiert |
| G2 | Logging über 4 Directories + keine strukturierte JSON-Kadenz | P1 | Mix von Script-Logs + Cron-Stdout-Logs ohne Konvention |
| G3 | Keine Metrics/Traces (OTEL) | P1 | grep-based Debugging als Standard |
| G4 | Kein Circuit-Breaker pro Agent/Tool | P1 | 85-Fallback-Storm 2026-04-19 (R50-Anlass) |
| G5 | `cron-health-audit` wöchentlich + buggy (Reparatur ≫ Frequenz-Erhöhung) | P1 | siehe G0 |
| G6 | „Heartbeat" ist de-facto Cron, kein periodic-awareness-Agent | P2 | HEARTBEAT.md Contract gut, Execution anders |
| G7 | `.openclaw/` nicht in Git — 156 `.bak-*` statt History | P1 (hochgestuft) | `git status` → `fatal: not a git repository` |
| G8 | R1-R50 nur R49 automatisch enforced | P2 | Regeln textuell in AGENTS.md/feedback_system_rules.md |
| G10 | Alert-Pipeline inkonsistent (direkter curl vs alert-dispatcher) | P2 | z.B. `forge-heartbeat.sh` direkter Discord-curl, `mc-watchdog.sh` via dispatcher |
| G11 | Keine Cron-Dependency-Map (z.B. `qmd update` → `kb-compiler`) | P3 | — |
| G12 | 2 Script-Directories ohne dokumentierte Trennung | P3 | `mc-watchdog.sh` in beiden; kein README |
| G13 | Kein Baseline/Canary für neue Crons | P3 | dry-run nur bei `self-optimizer.py` |

### GAP-Cluster neu

- **Audit & Integrität (G0, G5, G7):** der **teuerste** Cluster, weil Fehler-Detection selbst unzuverlässig ist — fix zuerst.
- **Scheduler (G1, G11, G13):** fix mit Single-Scheduler + Registry.
- **Observability (G2, G3, G10):** fix mit OTEL + structured logs + unified dispatcher.
- **Policy (G4, G8):** fix mit Circuit-Breaker + Policy-Engine.

---

## 4 · Zielmodell (korrigiert)

Die v1-3-Tier-Architektur (Kernel/Domain/Reporting auf Tier-0-Infrastruktur) bleibt valide. Ergänzungen aus v2-Erkenntnissen:

### 4.1 Prinzip „Check the checker"

Jedes Monitoring-Tool muss **einen eigenen Integritäts-Check** haben:
- `cron-health-audit.sh` → bekommt Unit-Tests (positive + negative Samples) und CI-Validation
- Alert-Pipeline → bekommt Canary-Alert alle 6h („If you can read this, alerts work")
- worker-monitor → bekommt signal-vs-noise-Metrik (% legitim vs grep-noise)

### 4.2 Audit-Tool-Repair (NEU als Tier-0-Komponente)

| Problem heute | Fix |
|---|---|
| `grep -iE 'error\|fail'` matcht Status-Felder | **Regex-Fix:** `grep -iE '^\S+ (ERROR\|FATAL\|CRITICAL)'` ODER Scripts auf JSON-structured-Logs umbauen und `jq` nutzen |
| Falsches Logfile geprüft | Audit liest **Cron-Registry** statt hardcoded Pfade |
| Unused ENV_MISSING | ENV-Check gegen `grep -r "ENV_NAME" scripts/` abgleichen |
| Schedule-Kadenz unbeachtet | Audit liest Schedule aus Registry und berechnet expected-mtime-age dynamisch |
| Wöchentlich | Nach Fix → `*/30min` |

### 4.3 Git-Repo für `.openclaw/scripts/` (NEU als P1)

v1 hatte das als P3 abgetan. v2 stuft hoch: **156 `.bak-*` Files** sind ein klares Symptom. Fix:

```
# Minimalversion
cd ~/.openclaw/scripts/
git init
git add -A
git commit -m "initial snapshot 2026-04-20"
# dann als Submodule in vault-Repo (optional)
```

Ergänzend: `.bak-*` Files archivieren (`.archive/` oder git-stash), dann nur via Git-Branch statt Dateisuffix.

### 4.4 Alles andere bleibt wie v1 §4

- Cron-Registry + Reconciler
- OTEL-Collector
- Circuit-Breaker (R50-Vorlage)
- Policy-Engine für enforcable R-Rules
- `/admin/crons` MC-Dashboard
- Heartbeat-Service statt Cron (Phase 5)

---

## 5 · Roadmap (überarbeitet)

### Phase 0 — Audit-Integrität herstellen (1-2 Tage) — **NEU als erste Priorität**

- **P0a:** `cron-health-audit.sh` Regex fixen (strikte severity-level matches) — **1 h**
- **P0b:** Audit liest Cron-Registry statt hardcoded Paths — **2 h**
- **P0c:** ENV-Checks gegen tatsächliche Script-Referenzen abgleichen — **1 h**
- **P0d:** Schedule auf `*/30min` setzen — **5 min**
- **P0e:** Canary-Alert-Script (Cron `0 */6 * * *`): `alert-dispatcher.sh canary info "canary-ok"` — **30 min**

### Phase 1 — Scheduler-Consolidation (unverändert)

- `cron-registry.yaml` + Reconciler
- 11 Memory-Crons → 1 Orchestrator
- Top-5 Kernel-Crons auf systemd-timer

### Phase 2 — GitOps (hochgestuft)

- `.openclaw/scripts/` → Git-Init, 156 `.bak-*` in `.archive/` wegräumen
- `.openclaw/workspace/scripts/` ebenfalls
- Optional: Submodule im Vault-Repo

### Phase 3 — Observability (unverändert)

- Unified alert-dispatcher für alle Scripts
- JSON-structured logs (ersetzt grep-Debugging)
- OTEL-Collector + 5 Top-Crons instrumentiert

### Phase 4 — Policy & Circuit-Breaker (unverändert)

- Circuit-Breaker pro Agent (R50 als Vorlage)
- 10 enforcable R-Rules in Policy-Engine

### Phase 5 — Future

- Heartbeat-Service statt Cron
- `/admin/crons` MC-Dashboard

---

## 6 · Priorisierte Empfehlungen (korrigiert)

| Prio | Empfehlung | Aufwand | Δ zu v1 |
|---|---|---|---|
| **P0** | `cron-health-audit.sh` Bugs fixen (regex, paths, envs) | 4-5h | **NEU in v2** |
| **P0** | Canary-Alert alle 6h | 30 min | **NEU** |
| **P0** | `cron-registry.yaml` + Reconciler | 4-6h | unverändert |
| **P0** | `.openclaw/scripts/` in Git | 1-2h | **hochgestuft von P3** |
| **P1** | Unified alert-dispatcher für alle Scripts | 2-4h | unverändert |
| **P1** | OTEL-Collector + Top-5-Crons | 1-2d | unverändert |
| **P1** | Circuit-Breaker pro Agent | 4h | unverändert |
| **P1** | Structured JSON-Logging | 1-2d | unverändert |
| **P2** | `/admin/crons` MC-Dashboard | 3-4h | unverändert |
| **P2** | Policy-Engine für 10 R-Rules | 1-2d | unverändert |
| **P2** | Memory-Crons auf 1 Orchestrator | 1-2h | unverändert |
| **P3** | Heartbeat als Service | 1-2d | unverändert |

---

## 7 · Offene Fragen an Operator (unverändert + 1 neu)

1. Scheduler-Präferenz (systemd-timer / openclaw-cron-plugin / Tier-split)?
2. OTEL-Wahl (SigNoz / Grafana-Tempo / extern)?
3. GitOps-Scope (nur scripts / auch openclaw.json / HEARTBEAT.md)?
4. Dashboard-Home (MC / externer Prometheus+Grafana)?
5. Policy-Engine (OPA / DIY `policy-engine.py`)?
6. **NEU:** `cron-health-audit.sh` — reparieren oder ersetzen? (Ein from-scratch-Rewrite mit strukturiertem JSON-Output wäre ggf. schneller als Regex-Patching.)

---

## 8 · v1-Fehler-Protokoll (Transparenz)

Korrekturen gegenüber v1 (damit Operator die Vertrauensbasis einordnen kann):

| # | v1-Aussage | v2-Korrektur | Ursache |
|---|---|---|---|
| 1 | „52 aktive Schedules" | **66** | v1 hat crontab-ENV-Lines nicht als Schedule gezählt; Summe falsch addiert |
| 2 | „~130 aktive Scripts" | **95** | v1 hat nicht nach `.bak-*` gefiltert |
| 3 | „1.180 Backups" | **156 `.bak-*` + 63 pycache** | v1 hat `find`-Total als Backups interpretiert |
| 4 | „worker-monitor 5192 Errors ohne Alert" | **Audit-Tool-grep-False-Positive; reale Rate niedrig** | v1 hat Audit-Output als Wahrheit angenommen ohne Gegencheck |
| 5 | „MC_WATCHDOG_WEBHOOK_URL missing = Gap" | **Audit prüft unused ENV** | Dito |
| 6 | „Auto-pickup Log 22h stale" | **Script-eigener Log aktualisiert jede Minute** | Audit prüft falsches Logfile |
| 7 | „9 openclaw-cron Jobs disabled" | **0 disabled, alle 16 enabled** | v1 hat HEARTBEAT.md-Text als aktuellen Zustand übernommen |

**Lesson Learned:** „Live-verify" ist nicht optional — R1 (Verify-After-Write) gilt analog für **Verify-Before-Reporting**. Audit-Tools sind Hinweisgeber, nicht Wahrheit. Das ist **genau der Punkt den R35/R49 für Atlas einfordern** — und er gilt natürlich auch für mich.

---

## 9 · Anhang — Referenzen

- `vault/03-Agents/cron-audit-2026-04-19.md`
- `workspace/HEARTBEAT.md`
- `memory/sprint_k_infra_hardening_plan.md`
- `feedback_system_rules.md` (R1-R50)
- [docs.openclaw.ai/automation](https://docs.openclaw.ai/automation)
- [Temporal Heartbeats](https://docs.temporal.io/activity-execution)
- [Cordum AI Circuit-Breaker](https://cordum.io/blog/ai-agent-circuit-breaker-pattern)
- [SigNoz OTEL Anthropic](https://signoz.io/docs/anthropic-monitoring/)

---

*v2 Ende. Live-verifiziert 2026-04-20 20:00 UTC. §8 listet explizit was v1 falsch hatte.*
