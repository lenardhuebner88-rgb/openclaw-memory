---
name: Sprint-K Infra-Hardening Plan
description: Sustainable fixes aus Sprint-A/B/C/D/E Incident-Cluster. RENAMED from Sprint-H to Sprint-K 2026-04-19 20:05 UTC — Atlas claimed "Sprint-H" autonomously für Board-Analytics.
status: draft
since: 2026-04-19
renamed_at: 2026-04-19 20:05 UTC
renamed_from: Sprint-H (Infra-Hardening)
owner: Operator (pieter_pan)
originSessionId: 71413231-e7bd-4ca4-a3fd-8154166039a0
---
# Sprint-K — Infra-Hardening (post Sprint-E, post-cascade-governance)

**Context:** Sprint-A bis Sprint-E haben 7+ Root-Cause-Klassen exponiert. Sprint-F läuft als nächstes (Ops-Inventory). Sprint-K adressiert die **tieferen systemischen Bugs** die durch aktive Beobachtung während Sprint-D/E aufgedeckt wurden.

**Namens-Historie:** Dieser Plan hieß bis 2026-04-19 ~20:00 UTC "Sprint-H Infra-Hardening" und lebte nur lokal in `memory/`. Parallel dazu hat Atlas autonomously einen **anderen** Sprint-H = "Board-Analytics" gestartet (Routes /analytics, /api/analytics, commits 0fe837f, fea4aa9). Um Namespace-Kollision zu vermeiden wurde dieser Plan umbenannt zu Sprint-K. Infra-Hardening-Inhalt (H1-H9) bleibt unverändert — nur Sprint-Letter rotiert.

## Scope-Matrix

| Sub | Title | Root-Cause | Impact | Agent | Estimate |
|---|---|---|---|---|---|
| **H1** | V8-Heap 4→6 GB + MemoryMax 4.5→7 GB | Gateway-OOM × 3 während Sprint-B/C | **DONE 2026-04-19** ✅ | Forge | 30 min |
| H2 | Tool-Allowlist statt Tool-Denylist | Sub-Agent uses `systemctl` in Prompt-Loop | prevents R46 class | Forge | 2-3h |
| H3 | memory-core reconcile debug | Background-reconciler spams logs | low-prio log hygiene | James→Forge | 1-2h |
| H4 | Concurrent-Subagent-Limit (max 2 with MC-restart) | R46 Parallel-Deploy-Race | P0 stability | Forge | 2h |
| H5 | R44 Board-Discipline Rule-Enforcement | Sub-Agent via sessions_spawn statt taskboard_create_task | Operator-blindness | Forge | 1h |
| **H6** | **Receipt-Lifecycle-Enforcement** | **R45 Sub-Agent-Receipt-Drift — E2 2h+ stuck assigned** | **P0 visibility** | Forge + Pixel | 3-4h |
| **H7** | **Deploy-Queue-Lock (MC-Restart-Serializer)** | **R46 Live-Case MC-Flap Sprint-E 17:06-17:08 UTC** | **P0 stability** | Forge | 2h |
| H8 | Budget-Alert $3 bug | False-alarms spammen logs + Discord | low-noise fix | Forge | 1h |
| **H9** | **Dark-Token-Contrast-Audit** | Sprint-E Playwright-Mobile-Audit fand 4× AA-Violations (`/monitoring` ratio 1.10, `/alerts` ratio 2.57) | P1 UX-Polish | Forge | 2h |

---

## H6 — Receipt-Lifecycle-Enforcement (Detail)

### Problem
Sub-Agents arbeiten stundenlang an Tasks die im Board `assigned` bleiben, nicht `in-progress`. Folgen:
- Board-UI "active"-Filter blind
- Discord #execution-reports silent während realer Arbeit  
- Worker-Monitor bypass (überwacht nur `in-progress`)
- Operator glaubt Atlas-Self-Report statt Board-Truth (R35-Pattern reload)

### Live-Case Sprint-E (2026-04-19 16:51-19:00 UTC)
- E2 Pixel 51508132 — 2h 8min in `assigned`, Session wuchs 0→410 KB
- E3 Forge 70369331 — 2h 20min in `assigned`, Session wuchs 0→187 KB  
- E1 hat funktioniert weil Task fertig wurde (final result-receipt kippte direkt auf `done`)

### Fix — 3 Layer

