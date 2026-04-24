---
title: Sprint-K Infra-Hardening Atlas-Dispatch-Prompt
date: 2026-04-19 20:30 UTC
status: superseded
trigger_suggestion: "Atlas Sprint-K Infra-Hardening starten"
estimated_effort: 14-18h orchestriert (8 subs, H1 bereits done)
prerequisites: Sprint-I Mobile-Polish done, R47-R49 deployed (done ✅)
---

# Sprint-K Dispatch-Prompt (Copy-Paste für Atlas)

```
REAL_TASK=true ORCHESTRATOR_MODE=true. Sprint-K Infra-Hardening — NICHT heartbeat.

Kontext:
Nach Sprint-E/F/G/H/I (Mobile-Polish) ist das System feature-komplett aber hat 8 systemische Infra-Gaps die durch Live-Cases identifiziert wurden. Sprint-K schließt diese:
- Atlas-Hallucination 2026-04-19 (fabricierte Commit-SHAs) → R49 mit Runtime-Enforcement
- R46 MC-Flap-Loop 17:06-17:22 UTC durch parallele deploy-contracts
- R45 Receipt-Drift Sub-Agents (E2/E3/E5a 2h+ assigned)
- Sprint-F operatorLock-Bypass → R47 3-Layer-Enforcement (J2 kann done sein oder offen)
- Budget-Alert $3 bug spammt Discord seit Tagen
- Sprint-E Playwright Contrast-AA Violations auf /monitoring + /alerts (4×)

Plan-Doku: /home/piet/vault/03-Agents/sprint-k-infra-hardening-plan-2026-04-19.md
(qmd deep_search "sprint-k infra hardening")

9 Sub-Tasks (H1 bereits done + H10-L1 cleanup done by Assistant 2026-04-19 23:12 UTC):
- Sub-K2 (Forge): Tool-Allowlist statt Tool-Denylist (Sub-Agents dürfen `systemctl` nicht mehr direkt → mc-restart-safe zwingen). 2-3h
- Sub-K3 (James→Forge): memory-core reconcile debug (Background-Reconciler spams logs). 1-2h
- Sub-K4 (Forge): Concurrent-Subagent-Limit mit MC-Restart-Contract (max 1 mit deploy-verify gleichzeitig). 2h
- Sub-K5 (Forge): R44 Board-Discipline Enforcement (sessions_spawn ohne Board-Task Ban). 1h
- Sub-K6 (Forge + Pixel): Receipt-Lifecycle-Enforcement — 4 Layers
  - L1 Agent-Prompt-Preamble (done ✅ in AGENTS.md)
  - L2 Dispatcher Auto-Transition assigned→in-progress on session-write (1-2h)
  - L3 Worker-Monitor Extension stall-detection für assigned>10min (1h)
  - L4 NEW: Commit-Signal Auto-Result (aus J1 RCA, 2h) — git post-commit hook oder Dispatcher-cron watches git log matches task-scope → auto receipt=result
- Sub-K7 (Forge): Deploy-Queue-Lock (mc-restart-safe Wrapper Integration in alle Agent-Prompt-Templates + Worker-Verify-Step). 2h
- Sub-K8 (Forge): Budget-Alert $3 bug (False-alarm spammt Discord + logs). 1h
- Sub-K9 (Forge): Dark-Token-Contrast-Audit (Sprint-E Playwright 4× AA-Violations auf /monitoring ratio 1.10 + /alerts 2.57). 2h
- Sub-K10 (Forge + Pixel optional): Cron-Inventory-Consolidation + Observability — 4-5h, 5 Layers
  - L1 Dead-Cron Cleanup (✅ DONE 2026-04-19 23:12 UTC — 9 disabled + 2 stale log cleaned by Assistant)
  - L2 Memory-Crons-Consolidation (11 separate → 1 orchestrator memory-maintenance-suite.sh @ 03:00-05:00 window) — 1-2h
  - L3 Systemd-Timer-Migration (worker-monitor + mc-watchdog + auto-pickup → systemd timers with Persistent=true + OnFailure hooks) — 2h
  - L4 Healthchecks.io-Observability (Docker healthchecks/healthchecks OR simple cron-health-monitor.sh) — 1-2h
  - L5 /admin/crons MC-Route Dashboard (Pixel optional, 2h) — analog /memory static portal
  - Referenz-Report: vault/03-Agents/cron-audit-2026-04-19.md (338 Zeilen) als baseline

Playbook:
1. qmd deep_search "sprint-k infra hardening" — Plan lesen
2. qmd deep_search "r47 scope-lock design" + "sprint-h h1 rca" — J2+J1 outputs als Baseline
3. POST 9 Board-Tasks via taskboard_create_task (R44 PFLICHT!)
4. Dispatch-Order:
   - Batch 1 (parallel, disjoint): K2 + K3 + K8 (Forge) + K9 (Forge)
   - Batch 2 (sequential nach K2/K3 done): K4 + K5 + K6 (alle Forge)
   - Batch 3 final: K7 (Forge, braucht K4 dependency für Lock-Integration)
5. R49-Compliance-Discipline: jede "done"-Claim MUSS inline `git log -1 <sha>` + `curl /api/tasks/<id>` Verify-Output enthalten

R47 Pre-Dispatch-Check (aktiv seit Sprint-J J2 deploy):
Prüfe Plan-Doc frontmatter für `operatorLock` — wenn true STOP + Operator-Approval anfragen.

Constraints:
- R45 Receipt-Discipline: accepted within 60s, progress alle 5min
- R46 mc-restart-safe PFLICHT (kein direkter systemctl restart)
- R47 Scope-Lock respect
- R49 Claim-Verify-Inline-Required für alle Status-Reports
- KEIN Sprint-L parallel

Anti-Scope:
- Keine neuen Features
- Keine UI-Polish (→ Sprint-I done)
- Keine Agent-Prompt-Revolutionen (nur R45/R46/R47/R49 bestehende Preambles preservieren)

Zeit-Budget: 18-23h orchestriert (+4-5h durch H10 Cron-Consolidation). Operator monitort passiv, R49-Validator-Cron läuft automatisch */15min (erkennt Hallucinations-Patterns).

Return format:
- EXECUTION_STATUS
- RESULT_SUMMARY:
  - 8 Board-Task-IDs + Final-Status (R49 compliant: inline verify-output pro Claim)
  - Report-Paths ls-verified (min. K9 + K3 + K6-L4 haben eigene Reports)
  - Git-Commits-Liste (1-2 pro Sub erwartet)
  - H6 L4 Commit-Signal Test: dispatche Test-Task, Agent commit ohne result-receipt, verify Auto-Completion innerhalb 3min
  - Residual-Findings → Sprint-L Kandidaten

Los.
```

