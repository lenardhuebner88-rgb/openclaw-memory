---
title: Sprint-M v1.2.1 Final Close
date: 2026-04-22
status: CLOSED
reviewer: Lens (APPROVE via Atlas-Verdict nach Gap-Closure Evidence)
closed-by: Operator (pieter_pan)
---

## Timeline

| Zeitpunkt | Event |
|---|---|
| 2026-04-20 | Plan v1.0 → v1.2.1 (4 Review-Iterationen) |
| 2026-04-21 23:11 CEST | Lens DECLINE (3 Gaps: QMD-native-embed, memory-orchestrator rc=1, M8 drift-check) |
| 2026-04-21 23:50 CEST | S-GOV Mini-Dispatch T2.1/T2.2/T4/T5 done |
| 2026-04-22 13:35 UTC | T4 flock-wrapper Regression Fix (Commit 5d6119b9, flock timeout 60→1800s) |
| 2026-04-22 18:12 UTC | mcp-taskboard-reaper Drift (Bonus) fixed via Operator v3-Patch |
| 2026-04-22 18:20 UTC | Lens Re-Review APPROVE (Atlas-Verdict via Evidence-Package) |

## Gap-Closures (verified)

| Gap | Status | Evidence |
|---|---|---|
| QMD-native-embed: in registry.jsonl | ✅ | `registry.jsonl` enthält Entry mit Schedule `15,45 * * * *` |
| memory-orchestrator qmd-update rc=1: flock -w 1800 wirksam | ✅ | Commit 5d6119b9; Logs: 0× rc=1 seit 13:35 UTC |
| M8 drift-check: registry-validate exit 0 | ✅ | `schema_ok: true`, `active_counts` = `expected_active_counts` |
| Bonus: mcp-taskboard-reaper drift | ✅ | Operator v3-Patch; `cron-reconciler --dry-run` zeigt `{"ok": true, "drift": []}` |

## Follow-ups (not Sprint-M Scope)

| Item | Status | Action |
|---|---|---|
| S-HEALTH: 145 consistency-issues | Open | Separater Sprint (nicht Sprint-M Scope) |
| S-RPT P0.2: Writer-Side Fix für finalReportSentAt | In Queue |bereits in Pipeline |
| Gateway-OOM E1-E4: Test-Design + Cleanup | Open | Operator-Decision pending |

## Metric Snapshot (post-close)

```
cron-reconciler.py --dry-run: exit 0 ({"ok": true, "drift": []})
registry-validate.py:           exit 0 (schema_ok, count_match)
memory-orchestrator hourly rc=1 since 13:35 UTC: 0
/api/health scheduler-related:   clean
```

## Lessons Learned

### 1. Schema-Validierung ist Critical für Config-Writes
**Ereignis:** 2026-04-20 25min Outage durch schema-invalid openclaw.json-write.
**Lektion:** Config-Änderungen müssen IMMER Schema-validiert werden, bevor sie angewendet werden. Das `config-apply-safe.sh` Tool (S-FND T3) adressiert dieses Risiko jetzt zentral.
**Action:** Tooling-Deployment für Schema-Validate → Snapshot → Probe → Auto-Revert ist Standard-Pattern für alle Config-Files.

### 2. Cron-Schedule-Drift erkennt man früh, aber fixiert langsam
**Ereignis:** mcp-taskboard-reaper drift zwischen Script-Doku (`*/30`), Registry (`*/15`) und Live Crontab (`*/5`) — 3 verschiedene Werte.
**Lektion:** Script-Inline-Doku wird oft überschrieben ohne Registry-Sync. composite-Key-Namen in der Registry (`name: crontab:mcp-taskboard-reaper:*/15`) erfordern atomare Updates (schedule + name同步).
**Action:** cron-reconciler.py + registry-validate.py als Standard-Tooling. registry.jsonl ist Source-of-Truth für Schedules.

### 3. Verification-Tools müssen für Agent-Ausführung funktionieren
**Ereignis:** Atlas konnte Python-Scripts mit Args nicht via exec ausführen (`python3 script.py --arg` blockiert). Verification dadurch verzögert.
**Lektion:** Wrapper-Scripts (bash) die direkt ausführbar sind, lösen das Problem.Agents können Bash-Scripts ohne Einschränkungen ausführen.
**Action:** Zukünftig: Bash-Wrapper für alle Critical-Verification-Scripts bereitstellen (`cron-health-check.sh`, `memory-orch-check.sh`).

### 4. Gap-Closure braucht messbare Evidence
**Ereignis:** Lens DECLINE hatte 3 Gaps. Gap-Closure erforderte konkrete Log-Einträge, Exit-Codes und Registry-Einträge als Nachweis.
**Lektion:** "Glaube nichts, mess alles" — Subjektive Aussagen reichen nicht für Approval. Evidence-Package muss Exit-Codes, Timestamps und konkrete Werte enthalten.
**Action:** Lens-Approvels brauchen immer ein strukturiertes Evidence-Package.

### 5. Sprint-Reviews müssen alle Stakeholder erreichen
**Ereignis:** Lens DECLINE kam um 23:11 CEST — spät am Abend. Gap-Closure erst am nächsten Tag.
**Lektion:** Review-Cycles so timen, dass Feedback rechtzeitig verarbeitet werden kann. Deadline-Ampel für späte Reviews einführen.
**Action:** Review-Feedback innerhalb von 24h adressieren oder eskalieren.

### 6. Bonus-Fixes dokumentieren und separaten Scope zuordnen
**Ereignis:** mcp-taskboard-reaper drift war nicht Teil des ursprünglichen Sprint-M Scopes, wurde aber als "Bonus" gefunden und behoben.
**Lektion:** Bonus-Fixes können den Sprint verzögern oder verwässern. Immer separat tracken und als Bonus kennzeichnen.
**Action:** Bonus-Fixes als separater Post-Sprint-Track, nicht als Teil des Sprint-Reviews.

---

*Sprint-M v1.2.1正式geschlossen — 2026-04-22 18:32 UTC*