**Layer 1: Agent-Prompt-Preamble (30 min Aufwand)**  
In `openclaw.json` bei `agents.list.{frontend-guru,sre-expert,efficiency-auditor,researcher}.defaults.systemPrompt` anhängen:
```
## Receipt-Discipline (Pflicht)
FIRST ACTION nach Task-Pickup: taskboard_post_receipt(taskId, receipt=accepted, summary="<kurz-plan>").
EVERY major step (build, test, commit, route-add): taskboard_post_receipt(taskId, receipt=progress, summary="<was-gemacht>").
FINAL step: taskboard_post_receipt(taskId, receipt=result, summary=<full>, status=done|failed).
Kein `assigned`-Status länger als 2min ohne Receipt.
```

**Layer 2: Dispatcher Auto-Transition (1-2h)**  
Mission-Control `/api/tasks/:id/dispatch` oder Task-Dispatcher-Hook:
- Wenn Sub-Agent-Session-File `sessions/<sessionId>.jsonl` erstmals ein non-empty-write bekommt → Auto-PATCH `status: assigned → in-progress` + `lastActivityAt`
- File-Watcher via `inotify` oder 10s-Poll-Loop
- Datei: `workspace/scripts/auto-transition-watcher.py` (neuer cron)

**Layer 3: Worker-Monitor Extension (1h)**  
`worker-monitor.py` Line ~898 reconcile-block:
- Zusätzlich zu `in-progress`-Check: `assigned` Tasks mit `startedAt` > 10min ohne irgendwelche Receipts  
- Warn bei 10min, Hard-Fail bei 20min mit note "assigned-stall without receipt (R45 violation)"

**Layer 4 (NEW aus Sprint-J J1 RCA): Commit-Signal Auto-Result (2h)**

*Forge-Recommendation aus `vault/03-Agents/sprint-h-h1-rca-2026-04-19.md`:*

Sprint-H H1 Live-Case: Worker hat Code committed (`0fe837f` analytics-API) aber keinen `receipt=result` gepostet → R40 stall-timeout → Board falsch auf `failed`. Work war tatsächlich delivered, Board-State war False-Positive.

**Fix-Design:**
- Dispatcher-Hook oder neuer Cron-Job watches `git log --since="<task.startedAt>"` im Mission-Control-Workspace
- Wenn ein Commit im Zeit-Range UND task-assigned-agent matcht UND commit-message enthält task-scope-keywords (z.B. "feat(analytics)" für Sprint-H H1) → trigger **Grace-Period-Timer** (1-2 min)
- Nach Grace-Period ohne explicit `receipt=result`: automatischer `receipt=result` mit status=`done` + resultSummary=`"Auto-completed based on commit-signal: <sha> — <message>"`
- Markiert in Board-Events als `auto-completion-via-commit-signal` statt normalem `receipt=result` für Audit-Transparenz

**Alternativ-Pattern (leichter):**
- Sub-Agent commit-hook (git `post-commit`) checked aktuelle Worker-Task-ID aus env-var, POST automatisch `receipt=result` status=done mit commit-SHA
- Vorteil: Agent muss sich nicht explizit erinnern Receipt zu posten, commit trigger es auto
- Nachteil: jeder Agent-Worker muss commit-hook installiert haben, hooks sind per-clone nicht per-repo

**Acceptance:**
- Test: Agent committet + exits ohne receipt, Board transitioniert innerhalb 3min auto auf `done`
- Board-Events zeigt clear `auto-completion-via-commit-signal`-Event mit commit-SHA
- False-Positive-Rate < 5% (commits ohne echten Task-Bezug würden irrtümlich complete)

### Acceptance Sprint-K H6 gesamt
- Jeder Sub-Agent postet innerhalb 60s `accepted`-Receipt messbar via Board-Events-Stream
- Board-UI zeigt E2/E3-analog Tasks als `in-progress` innerhalb 2min nach Dispatch
- Discord #execution-reports bekommt Receipts für alle 3+ Sub-Tasks pro Sprint
- Worker-Monitor escaliert korrekt bei Test-Case "dispatch task, dont post receipt, wait 20min"
- **(H6 L4)** Commit-Signal Auto-Completion für Test-Case "agent commits + exits ohne explicit result-receipt" → Board auto-done innerhalb 3min

---

## H7 — Deploy-Queue-Lock (MC-Restart-Serializer)