## H6 Layer-4 Implementation-Hint (for Forge K6)

**Option A — Server-side Dispatcher-Cron (empfohlen, less invasive):**

```python
# workspace/scripts/commit-signal-auto-result.py
# Cron */2min — watches for commits matching active in-progress tasks,
# auto-posts receipt=result if no explicit result received within grace-period.

import subprocess, json, urllib.request
from datetime import datetime, timedelta

GRACE_MIN = 2
MC_API = "http://localhost:3000/api/tasks"
GIT_REPO = "/home/piet/.openclaw/workspace/mission-control"

# 1. Fetch active tasks
tasks = json.load(urllib.request.urlopen(MC_API))["tasks"]
active = [t for t in tasks if t.get("status") == "in-progress" and t.get("startedAt")]

# 2. Get commits since earliest startedAt
earliest = min(t["startedAt"] for t in active)
commits = subprocess.check_output(
    ["git", "log", f"--since={earliest}", "--format=%H|%s|%an|%at"],
    cwd=GIT_REPO, text=True
).strip().splitlines()

# 3. For each commit, match against task-scope keywords
for commit_line in commits:
    sha, subject, author, ts = commit_line.split("|", 3)
    commit_time = datetime.fromtimestamp(int(ts))
    
    for task in active:
        # Simple keyword-match: task title keywords appear in commit message
        title_words = set(w.lower() for w in task["title"].split() if len(w) > 4)
        subject_words = set(w.lower() for w in subject.split() if len(w) > 4)
        if not (title_words & subject_words):
            continue
        
        # Grace period check
        started = datetime.fromisoformat(task["startedAt"].replace("Z", "+00:00"))
        if commit_time < started:
            continue
        gap = datetime.now() - commit_time
        if gap < timedelta(minutes=GRACE_MIN):
            continue  # wait for explicit receipt
        
        # Auto-post receipt=result
        payload = {
            "receipt": "result",
            "summary": f"Auto-completed via commit-signal {sha[:7]}: {subject}",
            "status": "done",
            "note": "H6 L4 commit-signal auto-result (R49-compliant: commit verified)"
        }
        req = urllib.request.Request(
            f"{MC_API}/{task['id']}/receipt",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        urllib.request.urlopen(req, timeout=5)
        print(f"AUTO-DONE {task['id'][:12]} via commit {sha[:7]}")
```

**Option B — Client-side Git post-commit Hook (alternative):**

```sh
# .git/hooks/post-commit (installed per-clone, manually)
#!/bin/sh
# H6 L4 — auto-post receipt=result on commit if worker-task-id in env
TASK_ID="${OPENCLAW_WORKER_TASK_ID:-}"
[ -z "$TASK_ID" ] && exit 0
SHA=$(git rev-parse HEAD)
SUBJECT=$(git log -1 --format=%s)
curl -sS -X POST http://localhost:3000/api/tasks/"$TASK_ID"/receipt \
  -H 'Content-Type: application/json' \
  -d "{\"receipt\":\"result\",\"summary\":\"Auto-result via post-commit hook: $SHA - $SUBJECT\",\"status\":\"done\"}"
```

**Forge soll entscheiden:** Option A (server-cron, reach alle agents) vs Option B (client-hook, per-agent-setup). Empfehlung: A für jetzt, B als nice-to-have.

## Trigger-Phrase-Konvention

Analog zu "Atlas nun nächster Sprint follow #42" für Sprint-I:
**"Atlas Sprint-K Infra-Hardening starten"** — exakte Phrase, damit Claude/Assistant diesen Plan aus Vault ziehen kann.

Plan-Doku: `/home/piet/vault/03-Agents/sprint-k-infra-hardening-plan-2026-04-19.md`
