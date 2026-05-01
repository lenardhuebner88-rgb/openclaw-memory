---
title: Sprint-1 Stabilization — Partial Closure (Codex-Fix-Pass)
date: 2026-05-01
status: report
related_sprint: update-2026.4.27-stab
parent_run_log: workspace/memory/working/2026-05-01-codex-fix-pass.md
---

# Sprint-1 Stabilization — Partial-Closure-Report 2026-05-01

## TL;DR

4 von 6 Sprint-1 Tasks sind durch den Codex-Fix-Pass (2026-05-01) und den vorherigen Audit (2026-04-30 Phase 7) **inhaltlich erledigt** und im Board auf `status=done` gesetzt. 2 Tasks bleiben offen: **T1 Nacht-Outage RCA** (P0) und **T6 OAuth+OpenRouter** (P0, Operator-Action).

## Closure-Matrix

| Task-ID | Sprint-Tag | Title | Closure-Pfad | resolvedAt |
|---|---|---|---|---|
| `7b67b446` | S1-T2 | Logrotate für 3 Spam-Logfiles | Codex-Fix-Pass T1 | 2026-05-01T11:53:58Z |
| `673dcaf3` | S1-T3 | Stale lock-File-Cleanup verifizieren | Audit Phase-7 (2026-04-30) | 2026-05-01T11:55:38Z |
| `e0922d9e` | S1-T4 | DeprecationWarning utcnow() | Codex-Fix-Pass T2 | 2026-05-01T11:55:37Z |
| `ea33ee3f` | S1-T5 | bundle-lsp disposal-error | Codex-Fix-Pass T3 | 2026-05-01T11:55:37Z |
| `7d5cf720` | S1-T1 | RCA Nacht-Outage MC DOWN 10x | **OPEN** | — |
| `f5f5a778` | S1-T6 | Operator-Action OAuth+OpenRouter | **OPEN** (Operator) | — |

## Evidenz pro Task

### S1-T2 Logrotate (`7b67b446`)
- Config: `~/.config/logrotate.d/openclaw-workspace`
- Policy: daily, 14d keep, gzip+delaycompress+copytruncate
- Timer: `logrotate.timer` enabled (next run: 2026-05-02 05:00 CEST)
- Disk-Effekt: 88% → 83% used (~5 GB freed durch initialen Cleanup-Sweep)

### S1-T3 Stale-Lock-Cleanup (`673dcaf3`)
- Skript-Erweiterung: `~/.openclaw/scripts/stale-lock-cleaner.sh`
- Neue Scope: `mission-control/data/locks/*.lock` mit 30min-mtime-Threshold (zusätzlich zu agent-jsonl-locks)
- Backup: `/home/piet/backups/2026-04-30-stale-lock-fix/stale-lock-cleaner.sh.orig`
- 24h-Live-Run: 0 stale locks

### S1-T4 utcnow() Deprecation (`e0922d9e`)
- Datei: `~/.openclaw/scripts/apply-mcp-recovery-patch.py`
- Replacement: `datetime.utcnow()` → `datetime.now(datetime.UTC)`
- `python3 -m py_compile` passes
- 0 `utcnow` matches in der Datei
- Verify nach 13:25 UTC Gateway-Restart: kein DeprecationWarning mehr

### S1-T5 bundle-lsp disposal-error (`ea33ee3f`)
- journalctl-Count seit 2026-04-30 20:35: **1** (einmalig beim 4.24→4.27-Übergang)
- Nach 2026-05-01 13:25 UTC controlled Gateway-Restart: **0** disposal-errors
- Klassifikation: RESOLVED-TRANSIENT (Module-Resolution-Glitch beim Versions-Wechsel)
- Kein Upstream-Issue notwendig

## Was bleibt offen (für Atlas)

### S1-T1 Nacht-Outage RCA (`7d5cf720`) — P0
Die mc-critical-alert hat 30.04 zwischen 00:25-05:13 UTC 10× "MC DOWN" gepostet. Root-Cause-Analyse ist **nicht** dokumentiert. Phase-1-Forensik im Audit-Run-Log (`2026-04-30-mc-night-outage-rca.md`) hat mind. die Trigger-Sequenz erfasst:
- 22:40 UTC Atlas selbst hat `mc-restart-safe atlas-v3-night-slice-deploy` getriggert
- Build crashte auf `/kanban-v3-preview/page` Export-Error
- systemd-restart-Loop 5h, weil `StartLimitIntervalSec=15min` zu kurz war
- Heute morgen 11:28 erfolgreicher Recovery (mit gefixter `page.tsx`)
- Restart-Policy gestern verschärft (`StartLimitIntervalSec=120s`)

**Atlas-Job:** RCA-Doc unter `vault/04-Sprints/reports/2026-04-30-mc-night-outage-rca.md` schreiben. Closure-PATCH danach.

### S1-T6 OAuth+OpenRouter (`f5f5a778`) — P0 Operator-Action
- Anthropic-OAuth war seit 2026-04-08 abgelaufen (~24 Tage)
- OpenRouter-Account leer
- Beide nur per Operator (Lenard) lösbar — Codex/Atlas können das nicht autonom machen
- Aufgabe-Detail in `vault/03-Agents/operator-actions-2026-04-29.md`

## Health post-closures

```json
{
  "status": "ok",
  "severity": "ok",
  "openCount": 0,
  "issueCount": 0,
  "consistencyIssues": 0,
  "totalTasks": 869
}
```

## Maintenance-Pointer

Dieser Report wird durch `sprint-index-generator.py` (geplant Sprint-5 T5.2) automatisch in `vault/04-Sprints/INDEX.md` referenziert. Bis dahin: manuell pflegen.