### Problem
R46 Live-Case Sprint-E 17:06-17:08 UTC:
- Pixel + Forge beide mit R42 Deploy-Verify-Contract im Prompt
- Beide `systemctl --user restart mission-control && sleep 30 && curl verify`
- Restarts racen gegeneinander → 3 Restarts in 10min → curl=000 während Flap → mehr Restarts
- Board zeigte `TASKS []` während MC deactivating

### Fix — Wrapper-Script
**Datei: `/home/piet/.local/bin/mc-restart-safe`** (in PATH vor systemctl oder als expliziter Call):
```sh
#!/bin/bash
# mc-restart-safe — serializes MC-restarts, prevents Sprint-E-style races
# Usage: mc-restart-safe [--timeout SEC] [--reason "why"]
set -euo pipefail
LOCK="/tmp/mc-deploy.lock"
TIMEOUT="${1:-120}"
REASON="${2:-unspecified}"

exec 200>"$LOCK" || { echo "cannot open lock"; exit 1; }
flock -w "$TIMEOUT" 200 || { echo "lock held by another deploy, timeout after ${TIMEOUT}s"; exit 2; }

echo "[mc-restart-safe] $(date -u +%FT%TZ) acquired lock, reason=$REASON caller=PPID:$PPID"
systemctl --user restart mission-control
# Wait for MC to come back before releasing lock
for i in $(seq 1 60); do
  sleep 1
  if curl -sS -o /dev/null -w '%{http_code}' --max-time 2 http://localhost:3000/api/health | grep -q 200; then
    echo "[mc-restart-safe] MC back in ${i}s"
    exit 0
  fi
done
echo "[mc-restart-safe] MC did not come back in 60s — releasing lock anyway"
exit 3
```

### Agent-Prompt-Anpassung
R42 Deploy-Verify-Contract in Sub-Agent-Prompts wird geändert von:
```
systemctl --user restart mission-control && sleep 30 && curl -f http://localhost:3000/<route>
```
zu:
```
mc-restart-safe 120 "sub-<agent>-deploy" && curl -f http://localhost:3000/<route>
```

### Atlas-Orchestrator Scheduling-Regel
Zusätzlich: Atlas soll **nicht** zwei Sub-Tasks mit `deploy_verify=true` **gleichzeitig** dispatchen. Flag im Task-Definition: `requires_mc_restart: true` → Dispatch-Serialization enforcement.

### Acceptance
- `flock` prevents 2 simultaneous MC-restarts (verify via parallel test)
- Sprint mit 2 Subs mit MC-restart: max 1 Restart-Event pro Zeit, keine Flap
- Agent-2 wartet sichtbar (Lock-Log) bis Agent-1 fertig

---

## H5 Update — R44 + R45 Konsolidiert

R44 (Board-Visibility): Sub-Agents **müssen** via `taskboard_create_task` angelegt werden, nicht via `sessions_spawn`-only.  
R45 (Receipt-Discipline): Auch nach R44-Compliance MÜSSEN Receipts posted werden.

Beide Rules zusammen via shared Agent-Prompt-Preamble enforcen (H6 Layer 1).

---

## Dispatch-Empfehlung

**NICHT** jetzt während Sprint-E läuft. Sprint-E aktuell @ E2+E3. Warten bis E1-E5 fertig, dann:

1. Sprint-F Ops-Inventory (queued ee455d69) läuft erst
2. Post-Sprint-F Abschlussbericht Sprint-D+E+F
3. Sprint-H Dispatch sequenziell — H4, H6, H7 als P0-Cluster (System-Stabilität > Features)
4. H2, H3, H5, H8 als P1-Follow-ups

**Geschätzte Gesamt-Zeit Sprint-H:** 12-15h orchestriert (H6+H7 sind die großen Items).

---

## Anti-Scope

- KEINE neuen Features in Sprint-H — nur Infra/Rules/Stabilität
- KEINE Agent-Prompt-Revolutionen — minimal-invasive Preamble-Additions
- KEINE Lock-File-Orchestrierung über multiple Files — nur /tmp/mc-deploy.lock
- NICHT in Sprint-H: Full Receipt-Scheduler-Redesign (bleibt lokal in Agent-Prompts)

## Signoff

Operator (pieter_pan) 2026-04-19 17:10 UTC — Sprint-H Plan erweitert um H6+H7 nach Sprint-E Live-Incidents.
